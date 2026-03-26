import ursina


class FlowerSystem:
	"""Gere la plantation, la croissance et la recolte des fleurs."""

	ZONE_REWATER_TIMEOUT = 60

	def __init__(
		self,
		player,
		inventory,
		maps_module,
		texture_paths,
		fleurs_dict,
		get_selected_hotbar_item,
		matrice_inventaire,
		destroy,
	):
		self.player = player
		self.inventory = inventory
		self.maps = maps_module
		self.texture_paths = texture_paths
		self.fleurs = fleurs_dict
		self.get_selected_hotbar_item = get_selected_hotbar_item
		self.matrice_inventaire = matrice_inventaire
		self.destroy = destroy
		self.planted_flowers = []

	def destroy_plants_in_zone(self, zone):
		"""Detruit toutes les pousses/fleurs liees a une zone."""
		destroyed_count = 0
		for plant in list(self.planted_flowers):
			if getattr(plant, "_zone", None) is zone:
				if getattr(plant, "_spot_pos", None) is not None:
					self.maps.release_occupied_spot(zone, plant._spot_pos)
				if plant in self.planted_flowers:
					self.planted_flowers.remove(plant)
				try:
					self.destroy(plant)
				except Exception:
					pass
				destroyed_count += 1
		return destroyed_count

	def update_zone_dry_timers(self):
		"""Si une zone seche trop longtemps, detruit les plantes restantes."""
		now = ursina.time.time()
		for zone in getattr(self.maps, "zones", []):
			dry_since = getattr(zone, "dry_since", None)
			if dry_since is None:
				continue
			if now - dry_since >= self.ZONE_REWATER_TIMEOUT:
				removed = self.destroy_plants_in_zone(zone)
				if removed > 0:
					print("Zone non arrosée depuis 2 minutes: pousses/fleurs détruites.")
				zone.dry_since = None

	def bloom_plant(self, plant):
		"""Fait passer une pousse en fleur mure."""
		if plant not in self.planted_flowers:
			return
		if getattr(plant, "growth_stage", 0) != 0:
			return

		zone = getattr(plant, "_zone", None)
		if zone is not None and not getattr(zone, "is_watered", False):
			return

		flower_texture = self.texture_paths.get(plant.flower_name)
		for quad in plant._quads:
			quad.texture = flower_texture
		plant.growth_stage = 1
		print(f"'{plant.flower_name}' a poussé ! Cliquez dessus pour récolter.")

		if zone is not None and getattr(zone, "is_watered", False):
			zone.grown_in_cycle = getattr(zone, "grown_in_cycle", 0) + 1
			if zone.grown_in_cycle >= 3:
				self.maps.reset_zone_to_dry(zone, start_dry_timer=True)
				print("La zone est redevenue marron. Ré-arrosez-la sous 2 minutes pour éviter la destruction des pousses/fleurs.")

		def harvest():
			if plant not in self.planted_flowers:
				return

			plant_zone = getattr(plant, "_zone", None)
			if plant_zone is not None and getattr(plant, "_spot_pos", None) is not None:
				self.maps.release_occupied_spot(plant_zone, plant._spot_pos)

			self.inventory.add_item(plant.flower_name)
			self.matrice_inventaire()
			print(f"'{plant.flower_name}' récoltée et ajoutée à l'inventaire !")

			if plant_zone is not None and getattr(plant_zone, "is_watered", False):
				self.maps.add_planting_spot(plant_zone, plant._spot_pos)

			if plant in self.planted_flowers:
				self.planted_flowers.remove(plant)
			self.destroy(plant)

		plant.on_click = harvest

	def update_plant_growth(self):
		"""La croissance avance uniquement quand la zone est arrosee."""
		dt = ursina.time.dt
		for plant in list(self.planted_flowers):
			if getattr(plant, "growth_stage", 0) != 0:
				continue

			zone = getattr(plant, "_zone", None)
			if zone is not None and not getattr(zone, "is_watered", False):
				continue

			plant.age += dt
			if plant.age >= getattr(plant, "growth_delay", 60):
				self.bloom_plant(plant)

	def build_flower_name_from_item(self, item_name):
		if not item_name:
			return None
		if item_name.startswith("Graines de "):
			candidate = item_name.replace("Graines de ", "")
			if candidate in self.fleurs:
				return candidate
		if item_name.startswith("Graines d'"):
			candidate = item_name.replace("Graines d'", "")
			if candidate in self.fleurs:
				return candidate
		return None

	def plant_selected_from_hotbar(self):
		selected_item = self.get_selected_hotbar_item()
		if selected_item is None:
			print("Aucun item sélectionné dans la hotbar")
			return False

		flower_name = self.build_flower_name_from_item(selected_item.item_name)
		if flower_name is None:
			print(f"L'item sélectionné '{selected_item.item_name}' n'est pas une graine valide")
			return False

		hit_info = ursina.raycast(self.player.position, self.player.forward, distance=20, ignore=[self.player])
		if not hit_info.hit:
			print("Aucune surface visée pour planter")
			return False

		planting_spots = [spot for zone in self.maps.zones for spot in getattr(zone, "planting_spots", [])]
		if hit_info.entity not in planting_spots:
			print("Cliquez sur un cercle vert pour planter")
			return False

		plant_pos = ursina.Vec3(hit_info.entity.x, 1.8, hit_info.entity.z)
		spot_pos = ursina.Vec3(hit_info.entity.x, hit_info.entity.y, hit_info.entity.z)

		spot_zone = None
		for zone in self.maps.zones:
			if hit_info.entity in getattr(zone, "planting_spots", []):
				spot_zone = zone
				zone.planting_spots.remove(hit_info.entity)
				break

		plant = ursina.Entity(position=plant_pos, collider="box")
		sprout_texture = self.texture_paths.get("Pousse")
		plant1 = ursina.Entity(
			parent=plant,
			model="quad",
			texture=sprout_texture,
			color=ursina.color.white,
			scale=(4, 4, 4),
			rotation_y=45,
			double_sided=True,
			shader=ursina.shaders.lit_with_shadows_shader,
		)
		plant2 = ursina.Entity(
			parent=plant,
			model="quad",
			texture=sprout_texture,
			color=ursina.color.white,
			scale=(4, 4, 4),
			rotation_y=135,
			double_sided=True,
			shader=ursina.shaders.lit_with_shadows_shader,
		)

		plant.flower_name = flower_name
		plant.growth_stage = 0
		plant.age = 0.0
		plant._quads = [plant1, plant2]
		plant._spot_pos = spot_pos
		plant._zone = spot_zone

		if spot_zone is not None:
			self.maps.register_occupied_spot(spot_zone, spot_pos)

		self.planted_flowers.append(plant)

		rarity = self.fleurs[flower_name].rareté
		plant.growth_delay = {1: 30, 2: 90, 3: 130, 4: 200}.get(rarity, 60)

		self.destroy(hit_info.entity)

		if getattr(selected_item, "stack", 1) > 1:
			selected_item.stack -= 1
			try:
				selected_item._update_tooltip_text()
			except Exception:
				pass
		else:
			try:
				self.destroy(selected_item)
			except Exception:
				pass

		self.matrice_inventaire()
		print(f"Plante '{flower_name}' plantée à {plant_pos}")
		return True

	def handle_left_click(self, atm_panel_visible, mushroom_panel_visible):
		"""Gere le clic gauche de plantation en tenant compte des interfaces ouvertes."""
		if atm_panel_visible or mushroom_panel_visible:
			return False

		planted = self.plant_selected_from_hotbar()
		if planted:
			print("Plante semée depuis la hotbar")
		return planted

from math import sin
import random
import ursina

from Objets import fleurs, texture_paths


class Scene3D:
	"""Contient les entites 3D et les interactions de proximite associees."""

	def __init__(self, player):
		self.player = player

		self.sky = ursina.Sky(texture="data/atm/sky3.jpg")

		self.stand_parent = ursina.Entity(position=(-10.55, 4, -20.95))
		self.stand = ursina.Entity(
			model="data/atm/atm.obj",
			texture="data/atm/atm2.jpg",
			double_sided=True,
			parent=self.stand_parent,
			position=(0, -3, 1.51),
			scale=(60, 60, 60),
			collider="box",
			shader=ursina.shaders.lit_with_shadows_shader,
		)

		flower_names = list(fleurs.keys())
		flower_textures = [texture_paths.get(name) for name in flower_names if texture_paths.get(name)]
		self.stand_animation = ursina.Entity(
			model="quad",
			texture=flower_textures[0] if flower_textures else None,
			double_sided=True,
			parent=self.stand_parent,
			position=(0, -0.9, 3),
			scale=(2.5, 2.5, 2.5),
			shader=ursina.shaders.lit_with_shadows_shader,
		)
		self.stand_animation.flower_textures = flower_textures
		self.stand.update = self._stand_update

		# use converted OBJ to avoid .blend import failure in Ursina
		self.puit = ursina.Entity(
			model="sources/models_compressed/Well.obj",
			texture="data/casa/Well_texture2.png",
			scale=(0.5),
			position=(-25, 1.5, 35),
			double_sided=True,
			collider="mesh",
			shader=ursina.shaders.lit_with_shadows_shader,
		)
		self.eau = ursina.Entity(
			model="quad",
			texture="data/casa/watta.jpg",
			rotation=(90, 0, 0),
			scale=(4.60),
			position=(-24.85, 4, 34.85),
			shader=ursina.shaders.lit_with_shadows_shader,
		)

		self.mushroom = ursina.Entity(
			model="data/casa/mushroom7.fbx",
			texture="data/casa/shroom_Base_Color2.png",
			position=(-40, 2, 2),
			scale=(0.03),
			double_sided=True,
			collider="box",
			shader=ursina.shaders.lit_with_shadows_shader,
		)

		self.hint_text = ursina.Text(
			text="Click droit",
			position=(-0.5, 0.4),
			origin=(0, 0),
			background=True,
			scale=2,
			enabled=False,
		)

		self.sun = ursina.DirectionalLight(shadow_map_resolution=(2048, 2048))
		self.sun.look_at(ursina.Vec3(-1, -1, -10))

	def bind_well_click(self, get_selected_hotbar_item, texture_paths):
		"""Connecte la logique de remplissage d'arrosoir au puits."""

		def on_well_click():
			selected_item = get_selected_hotbar_item()
			if selected_item and selected_item.item_name in ["Arrosoir rouillé", "Arrosoir en fer", "Arrosoir en or"]:
				dist = ((self.player.position.x - self.puit.position.x) ** 2 + (self.player.position.z - self.puit.position.z) ** 2) ** 0.5
				if dist < 5:
					if selected_item.item_name == "Arrosoir rouillé":
						selected_item.item_name = "Arrosoir rouillé rempli"
						selected_item.uses = 1
					elif selected_item.item_name == "Arrosoir en fer":
						selected_item.item_name = "Arrosoir en fer rempli"
						selected_item.uses = 2
					elif selected_item.item_name == "Arrosoir en or":
						selected_item.item_name = "Arrosoir en or rempli"
						selected_item.uses = 3
					selected_item.texture = texture_paths.get(selected_item.item_name, selected_item.item_name)
					selected_item._update_tooltip_text()
					print("Arrosoir rempli !")
				else:
					print("Trop loin du puit")
			else:
				print("Sélectionnez un arrosoir vide pour le remplir")

		self.puit.on_click = on_well_click

	def handle_right_click_interaction(self, atm_panel_visible, mushroom_panel_visible, toggle_atm, toggle_mushroom):
		"""Déclenche l'interaction 3D appropriée au clic droit."""
		if atm_panel_visible or mushroom_panel_visible:
			return

		if not self.hint_text.enabled:
			return

		if self.stand.hovered:
			toggle_atm()
		elif self.mushroom.hovered:
			toggle_mushroom()

	def _stand_update(self):
		# Keep ATM static (no rotation)
		self.stand.y += sin(ursina.time.time() * 10) * 0.01
		self.stand_animation.y += sin(ursina.time.time() * 10) * 0.01

		if hasattr(self.stand_animation, "flower_textures") and self.stand_animation.flower_textures:
			self.stand_animation._texture_i = int(ursina.time.time() * 1) % len(self.stand_animation.flower_textures)
			self.stand_animation.texture = self.stand_animation.flower_textures[self.stand_animation._texture_i]

		proximity_threshold = 6.0

		dx_stand = self.player.x - self.stand.world_x
		dy_stand = self.player.y - self.stand.world_y
		dz_stand = self.player.z - self.stand.world_z
		dist_stand = (dx_stand * dx_stand + dy_stand * dy_stand + dz_stand * dz_stand) ** 0.5

		dx_mush = self.player.x - self.mushroom.world_x
		dy_mush = self.player.y - self.mushroom.world_y
		dz_mush = self.player.z - self.mushroom.world_z
		dist_mush = (dx_mush * dx_mush + dy_mush * dy_mush + dz_mush * dz_mush) ** 0.5

		if dist_stand <= proximity_threshold:
			self.hint_text.text = "Click droit"
			self.hint_text.enabled = True
		elif dist_mush <= proximity_threshold:
			self.hint_text.text = "Click droit"
			self.hint_text.enabled = True
		else:
			self.hint_text.enabled = False


class SceneGameUI:
	"""Regroupe les interactions ATM/Champignon et leur UI."""

	def __init__(
		self,
		scene_3d,
		player,
		inventory,
		joueur,
		achat_sound,
		vente_sound,
		iPan,
		Inventory,
		fpc_mouse,
		get_selected_hotbar_item,
		matrice_inventaire,
		destroy,
		graines,
		arrosoirs,
		fleurs,
	):
		self.scene_3d = scene_3d
		self.player = player
		self.inventory = inventory
		self.joueur = joueur
		self.achat_sound = achat_sound
		self.vente_sound = vente_sound
		self.iPan = iPan
		self.Inventory = Inventory
		self.fpc_mouse = fpc_mouse
		self.get_selected_hotbar_item = get_selected_hotbar_item
		self.matrice_inventaire = matrice_inventaire
		self.destroy = destroy
		self.graines = graines
		self.arrosoirs = arrosoirs
		self.fleurs = fleurs
		self.tirage_en_cours = False

		self._build_ui()

	def has_any_watering_can(self, names):
		inv = getattr(self.Inventory, "instance", None)
		if inv is None:
			return False
		return any(getattr(item, "item_name", None) in names for item in inv.item_parent.children)

	def replace_first_watering_can(self, old_names, new_name):
		"""Remplace le premier arrosoir trouve par la nouvelle version."""
		inv = getattr(self.Inventory, "instance", None)
		if inv is None:
			return False

		for item in inv.item_parent.children:
			if getattr(item, "item_name", None) in old_names:
				item.item_name = new_name
				item.uses = None
				item.texture = texture_paths.get(new_name, new_name)
				try:
					item._update_tooltip_text()
				except Exception:
					pass
				return True
		return False

	def apply_drawn_watering_can_upgrade(self, item_name):
		"""Applique la progression d'arrosoir sans empiler plusieurs niveaux."""
		if item_name == "Arrosoir en fer":
			replaced = self.replace_first_watering_can(
				["Arrosoir rouillé", "Arrosoir rouillé rempli"],
				"Arrosoir en fer",
			)
			if not replaced:
				self.inventory.add_item("Arrosoir en fer")
			return True

		if item_name == "Arrosoir en or":
			replaced = self.replace_first_watering_can(
				["Arrosoir en fer", "Arrosoir en fer rempli", "Arrosoir rouillé", "Arrosoir rouillé rempli"],
				"Arrosoir en or",
			)
			if not replaced:
				self.inventory.add_item("Arrosoir en or")
			return True

		return False

	def make_1_wishes(self):
		"""Fait 1 tirage aleatoire et ajoute une graine a l'inventaire."""
		if not self.atm_panel.visible:
			return

		if self.mushroom_panel.visible:
			print("Fermez l'interface Champignon pour faire un tirage.")
			return

		if self.tirage_en_cours:
			print("Veuillez attendre avant de faire un nouveau tirage.")
			return

		self.tirage_en_cours = True
		draw_pool = []

		available_seed_keys = [key for key in self.graines.keys() if self.graines[key].rareté in [1, 2, 3, 4]]
		for key in available_seed_keys:
			seed = self.graines[key]
			weight = 85 if seed.rareté == 1 else 10 if seed.rareté == 2 else 4 if seed.rareté == 3 else 1
			draw_pool.append((seed.nom, seed.rareté, weight))

		has_iron = self.has_any_watering_can(["Arrosoir en fer", "Arrosoir en fer rempli"])
		has_gold = self.has_any_watering_can(["Arrosoir en or", "Arrosoir en or rempli"])

		if has_gold:
			drawable_cans = []
		elif has_iron:
			drawable_cans = ["Arrosoir en or"]
		else:
			drawable_cans = ["Arrosoir en fer", "Arrosoir en or"]

		for can_name in drawable_cans:
			if can_name not in self.arrosoirs:
				continue
			can = self.arrosoirs[can_name]
			can_weight = 1 if can_name == "Arrosoir en fer" else 0.5
			draw_pool.append((can.nom, can.rareté, can_weight))

		choices = [entry[0] for entry in draw_pool]
		weights = [entry[2] for entry in draw_pool]
		item_name2 = random.choices(choices, weights=weights, k=1)[0]

		rarity = 1
		for name, rarity_value, _ in draw_pool:
			if name == item_name2:
				rarity = rarity_value
				break

		is_can_upgrade = item_name2 in ["Arrosoir en fer", "Arrosoir en or"]
		can_receive = self.inventory.find_free_spot() is not None or is_can_upgrade

		if self.joueur.argent >= 10 and can_receive:
			self.show_seed_result(item_name2, rarity)

			if self.achat_sound is not None:
				try:
					self.achat_sound.play()
				except Exception as e:
					print(f"Erreur lecture son d'achat: {e}")

			upgraded = self.apply_drawn_watering_can_upgrade(item_name2)
			if not upgraded:
				self.inventory.add_item(item_name2)
			self.matrice_inventaire()
			self.joueur.argent -= 10
			print("1 voeu réalisé! Objet ajouté à l'inventaire.")
		else:
			if self.joueur.argent < 10:
				print("Pas assez d'argent pour faire un tirage.")
			else:
				print("Inventaire plein, impossible d'ajouter la fleur.")

		self.toggle_atm_interface()

		def reset_tirage():
			self.tirage_en_cours = False
			print("Vous pouvez maintenant faire un nouveau tirage.")

		ursina.invoke(reset_tirage, delay=5)

	def show_seed_result(self, seed_name, rarity):
		rarity_text = ""
		if rarity == 1:
			rarity_text = "Commun"
		elif rarity == 2:
			rarity_text = "Rare"
		elif rarity == 3:
			rarity_text = "Epique"
		elif rarity == 4:
			rarity_text = "Légendaire"

		item_texture = texture_paths.get(seed_name, f"../data/Graines/{seed_name}.png")
		seed_image = ursina.Entity(
			model="quad",
			texture=item_texture,
			scale=(0.3, 0.3),
			position=(0, 0.1),
			parent=ursina.camera.ui,
		)

		rarity_display = ursina.Text(
			text=rarity_text,
			position=(0, -0.15),
			scale=2,
			color=ursina.color.white,
			parent=ursina.camera.ui,
			origin=(0, 0),
		)

		def hide_result():
			seed_image.disable()
			rarity_display.disable()

		ursina.invoke(hide_result, delay=3)

	def _set_atm_widgets_enabled(self, is_enabled):
		self.atm_title.enabled = is_enabled
		self.atm_button.enabled = is_enabled
		self.close_button.enabled = is_enabled

	def _set_mushroom_widgets_enabled(self, is_enabled):
		self.mushroom_title.enabled = is_enabled
		self.mushroom_button.enabled = is_enabled
		self.close_mushroom_button.enabled = is_enabled

	def _close_mushroom_interface(self):
		self.mushroom_panel.visible = False
		self._set_mushroom_widgets_enabled(False)
		self.player.enable()
		self.fpc_mouse.locked = True
		self.player.cursor.visible = True

	def _apply_atm_button_styles(self):
		self.atm_button.color = ursina.color.green
		self.atm_button.highlight_color = ursina.color.lime
		self.atm_button.pressed_color = ursina.color.rgb(0, 100, 0)
		self.atm_button.text_color = ursina.color.white
		self.close_button.color = ursina.color.red
		self.close_button.highlight_color = ursina.color.pink
		self.close_button.pressed_color = ursina.color.rgb(100, 0, 0)
		self.close_button.text_color = ursina.color.white

	def _apply_mushroom_button_styles(self):
		self.mushroom_button.color = ursina.color.blue
		self.mushroom_button.highlight_color = ursina.color.cyan
		self.mushroom_button.pressed_color = ursina.color.rgb(0, 0, 100)
		self.mushroom_button.text_color = ursina.color.white
		self.close_mushroom_button.color = ursina.color.red
		self.close_mushroom_button.highlight_color = ursina.color.pink
		self.close_mushroom_button.pressed_color = ursina.color.rgb(100, 0, 0)
		self.close_mushroom_button.text_color = ursina.color.white

	def toggle_atm_interface(self):
		"""Affiche/cache l'interface ATM."""
		if not self.atm_panel.visible and self.mushroom_panel.visible:
			print("Fermez l'interface Champignon avant d'ouvrir l'ATM.")
			return

		self.atm_panel.visible = not self.atm_panel.visible
		self._set_atm_widgets_enabled(self.atm_panel.visible)
		if self.atm_panel.visible:
			if self.iPan and self.iPan.visible:
				self.Inventory.toggle()
			self._apply_atm_button_styles()
			ursina.invoke(self._apply_atm_button_styles, delay=0)
			self.player.disable()
			self.fpc_mouse.locked = False
			self.player.cursor.visible = True
		else:
			self.player.enable()
			self.fpc_mouse.locked = True
			self.player.cursor.visible = True

	def sell_selected_flower(self):
		if self.atm_panel.visible:
			print("Fermez l'interface ATM pour vendre au Champignon.")
			return

		selected_item = self.get_selected_hotbar_item()
		if not selected_item or not getattr(selected_item, "item_name", None):
			print("Ce n'est pas une fleur")
			self._close_mushroom_interface()
			return

		item_name = selected_item.item_name
		rarete = None

		if item_name in self.graines or item_name.lower().startswith("graines"):
			print("Ce n'est pas une fleur")
			self._close_mushroom_interface()
			return

		if item_name in self.fleurs:
			rarete = self.fleurs[item_name].rareté
		else:
			print("Ce n'est pas une Fleur")
			self._close_mushroom_interface()
			return

		gain = {1: 13, 2: 20, 3: 35, 4: 50}.get(rarete, 1)
		self.joueur.argent += gain
		print(f"{item_name} vendu ({'Commun' if rarete == 1 else 'Rare' if rarete == 2 else 'Epic' if rarete == 3 else 'Légendaire'}), +{gain}€")

		if self.vente_sound is not None:
			try:
				self.vente_sound.play()
			except Exception as e:
				print(f"Erreur lecture son de vente: {e}")

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

		self._close_mushroom_interface()

	def toggle_mushroom_interface(self):
		"""Affiche/cache l'interface Champignon."""
		if not self.mushroom_panel.visible and self.atm_panel.visible:
			print("Fermez l'interface ATM avant d'ouvrir le Champignon.")
			return

		self.mushroom_panel.visible = not self.mushroom_panel.visible
		self._set_mushroom_widgets_enabled(self.mushroom_panel.visible)
		if self.mushroom_panel.visible:
			if self.iPan and self.iPan.visible:
				self.Inventory.toggle()
			self._apply_mushroom_button_styles()
			ursina.invoke(self._apply_mushroom_button_styles, delay=0)
			self.player.disable()
			self.fpc_mouse.locked = False
			self.player.cursor.visible = True
		else:
			self.player.enable()
			self.fpc_mouse.locked = True
			self.player.cursor.visible = True

	def _build_ui(self):
		self.atm_panel = ursina.Panel(
			parent=ursina.camera.ui,
			model="quad",
			scale=(0.68, 0.46),
			position=(0, 0),
			color=ursina.color.dark_gray,
			visible=False,
		)

		self.atm_title = ursina.Text(
			parent=self.atm_panel,
			text="Distributeur Automatique",
			position=(0, 0.17),
			z=-0.2,
			scale=1.5,
			color=ursina.color.white,
		)

		self.atm_button = ursina.Button(
			parent=self.atm_panel,
			text="Faire 1 tirage",
			position=(0, -0.02),
			z=-0.3,
			scale=(0.42, 0.11),
			on_click=self.make_1_wishes,
		)

		self.close_button = ursina.Button(
			parent=self.atm_panel,
			text="Fermer",
			position=(0, -0.18),
			z=-0.3,
			scale=(0.2, 0.08),
			on_click=self.toggle_atm_interface,
		)
		self._apply_atm_button_styles()
		self._set_atm_widgets_enabled(False)

		self.mushroom_panel = ursina.Panel(
			parent=ursina.camera.ui,
			model="quad",
			scale=(0.68, 0.46),
			position=(0, 0),
			color=ursina.color.dark_gray,
			visible=False,
		)

		self.mushroom_title = ursina.Text(
			parent=self.mushroom_panel,
			text="Champignon Magique",
			position=(0, 0.17),
			z=-0.2,
			scale=1.5,
			color=ursina.color.white,
		)

		self.mushroom_button = ursina.Button(
			parent=self.mushroom_panel,
			text="Vendre la fleur tenue",
			position=(0, -0.01),
			z=-0.3,
			scale=(0.52, 0.12),
			on_click=self.sell_selected_flower,
		)

		self.close_mushroom_button = ursina.Button(
			parent=self.mushroom_panel,
			text="Fermer",
			position=(0, -0.18),
			z=-0.3,
			scale=(0.2, 0.08),
			on_click=self.toggle_mushroom_interface,
		)
		self._apply_mushroom_button_styles()
		self._set_mushroom_widgets_enabled(False)


def init_scene_models(player):
	return Scene3D(player)

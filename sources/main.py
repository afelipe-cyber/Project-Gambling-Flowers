from importlib.util import *
from pathlib import Path
import ursina
import ursina.prefabs.first_person_controller as fpc
from Inventaire import *
import maps
import random
import Joueur
from Objets import texture_paths
import pygame as pg
from math import sin

# Make assets resolvable from project root (not /sources).
ursina.application.asset_folder = Path(__file__).resolve().parent.parent
app = ursina.Ursina()
# créer le ciel
sky = ursina.Sky(texture="data/atm/sky3.jpg")
pg.init()  # Initialiser Pygame pour la musique
pg.mixer.music.load("data/Divers/Moonlight_Sonata.mp3")
pg.mixer.music.set_volume(0.2)
pg.mixer.music.play(-1)  # Jouer en boucle

try:
    achat_sound = pg.mixer.Sound("data/Divers/Achat.mp3")
    achat_sound.set_volume(0.7)
except Exception as e:
    achat_sound = None
    print(f"Impossible de charger le son d'achat: {e}")

try:
    vente_sound = pg.mixer.Sound("data/Divers/Vente.mp3")
    vente_sound.set_volume(0.7)
except Exception as e:
    vente_sound = None
    print(f"Impossible de charger le son de vente: {e}")
# Initialiser l'inventaire
inventory = init_inventory()
inventory.add_item("Arrosoir rouillé")
matrice_inventaire()  # Mettre à jour l'affichage

# Afficher argents du joueur
joueur = Joueur.Joueur("Player", argent=200, inventaire=inventory)
maps.joueur = joueur
argent_text = joueur.affichage_argent()


def update():
    joueur.affichage_argent()
    update_zone_dry_timers()
    update_plant_growth()

    # Bloque tout mouvement tant qu'une interface ATM/Champignon est ouverte.
    if 'player' in globals():
        ui_locked = (
            ('atm_panel' in globals() and atm_panel.visible)
            or ('mushroom_panel' in globals() and mushroom_panel.visible)
        )
        if ui_locked:
            player.speed = 0
            for move_key in ('w', 'a', 's', 'd', 'z', 'q'):
                ursina.held_keys[move_key] = 0
        else:
            player.speed = PLAYER_DEFAULT_SPEED


# Créer le terrain
platform = maps.create_map()
maps.fence()
maps.init_purchase_panel()

player = fpc.FirstPersonController(position=(-10.55, 2, -10), scale=2.5, speed=20)
PLAYER_DEFAULT_SPEED = player.speed
maps.player = player


def stand_update():
    global stand, stand_animation, stand_parent, hint_text, player, mushroom
    # Keep ATM static (no rotation)
    # stand_parent.rotation_y += 40 * ursina.time.dt
    # stand_animation.rotation_y += 40 * ursina.time.dt
    stand.y += sin(ursina.time.time() * 10) * 0.01
    stand_animation.y += sin(ursina.time.time() * 10) * 0.01

    # Cycle flower textures if available.
    if hasattr(stand_animation, "flower_textures") and stand_animation.flower_textures:
        stand_animation._texture_i = int(ursina.time.time() * 1) % len(stand_animation.flower_textures)
        stand_animation.texture = stand_animation.flower_textures[stand_animation._texture_i]

    # Show a prompt when the player is close to the ATM or mushroom.
    proximity_threshold = 6.0

    # Distance to stand
    dx_stand = player.x - stand.world_x
    dy_stand = player.y - stand.world_y
    dz_stand = player.z - stand.world_z
    dist_stand = (dx_stand*dx_stand + dy_stand*dy_stand + dz_stand*dz_stand) ** 0.5

    # Distance to mushroom
    dx_mush = player.x - mushroom.world_x
    dy_mush = player.y - mushroom.world_y
    dz_mush = player.z - mushroom.world_z
    dist_mush = (dx_mush*dx_mush + dy_mush*dy_mush + dz_mush*dz_mush) ** 0.5

    if dist_stand <= proximity_threshold:
        hint_text.text = "Click droit"
        hint_text.enabled = True
    elif dist_mush <= proximity_threshold:
        hint_text.text = "Click droit"
        hint_text.enabled = True
    else:
        hint_text.enabled = False

stand_parent = ursina.Entity(position=(-10.55, 4, -20.95))
stand = ursina.Entity(model="data/atm/atm.obj", texture="data/atm/atm2.jpg", double_sided=True, parent=stand_parent, position=(0, -3, 1.51), scale=(60, 60, 60), collider="box", shader=ursina.shaders.lit_with_shadows_shader, )
_flower_names = list(fleurs.keys()) if 'fleurs' in globals() else []
_flower_textures = [texture_paths.get(name) for name in _flower_names if texture_paths.get(name)]
stand_animation = ursina.Entity(
    model="quad",
    texture=_flower_textures[0] if _flower_textures else None,
    double_sided=True,
    parent=stand_parent,
    position=(0, -0.9, 3),
    scale=(2.5, 2.5, 2.5),
    shader=ursina.shaders.lit_with_shadows_shader,
)
stand_animation.flower_textures = _flower_textures
stand.update = stand_update

# Scene entities (house, well, mushroom, etc.)
#maison = ursina.Entity(model="data/casa/casa.fbx", texture="data/casa/casa.jpg", position=(0, 5, 0), scale=(0.1), shader=ursina.shaders.lit_with_shadows_shader)
# use converted OBJ to avoid .blend import failure in Ursina
puit = ursina.Entity(model="sources/models_compressed/Well.obj", texture="data/casa/Well_texture2.png", scale=(0.5), position=(-25, 1.5, 35), double_sided=True, collider="mesh", shader=ursina.shaders.lit_with_shadows_shader)
eau = ursina.Entity(model="quad", texture="data/casa/watta.jpg", rotation=(90, 0, 0), scale=(4.60), position=(-24.85, 4, 34.85), shader=ursina.shaders.lit_with_shadows_shader)
def on_well_click():
    selected_item = get_selected_hotbar_item()
    if selected_item and selected_item.item_name in ["Arrosoir rouillé", "Arrosoir en fer", "Arrosoir en or"]:
        dist = ((player.position.x - puit.position.x)**2 + (player.position.z - puit.position.z)**2)**0.5
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

puit.on_click = on_well_click

mushroom = ursina.Entity(model="data/casa/mushroom7.fbx", texture="data/casa/shroom_Base_Color2.png", position=(-40, 2, 2), scale=(0.03), double_sided=True, collider="box", shader=ursina.shaders.lit_with_shadows_shader)
#house_draft = ursina.Entity(model="data/casa/house-draft.fbx", texture="data/casa/1.jpg", position=(10, 5, 0), scale=(1.5, 1.5, 1.5), shader=ursina.shaders.lit_with_shadows_shader)

# Hint text shown when the player is close to the ATM
hint_text = ursina.Text(
    text="Click droit",
    position=(-0.5, 0.4),
    origin=(0, 0),
    background=True,
    scale=2,
    enabled=False,
)

# Variable globale pour gérer le délai entre les tirages
tirage_en_cours = False


def has_any_watering_can(names):
    inv = getattr(Inventory, "instance", None)
    if inv is None:
        return False
    return any(getattr(item, 'item_name', None) in names for item in inv.item_parent.children)


def replace_first_watering_can(old_names, new_name):
    """Remplace le premier arrosoir trouvé par la nouvelle version."""
    inv = getattr(Inventory, "instance", None)
    if inv is None:
        return False

    for item in inv.item_parent.children:
        if getattr(item, 'item_name', None) in old_names:
            item.item_name = new_name
            item.uses = None
            item.texture = texture_paths.get(new_name, new_name)
            try:
                item._update_tooltip_text()
            except Exception:
                pass
            return True
    return False


def apply_drawn_watering_can_upgrade(item_name):
    """Applique la progression d'arrosoir sans empiler plusieurs niveaux."""
    if item_name == "Arrosoir en fer":
        # Priorité: remplacer un rouillé existant.
        replaced = replace_first_watering_can(
            ["Arrosoir rouillé", "Arrosoir rouillé rempli"],
            "Arrosoir en fer"
        )
        if not replaced:
            inventory.add_item("Arrosoir en fer")
        return True

    if item_name == "Arrosoir en or":
        # Priorité: remplacer un fer, sinon un rouillé.
        replaced = replace_first_watering_can(
            ["Arrosoir en fer", "Arrosoir en fer rempli", "Arrosoir rouillé", "Arrosoir rouillé rempli"],
            "Arrosoir en or"
        )
        if not replaced:
            inventory.add_item("Arrosoir en or")
        return True

    return False

def make_1_wishes():
    """Fait 1 tirage aléatoire et ajoute une graine à l'inventaire"""
    global tirage_en_cours

    if mushroom_panel.visible:
        print("Fermez l'interface Champignon pour faire un tirage.")
        return
    
    # Vérifier si un tirage est déjà en cours
    if tirage_en_cours:
        print("Veuillez attendre avant de faire un nouveau tirage.")
        return
    
    # Marquer le tirage comme en cours
    tirage_en_cours = True
    
    # Pool de tirage : graines majoritaires + faible chance d'obtenir un arrosoir.
    draw_pool = []

    available_seed_keys = [key for key in graines.keys() if graines[key].rareté in [1, 2, 3, 4]]
    for key in available_seed_keys:
        seed = graines[key]
        weight = 85 if seed.rareté == 1 else 10 if seed.rareté == 2 else 4 if seed.rareté == 3 else 1
        draw_pool.append((seed.nom, seed.rareté, weight))

    # Arrosoirs tirables avec progression:
    # - Si or possédé: plus aucun arrosoir tirable
    # - Sinon si fer possédé: seulement or tirable
    # - Sinon: fer et or tirables
    has_iron = has_any_watering_can(["Arrosoir en fer", "Arrosoir en fer rempli"])
    has_gold = has_any_watering_can(["Arrosoir en or", "Arrosoir en or rempli"])

    if has_gold:
        drawable_cans = []
    elif has_iron:
        drawable_cans = ["Arrosoir en or"]
    else:
        drawable_cans = ["Arrosoir en fer", "Arrosoir en or"]

    for can_name in drawable_cans:
        if can_name not in arrosoirs:
            continue
        can = arrosoirs[can_name]
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
    
    # Les upgrades d'arrosoir peuvent remplacer un item existant sans case libre.
    is_can_upgrade = item_name2 in ["Arrosoir en fer", "Arrosoir en or"]
    can_receive = inventory.find_free_spot() is not None or is_can_upgrade

    if joueur.argent >= 10 and can_receive:
        # Afficher le résultat du tirage
        show_seed_result(item_name2, rarity)

        # Jouer le son d'achat du tirage.
        if achat_sound is not None:
            try:
                achat_sound.play()
            except Exception as e:
                print(f"Erreur lecture son d'achat: {e}")

        upgraded = apply_drawn_watering_can_upgrade(item_name2)
        if not upgraded:
            inventory.add_item(item_name2)
        matrice_inventaire()  # Mettre à jour l'affichage de l'inventaire
        joueur.argent -= 10  # Coût de 10 argents par tirage
        print("1 voeu réalisé! Objet ajouté à l'inventaire.")
    else:
        if joueur.argent < 10:
            print("Pas assez d'argent pour faire un tirage.")
        else:
            print("Inventaire plein, impossible d'ajouter la fleur.")
    
    # Fermer la fenêtre ATM après le tirage
    toggle_atm_interface()
    
    # Programmer la remise à zéro du délai après 5 secondes
    def reset_tirage():
        global tirage_en_cours
        tirage_en_cours = False
        print("Vous pouvez maintenant faire un nouveau tirage.")
    
    ursina.invoke(reset_tirage, delay=5)


def show_seed_result(seed_name, rarity):
    """Affiche l'image de l'objet tiré avec son niveau de rareté"""
    # Déterminer le texte de rareté
    rarity_text = ""
    if rarity == 1:
        rarity_text = "Commun"
    elif rarity == 2:
        rarity_text = "Rare"
    elif rarity == 3:
        rarity_text = "Epique"
    elif rarity == 4:
        rarity_text = "Légendaire"


    # Créer l'image de l'objet tiré
    item_texture = texture_paths.get(seed_name, f"../data/Graines/{seed_name}.png")
    seed_image = ursina.Entity(
        model='quad',
        texture=item_texture,
        scale=(0.3, 0.3),
        position=(0, 0.1),
        parent=ursina.camera.ui
    )
    
    # Créer le texte de rareté
    rarity_display = ursina.Text(
        text=rarity_text,
        position=(0, -0.15),
        scale=2,
        color=ursina.color.white,
        parent=ursina.camera.ui,
        origin=(0, 0)
    )
    
    # Fonction pour cacher l'affichage après 3 secondes
    def hide_result():
        seed_image.disable()
        rarity_display.disable()
    
    # Programmer la disparition après 3 secondes
    ursina.invoke(hide_result, delay=3)


def toggle_atm_interface():
    """Affiche/cache l'interface ATM"""
    if not atm_panel.visible and mushroom_panel.visible:
        print("Fermez l'interface Champignon avant d'ouvrir l'ATM.")
        return

    atm_panel.visible = not atm_panel.visible
    if atm_panel.visible:
        # Fermer l'inventaire si ouvert
        if iPan and iPan.visible:
            Inventory.toggle()
        # S'assurer que les couleurs des boutons sont correctement appliquées
        atm_button.color = ursina.color.green
        atm_button.highlight_color = ursina.color.lime
        atm_button.pressed_color = ursina.color.rgb(0, 100, 0)
        close_button.color = ursina.color.red
        close_button.highlight_color = ursina.color.pink
        close_button.pressed_color = ursina.color.rgb(100, 0, 0)
        # Désactiver les contrôles du joueur
        player.disable()
        fpc.mouse.locked = False
        player.cursor.visible = False
    else:
        # Réactiver les contrôles du joueur
        player.enable()
        fpc.mouse.locked = True
        player.cursor.visible = True


def sell_selected_flower():
    if atm_panel.visible:
        print("Fermez l'interface ATM pour vendre au Champignon.")
        return

    selected_item = get_selected_hotbar_item()
    if not selected_item or not getattr(selected_item, 'item_name', None):
        mushroom_panel.visible = False
        print("Ce n'est pas une fleur")
        player.enable()
        fpc.mouse.locked = True
        player.cursor.visible = True
        return

    item_name = selected_item.item_name
    rarete = None

    # Les graines ne sont pas des fleurs utilisables pour la vente ici
    if item_name in graines or item_name.lower().startswith("graines"):  # plus strict
        mushroom_panel.visible = False
        print("Ce n'est pas une fleur")
        player.enable()
        fpc.mouse.locked = True
        player.cursor.visible = True
        return

    if item_name in fleurs:
        rarete = fleurs[item_name].rareté
    else:
        # Item n'est pas une fleur connue
        mushroom_panel.visible = False
        print("Ce n'est pas une Fleur")
        player.enable()
        fpc.mouse.locked = True
        player.cursor.visible = True
        return

    gain = {1: 13, 2: 20, 3: 35, 4: 50}.get(rarete, 1)
    joueur.argent += gain
    print(f"{item_name} vendu ({'Commun' if rarete==1 else 'Rare' if rarete==2 else 'Epic' if rarete==3 else 'Légendaire'}), +{gain}€")

    if vente_sound is not None:
        try:
            vente_sound.play()
        except Exception as e:
            print(f"Erreur lecture son de vente: {e}")

    if getattr(selected_item, 'stack', 1) > 1:
        selected_item.stack -= 1
        try:
            selected_item._update_tooltip_text()
        except Exception:
            pass
    else:
        try:
            destroy(selected_item)
        except Exception:
            pass

    matrice_inventaire()

    # Fermer l'interface champignon après la vente
    mushroom_panel.visible = False
    player.enable()
    fpc.mouse.locked = True
    player.cursor.visible = True


def toggle_mushroom_interface():
    """Affiche/cache l'interface Champignon"""
    if not mushroom_panel.visible and atm_panel.visible:
        print("Fermez l'interface ATM avant d'ouvrir le Champignon.")
        return

    mushroom_panel.visible = not mushroom_panel.visible
    if mushroom_panel.visible:
        # Fermer l'inventaire si ouvert
        if iPan and iPan.visible:
            Inventory.toggle()
        # S'assurer que les couleurs des boutons sont correctement appliquées
        mushroom_button.color = ursina.color.blue
        mushroom_button.highlight_color = ursina.color.cyan
        mushroom_button.pressed_color = ursina.color.rgb(0, 0, 100)
        close_mushroom_button.color = ursina.color.red
        close_mushroom_button.highlight_color = ursina.color.pink
        close_mushroom_button.pressed_color = ursina.color.rgb(100, 0, 0)
        # Désactiver les contrôles du joueur
        player.disable()
        fpc.mouse.locked = False
        player.cursor.visible = False
    else:
        # Réactiver les contrôles du joueur
        player.enable()
        fpc.mouse.locked = True
        player.cursor.visible = True


# ATM Interface
atm_panel = ursina.Panel(
    parent=ursina.camera.ui,
    model='quad',
    scale=(0.6, 0.4),
    position=(0, 0),
    color=ursina.color.dark_gray,
    visible=False,
)

atm_title = ursina.Text(
    parent=atm_panel,
    text="Distributeur Automatique",
    position=(0, 0.15),
    scale=1.5,
    color=ursina.color.white,
)

atm_button = ursina.Button(
    parent=atm_panel,
    text="Faire 1 tirage",
    position=(0, -0.1),
    scale=(0.4, 0.1),
    on_click=make_1_wishes,
)

# Définir les couleurs après la création pour s'assurer qu'elles sont appliquées
atm_button.color = ursina.color.green
atm_button.highlight_color = ursina.color.lime
atm_button.pressed_color = ursina.color.rgb(0, 100, 0)

close_button = ursina.Button(
    parent=atm_panel,
    text="Fermer",
    position=(0, -0.25),
    scale=(0.2, 0.08),
    on_click=toggle_atm_interface,
)

# Définir les couleurs après la création pour s'assurer qu'elles sont appliquées
close_button.color = ursina.color.red
close_button.highlight_color = ursina.color.pink
close_button.pressed_color = ursina.color.rgb(100, 0, 0)

# Mushroom Interface
mushroom_panel = ursina.Panel(
    parent=ursina.camera.ui,
    model='quad',
    scale=(0.6, 0.4),
    position=(0, 0),
    color=ursina.color.dark_gray,
    visible=False,
)

mushroom_title = ursina.Text(
    parent=mushroom_panel,
    text="Champignon Magique",
    position=(0, 0.15),
    scale=1.5,
    color=ursina.color.white,
)

mushroom_button = ursina.Button(
    parent=mushroom_panel,
    text="Vendre La Fleurs dans la Main",
    position=(0, 0.2),
    scale=(0.6, 0.15),
    on_click=sell_selected_flower,
)

close_mushroom_button = ursina.Button(
    parent=mushroom_panel,
    text="Fermer",
    position=(0, -0.18),
    scale=(0.2, 0.08),
    on_click=toggle_mushroom_interface,
)


sun = ursina.DirectionalLight(shadow_map_resolution=(2048,2048))
sun.look_at(ursina.Vec3(-1, -1, -10))


# Mettre à jour la référence globale du joueur pour l'inventaire

Inventory.player = player

# Planter des fleurs sur le terrain en fonction de la hotbar du joueur
planted_flowers = []
ZONE_REWATER_TIMEOUT = 60


def destroy_plants_in_zone(zone):
    """Détruit toutes les pousses/fleurs liées à une zone et vide leur liste active."""
    destroyed_count = 0
    for plant in list(planted_flowers):
        if getattr(plant, '_zone', None) is zone:
            if getattr(plant, '_spot_pos', None) is not None:
                maps.release_occupied_spot(zone, plant._spot_pos)
            if plant in planted_flowers:
                planted_flowers.remove(plant)
            try:
                destroy(plant)
            except Exception:
                pass
            destroyed_count += 1
    return destroyed_count


def update_zone_dry_timers():
    """Si une zone sèche trop longtemps, détruit les plantes restantes de cette zone."""
    now = ursina.time.time()
    for zone in getattr(maps, 'zones', []):
        dry_since = getattr(zone, 'dry_since', None)
        if dry_since is None:
            continue
        if now - dry_since >= ZONE_REWATER_TIMEOUT:
            removed = destroy_plants_in_zone(zone)
            if removed > 0:
                print("Zone non arrosée depuis 2 minutes: pousses/fleurs détruites.")
            zone.dry_since = None


def bloom_plant(plant):
    """Fait passer une pousse en fleur mûre."""
    if plant not in planted_flowers:
        return
    if getattr(plant, 'growth_stage', 0) != 0:
        return

    zone = getattr(plant, '_zone', None)
    if zone is not None and not getattr(zone, 'is_watered', False):
        return

    flower_texture = texture_paths.get(plant.flower_name)
    for quad in plant._quads:
        quad.texture = flower_texture
    plant.growth_stage = 1
    print(f"'{plant.flower_name}' a poussé ! Cliquez dessus pour récolter.")

    # Après 3 fleurs poussées, la zone arrosée repasse en marron (sec).
    if zone is not None and getattr(zone, 'is_watered', False):
        zone.grown_in_cycle = getattr(zone, 'grown_in_cycle', 0) + 1
        if zone.grown_in_cycle >= 3:
            maps.reset_zone_to_dry(zone, start_dry_timer=True)
            print("La zone est redevenue marron. Ré-arrosez-la sous 2 minutes pour éviter la destruction des pousses/fleurs.")

    def harvest():
        if plant not in planted_flowers:
            return

        plant_zone = getattr(plant, '_zone', None)
        if plant_zone is not None and getattr(plant, '_spot_pos', None) is not None:
            maps.release_occupied_spot(plant_zone, plant._spot_pos)

        # Ajouter la fleur à l'inventaire
        inventory.add_item(plant.flower_name)
        matrice_inventaire()
        print(f"'{plant.flower_name}' récoltée et ajoutée à l'inventaire !")

        # Recréer le carré vert de plantation uniquement si la zone est arrosée.
        if plant_zone is not None and getattr(plant_zone, 'is_watered', False):
            maps.add_planting_spot(plant_zone, plant._spot_pos)

        if plant in planted_flowers:
            planted_flowers.remove(plant)
        destroy(plant)

    plant.on_click = harvest


def update_plant_growth():
    """La croissance avance uniquement quand la zone de la plante est arrosée."""
    dt = ursina.time.dt
    for plant in list(planted_flowers):
        if getattr(plant, 'growth_stage', 0) != 0:
            continue

        zone = getattr(plant, '_zone', None)
        if zone is not None and not getattr(zone, 'is_watered', False):
            # Zone non arrosée: croissance en pause.
            continue

        plant.age += dt
        if plant.age >= getattr(plant, 'growth_delay', 60):
            bloom_plant(plant)

def build_flower_name_from_item(item_name):
    if not item_name:
        return None
    # Accepte uniquement les graines : Graines de X ou Graines d'X
    if item_name.startswith("Graines de "):
        candidate = item_name.replace("Graines de ", "")
        if candidate in fleurs:
            return candidate
    if item_name.startswith("Graines d'"):
        candidate = item_name.replace("Graines d'", "")
        if candidate in fleurs:
            return candidate
    return None


def plant_selected_from_hotbar():
    selected_item = get_selected_hotbar_item()
    if selected_item is None:
        print("Aucun item sélectionné dans la hotbar")
        return False

    flower_name = build_flower_name_from_item(selected_item.item_name)
    if flower_name is None:
        print(f"L'item sélectionné '{selected_item.item_name}' n'est pas une graine valide")
        return False

    # détection du point visé via raycast.
    hit_info = ursina.raycast(player.position, player.forward, distance=20, ignore=[player])
    if not hit_info.hit:
        print("Aucune surface visée pour planter")
        return False

    # planter uniquement sur les cercles de plantation
    planting_spots = [spot for zone in maps.zones for spot in getattr(zone, 'planting_spots', [])]
    if hit_info.entity not in planting_spots:
        print("Cliquez sur un cercle vert pour planter")
        return False

    plant_pos = ursina.Vec3(hit_info.entity.x, 1.8, hit_info.entity.z)
    spot_pos = ursina.Vec3(hit_info.entity.x, hit_info.entity.y, hit_info.entity.z)

    # Trouver la zone propriétaire du carré vert et le retirer de sa liste
    spot_zone = None
    for z in maps.zones:
        if hit_info.entity in getattr(z, 'planting_spots', []):
            spot_zone = z
            z.planting_spots.remove(hit_info.entity)
            break

    # Créer une entité parent pour la fleur
    plant = ursina.Entity(
        position=plant_pos,
        collider='box'
    )
    # Afficher la Pousse à la plantation (la fleur poussera plus tard)
    sprout_texture = texture_paths.get("Pousse")
    plant1 = ursina.Entity(
        parent=plant,
        model='quad',
        texture=sprout_texture,
        color=ursina.color.white,
        scale=(4, 4, 4),
        rotation_y=45,
        double_sided=True,
        shader=ursina.shaders.lit_with_shadows_shader
    )
    plant2 = ursina.Entity(
        parent=plant,
        model='quad',
        texture=sprout_texture,
        color=ursina.color.white,
        scale=(4, 4, 4),
        rotation_y=135,
        double_sided=True,
        shader=ursina.shaders.lit_with_shadows_shader
    )
    plant.flower_name = flower_name  # La fleur finale est mémorisée
    plant.growth_stage = 0
    plant.age = 0.0
    plant._quads = [plant1, plant2]
    plant._spot_pos = spot_pos
    plant._zone = spot_zone

    if spot_zone is not None:
        maps.register_occupied_spot(spot_zone, spot_pos)

    planted_flowers.append(plant)

    # Délai de pousse selon la rareté : Commun=60s, Rare=100s, Epic=150s, Légendaire=300s
    rarity = fleurs[flower_name].rareté
    growth_delay = {1: 60, 2: 100, 3: 150, 4: 300}.get(rarity, 60)
    plant.growth_delay = growth_delay

    # Supprimer le carré vert après plantation
    destroy(hit_info.entity)

    # Consomme la graine/fleur de l'inventaire.
    if getattr(selected_item, 'stack', 1) > 1:
        selected_item.stack -= 1
        try:
            selected_item._update_tooltip_text()
        except Exception:
            pass
    else:
        try:
            destroy(selected_item)
        except Exception:
            pass

    matrice_inventaire()
    print(f"Plante '{flower_name}' plantée à {plant_pos}")
    return True

def input(key):
    # Bloquer l'ouverture/fermeture de l'inventaire pendant les interfaces ATM/Champignon.
    if key == 'e' and (atm_panel.visible or mushroom_panel.visible):
        return

    try:
        inv_input(key, player, fpc.mouse)
    except Exception as e:
        print("inv_input error:", e)

    if key == 'right mouse down':
        # Empêcher de basculer vers l'autre interface tant qu'une interface est ouverte.
        if atm_panel.visible or mushroom_panel.visible:
            return

        if hint_text.enabled:
            if stand.hovered:
                toggle_atm_interface()
            elif mushroom.hovered:
                toggle_mushroom_interface()

    if key == 'left mouse down':
        # Ne pas planter si l'interface ATM ou champignon est visible
        if not atm_panel.visible and not mushroom_panel.visible:
            planted = plant_selected_from_hotbar()
            if planted:
                print("Plante semée depuis la hotbar")

app.run()
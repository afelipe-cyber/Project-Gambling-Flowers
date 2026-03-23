from importlib.util import *
from pathlib import Path
import ursina
from ursina.shaders import lit_with_shadows_shader
import ursina.prefabs.first_person_controller as fpc
from Inventaire import *
import Objets
import maps
import random
import Joueur
import pygame as pg
from math import sin

# Make assets resolvable from project root (not /sources).
ursina.application.asset_folder = Path(__file__).resolve().parent.parent

app = ursina.Ursina()

# créer le ciel et la lumière
shader = ursina.shaders.lit_with_shadows_shader
sky = ursina.Sky(texture="data/atm/sky3.jpg")

# Initialiser l'inventaire
inventory = init_inventory()

# Ajouter des arrosoirs pour test
inventory.add_item("Arrosoir rouillé rempli")
inventory.add_item("Arrosoir en fer rempli")
inventory.add_item("Arrosoir en or rempli")
matrice_inventaire()  # Mettre à jour l'affichage

# Afficher argents du joueur
joueur = Joueur.Joueur("Player", argent=200, inventaire=inventory)
maps.joueur = joueur
argent_text = joueur.affichage_argent()


def update():
    joueur.affichage_argent()


# Créer le terrain
platform = maps.create_map()
maps.fence()
maps.init_purchase_panel()

player = fpc.FirstPersonController(position=(-10.55, 2, -10), scale=2.5, speed=20)
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
stand = ursina.Entity(model="data/atm/atm.obj", texture="data/atm/atm2.jpg", double_sided=True, parent=stand_parent, position=(0, -3, 1.51), scale=(60, 60, 60), collider="box", shader=ursina.shaders.lit_with_shadows_shader)
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
puit = ursina.Entity(model="sources/models_compressed/Well.obj", texture="data/casa/Well_texture2.png", scale=(0.5), position=(-25, 1.2, 35), double_sided=True, collider="mesh", shader=ursina.shaders.lit_with_shadows_shader)
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

def make_1_wishes():
    """Fait 1 tirage aléatoire et ajoute une graine à l'inventaire"""
    global tirage_en_cours
    
    # Vérifier si un tirage est déjà en cours
    if tirage_en_cours:
        print("Veuillez attendre avant de faire un nouveau tirage.")
        return
    
    # Marquer le tirage comme en cours
    tirage_en_cours = True
    
    # Sélectionner uniquement les graines de rareté Commune (1), Rare (2), Epic (3) ou Légendaire (4)
    available_items2 = [key for key in graines.keys() if graines[key].rareté in [1, 2, 3, 4]]
    # Poids : Commune = 85%, Rare = 10%, Epic = 4%, Légendaire = 1%
    weights = [85 if graines[key].rareté == 1 else 10 if graines[key].rareté == 2 else 4 if graines[key].rareté == 3 else 1 for key in available_items2]

    key = random.choices(available_items2, weights=weights, k=1)[0]
    item_name2 = graines[key].nom
    rarity = graines[key].rareté
    
    if joueur.argent >= 10 and inventory.find_free_spot() is not None:
        # Afficher le résultat du tirage
        show_seed_result(item_name2, rarity)
        
        inventory.add_item(item_name2)
        matrice_inventaire()  # Mettre à jour l'affichage de l'inventaire
        joueur.argent -= 10  # Coût de 10 argents par tirage
        print("1 voeu réalisé! Fleur ajoutée à l'inventaire.")
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
    """Affiche l'image de la graine tirée avec son niveau de rareté"""
    # Déterminer le texte de rareté
    rarity_text = ""
    if rarity == 1:
        rarity_text = "Commun"
    elif rarity == 2:
        rarity_text = "Rare"
    elif rarity == 3:
        rarity_text = "Epic"
    elif rarity == 4:
        rarity_text = "Légendaire"


    # Créer l'image de la graine
    seed_image = ursina.Entity(
        model='quad',
        texture=f"../data/Graines/{seed_name}.png",
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
    selected_item = get_selected_hotbar_item()
    if not selected_item or not getattr(selected_item, 'item_name', None):
        mushroom_panel.visible = False
        print("Ce n'est pas une Fleur")
        player.enable()
        fpc.mouse.locked = True
        player.cursor.visible = True
        return

    item_name = selected_item.item_name
    rarete = None

    # Les graines ne sont pas des fleurs utilisables pour la vente ici
    if item_name in graines or item_name.lower().startswith("graines"):  # plus strict
        mushroom_panel.visible = False
        print("Ce n'est pas une Fleur")
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

    plant_pos = hit_info.point + ursina.Vec3(0, 0.5, 0)
    plant = ursina.Entity(
        model='quad',
        texture=texture_paths.get(flower_name),
        color=ursina.color.white,
        position=plant_pos,
        scale=(1.5, 1.5, 1.5),
        rotation_x=90,
        collider='box',
        shader=ursina.shaders.lit_with_shadows_shader
    )
    plant.flower_name = flower_name
    plant.growth_stage = 0
    plant.age = 0.0

    planted_flowers.append(plant)

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
    try:
        inv_input(key, player, fpc.mouse)
    except Exception as e:
        print("inv_input error:", e)

    if key == 'right mouse down':
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
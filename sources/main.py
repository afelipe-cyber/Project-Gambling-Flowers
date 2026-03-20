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
# import PIL
# import time
# import random as rd
# import pygame as pg
from math import sin

# Make assets resolvable from project root (not /sources).
ursina.application.asset_folder = Path(__file__).resolve().parent.parent

app = ursina.Ursina()

# créer le ciel et la lumière
shader = ursina.shaders.lit_with_shadows_shader
sky = ursina.Sky(texture="data/atm/sky3.jpg")

# Initialiser l'inventaire
inventory = init_inventory()

# Afficher argents du joueur


# Créer le terrain
platform = maps.create_map()
maps.fence()

player = fpc.FirstPersonController(position=(-10.55, 2, -10), scale=2.5, speed=20)


def stand_update():
    global stand, stand_animation, stand_parent, hint_text, player
    # Keep ATM static (no rotation)
    # stand_parent.rotation_y += 40 * ursina.time.dt
    # stand_animation.rotation_y += 40 * ursina.time.dt
    stand.y += sin(ursina.time.time() * 10) * 0.01
    stand_animation.y += sin(ursina.time.time() * 10) * 0.01

    # Cycle flower textures if available.
    if hasattr(stand_animation, "flower_textures") and stand_animation.flower_textures:
        stand_animation._texture_i = int(ursina.time.time() * 1) % len(stand_animation.flower_textures)
        stand_animation.texture = stand_animation.flower_textures[stand_animation._texture_i]

    # Show a prompt when the player is close to the ATM.
    # Adjust `proximity_threshold` to change how close the player must get.
    proximity_threshold = 6.0
    dx = player.x - stand.world_x
    dy = player.y - stand.world_y
    dz = player.z - stand.world_z
    dist = (dx*dx + dy*dy + dz*dz) ** 0.5
    hint_text.enabled = dist <= proximity_threshold

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
maison = ursina.Entity(model="data/casa/casa.fbx", position=(0, 5, 0), scale=(0.5, 0.5, 0.5), shader=ursina.shaders.lit_with_shadows_shader)
puit = ursina.Entity(model="data/casa/Well.blend", texture="data/casa/Well_texture.png", scale=(1, 1, 1), position=(0, 0, 0), shader=ursina.shaders.lit_with_shadows_shader)
mushroom = ursina.Entity(model="data/casa/mushroom7.fbx", texture="data/casa/shader/mushroom_diff.png", position=(0, 0, 2), scale=(0.5, 0.5, 0.5), shader=ursina.shaders.lit_with_shadows_shader)
house_draft = ursina.Entity(model="data/casa/house-draft.fbx", position=(10, 5, 0), scale=(1.5, 1.5, 1.5), shader=ursina.shaders.lit_with_shadows_shader)

# Hint text shown when the player is close to the ATM
hint_text = ursina.Text(
    text="Click droit",
    position=(-0.5, 0.4),
    origin=(0, 0),
    background=True,
    scale=2,
    enabled=False,
)

def make_1_wishes():
    """Fait 1 tirage aléatoire et ajoute une graine à l'inventaire"""
    available_items2=list(graines.keys())
    key = random.choice(available_items2)
    item_name2 = graines[key].nom
    inventory.add_item(item_name2)
    matrice_inventaire()  # Mettre à jour l'affichage de l'inventaire
    print("1 voeu réalisé! Fleur ajoutée à l'inventaire.")

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

    # planter uniquement sur terrain ou zone clickable.
    if not hasattr(hit_info.entity, 'collider'):
        print("Surface non valide pour plantation")
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
        print(f"Right click detected, hint_text.enabled: {hint_text.enabled}, stand.hovered: {stand.hovered}")
        if hint_text.enabled:
            print("Hint is enabled")
            if stand.hovered:
                print("Stand is hovered, toggling ATM interface")
                # Toggle ATM interface
                toggle_atm_interface()
            else:
                print("Stand not hovered")
        else:
            print("Hint not enabled")

    if key == 'left mouse down':
        # Ne pas planter si l'interface ATM est visible
        if not atm_panel.visible:
            planted = plant_selected_from_hotbar()
            if planted:
                print("Plante semée depuis la hotbar")

app.run()
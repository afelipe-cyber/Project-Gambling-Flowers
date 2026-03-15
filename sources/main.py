from importlib.util import *
from pathlib import Path
import ursina
from ursina.shaders import lit_with_shadows_shader
import ursina.prefabs.first_person_controller as fpc
from Inventaire import *
import Objets
import maps
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

# Hint text shown when the player is close to the ATM
hint_text = ursina.Text(
    text="Click droit",
    position=(-0.5, 0.4),
    origin=(0, 0),
    background=True,
    scale=2,
    enabled=False,
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
    if item_name in fleurs:
        return item_name
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
        print(f"L'item sélectionné '{selected_item.item_name}' n'est pas une graine/fleur valide")
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


# # Peupler l'inventaire avec quelques fleurs au démarrage
# try:
#     for _ in range(5):
#         Item.new_item(rd.choice(mins))
# except Exception as e:
#     print('Erreur lors de la création d\'items d\'inventaire :', e)

# # Aussi remplir quelques cases du panneau d'inventaire (non-hotbar)
# try:
#     inv_slots = [h for h in hotspots if not h.onHotbar]
#     for i in range(min(5, len(inv_slots))):
#         h = inv_slots[i]
#         b = Item(rd.choice(mins))
#         b.currentSpot = h
#         items.append(b)
#         h.item = b
#         h.occupied = True
#         h.stack = 1
#         b.onHotbar = False
#         b.visible = False
#         b.x = h.x
#         b.y = h.y
#         b.update_stack_text()
# except Exception as e:
#     print('Erreur lors du remplissage du panneau d\'inventaire :', e)



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
                print("Stand is hovered, toggling inventory")
                # Toggle inventory
                Inventory.toggle()
                # Toggle player controls based on player state
                if player.enabled:
                    player.disable()
                    fpc.mouse.locked = False
                    player.cursor.visible = False
                else:
                    player.enable()
                    fpc.mouse.locked = True
                    player.cursor.visible = True
            else:
                print("Stand not hovered")
        else:
            print("Hint not enabled")

    if key == 'left mouse down':
        planted = plant_selected_from_hotbar()
        if planted:
            print("Plante semée depuis la hotbar")

app.run()
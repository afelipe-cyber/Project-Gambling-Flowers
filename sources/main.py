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
    global stand, stand_animation, stand_parent
    # Keep ATM static (no rotation)
    # stand_parent.rotation_y += 40 * ursina.time.dt
    # stand_animation.rotation_y += 40 * ursina.time.dt
    stand.y += sin(ursina.time.time() * 10) * 0.01
    stand_animation.y += sin(ursina.time.time() * 10) * 0.01

    # Cycle flower textures if available.
    if hasattr(stand_animation, "flower_textures") and stand_animation.flower_textures:
        stand_animation._texture_i = int(ursina.time.time() * 1) % len(stand_animation.flower_textures)
        stand_animation.texture = stand_animation.flower_textures[stand_animation._texture_i]

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
 

sun = ursina.DirectionalLight(shadow_map_resolution=(2048,2048))
sun.look_at(ursina.Vec3(-1, -1, -10))


# Mettre à jour la référence globale du joueur pour l'inventaire

Inventory.player = player



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

app.run()
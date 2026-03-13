from importlib.util import *
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

app = ursina.Ursina()

# créer le ciel et la lumière
shader = ursina.shaders.lit_with_shadows_shader
sky = ursina.Sky(texture="../data/atm/sky3.jpg")

# Initialiser l'inventaire
inventory = init_inventory()

# Créer le terrain
platform = maps.create_map()
maps.fence()
maps.stand_de_vente()

player = fpc.FirstPersonController(y=100, scale=2.5, speed=20)







def stand_update():
    global stand, stand_animation, stand_parent
    stand_parent.rotation_y += 40 * ursina.time.dt 
    #stand_animation.rotation_y += 20 * ursina.time.dt
    stand.y += sin(ursina.time.time() * 10) * 0.01
    stand_animation.y += sin(ursina.time.time() * 10) * 0.01

stand_parent = ursina.Entity(position=(-10.55, 4, -20.95))
stand = ursina.Entity(model="../data/atm/atm.obj", texture="../data/atm/atm2.jpg", double_sided=True, parent=stand_parent, position=(0, -0.4, 1.5), scale=(0.003, 0.003, 0.003), collider="box", shader=ursina.shaders.lit_with_shadows_shader)
stand_animation = ursina.Animation("../data/Fleurs/fleur", double_sided=True, parent=stand_parent, position=(0, -0.9, 1.51), scale=(2.5, 2.5, 2.5), fps=1, loop=True, autoplay=True)
stand.update = stand_update






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

# Fix for ursina importlib.util compatibility issue
from importlib.util import *

import ursina
import ursina.prefabs.first_person_controller as fpc
# from inventaire import *
from InventaireBIS import *
import PIL
import time
import random as rd
import pygame as pg


app = ursina.Ursina()

# Créer le terrain
platform = ursina.Entity(model='plane', texture='grass', scale=(100, 1, 100), collider='mesh')

def on_zone_click(zone):
    # ajouter: doit vérifier si le joueur à assez d'argent pour acheter la zone
    new_color = (zone.color[0] * 0.7, zone.color[1] * 0.7, zone.color[2] * 0.7, zone.color[3])
    zone.color = new_color
    zone.collider = None  # Désactiver le collider après le clic

# Jardin séparé en zones de 18x15
for i in range(2):  # 2 zones en largeur
    for j in range(5):  # 5 zones en profondeur
        x = 20 + (i - 0.5) * 18
        z = 0 + (j - 2) * 15
        zone = ursina.Entity(
            model="plane",
            scale=(18, 1, 15),
            position=(x, 0.01, z),
            color=ursina.color.rgb(139 / 255, 69 / 255, 19 / 255),
            texture=None,
            collider="mesh",
        )
        zone.on_click = lambda z=zone: on_zone_click(z)

player = fpc.FirstPersonController(y=100, scale=2, speed=20)

def fence():
    for i in range(30):
        vertical = ursina.Entity(model="cube", color = color.rgb(169 / 255, 124 / 255, 75 / 255) , texture="brick", position=(49-3.375*i, 1, 49), scale=(0.7, 4.5, 0.7), collider="mesh")
    
    horizontal_1 = ursina.Entity(model="cube", color = color.rgb(169 / 255, 124 / 255, 75 / 255) , texture="brick", position=(0, 2.6, 49), scale=(100, 0.43, 0.35), collider="mesh")
    horizontal_2 = ursina.Entity(model="cube", color = color.rgb(169 / 255, 124 / 255, 75 / 255) , texture="brick", position=(0, 1.7, 49), scale=(100, 0.43, 0.35), collider="mesh")

    for i in range(29):
        vertical = ursina.Entity(model="cube", color = color.rgb(169 / 255, 124 / 255, 75 / 255) , texture="brick", position=(49, 1, 45.625-3.375*i), scale=(0.7, 4.5, 0.7), collider="mesh")
    
    horizontal_1 = ursina.Entity(model="cube", color = color.rgb(169 / 255, 124 / 255, 75 / 255) , texture="brick", position=(49, 2.6, 0), scale=(0.35, 0.43, 100), collider="mesh")
    horizontal_2 = ursina.Entity(model="cube", color = color.rgb(169 / 255, 124 / 255, 75 / 255) , texture="brick", position=(49, 1.7, 0), scale=(0.35, 0.43, 100), collider="mesh")

    for i in range(30):
        vertical = ursina.Entity(model="cube", color = color.rgb(169 / 255, 124 / 255, 75 / 255) , texture="brick", position=(49-3.375*i, 1, -48.875), scale=(0.7, 4.5, 0.7), collider="mesh")

    horizontal_1 = ursina.Entity(model="cube", color = color.rgb(169 / 255, 124 / 255, 75 / 255) , texture="brick", position=(-49, 2.6, 0), scale=(0.35, 0.43, 100), collider="mesh")
    horizontal_2 = ursina.Entity(model="cube", color = color.rgb(169 / 255, 124 / 255, 75 / 255) , texture="brick", position=(-49, 1.7, 0), scale=(0.35, 0.43, 100), collider="mesh")

    for i in range(29):
        vertical = ursina.Entity(model="cube", color = color.rgb(169 / 255, 124 / 255, 75 / 255) , texture="brick", position=(-48.875, 1, 45.625-3.375*i), scale=(0.7, 4.5, 0.7), collider="mesh")

    horizontal_1 = ursina.Entity(model="cube", color = color.rgb(169 / 255, 124 / 255, 75 / 255) , texture="brick", position=(0, 2.6, -49), scale=(100, 0.43, 0.35), collider="mesh")
    horizontal_2 = ursina.Entity(model="cube", color = color.rgb(169 / 255, 124 / 255, 75 / 255) , texture="brick", position=(0, 1.7, -49), scale=(100, 0.43, 0.35), collider="mesh")

fence()


def stand_de_vente():
    base = ursina.Entity(model="cube", color = color.rgb(0 / 255, 90 / 255, 90 / 255) , texture="cobblestone", position=(-20, 0, -20), scale=(20, 1, 30), collider="mesh")

stand_de_vente()


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


# def input(key):
#     try:
#         inv_input(key, player, fpc.mouse)
#     except Exception as e:
#         print("inv_input error:", e)




app.run()
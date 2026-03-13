
# Fix for ursina importlib.util compatibility issue
import maps
from importlib.util import *
import InventaireBIS
import ursina
import ursina.prefabs.first_person_controller as fpc
# from inventaire import *
from InventaireBIS import *
import PIL
import time
import random as rd
import pygame as pg


app = ursina.Ursina()

# Initialiser l'inventaire
inventory = init_inventory()

# Créer le terrain
platform = maps.create_map()
fence = maps.fence()
stand_de_vente = maps.stand_de_vente()

player = fpc.FirstPersonController(y=100, scale=2.5, speed=20)

# Mettre à jour la référence globale du joueur pour l'inventaire

InventaireBIS.player = player








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
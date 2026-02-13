
import ursina
import ursina.prefabs.first_person_controller as fpc
import pathfinding as pf
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
        zone = ursina.Entity(model='plane', scale=(18, 1, 15), position=(x, 0.01, z), 
                           color=ursina.color.rgb(139/255, 69/255, 19/255), texture=None, collider='mesh')
        zone.on_click = lambda z=zone: on_zone_click(z)

player = fpc.FirstPersonController(y=100, scale=2, speed=20)

app.run()
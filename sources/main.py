
# Fix for ursina importlib.util compatibility issue
from importlib.util import*

import ursina
from ursina.shaders import lit_with_shadows_shader
import ursina.prefabs.first_person_controller as fpc
from inventaire import*
import PIL
import time
import random as rd
import pygame as pg
from math import sin


app = ursina.Ursina()

# créer le ciel et la lumière
shader = ursina.shaders.lit_with_shadows_shader
#    sky = ursina.Entity(model="sphere", texture="../data/atm/sky3.jpg", double_sided=True, position=(0,0,0), scale=(200, 200, 200), collider="box")
sky = ursina.Sky(texture="../data/atm/sky3.jpg")

# Créer le terrain
platform = ursina.Entity(model='cube', texture='grass', position=(0, -2, 0), scale=(100, 5, 100), collider='box', shader=ursina.shaders.lit_with_shadows_shader)

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
            model="cube",
            scale=(18, 5, 15),
            position=(x, -1.99, z),
            color=ursina.color.rgb(139 / 255, 69 / 255, 19 / 255),
            texture=None,
            collider="box",
            shader=ursina.shaders.lit_with_shadows_shader,
        )
        zone.on_click = lambda z=zone: on_zone_click(z)

player = fpc.FirstPersonController(y=100, scale=2.5, speed=20)

def fence():
    for i in range(30):
        vertical = ursina.Entity(model="cube", color = color.rgb(169 / 255, 124 / 255, 75 / 255) , texture="brick", position=(49-3.375*i, 1, 49), scale=(0.7, 4.5, 0.7), collider="box", shader=ursina.shaders.lit_with_shadows_shader)
    
    horizontal_1 = ursina.Entity(model="cube", color = color.rgb(169 / 255, 124 / 255, 75 / 255) , texture="brick", position=(0, 2.6, 49), scale=(100, 0.43, 0.35), collider="box",shader=ursina.shaders.lit_with_shadows_shader)
    horizontal_2 = ursina.Entity(model="cube", color = color.rgb(169 / 255, 124 / 255, 75 / 255) , texture="brick", position=(0, 1.7, 49), scale=(100, 0.43, 0.35), collider="box",shader=ursina.shaders.lit_with_shadows_shader)

    for i in range(29):
        vertical = ursina.Entity(model="cube", color = color.rgb(169 / 255, 124 / 255, 75 / 255) , texture="brick", position=(49, 1, 45.625-3.375*i), scale=(0.7, 4.5, 0.7), collider="box",shader=ursina.shaders.lit_with_shadows_shader)
    
    horizontal_1 = ursina.Entity(model="cube", color = color.rgb(169 / 255, 124 / 255, 75 / 255) , texture="brick", position=(49, 2.6, 0), scale=(0.35, 0.43, 100), collider="box",shader=ursina.shaders.lit_with_shadows_shader)
    horizontal_2 = ursina.Entity(model="cube", color = color.rgb(169 / 255, 124 / 255, 75 / 255) , texture="brick", position=(49, 1.7, 0), scale=(0.35, 0.43, 100), collider="box",shader=ursina.shaders.lit_with_shadows_shader)

    for i in range(30):
        vertical = ursina.Entity(model="cube", color = color.rgb(169 / 255, 124 / 255, 75 / 255) , texture="brick", position=(49-3.375*i, 1, -48.875), scale=(0.7, 4.5, 0.7), collider="box",shader=ursina.shaders.lit_with_shadows_shader)

    horizontal_1 = ursina.Entity(model="cube", color = color.rgb(169 / 255, 124 / 255, 75 / 255) , texture="brick", position=(-48.9, 2.6, 0), scale=(0.35, 0.43, 100), collider="box",shader=ursina.shaders.lit_with_shadows_shader)
    horizontal_2 = ursina.Entity(model="cube", color = color.rgb(169 / 255, 124 / 255, 75 / 255) , texture="brick", position=(-48.9, 1.7, 0), scale=(0.35, 0.43, 100), collider="box",shader=ursina.shaders.lit_with_shadows_shader)

    for i in range(29):
        vertical = ursina.Entity(model="cube", color = color.rgb(169 / 255, 124 / 255, 75 / 255) , texture="brick", position=(-48.875, 1, 45.625-3.375*i), scale=(0.7, 4.5, 0.7), collider="box",shader=ursina.shaders.lit_with_shadows_shader)

    horizontal_1 = ursina.Entity(model="cube", color = color.rgb(169 / 255, 124 / 255, 75 / 255) , texture="brick", position=(0, 2.6, -48.9), scale=(100, 0.43, 0.35), collider="box",shader=ursina.shaders.lit_with_shadows_shader)
    horizontal_2 = ursina.Entity(model="cube", color = color.rgb(169 / 255, 124 / 255, 75 / 255) , texture="brick", position=(0, 1.7, -49), scale=(100, 0.43, 0.35), collider="box",shader=ursina.shaders.lit_with_shadows_shader)

fence()


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

def stand_de_vente():
    base = ursina.Entity(model="cube", color = color.rgb(0 / 255, 90 / 255, 90 / 255) , texture="None", position=(-20, 0, -20), scale=(20, 1, 30), collider="box")
    fond = ursina.Entity(model="cube", color = color.rgb(0 / 255, 90 / 255, 90 / 255) , texture="brick", position=(-29, 1.5, -22), scale=(1, 20, 22.9), collider="box")
    side = ursina.Entity(model="cube", color = color.rgb(0 / 255, 90 / 255, 90 / 255) , texture="brick", position=(-23.55, 1.5, -33), scale=(12, 20, 1), collider="box")
    side = ursina.Entity(model="cube", color = color.rgb(0 / 255, 90 / 255, 90 / 255) , texture="brick", position=(-23.55, 1.5, -10.5), scale=(12, 20, 1), collider="box")
    facade = ursina.Entity(model="cube", color = color.rgb(0 / 255, 130 / 255, 110 / 255) , texture="brick", position=(-17.72, 0, -26.95), scale=(0.5, 9, 12.6), collider="box")
    arete = ursina.Entity(model="cube", color = color.rgb(0 / 255, 130 / 255, 110 / 255) , texture="brick", position=(-17.55, 0, -33), scale=(0.3, 23, 0.8), collider="box")
    arete = ursina.Entity(model="cube", color = color.rgb(0 / 255, 130 / 255, 110 / 255) , texture="brick", position=(-17.55, 0, -21), scale=(0.3, 23, 0.8), collider="box")
    arete = ursina.Entity(model="cube", color = color.rgb(0 / 255, 130 / 255, 110 / 255) , texture="brick", position=(-17.55, 9.5, -21.6), scale=(0.299, 0.5, 22.9), collider="box")
    arete = ursina.Entity(model="cube", color = color.rgb(0 / 255, 130 / 255, 110 / 255) , texture="brick", position=(-17.55, 0, -10.5), scale=(0.3, 23, 0.8), collider="box")
    porte_bas = ursina.Entity(model="cube", color = color.rgb(0 / 255, 130 / 255, 110 / 255) , texture="brick", position=(-17.55, 0, -18.5), scale=(0.1, 8.7, 5), collider="box")
    arete_entre_porte = ursina.Entity(model="cube", color = color.rgb(0 / 255, 130 / 255, 110 / 255) , texture="brick", position=(-17.55, 0, -15.75), scale=(0.3, 23, 0.8), collider="box")
    porte_bas = ursina.Entity(model="cube", color = color.rgb(0 / 255, 130 / 255, 110 / 255) , texture="brick", position=(-17.55, 0, -13.125), scale=(0.1, 8.7, 5), collider="box")
    cadre_porte = ursina.Entity(model="cube", color = color.rgb(0 / 255, 130 / 255, 110 / 255) , texture="brick", position=(-17.55, 4.5, -20.395), scale=(0.2, 10, 0.4), collider="box")
    cadre_porte = ursina.Entity(model="cube", color = color.rgb(0 / 255, 130 / 255, 110 / 255) , texture="brick", position=(-17.55, 4.5, -16.35), scale=(0.2, 10, 0.4), collider="box")

#    stand = ursina.Entity(model="../data/casa/casa.obj", texture="brick", position=(-17.55, 2, -26.95), scale=(0.5, 9, 10), collider="box")    
    sun = ursina.lights.DirectionalLight(shadow_map_resolution=(2048,2048))
    sun.look_at(Vec3(-1,-1,-10))
stand_de_vente()


# Peupler l'inventaire avec quelques fleurs au démarrage
try:
    for _ in range(5):
        Item.new_item(rd.choice(mins))
except Exception as e:
    print('Erreur lors de la création d\'items d\'inventaire :', e)

# Aussi remplir quelques cases du panneau d'inventaire (non-hotbar)
try:
    inv_slots = [h for h in hotspots if not h.onHotbar]
    for i in range(min(5, len(inv_slots))):
        h = inv_slots[i]
        b = Item(rd.choice(mins))
        b.currentSpot = h
        items.append(b)
        h.item = b
        h.occupied = True
        h.stack = 1
        b.onHotbar = False
        b.visible = False
        b.x = h.x
        b.y = h.y
        b.update_stack_text()
except Exception as e:
    print('Erreur lors du remplissage du panneau d\'inventaire :', e)


def input(key):
    try:
        inv_input(key, player, fpc.mouse)
    except Exception as e:
        print("inv_input error:", e)
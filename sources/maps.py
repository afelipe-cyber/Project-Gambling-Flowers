import ursina 
from importlib.util import *
import ursina.prefabs.first_person_controller as fpc

# Global joueur reference, set from main.py
joueur = None
player = None

# Purchase panel
purchase_panel = None
current_zone = None

def init_purchase_panel():
    global purchase_panel
    purchase_panel = ursina.Panel(
        parent=ursina.camera.ui,
        model='quad',
        scale=(0.6, 0.4),
        position=(0, 0),
        color=ursina.color.dark_gray,
        visible=False,
    )
    
    purchase_title = ursina.Text(
        parent=purchase_panel,
        text="Acheter zone 50 pièces",
        position=(0, 0),
        scale=1.2,
        color=ursina.color.red,
        z=-0.4,
        enabled=True,
    )
    
    yes_button = ursina.Button(
        parent=purchase_panel,
        text="Oui",
        position=(-0.15, -0.1),
        scale=(0.2, 0.1),
        on_click=confirm_purchase,
    )
    
    no_button = ursina.Button(
        parent=purchase_panel,
        text="Non",
        position=(0.15, -0.1),
        scale=(0.2, 0.1),
        on_click=cancel_purchase,
    )

def confirm_purchase():
    global current_zone, joueur
    if current_zone and joueur and joueur.argent >= 50:
        joueur.argent -= 50
        current_zone.color = ursina.color.rgb(139 / 255, 69 / 255, 19 / 255)  # Marron
        current_zone.collider = None  # Remove collider after purchase
        print("Zone achetée!")
    purchase_panel.visible = False
    # Réactiver les contrôles du joueur
    player.enable()
    fpc.mouse.locked = True
    player.cursor.visible = True

def cancel_purchase():
    global purchase_panel
    purchase_panel.visible = False
    # Réactiver les contrôles du joueur
    player.enable()
    fpc.mouse.locked = True
    player.cursor.visible = True


def create_map():
    platform = ursina.Entity(model='cube', texture='grass', scale=(100, 1, 100), collider='box', shader= ursina.shaders.lit_with_shadows_shader)
    for i in range(2):  # 2 zones en largeur
        for j in range(5):  # 5 zones en profondeur
            x = 20 + (i - 0.5) * 18
            z = 0 + (j - 2) * 15
            # Première zone (i=0, j=0) en marron, les autres en gris
            if i == 0 and j == 0:
                zone_color = ursina.color.rgb(139 / 255, 69 / 255, 19 / 255)  # Marron
            else:
                zone_color = ursina.color.gray  # Gris
            zone = ursina.Entity(
                model="cube",
                scale=(18, 5, 15),
                position=(x, -1.99, z),
                color=zone_color,
                texture=None,
                collider="box",
                shader=ursina.shaders.lit_with_shadows_shader,
            )
            zone.on_click = lambda z=zone: on_zone_click(z)

def fence():
    for i in range(30):
        vertical = ursina.Entity(model="cube", color = ursina.color.rgb(169 / 255, 124 / 255, 75 / 255) , texture="brick", position=(49-3.375*i, 1, 49), scale=(0.7, 4.5, 0.7), collider="mesh")
    
    horizontal_1 = ursina.Entity(model="cube", color = ursina.color.rgb(169 / 255, 124 / 255, 75 / 255) , texture="brick", position=(0, 2.6, 49), scale=(100, 0.43, 0.35), collider="mesh")
    horizontal_2 = ursina.Entity(model="cube", color = ursina.color.rgb(169 / 255, 124 / 255, 75 / 255) , texture="brick", position=(0, 1.7, 49), scale=(100, 0.43, 0.35), collider="mesh")

    for i in range(29):
        vertical = ursina.Entity(model="cube", color = ursina.color.rgb(169 / 255, 124 / 255, 75 / 255) , texture="brick", position=(49, 1, 45.625-3.375*i), scale=(0.7, 4.5, 0.7), collider="mesh")
    
    horizontal_1 = ursina.Entity(model="cube", color = ursina.color.rgb(169 / 255, 124 / 255, 75 / 255) , texture="brick", position=(49, 2.6, 0), scale=(0.35, 0.43, 100), collider="mesh")
    horizontal_2 = ursina.Entity(model="cube", color = ursina.color.rgb(169 / 255, 124 / 255, 75 / 255) , texture="brick", position=(49, 1.7, 0), scale=(0.35, 0.43, 100), collider="mesh")

    for i in range(30):
        vertical = ursina.Entity(model="cube", color = ursina.color.rgb(169 / 255, 124 / 255, 75 / 255) , texture="brick", position=(49-3.375*i, 1, -48.875), scale=(0.7, 4.5, 0.7), collider="mesh")

    horizontal_1 = ursina.Entity(model="cube", color = ursina.color.rgb(169 / 255, 124 / 255, 75 / 255) , texture="brick", position=(-49, 2.6, 0), scale=(0.35, 0.43, 100), collider="mesh")
    horizontal_2 = ursina.Entity(model="cube", color = ursina.color.rgb(169 / 255, 124 / 255, 75 / 255) , texture="brick", position=(-49, 1.7, 0), scale=(0.35, 0.43, 100), collider="mesh")

    for i in range(29):
        vertical = ursina.Entity(model="cube", color = ursina.color.rgb(169 / 255, 124 / 255, 75 / 255) , texture="brick", position=(-48.875, 1, 45.625-3.375*i), scale=(0.7, 4.5, 0.7), collider="mesh")

    horizontal_1 = ursina.Entity(model="cube", color = ursina.color.rgb(169 / 255, 124 / 255, 75 / 255) , texture="brick", position=(0, 2.6, -49), scale=(100, 0.43, 0.35), collider="mesh")
    horizontal_2 = ursina.Entity(model="cube", color = ursina.color.rgb(169 / 255, 124 / 255, 75 / 255) , texture="brick", position=(0, 1.7, -49), scale=(100, 0.43, 0.35), collider="mesh")



def on_zone_click(zone):
    global current_zone, joueur
    # Vérifier si la zone est grise (pas encore achetée)
    if zone.color == ursina.color.gray:
        if joueur.argent < 50:
            print("Pas assez d'argent pour acheter la zone.")
            return
        # Afficher le panel de confirmation
        current_zone = zone
        purchase_panel.visible = True
        # Désactiver les contrôles du joueur
        player.disable()
        fpc.mouse.locked = False
        player.cursor.visible = False
    else:
        # Zone déjà achetée, peut-être rien faire ou autre action
        pass



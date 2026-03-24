import ursina 
from importlib.util import *
import ursina.prefabs.first_person_controller as fpc
import math
from Objets import arrosoirs, texture_paths
from Inventaire import get_selected_hotbar_item

# Global joueur reference, set from main.py
joueur = None
player = None
zones = []

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
        # current_zone.collider = None  # Garder le collider pour permettre l'arrosage
        print("Zone achetée! Arrosez la zone pour faire apparaître les emplacements de plantation.")
        if not hasattr(current_zone, 'planting_spots'):
            current_zone.planting_spots = []
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
    global zones
    zones = []
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
            zones.append(zone)
            # Les cercles de plantation apparaissent uniquement après arrosage
            if not hasattr(zone, 'planting_spots'):
                zone.planting_spots = []
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
    elif zone.color == ursina.color.rgb(139 / 255, 69 / 255, 19 / 255):  # Marron
        selected_item = get_selected_hotbar_item()
        if selected_item and selected_item.item_name in ["Arrosoir rouillé rempli", "Arrosoir en fer rempli", "Arrosoir en or rempli"]:
            if selected_item.uses > 0:
                selected_item.uses -= 1
                zone.color = ursina.color.rgb(80 / 255, 40 / 255, 0 / 255)  # Marron foncé (arrosé)
                print("Zone arrosée ! Les emplacements de plantation sont maintenant disponibles.")
                print(f"Utilisations restantes: {selected_item.uses}")
                # Faire apparaître les 5 carrés verts de plantation
                if not hasattr(zone, 'planting_spots'):
                    zone.planting_spots = []
                for k in range(5):
                    angle = k * 2 * math.pi / 5
                    radius = 5
                    spot_x = zone.x + radius * math.cos(angle)
                    spot_z = zone.z + radius * math.sin(angle)
                    spot = ursina.Entity(
                        model='cube',
                        scale=(1, 3, 1),
                        position=(spot_x, zone.y + 2, spot_z),
                        color=ursina.color.green,
                        collider='box',
                    )
                    zone.planting_spots.append(spot)
                if selected_item.uses == 0:
                    # Changer en arrosoir vide
                    if "rouillé" in selected_item.item_name:
                        selected_item.item_name = "Arrosoir rouillé"
                    elif "fer" in selected_item.item_name:
                        selected_item.item_name = "Arrosoir en fer"
                    elif "or" in selected_item.item_name:
                        selected_item.item_name = "Arrosoir en or"
                    # Mettre à jour la texture et le tooltip
                    selected_item.texture = texture_paths.get(selected_item.item_name, selected_item.item_name)
                    selected_item._update_tooltip_text()
            else:
                print("Arrosoir vide !")
        else:
            print("Sélectionnez un arrosoir rempli pour arroser la zone")
    else:
        # Zone déjà arrosée ou autre
        pass



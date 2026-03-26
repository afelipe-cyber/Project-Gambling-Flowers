# Bibliothèques:
import ursina
import ursina.prefabs.first_person_controller as fpc
import pygame as pg
from importlib.util import *
from pathlib import Path

# Modules internes:
from Inventaire import *
import maps
import Joueur
import modele3d
import fleurs as fleurs_logic
from Objets import texture_paths


# Make assets resolvable from project root (not /sources).
ursina.application.asset_folder = Path(__file__).resolve().parent.parent
app = ursina.Ursina()
pg.init()  # Initialiser Pygame pour la musique
pg.mixer.music.load("data/Divers/Moonlight_Sonata.mp3")
pg.mixer.music.set_volume(0.2)
pg.mixer.music.play(-1)  # Jouer en boucle

try:
    achat_sound = pg.mixer.Sound("data/Divers/Achat.mp3")
    achat_sound.set_volume(0.7)
except Exception as e:
    achat_sound = None
    print(f"Impossible de charger le son d'achat: {e}")

try:
    vente_sound = pg.mixer.Sound("data/Divers/Vente.mp3")
    vente_sound.set_volume(0.7)
except Exception as e:
    vente_sound = None
    print(f"Impossible de charger le son de vente: {e}")
# Initialiser l'inventaire
inventory = init_inventory()
inventory.add_item("Arrosoir rouillé")
matrice_inventaire()  # Mettre à jour l'affichage

# Afficher argents du joueur
joueur = Joueur.Joueur("Player", argent=80, inventaire=inventory)
maps.joueur = joueur
argent_text = joueur.affichage_argent()


# Créer le terrain
platform = maps.create_map()
maps.fence()
maps.init_purchase_panel()

player = fpc.FirstPersonController(position=(-10.55, 2, -10), scale=2.5, speed=20)
PLAYER_DEFAULT_SPEED = player.speed
maps.player = player

scene_3d = modele3d.init_scene_models(player)
sky = scene_3d.sky
stand_parent = scene_3d.stand_parent
stand = scene_3d.stand
stand_animation = scene_3d.stand_animation
puit = scene_3d.puit
eau = scene_3d.eau
mushroom = scene_3d.mushroom
hint_text = scene_3d.hint_text
sun = scene_3d.sun
scene_3d.bind_well_click(get_selected_hotbar_item, texture_paths)

# Scene entities (house, well, mushroom, etc.)
#maison = ursina.Entity(model="data/casa/casa.fbx", texture="data/casa/casa.jpg", position=(0, 5, 0), scale=(0.1), shader=ursina.shaders.lit_with_shadows_shader)
#house_draft = ursina.Entity(model="data/casa/house-draft.fbx", texture="data/casa/1.jpg", position=(10, 5, 0), scale=(1.5, 1.5, 1.5), shader=ursina.shaders.lit_with_shadows_shader)

scene_ui = modele3d.SceneGameUI(
    scene_3d=scene_3d,
    player=player,
    inventory=inventory,
    joueur=joueur,
    achat_sound=achat_sound,
    vente_sound=vente_sound,
    iPan=iPan,
    Inventory=Inventory,
    fpc_mouse=fpc.mouse,
    get_selected_hotbar_item=get_selected_hotbar_item,
    matrice_inventaire=matrice_inventaire,
    destroy=destroy,
    graines=graines,
    arrosoirs=arrosoirs,
    fleurs=fleurs,
)

atm_panel = scene_ui.atm_panel
mushroom_panel = scene_ui.mushroom_panel


def toggle_atm_interface():
    scene_ui.toggle_atm_interface()


def toggle_mushroom_interface():
    scene_ui.toggle_mushroom_interface()

# Mettre à jour la référence globale du joueur pour l'inventaire

Inventory.player = player

flower_system = fleurs_logic.FlowerSystem(
    player=player,
    inventory=inventory,
    maps_module=maps,
    texture_paths=texture_paths,
    fleurs_dict=fleurs,
    get_selected_hotbar_item=get_selected_hotbar_item,
    matrice_inventaire=matrice_inventaire,
    destroy=destroy,
)


def update_zone_dry_timers():
    flower_system.update_zone_dry_timers()


def update_plant_growth():
    flower_system.update_plant_growth()


def plant_selected_from_hotbar():
    return flower_system.plant_selected_from_hotbar()


def update():
    joueur.affichage_argent()
    update_zone_dry_timers()
    update_plant_growth()

    # Bloque tout mouvement tant qu'une interface ATM/Champignon est ouverte.
    if 'player' in globals():
        ui_locked = (
            ('atm_panel' in globals() and atm_panel.visible)
            or ('mushroom_panel' in globals() and mushroom_panel.visible)
        )
        if ui_locked:
            player.speed = 0
            for move_key in ('w', 'a', 's', 'd', 'z', 'q'):
                ursina.held_keys[move_key] = 0
        else:
            player.speed = PLAYER_DEFAULT_SPEED

def input(key):
    # Bloquer l'ouverture/fermeture de l'inventaire pendant les interfaces ATM/Champignon.
    if key == 'e' and (atm_panel.visible or mushroom_panel.visible):
        return

    try:
        inv_input(key, player, fpc.mouse)
    except Exception as e:
        print("inv_input error:", e)

    if key == 'right mouse down':
        scene_3d.handle_right_click_interaction(
            atm_panel.visible,
            mushroom_panel.visible,
            toggle_atm_interface,
            toggle_mushroom_interface,
        )

    if key == 'left mouse down':
        flower_system.handle_left_click(atm_panel.visible, mushroom_panel.visible)

app.run()
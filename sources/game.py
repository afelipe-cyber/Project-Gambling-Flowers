import os

import ursina
import ursina.prefabs.first_person_controller as fpc
import pygame as pg

from Inventaire import *
import maps
import Joueur
import modele3d
import fleurs as fleurs_logic
from Objets import arrosoirs, fleurs, graines, texture_paths
import textures.sauvegarde as sauvegarde


class GameController:
    def __init__(self):
        self.title_text = None
        self.new_game_button = None
        self.load_game_button = None
        self.achat_sound = None
        self.vente_sound = None
        self.joueur = None
        self.inventory = None
        self.player = None
        self.scene_3d = None
        self.flower_system = None
        self.atm_panel = None
        self.mushroom_panel = None
        self.scene_ui = None

    def setup(self):
        self.init_audio()
        self.create_title_screen()

    def init_audio(self):
        pg.init()
        pg.mixer.music.load("data/Divers/Moonlight_Sonata.mp3")
        pg.mixer.music.set_volume(0.1)
        pg.mixer.music.play(-1)

        try:
            self.achat_sound = pg.mixer.Sound("data/Divers/Achat.mp3")
            self.achat_sound.set_volume(0.7)
        except Exception as e:
            self.achat_sound = None
            print(f"Impossible de charger le son d'achat: {e}")

        try:
            self.vente_sound = pg.mixer.Sound("data/Divers/Vente.mp3")
            self.vente_sound.set_volume(0.7)
        except Exception as e:
            self.vente_sound = None
            print(f"Impossible de charger le son de vente: {e}")

    def create_title_screen(self):
        self.title_text = ursina.Text(
            text="Project: Gambling Flowers",
            scale=2,
            position=(0, 0.3),
            origin=(0, 0),
            color=ursina.color.white,
        )

        self.new_game_button = ursina.Button(
            text="Nouvelle partie",
            scale=(0.5, 0.1),
            position=(0, 0),
            on_click=self.new_game,
        )

        self.load_game_button = ursina.Button(
            text="Charger dernière sauvegarde",
            scale=(0.5, 0.1),
            position=(0, -0.15),
            on_click=self.load_saved_game,
        )

    def new_game(self):
        self.title_text.disable()
        self.new_game_button.disable()
        self.load_game_button.disable()

        self.joueur = Joueur.Joueur("Player", argent=80, inventaire=init_inventory())
        self.joueur.inventaire.add_item("Arrosoir rouillé")
        self.inventory = self.joueur.inventaire
        matrice_inventaire()
        self.start_game_logic()

    def load_saved_game(self):
        print("Tentative de chargement de sauvegarde...")
        if os.path.exists(sauvegarde.SAVE_FILE):
            print(f"Sauvegarde trouvée: {sauvegarde.SAVE_FILE}")
            self.title_text.disable()
            self.new_game_button.disable()
            self.load_game_button.disable()

            self.joueur, saved_state = sauvegarde.load_game()
            if self.joueur:
                self.inventory = self.joueur.inventaire
                matrice_inventaire()
                try:
                    self.start_game_logic(saved_state=saved_state)
                except Exception as e:
                    print(f"Erreur dans start_game_logic: {e}")
            else:
                print("Erreur lors du chargement")
        else:
            print(f"Aucune sauvegarde trouvée à {sauvegarde.SAVE_FILE}")

    def start_game_logic(self, saved_state=None):
        self.joueur = self.joueur
        self.inventory = self.inventory
        maps.joueur = self.joueur

        argent_text = self.joueur.affichage_argent()

        maps.create_map()
        if saved_state is not None:
            maps.restore_zone_states(saved_state.get("zones", []))
        maps.fence()
        maps.init_purchase_panel()

        self.player = fpc.FirstPersonController(position=(-10.55, 2, -10), scale=2.5, speed=20)
        self.player_default_speed = self.player.speed
        maps.player = self.player

        self.scene_3d = modele3d.init_scene_models(self.player)
        scene_3d = self.scene_3d
        scene_3d.bind_well_click(get_selected_hotbar_item, texture_paths)

        self.scene_ui = modele3d.SceneGameUI(
            scene_3d=scene_3d,
            player=self.player,
            inventory=self.inventory,
            joueur=self.joueur,
            achat_sound=self.achat_sound,
            vente_sound=self.vente_sound,
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

        self.atm_panel = self.scene_ui.atm_panel
        self.mushroom_panel = self.scene_ui.mushroom_panel

        Inventory.player = self.player

        self.flower_system = fleurs_logic.FlowerSystem(
            player=self.player,
            inventory=self.inventory,
            maps_module=maps,
            texture_paths=texture_paths,
            fleurs_dict=fleurs,
            get_selected_hotbar_item=get_selected_hotbar_item,
            matrice_inventaire=matrice_inventaire,
            destroy=destroy,
        )

        if saved_state is not None:
            self.flower_system.restore_planted_flowers(saved_state.get("plants", []))

        self.register_ursina_callbacks()

    def register_ursina_callbacks(self):
        def update():
            self.joueur.affichage_argent()
            self.flower_system.update_zone_dry_timers()
            self.flower_system.update_plant_growth()

            if self.player is None:
                return

            ui_locked = (
                (self.atm_panel is not None and self.atm_panel.visible)
                or (self.mushroom_panel is not None and self.mushroom_panel.visible)
            )
            if ui_locked:
                self.player.speed = 0
                for move_key in ("w", "a", "s", "d", "z", "q"):
                    ursina.held_keys[move_key] = 0
            else:
                self.player.speed = self.player_default_speed

        def input(key):
            print("Input called with key:", key)
            if key == "e" and (self.atm_panel.visible or self.mushroom_panel.visible):
                return

            try:
                inv_input(key, self.player, fpc.mouse)
            except Exception as e:
                print("inv_input error:", e)

            if key == "right mouse down":
                self.scene_3d.handle_right_click_interaction(
                    self.atm_panel.visible,
                    self.mushroom_panel.visible,
                    self.toggle_atm_interface,
                    self.toggle_mushroom_interface,
                )

            if key == "left mouse down":
                self.flower_system.handle_left_click(self.atm_panel.visible, self.mushroom_panel.visible)

            if key == "p":
                print("Sauvegarde demandée")
                sauvegarde.save_game(self.joueur, self.flower_system)

            if key == "enter":
                print("fermeture du programme")
                ursina.application.quit()

        import __main__
        __main__.update = update
        __main__.input = input

    def toggle_atm_interface(self):
        if self.scene_ui is not None:
            self.scene_ui.toggle_atm_interface()

    def toggle_mushroom_interface(self):
        if self.scene_ui is not None:
            self.scene_ui.toggle_mushroom_interface()

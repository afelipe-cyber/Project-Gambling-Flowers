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

DRY_BROWN = ursina.color.rgb(139 / 255, 69 / 255, 19 / 255)
WATERED_BROWN = ursina.color.rgb(80 / 255, 40 / 255, 0 / 255)
ZONE_REWATER_TIMEOUT = 60

# Purchase panel
purchase_panel = None
current_zone = None


def _ensure_zone_state(zone):
    if not hasattr(zone, 'planting_spots'):
        zone.planting_spots = []
    if not hasattr(zone, 'occupied_spot_keys'):
        zone.occupied_spot_keys = set()
    if not hasattr(zone, 'is_watered'):
        zone.is_watered = False
    if not hasattr(zone, 'grown_in_cycle'):
        zone.grown_in_cycle = 0
    if not hasattr(zone, 'dry_since'):
        zone.dry_since = None


def _spot_position_key(position):
    return (
        round(position.x, 4),
        round(position.y, 4),
        round(position.z, 4),
    )


def register_occupied_spot(zone, position):
    _ensure_zone_state(zone)
    zone.occupied_spot_keys.add(_spot_position_key(position))


def release_occupied_spot(zone, position):
    _ensure_zone_state(zone)
    zone.occupied_spot_keys.discard(_spot_position_key(position))


def add_planting_spot(zone, position):
    _ensure_zone_state(zone)
    position_key = _spot_position_key(position)
    if position_key in zone.occupied_spot_keys:
        return None

    for existing_spot in zone.planting_spots:
        if _spot_position_key(existing_spot.position) == position_key:
            return existing_spot

    spot = ursina.Entity(
        model='cube',
        scale=(1, 3, 1),
        position=position,
        color=ursina.color.green,
        collider='box',
    )
    zone.planting_spots.append(spot)
    return spot


def reset_zone_to_dry(zone, start_dry_timer=False):
    """Remet la zone en marron sec et supprime les emplacements de plantation."""
    _ensure_zone_state(zone)
    zone.color = DRY_BROWN
    zone.is_watered = False
    zone.grown_in_cycle = 0
    zone.dry_since = ursina.time.time() if start_dry_timer else None

    for spot in list(zone.planting_spots):
        try:
            ursina.destroy(spot)
        except Exception:
            pass
    zone.planting_spots.clear()


def mark_zone_watered(zone):
    """Passe la zone en état arrosé et démarre un nouveau cycle de pousse."""
    _ensure_zone_state(zone)
    zone.color = WATERED_BROWN
    zone.is_watered = True
    zone.grown_in_cycle = 0
    zone.dry_since = None


def serialize_zones():
    zone_states = []
    for zone in zones:
        _ensure_zone_state(zone)
        if zone.color == ursina.color.gray:
            status = "locked"
        elif getattr(zone, "is_watered", False):
            status = "watered"
        else:
            status = "dry"

        dry_elapsed = None
        dry_timer_remaining = None
        if status == "dry" and getattr(zone, "dry_since", None) is not None:
            dry_elapsed = ursina.time.time() - zone.dry_since
            dry_timer_remaining = max(0.0, ZONE_REWATER_TIMEOUT - dry_elapsed)

        zone_states.append({
            "status": status,
            "grown_in_cycle": getattr(zone, "grown_in_cycle", 0),
            "dry_elapsed": dry_elapsed,
            "dry_timer_remaining": dry_timer_remaining,
        })
    return zone_states


def restore_zone_states(zone_states):
    for zone, state in zip(zones, zone_states):
        _ensure_zone_state(zone)

        for spot in list(zone.planting_spots):
            try:
                ursina.destroy(spot)
            except Exception:
                pass
        zone.planting_spots.clear()

        status = state.get("status", "locked")
        if status == "locked":
            zone.color = ursina.color.gray
            zone.is_watered = False
            zone.grown_in_cycle = 0
            zone.dry_since = None
        elif status == "dry":
            zone.color = DRY_BROWN
            zone.is_watered = False
            zone.grown_in_cycle = state.get("grown_in_cycle", 0)
            dry_timer_remaining = state.get("dry_timer_remaining")
            if dry_timer_remaining is not None:
                zone.dry_since = ursina.time.time() - max(0.0, ZONE_REWATER_TIMEOUT - dry_timer_remaining)
            else:
                dry_elapsed = state.get("dry_elapsed")
                zone.dry_since = ursina.time.time() - dry_elapsed if dry_elapsed is not None else None
        elif status == "watered":
            mark_zone_watered(zone)
            create_planting_spots(zone)


def create_planting_spots(zone):
    _ensure_zone_state(zone)
    for k in range(5):
        angle = k * 2 * math.pi / 5
        radius = 5
        spot_x = zone.x + radius * math.cos(angle)
        spot_z = zone.z + radius * math.sin(angle)
        add_planting_spot(zone, ursina.Vec3(spot_x, zone.y + 2, spot_z))

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
        position=(0, 0.08),
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

    # Center title between the two buttons and keep a stable vertical offset above them.
    purchase_title.x = (yes_button.x + no_button.x) / 2 - 0.15
    purchase_title.y = yes_button.y + 0.18

def confirm_purchase():
    global current_zone, joueur
    if current_zone and joueur and joueur.argent >= 50:
        joueur.argent -= 50
        reset_zone_to_dry(current_zone, start_dry_timer=False)
        # current_zone.collider = None  # Garder le collider pour permettre l'arrosage
        print("Zone achetée! Arrosez la zone pour faire apparaître les emplacements de plantation.")
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
                zone_color = DRY_BROWN  # Marron
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
            _ensure_zone_state(zone)
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
    elif zone.color == DRY_BROWN:  # Marron
        selected_item = get_selected_hotbar_item()
        if selected_item and selected_item.item_name in ["Arrosoir rouillé rempli", "Arrosoir en fer rempli", "Arrosoir en or rempli"]:
            if selected_item.uses > 0:
                selected_item.uses -= 1
                mark_zone_watered(zone)
                print("Zone arrosée ! Les emplacements de plantation sont maintenant disponibles.")
                print(f"Utilisations restantes: {selected_item.uses}")
                # Faire apparaître les 5 carrés verts de plantation
                create_planting_spots(zone)
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



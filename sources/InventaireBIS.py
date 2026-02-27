from ursina import *
from Objets import *
import ursina.prefabs.first_person_controller as fpc
import random


hotspots = []
items = []

hotbar = Entity(model="quad", parent=camera.ui)
hot_cols = 9
hot_wid = 1 / 16  # Largeur d'un slot ~ 1/10 de la hauteur de fenêtre.
hb_wid = hot_wid * hot_cols
hotbar.scale = Vec3(hb_wid, hot_wid, 0)
hotbar.y = -0.45 + (hotbar.scale_y * 0.5)
hotbar.color = color.light_gray
hotbar.z = 0

iPan = Entity(model="quad", parent=camera.ui)
iPan.rows = 3
iPan.scale_y = hotbar.scale_y * iPan.rows
iPan.scale_x = hotbar.scale_x
iPan.basePosY = hotbar.y + (hotbar.scale_y * 0.5) + (iPan.scale_y * 0.5)
iPan.gap = hotbar.scale_y
iPan.y = iPan.basePosY + iPan.gap
iPan.color = color.light_gray
iPan.z = 0
iPan.visible = False


class InventoryItem(Draggable):
    """Classe pour gérer un item unique de l'inventaire"""
    
    def __init__(self, parent, item_name, **kwargs):
        self.item_name = item_name
        self.original_position = None
        self.stack = 1  # Nombre d'items dans cette pile
        
        # Obtenir le chemin de texture depuis le dictionnaire
        texture_path = texture_paths.get(item_name, None)
        if texture_path is None:
            print(f"Warning: texture_path not found for {item_name}, using item_name as fallback")
            texture_path = item_name
        
        super().__init__(
            parent = parent,
            model = 'quad',
            texture = texture_path,
            color = color.white,
            origin = (-.5, .5),
            z = -.5,
            **kwargs
        )
        
        self._setup_tooltip()
        self.drag = self._on_drag
        self.drop = self._on_drop
    
    def _setup_tooltip(self):
        """Configure le tooltip avec le nom de l'item et le stack"""
        self._update_tooltip_text()
        self.tooltip.background.color = color.hsv(0, 0, 0, .8)
    
    def _update_tooltip_text(self):
        """Met à jour le texte du tooltip avec le nom et le stack"""
        name = self.item_name.replace('_', ' ').title()
        if self.stack > 1:
            name += f"-{self.stack}"
        self.tooltip = Tooltip(name)
        self.tooltip.background.color = color.hsv(0, 0, 0, .8)
    
    
    def _on_drag(self):
        """Appelé quand l'item commence à être dragué"""
        self.original_position = (self.x, self.y)
        self.z -= .05  # Assure que l'item dragué est au-dessus
    
    def _on_drop(self, inventory):
        """Appelé quand l'item est relâché"""
        self._snap_to_grid()
        self.z += .05
        
        if not self._is_inside_inventory(inventory):
            self._restore_position()
            return
        
        self._swap_if_occupied(inventory)
    
    def _snap_to_grid(self):
        """Arrondit la position pour coller à la grille"""
        self.x = int(self.x)
        self.y = int(self.y)
        self.z = -0.5
    
    def _is_inside_inventory(self, inventory):
        """Vérifie si l'item est dans les limites de l'inventaire"""
        return not (self.x < 0 or self.x >= inventory.INVENTORY_WIDTH or self.y > 0 or self.y <= -inventory.INVENTORY_HEIGHT)
    
    def _restore_position(self):
        """Restaure la position originale"""
        self.position = self.original_position
    
    def _swap_if_occupied(self, inventory):
        """Gère les collisions: fusionne si même type, échange sinon"""
        # Sauvegarder la position avant de potentiellement détruire self
        my_x, my_y = self.x, self.y
        my_original_pos = self.original_position
        
        for other_item in inventory.item_parent.children:
            if other_item != self and other_item.x == my_x and other_item.y == my_y:
                # Vérifier si c'est le même type d'item
                if other_item.item_name == self.item_name:
                    # Même type: augmenter le compteur de 1 et détruire cet item
                    other_item.stack += self.stack
                    # mettre à jour l'affichage (tooltip/label) du stack
                    if hasattr(other_item, '_update_tooltip_text'):
                        try:
                            other_item._update_tooltip_text()
                        except Exception:
                            pass
                    destroy(self)
                else:
                    # Type différent: échanger les positions
                    other_item.position = my_original_pos
                    self.position = (my_x, my_y)
                return
    


class Inventory(Entity):
    """Gère l'affichage et la logique de l'inventaire.

    Un mini-hotbar (la première rangée) est toujours visible. Appuyer sur
    "e" bascule l'affichage entre la hotbar seule et l'inventaire complet.
    """
    scalar = hotbar.scale_y * 0.9
    rowFit = 9
    # dimensions de l'inventaire (largeur = nombre de colonnes, hauteur = lignes)
    INVENTORY_WIDTH = hot_cols
    INVENTORY_HEIGHT = iPan.rows

    def __init__(self):
        # utiliser une variable intermédiaire pour éviter de lire self.scale_y
        s = Inventory.scalar
        super().__init__(
            parent = camera.ui,
            model = 'quad',
            scale_y = s,
            scale_x = s,
            texture = None,
            color = color.dark_gray,
            z = -1,
            visibility = False # Commence invisible, sera rendu visible après appuie sur e
        )
        
        # Conteneur pour les items; il ne doit pas être redimensionné
        # car les positions des items sont déjà exprimées en unités de
        # grille correspondant aux carrés gris foncé (hotspots). Une échelle
        # différente provoquait un décalage visuel.
        self.item_parent = Entity(
            parent=self,
            position=(-self.scale_x, -self.scale_y, 0),
            scale=Vec3(1, 1, 1),
        )

        # état d'affichage : False = hotbar seule, True = inventaire complet
        self.showing_full = False
        # enregistrer la position et l'échelle de l'inventaire complet
        self._full_pos = self.position
        self._full_scale = self.scale
        # calculer une position pour la hotbar (bas de l'écran)
        self._hotbar_pos = Vec3(0, -0.45 + (self.scale_y * 0.5), 0)

    @staticmethod
    def toggle():
        # Affiche / cache le panneau principal.
        iPan.visible = not iPan.visible
        # Bascule la visibilité des slots non-hotbar.
        for h in hotspots:
            if not h.onHotbar:
                h.visible = not h.visible
                if hasattr(h, 't'):
                    h.t.visible = h.visible
                if hasattr(h, 'item'):
                    h.item.visible = h.visible

    
    def find_free_spot(self):
        """Trouve la première case libre dans l'inventaire"""
        taken_spots = [(int(item.x), int(item.y)) 
                       for item in self.item_parent.children]
        
        for y in range(self.INVENTORY_HEIGHT):
            for x in range(self.INVENTORY_WIDTH):
                if (x, -y) not in taken_spots:
                    return (x, -y)
        
        return None
    
    def add_item(self, item_name):
        """Ajoute un item à l'inventaire"""
        free_spot = self.find_free_spot()
        
        if free_spot is None:
            print("L'inventaire est plein!")
            return
        
        item = InventoryItem(
            parent = self.item_parent,
            item_name = item_name,
            position = free_spot
        )
        
        # Créer une référence à self pour que le drop puisse y accéder
        item._inventory = self
        
        # Wrapper le drop pour passer l'inventaire
        original_drop = item._on_drop
        item.drop = lambda: original_drop(self)

    


def init_inventory():
    """Initialise l'inventaire et crée les slots"""
    inventory = Inventory()
    
    # Debug: Vérifier que texture_paths est rempli
    print(f"DEBUG: texture_paths contient {len(texture_paths)} entrées")
    if texture_paths:
        first_key = list(texture_paths.keys())[0]
        print(f"DEBUG: Exemple - {first_key}: {texture_paths[first_key]}")

    for i in range(Inventory.rowFit):
        bud = Inventory()
        bud.onHotbar = True
        bud.visible = True
        bud.y = hotbar.y
        bud.x = hotbar.x - hotbar.scale_x * 0.5 + Inventory.scalar * 0.5 * 1.2 + i * bud.scale_x * 1.1
        hotspots.append(bud)

    for i in range(Inventory.rowFit):
        for j in range(iPan.rows):
            bud = Inventory()
            bud.onHotbar = False
            bud.visible = False
            bud.y = iPan.y + iPan.scale_y * 0.5 - Inventory.scalar * 0.5 * 1.2 - Inventory.scalar * j * 1.1
            bud.x = iPan.x - iPan.scale_x * 0.5 + Inventory.scalar * 0.5 * 1.2 + i * Inventory.scalar * 1.1
            hotspots.append(bud)
    Inventory.toggle()
    Inventory.toggle()

    # Ajouter 7 items au démarrage
    available_items = list(fleurs.keys())
    for _ in range(7):
        item_name = random.choice(available_items)
        inventory.add_item(item_name)
    
    return inventory


# ==========================
# input helper functions
# ==========================

# Variables globales pour l'inventaire
player = None

def _base_inv_input(key, subject, mouse):
    if subject is None:
        return
    try:
        wnum = int(key)
        if 0 < wnum < 10:
            for h in hotspots:
                h.color = color.white
            wnum -= 1
            hotspots[wnum].color = color.black
            if hotspots[wnum].occupied:
                subject.blockType = hotspots[wnum].item.blockType
    except Exception:
        pass
    # Pause / reprise et affichage de l'inventaire.
    if key == "e":
        if hasattr(subject, 'enabled') and subject.enabled:
            Inventory.toggle()
            subject.disable()
            if hasattr(mouse, 'locked'):
                mouse.locked = False
            if hasattr(subject, 'cursor'):
                subject.cursor.visible = False
        elif hasattr(subject, 'enabled'):
            Inventory.toggle()
            subject.enable()
            if hasattr(mouse, 'locked'):
                mouse.locked = True
            if hasattr(subject, 'cursor'):
                subject.cursor.visible = True
        else:
            # Si subject n'a pas d'attribut 'enabled', juste toggle
            Inventory.toggle()


def inv_input(key, subject, mouse):
    """Wrapper AZERTY + call base handler"""
    azerty_map = {
        '&': '1', 'é': '2', '"': '3', "'": '4', '(': '5',
        '-': '6', 'è': '7', '_': '8', 'ç': '9'
    }
    if key in azerty_map:
        key = azerty_map[key]
    _base_inv_input(key, subject, mouse)

    
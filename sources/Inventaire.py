from ursina import *
from Objets import *


hotspots = []
items = []

hot_cols = 9
hot_wid = 1 / 16  # Largeur d'un slot ~ 1/10 de la hauteur de fenêtre.
hb_wid = hot_wid * hot_cols

hotbar = None
iPan = None
selected_hotbar_index = 0


def get_selected_hotbar_item():
    inv = getattr(Inventory, "instance", None)
    if inv is None:
        return None

    current_matrix = matrice_inventaire(set_matrix=False)
    if not current_matrix:
        return None

    if selected_hotbar_index < 0 or selected_hotbar_index >= len(current_matrix[0]):
        return None

    return current_matrix[0][selected_hotbar_index]


class InventoryItem(Draggable):
    """Classe pour gérer un item unique de l'inventaire"""
    
    def __init__(self, parent, item_name, **kwargs):
        self.item_name = item_name
        self.original_position = None
        self.stack = 1  # Nombre d'items dans cette pile
        self.uses = self._get_uses_for_item(item_name)  # Utilisations restantes pour les arrosoirs
        
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
            origin = (0, 0),
            z = -.5,
            **kwargs
        )
        # Adapter la taille de l'icône à celle d'un slot
        try:
            from math import isfinite  # pour éviter les soucis d'import si modifié ailleurs
            slot_size = Inventory.scalar * 0.9
            self.scale_x = slot_size
            self.scale_y = slot_size
        except Exception:
            pass
        
        self._setup_tooltip()
        self.drag = self._on_drag
        self.drop = self._on_drop
    
    def _get_uses_for_item(self, item_name):
        """Retourne le nombre d'utilisations pour les arrosoirs remplis"""
        if item_name == "Arrosoir rouillé rempli":
            return 1
        elif item_name == "Arrosoir en fer rempli":
            return 2
        elif item_name == "Arrosoir en or rempli":
            return 3
        else:
            return None  # Pas d'utilisations limitées
    
    def _setup_tooltip(self):
        """Configure le tooltip avec le nom de l'item et le stack"""
        self._update_tooltip_text()
        self.tooltip.background.color = color.hsv(0, 0, 0, .8)
    
    def _update_tooltip_text(self):
        """Met à jour le texte du tooltip avec le nom, le stack et les utilisations"""
        name = self.item_name.replace('_', ' ').title()

        # Affiche la rareté uniquement pour les graines et les fleurs.
        rarity = None
        if self.item_name in graines:
            rarity = graines[self.item_name].rareté
        elif self.item_name in fleurs:
            rarity = fleurs[self.item_name].rareté

        rarity_text = None
        if rarity == 1:
            rarity_text = "Commun"
        elif rarity == 2:
            rarity_text = "Rare"
        elif rarity == 3:
            rarity_text = "Epic"
        elif rarity == 4:
            rarity_text = "Légendaire"

        if rarity_text is not None:
            name += f"\nRareté: {rarity_text}"

        if self.uses is not None:
            name += f" ({self.uses} utilisations)"
        self.tooltip = Tooltip(name)
        self.tooltip.background.color = color.hsv(0, 0, 0, .8)
    
    
    def _on_drag(self):
        """Appelé quand l'item commence à être dragué"""
        self.original_position = (self.x, self.y)
        # Sauvegarde aussi la case de grille actuelle si disponible
        if hasattr(self, "grid_x") and hasattr(self, "grid_y"):
            self.original_grid = (self.grid_x, self.grid_y)
        self.z -= .05  # Assure que l'item dragué est au-dessus
    
    def _on_drop(self, inventory):
        """Appelé quand l'item est relâché"""
        self._snap_to_grid(inventory)
        self.z += .05
        
        if not self._is_inside_inventory(inventory):
            self._restore_position()
            return
        
        self._swap_if_occupied(inventory)
        
        # Mettre à jour la matrice après le déplacement
        matrice_inventaire()
    
    def _snap_to_grid(self, inventory):
        """Place l'item au centre de la case de grille la plus proche"""
        # On part de la position écran actuelle
        wx, wy = self.x, self.y
        gx, gy = inventory.world_to_grid(wx, wy)

        # Enregistrer la position de grille arrondie
        self.grid_x = gx
        self.grid_y = gy

        # Reconvertir en coordonnées écran alignées sur la case
        snapped_pos = inventory.grid_to_world(gx, gy)
        self.position = snapped_pos
        self.z = -0.5
    
    def _is_inside_inventory(self, inventory):
        """Vérifie si l'item est dans les limites de l'inventaire"""
        # Utilise les indices de grille plutôt que les coordonnées écran brutes
        gx = getattr(self, "grid_x", None)
        gy = getattr(self, "grid_y", None)
        if gx is None or gy is None:
            gx, gy = inventory.world_to_grid(self.x, self.y)
            self.grid_x, self.grid_y = gx, gy

        return not (
            gx < 0
            or gx >= inventory.INVENTORY_WIDTH
            or gy > 0
            or gy <= -(inventory.INVENTORY_HEIGHT + 1)
        )
    
    def _restore_position(self):
        """Restaure la position originale"""
        # Restaure la position écran
        self.position = self.original_position
        # Et la case de grille si elle a été sauvegardée
        if hasattr(self, "original_grid"):
            self.grid_x, self.grid_y = self.original_grid
    
    def _swap_if_occupied(self, inventory):
        """Gère les collisions: échange les positions sans jamais fusionner."""
        # Sauvegarder la position avant de potentiellement détruire self
        my_x = getattr(self, "grid_x", None)
        my_y = getattr(self, "grid_y", None)
        if my_x is None or my_y is None:
            my_x, my_y = inventory.world_to_grid(self.x, self.y)
            self.grid_x, self.grid_y = my_x, my_y
        my_original_pos = self.original_position
        my_original_grid = getattr(self, "original_grid", (my_x, my_y))
        
        for other_item in inventory.item_parent.children:
            # S'assurer que l'autre item a aussi des coordonnées de grille
            ox = getattr(other_item, "grid_x", None)
            oy = getattr(other_item, "grid_y", None)
            if ox is None or oy is None:
                ox, oy = inventory.world_to_grid(other_item.x, other_item.y)
                other_item.grid_x, other_item.grid_y = ox, oy

            if other_item != self and ox == my_x and oy == my_y:
                # Échanger les cases de grille et les positions.
                ogx, ogy = my_original_grid
                other_item.grid_x, other_item.grid_y = ogx, ogy
                self.grid_x, self.grid_y = my_x, my_y

                other_item.position = inventory.grid_to_world(ogx, ogy)
                self.position = inventory.grid_to_world(my_x, my_y)
                return
    


class Inventory(Entity):
    """Gère l'affichage et la logique de l'inventaire.

    Un mini-hotbar (la première rangée) est toujours visible. Appuyer sur
    "e" bascule l'affichage entre la hotbar seule et l'inventaire complet.
    """
    scalar = hot_wid * 0.9
    rowFit = 9
    # dimensions de l'inventaire (largeur = nombre de colonnes, hauteur = lignes)
    INVENTORY_WIDTH = hot_cols
    INVENTORY_HEIGHT = iPan.rows if iPan else 3

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
        
        # Conteneur pour les items; on le parent à l'UI pour ne pas subir
        # l'échelle de l'entité Inventory elle-même.
        self.item_parent = Entity(
            parent=camera.ui,
            position=(0, 0, -1),
            scale=Vec3(1, 1, 1),
        )

        # état d'affichage : False = hotbar seule, True = inventaire complet
        self.showing_full = False
        # enregistrer la position et l'échelle de l'inventaire complet
        self._full_pos = self.position
        self._full_scale = self.scale
        # calculer une position pour la hotbar (bas de l'écran)
        self._hotbar_pos = Vec3(0, -0.45 + (self.scale_y * 0.5), 0)
        
        # Initialiser la matrice de l'inventaire
        self.matrix = []

    def update(self):
        """Vérifie automatiquement si la matrice a changé et synchronise si nécessaire."""
        current_matrix = matrice_inventaire(set_matrix=False)
        if current_matrix != self.matrix:
            synchroniser_inventaire_depuis_matrice(self.matrix)

    def grid_to_world(self, gx, gy):
        """Convertit une coordonnée de grille (x, y) en position écran alignée sur les slots."""
        slot_size = Inventory.scalar * 1.1

        if gy == 0:  # hotbar
            base_x = hotbar.x - hotbar.scale_x * 0.5 + Inventory.scalar * 0.5 * 1.2
            base_y = hotbar.y
        else:  # inventory
            base_x = iPan.x - iPan.scale_x * 0.5 + Inventory.scalar * 0.5 * 1.2
            base_y = iPan.y + iPan.scale_y * 0.5 - Inventory.scalar * 0.5 * 1.2 + Inventory.scalar * 1.1

        x = base_x + gx * slot_size
        y = base_y + gy * slot_size

        return Vec3(x, y, -0.5)

    def world_to_grid(self, wx, wy):
        """Convertit une position écran en indices de grille (x, y)."""
        slot_size = Inventory.scalar * 1.1

        if wy > hotbar.y + hotbar.scale_y * 0.5:
            # inventory
            base_x = iPan.x - iPan.scale_x * 0.5 + Inventory.scalar * 0.5 * 1.2
            base_y = iPan.y + iPan.scale_y * 0.5 - Inventory.scalar * 0.5 * 1.2 + Inventory.scalar * 1.1
        else:
            # hotbar
            base_x = hotbar.x - hotbar.scale_x * 0.5 + Inventory.scalar * 0.5 * 1.2
            base_y = hotbar.y

        gx = round((wx - base_x) / slot_size)
        gy = round((wy - base_y) / slot_size)

        return gx, gy

    @staticmethod
    def toggle():
        # Affiche / cache le panneau principal.
        iPan.visible = not iPan.visible
        show = iPan.visible
        # Bascule la visibilité des slots non-hotbar.
        for h in hotspots:
            if not h.onHotbar:
                h.visible = show
                if hasattr(h, 't'):
                    h.t.visible = h.visible
                if hasattr(h, 'item'):
                    h.item.visible = h.visible
        # Bascule aussi la visibilité des items de l'inventaire BIS
        inv = getattr(Inventory, "instance", None)
        if inv is not None:
            for child in inv.item_parent.children:
                if show:
                    child.visible = True
                else:
                    # Garder visibles les items de la hotbar (première rangée, grid_y == 0)
                    gy = getattr(child, "grid_y", None)
                    if gy is None:
                        _, gy = inv.world_to_grid(child.x, child.y)
                        child.grid_y = gy
                    child.visible = show or (gy == 0)

    
    def find_free_spot(self):
        """Trouve la première case libre dans l'inventaire"""
        taken_spots = []
        for item in self.item_parent.children:
            gx = getattr(item, "grid_x", None)
            gy = getattr(item, "grid_y", None)
            if gx is None or gy is None:
                gx, gy = self.world_to_grid(item.x, item.y)
                item.grid_x, item.grid_y = gx, gy
            taken_spots.append((gx, gy))
        
        for y in range(self.INVENTORY_HEIGHT + 1):
            spot_y = 0 if y == 0 else -y
            for x in range(self.INVENTORY_WIDTH):
                if (x, spot_y) not in taken_spots:
                    return (x, spot_y)
        
        return None
    
    def add_item(self, item_name):
        """Ajoute un item à l'inventaire"""
        free_spot = self.find_free_spot()
        
        if free_spot is None:
            print("L'inventaire est plein!")
            return
        
        # Convertit la case de grille en position écran alignée
        gx, gy = free_spot
        world_pos = self.grid_to_world(gx, gy)

        item = InventoryItem(
            parent = self.item_parent,
            item_name = item_name,
            position = world_pos
        )
        # Mémorise la case de grille de l'item
        item.grid_x, item.grid_y = gx, gy
        # Hotbar (grid_y == 0) toujours visible ; le reste suit le panneau
        item.visible = iPan.visible or (gy == 0)
        
        # Créer une référence à self pour que le drop puisse y accéder
        item._inventory = self
        
        # Wrapper le drop pour passer l'inventaire
        original_drop = item._on_drop
        item.drop = lambda: original_drop(self)

    
    def passage_inventaire_hotbar(self):
        """Déplace un item de la hotbar vers l'inventaire"""
        for item in self.item_parent.children:
            if item.onHotbar:
                item.passage_hotbar_inventaire()
                break
    

class Hotbar(Entity):
    """Gère l'affichage et la logique de la hotbar"""

    def __init__(self):
        super().__init__(
            model="quad",
            parent=camera.ui,
            scale=Vec3(hb_wid, hot_wid, 0),
            y=-0.45 + (hot_wid * 0.5),
            color=color.light_gray,
            z=0
        )
        self.scalar = self.scale_y * 0.9
        self.row_fit = 9

def init_inventory():
    """Initialise l'inventaire et crée les slots"""
    global hotbar, iPan
    hotbar = Hotbar()
    
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
    
    inventory = Inventory()
    # Réduit l'entité principale pour qu'elle ne dessine pas de grand carré au centre,
    # tout en gardant les autres instances (hotbar + grille) à leur taille normale.
    inventory.scale_x = 0
    inventory.scale_y = 0
    # Mémorise l'instance principale de l'inventaire (celle qui contient les items)
    Inventory.instance = inventory
    
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


# Test
    # Ajouter 20 items au démarrage
    # available_items1=list(fleurs.keys())
    # available_items2=list(graines.keys())
    # available_items3=list(arrosoirs.keys())
    # for _ in range(7):
    #     item_name1 = random.choice(available_items1)
    #     inventory.add_item(item_name1)
    # for _ in range(7):
    #     key = random.choice(available_items2)
    #     item_name2 = graines[key].nom
    #     inventory.add_item(item_name2)
    # for _ in range(6):
    #     key = random.choice(available_items3)
    #     item_name3 = arrosoirs[key].nom
    #     inventory.add_item(item_name3)
    
    # Initialiser la matrice après ajout des items
    matrice_inventaire()
    
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
            # synchronisation de la sélection de la hotbar
            global selected_hotbar_index
            selected_hotbar_index = wnum
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


def matrice_inventaire(set_matrix=True):
    """Retourne une matrice représentant l'état de l'inventaire.

    matrice[0]  -> ligne de hotbar (grid_y == 0)
    matrice[1:] -> lignes de l'inventaire (grid_y == -1, -2, -3 ...)

    Chaque case contient soit None, soit l'instance d'InventoryItem présente
    à cet emplacement (on peut ensuite lire item.item_name, item.stack, etc.).
    """
    inv = getattr(Inventory, "instance", None)
    if inv is None:
        return []

    width = Inventory.INVENTORY_WIDTH
    height = Inventory.INVENTORY_HEIGHT  # nb de lignes d'inventaire (hors hotbar)

    # matrice[0] = hotbar, matrice[1..height] = lignes d'inventaire
    matrice = [[None for _ in range(width)] for _ in range(height + 1)]

    for item in inv.item_parent.children:
        # Récupérer les coordonnées de grille de l'item
        gx = getattr(item, "grid_x", None)
        gy = getattr(item, "grid_y", None)
        if gx is None or gy is None:
            gx, gy = inv.world_to_grid(item.x, item.y)
            item.grid_x, item.grid_y = gx, gy

        # Hotbar : gy == 0 -> ligne 0
        # Inventaire : gy < 0 -> ligne -gy
        if gy == 0:
            row = 0
        else:
            row = -gy

        if 0 <= row <= height and 0 <= gx < width:
            matrice[row][gx] = item

    # Stocker aussi sur l'instance pour un accès direct ailleurs
    if set_matrix:
        inv.matrix = matrice
        # Afficher la matrice pour debug
        # print("Matrice de l'inventaire :")
        for i, row in enumerate(matrice):
            row_str = []
            for cell in row:
                if cell is None:
                    row_str.append("None")
                else:
                    row_str.append(cell.item_name)
            # print(f"Ligne {i}: {row_str}")
    return matrice


def synchroniser_inventaire_depuis_matrice(matrice=None):
    """Applique une matrice d'inventaire à l'UI/logiciel.if key == 'right mouse down':
        print(f"Right click detected, hint_text.enabled: {hint_text.enabled}, stand.hovered: {stand.hovered}")
        if hint_text.enabled:
            print("Hint is enabled")
            if stand.hovered:
                print("Stand is hovered, toggling inventory")
                # Toggle inventory
                Inventory.toggle()
                # Toggle player controls based on player state
                if player.enabled:
                    player.disable()
                    fpc.mouse.locked = False
                    player.cursor.visible = False
                else:
                    player.enable()
                    fpc.mouse.locked = True
                    player.cursor.visible = True
            else:
                print("Stand not hovered")
        else:
            print("Hint not enabled")

    - Si une case de la matrice est None -> l'item correspondant est supprimé.
    - Si un item est déplacé dans la matrice -> il est déplacé visuellement.
    - Les lignes suivent la même convention que `matrice_inventaire()` :
      matrice[0] = hotbar, matrice[1..] = lignes de l'inventaire.

    Utilisation typique :
        m = matrice_inventaire()
        m[2][5] = None  # supprimer l'item de la ligne 2, col 5
        synchroniser_inventaire_depuis_matrice(m)
    """
    inv = getattr(Inventory, "instance", None)
    if inv is None:
        return

    if matrice is None:
        matrice = getattr(inv, "matrix", None)
    if not matrice:
        return

    width = Inventory.INVENTORY_WIDTH
    height = Inventory.INVENTORY_HEIGHT

    # Ensemble des items qui doivent exister après synchro,
    # mappés à leur position cible (gx, gy).
    desired_positions = {}

    for row_idx, row in enumerate(matrice):
        if row is None:
            continue
        for gx, cell in enumerate(row):
            if gx < 0 or gx >= width:
                continue
            if cell is None:
                continue
            # On ne gère que les vrais InventoryItem déjà existants.
            if not isinstance(cell, InventoryItem):
                continue

            # Conversion ligne -> gy de grille
            if row_idx == 0:
                gy = 0
            else:
                gy = -row_idx

            if -height <= gy <= 0:
                desired_positions[cell] = (gx, gy)

    # 1) Supprimer / retirer les items qui ne sont plus dans la matrice.
    for item in list(inv.item_parent.children):
        if item not in desired_positions:
            destroy(item)

    # 2) Mettre à jour la position des items gardés.
    for item, (gx, gy) in desired_positions.items():
        # Met à jour les coords de grille
        item.grid_x, item.grid_y = gx, gy
        # Met à jour la position monde alignée sur les slots
        item.position = inv.grid_to_world(gx, gy)
        # Visibilité : hotbar toujours visible, inventaire suit l'état du panneau
        item.visible = iPan.visible or (gy == 0)

    # Mémoriser la matrice actuelle sur l'instance
    inv.matrix = matrice


# ==========================
# test
# ==========================

# if __name__ == "__main__":
#     from ursina import *
#     from Objets import *
    
#     app = Ursina()
    
#     # Initialiser l'inventaire
#     inventory = init_inventory()
    
#     # Créer un joueur basique pour les inputs
#     player = Entity()
#     player.enabled = True
    
#     # Créer une souris basique
#     mouse = Entity()
#     mouse.locked = True
    
#     # Fonction pour gérer les inputs
#     def input_handler(key):
#         inv_input(key, player, mouse)
    
#     # Assigner la fonction d'input
#     app.input = input_handler
    
#     # Lancer l'application
#     app.run()


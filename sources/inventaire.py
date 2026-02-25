from ursina import *
import random as ra
import numpy as np
import os

"""
Système d'inventaire intégré (sans dépendance au dossier python_meshCraft_tut_2021).

- Reprend les éléments nécessaires de `config.py` et `inventory_system.py`
  du tutoriel MeshCraft.
- Ajoute un wrapper AZERTY pour mapper les touches (&, é, ", ', (, -, è, _, ç)
  vers les chiffres 1..9 pour la sélection de la hotbar.
"""




# Construire le catalogue à partir des images dans data/Fleurs et data/Graines
objets = {}
# Correction : on cherche le dossier "data" dans le même répertoire que le script
base_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "data"))
fleurs_dir = os.path.join(base_dir, "Fleurs")
graines_dir = os.path.join(base_dir, "Graines")

def _add_images_from_dir(dpath):
    if not os.path.isdir(dpath):
        return
    for fn in sorted(os.listdir(dpath)):
        if not fn.lower().endswith(('.png', '.jpg', '.jpeg')):
            continue
        name = os.path.splitext(fn)[0]
        # Clef simple dérivée du nom de fichier (sans extension)
        key = name
        path = os.path.join(dpath, fn)
        path = os.path.abspath(path)
        # On stocke le chemin de l'image comme premier élément du tuple.
        # Format: (texture_path,) ou (texture_path, Vec4(r,g,b,a)).
        objets[key] = (path,)

_add_images_from_dir(fleurs_dir)
_add_images_from_dir(graines_dir)

mins = list(objets.keys())
print(f"[inventaire] loaded {len(mins)} items")


# ---------------------------------------------------------------------------
# Système d'inventaire (extraits nécessaires de inventory_system.py)
# ---------------------------------------------------------------------------

hotspots = []
items = []


# Inventory hotbar.
hotbar = Entity(model="quad", parent=camera.ui)
hot_cols = 9
hot_wid = 1 / 16  # Largeur d'un slot ~ 1/10 de la hauteur de fenêtre.
hb_wid = hot_wid * hot_cols
hotbar.scale = Vec3(hb_wid, hot_wid, 0)
hotbar.y = -0.45 + (hotbar.scale_y * 0.5)
hotbar.color = color.dark_gray
hotbar.z = 0


# Inventory main panel.
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


class Hotspot(Entity):
    # Taille des slots basée sur la hotbar.
    scalar = hotbar.scale_y * 0.9
    # Nombre de slots sur la hotbar.
    rowFit = 9

    def __init__(this):
        super().__init__()
        this.model = load_model("quad", use_deepcopy=True)
        this.parent = camera.ui
        this.scale_y = Hotspot.scalar
        this.scale_x = this.scale_y
        this.color = color.white
        this.texture = None
        this.z = -1

        this.onHotbar = False
        this.visible = False
        this.occupied = False
        this.item = None
        this.stack = 0
        this.t = Text("", scale=1.5)

    @staticmethod
    def toggle():
        # Affiche / cache le panneau principal.
        if iPan.visible:
            iPan.visible = False
        else:
            iPan.visible = True
        # Bascule la visibilité des slots non-hotbar.
        for h in hotspots:
            if not h.visible and not h.onHotbar:
                h.visible = True
                h.t.visible = True
                if h.item:
                    h.item.visible = True
            elif not h.onHotbar:
                h.visible = False
                h.t.visible = False
                if h.item:
                    h.item.visible = False


class Item(Draggable):
    def __init__(this, _blockType):
        super().__init__()
        this.parent = camera.ui
        # Modèle de base.
        this.model = load_model("quad", use_deepcopy=True)
        this.scale_x = Hotspot.scalar * 0.9
        this.scale_y = this.scale_x
        this.color = color.white
        this.texture = "texture_atlas_3.png"
        this.texture_scale *= 64 / this.texture.width
        this.z = -2

        # Type de bloc.
        if _blockType is None:
            this.blockType = mins[ra.randint(0, len(mins) - 1)]
        else:
            this.blockType = _blockType

        this.onHotbar = False
        this.visible = False
        this.currentSpot = None

        this.set_texture()
        this.set_colour()

    def set_texture(this):
        val = objets[this.blockType][0]
        # Si la valeur est une chaîne, on la considère comme un chemin d'image
        if isinstance(val, str):
            try:
                tex = load_texture(val)
                this.texture = tex
                try:
                    this.texture_scale *= 64 / tex.width
                except Exception:
                    pass
                this.rotation_z = 180
            except Exception:
                print(f"[inventaire] erreur load_texture pour '{this.blockType}' path='{val}'")
                # fallback: essayer d'assigner la chaîne (ursina peut aussi gérer ça)
                this.texture = val
                try:
                    self_tex = this.texture
                    this.texture_scale *= 64 / getattr(self_tex, 'width', 64)
                except Exception:
                    pass
                this.rotation_z = 180
        else:
            uu = val
            uv = objets[this.blockType][1]
            basemod = load_model("block.obj", use_deepcopy=True)
            e = Empty(model=basemod)
            cb = e.model.uvs.copy()
            cb = cb[-6:]
            cb = cb[3:] + cb[:3]
            this.model.uvs = [Vec2(uu, uv) + u for u in cb]
            this.model.generate()
            this.rotation_z = 180

    def set_colour(this):
        if len(objets[this.blockType]) > 2:
            this.color = objets[this.blockType][2]

    def fixPos(this):
        closest = -1
        closestHotty = None
        for h in hotspots:
            if h.occupied and h.item != this:
                continue
            dist = h.position - this.position
            dist = np.linalg.norm(dist)
            if dist < closest or closest == -1:
                closestHotty = h
                closest = dist
        if closestHotty is not None:
            this.position = closestHotty.position
            closestHotty.occupied = True
            closestHotty.item = this
            closestHotty.stack = this.currentSpot.stack
            if this.currentSpot != closestHotty:
                this.currentSpot.stack = 0
                this.currentSpot.t.text = "     "
                this.currentSpot.occupied = False
                this.currentSpot.item = None
                this.currentSpot = closestHotty
        elif this.currentSpot:
            this.position = this.currentSpot.position

    def update_stack_text(this):
        stackNum = this.currentSpot.stack
        myText = "<white><bold>" + str(stackNum)
        this.currentSpot.t.text = myText
        this.currentSpot.t.origin = (0, 0)
        this.currentSpot.t.z = -3
        this.currentSpot.t.x = this.currentSpot.x
        this.currentSpot.t.y = this.currentSpot.y

    def drop(this):
        this.fixPos()
        this.update_stack_text()

    @staticmethod
    def stack_check(_blockType):
        for h in hotspots:
            if h.onHotbar is False:
                continue
            if h.occupied is False:
                continue
            if h.item.blockType == _blockType:
                h.stack += 1
                h.item.update_stack_text()
                return True
        return False

    @staticmethod
    def new_item(_blockType):
        aStack = Item.stack_check(_blockType)
        if aStack is False:
            for h in hotspots:
                if not h.onHotbar or h.occupied:
                    continue
                h.stack = 1
                b = Item(_blockType)
                b.currentSpot = h
                items.append(b)
                h.item = b
                h.occupied = True
                b.onHotbar = True
                b.visible = True
                b.x = h.x
                b.y = h.y
                b.update_stack_text()
                break


# Hotspots pour la hotbar.
for i in range(Hotspot.rowFit):
    bud = Hotspot()
    bud.onHotbar = True
    bud.visible = True
    bud.y = hotbar.y
    bud.x = hotbar.x - hotbar.scale_x * 0.5 + Hotspot.scalar * 0.5 * 1.2 + i * bud.scale_x * 1.1
    hotspots.append(bud)

# Hotspots pour le panneau d'inventaire principal.
for i in range(Hotspot.rowFit):
    for j in range(iPan.rows):
        bud = Hotspot()
        bud.onHotbar = False
        bud.visible = False
        bud.y = iPan.y + iPan.scale_y * 0.5 - Hotspot.scalar * 0.5 * 1.2 - Hotspot.scalar * j * 1.1
        bud.x = iPan.x - iPan.scale_x * 0.5 + Hotspot.scalar * 0.5 * 1.2 + i * Hotspot.scalar * 1.1
        hotspots.append(bud)

# Assure que les items hors hotbar sont bien invisibles au début.
Hotspot.toggle()
Hotspot.toggle()

# Texte "où suis-je ?".


def _base_inv_input(key, subject, mouse):
    """Logique d'inventaire du tutoriel (sans wrapper AZERTY)."""
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
    # Pause / reprise et affichage de l'inventaire.
    if key == "e" and subject.enabled:
        Hotspot.toggle()
        subject.disable()
        mouse.locked = False
        subject.cursor.visible = False  # Cache le carré blanc
    elif key == "e" and not subject.enabled:
        Hotspot.toggle()
        subject.enable()
        mouse.locked = True
        subject.cursor.visible = True   # Réaffiche le carré blanc


def inv_input(key, subject, mouse):
    """Wrapper AZERTY pour l'inventaire."""
    # Mapping AZERTY -> nombres 1-9
    azerty_map = {
        '&': '1', 'é': '2', '"': '3', "'": '4', '(': '5',
        '-': '6', 'è': '7', '_': '8', 'ç': '9'
    }
    
    # Convertir la touche AZERTY en nombre si nécessaire
    if key in azerty_map:
        key = azerty_map[key]
    
    _base_inv_input(key, subject, mouse)
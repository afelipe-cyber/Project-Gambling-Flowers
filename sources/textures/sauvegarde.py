import os
import pickle
from pathlib import Path

import maps
import Joueur
from Inventaire import init_inventory

SAVE_DIR = Path(__file__).resolve().parents[2] / "sauvegarde"
SAVE_DIR.mkdir(exist_ok=True)
SAVE_FILE = SAVE_DIR / "savegame.pkl"


def save_game(joueur, flower_system=None):
    print("Sauvegarde en cours...")
    inventory_items = []
    if getattr(joueur.inventaire, 'item_parent', None):
        for item in joueur.inventaire.item_parent.children:
            inventory_items.append({
                'item_name': item.item_name,
                'stack': getattr(item, 'stack', 1),
            })

    data = {
        'nom': joueur.nom,
        'argent': joueur.argent,
        'inventory_items': inventory_items,
        'plants': [],
        'zones': [],
    }

    if flower_system is not None:
        data['plants'] = flower_system.serialize_planted_flowers()
        data['zones'] = maps.serialize_zones()

    print(f"Sauvegarde vers {SAVE_FILE}")
    with open(SAVE_FILE, 'wb') as f:
        pickle.dump(data, f)
    print("Partie sauvegardée.")


def load_game():
    if os.path.exists(SAVE_FILE):
        print("Chargement des données...")
        with open(SAVE_FILE, 'rb') as f:
            data = pickle.load(f)
        print(f"Données chargées: {data}")
        joueur = Joueur.Joueur(data['nom'], argent=data['argent'], inventaire=init_inventory())
        for item_info in data.get('inventory_items', []):
            item_name = item_info.get('item_name')
            if item_name:
                print(f"Ajout d'item: {item_name}")
                joueur.inventaire.add_item(item_name)
        print("Joueur créé avec succès")
        return joueur, data
    else:
        print("Aucun fichier de sauvegarde")
        return None, None

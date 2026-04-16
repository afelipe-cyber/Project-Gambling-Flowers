import ursina
from pathlib import Path

import game

# Rendre les assets accessibles depuis la racine du projet (et non depuis /sources).
ursina.application.asset_folder = Path(__file__).resolve().parent.parent
app = ursina.Ursina()

controller = game.GameController()
controller.setup()

app.run()

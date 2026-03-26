# GAMBLING FLOWERS

Gambling Flowers est un jeu de gestion et de simulation dans lequel vous incarnez un joueur, votre objectif est de planter des graines pour obtenir des fleurs pour ensuite les vendre. En vendant les fleurs, vous obtiendrez de l'argent, qui pourra être utilisé dans notre système de Gacha pour obtenir d'autres graines.

## Sommaire

├─ [Fonctionnalités](#fonctionnalites)  
├─ [Installation & Démarrage](#installation)  
├─ [Structure du projet](#structure)  
└─ [Auteurs](#auteurs)  

<a id="fonctionnalites"></a>
### Fonctionnalités

- **Planter les graines**: Vous pouvez plantez des graines et attendre qu'elles grandissent.
- **Arroser les parcelles**: L'arrosage des parcelles est importante car si une parcelle n'est pas arrosée, alors les graines plantées mourront.
- **Système de Gacha**: Vous pourriez faire des tirages pour obtenir des graines et des arrosoirs de différentes raretés.
- **Récolte et Vente de fleurs**: Vous pourrez récolter les fleurs et les vendre, plus la rareté de la fleur est élevée plus elle sera cher.

<a id="installation"></a>
### Installation et Démarrage

### Prérequis

*A noter que ci-dessous ne sont listés que les principaux modules nécessaire au fonctionnement unique du code.*

- **Python 3.12+** : Le projet est testé pour fonctionner sur cette version, mais il est **fortement recommandé** d'utiliser la dernière version stable de Python.
- **pip** : Pour l'installation des dépendances (inclus lors de l'installation de Python).
- [**Ursina Engine**](https://www.ursinaengine.org/installation.html) : La version la plus stable d'Ursina, utilisée comme moteur de rendu.
- **importlib.util** : Bibliothèque qui fournit du code utilitaire pour les importeurs, permettant la gestion dynamique des modules.
- **pathlib** : Bibliothèque qui offre une approche orientée objet pour manipuler les chemins du système de fichiers.
- **pygame** : La version communautaire de pygame, utilisée comme lecteur de musique.

### Installation

Si vous installez le projet via git :

```bash
git clone https://github.com/afelipe-cyber/Project-Gambling-Flowers.git
cd Gambling-Flowers
pip install -r "requirements.txt"
```

### Démarrer le jeu

```bash
python3 sources/main.py
```

<a id="structure"></a>
## Fabriqué avec

...

<a id="auteurs"></a>
## Auteurs

- **HUANG Samuel** — Architecture du moteur, UI Manager, système de tirage, intéraction PNJ, arrosage
- **FELIPE Antoine** — Texture finder, système de plantage et récolte
- **DO DUY Raphaël** — Modèles 3D, création de la plateforme, création des ombres


## License

Ce projet est sous licence **General Public License v3.0** - voir le fichier [LICENSE](LICENSE) pour plus d'informations

---

### Crédits

#### Musique de fond, et son

*Moonlight Sonata*, Beethoven

[*Cash Register Cha-Ching*, cashregistersound](https://cashregistersound.bandcamp.com/album/cash-register-cha-ching-sound-effects-30-hd-sounds-download-any-sound-or-the-complete-sample-pack)

[Cash Register "Kaching" (Money Sound), Sound Library](https://www.youtube.com/watch?v=FFt6VGujJnY)

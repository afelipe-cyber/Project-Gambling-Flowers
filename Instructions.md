# Comment constituer votre dossier technique ?

## Nommer son dossier technique

Le répertoire racine du projet doit respecter la dénomination suivante : 

2026_ID du projet_nom du projet

L'ID d'un projet est unique. Il est fourni lors de la création d'un nouveau projet sur la plateforme de dépôt : https://depot.trophees-nsi.fr/

## La nomenclature à respecter

Le dossier technique doit contenir les éléments précisés ci-dessous, en respectant cette même nomenclature :

- un fichier presentation.md,
- un fichier README.md,
- un fichier LICENSE,
- un fichier requirements.txt,
- un répertoire sources,

Selon la dimension et la nature du projet, vous pouvez également ajouter les répertoires suivants :

- un répertoire docs,
- un répertoire data,
- un répertoire test,
- un répertoire exemples.

## Les fichiers et répertoires à fournir

### Le fichier presentation.md

La présentation du projet est une description synthétique rédigée par les élèves. 

### Le fichier readme.md

Ce fichier explique comment lancer le projet. Il indique les éventuelles contraintes sur la version de Python à utiliser pour exécuter le projet.

### Le fichier licence.txt

Ce fichier précise le nom de la licence libre (GPL v3+) qui s’applique au projet.

### Le fichier requirements.txt

Ce fichier texte permet de spécifier les dépendances du projet, c'est-à-dire les bibliothèques Python nécessaires au bon fonctionnement de votre solution. Chaque bibliothèque est précisée avec son nom suivi éventuellement d'une version. 

La commande la plus courante pour enregistrer la liste des paquets actuels de votre environnement : (`pip freeze > requirements.txt`)

### Le répertoire sources 

Il contient le code du projet (les fichiers python notamment). Dans le cas d’un projet python, le programme principal doit impérativement s’appeler : main.py.

### Le répertoire docs *(facultatif)*

Il contient la description de la structuration du projet (rôle des différents fichiers, explication de la structuration du code par exemple) afin de permettre une reprise du projet par d’autres élèves.

### Le répertoire data *(facultatif)*

C’est le répertoire où seront stockés les fichiers générés par le projet, ainsi que les fichiers de ressources nécessaires au fonctionnement du projet (images, base de données, etc.).

### Le répertoire test *(facultatif)*

Il contient des scripts de tests de l’application.

### Le répertoire exemples *(facultatif)*

Il peut contenir des captures d’écran, des vidéos, des explications textuelles sur les différentes façons d’utiliser le logiciel.
import random as rd
class Joueur:

    def __init__(self, nom, pv, atk, argent, inventaire ):
        self.nom = nom
        self.pv = pv
        self.atk = atk
        self.argent = 0
        self.inventaire = {}

    def recolte(self,fleur):
        if fleur.statut == 4:
            self.inventaire[fleur.nom] = fleur
        #TODO : supprime la fleur du champ de plantation
        pass
    
    def arrosage(self, arrosoir, emplacement):
        pass

    def plantation(self, graine, emplacement):
        pass

    def tirer(self, fleurs):
        pull_rarete = rd.randint(1,1000)
        if pull_rarete<37:
        elif 37<pull_rarete<134:
        elif 134<pull_rarete<323
        pass

    def attaquer(self, ennemi):
        ennemi.pv -= self.atk

    def subir_degats(self, ennemi):
        self.pv -= ennemi.atk
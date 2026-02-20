import random as rd
class Joueur:

    def __init__(self, nom, pv, atk, argent, inventaire ):
        self.nom = nom
        self.pv = pv
        self.atk = atk
        self.argent = 0
        self.inventaire = {}

    def recolte(self,fleur):
        #si la fleur a terminé sa croissance(statut=4), le joueur recupère la fleur
        if fleur.statut == 4:
            if fleur.nom in self.inventaire:
                fleur.quantite += 1
            else:
                self.inventaire[fleur.nom] = fleur
        #TODO : supprime la fleur du champ de plantation
        pass 
    
    def arrosage(self, arrosoir, emplacement):
        pass

    def plantation(self, graine, emplacement):
        if graine.quatite == 0:
            del self.inventaire[graine.nom]
        else: graine.quatite -= 1
        pass

    def tirer(self, fleurs):
        #valeur qui va determiner la rarerté de l'objet tiré
        pull_rarete = rd.randint(1,1000)
        
        #liste des fleurs, de rarete determinée par pull_rarete, parmis lesquelles va etre choisie aléatoirement la fleur tirée par le joueur
        pool_rarete=[]

        #variable qui contient la taille de la liste pool_rarete
        n=0
                
        #objet de rarete UR (3,7%)
        if pull_rarete<37:
            
            #si la rarete determinée est UR alors on créer un liste des fleurs de rareté UR
            for elem in fleurs:
                if fleurs[elem][1] == 5:
                pool_rarete.append(fleurs[elem])
                
        #objet de rarete SSR (9,7%)
        elif 37<pull_rarete<134:

            #si la rarete determinée est SSR alors on créer un liste des fleurs de rareté SSR
            for elem in fleurs:
                elif fleurs[elem][1] == 4:
                pool_rarete.append(fleurs[elem])
                
        #objet de rarete SR (18,9%)
        elif 134<pull_rarete<323:

            #si la rarete determinée est SR alors on créer un liste des fleurs de rareté SR
            for elem in fleurs:
                elif fleurs[elem][1] == 3:
                pool_rarete.append(fleurs[elem])
                
        #objet de rarete R (26,5%)
        elif 323<pull_rarete<588:

            #si la rarete determinée est R alors on créer un liste des fleurs de rareté R
            for elem in fleurs:
                elif fleurs[elem][1] == 2:
                pool_rarete.append(fleurs[elem])
                
        #objet de rarete C (41,2%)
        elif 588<pull_rarete<1000:

            #si la rarete determinée est C alors on créer un liste des fleurs de rareté C
            for elem in fleurs:
                elif fleurs[elem][1] == 1:
                pool_rarete.append(fleurs[elem])
                
        n=len(pool_rarete)

        #on récupère dans une variable la fleur sélectionner aléatoirement parmis les autres fleurs de la liste de la rarete du tirage
        pull = pool_rarete[rd.randint(pool_rarete)]
        
        if pull.nom in self.inventaire:
            pull.quantité += 1
        else:
            self.invnetaire[pull.nom] = pull

    def attaquer(self, ennemi):
        ennemi.pv -= self.atk

    def subir_degats(self, ennemi):
        self.pv -= ennemi.atk

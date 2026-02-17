class PNJ:
    
    def __init__(self, nom, acheteur):
        self.nom = nom
        # self.inventaire = MC.Inventaire()
        self.inventaire = {}
        self.acheteur = acheteur

    def dialogue(self, message):
        print(message)

    def ajouter_objet(self, nom_objet, quantite, prix):
        if nom_objet in objets_possibles:
            objet = objets_possibles[nom_objet]
            self.inventaire[nom_objet] = (quantite, prix)
        else:
            print(f"Objet '{nom_objet}' n'est pas disponible dans objets_possibles.")
        
    def vendre_objet(self, nom_objet, joueur):
        if nom_objet in self.inventaire:
            quantite, prix = self.inventaire[nom_objet]
            if joueur.inventaire.objets.get("Argent", 0) >= prix:
                joueur.inventaire.retirer_objet("Argent", prix)
                joueur.inventaire.ajouter_objet(nom_objet, 1)
                if nom_objet != "Graine commune":
                    if quantite > 1:
                        self.inventaire[nom_objet] = (quantite - 1, prix)
                    else:
                        del self.inventaire[nom_objet]
                print(f"Vous avez acheté {nom_objet} pour {prix} Pièce.")
            else:
                print("Vous n'avez pas assez d'argent.")
        else:
            print("Cet objet n'est pas disponible à la vente.")
        
    def acheter_objet(self, nom_objet, quantite):
        if self.acheteur == True:
            if joueur.inventaire.objets.get(nom_objet) >= quantite:
                joueur.inventaire.ajouter_objet("Argent",prix*quantite)
                joueur.inventaire.retirer_objet(nom_objet, quantite)
            else:
                print("Vous n'avez pas assez de fleur ...")
        else:
            print(self.nom, "n'achaite pas de fleur ...")
        if joueur.inventaire.objets.get(nom_objet) = 0:
            del joueur.inventaire[nom_objet]
            
    def afficher_inventaire(self):
        # print(self.objets)
        print("\n==== Boutique de", self.nom, "====")
        for nom, (quantite, prix) in self.inventaire.items():
            print(f"{nom} {Objets.objets_possibles[nom].rarete_texte()}\n↳ Quantité: {quantite}\n↳ Prix: {prix}\n")

#PNJ vendeur d'arrosoirs
Roberto = PNJ("Roberto le maître jardinier", False)
Roberto.ajouter_objet("Arrosoir Rouillé", 1, 0)
Roberto.ajouter_objet("Arrosoir en Bois", 1, ...)
Roberto.ajouter_objet("Arrosoir en Plastique", 1, ...)
Roberto.ajouter_objet("Arrosoir en Fer", 1, ...)


#PNJ Achereur / Vendeur : (Fleurs / Graines)
Antonio = PNJ("Antonio D'Féli-Pet", True)
Antonio.ajouter_objet("Graine commune",1, ...)
Antonio.ajouter_objet("Crotin de cheval", 1, 0)

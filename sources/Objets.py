class Fleurs:
    def __init__(self, nom, rareté):
        self.nom = nom
        self.rareté = rareté

    def affichage_fl(self):
        # Retourne une représentation unicode simple de la fleur
        return f"{self.nom} (Rareté: {self.rarete_texte()})"
    
    def rarete_texte(self):
        # Retourne une représentation unicode simple en fonction de la rareté
        if self.rareté == 1:
            return "C"
        elif self.rareté == 2:
            return "R"
        elif self.rareté == 3:
            return "SR"
        elif self.rareté == 4:
            return "SSR"
        elif self.rareté == 5:
            return "UR"
        elif self.rareté == 0:
            return "En cours de développement"
        
    def __str__(self):
        return f"{self.nom} de rareté {self.rareté}"

fleurs = {

    "Cécilia": Fleurs("Cécilia", 0),
    "Dendrobium sanglant": Fleurs("Dendrobium sanglant", 0),
    "Chrysanthème": Fleurs("Chrysanthème", 0),
    "Fleur de Qingxin": Fleurs("Fleur de Qingxin", 0),
    "Fleur de soie": Fleurs("Fleur de soie", 0),
    "Fleur funéraire": Fleurs("Fleur funéraire", 0),
    "Fleur sucrante": Fleurs("Fleur sucrante", 0),
    "Gueule-de-loup": Fleurs("Gueule-de-loup", 0),
    "Herbe à lampe": Fleurs("Herbe à lampe", 0),
    "Herbe à sanglots": Fleurs("Herbe à sanglots", 0),
    "Inteyvat": Fleurs("Inteyvat", 0),
    "Kalpalotus": Fleurs("Kalpalotus", 0),
    "Lotus pluvieux": Fleurs("Lotus pluvieux", 0),
    "Lys calla": Fleurs("Lys calla", 0),
    "Lys lacmineux": Fleurs("Lys lacmineux", 0),
    "Lys verni": Fleurs("Lys verni", 0),
    "Marcotte": Fleurs("Marcotte", 0),
    "Muget bleu": Fleurs("Muget bleu", 0),
    "Padisachidée": Fleurs("Padisachidée", 0),
    "Rose arc-en-ciel": Fleurs("Rose arc-en-ciel", 0),
    "Rose sumérienne": Fleurs("Rose sumérienne", 0),
    "Viparyas": Fleurs("Viparyas", 0),

}

class Graines:
    def __init__(self, nom, rareté):
        self.nom = nom
        self.rareté = rareté

    def affichage_gr(self):
        # Retourne une représentation unicode simple de la graine
        return f"{self.nom} (Rareté: {self.rarete_texte()})"
    
    def rarete_texte(self):
        # Retourne une représentation unicode simple en fonction de la rareté
        if self.rareté == 1:
            return "C"
        elif self.rareté == 2:
            return "R"
        elif self.rareté == 3:
            return "SR"
        elif self.rareté == 4:
            return "SSR"
        elif self.rareté == 5:
            return "UR"
        elif self.rareté == 0:
            return "En cours de développement"
        
    def __str__(self):
        return f"{self.nom} de rareté {self.rareté}"
    
Graines = {
    "Cécilia": Graines("Graine de Cécilia", 0),
    "Dendrobium sanglant": Graines("Graine de Dendrobium sanglant", 0),
    "Chrysanthème": Graines("Graine de Chrysanthème", 0),
    "Fleur de Qingxin": Graines("Graine de Fleur de Qingxin", 0),
    "Fleur de soie": Graines("Graine de Fleur de soie", 0),
    "Fleur funéraire": Graines("Graine de Fleur funéraire", 0),
    "Fleur sucrante": Graines("Graine de Fleur sucrante", 0),
    "Gueule-de-loup": Graines("Graine de Gueule-de-loup", 0),
    "Herbe à lampe": Graines("Graine de Herbe à lampe", 0),
    "Herbe à sanglots": Graines("Graine de Herbe à sanglots", 0),
    "Inteyvat": Graines("Graine de Inteyvat", 0),
    "Kalpalotus": Graines("Graine de Kalpalotus", 0),
    "Lotus pluvieux": Graines("Graine de Lotus pluvieux", 0),
    "Lys calla": Graines("Graine de Lys calla", 0),
    "Lys lacmineux": Graines("Graine de Lys lacmineux", 0),
    "Lys verni": Graines("Graine de Lys verni", 0),
    "Marcotte": Graines("Graine de Marcotte", 0),
    "Muget bleu": Graines("Graine de Muget bleu", 0),
    "Padisachidée": Graines("Graine de Padisachidée", 0),
    "Rose arc-en-ciel": Graines("Graine de Rose arc-en-ciel", 0),
    "Rose sumérienne": Graines("Graine de Rose sumérienne", 0),
    "Viparyas": Graines("Graine de Viparyas", 0),

}

# # Test
# print("Fleurs disponibles :")
# for nom, fleur in fleurs.items():
#     print(fleur.affichage_fl())

# print("\nGraines disponibles :")
# for nom, graine in Graines.items():
#     print(graine.affichage_gr())
class Fleurs:
    def __init__(self, nom, rareté, texture=None):
        self.nom = nom
        self.rareté = rareté
        self.texture = f"../data/Fleurs/{nom}.png"

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

# Dictionnaire global mappant les noms aux chemins de texture
texture_paths = {}

fleurs = {

    "Cécilia": Fleurs("Cécilia", 0, "Cécilia"),
    "Dendrobium sanglant": Fleurs("Dendrobium sanglant", 0, "Dendrobium sanglant"),
    "Chrysanthème": Fleurs("Chrysanthème", 0, "Chrysanthème"),
    "Fleur de Qingxin": Fleurs("Fleur de Qingxin", 0, "Fleur de Qingxin"),
    "Fleur de soie": Fleurs("Fleur de soie", 0, "Fleur de soie"),
    "Fleur funéraire": Fleurs("Fleur funéraire", 0, "Fleur funéraire"),
    "Fleur sucrante": Fleurs("Fleur sucrante", 0, "Fleur sucrante"),
    "Gueule-de-loup": Fleurs("Gueule-de-loup", 0, "Gueule-de-loup"),
    "Herbe à lampe": Fleurs("Herbe à lampe", 0, "Herbe à lampe"),
    "Herbe à sanglots": Fleurs("Herbe à sanglots", 0, "Herbe à sanglots"),
    "Inteyvat": Fleurs("Inteyvat", 0, "Inteyvat"),
    "Kalpalotus": Fleurs("Kalpalotus", 0, "Kalpalotus"),
    "Lotus pluvieux": Fleurs("Lotus pluvieux", 0, "Lotus pluvieux"),
    "Lys calla": Fleurs("Lys calla", 0, "Lys calla"),
    "Lys lacmineux": Fleurs("Lys lacmineux", 0, "Lys lacmineux"),
    "Lys verni": Fleurs("Lys verni", 0, "Lys verni"),
    "Marcotte": Fleurs("Marcotte", 0, "Marcotte"),
    "Muget bleu": Fleurs("Muget bleu", 0, "Muget bleu"),
    "Padisachidée": Fleurs("Padisachidée", 0, "Padisachidée"),
    "Rose arc-en-ciel": Fleurs("Rose arc-en-ciel", 0, "Rose arc-en-ciel"),
    "Rose sumérienne": Fleurs("Rose sumérienne", 0, "Rose sumérienne"),
    "Viparyas": Fleurs("Viparyas", 0, "Viparyas"),

}

# Remplir le dictionnaire des textures
for nom, fleur_obj in fleurs.items():
    texture_paths[nom] = fleur_obj.texture

class Graines:
    def __init__(self, nom, rareté, texture=None):
        self.nom = nom
        self.rareté = rareté
        self.texture = f"../data/Graines/{nom}.png"

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
    
graines = {
    "Graines de Cécilia": Graines("Graines de Cécilia", 0, "Graines de Cécilia"),
    "Graines de Dendrobium sanglant": Graines("Graines de Dendrobium sanglant", 0, "Graines de Dendrobium sanglant"),
    "Graines de Chrysanthèmes": Graines("Graines de Chrysanthèmes", 0, "Graines de Chrysanthèmes"),
    "Graines de Fleur de Qingxin": Graines("Graines de Fleur de Qingxin", 0, "Graines de Fleur de Qingxin"),
    "Graines de Fleur de soie": Graines("Graines de Fleur de soie", 0, "Graines de Fleur de soie"),
    "Graines de Fleur funéraire": Graines("Graines de Fleur funéraire", 0, "Graines de Fleur funéraire"),
    "Graines de Fleur sucrante": Graines("Graines de Fleur sucrante", 0, "Graines de Fleur sucrante"),
    "Graines de Gueule de loup": Graines("Graines de Gueule de loup", 0, "Graines de Gueule de loup"),
    "Graines d'Herbe à lampe": Graines("Graines d'Herbe à lampe", 0, "Graines d'Herbe à lampe"),
    "Graines d'Herbe à sanglots": Graines("Graines d'Herbe à sanglots", 0, "Graines d'Herbe à sanglots"),
    "Graines de Inteyvat": Graines("Graines de Inteyvat", 0, "Graines de Inteyvat"),
    "Graines de Kalpalotus": Graines("Graines de Kalpalotus", 0, "Graines de Kalpalotus"),
    "Graines de Lotus pluvieux": Graines("Graines de Lotus pluvieux", 0, "Graines de Lotus pluvieux"),
    "Graines de Lys calla": Graines("Graines de Lys calla", 0, "Graines de Lys calla"),
    "Graines de Lys lacmineux": Graines("Graines de Lys lacmineux", 0, "Graines de Lys lacmineux"),
    "Graines de Lys verni": Graines("Graines de Lys verni", 0, "Graines de Lys verni"),
    "Graines de Marcotte": Graines("Graines de Marcotte", 0, "Graines de Marcotte"),
    "Graines de Muget bleu": Graines("Graines de Muget bleu", 0, "Graines de Muget bleu"),
    "Graines de Padisachidée": Graines("Graines de Padisachidée", 0, "Graines de Padisachidée"),
    "Graines de Rose arc-en-ciel": Graines("Graines de Rose arc-en-ciel", 0, "Graines de Rose arc-en-ciel"),
    "Graines de Rose sumérienne": Graines("Graines de Rose sumérienne", 0, "Graines de Rose sumérienne"),
    "Graines de Viparyas": Graines("Graines de Viparyas", 0, "Graines de Viparyas"),

}

# Ajouter les graines au dictionnaire des textures
for nom, graine_obj in graines.items():
    texture_paths[graine_obj.nom] = graine_obj.texture

class Arrosoirs:
    def __init__(self, nom, rareté, texture=None):
        self.nom = nom
        self.rareté = rareté
        self.texture = f"../data/Arrosoirs/{nom}.png"

    def affichage_ar(self):
        # Retourne une représentation unicode simple de l'arrosoir
        return f"{self.nom} (Rareté: {self.rarete_texte()})"
    
    def rarete_texte(self):
        # Retourne une représentation unicode simple en fonction de la rareté
        if self.rareté == 1:
            return "C"
        elif self.rareté == 2:
            return "R"
        elif self.rareté == 3:
            return "SR"
        elif self.rareté == 0:
            return "En cours de développement"
    
    def __str__(self):
        return f"{self.nom} de rareté {self.rareté}"
    
arrosoirs = {
        "Arrosoir rouillé": Arrosoirs("Arrosoir rouillé", 0, "Arrosoir rouillé"),
        "Arrosoir rouillé rempli": Arrosoirs("Arrosoir rouillé rempli", 0, "Arrosoir rouillé rempli"),
        "Arrosoir en fer": Arrosoirs("Arrosoir en fer", 0, "Arrosoir en fer"),
        "Arrosoir en fer rempli": Arrosoirs("Arrosoir en fer rempli", 0, "Arrosoir en fer rempli"),
        "Arrosoir en or": Arrosoirs("Arrosoir en or", 0, "Arrosoir en or"),
        "Arrosoir en or rempli": Arrosoirs("Arrosoir en or rempli", 0, "Arrosoir en or rempli"),

    }

# Ajouter les arrosoirs au dictionnaire des textures
for nom, arrosoir_obj in arrosoirs.items():
    texture_paths[arrosoir_obj.nom] = arrosoir_obj.texture

# Test
if __name__ == "__main__":
    for nom, fleur in fleurs.items():
        print(fleur.affichage_fl())
    
    for nom, graine in graines.items():
        print(graine.affichage_gr())

    for nom, arrosoir in arrosoirs.items():
        print(arrosoir.affichage_ar())
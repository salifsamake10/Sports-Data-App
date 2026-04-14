class Joueur:
    def __init__(self, nom: str, poste: str, age: int = None, equipe=None):
        self.nom = nom
        self.poste = poste
        self.age = age
        self.equipe = equipe

        # Statistiques
        self.buts = 0
        self.passes = 0
        self.minutes_jouees = 0

    def mettre_a_jour_stats(self, match):
        pass 

    def __str__(self):
        return f"{self.nom} ({self.poste})"

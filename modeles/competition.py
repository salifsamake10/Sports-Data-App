class Competition:
    def __init__(self, nom: str, saison: str, pays=None):
        self.nom = nom
        self.saison = saison
        self.pays = pays

        self.equipes = []
        self.matchs = []

    def ajouter_equipe(self, equipe):
        self.equipes.append(equipe)

    def ajouter_match(self, match):
        self.matchs.append(match)

    def classement(self):
        return sorted(self.equipes, key=lambda e: (e.points, e.difference_buts()), reverse=True)

    def matchs_par_journee(self, journee):
        return [m for m in self.matchs if m.journee == journee]

    def __str__(self):
        return f"{self.nom} ({self.saison})"

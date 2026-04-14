class Equipe:
    def __init__(self, nom: str, pays=None, coach =None):
        self.nom = nom
        self.pays = pays
        self.coach = coach

        self.joueurs = []
        self.matchs = []

        # Statistiques
        self.victoires = 0
        self.defaites = 0
        self.nuls = 0
        self.buts_marques = 0
        self.buts_encaisses = 0
        self.points = 0

    def ajouter_joueur(self, joueur):
        self.joueurs.append(joueur)
        joueur.equipe = self

    def ajouter_match(self, match):
        self.matchs.append(match)

    def mettre_a_jour_stats(self, match):
        if match.equipe_domicile == self:
            self.buts_marques += match.score_dom
            self.buts_encaisses += match.score_ext
        else:
            self.buts_marques += match.score_ext
            self.buts_encaisses += match.score_dom

        if match.vainqueur() == self:
            self.victoires += 1
            self.points += 3
        elif match.est_nul():
            self.nuls += 1
            self.points += 1
        else:
            self.defaites += 1

    def difference_buts(self):
        return self.buts_marques - self.buts_encaisses

    def __str__(self):
        return f"Équipe {self.nom}"


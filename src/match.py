class Match:
    def __init__(self, date, equipe_domicile, equipe_exterieure,
                 score_dom=None, score_ext=None, competition=None, journee=None):
        self.date = date
        self.equipe_domicile = equipe_domicile
        self.equipe_exterieure = equipe_exterieure
        self.score_dom = score_dom
        self.score_ext = score_ext
        self.competition = competition
        self.journee = journee

        self.joueurs_domicile = []
        self.joueurs_exterieur = []

    def vainqueur(self):
        if self.score_dom is None or self.score_ext is None:
            return None
        if self.score_dom > self.score_ext:
            return self.equipe_domicile
        if self.score_ext > self.score_dom:
            return self.equipe_exterieure
        return None

    def est_nul(self):
        return self.score_dom == self.score_ext

    def difference_buts(self):
        return abs(self.score_dom - self.score_ext)

    def mettre_a_jour_equipes(self):
        self.equipe_domicile.mettre_a_jour_stats(self)
        self.equipe_exterieure.mettre_a_jour_stats(self)

    def __str__(self):
        return f"{self.equipe_domicile.nom} {self.score_dom} - {self.score_ext} {self.equipe_exterieure.nom}"

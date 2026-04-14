class ChargeurBase:
    def charger_pays(self):
        raise NotImplementedError

    def charger_competitions(self):
        raise NotImplementedError

    def charger_equipes(self):
        raise NotImplementedError

    def charger_joueurs(self):
        raise NotImplementedError

    def charger_matchs(self):
        raise NotImplementedError

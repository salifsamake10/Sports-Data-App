import pandas as pd
from modeles.pays import Pays
from modeles.equipe import Equipe
from modeles.joueur import Joueur
from modeles.match import Match
from modeles.competition import Competition
from chargeurs.chargeur_base import ChargeurBase

class ChargeurFootball(ChargeurBase):

    def __init__(self, chemin):
        self.chemin = chemin

    def charger_pays(self):
        df = pd.read_csv(self.chemin + "country.csv")
        return {row["id"]: Pays(row["name"]) for _, row in df.iterrows()}

    def charger_competitions(self, pays):
        df = pd.read_csv(self.chemin + "league.csv")
        return {row["id"]: Competition(row["name"], None, pays[row["country_id"]])
                for _, row in df.iterrows()}

    def charger_equipes(self):
        df = pd.read_csv(self.chemin + "team.csv")
        return {row["team_api_id"]: Equipe(row["team_long_name"])
                for _, row in df.iterrows()}

    def charger_joueurs(self):
        df = pd.read_csv(self.chemin + "player.csv")
        return {row["player_api_id"]: Joueur(row["player_name"], "Inconnu")
                for _, row in df.iterrows()}

    def charger_matchs(self, competitions, equipes):
        df = pd.read_csv(self.chemin + "match.csv")
        matchs = []
        for _, row in df.iterrows():
            match = Match(
                date=row["date"],
                equipe_domicile=equipes[row["home_team_api_id"]],
                equipe_exterieure=equipes[row["away_team_api_id"]],
                score_dom=row["home_team_goal"],
                score_ext=row["away_team_goal"],
                competition=competitions[row["league_id"]],
                journee=row["stage"]
            )
            matchs.append(match)
        return matchs

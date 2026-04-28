"""Tests du mapper (transformation dict → objets)."""

import pytest

from src.data import DataMapper
from src.models import Competition, Equipe


CONFIG_FOOT = {
    "sport": "Football",
    "competition": "Ligue 1",
    "categorie": "Senior",
    "genre": "MASCULIN",
    "type_participant": "equipe",
    "type_resultat": "buts",
    "saison": {"debut": 2023, "fin": 2024},
    "pays_defaut": {"nom": "France", "code": "FRA"},
    "mapping": {
        "date": "Date",
        "participant_dom": "HomeTeam",
        "participant_ext": "AwayTeam",
        "score_dom": "FTHG",
        "score_ext": "FTAG",
        "phase": "Phase",
    },
}


class TestDataMapper:
    def test_construit_competition(self):
        mapper = DataMapper(CONFIG_FOOT)
        donnees = [
            {
                "Date": "2023-08-12",
                "HomeTeam": "PSG",
                "AwayTeam": "OM",
                "FTHG": "2",
                "FTAG": "0",
                "Phase": "J1",
            }
        ]
        competition = mapper.construire_competition(donnees)
        assert isinstance(competition, Competition)
        assert competition.nom == "Ligue 1"

    def test_cree_participants_uniques(self):
        """Une même équipe apparaissant plusieurs fois doit être un seul objet."""
        mapper = DataMapper(CONFIG_FOOT)
        donnees = [
            {"Date": "2023-08-12", "HomeTeam": "PSG", "AwayTeam": "OM",
             "FTHG": "2", "FTAG": "0", "Phase": "J1"},
            {"Date": "2023-08-19", "HomeTeam": "OM", "AwayTeam": "PSG",
             "FTHG": "1", "FTAG": "3", "Phase": "J2"},
        ]
        competition = mapper.construire_competition(donnees)
        # PSG et OM = 2 participants uniques
        assert len(competition.participants) == 2

    def test_construit_equipes(self):
        mapper = DataMapper(CONFIG_FOOT)
        donnees = [
            {"Date": "2023-08-12", "HomeTeam": "PSG", "AwayTeam": "OM",
             "FTHG": "2", "FTAG": "0", "Phase": "J1"},
        ]
        competition = mapper.construire_competition(donnees)
        for p in competition.participants:
            assert isinstance(p, Equipe)

    def test_classement_calcule(self):
        mapper = DataMapper(CONFIG_FOOT)
        donnees = [
            {"Date": "2023-08-12", "HomeTeam": "PSG", "AwayTeam": "OM",
             "FTHG": "3", "FTAG": "0", "Phase": "J1"},
        ]
        competition = mapper.construire_competition(donnees)
        psg = next(p for p in competition.participants if p.nom == "PSG")
        om = next(p for p in competition.participants if p.nom == "OM")
        assert psg.get_stat("buts").valeur == 3.0
        assert om.get_stat("buts").valeur == 0.0

    def test_ligne_incomplete_ignoree(self):
        mapper = DataMapper(CONFIG_FOOT)
        donnees = [
            {"Date": "2023-08-12", "HomeTeam": "", "AwayTeam": "OM",
             "FTHG": "2", "FTAG": "0", "Phase": "J1"},
        ]
        competition = mapper.construire_competition(donnees)
        assert len(competition.matchs) == 0

"""Tests du mapper relationnel — cœur de la généricité du projet."""

from pathlib import Path

import pytest

from src.data import RelationalMapper
from src.models import Competition, Equipe, Joueur


@pytest.fixture
def dossier_foot_factice(tmp_path: Path) -> Path:
    """Crée un mini dataset football relationnel."""
    (tmp_path / "team.csv").write_text(
        "team_api_id,team_long_name\n100,PSG\n101,OM\n102,Lyon\n",
        encoding="utf-8",
    )
    (tmp_path / "match.csv").write_text(
        "league_id,season,date,home_team_api_id,away_team_api_id,"
        "home_team_goal,away_team_goal,stage\n"
        "4769,2015/2016,2015-08-08,100,101,3,1,1\n"
        "4769,2015/2016,2015-08-15,102,100,0,2,2\n"
        "4769,2015/2016,2015-08-22,101,102,1,1,3\n"
        "1729,2015/2016,2015-08-08,200,201,1,0,1\n",
        encoding="utf-8",
    )
    return tmp_path


@pytest.fixture
def config_foot(dossier_foot_factice: Path) -> dict:
    return {
        "type_mapper": "relationnel",
        "sport": "Football",
        "competition": "Ligue 1 Test",
        "type_participant": "equipe",
        "type_resultat": "buts",
        "saison": {"debut": 2015, "fin": 2016},
        "pays_defaut": {"nom": "France", "code": "FRA"},
        "dossier": str(dossier_foot_factice),
        "fichier_matchs": "match.csv",
        "fichier_participants": "team.csv",
        "mapping_participant": {"id": "team_api_id", "nom": "team_long_name"},
        "mapping_match": {
            "date": "date",
            "participant_1": "home_team_api_id",
            "participant_2": "away_team_api_id",
            "score_1": "home_team_goal",
            "score_2": "away_team_goal",
            "phase": "stage",
        },
        "filtres": {"league_id": "4769", "season": "2015/2016"},
    }


class TestRelationalMapperFootball:
    def test_construire_competition_retourne_competition(self, config_foot):
        mapper = RelationalMapper(config_foot)
        competition = mapper.construire_competition()
        assert isinstance(competition, Competition)
        assert competition.nom == "Ligue 1 Test"

    def test_filtres_appliques_correctement(self, config_foot):
        """Le filtre doit garder seulement les matchs de la Ligue 1."""
        mapper = RelationalMapper(config_foot)
        competition = mapper.construire_competition()
        # 3 matchs Ligue 1 + 1 match Premier League → 3 retenus
        assert len(competition.matchs) == 3

    def test_participants_charges_depuis_fichier(self, config_foot):
        mapper = RelationalMapper(config_foot)
        competition = mapper.construire_competition()
        noms = {p.nom for p in competition.participants}
        assert "PSG" in noms
        assert "OM" in noms
        assert "Lyon" in noms

    def test_participants_sont_des_equipes(self, config_foot):
        mapper = RelationalMapper(config_foot)
        competition = mapper.construire_competition()
        for p in competition.participants:
            assert isinstance(p, Equipe)

    def test_classement_calcule(self, config_foot):
        """PSG devrait avoir 2 victoires (3-1 et 0-2)."""
        mapper = RelationalMapper(config_foot)
        competition = mapper.construire_competition()
        psg = next(p for p in competition.participants if p.nom == "PSG")
        # PSG a marqué 3+2 = 5 buts
        assert psg.get_stat("buts").valeur == 5.0


class TestRelationalMapperTennis:
    """Test du mode winner_loser pour le tennis."""

    def test_mode_winner_loser(self, tmp_path):
        # Mini dataset tennis
        (tmp_path / "matches.csv").write_text(
            "tourney_date,winner_id,loser_id,round\n"
            "20240101,100,101,F\n"
            "20240102,100,102,SF\n"
            "20240103,101,102,QF\n",
            encoding="utf-8",
        )
        (tmp_path / "players.csv").write_text(
            "player_id,name_first,name_last\n"
            "100,Novak,Djokovic\n"
            "101,Carlos,Alcaraz\n"
            "102,Jannik,Sinner\n",
            encoding="utf-8",
        )

        config = {
            "type_mapper": "relationnel",
            "sport": "Tennis",
            "competition": "ATP Test",
            "type_participant": "joueur",
            "type_resultat": "victoire",
            "mode_resultat": "winner_loser",
            "saison": {"debut": 2024, "fin": 2024},
            "pays_defaut": {"nom": "INT", "code": "INT"},
            "dossier": str(tmp_path),
            "fichier_matchs": "matches.csv",
            "fichier_participants": "players.csv",
            "mapping_participant": {"id": "player_id", "nom": "name_last"},
            "mapping_match": {
                "date": "tourney_date",
                "participant_1": "winner_id",
                "participant_2": "loser_id",
                "phase": "round",
            },
        }

        mapper = RelationalMapper(config)
        competition = mapper.construire_competition()

        # Djokovic a 2 victoires
        djoko = next(p for p in competition.participants if p.nom == "Djokovic")
        assert djoko.get_stat("victoire").valeur == 2.0
        assert isinstance(djoko, Joueur)


class TestRelationalMapperEcheances:
    def test_pas_de_fichier_participants_optionnel(self, tmp_path):
        """Échecs : participants créés à la volée sans fichier."""
        (tmp_path / "matches.csv").write_text(
            "round,player_1,player_2,score_player_1,score_player_2\n"
            "1,Carlsen,Nakamura,1,0\n"
            "2,Carlsen,Caruana,0.5,0.5\n",
            encoding="utf-8",
        )

        config = {
            "type_mapper": "relationnel",
            "sport": "Échecs",
            "competition": "Tournoi Test",
            "type_participant": "joueur",
            "type_resultat": "score",
            "saison": {"debut": 2024, "fin": 2024},
            "pays_defaut": {"nom": "INT", "code": "INT"},
            "dossier": str(tmp_path),
            "fichier_matchs": "matches.csv",
            "mapping_match": {
                "date": "round",
                "participant_1": "player_1",
                "participant_2": "player_2",
                "score_1": "score_player_1",
                "score_2": "score_player_2",
            },
        }

        mapper = RelationalMapper(config)
        competition = mapper.construire_competition()
        assert len(competition.matchs) == 2
        assert len(competition.participants) == 3


class TestNettoyagePandas:
    def test_supprime_doublons(self, dossier_foot_factice, config_foot):
        """Doublons exacts dans le CSV → 1 seul match."""
        # Ajout d'un doublon
        chemin = dossier_foot_factice / "match.csv"
        contenu = chemin.read_text() + "4769,2015/2016,2015-08-08,100,101,3,1,1\n"
        chemin.write_text(contenu, encoding="utf-8")

        mapper = RelationalMapper(config_foot)
        competition = mapper.construire_competition()
        # 3 uniques (le doublon doit être ignoré)
        assert len(competition.matchs) == 3

    def test_gere_valeurs_manquantes(self, tmp_path, config_foot):
        """Une ligne avec score manquant doit être ignorée."""
        (tmp_path / "team.csv").write_text(
            "team_api_id,team_long_name\n100,PSG\n101,OM\n",
            encoding="utf-8",
        )
        (tmp_path / "match.csv").write_text(
            "league_id,season,date,home_team_api_id,away_team_api_id,"
            "home_team_goal,away_team_goal,stage\n"
            "4769,2015/2016,2015-08-08,100,101,3,1,1\n"
            "4769,2015/2016,2015-08-15,100,101,NA,NA,2\n",
            encoding="utf-8",
        )
        config_foot["dossier"] = str(tmp_path)
        mapper = RelationalMapper(config_foot)
        competition = mapper.construire_competition()
        # Seul le 1er match valide est gardé
        assert len(competition.matchs) == 1

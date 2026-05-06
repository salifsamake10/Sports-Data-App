"""Tests du service de statistiques."""

from datetime import date

import pytest

from src.models import Match, MatchStatus, Resultat
from src.services import StatistiquesService


@pytest.fixture
def competition_complete(competition_ligue1, equipe_psg, equipe_om):
    """Competition avec un match terminé."""
    m = Match(id=1, date=date(2024, 1, 1), participants=[equipe_psg, equipe_om])
    m.ajouter_resultat(Resultat(1, 4, "buts", equipe_psg))
    m.ajouter_resultat(Resultat(2, 1, "buts", equipe_om))
    m.statut = MatchStatus.TERMINE
    competition_ligue1.ajouter_match(m)
    competition_ligue1.mettre_a_jour_classement()
    return competition_ligue1


class TestStatistiquesService:
    def test_meilleure_attaque(self, competition_complete, equipe_psg):
        meilleur = StatistiquesService.meilleur_attaque(competition_complete)
        assert meilleur == equipe_psg

    def test_meilleure_defense(self, competition_complete, equipe_psg):
        # PSG a encaissé 1, OM a encaissé 4 → PSG meilleure défense
        meilleure = StatistiquesService.meilleure_defense(competition_complete)
        assert meilleure == equipe_psg

    def test_moyenne_par_match(self, competition_complete):
        # 4 + 1 = 5 buts en 1 match
        moyenne = StatistiquesService.moyenne_par_match(competition_complete)
        assert moyenne == 5.0

    def test_moyenne_aucun_match(self, competition_ligue1):
        moyenne = StatistiquesService.moyenne_par_match(competition_ligue1)
        assert moyenne == 0.0

    def test_top_n_buteurs(self, competition_complete, equipe_psg, equipe_om):
        top = StatistiquesService.top_n_buteurs(competition_complete, n=2)
        assert top[0][0] == equipe_psg
        assert top[0][1] == 4.0
        assert top[1][0] == equipe_om

    def test_matchs_avec_plus_de(self, competition_complete):
        # Le match a 5 buts au total → > 4
        matchs = StatistiquesService.matchs_avec_plus_de(competition_complete, seuil=4)
        assert len(matchs) == 1

    def test_matchs_avec_plus_de_seuil_non_atteint(self, competition_complete):
        matchs = StatistiquesService.matchs_avec_plus_de(competition_complete, seuil=10)
        assert len(matchs) == 0

    def test_taux_match_nul(self, competition_ligue1, equipe_psg, equipe_om):
        m = Match(id=1, date=date(2024, 1, 1), participants=[equipe_psg, equipe_om])
        m.ajouter_resultat(Resultat(1, 1, "buts", equipe_psg))
        m.ajouter_resultat(Resultat(2, 1, "buts", equipe_om))
        m.statut = MatchStatus.TERMINE
        competition_ligue1.ajouter_match(m)
        assert StatistiquesService.taux_match_nul(competition_ligue1) == 1.0

    def test_rapport_global(self, competition_complete):
        rapport = StatistiquesService.rapport_global(competition_complete)
        assert rapport["nom"] == "Ligue 1"
        assert rapport["sport"] == "Football"
        assert rapport["nb_matchs_termines"] == 1
        assert rapport["moyenne_buts_par_match"] == 5.0

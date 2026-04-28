"""Tests du service de classement."""

from datetime import date

import pytest

from src.models import Match, MatchStatus, Resultat
from src.services import ClassementService


@pytest.fixture
def competition_avec_matchs(competition_ligue1, equipe_psg, equipe_om, france):
    """Compétition avec 2 matchs PSG-OM (un avec victoire PSG, un nul)."""
    from src.models import Equipe, Genre
    lyon = Equipe(id=12, nom="Lyon", pays=france, genre=Genre.MASCULIN)

    # Match 1 : PSG bat OM 3-1
    m1 = Match(id=1, date=date(2024, 1, 1), participants=[equipe_psg, equipe_om])
    m1.ajouter_resultat(Resultat(1, 3, "buts", equipe_psg))
    m1.ajouter_resultat(Resultat(2, 1, "buts", equipe_om))
    m1.statut = MatchStatus.TERMINE

    # Match 2 : PSG vs Lyon nul 2-2
    m2 = Match(id=2, date=date(2024, 1, 8), participants=[equipe_psg, lyon])
    m2.ajouter_resultat(Resultat(3, 2, "buts", equipe_psg))
    m2.ajouter_resultat(Resultat(4, 2, "buts", lyon))
    m2.statut = MatchStatus.TERMINE

    # Match 3 : OM bat Lyon 1-0
    m3 = Match(id=3, date=date(2024, 1, 15), participants=[equipe_om, lyon])
    m3.ajouter_resultat(Resultat(5, 1, "buts", equipe_om))
    m3.ajouter_resultat(Resultat(6, 0, "buts", lyon))
    m3.statut = MatchStatus.TERMINE

    competition_ligue1.ajouter_match(m1)
    competition_ligue1.ajouter_match(m2)
    competition_ligue1.ajouter_match(m3)
    return competition_ligue1


class TestClassement310:
    def test_classement_3_1_0(self, competition_avec_matchs, equipe_psg):
        classement = ClassementService.classement_par_points_3_1_0(
            competition_avec_matchs
        )
        # PSG : 1 victoire (3) + 1 nul (1) = 4 points
        psg_ligne = next(l for l in classement if l["participant"] == equipe_psg)
        assert psg_ligne["points"] == 4
        assert psg_ligne["victoires"] == 1
        assert psg_ligne["nuls"] == 1
        assert psg_ligne["defaites"] == 0

    def test_premier_du_classement(self, competition_avec_matchs, equipe_psg):
        classement = ClassementService.classement_par_points_3_1_0(
            competition_avec_matchs
        )
        assert classement[0]["participant"] == equipe_psg

    def test_difference_de_buts(self, competition_avec_matchs, equipe_psg):
        classement = ClassementService.classement_par_points_3_1_0(
            competition_avec_matchs
        )
        psg_ligne = next(l for l in classement if l["participant"] == equipe_psg)
        # PSG : marqués 3+2=5, encaissés 1+2=3 → diff +2
        assert psg_ligne["marques"] == 5
        assert psg_ligne["encaisses"] == 3
        assert psg_ligne["difference"] == 2

    def test_ignore_matchs_non_termines(
        self, competition_ligue1, match_psg_om
    ):
        # match_psg_om a statut PLANIFIE par défaut
        competition_ligue1.ajouter_match(match_psg_om)
        classement = ClassementService.classement_par_points_3_1_0(
            competition_ligue1
        )
        for ligne in classement:
            assert ligne["points"] == 0
            assert ligne["joues"] == 0


class TestClassementVictoires:
    def test_classement_par_victoires(self, competition_avec_matchs, equipe_psg):
        classement = ClassementService.classement_par_victoires(
            competition_avec_matchs
        )
        psg_ligne = next(l for l in classement if l["participant"] == equipe_psg)
        assert psg_ligne["victoires"] == 1

    def test_ratio_calcule(self, competition_avec_matchs, equipe_psg):
        classement = ClassementService.classement_par_victoires(
            competition_avec_matchs
        )
        psg_ligne = next(l for l in classement if l["participant"] == equipe_psg)
        # PSG : 1 victoire / 2 matchs = 0.5
        assert psg_ligne["ratio"] == 0.5


class TestAffichage:
    def test_affichage_classement_points(self, competition_avec_matchs):
        classement = ClassementService.classement_par_points_3_1_0(
            competition_avec_matchs
        )
        affichage = ClassementService.afficher_classement(classement)
        assert "PSG" in affichage
        assert "Pts" in affichage

    def test_affichage_classement_vide(self):
        affichage = ClassementService.afficher_classement([])
        assert "Aucun" in affichage

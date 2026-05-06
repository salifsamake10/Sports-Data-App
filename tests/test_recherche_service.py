"""Tests du service de recherche."""

from datetime import date

import pytest

from src.models import Match, MatchStatus
from src.services import RechercheService


@pytest.fixture
def competition_pour_recherche(competition_ligue1, equipe_psg, equipe_om, france):
    from src.models import Equipe, Genre

    lyon = Equipe(id=12, nom="Lyon", pays=france, genre=Genre.MASCULIN)

    m1 = Match(
        id=1,
        date=date(2024, 1, 5),
        participants=[equipe_psg, equipe_om],
        phase="J1",
        statut=MatchStatus.TERMINE,
    )
    m2 = Match(
        id=2,
        date=date(2024, 1, 12),
        participants=[equipe_psg, lyon],
        phase="J2",
        statut=MatchStatus.TERMINE,
    )
    m3 = Match(
        id=3,
        date=date(2024, 2, 1),
        participants=[equipe_om, lyon],
        phase="J3",
        statut=MatchStatus.PLANIFIE,
    )
    competition_ligue1.ajouter_match(m1)
    competition_ligue1.ajouter_match(m2)
    competition_ligue1.ajouter_match(m3)
    return competition_ligue1


class TestRechercheService:
    def test_chercher_participant_par_nom_partiel(self, competition_pour_recherche, equipe_psg):
        resultats = RechercheService.chercher_participant_par_nom(competition_pour_recherche, "PSG")
        assert equipe_psg in resultats

    def test_chercher_insensible_a_la_casse(self, competition_pour_recherche, equipe_psg):
        resultats = RechercheService.chercher_participant_par_nom(competition_pour_recherche, "psg")
        assert equipe_psg in resultats

    def test_chercher_exact(self, competition_pour_recherche):
        resultats = RechercheService.chercher_participant_par_nom(
            competition_pour_recherche, "ps", exact=True
        )
        assert len(resultats) == 0

    def test_matchs_entre_dates(self, competition_pour_recherche):
        matchs = RechercheService.matchs_entre_dates(
            competition_pour_recherche,
            debut=date(2024, 1, 1),
            fin=date(2024, 1, 31),
        )
        assert len(matchs) == 2

    def test_matchs_par_phase(self, competition_pour_recherche):
        matchs = RechercheService.matchs_par_phase(competition_pour_recherche, "J1")
        assert len(matchs) == 1

    def test_matchs_par_statut(self, competition_pour_recherche):
        termines = RechercheService.matchs_par_statut(
            competition_pour_recherche, MatchStatus.TERMINE
        )
        planifies = RechercheService.matchs_par_statut(
            competition_pour_recherche, MatchStatus.PLANIFIE
        )
        assert len(termines) == 2
        assert len(planifies) == 1

    def test_confrontation_directe(self, competition_pour_recherche, equipe_psg, equipe_om):
        matchs = RechercheService.confrontation_directe(
            competition_pour_recherche, equipe_psg, equipe_om
        )
        assert len(matchs) == 1

    def test_filtrer_matchs_combine(self, competition_pour_recherche, equipe_psg):
        matchs = RechercheService.filtrer_matchs(
            competition_pour_recherche,
            statut=MatchStatus.TERMINE,
            participant=equipe_psg,
        )
        assert len(matchs) == 2  # 2 matchs terminés impliquant PSG

    def test_filtrer_par_dates(self, competition_pour_recherche):
        matchs = RechercheService.filtrer_matchs(
            competition_pour_recherche,
            date_min=date(2024, 1, 10),
            date_max=date(2024, 1, 20),
        )
        assert len(matchs) == 1

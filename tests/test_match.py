"""Tests de la classe Match."""

from datetime import date

import pytest

from src.models import Match, MatchStatus, Resultat


class TestMatch:
    def test_creation_valide(self, match_psg_om):
        assert match_psg_om.id == 100
        assert match_psg_om.statut == MatchStatus.PLANIFIE
        assert len(match_psg_om.participants) == 2
        assert match_psg_om.phase == "Journée 27"

    def test_moins_de_2_participants_leve_erreur(self, equipe_psg):
        with pytest.raises(ValueError, match="au moins 2 participants"):
            Match(
                id=1,
                date=date(2024, 1, 1),
                participants=[equipe_psg],
            )

    def test_ajouter_resultat(self, match_psg_om, equipe_psg):
        resultat = Resultat(id=1, valeur=3, type="buts", participant=equipe_psg)
        match_psg_om.ajouter_resultat(resultat)
        assert len(match_psg_om.resultats) == 1

    def test_ajouter_resultat_participant_externe_leve_erreur(
        self, match_psg_om, joueur_messi
    ):
        resultat = Resultat(id=1, valeur=1, type="buts", participant=joueur_messi)
        with pytest.raises(ValueError, match="ne fait pas partie"):
            match_psg_om.ajouter_resultat(resultat)

    def test_get_score_participant(self, match_psg_om, equipe_psg):
        match_psg_om.ajouter_resultat(
            Resultat(id=1, valeur=2, type="buts", participant=equipe_psg)
        )
        match_psg_om.ajouter_resultat(
            Resultat(id=2, valeur=1, type="buts", participant=equipe_psg)
        )
        assert match_psg_om.get_score_participant(equipe_psg) == 3.0

    def test_get_vainqueur_match_planifie(self, match_psg_om):
        """Un match non terminé ne peut pas avoir de vainqueur."""
        assert match_psg_om.get_vainqueur() is None

    def test_get_vainqueur_match_termine(self, match_psg_om, equipe_psg, equipe_om):
        match_psg_om.ajouter_resultat(
            Resultat(id=1, valeur=3, type="buts", participant=equipe_psg)
        )
        match_psg_om.ajouter_resultat(
            Resultat(id=2, valeur=1, type="buts", participant=equipe_om)
        )
        match_psg_om.statut = MatchStatus.TERMINE
        assert match_psg_om.get_vainqueur() == equipe_psg

    def test_match_nul(self, match_psg_om, equipe_psg, equipe_om):
        match_psg_om.ajouter_resultat(
            Resultat(id=1, valeur=2, type="buts", participant=equipe_psg)
        )
        match_psg_om.ajouter_resultat(
            Resultat(id=2, valeur=2, type="buts", participant=equipe_om)
        )
        match_psg_om.statut = MatchStatus.TERMINE
        assert match_psg_om.est_nul() is True
        assert match_psg_om.get_vainqueur() is None

    def test_pas_nul_si_pas_termine(self, match_psg_om):
        assert match_psg_om.est_nul() is False

    def test_get_resultats_participant(self, match_psg_om, equipe_psg, equipe_om):
        r1 = Resultat(id=1, valeur=2, type="buts", participant=equipe_psg)
        r2 = Resultat(id=2, valeur=1, type="buts", participant=equipe_om)
        match_psg_om.ajouter_resultat(r1)
        match_psg_om.ajouter_resultat(r2)

        psg_results = match_psg_om.get_resultats_participant(equipe_psg)
        assert len(psg_results) == 1
        assert psg_results[0] == r1

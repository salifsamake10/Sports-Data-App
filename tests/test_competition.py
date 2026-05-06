"""Tests de la classe Competition."""

import pytest

from src.models import MatchStatus, Resultat


class TestCompetition:
    def test_creation_valide(self, competition_ligue1):
        assert competition_ligue1.nom == "Ligue 1"
        assert competition_ligue1.matchs == []
        assert competition_ligue1.participants == []

    def test_nom_vide_leve_erreur(self, football, saison_2023):
        from src.models import Competition

        with pytest.raises(ValueError):
            Competition(id=1, nom="", sport=football, saison=saison_2023)

    def test_ajouter_participant(self, competition_ligue1, equipe_psg):
        competition_ligue1.ajouter_participant(equipe_psg)
        assert equipe_psg in competition_ligue1.participants

    def test_ajouter_participant_doublon_leve_erreur(self, competition_ligue1, equipe_psg):
        competition_ligue1.ajouter_participant(equipe_psg)
        with pytest.raises(ValueError, match="déjà inscrit"):
            competition_ligue1.ajouter_participant(equipe_psg)

    def test_ajouter_match_inscrit_participants(
        self, competition_ligue1, match_psg_om, equipe_psg, equipe_om
    ):
        """Ajouter un match inscrit automatiquement les participants."""
        competition_ligue1.ajouter_match(match_psg_om)
        assert equipe_psg in competition_ligue1.participants
        assert equipe_om in competition_ligue1.participants
        assert match_psg_om in competition_ligue1.matchs

    def test_get_matchs_participant(self, competition_ligue1, match_psg_om, equipe_psg):
        competition_ligue1.ajouter_match(match_psg_om)
        matchs = competition_ligue1.get_matchs_participant(equipe_psg)
        assert match_psg_om in matchs

    def test_mettre_a_jour_classement(
        self, competition_ligue1, match_psg_om, equipe_psg, equipe_om
    ):
        match_psg_om.ajouter_resultat(Resultat(id=1, valeur=3, type="buts", participant=equipe_psg))
        match_psg_om.ajouter_resultat(Resultat(id=2, valeur=1, type="buts", participant=equipe_om))
        match_psg_om.statut = MatchStatus.TERMINE
        competition_ligue1.ajouter_match(match_psg_om)

        competition_ligue1.mettre_a_jour_classement()

        assert equipe_psg.get_stat("buts").valeur == 3.0
        assert equipe_om.get_stat("buts").valeur == 1.0

    def test_get_classement(self, competition_ligue1, match_psg_om, equipe_psg, equipe_om):
        match_psg_om.ajouter_resultat(Resultat(id=1, valeur=3, type="buts", participant=equipe_psg))
        match_psg_om.ajouter_resultat(Resultat(id=2, valeur=1, type="buts", participant=equipe_om))
        match_psg_om.statut = MatchStatus.TERMINE
        competition_ligue1.ajouter_match(match_psg_om)
        competition_ligue1.mettre_a_jour_classement()

        classement = competition_ligue1.get_classement(critere="buts")
        assert classement[0] == equipe_psg
        assert classement[1] == equipe_om

    def test_get_statistiques(self, competition_ligue1, match_psg_om, equipe_psg, equipe_om):
        match_psg_om.ajouter_resultat(Resultat(id=1, valeur=2, type="buts", participant=equipe_psg))
        match_psg_om.ajouter_resultat(Resultat(id=2, valeur=2, type="buts", participant=equipe_om))
        match_psg_om.statut = MatchStatus.TERMINE
        competition_ligue1.ajouter_match(match_psg_om)

        stats = competition_ligue1.get_statistiques()
        assert stats["nb_matchs"] == 1
        assert stats["nb_matchs_termines"] == 1
        assert stats["nb_participants"] == 2
        assert stats["nb_matchs_nuls"] == 1

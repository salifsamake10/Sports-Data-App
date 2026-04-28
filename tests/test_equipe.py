"""Tests de la classe Equipe."""

import pytest

from src.models import Equipe, Genre, Resultat


class TestEquipe:
    def test_creation_vide(self, equipe_psg):
        assert equipe_psg.nom == "PSG"
        assert equipe_psg.joueurs == []
        assert equipe_psg.genre == Genre.MASCULIN

    def test_ajouter_joueur(self, equipe_psg, joueur_messi):
        equipe_psg.ajouter_joueur(joueur_messi)
        assert joueur_messi in equipe_psg.joueurs
        assert len(equipe_psg.joueurs) == 1

    def test_ajouter_joueur_doublon_leve_erreur(self, equipe_psg, joueur_messi):
        equipe_psg.ajouter_joueur(joueur_messi)
        with pytest.raises(ValueError, match="déjà partie"):
            equipe_psg.ajouter_joueur(joueur_messi)

    def test_retirer_joueur(self, equipe_psg, joueur_messi):
        equipe_psg.ajouter_joueur(joueur_messi)
        equipe_psg.retirer_joueur(joueur_messi)
        assert joueur_messi not in equipe_psg.joueurs

    def test_retirer_joueur_inexistant_leve_erreur(self, equipe_psg, joueur_messi):
        with pytest.raises(ValueError, match="ne fait pas partie"):
            equipe_psg.retirer_joueur(joueur_messi)

    def test_update_stats(self, equipe_psg):
        resultat = Resultat(id=1, valeur=3, type="buts", participant=equipe_psg)
        equipe_psg.update_stats(resultat)
        assert equipe_psg.get_stat("buts").valeur == 3.0

    def test_update_stats_cumule(self, equipe_psg):
        r1 = Resultat(id=1, valeur=2, type="buts", participant=equipe_psg)
        r2 = Resultat(id=2, valeur=3, type="buts", participant=equipe_psg)
        equipe_psg.update_stats(r1)
        equipe_psg.update_stats(r2)
        assert equipe_psg.get_stat("buts").valeur == 5.0

    def test_serialisation(self, equipe_psg, joueur_messi):
        equipe_psg.ajouter_joueur(joueur_messi)
        data = equipe_psg.to_dict()
        assert data["nom"] == "PSG"
        assert len(data["joueurs"]) == 1
        assert data["genre"] == "MASCULIN"

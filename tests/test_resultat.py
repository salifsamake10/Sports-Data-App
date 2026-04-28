"""Tests de la classe Resultat."""

import pytest

from src.models import Resultat


class TestResultat:
    def test_creation_valide(self, joueur_messi):
        resultat = Resultat(id=1, valeur=2, type="buts", participant=joueur_messi)
        assert resultat.id == 1
        assert resultat.valeur == 2.0
        assert resultat.type == "buts"
        assert resultat.participant == joueur_messi

    def test_type_vide_leve_erreur(self, joueur_messi):
        with pytest.raises(ValueError, match="type de résultat"):
            Resultat(id=1, valeur=2, type="", participant=joueur_messi)

    def test_egalite_par_id(self, joueur_messi, joueur_ronaldo):
        r1 = Resultat(id=1, valeur=2, type="buts", participant=joueur_messi)
        r2 = Resultat(id=1, valeur=5, type="sets", participant=joueur_ronaldo)
        assert r1 == r2

    def test_serialisation(self, joueur_messi):
        resultat = Resultat(id=1, valeur=3, type="buts", participant=joueur_messi)
        data = resultat.to_dict()
        assert data == {
            "id": 1,
            "valeur": 3.0,
            "type": "buts",
            "participant_id": joueur_messi.id,
        }

    def test_resultat_echecs(self, joueur_messi):
        """Un Resultat doit pouvoir représenter un résultat d'échecs."""
        resultat = Resultat(id=1, valeur=1.0, type="victoire", participant=joueur_messi)
        assert resultat.type == "victoire"
        assert resultat.valeur == 1.0

    def test_resultat_demi_point_echecs(self, joueur_messi):
        """Aux échecs, un nul vaut 0.5."""
        resultat = Resultat(id=1, valeur=0.5, type="nul", participant=joueur_messi)
        assert resultat.valeur == 0.5

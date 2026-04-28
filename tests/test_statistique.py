"""Tests de la classe Statistique."""

import pytest

from src.models import Statistique


class TestStatistique:
    def test_creation_valide(self):
        stat = Statistique(nom="buts", valeur=12, unite="buts")
        assert stat.nom == "buts"
        assert stat.valeur == 12.0
        assert stat.unite == "buts"

    def test_unite_optionnelle(self):
        stat = Statistique(nom="elo", valeur=1850)
        assert stat.unite == ""

    def test_valeur_convertie_en_float(self):
        stat = Statistique(nom="points", valeur=15)
        assert isinstance(stat.valeur, float)
        assert stat.valeur == 15.0

    def test_nom_vide_leve_erreur(self):
        with pytest.raises(ValueError):
            Statistique(nom="", valeur=10)

    def test_mettre_a_jour(self):
        stat = Statistique(nom="buts", valeur=5)
        stat.mettre_a_jour(20)
        assert stat.valeur == 20.0

    def test_incrementer_par_defaut(self):
        stat = Statistique(nom="buts", valeur=5)
        stat.incrementer()
        assert stat.valeur == 6.0

    def test_incrementer_avec_delta(self):
        stat = Statistique(nom="buts", valeur=5)
        stat.incrementer(3)
        assert stat.valeur == 8.0

    def test_serialisation(self):
        stat = Statistique(nom="sets", valeur=2.5, unite="sets")
        data = stat.to_dict()
        assert data == {"nom": "sets", "valeur": 2.5, "unite": "sets"}

    def test_deserialisation(self):
        stat = Statistique.from_dict({"nom": "elo", "valeur": 1900, "unite": "points"})
        assert stat.nom == "elo"
        assert stat.valeur == 1900.0

    def test_egalite_meme_nom_meme_valeur(self):
        s1 = Statistique(nom="buts", valeur=10)
        s2 = Statistique(nom="buts", valeur=10, unite="autre")
        assert s1 == s2

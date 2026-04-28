"""Tests des classes Sport, Saison, Pays."""

import pytest

from src.models import Pays, Saison, Sport


class TestSport:
    def test_creation_valide(self):
        sport = Sport(id=1, nom="Football")
        assert sport.id == 1
        assert sport.nom == "Football"

    def test_nom_vide_leve_erreur(self):
        with pytest.raises(ValueError, match="ne peut pas être vide"):
            Sport(id=1, nom="")

    def test_nom_blanc_leve_erreur(self):
        with pytest.raises(ValueError):
            Sport(id=1, nom="   ")

    def test_egalite_par_id(self):
        s1 = Sport(id=1, nom="Football")
        s2 = Sport(id=1, nom="Soccer")
        assert s1 == s2

    def test_serialisation(self):
        sport = Sport(id=2, nom="Tennis")
        data = sport.to_dict()
        assert data == {"id": 2, "nom": "Tennis"}

    def test_deserialisation(self):
        sport = Sport.from_dict({"id": 3, "nom": "Échecs"})
        assert sport.id == 3
        assert sport.nom == "Échecs"


class TestSaison:
    def test_creation_avec_nom_par_defaut(self):
        saison = Saison(annee_debut=2023, annee_fin=2024)
        assert saison.nom == "2023-2024"
        assert saison.duree() == 1

    def test_creation_avec_nom_personnalise(self):
        saison = Saison(annee_debut=2024, annee_fin=2024, nom="Olympiade 2024")
        assert saison.nom == "Olympiade 2024"

    def test_annee_fin_inferieure_leve_erreur(self):
        with pytest.raises(ValueError, match="année de fin"):
            Saison(annee_debut=2024, annee_fin=2023)

    def test_egalite_par_annees(self):
        s1 = Saison(2023, 2024)
        s2 = Saison(2023, 2024, nom="Différent")
        assert s1 == s2


class TestPays:
    def test_creation_valide(self):
        pays = Pays(nom="France", code="FRA")
        assert pays.nom == "France"
        assert pays.code == "FRA"

    def test_code_minuscule_devient_majuscule(self):
        pays = Pays(nom="France", code="fr")
        assert pays.code == "FR"

    def test_code_invalide_leve_erreur(self):
        with pytest.raises(ValueError, match="2 ou 3 caractères"):
            Pays(nom="France", code="FRAN")

    def test_nom_vide_leve_erreur(self):
        with pytest.raises(ValueError):
            Pays(nom="", code="FR")

    def test_egalite_par_code(self):
        p1 = Pays(nom="France", code="FRA")
        p2 = Pays(nom="République française", code="FRA")
        assert p1 == p2

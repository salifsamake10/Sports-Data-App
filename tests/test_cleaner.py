"""Tests du nettoyeur de données."""

from datetime import date

from src.data import DataCleaner


class TestDataCleaner:
    def test_supprimer_espaces(self):
        cleaner = DataCleaner()
        donnees = [{"nom": "  PSG  ", "ville": "Paris "}]
        resultat = cleaner.supprimer_espaces(donnees)
        assert resultat[0]["nom"] == "PSG"
        assert resultat[0]["ville"] == "Paris"

    def test_gerer_valeurs_manquantes(self):
        cleaner = DataCleaner()
        donnees = [{"nom": "PSG", "score": "NA"}, {"nom": "OM", "score": "5"}]
        resultat = cleaner.gerer_valeurs_manquantes(donnees)
        assert resultat[0]["score"] is None
        assert resultat[1]["score"] == "5"

    def test_supprimer_doublons(self):
        cleaner = DataCleaner()
        donnees = [{"nom": "PSG"}, {"nom": "OM"}, {"nom": "PSG"}]
        resultat = cleaner.supprimer_doublons(donnees)
        assert len(resultat) == 2

    def test_pipeline_complet(self):
        cleaner = DataCleaner()
        donnees = [
            {"nom": " PSG ", "score": "3"},
            {"nom": "OM", "score": "NA"},
            {"nom": " PSG ", "score": "3"},  # doublon après nettoyage
        ]
        resultat = cleaner.nettoyer(donnees)
        assert len(resultat) == 2
        assert resultat[0]["nom"] == "PSG"
        assert resultat[1]["score"] is None

    def test_convertir_int_valide(self):
        assert DataCleaner.convertir_int("12") == 12
        assert DataCleaner.convertir_int("3.5") == 3
        assert DataCleaner.convertir_int(7) == 7

    def test_convertir_int_invalide_retourne_defaut(self):
        assert DataCleaner.convertir_int("abc") is None
        assert DataCleaner.convertir_int("abc", defaut=0) == 0
        assert DataCleaner.convertir_int(None) is None

    def test_convertir_float_valide(self):
        assert DataCleaner.convertir_float("3.14") == 3.14
        assert DataCleaner.convertir_float("5") == 5.0

    def test_convertir_date_iso(self):
        assert DataCleaner.convertir_date("2024-03-15") == date(2024, 3, 15)

    def test_convertir_date_format_fr(self):
        assert DataCleaner.convertir_date("15/03/2024") == date(2024, 3, 15)

    def test_convertir_date_invalide(self):
        assert DataCleaner.convertir_date("pas une date") is None

    def test_convertir_date_deja_date(self):
        d = date(2024, 1, 1)
        assert DataCleaner.convertir_date(d) == d

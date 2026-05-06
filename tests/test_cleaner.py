"""Tests du nettoyeur de données (DataCleaner)."""

from datetime import date

from src.data import DataCleaner


class TestConvertirInt:
    def test_int_valide(self):
        assert DataCleaner.convertir_int("12") == 12

    def test_int_depuis_float(self):
        assert DataCleaner.convertir_int("3.5") == 3

    def test_int_invalide_retourne_defaut(self):
        assert DataCleaner.convertir_int("abc") is None
        assert DataCleaner.convertir_int("abc", defaut=0) == 0

    def test_int_none_retourne_defaut(self):
        assert DataCleaner.convertir_int(None) is None


class TestConvertirFloat:
    def test_float_valide(self):
        assert DataCleaner.convertir_float("3.14") == 3.14

    def test_float_depuis_int(self):
        assert DataCleaner.convertir_float("5") == 5.0

    def test_float_invalide_retourne_defaut(self):
        assert DataCleaner.convertir_float("xyz") is None


class TestConvertirDate:
    def test_iso(self):
        assert DataCleaner.convertir_date("2024-03-15") == date(2024, 3, 15)

    def test_format_fr(self):
        assert DataCleaner.convertir_date("15/03/2024") == date(2024, 3, 15)

    def test_invalide_retourne_none(self):
        assert DataCleaner.convertir_date("pas une date") is None

    def test_deja_date(self):
        d = date(2024, 1, 1)
        assert DataCleaner.convertir_date(d) == d

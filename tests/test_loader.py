"""Tests des chargeurs CSV et JSON."""

import json

import pytest

from src.data import CSVLoader, JSONLoader, get_loader


class TestCSVLoader:
    def test_charger_csv_valide(self, tmp_path):
        fichier = tmp_path / "test.csv"
        fichier.write_text("nom,age\nMessi,36\nRonaldo,39\n", encoding="utf-8")
        loader = CSVLoader()
        donnees = loader.load(fichier)
        assert len(donnees) == 2
        assert donnees[0]["nom"] == "Messi"

    def test_fichier_inexistant_leve_erreur(self):
        loader = CSVLoader()
        with pytest.raises(FileNotFoundError):
            loader.load("/inexistant.csv")

    def test_csv_avec_separateur_different(self, tmp_path):
        fichier = tmp_path / "test.csv"
        fichier.write_text("nom;age\nMessi;36\n", encoding="utf-8")
        loader = CSVLoader(delimiter=";")
        donnees = loader.load(fichier)
        assert donnees[0]["nom"] == "Messi"


class TestJSONLoader:
    def test_charger_liste_directe(self, tmp_path):
        fichier = tmp_path / "test.json"
        fichier.write_text(
            json.dumps([{"nom": "PSG"}, {"nom": "OM"}]), encoding="utf-8"
        )
        loader = JSONLoader()
        donnees = loader.load(fichier)
        assert len(donnees) == 2
        assert donnees[0]["nom"] == "PSG"


class TestGetLoader:
    def test_factory_csv(self):
        assert isinstance(get_loader("csv"), CSVLoader)

    def test_factory_json(self):
        assert isinstance(get_loader("json"), JSONLoader)

    def test_format_inconnu_leve_erreur(self):
        with pytest.raises(ValueError, match="non supporté"):
            get_loader("xml")

    def test_factory_avec_point(self):
        assert isinstance(get_loader(".csv"), CSVLoader)

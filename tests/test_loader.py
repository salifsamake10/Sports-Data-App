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
        assert donnees[1]["age"] == "39"

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

    def test_charger_dict_avec_data(self, tmp_path):
        fichier = tmp_path / "test.json"
        fichier.write_text(
            json.dumps({"data": [{"nom": "PSG"}], "meta": "info"}),
            encoding="utf-8",
        )

        loader = JSONLoader()
        donnees = loader.load(fichier)

        assert len(donnees) == 1
        assert donnees[0]["nom"] == "PSG"

    def test_format_invalide_leve_erreur(self, tmp_path):
        fichier = tmp_path / "test.json"
        fichier.write_text(json.dumps({"erreur": "format"}), encoding="utf-8")

        loader = JSONLoader()
        with pytest.raises(ValueError, match="liste"):
            loader.load(fichier)


class TestGetLoader:
    def test_factory_csv(self):
        loader = get_loader("csv")
        assert isinstance(loader, CSVLoader)

    def test_factory_json(self):
        loader = get_loader("json")
        assert isinstance(loader, JSONLoader)

    def test_format_inconnu_leve_erreur(self):
        with pytest.raises(ValueError, match="non supporté"):
            get_loader("xml")

    def test_factory_avec_point(self):
        """get_loader doit accepter '.csv' aussi."""
        loader = get_loader(".csv")
        assert isinstance(loader, CSVLoader)

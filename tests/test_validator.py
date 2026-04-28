"""Tests du validateur de données."""

import pytest

from src.data import DataValidator, ValidationError


SCHEMA = {
    "champs_obligatoires": ["nom", "score"],
    "types": {"score": "int"},
}


class TestDataValidator:
    def test_donnees_valides(self):
        validator = DataValidator(SCHEMA)
        donnees = [{"nom": "PSG", "score": "3"}, {"nom": "OM", "score": "1"}]
        assert validator.valider(donnees) is True

    def test_champ_obligatoire_manquant(self):
        validator = DataValidator(SCHEMA)
        donnees = [{"nom": "PSG"}]  # score manquant
        assert validator.valider(donnees) is False
        assert "score" in validator.erreurs[0]

    def test_champ_obligatoire_vide(self):
        validator = DataValidator(SCHEMA)
        donnees = [{"nom": "PSG", "score": ""}]
        assert validator.valider(donnees) is False

    def test_type_invalide(self):
        validator = DataValidator(SCHEMA)
        donnees = [{"nom": "PSG", "score": "abc"}]
        assert validator.valider(donnees) is False

    def test_mode_strict_leve_erreur(self):
        validator = DataValidator(SCHEMA)
        donnees = [{"nom": "PSG"}]
        with pytest.raises(ValidationError):
            validator.valider(donnees, strict=True)

    def test_rapport_sans_erreur(self):
        validator = DataValidator(SCHEMA)
        validator.valider([{"nom": "PSG", "score": "3"}])
        assert validator.get_rapport() == "Aucune erreur de validation."

    def test_rapport_avec_erreurs(self):
        validator = DataValidator(SCHEMA)
        validator.valider([{"nom": "PSG"}])
        rapport = validator.get_rapport()
        assert "Erreurs" in rapport

    def test_accumulation_erreurs_mode_non_strict(self):
        validator = DataValidator(SCHEMA)
        donnees = [{"nom": "PSG"}, {"nom": "OM"}]
        validator.valider(donnees, strict=False)
        assert len(validator.erreurs) == 2

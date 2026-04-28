"""Tests de la classe Coach."""

from datetime import date, timedelta

import pytest

from src.models import Coach


class TestCoach:
    def test_creation_valide(self, coach_deschamps):
        assert coach_deschamps.nom == "Deschamps"
        assert coach_deschamps.prenom == "Didier"
        assert coach_deschamps.experience == 12

    def test_nom_vide_leve_erreur(self, france):
        with pytest.raises(ValueError, match="nom"):
            Coach(
                nom="",
                prenom="Didier",
                date_naissance=date(1968, 10, 15),
                nationalite=france,
            )

    def test_prenom_vide_leve_erreur(self, france):
        with pytest.raises(ValueError, match="prénom"):
            Coach(
                nom="Deschamps",
                prenom="",
                date_naissance=date(1968, 10, 15),
                nationalite=france,
            )

    def test_experience_negative_leve_erreur(self, france):
        with pytest.raises(ValueError, match="expérience"):
            Coach(
                nom="Deschamps",
                prenom="Didier",
                date_naissance=date(1968, 10, 15),
                nationalite=france,
                experience=-1,
            )

    def test_date_naissance_futur_leve_erreur(self, france):
        future = date.today() + timedelta(days=1)
        with pytest.raises(ValueError, match="dans le futur"):
            Coach(
                nom="Deschamps",
                prenom="Didier",
                date_naissance=future,
                nationalite=france,
            )

    def test_get_age(self, coach_deschamps):
        age = coach_deschamps.get_age()
        annee_courante = date.today().year
        age_attendu = annee_courante - 1968
        assert age in (age_attendu, age_attendu - 1)

    def test_serialisation(self, coach_deschamps):
        data = coach_deschamps.to_dict()
        assert data["nom"] == "Deschamps"
        assert data["experience"] == 12
        assert "date_naissance" in data
        assert data["nationalite"]["code"] == "FRA"

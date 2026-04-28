"""Tests de la classe Joueur."""

from datetime import date, timedelta

import pytest

from src.models import Genre, Joueur, Resultat, Statistique


class TestJoueur:
    def test_creation_valide(self, joueur_messi):
        assert joueur_messi.nom == "Messi"
        assert joueur_messi.prenom == "Lionel"
        assert joueur_messi.genre == Genre.MASCULIN
        assert joueur_messi.stats == []

    def test_prenom_vide_leve_erreur(self, espagne):
        with pytest.raises(ValueError, match="prénom"):
            Joueur(
                id=1,
                nom="Messi",
                prenom="",
                date_naissance=date(1987, 6, 24),
                pays=espagne,
                genre=Genre.MASCULIN,
            )

    def test_date_naissance_futur_leve_erreur(self, espagne):
        future = date.today() + timedelta(days=1)
        with pytest.raises(ValueError, match="dans le futur"):
            Joueur(
                id=1,
                nom="Test",
                prenom="Future",
                date_naissance=future,
                pays=espagne,
                genre=Genre.MASCULIN,
            )

    def test_get_age(self, joueur_messi):
        age = joueur_messi.get_age()
        annee_courante = date.today().year
        age_attendu = annee_courante - 1987
        # Tolérance de 1 an selon la date de l'année
        assert age in (age_attendu, age_attendu - 1)

    def test_update_stats_creation(self, joueur_messi):
        """Si la stat n'existe pas, elle est créée."""
        resultat = Resultat(id=1, valeur=2, type="buts", participant=joueur_messi)
        joueur_messi.update_stats(resultat)

        stat = joueur_messi.get_stat("buts")
        assert stat is not None
        assert stat.valeur == 2.0

    def test_update_stats_incrementation(self, joueur_messi):
        """Si la stat existe, elle est incrémentée."""
        joueur_messi.ajouter_stat(Statistique(nom="buts", valeur=5))
        resultat = Resultat(id=1, valeur=3, type="buts", participant=joueur_messi)
        joueur_messi.update_stats(resultat)

        assert joueur_messi.get_stat("buts").valeur == 8.0

    def test_get_stat_inexistante(self, joueur_messi):
        assert joueur_messi.get_stat("inexistant") is None

    def test_ajouter_stat_remplace(self, joueur_messi):
        """Ajouter une stat avec un nom existant remplace l'ancienne."""
        joueur_messi.ajouter_stat(Statistique(nom="buts", valeur=5))
        joueur_messi.ajouter_stat(Statistique(nom="buts", valeur=15))
        assert len(joueur_messi.stats) == 1
        assert joueur_messi.get_stat("buts").valeur == 15.0

    def test_egalite_par_id_et_type(self, joueur_messi, joueur_ronaldo):
        assert joueur_messi != joueur_ronaldo

    def test_serialisation(self, joueur_messi):
        data = joueur_messi.to_dict()
        assert data["id"] == 1
        assert data["nom"] == "Messi"
        assert data["genre"] == "MASCULIN"
        assert "date_naissance" in data

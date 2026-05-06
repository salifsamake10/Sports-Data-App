"""Tests du saver (sauvegarde JSON)."""

import json

import pytest

from src.data import DataSaver


class TestDataSaver:
    def test_sauvegarder_competition(
        self, tmp_path, competition_ligue1, match_psg_om, equipe_psg, equipe_om
    ):
        from src.models import MatchStatus, Resultat

        match_psg_om.ajouter_resultat(Resultat(id=1, valeur=2, type="buts", participant=equipe_psg))
        match_psg_om.ajouter_resultat(Resultat(id=2, valeur=0, type="buts", participant=equipe_om))
        match_psg_om.statut = MatchStatus.TERMINE
        competition_ligue1.ajouter_match(match_psg_om)

        chemin = tmp_path / "competition.json"
        saver = DataSaver()
        saver.sauvegarder_competition(competition_ligue1, chemin)

        assert chemin.exists()
        with open(chemin, encoding="utf-8") as f:
            data = json.load(f)
        assert data["nom"] == "Ligue 1"
        assert len(data["matchs"]) == 1

    def test_charger_dict(self, tmp_path):
        chemin = tmp_path / "data.json"
        chemin.write_text(json.dumps({"nom": "test"}), encoding="utf-8")

        saver = DataSaver()
        data = saver.charger_dict(chemin)
        assert data["nom"] == "test"

    def test_charger_dict_inexistant_leve_erreur(self):
        saver = DataSaver()
        with pytest.raises(FileNotFoundError):
            saver.charger_dict("/inexistant.json")

    def test_creation_dossier_parent(self, tmp_path, competition_ligue1):
        chemin = tmp_path / "sous" / "dossier" / "competition.json"
        saver = DataSaver()
        saver.sauvegarder_competition(competition_ligue1, chemin)
        assert chemin.exists()

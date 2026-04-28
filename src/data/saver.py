"""Module de sauvegarde des objets métier.

Sérialise les objets en JSON pour les sauvegarder, et les recharge
ensuite si nécessaire. Utilise les méthodes to_dict() des classes models.
"""

from __future__ import annotations

import json
from pathlib import Path

from src.models import Competition


class DataSaver:
    """Sauvegarde et recharge des objets métier.

    Repose sur les méthodes to_dict() des classes du package models.
    """

    def __init__(self, encoding: str = "utf-8", indent: int = 2) -> None:
        """Initialise le saver.

        Parameters
        ----------
        encoding : str, optional
            Encodage du fichier de sortie (par défaut "utf-8").
        indent : int, optional
            Indentation JSON pour la lisibilité (par défaut 2).
        """
        self.encoding = encoding
        self.indent = indent

    def sauvegarder_competition(
        self, competition: Competition, path: str | Path
    ) -> None:
        """Sauvegarde une compétition complète au format JSON.

        Parameters
        ----------
        competition : Competition
            Competition à sauvegarder.
        path : str or Path
            Chemin de sortie.
        """
        chemin = Path(path)
        chemin.parent.mkdir(parents=True, exist_ok=True)
        with open(chemin, "w", encoding=self.encoding) as f:
            json.dump(
                competition.to_dict(),
                f,
                indent=self.indent,
                ensure_ascii=False,
            )

    def charger_dict(self, path: str | Path) -> dict:
        """Charge un dict depuis un fichier JSON.

        Note: la reconstruction complète des objets nécessite de
        passer par les méthodes from_dict() des classes concernées.

        Parameters
        ----------
        path : str or Path
            Chemin du fichier JSON.

        Returns
        -------
        dict
            Données désérialisées.

        Raises
        ------
        FileNotFoundError
            Si le fichier n'existe pas.
        """
        chemin = Path(path)
        if not chemin.exists():
            raise FileNotFoundError(f"Fichier introuvable : {chemin}")
        with open(chemin, encoding=self.encoding) as f:
            return json.load(f)

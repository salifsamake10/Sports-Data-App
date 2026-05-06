"""Module de sauvegarde des objets métier."""

from __future__ import annotations

import json
from pathlib import Path

from src.models import Competition


class DataSaver:
    """Sauvegarde et recharge des objets métier."""

    def __init__(self, encoding: str = "utf-8", indent: int = 2) -> None:
        self.encoding = encoding
        self.indent = indent

    def sauvegarder_competition(self, competition: Competition, path: str | Path) -> None:
        """Sauvegarde une compétition au format JSON."""
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
        """Charge un dict depuis un fichier JSON."""
        chemin = Path(path)
        if not chemin.exists():
            raise FileNotFoundError(f"Fichier introuvable : {chemin}")
        with open(chemin, encoding=self.encoding) as f:
            return json.load(f)

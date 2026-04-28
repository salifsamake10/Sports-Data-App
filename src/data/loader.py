"""Module de chargement des données brutes (CSV, JSON).

Ce module est volontairement générique : il ne connaît pas le sport,
il se contente de lire un fichier et retourner une liste de dictionnaires.
La transformation en objets métier est faite par mapper.py.
"""

from __future__ import annotations

import csv
import json
from abc import ABC, abstractmethod
from pathlib import Path


class DataLoader(ABC):
    """Classe abstraite pour le chargement de données.

    Toute source de données (CSV, JSON, API…) doit hériter de cette classe
    et implémenter la méthode load().
    """

    @abstractmethod
    def load(self, path: str | Path) -> list[dict]:
        """Charge un fichier et retourne son contenu sous forme de liste de dicts.

        Parameters
        ----------
        path : str or Path
            Chemin vers le fichier à charger.

        Returns
        -------
        list[dict]
            Liste de dictionnaires, un par ligne/enregistrement.

        Raises
        ------
        FileNotFoundError
            Si le fichier n'existe pas.
        """
        ...


class CSVLoader(DataLoader):
    """Chargeur pour les fichiers CSV.

    Utilise csv.DictReader pour transformer chaque ligne en dict
    où les clés sont les noms de colonnes.
    """

    def __init__(self, delimiter: str = ",", encoding: str = "utf-8") -> None:
        """Initialise le chargeur CSV.

        Parameters
        ----------
        delimiter : str, optional
            Séparateur de colonnes (par défaut ",").
        encoding : str, optional
            Encodage du fichier (par défaut "utf-8").
        """
        self.delimiter = delimiter
        self.encoding = encoding

    def load(self, path: str | Path) -> list[dict]:
        """Charge un CSV et retourne une liste de dicts.

        Parameters
        ----------
        path : str or Path
            Chemin vers le fichier CSV.

        Returns
        -------
        list[dict]
            Une entrée par ligne du CSV.

        Raises
        ------
        FileNotFoundError
            Si le fichier n'existe pas.
        """
        chemin = Path(path)
        if not chemin.exists():
            raise FileNotFoundError(f"Fichier introuvable : {chemin}")

        with open(chemin, encoding=self.encoding, newline="") as f:
            reader = csv.DictReader(f, delimiter=self.delimiter)
            return list(reader)


class JSONLoader(DataLoader):
    """Chargeur pour les fichiers JSON.

    Le fichier JSON doit contenir soit une liste de dicts directement,
    soit un dict avec une clé "data" contenant la liste.
    """

    def __init__(self, encoding: str = "utf-8") -> None:
        """Initialise le chargeur JSON.

        Parameters
        ----------
        encoding : str, optional
            Encodage du fichier (par défaut "utf-8").
        """
        self.encoding = encoding

    def load(self, path: str | Path) -> list[dict]:
        """Charge un JSON et retourne une liste de dicts.

        Parameters
        ----------
        path : str or Path
            Chemin vers le fichier JSON.

        Returns
        -------
        list[dict]
            Liste de dictionnaires.

        Raises
        ------
        FileNotFoundError
            Si le fichier n'existe pas.
        ValueError
            Si le contenu n'est ni une liste ni un dict avec clé "data".
        """
        chemin = Path(path)
        if not chemin.exists():
            raise FileNotFoundError(f"Fichier introuvable : {chemin}")

        with open(chemin, encoding=self.encoding) as f:
            contenu = json.load(f)

        if isinstance(contenu, list):
            return contenu
        if isinstance(contenu, dict) and "data" in contenu:
            return contenu["data"]
        raise ValueError(
            "Le JSON doit être une liste ou un dict avec une clé 'data'."
        )


def get_loader(format_fichier: str) -> DataLoader:
    """Factory : retourne le DataLoader adapté au format.

    Parameters
    ----------
    format_fichier : str
        Format du fichier ("csv" ou "json").

    Returns
    -------
    DataLoader
        Instance du chargeur approprié.

    Raises
    ------
    ValueError
        Si le format n'est pas supporté.
    """
    format_fichier = format_fichier.lower().strip().lstrip(".")
    loaders = {
        "csv": CSVLoader,
        "json": JSONLoader,
    }
    if format_fichier not in loaders:
        raise ValueError(
            f"Format '{format_fichier}' non supporté. "
            f"Formats disponibles : {list(loaders.keys())}"
        )
    return loaders[format_fichier]()

"""Module de chargement des données brutes (CSV, JSON) avec pandas.

Ce module est volontairement générique : il ne connaît pas le sport,
il se contente de lire un fichier et retourner une liste de dictionnaires.
La transformation en objets métier est faite par mapper.py.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

import pandas as pd


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
    """Chargeur pour les fichiers CSV utilisant pandas.

    Utilise pd.read_csv pour lire le fichier puis convertit en liste de dicts.
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
        """Charge un CSV avec pandas et retourne une liste de dicts.

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

        df = pd.read_csv(chemin, sep=self.delimiter, encoding=self.encoding)
        # Conversion en liste de dicts pour rester compatible avec le mapper
        return df.to_dict(orient="records")


class JSONLoader(DataLoader):
    """Chargeur pour les fichiers JSON utilisant pandas.

    Utilise pd.read_json pour la lecture.
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
        """
        chemin = Path(path)
        if not chemin.exists():
            raise FileNotFoundError(f"Fichier introuvable : {chemin}")

        df = pd.read_json(chemin, encoding=self.encoding)
        return df.to_dict(orient="records")


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

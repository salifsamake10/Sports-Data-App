"""Module de nettoyage des données brutes avec pandas.

Effectue un pré-traitement avant la transformation en objets :
- suppression des doublons
- gestion des valeurs manquantes
- normalisation des types (str → int, str → date…)
"""

from __future__ import annotations

from datetime import date

import pandas as pd


class DataCleaner:
    """Nettoyeur générique de données utilisant pandas.

    Reçoit une liste de dicts (sortie du loader), la convertit en DataFrame
    pandas pour le nettoyage, puis la reconvertit en liste de dicts pour
    le mapper.
    """

    def __init__(self, valeurs_manquantes: list[str] | None = None) -> None:
        """Initialise le nettoyeur.

        Parameters
        ----------
        valeurs_manquantes : list[str], optional
            Liste des chaînes considérées comme valeurs manquantes.
            Par défaut : ["", "NA", "N/A", "null", "None", "-", "?"].
        """
        self.valeurs_manquantes = valeurs_manquantes or [
            "",
            "NA",
            "N/A",
            "null",
            "None",
            "-",
            "?",
        ]

    def nettoyer(self, donnees: list[dict]) -> list[dict]:
        """Pipeline complet de nettoyage avec pandas.

        Convertit les données en DataFrame, applique les nettoyages,
        puis reconvertit en liste de dicts.

        Parameters
        ----------
        donnees : list[dict]
            Données brutes issues du loader.

        Returns
        -------
        list[dict]
            Données nettoyées.
        """
        if not donnees:
            return []

        df = pd.DataFrame(donnees)

        # 1. Nettoyage des espaces dans les colonnes texte
        df = self._nettoyer_espaces_df(df)

        # 2. Remplacer les valeurs manquantes connues par NaN
        df = df.replace(self.valeurs_manquantes, pd.NA)

        # 3. Supprimer les doublons
        df = df.drop_duplicates()

        # 4. Conversion en liste de dicts
        # On remplace les NaN par None pour la suite du pipeline
        df = df.where(df.notna(), None)
        return df.to_dict(orient="records")

    def _nettoyer_espaces_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """Supprime les espaces en début/fin des colonnes texte."""
        # Sélectionne uniquement les colonnes de type object (str)
        colonnes_str = df.select_dtypes(include="object").columns
        for col in colonnes_str:
            df[col] = df[col].astype(str).str.strip()
        return df

    @staticmethod
    def convertir_int(valeur, defaut: int | None = None) -> int | None:
        """Convertit une valeur en int, avec gestion d'erreur.

        Utilise pd.to_numeric pour bénéficier de la gestion robuste de pandas.

        Parameters
        ----------
        valeur : any
            Valeur à convertir.
        defaut : int, optional
            Valeur par défaut si la conversion échoue.

        Returns
        -------
        int or None
            Valeur convertie ou défaut.
        """
        if valeur is None or pd.isna(valeur):
            return defaut
        try:
            resultat = pd.to_numeric(valeur, errors="coerce")
            if pd.isna(resultat):
                return defaut
            return int(resultat)
        except (ValueError, TypeError):
            return defaut

    @staticmethod
    def convertir_float(valeur, defaut: float | None = None) -> float | None:
        """Convertit une valeur en float avec pandas."""
        if valeur is None or pd.isna(valeur):
            return defaut
        try:
            resultat = pd.to_numeric(valeur, errors="coerce")
            if pd.isna(resultat):
                return defaut
            return float(resultat)
        except (ValueError, TypeError):
            return defaut

    @staticmethod
    def convertir_date(
        valeur, formats: list[str] | None = None, defaut: date | None = None
    ) -> date | None:
        """Convertit une chaîne en date avec pandas.

        Utilise pd.to_datetime qui gère automatiquement de nombreux formats.

        Parameters
        ----------
        valeur : str
            Chaîne représentant une date.
        formats : list[str], optional
            Formats à essayer. Si None, pandas devine.
        defaut : date, optional
            Valeur par défaut si la conversion échoue.

        Returns
        -------
        date or None
            Date convertie ou défaut.
        """
        if valeur is None or pd.isna(valeur) or valeur == "":
            return defaut
        if isinstance(valeur, date):
            return valeur

        # Essai sans format imposé (pandas est très tolérant)
        try:
            resultat = pd.to_datetime(valeur, errors="coerce")
            if pd.isna(resultat):
                # Essai avec les formats explicites si fournis
                if formats:
                    for fmt in formats:
                        resultat = pd.to_datetime(valeur, format=fmt, errors="coerce")
                        if not pd.isna(resultat):
                            return resultat.date()
                return defaut
            return resultat.date()
        except Exception:
            return defaut

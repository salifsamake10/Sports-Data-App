"""Module de nettoyage des données brutes.

Effectue un pré-traitement avant la transformation en objets :
- suppression des doublons
- nettoyage des espaces parasites
- gestion des valeurs manquantes
- normalisation des types (str → int, str → date…)
"""

from __future__ import annotations

from datetime import date, datetime


class DataCleaner:
    """Nettoyeur générique de données.

    Fournit des méthodes de nettoyage indépendantes du sport.
    """

    def __init__(self, valeurs_manquantes: list[str] | None = None) -> None:
        """Initialise le nettoyeur.

        Parameters
        ----------
        valeurs_manquantes : list[str], optional
            Liste des chaînes considérées comme valeurs manquantes.
            Par défaut : ["", "NA", "N/A", "null", "None", "-"].
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
        """Pipeline complet de nettoyage.

        Applique les étapes : trim, valeurs manquantes, doublons.

        Parameters
        ----------
        donnees : list[dict]
            Données brutes issues du loader.

        Returns
        -------
        list[dict]
            Données nettoyées.
        """
        donnees = self.supprimer_espaces(donnees)
        donnees = self.gerer_valeurs_manquantes(donnees)
        donnees = self.supprimer_doublons(donnees)
        return donnees

    def supprimer_espaces(self, donnees: list[dict]) -> list[dict]:
        """Supprime les espaces en début/fin des valeurs textuelles.

        Parameters
        ----------
        donnees : list[dict]
            Données à nettoyer.

        Returns
        -------
        list[dict]
            Données avec espaces nettoyés.
        """
        return [
            {k: (v.strip() if isinstance(v, str) else v) for k, v in ligne.items()}
            for ligne in donnees
        ]

    def gerer_valeurs_manquantes(
        self, donnees: list[dict], remplacement=None
    ) -> list[dict]:
        """Remplace les valeurs manquantes par une valeur par défaut.

        Parameters
        ----------
        donnees : list[dict]
            Données à traiter.
        remplacement : optional
            Valeur de remplacement (par défaut None).

        Returns
        -------
        list[dict]
            Données avec valeurs manquantes traitées.
        """
        resultat = []
        for ligne in donnees:
            ligne_propre = {}
            for cle, valeur in ligne.items():
                if isinstance(valeur, str) and valeur in self.valeurs_manquantes:
                    ligne_propre[cle] = remplacement
                else:
                    ligne_propre[cle] = valeur
            resultat.append(ligne_propre)
        return resultat

    def supprimer_doublons(self, donnees: list[dict]) -> list[dict]:
        """Supprime les lignes strictement identiques.

        Parameters
        ----------
        donnees : list[dict]
            Données à dédupliquer.

        Returns
        -------
        list[dict]
            Données sans doublons (ordre préservé).
        """
        vu = set()
        resultat = []
        for ligne in donnees:
            cle = tuple(sorted(ligne.items()))
            if cle not in vu:
                vu.add(cle)
                resultat.append(ligne)
        return resultat

    @staticmethod
    def convertir_int(valeur, defaut: int | None = None) -> int | None:
        """Convertit une valeur en int, avec gestion d'erreur.

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
        if valeur is None:
            return defaut
        try:
            return int(float(valeur))
        except (ValueError, TypeError):
            return defaut

    @staticmethod
    def convertir_float(valeur, defaut: float | None = None) -> float | None:
        """Convertit une valeur en float."""
        if valeur is None:
            return defaut
        try:
            return float(valeur)
        except (ValueError, TypeError):
            return defaut

    @staticmethod
    def convertir_date(
        valeur, formats: list[str] | None = None, defaut: date | None = None
    ) -> date | None:
        """Convertit une chaîne en date.

        Parameters
        ----------
        valeur : str
            Chaîne représentant une date.
        formats : list[str], optional
            Formats à essayer (par défaut: ISO, FR, US).
        defaut : date, optional
            Valeur par défaut si la conversion échoue.

        Returns
        -------
        date or None
            Date convertie ou défaut.
        """
        if not valeur:
            return defaut
        if isinstance(valeur, date):
            return valeur
        formats = formats or ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y"]
        for fmt in formats:
            try:
                return datetime.strptime(str(valeur), fmt).date()
            except ValueError:
                continue
        return defaut

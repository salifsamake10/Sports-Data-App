"""Module de validation des données.

Vérifie que les données respectent un schéma attendu :
- présence des champs obligatoires
- validité des types
- cohérence des valeurs
"""

from __future__ import annotations


class ValidationError(Exception):
    """Erreur levée lorsqu'une donnée ne respecte pas le schéma."""


class DataValidator:
    """Valide une liste de dicts contre un schéma.

    Le schéma est un dict de la forme :
        {
            "champs_obligatoires": ["nom_equipe_dom", "nom_equipe_ext", ...],
            "types": {"score_dom": "int", "date": "str", ...}
        }

    Attributs
    ----------
    schema : dict
        Schéma de validation.
    erreurs : list[str]
        Liste des erreurs détectées lors du dernier appel à valider().
    """

    TYPES_VALIDES = {
        "str": str,
        "int": int,
        "float": (int, float),
        "bool": bool,
    }

    def __init__(self, schema: dict) -> None:
        """Initialise le validateur.

        Parameters
        ----------
        schema : dict
            Schéma de validation.
        """
        self.schema = schema
        self.erreurs: list[str] = []

    def valider(self, donnees: list[dict], strict: bool = False) -> bool:
        """Valide une liste de dicts contre le schéma.

        Parameters
        ----------
        donnees : list[dict]
            Données à valider.
        strict : bool, optional
            Si True, lève ValidationError au premier problème.
            Sinon, accumule les erreurs dans self.erreurs.

        Returns
        -------
        bool
            True si toutes les lignes sont valides.

        Raises
        ------
        ValidationError
            Si strict=True et qu'une erreur est trouvée.
        """
        self.erreurs = []
        for index, ligne in enumerate(donnees):
            erreurs_ligne = self._valider_ligne(ligne, index)
            if erreurs_ligne and strict:
                raise ValidationError(erreurs_ligne[0])
            self.erreurs.extend(erreurs_ligne)
        return len(self.erreurs) == 0

    def _valider_ligne(self, ligne: dict, index: int) -> list[str]:
        """Valide une seule ligne et retourne la liste de ses erreurs."""
        erreurs = []
        # Champs obligatoires
        for champ in self.schema.get("champs_obligatoires", []):
            if champ not in ligne or ligne[champ] in (None, ""):
                erreurs.append(f"Ligne {index}: champ obligatoire '{champ}' manquant ou vide.")
        # Vérification des types
        for champ, type_attendu in self.schema.get("types", {}).items():
          if (
                champ in ligne
                and ligne[champ] is not None
                and not self._verifier_type(ligne[champ], type_attendu)
            ):
              erreurs.append(
                        f"Ligne {index}: champ '{champ}' devrait être de type "
                        f"'{type_attendu}', a la valeur '{ligne[champ]}'."
                    )
        return erreurs

    def _verifier_type(self, valeur, type_attendu: str) -> bool:
        """Vérifie si une valeur est compatible avec un type attendu."""
        if type_attendu not in self.TYPES_VALIDES:
            return True  # Type inconnu = pas de validation
        type_python = self.TYPES_VALIDES[type_attendu]
        # Pour les nombres en string, on tente une conversion
        if type_attendu in ("int", "float") and isinstance(valeur, str):
            try:
                float(valeur)
                return True
            except ValueError:
                return False
        return isinstance(valeur, type_python)

    def get_rapport(self) -> str:
        """Retourne un rapport formaté des erreurs."""
        if not self.erreurs:
            return "Aucune erreur de validation."
        return "Erreurs détectées:\n" + "\n".join(f"  - {e}" for e in self.erreurs)

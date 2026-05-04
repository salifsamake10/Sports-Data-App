"""Module définissant la classe Saison."""

from __future__ import annotations


class Saison:
    """Représente une saison sportive.

    Une saison est une période durant laquelle se déroule une compétition.
    Elle est caractérisée par une année de début et une année de fin.

    Attributs
    ----------
    annee_debut : int
        Année de début de la saison.
    annee_fin : int
        Année de fin de la saison.
    nom : str
        Nom lisible de la saison (ex: "2023-2024").
    """

    def __init__(self, annee_debut: int, annee_fin: int, nom: str | None = None) -> None:
        """Initialise une saison.

        Parameters
        ----------
        annee_debut : int
            Année de début (ex: 2023).
        annee_fin : int
            Année de fin (ex: 2024).
        nom : str, optional
            Nom personnalisé. Par défaut "annee_debut-annee_fin".

        Raises
        ------
        ValueError
            Si annee_fin < annee_debut.
        """
        if annee_fin < annee_debut:
            raise ValueError(
                f"L'année de fin ({annee_fin}) doit être >= année de début ({annee_debut})."
            )
        self.annee_debut = annee_debut
        self.annee_fin = annee_fin
        self.nom = nom if nom else f"{annee_debut}-{annee_fin}"

    def __repr__(self) -> str:
        return f"Saison({self.nom})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Saison):
            return NotImplemented
        return self.annee_debut == other.annee_debut and self.annee_fin == other.annee_fin

    def __hash__(self) -> int:
        return hash((self.annee_debut, self.annee_fin))

    def duree(self) -> int:
        """Retourne la durée de la saison en années."""
        return self.annee_fin - self.annee_debut

    def to_dict(self) -> dict:
        """Sérialise la saison en dictionnaire."""
        return {
            "annee_debut": self.annee_debut,
            "annee_fin": self.annee_fin,
            "nom": self.nom,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Saison:
        """Crée une Saison à partir d'un dictionnaire."""
        return cls(
            annee_debut=data["annee_debut"],
            annee_fin=data["annee_fin"],
            nom=data.get("nom"),
        )

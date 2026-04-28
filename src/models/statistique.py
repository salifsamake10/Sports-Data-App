"""Module définissant la classe Statistique."""

from __future__ import annotations


class Statistique:
    """Représente une statistique générique d'un participant.

    Permet de stocker n'importe quelle métrique sportive sous forme
    nom/valeur/unité, ce qui rend la classe utilisable pour tous les sports.

    Attributes
    ----------
    nom : str
        Nom de la statistique (ex: "buts", "elo", "sets_gagnes").
    valeur : float
        Valeur numérique de la statistique.
    unite : str
        Unité de mesure (ex: "buts", "points", "matchs").

    Examples
    --------
    >>> Statistique("buts", 12, "buts")
    Statistique(nom='buts', valeur=12.0, unite='buts')
    >>> Statistique("elo", 1850, "points")
    Statistique(nom='elo', valeur=1850.0, unite='points')
    """

    def __init__(self, nom: str, valeur: float, unite: str = "") -> None:
        """Initialise une statistique.

        Parameters
        ----------
        nom : str
            Nom de la statistique.
        valeur : float
            Valeur numérique.
        unite : str, optional
            Unité de mesure (par défaut chaîne vide).

        Raises
        ------
        ValueError
            Si le nom est vide.
        """
        if not nom or not nom.strip():
            raise ValueError("Le nom de la statistique ne peut pas être vide.")
        self.nom = nom.strip()
        self.valeur = float(valeur)
        self.unite = unite.strip()

    def __repr__(self) -> str:
        return f"Statistique(nom='{self.nom}', valeur={self.valeur}, unite='{self.unite}')"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Statistique):
            return NotImplemented
        return self.nom == other.nom and self.valeur == other.valeur

    def mettre_a_jour(self, nouvelle_valeur: float) -> None:
        """Remplace la valeur courante par une nouvelle valeur.

        Parameters
        ----------
        nouvelle_valeur : float
            Nouvelle valeur de la statistique.
        """
        self.valeur = float(nouvelle_valeur)

    def incrementer(self, delta: float = 1.0) -> None:
        """Ajoute delta à la valeur courante.

        Parameters
        ----------
        delta : float
            Valeur à ajouter (par défaut 1).
        """
        self.valeur += float(delta)

    def to_dict(self) -> dict:
        """Sérialise la statistique en dictionnaire."""
        return {"nom": self.nom, "valeur": self.valeur, "unite": self.unite}

    @classmethod
    def from_dict(cls, data: dict) -> Statistique:
        """Crée une Statistique à partir d'un dictionnaire."""
        return cls(
            nom=data["nom"],
            valeur=data["valeur"],
            unite=data.get("unite", ""),
        )

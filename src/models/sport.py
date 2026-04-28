"""Module définissant la classe Sport."""

class Sport:
    """Représente un sport.

    Un sport est une discipline (football, tennis, échecs, etc.).
    Cette classe sert d'entité de référence pour catégoriser les compétitions.

    Attributes
    ----------
    id : int
        Identifiant unique du sport.
    nom : str
        Nom du sport (ex: "Football", "Tennis").
    """

    def __init__(self, id: int, nom: str) -> None:
        """Initialise un sport.

        Parameters
        ----------
        id : int
            Identifiant unique.
        nom : str
            Nom du sport.

        Raises
        ------
        ValueError
            Si le nom est vide.
        """
        if not nom or not nom.strip():
            raise ValueError("Le nom du sport ne peut pas être vide.")
        self.id = id
        self.nom = nom.strip()

    def __repr__(self) -> str:
        return f"Sport(id={self.id}, nom='{self.nom}')"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Sport):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def to_dict(self) -> dict:
        """Sérialise le sport en dictionnaire."""
        return {"id": self.id, "nom": self.nom}

    @classmethod
    def from_dict(cls, data: dict) -> Sport:  # noqa: F821
        """Crée un Sport à partir d'un dictionnaire."""
        return cls(id=data["id"], nom=data["nom"])

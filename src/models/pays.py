"""Module définissant la classe Pays."""

from __future__ import annotations


class Pays:
    """Représente un pays.

    Utilisé pour la nationalité des joueurs, équipes, coachs, etc.

    Attributs
    ----------
    nom : str
        Nom du pays (ex: "France").
    code : str
        Code ISO du pays sur 2 ou 3 lettres (ex: "FR", "FRA").
    """

    def __init__(self, nom: str, code: str) -> None:
        """Initialise un pays.

        Parameters
        ----------
        nom : str
            Nom du pays.
        code : str
            Code ISO (2 ou 3 caractères).

        Raises
        ------
        ValueError
            Si le nom est vide ou si le code n'a pas 2 ou 3 caractères.
        """
        if not nom or not nom.strip():
            raise ValueError("Le nom du pays ne peut pas être vide.")
        if not code or len(code.strip()) not in (2, 3):
            raise ValueError("Le code pays doit faire 2 ou 3 caractères.")
        self.nom = nom.strip()
        self.code = code.strip().upper()

    def __repr__(self) -> str:
        return f"Pays(nom='{self.nom}', code='{self.code}')"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Pays):
            return NotImplemented
        return self.code == other.code

    def __hash__(self) -> int:
        return hash(self.code)

    def to_dict(self) -> dict:
        """Sérialise le pays en dictionnaire."""
        return {"nom": self.nom, "code": self.code}

    @classmethod
    def from_dict(cls, data: dict) -> Pays:
        """Crée un Pays à partir d'un dictionnaire."""
        return cls(nom=data["nom"], code=data["code"])
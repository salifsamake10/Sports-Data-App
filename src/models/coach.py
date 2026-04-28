"""Module définissant la classe Coach."""

from datetime import date
from .pays import Pays


class Coach:
    """Représente un entraîneur d'équipe.

    Attributes
    ----------
    nom : str
        Nom de famille du coach.
    prenom : str
        Prénom.
    date_naissance : date
        Date de naissance.
    nationalite : Pays
        Nationalité.
    experience : int
        Nombre d'années d'expérience.
    """

    def __init__(
        self,
        nom: str,
        prenom: str,
        date_naissance: date,
        nationalite: Pays,
        experience: int = 0,
    ) -> None:
        """Initialise un coach.

        Parameters
        ----------
        nom : str
            Nom de famille.
        prenom : str
            Prénom.
        date_naissance : date
            Date de naissance.
        nationalite : Pays
            Pays de nationalité.
        experience : int, optional
            Années d'expérience (par défaut 0).

        Raises
        ------
        ValueError
            Si nom/prénom vides, date dans le futur, ou expérience négative.
        """
        if not nom or not nom.strip():
            raise ValueError("Le nom du coach ne peut pas être vide.")
        if not prenom or not prenom.strip():
            raise ValueError("Le prénom du coach ne peut pas être vide.")
        if date_naissance > date.today():
            raise ValueError("La date de naissance ne peut pas être dans le futur.")
        if experience < 0:
            raise ValueError("L'expérience ne peut pas être négative.")
        self.nom = nom.strip()
        self.prenom = prenom.strip()
        self.date_naissance = date_naissance
        self.nationalite = nationalite
        self.experience = experience

    def __repr__(self) -> str:
        return f"Coach(nom='{self.prenom} {self.nom}', experience={self.experience} ans)"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Coach):
            return NotImplemented
        return (
            self.nom == other.nom
            and self.prenom == other.prenom
            and self.date_naissance == other.date_naissance
        )

    def __hash__(self) -> int:
        return hash((self.nom, self.prenom, self.date_naissance))

    def get_age(self) -> int:
        """Calcule l'âge du coach en années."""
        aujourd_hui = date.today()
        age = aujourd_hui.year - self.date_naissance.year
        if (aujourd_hui.month, aujourd_hui.day) < (
            self.date_naissance.month,
            self.date_naissance.day,
        ):
            age -= 1
        return age

    def to_dict(self) -> dict:
        """Sérialise le coach en dictionnaire."""
        return {
            "nom": self.nom,
            "prenom": self.prenom,
            "date_naissance": self.date_naissance.isoformat(),
            "nationalite": self.nationalite.to_dict(),
            "experience": self.experience,
        }
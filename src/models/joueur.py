"""Module définissant la classe Joueur."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from .enums import Genre
from .participant import Participant
from .statistique import Statistique

if TYPE_CHECKING:
    from .pays import Pays
    from .resultat import Resultat


class Joueur(Participant):
    """Représente un joueur individuel.

    Hérite de Participant et ajoute les attributs propres à un joueur :
    prénom, date de naissance, pays, genre.

    Attributes
    ----------
    id : int
        Identifiant unique.
    nom : str
        Nom de famille.
    prenom : str
        Prénom.
    date_naissance : date
        Date de naissance.
    pays : Pays
        Pays / nationalité.
    genre : Genre
        Genre du joueur.
    stats : list[Statistique]
        Statistiques accumulées.
    """

    def __init__(
        self,
        id: int,
        nom: str,
        prenom: str,
        date_naissance: date,
        pays: Pays,
        genre: Genre,
    ) -> None:
        """Initialise un joueur.

        Parameters
        ----------
        id : int
            Identifiant unique.
        nom : str
            Nom de famille.
        prenom : str
            Prénom.
        date_naissance : date
            Date de naissance.
        pays : Pays
            Pays/nationalité.
        genre : Genre
            Genre du joueur.

        Raises
        ------
        ValueError
            Si le prénom est vide ou si la date de naissance est dans le futur.
        """
        super().__init__(id=id, nom=nom)
        if not prenom or not prenom.strip():
            raise ValueError("Le prénom ne peut pas être vide.")
        if date_naissance > date.today():
            raise ValueError("La date de naissance ne peut pas être dans le futur.")
        self.prenom = prenom.strip()
        self.date_naissance = date_naissance
        self.pays = pays
        self.genre = genre

    def __repr__(self) -> str:
        return (
            f"Joueur(id={self.id}, nom='{self.prenom} {self.nom}', "
            f"genre={self.genre.value})"
        )

    def get_age(self) -> int:
        """Calcule et retourne l'âge du joueur en années.

        Returns
        -------
        int
            Âge en années révolues.
        """
        aujourd_hui = date.today()
        age = aujourd_hui.year - self.date_naissance.year
        # Ajuste si l'anniversaire n'est pas encore passé cette année
        if (aujourd_hui.month, aujourd_hui.day) < (
            self.date_naissance.month,
            self.date_naissance.day,
        ):
            age -= 1
        return age

    def update_stats(self, resultat: Resultat) -> None:
        """Met à jour les statistiques du joueur à partir d'un résultat.

        Cherche une stat existante portant le même nom que le type du
        résultat. Si elle existe, on l'incrémente ; sinon on la crée.

        Parameters
        ----------
        resultat : Resultat
            Résultat à intégrer.
        """
        stat = self.get_stat(resultat.type)
        if stat is None:
            stat = Statistique(nom=resultat.type, valeur=resultat.valeur)
            self.ajouter_stat(stat)
        else:
            stat.incrementer(resultat.valeur)

    def to_dict(self) -> dict:
        """Sérialise le joueur en dictionnaire."""
        return {
            "id": self.id,
            "nom": self.nom,
            "prenom": self.prenom,
            "date_naissance": self.date_naissance.isoformat(),
            "pays": self.pays.to_dict(),
            "genre": self.genre.value,
            "stats": [s.to_dict() for s in self.stats],
        }
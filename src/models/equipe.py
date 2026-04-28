"""Module définissant la classe Equipe."""


from datetime import date


from .enums import Genre
from .participant import Participant
from .statistique import Statistique

from .joueur import Joueur
from .pays import Pays
from .resultat import Resultat


class Equipe(Participant):
    """Représente une équipe sportive (sport collectif).

    Hérite de Participant et regroupe une liste de joueurs.

    Attributes
    ----------
    id : int
        Identifiant unique.
    nom : str
        Nom de l'équipe.
    joueurs : list[Joueur]
        Liste des joueurs de l'équipe.
    pays : Pays
        Pays/ville représenté(e) par l'équipe.
    genre : Genre
        Genre de l'équipe (MASCULIN, FEMININ, MIXTE).
    date_creation : date or None
        Date de fondation de l'équipe (optionnel).
    """

    def __init__(
        self,
        id: int,
        nom: str,
        pays: Pays,
        genre: Genre,
        joueurs: list[Joueur] | None = None,
        date_creation: date | None = None,
    ) -> None:
        """Initialise une équipe.

        Parameters
        ----------
        id : int
            Identifiant unique.
        nom : str
            Nom de l'équipe.
        pays : Pays
            Pays représenté.
        genre : Genre
            Genre de l'équipe.
        joueurs : list[Joueur], optional
            Liste initiale de joueurs.
        date_creation : date, optional
            Date de fondation.
        """
        super().__init__(id=id, nom=nom)
        self.pays = pays
        self.genre = genre
        self.joueurs: list[Joueur] = list(joueurs) if joueurs else []
        self.date_creation = date_creation

    def __repr__(self) -> str:
        return (
            f"Equipe(id={self.id}, nom='{self.nom}', "
            f"genre={self.genre.value}, joueurs={len(self.joueurs)})"
        )

    def ajouter_joueur(self, joueur: Joueur) -> None:
        """Ajoute un joueur à l'équipe.

        Parameters
        ----------
        joueur : Joueur
            Joueur à ajouter.

        Raises
        ------
        ValueError
            Si le joueur est déjà dans l'équipe.
        """
        if joueur in self.joueurs:
            raise ValueError(f"Le joueur {joueur.nom} fait déjà partie de l'équipe.")
        self.joueurs.append(joueur)

    def retirer_joueur(self, joueur: Joueur) -> None:
        """Retire un joueur de l'équipe.

        Parameters
        ----------
        joueur : Joueur
            Joueur à retirer.

        Raises
        ------
        ValueError
            Si le joueur n'est pas dans l'équipe.
        """
        if joueur not in self.joueurs:
            raise ValueError(f"Le joueur {joueur.nom} ne fait pas partie de l'équipe.")
        self.joueurs.remove(joueur)

    def update_stats(self, resultat: Resultat) -> None:
        """Met à jour les statistiques de l'équipe.

        Cherche la stat correspondant au type du résultat. Si elle
        n'existe pas, elle est créée ; sinon on l'incrémente.

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
        """Sérialise l'équipe en dictionnaire."""
        return {
            "id": self.id,
            "nom": self.nom,
            "pays": self.pays.to_dict(),
            "genre": self.genre.value,
            "joueurs": [j.to_dict() for j in self.joueurs],
            "date_creation": (
                self.date_creation.isoformat() if self.date_creation else None
            ),
            "stats": [s.to_dict() for s in self.stats],
        }
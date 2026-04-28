"""Module définissant la classe abstraite Participant."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from .statistique import Statistique

if TYPE_CHECKING:
    from .match import Match
    from .resultat import Resultat


class Participant(ABC):
    """Classe abstraite représentant un participant à des matchs.

    Sert de base aux classes Joueur (sports individuels) et Equipe
    (sports collectifs). Permet à Match de manipuler ses participants
    de manière uniforme, quel que soit le sport.

    Attributes
    ----------
    id : int
        Identifiant unique du participant.
    nom : str
        Nom du participant.
    stats : list[Statistique]
        Liste des statistiques accumulées.
    """

    def __init__(self, id: int, nom: str) -> None:
        """Initialise un participant.

        Parameters
        ----------
        id : int
            Identifiant unique.
        nom : str
            Nom du participant.

        Raises
        ------
        ValueError
            Si le nom est vide.
        """
        if not nom or not nom.strip():
            raise ValueError("Le nom du participant ne peut pas être vide.")
        self.id = id
        self.nom = nom.strip()
        self.stats: list[Statistique] = []

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id}, nom='{self.nom}')"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Participant):
            return NotImplemented
        return self.id == other.id and type(self) is type(other)

    def __hash__(self) -> int:
        return hash((type(self).__name__, self.id))

    @abstractmethod
    def update_stats(self, resultat: Resultat) -> None:
        """Met à jour les statistiques à partir d'un nouveau résultat.

        Méthode abstraite — chaque sous-classe doit l'implémenter
        selon la nature du sport.

        Parameters
        ----------
        resultat : Resultat
            Le résultat à intégrer aux statistiques.
        """
        ...

    def get_stat(self, nom: str) -> Statistique | None:
        """Retourne la statistique correspondant au nom donné.

        Parameters
        ----------
        nom : str
            Nom de la statistique recherchée.

        Returns
        -------
        Statistique or None
            La statistique trouvée, ou None si aucune correspondance.
        """
        for stat in self.stats:
            if stat.nom == nom:
                return stat
        return None

    def ajouter_stat(self, statistique: Statistique) -> None:
        """Ajoute une statistique au participant.

        Si une stat avec le même nom existe déjà, elle est remplacée.

        Parameters
        ----------
        statistique : Statistique
            La statistique à ajouter.
        """
        existante = self.get_stat(statistique.nom)
        if existante is not None:
            self.stats.remove(existante)
        self.stats.append(statistique)

    def get_historique(self, matchs: list[Match]) -> list[Match]:
        """Retourne la liste des matchs joués par ce participant.

        Parameters
        ----------
        matchs : list[Match]
            Liste de matchs à filtrer.

        Returns
        -------
        list[Match]
            Matchs où le participant figure.
        """
        return [m for m in matchs if self in m.participants]

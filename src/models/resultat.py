"""Module définissant la classe Resultat."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .participant import Participant


class Resultat:
    """Représente le résultat d'un participant dans un match.

    Un résultat associe une valeur numérique (score, points, etc.)
    et un type (buts, sets, victoire) à un participant précis.

    Attributes
    ----------
    id : int
        Identifiant unique du résultat.
    valeur : float
        Valeur numérique du résultat.
    type : str
        Type de résultat (ex: "buts", "sets", "victoire", "elo").
    participant : Participant
        Participant auquel se rattache ce résultat.

    Examples
    --------
    Football :
    >>> Resultat(1, valeur=3, type="buts", participant=psg)

    Tennis :
    >>> Resultat(2, valeur=2, type="sets", participant=nadal)

    Échecs :
    >>> Resultat(3, valeur=1.0, type="victoire", participant=carlsen)
    """

    def __init__(
        self,
        id: int,
        valeur: float,
        type: str,
        participant: Participant,
    ) -> None:
        """Initialise un résultat.

        Parameters
        ----------
        id : int
            Identifiant unique.
        valeur : float
            Valeur numérique du résultat.
        type : str
            Type de résultat.
        participant : Participant
            Participant concerné.

        Raises
        ------
        ValueError
            Si le type est vide.
        """
        if not type or not type.strip():
            raise ValueError("Le type de résultat ne peut pas être vide.")
        self.id = id
        self.valeur = float(valeur)
        self.type = type.strip()
        self.participant = participant

    def __repr__(self) -> str:
        return (
            f"Resultat(id={self.id}, valeur={self.valeur}, "
            f"type='{self.type}', participant={self.participant.nom})"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Resultat):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def to_dict(self) -> dict:
        """Sérialise le résultat en dictionnaire.

        Note: ne sérialise que l'id du participant pour éviter la récursion.
        """
        return {
            "id": self.id,
            "valeur": self.valeur,
            "type": self.type,
            "participant_id": self.participant.id,
        }

"""Module définissant la classe Match."""

from __future__ import annotations

from datetime import date as date_type
from typing import TYPE_CHECKING

from .enums import MatchStatus

if TYPE_CHECKING:
    from .participant import Participant
    from .resultat import Resultat


class Match:
    """Représente un match (affrontement entre participants).

    Un match oppose 2 participants ou plus, suit un cycle de vie
    (planifié → en cours → terminé) et produit des résultats.

    Attributes
    ----------
    id : int
        Identifiant unique.
    date : date
        Date du match.
    statut : MatchStatus
        État courant du match.
    participants : list[Participant]
        Participants opposés.
    resultats : list[Resultat]
        Résultats du match.
    lieu : optional
        Lieu du match (optionnel).
    phase : str
        Phase de la compétition ("Poule A", "Demi-finale", "Journée 12"...).
    type_fin : str
        Type de fin ("REGLEMENTAIRE", "PROLONGATION", "TAB", "FORFAIT"...).
    """

    def __init__(
        self,
        id: int,
        date: date_type,
        participants: list[Participant],
        statut: MatchStatus = MatchStatus.PLANIFIE,
        lieu=None,
        phase: str = "",
        type_fin: str = "REGLEMENTAIRE",
    ) -> None:
        """Initialise un match.

        Parameters
        ----------
        id : int
            Identifiant unique.
        date : date
            Date du match.
        participants : list[Participant]
            Liste de 2 participants minimum.
        statut : MatchStatus, optional
            Statut initial (par défaut PLANIFIE).
        lieu : Lieu, optional
            Lieu du match.
        phase : str, optional
            Phase / journée de la compétition.
        type_fin : str, optional
            Type de fin du match.

        Raises
        ------
        ValueError
            Si moins de 2 participants.
        """
        if len(participants) < 2:
            raise ValueError("Un match doit avoir au moins 2 participants.")
        self.id = id
        self.date = date
        self.statut = statut
        self.participants: list[Participant] = list(participants)
        self.resultats: list[Resultat] = []
        self.lieu = lieu
        self.phase = phase
        self.type_fin = type_fin

    def __repr__(self) -> str:
        noms = " vs ".join(p.nom for p in self.participants)
        return f"Match(id={self.id}, {noms}, statut={self.statut.value})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Match):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def ajouter_resultat(self, resultat: Resultat) -> None:
        """Ajoute un résultat au match.

        Parameters
        ----------
        resultat : Resultat
            Résultat à enregistrer.

        Raises
        ------
        ValueError
            Si le participant du résultat n'est pas dans le match.
        """
        if resultat.participant not in self.participants:
            raise ValueError(
                f"Le participant {resultat.participant.nom} "
                f"ne fait pas partie de ce match."
            )
        self.resultats.append(resultat)

    def obtenir_resultats(self) -> list[Resultat]:
        """Retourne la liste des résultats."""
        return list(self.resultats)

    def get_resultats_participant(self, participant: Participant) -> list[Resultat]:
        """Retourne les résultats associés à un participant donné."""
        return [r for r in self.resultats if r.participant == participant]

    def get_score_participant(self, participant: Participant) -> float:
        """Calcule le score total d'un participant pour ce match.

        Parameters
        ----------
        participant : Participant
            Participant cible.

        Returns
        -------
        float
            Somme des valeurs des résultats du participant.
        """
        return sum(r.valeur for r in self.get_resultats_participant(participant))

    def get_vainqueur(self) -> Participant | None:
        """Détermine le vainqueur du match.

        Compare les scores totaux des participants. Si plusieurs
        participants ont le même score maximal, retourne None (match nul).

        Returns
        -------
        Participant or None
            Le vainqueur, ou None si égalité ou si pas encore terminé.
        """
        if self.statut != MatchStatus.TERMINE or not self.resultats:
            return None
        scores = {p: self.get_score_participant(p) for p in self.participants}
        score_max = max(scores.values())
        gagnants = [p for p, s in scores.items() if s == score_max]
        if len(gagnants) == 1:
            return gagnants[0]
        return None  # Match nul ou égalité

    def est_nul(self) -> bool:
        """Indique si le match s'est terminé sur un nul.

        Returns
        -------
        bool
            True si match terminé sans vainqueur unique.
        """
        if self.statut != MatchStatus.TERMINE or not self.resultats:
            return False
        return self.get_vainqueur() is None

    def to_dict(self) -> dict:
        """Sérialise le match en dictionnaire."""
        return {
            "id": self.id,
            "date": self.date.isoformat(),
            "statut": self.statut.value,
            "participants_ids": [p.id for p in self.participants],
            "resultats": [r.to_dict() for r in self.resultats],
            "phase": self.phase,
            "type_fin": self.type_fin,
        }
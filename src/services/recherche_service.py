"""Service de recherche dans les données d'une compétition."""

from __future__ import annotations

from datetime import date

from src.models import Competition, Match, MatchStatus, Participant


class RechercheService:
    """Service de recherche et filtrage."""

    @staticmethod
    def chercher_participant_par_nom(
        competition: Competition, nom: str, exact: bool = False
    ) -> list[Participant]:
        """Recherche un participant par son nom.

        Parameters
        ----------
        competition : Competition
            Compétition dans laquelle chercher.
        nom : str
            Nom (ou fragment) recherché.
        exact : bool, optional
            Si True, comparaison stricte ; sinon contient (insensible casse).

        Returns
        -------
        list[Participant]
            Liste des participants correspondants.
        """
        nom_recherche = nom.strip()
        if exact:
            return [p for p in competition.participants if p.nom == nom_recherche]
        nom_lower = nom_recherche.lower()
        return [p for p in competition.participants if nom_lower in p.nom.lower()]

    @staticmethod
    def matchs_entre_dates(
        competition: Competition, debut: date, fin: date
    ) -> list[Match]:
        """Retourne les matchs joués entre deux dates.

        Parameters
        ----------
        competition : Competition
            Compétition à filtrer.
        debut : date
            Date de début (incluse).
        fin : date
            Date de fin (incluse).

        Returns
        -------
        list[Match]
            Matchs dans l'intervalle.
        """
        return [m for m in competition.matchs if debut <= m.date <= fin]

    @staticmethod
    def matchs_par_phase(competition: Competition, phase: str) -> list[Match]:
        """Retourne les matchs d'une phase donnée.

        Parameters
        ----------
        competition : Competition
            Compétition à filtrer.
        phase : str
            Phase recherchée (ex: "J1", "Quart de finale").

        Returns
        -------
        list[Match]
            Matchs correspondants.
        """
        phase_lower = phase.strip().lower()
        return [m for m in competition.matchs if m.phase.lower() == phase_lower]

    @staticmethod
    def matchs_par_statut(
        competition: Competition, statut: MatchStatus
    ) -> list[Match]:
        """Retourne les matchs ayant un statut donné."""
        return [m for m in competition.matchs if m.statut == statut]

    @staticmethod
    def confrontation_directe(
        competition: Competition,
        participant_a: Participant,
        participant_b: Participant,
    ) -> list[Match]:
        """Retourne tous les matchs entre deux participants.

        Parameters
        ----------
        competition : Competition
            Compétition cible.
        participant_a, participant_b : Participant
            Les deux participants.

        Returns
        -------
        list[Match]
            Liste des affrontements directs.
        """
        return [
            m
            for m in competition.matchs
            if participant_a in m.participants and participant_b in m.participants
        ]

    @staticmethod
    def filtrer_matchs(
        competition: Competition,
        statut: MatchStatus | None = None,
        phase: str | None = None,
        date_min: date | None = None,
        date_max: date | None = None,
        participant: Participant | None = None,
    ) -> list[Match]:
        """Filtre les matchs selon plusieurs critères combinés.

        Tous les critères passés sont appliqués (ET logique).

        Parameters
        ----------
        competition : Competition
            Compétition cible.
        statut : MatchStatus, optional
            Filtre par statut.
        phase : str, optional
            Filtre par phase.
        date_min : date, optional
            Date minimum (incluse).
        date_max : date, optional
            Date maximum (incluse).
        participant : Participant, optional
            Match impliquant ce participant.

        Returns
        -------
        list[Match]
            Matchs correspondant à tous les critères.
        """
        resultat = list(competition.matchs)
        if statut is not None:
            resultat = [m for m in resultat if m.statut == statut]
        if phase is not None:
            resultat = [m for m in resultat if m.phase.lower() == phase.lower()]
        if date_min is not None:
            resultat = [m for m in resultat if m.date >= date_min]
        if date_max is not None:
            resultat = [m for m in resultat if m.date <= date_max]
        if participant is not None:
            resultat = [m for m in resultat if participant in m.participants]
        return resultat

"""Module définissant la classe Competition."""

from .enums import Genre
from .match import Match
from .participant import Participant
from .saison import Saison
from .sport import Sport


class Competition:
    """Représente une compétition sportive (championnat, tournoi, coupe...).

    Une compétition regroupe des matchs sur une saison et permet de
    calculer un classement des participants.

    Attributs
    ----------
    id : int
        Identifiant unique.
    nom : str
        Nom de la compétition (ex: "Ligue 1", "Roland Garros").
    sport : Sport
        Sport concerné.
    saison : Saison
        Saison sportive.
    categorie : str
        Catégorie ("Senior", "U17", "Vétéran"...).
    genre : Genre
        Genre des participants.
    matchs : list[Match]
        Liste des matchs.
    participants : list[Participant]
        Liste des participants inscrits.
    """

    def __init__(
        self,
        id: int,
        nom: str,
        sport: Sport,
        saison: Saison,
        categorie: str = "Senior",
        genre: Genre = Genre.MASCULIN,
    ) -> None:
        """Initialise une compétition.

        Parameters
        ----------
        id : int
            Identifiant unique.
        nom : str
            Nom de la compétition.
        sport : Sport
            Sport concerné.
        saison : Saison
            Saison.
        categorie : str, optional
            Catégorie d'âge (par défaut "Senior").
        genre : Genre, optional
            Genre (par défaut MASCULIN).

        Raises
        ------
        ValueError
            Si le nom est vide.
        """
        if not nom or not nom.strip():
            raise ValueError("Le nom de la compétition ne peut pas être vide.")
        self.id = id
        self.nom = nom.strip()
        self.sport = sport
        self.saison = saison
        self.categorie = categorie
        self.genre = genre
        self.matchs: list[Match] = []
        self.participants: list[Participant] = []

    def __repr__(self) -> str:
        return (
            f"Competition(id={self.id}, nom='{self.nom}', "
            f"sport={self.sport.nom}, saison={self.saison.nom})"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Competition):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    # ----- Gestion des participants -----

    def ajouter_participant(self, participant: Participant) -> None:
        """Inscrit un participant à la compétition.

        Parameters
        ----------
        participant : Participant
            Participant à inscrire.

        Raises
        ------
        ValueError
            Si le participant est déjà inscrit.
        """
        if participant in self.participants:
            raise ValueError(f"Le participant {participant.nom} est déjà inscrit.")
        self.participants.append(participant)

    def get_participants(self) -> list[Participant]:
        """Retourne la liste des participants inscrits."""
        return list(self.participants)

    # ----- Gestion des matchs -----

    def ajouter_match(self, match: Match) -> None:
        """Ajoute un match à la compétition.

        Inscrit automatiquement les participants du match s'ils ne le sont pas.

        Parameters
        ----------
        match : Match
            Match à ajouter.
        """
        self.matchs.append(match)
        for p in match.participants:
            if p not in self.participants:
                self.participants.append(p)

    def get_matchs_participant(self, participant: Participant) -> list[Match]:
        """Retourne les matchs joués par un participant.

        Parameters
        ----------
        participant : Participant
            Participant cible.

        Returns
        -------
        list[Match]
            Matchs où figure le participant.
        """
        return [m for m in self.matchs if participant in m.participants]

    # ----- Classement et statistiques -----

    def mettre_a_jour_classement(self) -> None:
        """Recalcule les statistiques de tous les participants.

        Parcourt tous les matchs terminés et appelle update_stats()
        sur chaque participant pour chaque résultat.
        """
        # Réinitialise les stats des participants
        for p in self.participants:
            p.stats.clear()
        # Recalcule à partir de tous les résultats
        for match in self.matchs:
            for resultat in match.obtenir_resultats():
                resultat.participant.update_stats(resultat)

    def get_classement(self, critere: str = "points") -> list[Participant]:
        """Retourne le classement des participants selon un critère.

        Parameters
        ----------
        critere : str, optional
            Nom de la statistique servant de critère (par défaut "points").

        Returns
        -------
        list[Participant]
            Participants triés du meilleur au moins bon selon le critère.
        """

        def cle_tri(p: Participant) -> float:
            stat = p.get_stat(critere)
            return stat.valeur if stat else 0.0

        return sorted(self.participants, key=cle_tri, reverse=True)

    def get_statistiques(self) -> dict:
        """Retourne des statistiques globales de la compétition.

        Returns
        -------
        dict
            Dictionnaire contenant nombre de matchs, participants, etc.
        """
        from .enums import MatchStatus

        matchs_termines = [m for m in self.matchs if m.statut == MatchStatus.TERMINE]
        return {
            "nb_matchs": len(self.matchs),
            "nb_matchs_termines": len(matchs_termines),
            "nb_participants": len(self.participants),
            "nb_matchs_nuls": sum(1 for m in matchs_termines if m.est_nul()),
        }

    def to_dict(self) -> dict:
        """Sérialise la compétition en dictionnaire."""
        return {
            "id": self.id,
            "nom": self.nom,
            "sport": self.sport.to_dict(),
            "saison": self.saison.to_dict(),
            "categorie": self.categorie,
            "genre": self.genre.value,
            "participants_ids": [p.id for p in self.participants],
            "matchs": [m.to_dict() for m in self.matchs],
        }

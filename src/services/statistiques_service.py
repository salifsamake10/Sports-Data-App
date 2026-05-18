"""Service de calcul de statistiques agrégées sur une compétition."""

from __future__ import annotations

from src.models import Competition, Match, MatchStatus, Participant


class StatistiquesService:
    """Service d'analyses statistiques globales.

    Méthodes statiques pour obtenir des indicateurs agrégés
    sur une ou plusieurs compétitions.
    """

    @staticmethod
    def meilleur_attaque(
        competition: Competition, type_resultat: str = "buts"
    ) -> Participant | None:
        """Retourne le participant ayant marqué le plus.

        Parameters
        ----------
        competition : Competition
            Compétition à analyser.
        type_resultat : str
            Type de résultat à comparer.

        Returns
        -------
        Participant or None
            Le meilleur attaquant, ou None si pas de données.
        """
        if not competition.participants:
            return None
        return max(
            competition.participants,
            key=lambda p: p.get_stat(type_resultat).valeur if p.get_stat(type_resultat) else 0,
        )

    @staticmethod
    def meilleure_defense(
        competition: Competition, type_resultat: str = "buts"
    ) -> Participant | None:
        """Retourne le participant ayant le moins encaissé.

        Calcule pour chaque participant le total des résultats encaissés
        sur l'ensemble de ses matchs.

        Parameters
        ----------
        competition : Competition
            Compétition à analyser.
        type_resultat : str
            Type de résultat à comparer.

        Returns
        -------
        Participant or None
            Le meilleur défenseur (moins encaissé).
        """
        if not competition.participants:
            return None

        encaisses = {p: 0.0 for p in competition.participants}
        for match in competition.matchs:
            if match.statut != MatchStatus.TERMINE:
                continue
            for p in match.participants:
                # Tous les résultats du match qui ne sont pas du participant
                for resultat in match.resultats:
                    if resultat.participant != p and resultat.type == type_resultat:
                        encaisses[p] += resultat.valeur

        return min(encaisses, key=encaisses.get)

    @staticmethod
    def moyenne_par_match(competition: Competition, type_resultat: str = "buts") -> float:
        """Calcule la moyenne du type de résultat par match.

        Parameters
        ----------
        competition : Competition
            Compétition cible.
        type_resultat : str
            Type de résultat à moyenner.

        Returns
        -------
        float
            Moyenne sur tous les matchs terminés.
        """
        matchs_termines = [m for m in competition.matchs if m.statut == MatchStatus.TERMINE]
        if not matchs_termines:
            return 0.0
        total = sum(
            r.valeur for m in matchs_termines for r in m.resultats if r.type == type_resultat
        )
        return total / len(matchs_termines)

    @staticmethod
    def top_n_buteurs(
        competition: Competition,
        n: int = 5,
        type_resultat: str = "buts",
    ) -> list[tuple[Participant, float]]:
        """Retourne les N meilleurs participants pour une stat.

        Parameters
        ----------
        competition : Competition
            Compétition cible.
        n : int, optional
            Nombre de participants (par défaut 5).
        type_resultat : str
            Type de stat.

        Returns
        -------
        list[tuple[Participant, float]]
            Top N : (participant, valeur).
        """
        scores = []
        for p in competition.participants:
            stat = p.get_stat(type_resultat)
            valeur = stat.valeur if stat else 0
            scores.append((p, valeur))
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:n]

    @staticmethod
    def matchs_avec_plus_de(
        competition: Competition,
        seuil: float,
        type_resultat: str = "buts",
    ) -> list[Match]:
        """Retourne les matchs avec un total supérieur à un seuil.

        Utile pour repérer les "matchs spectaculaires".

        Parameters
        ----------
        competition : Competition
            Compétition à filtrer.
        seuil : float
            Seuil minimum (strict).
        type_resultat : str
            Type de résultat à totaliser.

        Returns
        -------
        list[Match]
            Liste des matchs concernés.
        """
        resultat = []
        for match in competition.matchs:
            if match.statut != MatchStatus.TERMINE:
                continue
            total = sum(r.valeur for r in match.resultats if r.type == type_resultat)
            if total > seuil:
                resultat.append(match)
        return resultat

    @staticmethod
    def taux_match_nul(competition: Competition) -> float:
        """Pourcentage de matchs nuls dans la compétition.

        Parameters
        ----------
        competition : Competition
            Compétition cible.

        Returns
        -------
        float
            Pourcentage entre 0 et 1.
        """
        matchs_termines = [m for m in competition.matchs if m.statut == MatchStatus.TERMINE]
        if not matchs_termines:
            return 0.0
        nuls = sum(1 for m in matchs_termines if m.est_nul())
        return nuls / len(matchs_termines)

    @staticmethod
    def rapport_global(competition: Competition, type_resultat: str = "buts") -> dict:
        """Génère un rapport synthétique de la compétition.

        Parameters
        ----------
        competition : Competition
            Compétition à analyser.

        Returns
        -------
        dict
            Indicateurs principaux.
        """
        return {
            "nom": competition.nom,
            "sport": competition.sport.nom,
            "nb_participants": len(competition.participants),
            "nb_matchs_total": len(competition.matchs),
            "nb_matchs_termines": sum(
                1 for m in competition.matchs if m.statut == MatchStatus.TERMINE
            ),
            "moyenne_buts_par_match": round(StatistiquesService.moyenne_par_match(
                                                                    competition, type_resultat), 2),
            "taux_match_nul": round(StatistiquesService.taux_match_nul(competition) * 100, 1)
        }

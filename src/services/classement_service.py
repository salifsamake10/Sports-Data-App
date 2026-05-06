"""Service de calcul de classements.

Implémente différentes stratégies de classement (foot, tennis, échecs…)
qui peuvent s'appliquer à n'importe quelle compétition.
"""

from __future__ import annotations

from src.models import Competition, MatchStatus


class ClassementService:
    """Service de calcul de classements selon différentes règles.

    Chaque méthode applique une stratégie de calcul de points et
    retourne une liste de tuples (participant, points, détails).
    """

    @staticmethod
    def classement_par_points_3_1_0(
        competition: Competition,
        type_resultat: str = "buts",
    ) -> list[dict]:
        """Classement style football : 3 pts victoire, 1 pt nul, 0 défaite.

        Parameters
        ----------
        competition : Competition
            Compétition à classer.
        type_resultat : str, optional
            Type de résultat sur lequel se base la victoire (par défaut "buts").

        Returns
        -------
        list[dict]
            Liste triée du meilleur au moins bon, chaque entrée contient :
            participant, points, victoires, nuls, defaites, marques, encaisses,
            difference, joues.
        """
        stats = {
            p: {
                "participant": p,
                "points": 0,
                "victoires": 0,
                "nuls": 0,
                "defaites": 0,
                "marques": 0.0,
                "encaisses": 0.0,
                "joues": 0,
            }
            for p in competition.participants
        }

        for match in competition.matchs:
            if match.statut != MatchStatus.TERMINE:
                continue
            if len(match.participants) != 2:
                continue

            p1, p2 = match.participants
            score1 = match.get_score_participant(p1)
            score2 = match.get_score_participant(p2)

            stats[p1]["joues"] += 1
            stats[p2]["joues"] += 1
            stats[p1]["marques"] += score1
            stats[p1]["encaisses"] += score2
            stats[p2]["marques"] += score2
            stats[p2]["encaisses"] += score1

            if score1 > score2:
                stats[p1]["points"] += 3
                stats[p1]["victoires"] += 1
                stats[p2]["defaites"] += 1
            elif score2 > score1:
                stats[p2]["points"] += 3
                stats[p2]["victoires"] += 1
                stats[p1]["defaites"] += 1
            else:
                stats[p1]["points"] += 1
                stats[p2]["points"] += 1
                stats[p1]["nuls"] += 1
                stats[p2]["nuls"] += 1

        # Calcul de la différence et tri
        resultat = list(stats.values())
        for ligne in resultat:
            ligne["difference"] = ligne["marques"] - ligne["encaisses"]

        # Tri : points décroissants, puis différence, puis marqués
        resultat.sort(
            key=lambda x: (x["points"], x["difference"], x["marques"]),
            reverse=True,
        )
        return resultat

    @staticmethod
    def classement_par_victoires(
        competition: Competition,
    ) -> list[dict]:
        """Classement simple : nombre de victoires (sports individuels).

        Adapté pour tennis, badminton, échecs où le nombre de victoires
        est le critère principal.

        Parameters
        ----------
        competition : Competition
            Compétition à classer.

        Returns
        -------
        list[dict]
            Liste triée par nombre de victoires.
        """
        stats = {
            p: {
                "participant": p,
                "victoires": 0,
                "defaites": 0,
                "joues": 0,
                "ratio": 0.0,
            }
            for p in competition.participants
        }

        for match in competition.matchs:
            if match.statut != MatchStatus.TERMINE:
                continue
            vainqueur = match.get_vainqueur()
            for p in match.participants:
                stats[p]["joues"] += 1
                if vainqueur is None:
                    continue  # Match nul ou non décidé
                if p == vainqueur:
                    stats[p]["victoires"] += 1
                else:
                    stats[p]["defaites"] += 1

        for ligne in stats.values():
            if ligne["joues"] > 0:
                ligne["ratio"] = ligne["victoires"] / ligne["joues"]

        resultat = sorted(
            stats.values(),
            key=lambda x: (x["victoires"], x["ratio"]),
            reverse=True,
        )
        return resultat

    @staticmethod
    def classement_par_score_total(
        competition: Competition,
        type_resultat: str = "buts",
    ) -> list[dict]:
        """Classement par cumul d'une statistique (sports à scores).

        Parameters
        ----------
        competition : Competition
            Compétition à classer.
        type_resultat : str
            Type de stat à cumuler.

        Returns
        -------
        list[dict]
            Liste triée par valeur cumulée décroissante.
        """
        resultat = []
        for p in competition.participants:
            stat = p.get_stat(type_resultat)
            valeur = stat.valeur if stat else 0.0
            resultat.append({"participant": p, "total": valeur})
        resultat.sort(key=lambda x: x["total"], reverse=True)
        return resultat

    @staticmethod
    def afficher_classement(classement: list[dict], limite: int = 10) -> str:
        """Formate un classement pour affichage console.

        Parameters
        ----------
        classement : list[dict]
            Sortie d'une méthode de classement.
        limite : int, optional
            Nombre maximum de lignes (par défaut 10).

        Returns
        -------
        str
            Tableau formaté.
        """
        if not classement:
            return "Aucun participant."

        lignes = []
        # En-têtes selon le type de classement
        premiere = classement[0]
        if "points" in premiere:
            lignes.append(
                f"{'#':>3} {'Participant':<20} {'Pts':>4} "
                f"{'J':>3} {'V':>3} {'N':>3} {'D':>3} {'Diff':>5}"
            )
            lignes.append("-" * 50)
            for i, ligne in enumerate(classement[:limite], 1):
                lignes.append(
                    f"{i:>3} {ligne['participant'].nom:<20} "
                    f"{ligne['points']:>4} {ligne['joues']:>3} "
                    f"{ligne['victoires']:>3} {ligne['nuls']:>3} "
                    f"{ligne['defaites']:>3} {ligne['difference']:>+5.0f}"
                )
        elif "victoires" in premiere:
            lignes.append(f"{'#':>3} {'Participant':<20} {'V':>3} {'D':>3} {'J':>3} {'Ratio':>6}")
            lignes.append("-" * 45)
            for i, ligne in enumerate(classement[:limite], 1):
                lignes.append(
                    f"{i:>3} {ligne['participant'].nom:<20} "
                    f"{ligne['victoires']:>3} {ligne['defaites']:>3} "
                    f"{ligne['joues']:>3} {ligne['ratio']:>6.2%}"
                )
        else:
            lignes.append(f"{'#':>3} {'Participant':<20} {'Total':>8}")
            lignes.append("-" * 35)
            for i, ligne in enumerate(classement[:limite], 1):
                lignes.append(f"{i:>3} {ligne['participant'].nom:<20} {ligne['total']:>8.1f}")
        return "\n".join(lignes)

from __future__ import annotations

from .joueur import Joueur


class Equipe:
    """
    Classe représentant une équipe de joueurs.

    Parameters
    ----------
    nom_officiel : str
        Nom officiel de l'équipe.
    nom_abreviation : str
        Abréviation de 2 à 3 caractères, alphanumérique et en majuscules.
    region : str
        Région de l'équipe, parmi "KR", "CN", "EMEA", "NA", "APAC", "VN", "BR", "LAT".
    joueurs : tuple[Joueur]
        Tuple contenant exactement 5 instances de Joueur, toutes uniques.
    coachs : tuple[Coach]
        Tuple contenant 1 ou 2 instances de Coach, toutes uniques.

    Examples
    --------
    >>> j1 = Joueur("Alpha")
    >>> j2 = Joueur("Bravo")
    >>> j3 = Joueur("Charlie")
    >>> j4 = Joueur("Delta")
    >>> j5 = Joueur("Echo")
    >>> c1 = Coach("MasterYoda")
    >>> equipe = Equipe("TeamRocket", "TR", "EMEA", (j1,j2,j3,j4,j5), (c1,))
    >>> print(equipe.nom_officiel)
    TeamRocket
    >>> print(equipe.joueurs[0])
    Alpha
    """

    def __init__(self, nom_officiel: str, nom_abreviation: str, pays: str, joueurs: tuple[Joueur]) -> None:
        if not isinstance(nom_officiel, str):
            raise TypeError("Le nom officiel doit être une chaîne de caractères")
        if (
            not isinstance(nom_abreviation, str)
            or len(nom_abreviation) not in (2, 3)
            or not nom_abreviation.isalnum()
            or not nom_abreviation.isupper()
        ):
            raise ValueError("Nom abréviation invalide (2-3 caractères, alphanumérique, majuscules)")

        if not all(isinstance(j, Joueur) for j in joueurs):
            raise TypeError("Tous les éléments de joueurs doivent être des instances de Joueur")
        if len(set(joueurs)) != len(joueurs):
            raise ValueError("Tous les joueurs doivent être uniques")


        self.__nom_officiel: str = nom_officiel
        self.__nom_abreviation: str = nom_abreviation
        self.__pays: str = pays
        self.__joueurs: tuple[Joueur, ...] = joueurs

    # Propriétés
    @property
    def nom_officiel(self) -> str:
        """Renvoie le nom officiel de l'équipe."""
        return self.__nom_officiel

    @property
    def nom_abreviation(self) -> str:
        """Renvoie l'abréviation de l'équipe."""
        return self.__nom_abreviation

    @property
    def pays(self) -> str:
        """Renvoie la région de l'équipe."""
        return self.__pays

    @property
    def joueurs(self) -> tuple[Joueur, ...]:
        """Renvoie le tuple des joueurs de l'équipe."""
        return self.__joueurs


    #  Methode

    def __str__(self) -> str:
        """
        Représentation informelle de l'équipe.

        Returns
        -------
        str
            Nom abrégé de l'équipe.
        """
        return self.nom_abreviation

    def __repr__(self) -> str:
        """
        Représentation officielle de l'équipe, utilisable pour recréer l'instance.

        Returns
        -------
        str
            Code Python pour créer cette équipe.


        """
        return (
            f"{self.__class__.__name__}("
            f"'{self.nom_officiel}', '{self.nom_abreviation}', '{self.pays}', "
            f"{self.joueurs})"
        )

    def __eq__(self, other: object) -> bool:
        """
        Test d'égalité entre deux équipes.

        Parameters
        ----------
        other
            Autre objet à comparer.

        Returns
        -------
        bool
            True si les deux équipes ont le même nom officiel, False sinon.


        """
        if isinstance(other, Equipe):
            return self.nom_officiel == other.nom_officiel
        return NotImplemented

    def __lt__(self, other: object) -> bool:
        """
        Comparaison stricte entre deux équipes.

        Parameters
        ----------
        other : Equipe
            Autre objet à comparer.

        Returns
        -------
        bool
            True si le nom officiel de l'équipe courante est strictement
            inférieur à celui de l'autre équipe.

        """
        if isinstance(other, Equipe):
            return self.nom_officiel < other.nom_officiel
        return NotImplemented

    def __hash__(self) -> int:
        """
        Rend l'équipe hachable.

        Returns
        -------
        int
            Valeur de hachage basée sur la représentation officielle.


        """
        return hash(repr(self))
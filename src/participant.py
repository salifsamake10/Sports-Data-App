from __future__ import annotations

from abc import ABC
from typing import Any
from 

class _Participant(ABC):
    """
    Classe représentant une un participant avec un pseudonyme.

    Parameters
    ----------
    pseudo : str
        Pseudonyme du participant, chaîne de caractères de longueur 2 à 16.

    Examples
    --------
    >>> Participant1 = _Participant("Alice")
    >>> Participant2 = _Participant("Bob")
    >>> Participant1 == personne2
    False
    >>> print(Participant1)
    Alice
    """

    def __init__(self, pseudo: str, coach : tuple[_Coach, ...]) -> None:
        if not isinstance(pseudo, str):
            raise TypeError("Le pseudo doit être une chaîne de caractères")
        if not (2 <= len(pseudo) <= 16):
            raise ValueError("Le pseudo doit avoir entre 2 et 16 caractères")
        self.__pseudo = pseudo

    @property
    def pseudo(self) -> str:
        """
        Renvoie le pseudonyme du participant.

        Returns
        -------
        str
            Pseudonyme du participant

        Examples
        --------
        >>> Participant = _Participant("Alice")
        >>> Participant.pseudo
        'Alice'
        """
        return self.__pseudo

    def __eq__(self, other: Any) -> bool:
        """
        Test d'égalité entre deux participants.

        Parameters
        ----------
        other : Any
            Objet à comparer

        Returns
        -------
        bool
            True si les deux objets sont des _Participant et ont le même pseudo

        Examples
        --------
        >>> p1 = _Participant("Alice")
        >>> p2 = _Participant("Alice")
        >>> p3 = _Participant("Bob")
        >>> p1 == p2
        True
        >>> p1 == p3
        False
        """
        if isinstance(other, _Participant):
            return self.__pseudo == other.__pseudo
        return NotImplemented

    def __str__(self) -> str:
        """
        Représentation informelle de la personne.

        Returns
        -------
        str
            Pseudonyme de la personne

        Examples
        --------
        >>> p = _Personne("Alice")
        >>> str(p)
        'Alice'
        """
        return self.__pseudo

    def __repr__(self) -> str:
        """
        Représentation officielle de l'objet.

        Returns
        -------
        str
            Chaîne de caractères Python permettant de recréer l'objet

        Examples
        --------
        >>> p = _Personne("Alice")
        >>> repr(p)
        "_Personne('Alice')"
        """
        return f"{self.__class__.__name__}('{self.__pseudo}')"

    def __hash__(self) -> int:
        """
        Rendu hachable pour la personne.

        Returns
        -------
        int
            Valeur de hachage basée sur la représentation officielle

        Examples
        --------
        >>> p = _Personne("Alice")
        >>> isinstance(hash(p), int)
        True
        """
        return hash(repr(self))
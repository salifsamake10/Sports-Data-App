from .participant import _Participant


class Joueur(_Participant):
    """
    Classe représentant un joueur, héritant de _Participants.

    Parameters
    ----------
    pseudo : str
        Pseudonyme du joueur, chaîne de caractères de longueur 2 à 16.

    Examples
    --------
    >>> joueur1 = Joueur("Ninja")
    >>> joueur2 = Joueur("Shadow")
    >>> joueur1 == joueur2
    False
    >>> print(joueur1)
    Ninja
    """

    pass
"""Module des énumérations utilisées dans le projet."""

from enum import Enum


class Genre(Enum):
    """Genre d'un participant ou d'une compétition."""

    MASCULIN = "MASCULIN"
    FEMININ = "FEMININ"
    MIXTE = "MIXTE"


class MatchStatus(Enum):
    """Cycle de vie d'un match."""

    PLANIFIE = "PLANIFIE"
    EN_COURS = "EN_COURS"
    TERMINE = "TERMINE"
    ANNULE = "ANNULE"

"""Package services — logique métier de haut niveau."""

from .classement_service import ClassementService
from .recherche_service import RechercheService
from .statistiques_service import StatistiquesService

__all__ = [
    "ClassementService",
    "RechercheService",
    "StatistiquesService",
]

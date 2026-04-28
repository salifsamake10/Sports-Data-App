"""Point d'entrée de l'application de gestion de résultats sportifs.

Usage
-----
    python -m src.main --config configs/ligue1.json
    python -m src.main --config configs/ligue1.json --action classement
    python -m src.main --config configs/ligue1.json --action stats
    python -m src.main --config configs/ligue1.json --action sauvegarder
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.data import (
    DataCleaner,
    DataMapper,
    DataSaver,
    DataValidator,
    ValidationError,
    get_loader,
)
from src.models import Competition
from src.services import (
    ClassementService,
    StatistiquesService,
)


def charger_config(path: str | Path) -> dict:
    """Charge un fichier de configuration JSON."""
    chemin = Path(path)
    if not chemin.exists():
        raise FileNotFoundError(f"Fichier de configuration introuvable : {chemin}")
    with open(chemin, encoding="utf-8") as f:
        return json.load(f)


def construire_competition(config: dict) -> Competition:
    """Pipeline complet : load → clean → validate → map → competition.

    Parameters
    ----------
    config : dict
        Configuration chargée depuis un fichier JSON.

    Returns
    -------
    Competition
        Competition entièrement construite.

    Raises
    ------
    ValidationError
        Si les données ne respectent pas le schéma.
    """
    print(f"\n=== Chargement de '{config.get('competition', '?')}' ===")

    # 1. Lecture brute
    loader = get_loader(config["format_fichier"])
    donnees_brutes = loader.load(config["fichier_donnees"])
    print(f"  ✓ {len(donnees_brutes)} lignes brutes chargées")

    # 2. Nettoyage
    cleaner = DataCleaner()
    donnees_propres = cleaner.nettoyer(donnees_brutes)
    print(f"  ✓ {len(donnees_propres)} lignes après nettoyage")

    # 3. Validation
    schema = config.get("schema_validation")
    if schema:
        validator = DataValidator(schema)
        if not validator.valider(donnees_propres):
            print("  ⚠ Avertissements de validation :")
            for err in validator.erreurs[:5]:
                print(f"    - {err}")
            if len(validator.erreurs) > 5:
                print(f"    ... et {len(validator.erreurs) - 5} autres.")
        else:
            print("  ✓ Validation OK")

    # 4. Construction des objets
    mapper = DataMapper(config)
    competition = mapper.construire_competition(donnees_propres)
    print(
        f"  ✓ Competition construite : "
        f"{len(competition.matchs)} matchs, "
        f"{len(competition.participants)} participants"
    )
    return competition


def afficher_classement(competition: Competition, config: dict) -> None:
    """Affiche le classement selon le sport."""
    print(f"\n=== Classement — {competition.nom} ===\n")
    type_classement = config.get("type_classement", "points_3_1_0")
    type_resultat = config.get("type_resultat", "buts")

    if type_classement == "points_3_1_0":
        classement = ClassementService.classement_par_points_3_1_0(
            competition, type_resultat
        )
    elif type_classement == "victoires":
        classement = ClassementService.classement_par_victoires(competition)
    else:
        classement = ClassementService.classement_par_score_total(
            competition, type_resultat
        )

    print(ClassementService.afficher_classement(classement, limite=20))


def afficher_statistiques(competition: Competition, config: dict) -> None:
    """Affiche les statistiques globales de la compétition."""
    print(f"\n=== Statistiques — {competition.nom} ===\n")
    type_resultat = config.get("type_resultat", "buts")

    rapport = StatistiquesService.rapport_global(competition)
    for cle, valeur in rapport.items():
        print(f"  {cle:<25} : {valeur}")

    print("\n--- Top 5 attaques ---")
    top = StatistiquesService.top_n_buteurs(
        competition, n=5, type_resultat=type_resultat
    )
    for i, (p, v) in enumerate(top, 1):
        print(f"  {i}. {p.nom:<20} {v:.0f} {type_resultat}")

    meilleure_def = StatistiquesService.meilleure_defense(
        competition, type_resultat=type_resultat
    )
    if meilleure_def:
        print(f"\nMeilleure défense : {meilleure_def.nom}")

    spectaculaires = StatistiquesService.matchs_avec_plus_de(
        competition, seuil=4, type_resultat=type_resultat
    )
    if spectaculaires:
        print(f"\nMatchs avec plus de 4 {type_resultat} : {len(spectaculaires)}")


def sauvegarder(competition: Competition, config: dict) -> None:
    """Sauvegarde la compétition au format JSON."""
    nom_fichier = config.get("competition", "competition").lower().replace(" ", "_")
    chemin = Path("output") / f"{nom_fichier}.json"
    saver = DataSaver()
    saver.sauvegarder_competition(competition, chemin)
    print(f"\n✓ Compétition sauvegardée : {chemin}")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse les arguments de la ligne de commande."""
    parser = argparse.ArgumentParser(
        description="Application de gestion de résultats sportifs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples :
  python -m src.main --config configs/ligue1.json
  python -m src.main --config configs/ligue1.json --action classement
  python -m src.main --config configs/ligue1.json --action stats
  python -m src.main --config configs/ligue1.json --action sauvegarder
        """,
    )
    parser.add_argument(
        "--config",
        required=True,
        help="Chemin vers le fichier de configuration JSON.",
    )
    parser.add_argument(
        "--action",
        choices=["all", "classement", "stats", "sauvegarder"],
        default="all",
        help="Action à effectuer (par défaut : all).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Fonction principale.

    Parameters
    ----------
    argv : list[str], optional
        Arguments CLI (None pour utiliser sys.argv).

    Returns
    -------
    int
        Code de sortie (0 si succès).
    """
    args = parse_args(argv)

    try:
        config = charger_config(args.config)
    except FileNotFoundError as exc:
        print(f"{exc}", file=sys.stderr)
        return 1

    try:
        competition = construire_competition(config)
    except (ValidationError, KeyError, ValueError) as exc:
        print(f"Erreur de chargement : {exc}", file=sys.stderr)
        return 2

    if args.action in ("all", "classement"):
        afficher_classement(competition, config)
    if args.action in ("all", "stats"):
        afficher_statistiques(competition, config)
    if args.action in ("all", "sauvegarder"):
        sauvegarder(competition, config)

    return 0


if __name__ == "__main__":
    sys.exit(main())

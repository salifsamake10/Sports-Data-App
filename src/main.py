"""Point d'entrée de l'application de gestion de résultats sportifs.

Usage
-----
    python -m src.main --config configs/ligue1_relationnel.json
    python -m src.main --config configs/tennis_atp.json --action classement
    python -m src.main --config configs/basketball_nba.json --action stats
    python -m src.main --config configs/chess.json --action sauvegarder
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
    RelationalMapper,
    ValidationError,
    get_loader,
)
from src.models import Competition
from src.services import (
    ClassementService,
    RechercheService,
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

    Branche entre RelationalMapper (multi-fichiers) et DataMapper simple
    selon la valeur de "type_mapper" dans la config.

    Parameters
    ----------
    config : dict
        Configuration chargée depuis un fichier JSON.

    Returns
    -------
    Competition
        Competition entièrement construite.
    """
    nom = config.get("competition", config.get("ligue_filtre", "?"))
    print(f"\n=== Chargement de '{nom}' ===")

    # Mapper relationnel (multi-fichiers liés par id)
    if config.get("type_mapper") == "relationnel":
        mapper = RelationalMapper(config)
        competition = mapper.construire_competition()
        return competition

    # Mapper simple (un seul fichier CSV)
    loader = get_loader(config["format_fichier"])
    donnees_brutes = loader.load(config["fichier_donnees"])
    print(f"  ✓ {len(donnees_brutes)} lignes brutes chargées")

    cleaner = DataCleaner()
    donnees_propres = cleaner.nettoyer(donnees_brutes)
    print(f"  ✓ {len(donnees_propres)} lignes après nettoyage")

    schema = config.get("schema_validation")
    if schema:
        validator = DataValidator(schema)
        if not validator.valider(donnees_propres):
            print("  ⚠ Avertissements de validation :")
            for err in validator.erreurs[:5]:
                print(f"    - {err}")
        else:
            print("  ✓ Validation OK")

    mapper = DataMapper(config)
    competition = mapper.construire_competition(donnees_propres)
    print(
        f"  ✓ Competition construite : "
        f"{len(competition.matchs)} matchs, "
        f"{len(competition.participants)} participants"
    )
    return competition


def afficher_classement(competition: Competition, config: dict) -> None:
    """Affiche le classement selon le type configuré."""
    print(f"\n=== Classement — {competition.nom} ===\n")
    type_classement = config.get("type_classement", "points_3_1_0")
    type_resultat = config.get("type_resultat", "buts")

    if type_classement == "points_3_1_0":
        classement = ClassementService.classement_par_points_3_1_0(
            competition, type_resultat
        )
    elif type_classement == "victoires":
        classement = ClassementService.classement_par_victoires(competition)
    elif type_classement == "score_total":
        classement = ClassementService.classement_par_score_total(
            competition, type_resultat
        )
    else:
        classement = ClassementService.classement_par_score_total(
            competition, type_resultat
        )

    print(ClassementService.afficher_classement(classement, limite=20))


def afficher_statistiques(competition: Competition, config: dict) -> None:
    """Affiche les statistiques globales."""
    print(f"\n=== Statistiques — {competition.nom} ===\n")
    type_resultat = config.get("type_resultat", "buts")

    rapport = StatistiquesService.rapport_global(competition)
    for cle, valeur in rapport.items():
        print(f"  {cle:<25} : {valeur}")

    print("\n--- Top 5 ---")
    top = StatistiquesService.top_n_buteurs(
        competition, n=5, type_resultat=type_resultat
    )
    for i, (p, v) in enumerate(top, 1):
        print(f"  {i}. {p.nom:<25} {v:.0f} {type_resultat}")


def sauvegarder(competition: Competition, config: dict) -> None:
    """Sauvegarde la compétition au format JSON."""
    nom_fichier = competition.nom.lower().replace(" ", "_").replace("/", "_")
    chemin = Path("output") / f"{nom_fichier}.json"
    saver = DataSaver()
    saver.sauvegarder_competition(competition, chemin)
    print(f"\n✓ Compétition sauvegardée : {chemin}")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse les arguments de la ligne de commande."""
    parser = argparse.ArgumentParser(
        description="Application de gestion de résultats sportifs",
    )
    parser.add_argument("--config", required=True, help="Chemin vers la config JSON.")
    parser.add_argument(
        "--action",
        choices=["all", "classement", "stats", "sauvegarder"],
        default="all",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Fonction principale."""
    args = parse_args(argv)

    try:
        config = charger_config(args.config)
    except FileNotFoundError as exc:
        print(f"❌ {exc}", file=sys.stderr)
        return 1

    try:
        competition = construire_competition(config)
    except (ValidationError, KeyError, ValueError, FileNotFoundError) as exc:
        print(f"❌ Erreur de chargement : {exc}", file=sys.stderr)
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

# Application de gestion de résultats sportifs

Projet de traitement de données — ENSAI 2025/2026

Application Python permettant de charger, analyser et visualiser les résultats
de compétitions sportives à partir de jeux de données variés. L'application
est conçue pour être **générique** : elle fonctionne avec n'importe quel sport
(football, tennis, basketball, échecs, etc.) sans modifier le code, simplement
en changeant le fichier de configuration.

## Fonctionnalités

- Chargement de données brutes au format CSV depuis différents datasets
- Modélisation orientée objet : `Sport`, `Saison`, `Pays`, `Competition`, `Match`,
  `Participant` (Joueur, Équipe), `Resultat`, `Statistique`
- Calcul automatique de classements selon des règles configurables
  (système 3-1-0 pour le foot, victoires pour le tennis, score total pour les échecs)
- Statistiques agrégées : meilleur attaque, meilleure défense, top 5, taux de match nul
- Recherche multi-critères (par phase, par dates, confrontations directes)
- Sauvegarde des résultats au format JSON

## Sports supportés

L'application a été testée et validée sur 4 sports avec des structures de données très différentes :

| Sport | Source | Type | Exemple de classement |
|---|---|---|---|
| Football européen | `football_european_leagues` | Collectif | Ligue 1 2015/2016, PSG champion (96 pts) |
| Tennis ATP | `tennis` | Individuel | ATP Tour 2024, Sinner n°1 (74 victoires) |
| Basketball NBA | `Basketball` | Collectif | NBA 2022-2023, Boston en tête |
| Échecs | `chess` | Individuel | Tournoi 2024, Esipenko 1er |

## Prérequis

- **Python 3.11+**
- Système d'exploitation : Windows / Mac / Linux

## Installation

### 1. Cloner le dépôt

```bash
git clone <url-du-depot>
cd Projet_Info
```

### 2. Créer et activer un environnement virtuel

**Windows (PowerShell)** :

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Mac / Linux** :

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

## Lancement de l'application

L'application se lance avec une configuration JSON qui décrit le dataset
à charger.

```bash
python -m src.main --config configs/football_european_leagues.json
python -m src.main --config configs/tennis.json
python -m src.main --config configs/basketball.json
python -m src.main --config configs/chess.json
```

### Actions disponibles

L'option `--action` permet de cibler une opération précise :

```bash
python -m src.main --config configs/tennis.json --action classement
python -m src.main --config configs/tennis.json --action stats
python -m src.main --config configs/tennis.json --action sauvegarder
python -m src.main --config configs/tennis.json --action all       # par défaut
```

## Architecture du projet

```
Projet_Info/
├── src/
│   ├── models/          Classes du domaine (Match, Joueur, Equipe…)
│   ├── data/            Chargement, nettoyage, mapping, sauvegarde
│   ├── services/        Logique métier (classement, statistiques, recherche)
│   └── main.py          Point d'entrée CLI
├── configs/             Fichiers JSON de configuration par sport
├── datasets/            Données brutes
├── tests/               Tests unitaires pytest
├── output/              Fichiers JSON sauvegardés (créé automatiquement)
├── requirements.txt
├── LICENSE
└── README.md
```

## Tests

Les tests utilisent **pytest**. Pour les lancer :

```bash
pytest tests/ -v
```

Pour mesurer la couverture de code :

```bash
pip install pytest-cov
pytest tests/ --cov=src --cov-report=term-missing
```

## Style de code

- **Style des docstrings** : NumPy
- **Linter recommandé** : Ruff
  ```bash
  pip install ruff
  ruff check src/ tests/
  ```
- **Formatter recommandé** (optionnel) : Ruff format
  ```bash
  ruff format src/ tests/
  ```

## Ajouter un nouveau sport

L'un des objectifs principaux est la **réutilisabilité**. Pour ajouter un
nouveau sport, **aucune modification du code Python n'est requise** : il
suffit de créer un nouveau fichier JSON dans `configs/`.

Exemple pour ajouter le volleyball :

1. Placer les données CSV dans `datasets/volleyball/`
2. Créer `configs/volleyball.json` en s'inspirant des configs existantes
3. Lancer : `python -m src.main --config configs/volleyball.json`

## Auteurs

Projet réalisé dans le cadre du cours « Projet de traitement de données »
de l'ENSAI, encadré par Johann Faouzi.

## Licence

Ce projet est distribué sous licence MIT — voir le fichier `LICENSE` pour
plus de détails.

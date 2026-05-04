"""Mapper générique pour datasets relationnels multi-sports.

S'adapte à n'importe quel dataset (foot, tennis, basket, échecs)
via un fichier de configuration. Aucun code spécifique au sport :
il suffit d'écrire la bonne config JSON.

Utilise pandas pour le chargement, le filtrage et le nettoyage des CSV.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd

from src.models import (
    Competition,
    Equipe,
    Genre,
    Joueur,
    Match,
    MatchStatus,
    Pays,
    Resultat,
    Saison,
    Sport,
)


class RelationalMapper:
    """Mapper relationnel générique multi-sports.

    Charge les fichiers du dataset avec pandas et reconstruit
    les liens entre matchs et participants.
    """

    # Valeurs considérées comme manquantes dans les CSV
    VALEURS_MANQUANTES = ["", "NA", "N/A", "null", "None", "-", "?"]

    def __init__(self, config: dict) -> None:
        """Initialise le mapper.

        Parameters
        ----------
        config : dict
            Configuration du dataset (voir docstring du module).
        """
        self.config = config
        self._participants_par_cle: dict[str, Equipe | Joueur] = {}
        self._next_match_id = 1
        self._next_resultat_id = 1
        self._next_participant_id = 1

    # ===== Méthode principale =====

    def construire_competition(self) -> Competition:
        """Construit une Competition complète à partir des fichiers.

        Returns
        -------
        Competition
            Competition complète avec participants, matchs et résultats.
        """
        dossier = self.config["dossier"]

        # 1. Charger les participants depuis fichier_participants si présent
        if "fichier_participants" in self.config:
            self._charger_participants(dossier)

        # 2. Créer le squelette de la Competition
        competition = self._creer_competition()

        # 3. Charger les matchs avec pandas et appliquer les filtres
        df_matchs = self._charger_csv(
            f"{dossier}/{self.config['fichier_matchs']}"
        )
        nb_brut = len(df_matchs)
        df_matchs = self._appliquer_filtres(df_matchs)
        print(f"  → {nb_brut} matchs bruts, {len(df_matchs)} après filtrage")

        # 4. Construire chaque match
        nb_ajoutes = 0
        for ligne in df_matchs.itertuples(index=False):
            match = self._construire_match(ligne._asdict())
            if match is not None:
                competition.ajouter_match(match)
                nb_ajoutes += 1

        print(f"  → {nb_ajoutes} matchs valides ajoutés")
        print(f"  → {len(competition.participants)} participants")

        competition.mettre_a_jour_classement()
        return competition

    # ===== Chargement et nettoyage avec pandas =====

    def _charger_csv(self, chemin: str) -> pd.DataFrame:
        """Charge un CSV avec pandas et le nettoie.

        Parameters
        ----------
        chemin : str
            Chemin vers le fichier CSV.

        Returns
        -------
        pd.DataFrame
            DataFrame nettoyé (espaces supprimés, NaN normalisés, doublons).
        """
        chemin_path = Path(chemin)
        if not chemin_path.exists():
            raise FileNotFoundError(f"Fichier introuvable : {chemin_path}")

        # Lecture avec pandas + traitement des valeurs manquantes
        df = pd.read_csv(chemin_path, na_values=self.VALEURS_MANQUANTES)

        # Nettoyage : strip sur les colonnes texte
        colonnes_str = df.select_dtypes(include="object").columns
        for col in colonnes_str:
            df[col] = df[col].astype(str).str.strip()
            # Remettre NaN pour les chaînes "nan" (artefact de astype(str))
            df[col] = df[col].replace("nan", pd.NA)

        # Suppression des doublons
        df = df.drop_duplicates()
        return df

    def _charger_participants(self, dossier: str) -> None:
        """Charge les participants depuis fichier_participants avec pandas."""
        chemin = f"{dossier}/{self.config['fichier_participants']}"
        df = self._charger_csv(chemin)

        mapping = self.config.get("mapping_participant", {})
        col_id = mapping.get("id")
        col_nom = mapping.get("nom")
        if not col_id or not col_nom:
            return

        # Itération sur le DataFrame (style itertuples du prof)
        for r in df.itertuples(index=False):
            cle = str(getattr(r, col_id, "")).strip()
            nom = str(getattr(r, col_nom, "")).strip()
            if cle and cle != "nan" and nom and nom != "nan":
                self._participants_par_cle[cle] = self._creer_participant(nom)

        print(
            f"  → {len(self._participants_par_cle)} participants chargés "
            f"depuis {self.config['fichier_participants']}"
        )

    # ===== Filtres pandas =====

    def _appliquer_filtres(self, df: pd.DataFrame) -> pd.DataFrame:
        """Applique les filtres définis dans la config avec pandas.

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame à filtrer.

        Returns
        -------
        pd.DataFrame
            DataFrame filtré.
        """
        filtres = self.config.get("filtres", {})
        if not filtres:
            return df

        masque = pd.Series(True, index=df.index)
        for col, valeur_attendue in filtres.items():
            if col not in df.columns:
                continue
            # Conversion en str pour comparaison robuste
            masque &= df[col].astype(str) == str(valeur_attendue)

        return df[masque]

    # ===== Création de Competition =====

    def _creer_competition(self) -> Competition:
        sport = Sport(id=1, nom=self.config.get("sport", "Sport"))
        info_saison = self.config.get("saison", {})
        saison = Saison(
            annee_debut=info_saison.get("debut", 2024),
            annee_fin=info_saison.get("fin", 2025),
            nom=info_saison.get("nom"),
        )
        return Competition(
            id=1,
            nom=self.config.get("competition", "Compétition"),
            sport=sport,
            saison=saison,
            categorie=self.config.get("categorie", "Senior"),
            genre=Genre[self.config.get("genre", "MASCULIN")],
        )

    # ===== Construction d'un Match =====

    def _construire_match(self, ligne: dict) -> Match | None:
        """Construit un Match à partir d'une ligne du dataset."""
        mapping = self.config["mapping_match"]

        cle_p1 = self._lire_cle(ligne, mapping["participant_1"])
        cle_p2 = self._lire_cle(ligne, mapping["participant_2"])
        if not cle_p1 or not cle_p2:
            return None

        # Mode "winner_loser" : le gagnant a 1, le perdant 0
        if self.config.get("mode_resultat") == "winner_loser":
            score_1, score_2 = 1.0, 0.0
        else:
            score_1 = self._lire_float(ligne, mapping["score_1"])
            score_2 = self._lire_float(ligne, mapping["score_2"])
            if score_1 is None or score_2 is None:
                return None

        p1 = self._get_or_create_participant(cle_p1)
        p2 = self._get_or_create_participant(cle_p2)

        date_match = self._lire_date(ligne, mapping["date"])

        match = Match(
            id=self._next_match_id,
            date=date_match,
            participants=[p1, p2],
            statut=MatchStatus.TERMINE,
            phase=str(ligne.get(mapping.get("phase", ""), "")),
        )
        self._next_match_id += 1

        type_resultat = self.config.get("type_resultat", "points")
        match.ajouter_resultat(
            Resultat(
                id=self._next_resultat_id,
                valeur=score_1,
                type=type_resultat,
                participant=p1,
            )
        )
        self._next_resultat_id += 1
        match.ajouter_resultat(
            Resultat(
                id=self._next_resultat_id,
                valeur=score_2,
                type=type_resultat,
                participant=p2,
            )
        )
        self._next_resultat_id += 1
        return match

    # ===== Helpers de lecture utilisant pandas =====

    @staticmethod
    def _lire_cle(ligne: dict, colonne: str) -> str:
        """Lit une clé (id ou nom) depuis une ligne, gère les NaN."""
        valeur = ligne.get(colonne)
        if valeur is None or pd.isna(valeur):
            return ""
        # Si c'est un nombre flottant style 12345.0, on le convertit en int
        if isinstance(valeur, float) and valeur.is_integer():
            return str(int(valeur))
        return str(valeur).strip()

    @staticmethod
    def _lire_float(ligne: dict, colonne: str) -> float | None:
        """Lit un nombre depuis une ligne avec pd.to_numeric."""
        valeur = ligne.get(colonne)
        if valeur is None or pd.isna(valeur):
            return None
        try:
            resultat = pd.to_numeric(valeur, errors="coerce")
            if pd.isna(resultat):
                return None
            return float(resultat)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _lire_date(ligne: dict, colonne: str) -> date:
        """Lit une date avec pd.to_datetime (gère plusieurs formats)."""
        valeur = ligne.get(colonne)
        if valeur is None or pd.isna(valeur):
            return date(2000, 1, 1)

        # Cas particulier : format AAAAMMJJ tennis (entier)
        if isinstance(valeur, (int, float)) and not pd.isna(valeur):
            try:
                resultat = pd.to_datetime(str(int(valeur)), format="%Y%m%d", errors="coerce")
                if not pd.isna(resultat):
                    return resultat.date()
            except (ValueError, TypeError):
                pass

        # Cas général : pandas devine le format
        try:
            valeur_str = str(valeur).split(" ")[0]
            resultat = pd.to_datetime(valeur_str, errors="coerce")
            if pd.isna(resultat):
                return date(2000, 1, 1)
            return resultat.date()
        except (ValueError, TypeError):
            return date(2000, 1, 1)

    # ===== Gestion des participants =====

    def _get_or_create_participant(self, cle: str) -> Equipe | Joueur:
        """Retourne le participant existant ou en crée un."""
        if cle in self._participants_par_cle:
            return self._participants_par_cle[cle]
        participant = self._creer_participant(cle)
        self._participants_par_cle[cle] = participant
        return participant

    def _creer_participant(self, nom: str) -> Equipe | Joueur:
        """Crée un Participant selon le type configuré."""
        type_p = self.config.get("type_participant", "equipe").lower()
        pays_defaut = self._pays_defaut()
        genre = Genre[self.config.get("genre", "MASCULIN")]
        pid = self._next_participant_id
        self._next_participant_id += 1

        if type_p == "joueur":
            parties = nom.replace(",", "").split()
            prenom = parties[-1] if len(parties) > 1 else "Inconnu"
            nom_famille = parties[0] if parties else nom
            return Joueur(
                id=pid,
                nom=nom_famille,
                prenom=prenom,
                date_naissance=date(2000, 1, 1),
                pays=pays_defaut,
                genre=genre,
            )
        return Equipe(id=pid, nom=nom, pays=pays_defaut, genre=genre)

    def _pays_defaut(self) -> Pays:
        info = self.config.get("pays_defaut", {"nom": "Inconnu", "code": "XXX"})
        return Pays(nom=info["nom"], code=info["code"])

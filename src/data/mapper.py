"""Module de transformation des données nettoyées en objets métier.

Le mapper est le pont entre les dicts (sortie du cleaner) et les
classes du dossier models. Il utilise un fichier de configuration
qui décrit la correspondance entre les colonnes du dataset et les
attributs des objets ce qui rend le système réutilisable pour
n'importe quel sport sans modifier le code.
"""

from __future__ import annotations

from datetime import date

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
    # Statistique,
)

from .cleaner import DataCleaner


class DataMapper:
    """Transforme des dicts nettoyés en objets métier.

    La configuration permet d'adapter le mapping à n'importe quel
    dataset sans toucher au code.

    Configuration attendue (exemple) :
        {
          "sport": "Football",
          "saison": {"debut": 2023, "fin": 2024},
          "competition": "Ligue 1",
          "type_participant": "equipe",
          "mapping": {
            "id_match": "MatchID",
            "date": "Date",
            "participant_dom": "HomeTeam",
            "participant_ext": "AwayTeam",
            "score_dom": "FTHG",
            "score_ext": "FTAG"
          }
        }

    Attributs
    ----------
    config : dict
        Configuration du dataset.
    cleaner : DataCleaner
        Utilitaire de conversion de types.
    """

    def __init__(self, config: dict) -> None:
        """Initialise le mapper.

        Parameters
        ----------
        config : dict
            Configuration du mapping (voir docstring de classe).
        """
        self.config = config
        self.cleaner = DataCleaner()
        self._cache_participants: dict[str, Joueur | Equipe] = {}
        self._next_participant_id = 1
        self._next_match_id = 1
        self._next_resultat_id = 1

    # ===== Méthode principale =====

    def construire_competition(self, donnees: list[dict]) -> Competition:
        """Construit une Competition complète à partir des données nettoyées.

        Parameters
        ----------
        donnees : list[dict]
            Lignes nettoyées par DataCleaner.

        Returns
        -------
        Competition
            Competition complète avec ses participants, matchs et résultats.
        """
        # Création des entités de référence
        sport = self._construire_sport()
        saison = self._construire_saison()
        competition = Competition(
            id=1,
            nom=self.config.get("competition", "Compétition"),
            sport=sport,
            saison=saison,
            categorie=self.config.get("categorie", "Senior"),
            genre=Genre[self.config.get("genre", "MASCULIN")],
        )

        # Construction des matchs (qui inscrivent les participants)
        for ligne in donnees:
            match = self._construire_match(ligne)
            if match is not None:
                competition.ajouter_match(match)

        # Mise à jour du classement
        competition.mettre_a_jour_classement()
        return competition

    # ===== Méthodes internes =====

    def _construire_sport(self) -> Sport:
        return Sport(id=1, nom=self.config.get("sport", "Sport"))

    def _construire_saison(self) -> Saison:
        info = self.config.get("saison", {})
        return Saison(
            annee_debut=info.get("debut", 2024),
            annee_fin=info.get("fin", 2025),
        )

    def _construire_match(self, ligne: dict) -> Match | None:
        """Construit un Match à partir d'une ligne du dataset."""
        mapping = self.config["mapping"]

        # Date du match
        date_str = ligne.get(mapping["date"])
        date_match = self.cleaner.convertir_date(date_str, defaut=date.today())

        # Participants (créés ou récupérés du cache)
        nom_dom = ligne.get(mapping["participant_dom"])
        nom_ext = ligne.get(mapping["participant_ext"])
        if not nom_dom or not nom_ext:
            return None  # Ligne incomplète, on ignore

        participant_dom = self._get_or_create_participant(nom_dom)
        participant_ext = self._get_or_create_participant(nom_ext)

        # Création du match
        match = Match(
            id=self._next_match_id,
            date=date_match,
            participants=[participant_dom, participant_ext],
            statut=MatchStatus.TERMINE,
            phase=ligne.get(mapping.get("phase", ""), ""),
        )
        self._next_match_id += 1

        # Ajout des résultats
        score_dom = self.cleaner.convertir_float(ligne.get(mapping["score_dom"]))
        score_ext = self.cleaner.convertir_float(ligne.get(mapping["score_ext"]))
        type_resultat = self.config.get("type_resultat", "points")

        if score_dom is not None:
            match.ajouter_resultat(
                Resultat(
                    id=self._next_resultat_id,
                    valeur=score_dom,
                    type=type_resultat,
                    participant=participant_dom,
                )
            )
            self._next_resultat_id += 1

        if score_ext is not None:
            match.ajouter_resultat(
                Resultat(
                    id=self._next_resultat_id,
                    valeur=score_ext,
                    type=type_resultat,
                    participant=participant_ext,
                )
            )
            self._next_resultat_id += 1

        return match

    def _get_or_create_participant(self, nom: str) -> Joueur | Equipe:
        """Retourne le participant existant ou en crée un nouveau."""
        if nom in self._cache_participants:
            return self._cache_participants[nom]

        type_participant = self.config.get("type_participant", "equipe").lower()
        pays_defaut = self._get_pays_defaut()
        genre = Genre[self.config.get("genre", "MASCULIN")]

        if type_participant == "joueur":
            participant = Joueur(
                id=self._next_participant_id,
                nom=nom,
                prenom=self.config.get("prenom_defaut", "Inconnu"),
                date_naissance=date(2000, 1, 1),
                pays=pays_defaut,
                genre=genre,
            )
        else:
            participant = Equipe(
                id=self._next_participant_id,
                nom=nom,
                pays=pays_defaut,
                genre=genre,
            )

        self._next_participant_id += 1
        self._cache_participants[nom] = participant
        return participant

    def _get_pays_defaut(self) -> Pays:
        info = self.config.get("pays_defaut", {"nom": "Inconnu", "code": "XXX"})
        return Pays(nom=info["nom"], code=info["code"])

"""Interface Streamlit pour l'application de gestion de résultats sportifs.

Lancement
---------
    streamlit run src/ui/app.py
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

from src.data import RelationalMapper
from src.models import Competition, MatchStatus
from src.services import (
    ClassementService,
    RechercheService,
    StatistiquesService,
)

# ============================================================
# Configuration de la page
# ============================================================

st.set_page_config(
    page_title="Sport App — Résultats Sportifs",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# Chargement des configs et donnéces (avec cache)
# ============================================================

CONFIGS_DIR = Path("configs")


@st.cache_data
def lister_configs() -> dict:
    """Liste toutes les configs JSON disponibles."""
    configs = {}
    if not CONFIGS_DIR.exists():
        return configs
    for fichier in CONFIGS_DIR.glob("*.json"):
        with open(fichier, encoding="utf-8") as f:
            data = json.load(f)
        nom_affichage = f"{data.get('sport', '?')} — {data.get('competition', fichier.stem)}"
        configs[nom_affichage] = str(fichier)
    return configs


@st.cache_resource
def charger_competition(chemin_config: str) -> Competition:
    """Charge une compétition depuis sa config (cachée pour la performance)."""
    with open(chemin_config, encoding="utf-8") as f:
        config = json.load(f)
    mapper = RelationalMapper(config)
    return mapper.construire_competition()


def get_config(chemin_config: str) -> dict:
    """Retourne la config sans charger la compétition."""
    with open(chemin_config, encoding="utf-8") as f:
        return json.load(f)


# ============================================================
# Sidebar — sélection du sport
# ============================================================

st.sidebar.title(" Sport App")
st.sidebar.markdown("---")

configs = lister_configs()
if not configs:
    st.error("Aucune configuration trouvée dans le dossier `configs/`.")
    st.stop()

choix_competition = st.sidebar.selectbox(
    "Sélectionnez une compétition",
    options=list(configs.keys()),
)
chemin_config = configs[choix_competition]
config = get_config(chemin_config)

# Chargement (avec spinner)
with st.spinner(f"Chargement de {choix_competition}..."):
    competition = charger_competition(chemin_config)

st.sidebar.success(f" {len(competition.matchs)} matchs chargés")
st.sidebar.success(f" {len(competition.participants)} participants")

# Choix de la page
page = st.sidebar.radio(
    "Navigation",
    options=[
        "Vue d'ensemble",
        "Classement",
        "Statistiques avancées",
        "Recherche",
        "Comparaison",
        "Liste des matchs",
    ],
)


# ============================================================
# En-tête
# ============================================================

st.title(f"{competition.nom}")
st.markdown(
    f"**Sport :** {competition.sport.nom}  |  "
    f"**Saison :** {competition.saison.nom}  |  "
    f"**Catégorie :** {competition.categorie}  |  "
    f"**Genre :** {competition.genre.value}"
)
st.markdown("---")


# ============================================================
# Page : Vue d'ensemble
# ============================================================

if page == "Vue d'ensemble":
    rapport = StatistiquesService.rapport_global(competition)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Matchs joués", rapport["nb_matchs_termines"])
    col2.metric("Participants", rapport["nb_participants"])
    col3.metric(
        "Moyenne par match",
        f"{rapport['moyenne_buts_par_match']:.2f}",
        help=f"Moyenne de {config.get('type_resultat', 'points')} par match",
    )
    col4.metric("Taux de match nul", f"{rapport['taux_match_nul']:.1f}%")

    st.markdown("---")

    col_g, col_d = st.columns(2)

    with col_g:
        st.subheader("Meilleure attaque")
        type_resultat = config.get("type_resultat", "points")
        meilleur = StatistiquesService.meilleur_attaque(competition, type_resultat)
        if meilleur:
            stat = meilleur.get_stat(type_resultat)
            valeur = stat.valeur if stat else 0
            st.success(f"**{meilleur.nom}** — {valeur:.0f} {type_resultat}")

    with col_d:
        st.subheader("Meilleure défense")
        meilleure_def = StatistiquesService.meilleure_defense(
            competition, config.get("type_resultat", "points")
        )
        if meilleure_def:
            st.info(f"**{meilleure_def.nom}**")

    st.markdown("---")

    # Graphique : Top 10
    st.subheader(f"Top 10 — {config.get('type_resultat', 'points')}")
    top = StatistiquesService.top_n_buteurs(
        competition, n=10, type_resultat=config.get("type_resultat", "points")
    )
    if top:
        df_top = pd.DataFrame(
            [(p.nom, v) for p, v in top],
            columns=["Participant", config.get("type_resultat", "points").capitalize()],
        )
        st.bar_chart(
            df_top.set_index("Participant"),
            height=400,
            color="#534AB7",
        )


# ============================================================
# Page : Classement
# ============================================================

elif page == "Classement":
    st.subheader("Classement complet")

    type_classement = config.get("type_classement", "points_3_1_0")
    type_resultat = config.get("type_resultat", "points")

    # Choix du mode de classement
    mode_options = {
        "Points (3 victoire, 1 nul, 0 défaite)": "points_3_1_0",
        "Nombre de victoires": "victoires",
        f"Total {type_resultat} marqués": "score_total",
    }
    mode_label = st.radio(
        "Mode de classement",
        options=list(mode_options.keys()),
        index=list(mode_options.values()).index(type_classement)
        if type_classement in mode_options.values()
        else 0,
        horizontal=True,
    )
    mode = mode_options[mode_label]

    if mode == "points_3_1_0":
        classement = ClassementService.classement_par_points_3_1_0(competition, type_resultat)
        df = pd.DataFrame(
            [
                {
                    "Rang": i + 1,
                    "Participant": ligne["participant"].nom,
                    "Pts": ligne["points"],
                    "J": ligne["joues"],
                    "V": ligne["victoires"],
                    "N": ligne["nuls"],
                    "D": ligne["defaites"],
                    f"{type_resultat.capitalize()} +": int(ligne["marques"]),
                    f"{type_resultat.capitalize()} -": int(ligne["encaisses"]),
                    "Diff": int(ligne["difference"]),
                }
                for i, ligne in enumerate(classement)
            ]
        )
    elif mode == "victoires":
        classement = ClassementService.classement_par_victoires(competition)
        df = pd.DataFrame(
            [
                {
                    "Rang": i + 1,
                    "Participant": ligne["participant"].nom,
                    "Victoires": ligne["victoires"],
                    "Défaites": ligne["defaites"],
                    "Joués": ligne["joues"],
                    "Ratio": f"{ligne['ratio']:.1%}",
                }
                for i, ligne in enumerate(classement)
            ]
        )
    else:
        classement = ClassementService.classement_par_score_total(competition, type_resultat)
        df = pd.DataFrame(
            [
                {
                    "Rang": i + 1,
                    "Participant": ligne["participant"].nom,
                    f"Total {type_resultat}": ligne["total"],
                }
                for i, ligne in enumerate(classement)
            ]
        )

    st.dataframe(df, use_container_width=True, hide_index=True, height=600)


# ============================================================
# Page : Statistiques avancées
# ============================================================

elif page == "Statistiques avancées":
    type_resultat = config.get("type_resultat", "points")

    st.subheader("Indicateurs de performance")

    col1, col2 = st.columns(2)

    with col1:
        seuil = st.slider(
            f"Matchs avec plus de X {type_resultat} au total",
            min_value=1,
            max_value=20,
            value=5,
        )
        matchs_spec = StatistiquesService.matchs_avec_plus_de(
            competition, seuil=float(seuil), type_resultat=type_resultat
        )
        st.metric(f"Matchs spectaculaires (> {seuil})", len(matchs_spec))

    with col2:
        if matchs_spec:
            st.write("**Aperçu :**")
            for m in matchs_spec[:5]:
                noms = " vs ".join(p.nom for p in m.participants)
                total = sum(r.valeur for r in m.resultats if r.type == type_resultat)
                st.text(f"{m.date} — {noms} ({int(total)} {type_resultat})")

    st.markdown("---")

    # Distribution des scores
    st.subheader("Distribution des scores par match")
    matchs_termines = [m for m in competition.matchs if m.statut == MatchStatus.TERMINE]
    if matchs_termines:
        totaux = []
        for m in matchs_termines:
            total = sum(r.valeur for r in m.resultats if r.type == type_resultat)
            totaux.append(total)

        df_distrib = pd.DataFrame({f"Total {type_resultat}": totaux})
        st.bar_chart(
            df_distrib[f"Total {type_resultat}"].value_counts().sort_index(),
            color="#1D9E75",
        )

    st.markdown("---")

    # Statistiques globales
    st.subheader("Récapitulatif")
    rapport = StatistiquesService.rapport_global(competition)
    df_rapport = pd.DataFrame([{"Indicateur": k, "Valeur": v} for k, v in rapport.items()])
    st.table(df_rapport)


# ============================================================
# Page : Recherche
# ============================================================

elif page == "Recherche":
    st.subheader("Recherche d'un participant")

    nom_recherche = st.text_input("Nom (ou partie du nom) :", placeholder="Ex : PSG, Sinner...")

    if nom_recherche:
        resultats = RechercheService.chercher_participant_par_nom(competition, nom_recherche)

        if not resultats:
            st.warning("Aucun participant trouvé.")
        else:
            st.success(f"{len(resultats)} participant(s) trouvé(s)")

            for participant in resultats:
                with st.expander(f"{participant.nom}", expanded=True):
                    matchs_p = competition.get_matchs_participant(participant)

                    col1, col2, col3 = st.columns(3)
                    col1.metric("Matchs joués", len(matchs_p))

                    type_resultat = config.get("type_resultat", "points")
                    stat = participant.get_stat(type_resultat)
                    if stat:
                        col2.metric(type_resultat.capitalize(), f"{stat.valeur:.0f}")

                    # Compter victoires
                    victoires = sum(
                        1
                        for m in matchs_p
                        if m.statut == MatchStatus.TERMINE and m.get_vainqueur() == participant
                    )
                    col3.metric("Victoires", victoires)

                    # Liste des matchs
                    if matchs_p:
                        df_matchs = pd.DataFrame(
                            [
                                {
                                    "Date": m.date,
                                    "Adversaire": [
                                        p.nom for p in m.participants if p != participant
                                    ][0],
                                    "Score": m.get_score_participant(participant),
                                    "Score adv.": sum(
                                        m.get_score_participant(p)
                                        for p in m.participants
                                        if p != participant
                                    ),
                                    "Phase": m.phase or "—",
                                }
                                for m in matchs_p[:50]
                            ]
                        )
                        st.dataframe(df_matchs, use_container_width=True, hide_index=True)


# ============================================================
# Page : Comparaison
# ============================================================

elif page == "Comparaison":
    st.subheader("Comparer deux participants")

    noms_participants = sorted([p.nom for p in competition.participants])

    col1, col2 = st.columns(2)
    with col1:
        nom_a = st.selectbox("Participant A", options=noms_participants, key="a")
    with col2:
        nom_b = st.selectbox(
            "Participant B",
            options=noms_participants,
            index=min(1, len(noms_participants) - 1),
            key="b",
        )

    if nom_a == nom_b:
        st.warning("Choisissez deux participants différents.")
    else:
        p_a = next(p for p in competition.participants if p.nom == nom_a)
        p_b = next(p for p in competition.participants if p.nom == nom_b)

        type_resultat = config.get("type_resultat", "points")

        # Stats individuelles
        col_a, col_b = st.columns(2)
        for col, p in [(col_a, p_a), (col_b, p_b)]:
            with col:
                st.markdown(f"### {p.nom}")
                matchs = competition.get_matchs_participant(p)
                victoires = sum(
                    1 for m in matchs if m.statut == MatchStatus.TERMINE and m.get_vainqueur() == p
                )
                stat = p.get_stat(type_resultat)
                valeur = stat.valeur if stat else 0
                st.metric("Matchs", len(matchs))
                st.metric("Victoires", victoires)
                st.metric(type_resultat.capitalize(), f"{valeur:.0f}")

        st.markdown("---")

        # Confrontations directes
        st.subheader("Confrontations directes")
        confrontations = RechercheService.confrontation_directe(competition, p_a, p_b)

        if not confrontations:
            st.info("Aucune confrontation directe trouvée.")
        else:
            v_a = sum(1 for m in confrontations if m.get_vainqueur() == p_a)
            v_b = sum(1 for m in confrontations if m.get_vainqueur() == p_b)
            nuls = sum(1 for m in confrontations if m.est_nul())

            col1, col2, col3 = st.columns(3)
            col1.metric(f"Victoires {p_a.nom}", v_a)
            col2.metric("Nuls", nuls)
            col3.metric(f"Victoires {p_b.nom}", v_b)

            df_conf = pd.DataFrame(
                [
                    {
                        "Date": m.date,
                        f"{p_a.nom}": m.get_score_participant(p_a),
                        f"{p_b.nom}": m.get_score_participant(p_b),
                        "Vainqueur": m.get_vainqueur().nom if m.get_vainqueur() else "Nul",
                        "Phase": m.phase or "—",
                    }
                    for m in confrontations
                ]
            )
            st.dataframe(df_conf, use_container_width=True, hide_index=True)


# ============================================================
# Page : Liste des matchs
# ============================================================

elif page == "Liste des matchs":
    st.subheader("Tous les matchs")

    # Filtres
    col1, col2 = st.columns(2)
    with col1:
        phases = sorted({m.phase for m in competition.matchs if m.phase})
        phase_filtre = st.selectbox("Filtrer par phase", options=["Toutes"] + phases)
    with col2:
        nb_max = st.number_input(
            "Nombre maximum à afficher", min_value=10, max_value=2000, value=100
        )

    matchs = competition.matchs
    if phase_filtre != "Toutes":
        matchs = [m for m in matchs if m.phase == phase_filtre]

    df_matchs = pd.DataFrame(
        [
            {
                "Date": m.date,
                "Phase": m.phase or "—",
                "Domicile": m.participants[0].nom,
                "Score": f"{int(m.get_score_participant(m.participants[0]))} - "
                f"{int(m.get_score_participant(m.participants[1]))}",
                "Extérieur": m.participants[1].nom,
                "Statut": m.statut.value,
            }
            for m in matchs[: int(nb_max)]
        ]
    )
    st.dataframe(df_matchs, use_container_width=True, hide_index=True, height=600)


# ============================================================
# Footer
# ============================================================

st.sidebar.markdown("---")
st.sidebar.caption("Projet ENSAI 2025/2026")

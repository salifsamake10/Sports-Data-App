"""Fixtures pytest partagées entre tous les tests."""

from datetime import date

import pytest

from src.models import (
    Coach,
    Competition,
    Equipe,
    Genre,
    Joueur,
    Match,
    MatchStatus,
    Pays,
    Saison,
    Sport,
)


@pytest.fixture
def france() -> Pays:
    return Pays(nom="France", code="FRA")


@pytest.fixture
def espagne() -> Pays:
    return Pays(nom="Espagne", code="ESP")


@pytest.fixture
def football() -> Sport:
    return Sport(id=1, nom="Football")


@pytest.fixture
def saison_2023() -> Saison:
    return Saison(annee_debut=2023, annee_fin=2024)


@pytest.fixture
def joueur_messi(espagne: Pays) -> Joueur:
    return Joueur(
        id=1,
        nom="Messi",
        prenom="Lionel",
        date_naissance=date(1987, 6, 24),
        pays=espagne,
        genre=Genre.MASCULIN,
    )


@pytest.fixture
def joueur_ronaldo(france: Pays) -> Joueur:
    return Joueur(
        id=2,
        nom="Ronaldo",
        prenom="Cristiano",
        date_naissance=date(1985, 2, 5),
        pays=france,
        genre=Genre.MASCULIN,
    )


@pytest.fixture
def equipe_psg(france: Pays) -> Equipe:
    return Equipe(id=10, nom="PSG", pays=france, genre=Genre.MASCULIN)


@pytest.fixture
def equipe_om(france: Pays) -> Equipe:
    return Equipe(id=11, nom="OM", pays=france, genre=Genre.MASCULIN)


@pytest.fixture
def coach_deschamps(france: Pays) -> Coach:
    return Coach(
        nom="Deschamps",
        prenom="Didier",
        date_naissance=date(1968, 10, 15),
        nationalite=france,
        experience=12,
    )


@pytest.fixture
def match_psg_om(equipe_psg: Equipe, equipe_om: Equipe) -> Match:
    return Match(
        id=100,
        date=date(2024, 3, 15),
        participants=[equipe_psg, equipe_om],
        statut=MatchStatus.PLANIFIE,
        phase="Journée 27",
    )


@pytest.fixture
def competition_ligue1(football: Sport, saison_2023: Saison) -> Competition:
    return Competition(
        id=1,
        nom="Ligue 1",
        sport=football,
        saison=saison_2023,
        categorie="Senior",
        genre=Genre.MASCULIN,
    )

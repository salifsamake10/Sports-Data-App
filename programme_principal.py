from chargeurs.chargeur_football import ChargeurFootball

if __name__ == "__main__":
    chargeur = ChargeurFootball("donnees/")

    # Chargement des données
    pays = chargeur.charger_pays()
    competitions = chargeur.charger_competitions(pays)
    equipes = chargeur.charger_equipes()
    joueurs = chargeur.charger_joueurs()
    matchs = chargeur.charger_matchs(competitions, equipes)

    print("=== Chargement terminé ===")
    print(f"Pays chargés : {len(pays)}")
    print(f"Compétitions chargées : {len(competitions)}")
    print(f"Équipes chargées : {len(equipes)}")
    print(f"Joueurs chargés : {len(joueurs)}")
    print(f"Matchs chargés : {len(matchs)}")

from chargeurs.chargeur_football import ChargeurFootball

if __name__ == "__main__":
    chargeur = ChargeurFootball("donnees/")

    pays = chargeur.charger_pays()
    competitions = chargeur.charger_competitions(pays)
    equipes = chargeur.charger_equipes()
    joueurs = chargeur.charger_joueurs()
    matchs = chargeur.charger_matchs(competitions, equipes)

    print("Chargement terminé.")
    print(f"{len(matchs)} matchs chargés.")

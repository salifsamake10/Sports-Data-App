class Coach:
    def __init__(self, nom: str, nationalite: str = None, date_naissance=None, experience: int = None):
        self.nom = nom
        self.nationalite = nationalite
        self.date_naissance = date_naissance
        self.experience = experience

    def __str__(self):
        return f"Coach {self.nom}"

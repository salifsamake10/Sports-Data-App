class Pays:
    def __init__(self, nom: str, code: str = None):
        self.nom = nom
        self.code = code

    def __str__(self):
        return f"{self.nom} ({self.code})" if self.code else self.nom
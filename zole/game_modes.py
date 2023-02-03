class GameMode:
    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return self.name


class GameMode:
    NOTSET = GameMode('Not set')
    PASS = GameMode('Garām')
    PACELT = GameMode('Pacelt')
    ZOLE = GameMode('Zole')
    GALDINS = GameMode('Galdiņš')
    MAZAZOLE = GameMode("Mazā zole")

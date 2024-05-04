class Effect:
    def __init__(self, name:str, level:int = 1, turns:int = 0):
        self.name:str = name
        self.level:int = level
        self.truns:int = turns

    def next_trun(self):
        self.truns -= 1

        if self.truns <= 0:
            print(f"El efecto {self.name} ha terminado")
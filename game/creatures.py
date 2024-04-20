import math

class Mob:
    def __init__(self, name:str = "mob", health:int = 10, defense:float = 0, strength:int = 1):
        self.__name:str = name
        self.__health:int = health
        self.__defense:float = defense
        self.__strength:int = strength

        self.__alive:bool = True

    def get_name(self) -> str:
        return self.__name
    
    def get_health(self) -> int:
        return self.__health
    
    def get_defense(self) -> float:
        return self.__defense
    
    def get_strength(self) -> int:
        return self.__strength
    
    def get_alive(self) -> bool:
        return self.__alive
    
    def attack(self, mob) -> int:
        if not self.__alive:
            raise Exception(f"Mob->{self.__name} No puede atacar porque esta muerto")
        
        damage:int = math.ceil((1 - mob.__defense) * self.__strength)
        mob.__health -= damage

        if mob.__alive and mob.__health <= 0:
            mob.__dead(self.__name)

        if mob.__health < 0:
            mob.__health = 0

        return damage
    
    def __dead(self, reason:str):
        self.__health = 0
        self.__alive = False
        print(f"{self.__name} Murió por: {reason}")

    def kill(self):
        self.__dead("kill")

    def show_stats(self):
        print(f"Nombre: {self.__name}")
        print(f"Vida: {self.__health}")
        print(f"Defensa: {self.__defense}")
        print(f"Fuerza: {self.__strength}")
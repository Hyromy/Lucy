import math, random

class Mob:
    def __init__(self, name:str = "mob", health:int = 10, defense:float = 0, strength:int = 1):
        self.name:str = name
        self.health:int = health
        self.defense:float = defense
        self.strength:int = strength

        self.alive:bool = True
        self.effects = []

    def attack(self, mob) -> int:
        if not self.alive:
            raise Exception(f"Mob->{self.name} No puede atacar porque esta muerto")
        
        damage:int = math.ceil((1 - mob.defense) * self.strength)
        mob.health -= damage

        if mob.alive and mob.health <= 0:
            mob.dead(self.name)

        if mob.health < 0:
            mob.health = 0

        return damage
    
    def dead(self, reason:str):
        self.health = 0
        self.alive = False
        print(f"{self.name} Murió por: {reason}")

    def show_stats(self):
        print(f"Nombre: {self.name}")
        print(f"Vida: {self.health}")
        print(f"Defensa: {self.defense}")
        print(f"Fuerza: {self.strength}")

    def apply_effect(self, effect, mob, rate:float) -> bool:
        if rate >= random.random():
            mob.effects.append(effect)

            return True
        return False
#начало начал
class Person:
    def __init__(self, name="", health=0, mana=0):
        self.name = name
        self.health = health
        self.mana = mana
    def status(self):
        return f"{self.name} health: {self.health} mana: {self.mana}"
    def drink_heal_potion(self, potion_amount):
        self.health += potion_amount
    def	drink_mana_potion(self, potion_amount):
        self.mana += potion_amount
#не ну это наш гг
class protagonist(Person):
    def __init__(self, name, health=0, mana=0, strength=0, agility=0, intellect=0, experience=0, level=0):
        super().__init__(name, health, mana)
        self.strength = strength
        self.agility = agility
        self.intellect = intellect
        self.experience = experience
        self.level = level
    def scream(self):
        return f"Я будущий герой {self.name}, но я не выбрал специальность."
    def	attack(self, target, damage):
        return f"Я будущий герой {self.name}, и я без оружия, но я нанес {target} урон {damage} своими руками."
#дальше идёт класс воина
class warrior(protagonist):
    def __init__(self, name="", health=100, mana=100, strenth=1, agility=1, intellect=1, experience=0, level=1, weapon=None):
        super().__init__(name, health, mana, strenth, agility, intellect, experience, level)
        self.atWeaponOBJ = weapon


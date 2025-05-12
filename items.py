# Модуль предметов для RPG

class Item:
    def __init__(self, name, description=None):
        self.name = name
        self.description = description or ""

    def use(self, target):
        return f"{self.name} не может быть использован напрямую."

class Weapon(Item):
    def __init__(self, name, power, description=None):
        super().__init__(name, description)
        self.power = power

    def use(self, target):
        return f"{target.name} использует {self.name} с силой {self.power}."

class Potion(Item):
    def __init__(self, name, heal_power, description=None):
        super().__init__(name, description)
        self.heal_power = heal_power

    def use(self, target):
        target.drink_heal_potion(self.heal_power)
        return f"{target.name} выпил {self.name} и восстановил {self.heal_power} здоровья."

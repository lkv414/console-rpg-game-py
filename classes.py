# начало начал
class Person:
    def __init__(self, name="", health=0, mana=0):
        self.name = name
        self.health = health
        self.mana = mana

    def status(self):
        return f"{self.name} health: {self.health} mana: {self.mana}"

    def drink_heal_potion(self, potion_amount):
        self.health += potion_amount

    def drink_mana_potion(self, potion_amount):
        self.mana += potion_amount


# не ну это наш гг
class Protagonist(Person):
    def __init__(self, name, health=0, mana=0, strength=0, agility=0, intellect=0, experience=0, level=0):
        super().__init__(name, health, mana)
        self.strength = strength
        self.agility = agility
        self.intellect = intellect
        self.experience = experience
        self.level = level

    def scream(self):
        return f"Я будущий герой {self.name}, но я не выбрал специальность."

    def attack(self, target, damage):
        return f"Я будущий герой {self.name}, и я без оружия, но я нанес {target} урон {damage} своими руками."


# дальше идёт класс воина
class Warrior(Protagonist):
    def __init__(self, name="", health=100, mana=100, strength=1, agility=1, intellect=1, experience=0, level=1,
                 weapon=None):
        super().__init__(name, health, mana, strength, agility, intellect, experience, level)
        self.weapon = weapon

    def scream(self):
        weapon_name = self.weapon if self.weapon else "без оружия"
        return f"Я герой {self.name}, и я воин с {weapon_name}."

    def attack(self, target, damage):
        self.experience += 10
        if self.experience >= 100:
            self.level += 1
            self.strength += 3
            self.agility += 2
            self.intellect += 1
            self.experience = 0
        weapon_name = self.weapon if self.weapon else "кулаками"
        return f"{self.name} нанес с помощью {weapon_name} по {target} урон {damage}."


# класс мага
class Mage(Protagonist):
    def __init__(self, name="", health=100, mana=100, strength=1, agility=1, intellect=1, experience=0, level=1,
                 spells=None):
        super().__init__(name, health, mana, strength, agility, intellect, experience, level)
        self.spells = spells or []

    def scream(self):
        return f"Я маг-герой {self.name}, и я знаю {len(self.spells)} заклинаний."

    def add_magic(self, spell):
        self.spells.append(spell)

    def cast_spell(self, spell, target, damage):
        self.experience += 10
        if self.experience >= 100:
            self.level += 1
            self.strength += 1
            self.agility += 2
            self.intellect += 4
            self.experience = 0
        return f"{self.name} нанес заклинанием {spell} по {target} урон {damage}."


# класс лучника
class Archer(Protagonist):
    def __init__(self, name="", health=100, mana=100, strength=1, agility=1, intellect=1, experience=0, level=1,
                 weapon="bow"):
        super().__init__(name, health, mana, strength, agility, intellect, experience, level)
        self.weapon = weapon

    def attack(self, target, damage):
        self.experience += 10
        if self.experience >= 100:
            self.level += 1
            self.strength += 2
            self.agility += 3
            self.intellect += 1
            self.experience = 0
        return f"{self.name} выпустила стрелу из {self.weapon} по {target} урон {damage}."

    def scream(self):
        return f"Я лучница {self.name}, и мой лук — {self.weapon}."


# нпс
class NPC(Person):
    def __init__(self, name="", health=100, mana=100, level=1):
        super().__init__(name, health, mana)
        self.level = level
        self.items = []

    def scream(self):
        return f"Я {self.name}, обычный NPC!"


# класс травника
class Herbalist(NPC):
    def __init__(self, name="", health=100, mana=100, level=1, items=None):
        super().__init__(name, health, mana, level)
        self.items = items if items is not None else []
        self.profession = "Травник"

    def scream(self):
        return f"Я {self.name}, обычный {self.profession}!"

    def make_potion(self, potion_name, heal_power):
        potion = Potion(potion_name, heal_power)
        self.items.append(potion)
        return f"Зелье {potion_name} с лечебной силой {heal_power} создано и добавлено в инвентарь!"

    def job(self, target, potion_name):
        for potion in self.items:
            if potion.name == potion_name:
                target.drink_heal_potion(potion.heal_power)
                self.items.remove(potion)
                return f"{self.name} передал зелье {potion_name} для {target.name}. {target.name} восстановил {potion.heal_power} здоровья!"
        return f"Зелье {potion_name} не найдено в инвентаре {self.name}!"


# класс кузнеца
class Blacksmith(NPC):
    def __init__(self, name="", health=100, mana=100, level=1, items=None):
        super().__init__(name, health, mana, level)
        self.items = items if items is not None else []
        self.profession = "Кузнец"

    def scream(self):
        return f"Я {self.name}, обычный {self.profession}!"

    def forge_item(self, item_name, item_power):
        item = Weapon(item_name, item_power)
        self.items.append(item)
        return f"Предмет {item_name} с силой {item_power} выкован и добавлен в инвентарь!"

    def give_item(self, target, item_name):
        for item in self.items:
            if item.name == item_name:
                if hasattr(target, "weapon"):
                    target.weapon = item.name
                    self.items.remove(item)
                    return f"{self.name} передал {item_name} для {target.name}. Теперь у {target.name} новое оружие: {item_name} с силой {item.power}!"
                elif hasattr(target, "items"):
                    target.items.append(item)
                    self.items.remove(item)
                    return f"{self.name} передал {item_name} для {target.name}. Предмет добавлен в инвентарь {target.name}!"
                else:
                    return f"{target.name} не может принять предмет {item_name}!"
        return f"Предмет {item_name} не найден в инвентаре {self.name}!"


# класс торговца
class Trader(NPC):
    def __init__(self, name="", health=100, mana=100, level=1, items=None):
        super().__init__(name, health, mana, level)
        self.items = items if items is not None else []
        self.profession = "Торговец"

    def scream(self):
        return f"Добро пожаловать! Я {self.name}, местный {self.profession}."

    def add_item(self, item):
        self.items.append(item)
        return f"Предмет {item.name} добавлен в инвентарь {self.name}!"

    def sell_item(self, target, item_name, price):
        for item in self.items:
            if item.name == item_name:
                if hasattr(target, "weapon"):
                    target.weapon = item.name
                    self.items.remove(item)
                    return f"{self.name} продал {item_name} для {target.name} за {price} монет. Теперь у {target.name} новое оружие: {item_name}!"
                elif hasattr(target, "items"):
                    target.items.append(item)
                    self.items.remove(item)
                    return f"{self.name} продал {item_name} для {target.name} за {price} монет. Предмет добавлен в инвентарь {target.name}!"
                else:
                    return f"{target.name} не может принять предмет {item_name}!"
        return f"Предмет {item_name} не найден в инвентаре {self.name}!"


# класс странствующего волшебника
class WanderingWizard(NPC):
    def __init__(self, name="", health=100, mana=100, level=1, items=None):
        super().__init__(name, health, mana, level)
        self.items = items if items is not None else []
        self.profession = "Странствующий Волшебник"

    def scream(self):
        return f"Я {self.name}, {self.profession}, могу поделиться знаниями."

    def teach_spell(self, target, spell_name):
        if hasattr(target, "spells"):
            target.spells.append(spell_name)
            return f"{self.name} научил {target.name} заклинанию {spell_name}!"
        return f"{target.name} не может выучить заклинание {spell_name}!"


# классы предметов
class Weapon:
    def __init__(self, name, power):
        self.name = name
        self.power = power

    def use(self):
        return f"Использовано оружие {self.name} с силой {self.power}!"


class Armor:
    def __init__(self, name, defense):
        self.name = name
        self.defense = defense

    def use(self):
        return f"Надеты доспехи {self.name} с защитой {self.defense}!"


class Potion:
    def __init__(self, name, heal_power):
        self.name = name
        self.heal_power = heal_power

    def use(self, target):
        target.drink_heal_potion(self.heal_power)
        return f"Зелье {self.name} использовано! {target.name} восстановил {self.heal_power} здоровья."
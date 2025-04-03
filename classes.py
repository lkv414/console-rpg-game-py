# начало начал
import random
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
        self.money = 0  # Добавляем деньги
        self.health_potions = []  # Список зелий здоровья
        self.mana_potions = []  # Список зелий маны

    def scream(self):
        return f"Я будущий герой {self.name}, но я не выбрал специальность."

    def attack(self, target, damage):
        return f"Я будущий герой {self.name}, и я без оружия, но я нанес {target} урон {damage} своими руками."

    def use_health_potion(self):
        if self.health_potions:
            potion = self.health_potions.pop(0)  # Удаляем и получаем первое зелье
            self.drink_heal_potion(potion.heal_power)
            return f"{self.name} использовал зелье здоровья и восстановил {potion.heal_power} HP. Осталось зелий: {len(self.health_potions)}."
        return f"У {self.name} нет зелий здоровья!"

    def use_mana_potion(self):
        if self.mana_potions:
            potion = self.mana_potions.pop(0)  # Удаляем и получаем первое зелье
            self.drink_mana_potion(potion.heal_power)
            return f"{self.name} использовал зелье маны и восстановил {potion.heal_power} маны. Осталось зелий: {len(self.mana_potions)}."
        return f"У {self.name} нет зелий маны!"


# дальше идёт класс воина
class Warrior(Protagonist):
    def __init__(self, name="", health=100, mana=100, strength=1, agility=1, intellect=1, experience=0, level=1, weapon=None):
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
        # Урон увеличивается за счёт strength
        total_damage = damage + self.strength
        weapon_name = self.weapon if self.weapon else "кулаками"
        return f"{self.name} нанес с помощью {weapon_name} по {target} урон {total_damage}."


# класс мага
class Mage(Protagonist):
    def __init__(self, name="", health=100, mana=100, strength=1, agility=1, intellect=1, experience=0, level=1, spells=None):
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
        # Урон увеличивается за счёт intellect
        total_damage = damage + self.intellect * 2
        return f"{self.name} нанес заклинанием {spell} по {target} урон {total_damage}."


# класс лучника
class Archer(Protagonist):
    def __init__(self, name="", health=100, mana=100, strength=1, agility=1, intellect=1, experience=0, level=1, weapon="bow"):
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
        # Урон увеличивается за счёт agility
        total_damage = damage + self.agility
        return f"{self.name} выпустил стрелу из {self.weapon} по {target} урон {total_damage}."

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
    def __init__(self, name="Травник Василий", health=100, mana=100, level=1, items=None):
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
    def __init__(self, name="Кузнец Иван", health=100, mana=100, level=1, items=None):
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

    def sell_weapon(self, target, weapon_name, price):
        weapon = Weapon(weapon_name, 10)  # Меч с фиксированной силой 10
        if target.money >= price:
            target.money -= price
            target.weapon = weapon.name
            return f"{self.name} продал {weapon_name} для {target.name} за {price} монет. Теперь у {target.name} новое оружие: {weapon_name}!"
        else:
            return f"У {target.name} недостаточно денег для покупки {weapon_name}!"


# класс торговца
class Trader(NPC):
    def __init__(self, name="Торговец Фёдор", health=100, mana=100, level=1, items=None):
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
                if target.money >= price:
                    target.money -= price
                    if isinstance(item, Potion):
                        if "Health" in item.name:
                            target.health_potions.append(item)
                        elif "Mana" in item.name:
                            target.mana_potions.append(item)
                    else:
                        if hasattr(target, "weapon"):
                            target.weapon = item.name
                        elif hasattr(target, "items"):
                            target.items.append(item)
                    self.items.remove(item)
                    return f"{self.name} продал {item_name} для {target.name} за {price} монет."
                else:
                    return f"У {target.name} недостаточно денег для покупки {item_name}!"
        return f"Предмет {item_name} не найден в инвентаре {self.name}!"


# класс странствующего волшебника
class WanderingWizard(NPC):
    def __init__(self, name="Волшебник Мирон", health=100, mana=100, level=1, items=None):
        super().__init__(name, health, mana, level)
        self.items = items if items is not None else []
        self.profession = "Странствующий Волшебник"

    def scream(self):
        return f"Я {self.name}, {self.profession}, могу поделиться знаниями."

    def teach_spell(self, target, spell_name):
        if hasattr(target, "spells"):
            target.spells.append(spell_name)
            return f"{self.name} научил {target.name} заклинанию {spell_name}!"

    def sell_spell(self, target, spell_name, price):
        if target.money >= price:
            target.money -= price
            if hasattr(target, "spells"):
                target.spells.append(spell_name)
                return f"{self.name} продал заклинание {spell_name} для {target.name} за {price} монет."
            else:
                return f"{target.name} не может выучить заклинание {spell_name}!"
        else:
            return f"У {target.name} недостаточно денег для покупки заклинания {spell_name}!"


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


# враги
class Enemy(Person):
    def __init__(self, name="", health=100, mana=100, level=1, items=None):
        super().__init__(name, health, mana)
        self.level = level
        self.items = items if items is not None else []

    def attack(self, target, damage, dodge_chance):
        # Проверяем, уклоняется ли цель
        if random.randint(1, 100) <= dodge_chance:
            return f"{self.name} атаковал {target.name}, но промахнулся!"
        target.health -= damage
        return f"{self.name} атаковал {target.name}, нанеся {damage} урона."

    def __str__(self):
        return f"{self.name} (уровень: {self.level}, здоровье: {self.health}, мана: {self.mana})"


class Imp(Enemy):
    def __init__(self, name="Бес", health=80, mana=150, level=1, items=None):
        super().__init__(name, health, mana, level, items)

    def steal_mana(self, target):
        stolen_mana = min(20, target.mana)
        target.mana -= stolen_mana
        self.mana += stolen_mana
        return f"{self.name} украл {stolen_mana} маны у {target.name}!"


class Necromancer(Enemy):
    def __init__(self, name="Некромант", health=90, mana=120, level=2, items=None):
        super().__init__(name, health, mana, level, items)

    def raise_dead(self):
        return f"{self.name} поднял скелета из мёртвых для боя!"

    def curse(self, target, damage):
        return f"{self.name} наложил проклятие на {target.name}, нанеся {damage} урона и снизив силу!"


class Boss(Imp):
    def __init__(self, name="Король Бесов", health=300, mana=200, level=5, items=None):
        super().__init__(name, health, mana, level, items)

    def summon_minions(self):
        return f"{self.name} призвал двух младших бесов для помощи в бою!"

    def dark_pulse(self, target, damage):
        total_damage = damage + self.level * 5
        return f"{self.name} выпустил темный импульс, нанеся {total_damage} урона {target.name}!"

    def __str__(self):
        return f"БОСС: {self.name} (уровень: {self.level}, здоровье: {self.health}, мана: {self.mana})"
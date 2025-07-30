from abc import ABC, abstractmethod
from dataclasses import dataclass
from random import randint
from rich import print


class Entity(ABC):
    @abstractmethod
    def take_damage(self, damage: float):
        raise NotImplementedError

    @abstractmethod
    def take_health(self, health: float):
        raise NotImplementedError


class Item(ABC):
    @abstractmethod
    def get_brokenness_state(self):
        raise NotImplementedError

    @abstractmethod
    def use(self):
        raise NotImplementedError

    @abstractmethod
    def repair(self):
        raise NotImplementedError


class Weapon(Item):
    def __init__(
        self,
        name: str,
        damage: int,
        level: int = 1,
        initial_brokenness=0.0,
        breaking_value: float = 1.0,
    ):
        self.name = name
        self.initial_brokenness = initial_brokenness
        self.breaking_value = breaking_value
        self.level = level

        if self.level == 1:
            self.name = f"Поломанный {self.name}"
        elif self.level == 2:
            self.name = f"Ржавый {self.name}"
        elif self.level == 3:
            self.name = f"Старый {self.name}"
        elif self.level == 4:
            self.name = f"Обычный {self.name}"
        elif self.level == 5:
            self.name = f"Редкий {self.name}"
        elif self.level == 6:
            self.name = f"Хороший {self.name}"
        elif self.level == 7:
            self.name = f"Отличный {self.name}"
        elif self.level == 8:
            self.name = f"Мифический {self.name}"
        elif self.level == 9:
            self.name = f"Легендарный {self.name}"

        try:
            self.damage = (
                max([1, round(damage * level / (self.initial_brokenness / 10), 2)]) * 2
            )
        except ZeroDivisionError:
            self.damage = 1

        self.name = f"{self.name} ({self.get_brokenness_state()})"

    def get_brokenness_state(self):
        state = "Идеал"

        if self.initial_brokenness >= 10.0 and self.initial_brokenness <= 25.0:
            state = "Как новый"
        elif self.initial_brokenness >= 25.0 and self.initial_brokenness <= 50.0:
            state = "Б/У"
        elif self.initial_brokenness >= 50.0 and self.initial_brokenness <= 75.0:
            state = "Старый"
        elif self.initial_brokenness >= 75.0 and self.initial_brokenness <= 90.0:
            state = "Разваливающийся"
        elif self.initial_brokenness > 90.0:
            state = "Сломанный"

        if self.initial_brokenness == 0.0:
            state = "Идеал"

        return state

    def use(self):
        self.initial_brokenness -= self.breaking_value

        try:
            self.damage = max(
                [1, self.damage * self.level // (self.initial_brokenness // 10)]
            )
        except ZeroDivisionError:
            self.damage = 1

    def repair(self):
        self.damage = self.damage * (self.initial_brokenness / 10)
        self.initial_brokenness = 0.0
        self.name = " ".join(self.name.split(' ')[1:])
        self.name = f"{self.name} ({self.get_brokenness_state()})"


@dataclass
class AttackSpell:
    spell_name: str
    spell_desc: str
    mana_cost: float
    spell_damage: float
    negative_effect: str = None
    spell_type: str = "ATTACK"


@dataclass
class HealthSpell:
    spell_name: str
    spell_desc: str
    mana_cost: float
    healing: float
    spell_type: str = "HEALTH"


@dataclass
class ManaSpell:
    spell_name: str
    spell_desc: str
    mana: float
    spell_type: str = "MANA"
    mana_cost: float = 0.0


class Enemy(Entity):
    def __init__(self, multiplier, player, name: str, danger_level: int):
        self.danger_level = danger_level
        self.player = player
        self.name = name
        if self.danger_level == 2:
            self.name = f"Злой {self.name}"
        elif self.danger_level == 3:
            self.name = f"Гига{self.name.lower()}"
        elif self.danger_level == 4:
            self.name = f"Кровавый {self.name}"
        elif self.danger_level == 5:
            self.name = f"Темный {self.name}"
        elif self.danger_level == 6:
            self.name = f"Чернолорд {self.name}"
        elif self.danger_level == 7:
            self.name = f"Лич {self.name}"
        elif self.danger_level == 8:
            self.name = f"Владыка личей {self.name}"
        elif self.danger_level == 9:
            self.name = f"Архилич {self.name}"
        elif self.danger_level == 10:
            self.name == f"Владыка архиличей {self.name}"
        elif self.danger_level == 11:
            self.name = f"Владыка хаоса {self.name}"

        self.hp = (randint(10, 100) * self.player.lvl * self.danger_level) * multiplier
        self.damage = (
            randint(1, 10) * self.player.lvl * self.danger_level
        ) * multiplier

        self.negative_effects = {}

    def apply_negative_effect(self, effect_name: str, effect_damage: str):
        self.negative_effects[f"{effect_name}@{len(self.negative_effects)}"] = (
            effect_damage
        )

    @property
    def damage_attack(self):
        self.damage = randint(1, 10) * self.player.lvl * self.danger_level
        return self.damage

    def take_damage(self, damage: float):
        self.hp -= damage
        self.hp = round(self.hp, 2)

    def take_health(self, health: float):
        self.hp += health
        self.hp = round(self.hp, 2)


@dataclass
class PassiveAbility:
    name: str
    desc: str
    param: str
    value: any


class Player(Entity):
    def __init__(
        self,
        name: str,
        race: str,
        initial_hp: float = 100.0,
        initial_weapon: Weapon = Weapon("Медный кинжал", 10, initial_brokenness=50.0),
    ):
        self.initial_weapon = initial_weapon
        self.name = name
        self.lvl = 1
        self.xp = 0
        self.hp = initial_hp
        self.race = race.lower()

        self.passive_abilities = []

        self.power = randint(3, 10) + 3 if self.race == "орк" else randint(1, 10)
        self.agility = randint(3, 10) + 3 if self.race == "хоббит" else randint(1, 10)
        self.wisdom = randint(3, 10) + 3 if self.race == "эльф" else randint(1, 10)

        if self.race == "человек":
            self.power = randint(2, 10) + 1
            self.agility = randint(2, 10) + 1
            self.wisdom = randint(2, 10) + 1
            self.passive_abilities.append(
                PassiveAbility(
                    name="Универсал",
                    desc="Каждый гейм-мув вы получаете дополнительную ману, монеты или XP.",
                    param="random_additional_param",
                    value=15,
                )
            )
        elif self.race == "хоббит":
            self.money = 10 * self.agility
            self.passive_abilities.append(
                PassiveAbility(
                    name="Скидка",
                    desc="Хоббиты обожают деньги и всегда могут получить скидку (25%).",
                    param="discount",
                    value=25,
                )
            )
        elif self.race == "орк":
            self.passive_abilities.append(
                PassiveAbility(
                    name="Стойкость",
                    desc=f"Орочье наследие сделало вас невероятно стойким. Вы можете уходить в минус на {50 * self.lvl}HP.",
                    param="health_fortitude",
                    value=50,
                )
            )
            self.initial_weapon.damage *= 2
            self.hp *= 2
        elif self.race == "эльф":
            self.passive_abilities.append(
                PassiveAbility(
                    name="Мания маны",
                    desc="Эльфийская душа позволяет вам получить ману за убийство врага.",
                    param="mana_loot",
                    value=2,
                )
            )

        self.money = 2 * self.agility * self.lvl * 2
        self.damage = self.power + self.initial_weapon.damage
        self.mana = 10 * self.wisdom

        self.calc_additional_params()

        self.negative_effects = {}

        self.inventory = {}
        self.spells = {
            "ФАЕРБОЛЛ": AttackSpell(
                spell_name="Фаерболл",
                spell_desc="Наносит огромный урон, но требует большой сосредоточенности",
                mana_cost=100.0 * self.lvl,
                spell_damage=100.0 * self.lvl,
            ),
            "ЗЛАЯ НАСМЕШКА": AttackSpell(
                spell_name="Злая насмешка",
                spell_desc="Унижает вашего врага. Настолько, что он кричит от боли",
                mana_cost=10.0 * self.lvl,
                spell_damage=10.0 * self.lvl,
            ),
            "ЗВОН КЛАДБИЩА": AttackSpell(
                negative_effect="necromancy",
                spell_name="Звон кладбища",
                spell_desc="Темное заклинание некромантов. Высасывает силы из существа, пока оно не иссхонет.",
                mana_cost=70.0 * self.lvl,
                spell_damage=5.0 * self.lvl,
            ),
            "ЯДОВИТЫЙ ДЫМ": AttackSpell(
                negative_effect="poison",
                spell_name="Ядовитый дым",
                spell_desc="Дешевое заклинание, наносит мало урона, но с каждым ходом урон удваивается из-за эффекта отравления.",
                mana_cost=10.0 * self.lvl,
                spell_damage=0.5 * self.lvl,
            ),
            "МАГИЧЕСКАЯ СТРЕЛА": AttackSpell(
                spell_name="Магическая стрела",
                spell_desc="Обычное заклинание, наносит немного урона, зато пробивает броню",
                mana_cost=25.0 * self.lvl,
                spell_damage=20.0 * self.lvl,
            ),
            "ПРЕВОЗМОГАНИЕ": HealthSpell(
                spell_name="Превозмогание",
                spell_desc="Вы собираете свои силы и превозмогаете любую боль",
                mana_cost=15.0 * self.lvl,
                healing=20.0 * self.lvl,
            ),
            "ЯД ДРАКОНОВ": AttackSpell(
                negative_effect="poison",
                spell_name="Яд драконов",
                spell_desc="Дорогое заклинание, наносит меньше урона чем боевые, но с каждым ходом урон удваивается из-за эффекта отравления.",
                mana_cost=100.0 * self.lvl,
                spell_damage=5.0 * self.lvl,
            ),
            "ВЕЛИКОЕ ПРЕВОЗМОГАНИЕ": HealthSpell(
                spell_name="Великое превозмогание",
                spell_desc="Теперь вы можете стерпеть любую боль, любая рана для вас синяк",
                mana_cost=150.0 * self.lvl,
                healing=100.0 * self.lvl,
            ),
            "МАЛОЕ ЗАПИТЫВАНИЕ": ManaSpell(
                spell_name="Малое запитывание",
                spell_desc="Вы запитываетесь маной из окружающей среды. Быстро, но мало",
                mana=20.0 * self.lvl,
            ),
            "СРЕДНЕЕ ЗАПИТЫВАНИЕ": ManaSpell(
                spell_name="Среднее запитывание",
                spell_desc="Вы запитываетесь маной из окружающей среды. Должно хватить",
                mana=75.0 * self.lvl,
                mana_cost=25.0 * self.lvl,
            ),
            "ВЕЛИКОЕ ЗАПИТЫВАНИЕ": ManaSpell(
                spell_name="Великое запитывание",
                spell_desc="Вы запитываетесь маной из окружающей среды. Требует концентрации",
                mana=125.0 * self.lvl,
                mana_cost=50.0 * self.lvl,
            ),
        }

    def calc_damage(self):
        if self.race == "эльф":
            self.damage //= 2
        elif self.race == "орк":
            self.damage *= 3
        elif self.race == "хоббит":
            self.damage //= 2

    def level_up(self):
        self.lvl += 1
        print(f"{'>' * 8} LEVEL UP {'<' * 8}")
        print(f"Новый уровень: {self.lvl}")

        for i in range(len(self.passive_abilities)):
            self.passive_abilities[i].value *= self.lvl

        self.spells = {
            "ФАЕРБОЛЛ": AttackSpell(
                spell_name="Фаерболл",
                spell_desc="Наносит огромный урон, но требует большой сосредоточенности",
                mana_cost=100.0 * self.lvl,
                spell_damage=100.0 * self.lvl,
            ),
            "ЗЛАЯ НАСМЕШКА": AttackSpell(
                spell_name="Злая насмешка",
                spell_desc="Унижает вашего врага. Настолько, что он кричит от боли",
                mana_cost=10.0 * self.lvl,
                spell_damage=10.0 * self.lvl,
            ),
            "ЗВОН КЛАДБИЩА": AttackSpell(
                negative_effect="necromancy",
                spell_name="Звон кладбища",
                spell_desc="Темное заклинание некромантов. Высасывает силы из существа, пока оно не иссхонет.",
                mana_cost=70.0 * self.lvl,
                spell_damage=5.0 * self.lvl,
            ),
            "ЯДОВИТЫЙ ДЫМ": AttackSpell(
                negative_effect="poison",
                spell_name="Ядовитый дым",
                spell_desc="Дешевое заклинание, наносит мало урона, но с каждым ходом урон удваивается из-за эффекта отравления.",
                mana_cost=10.0 * self.lvl,
                spell_damage=1.0 * self.lvl,
            ),
            "ЯД ДРАКОНОВ": AttackSpell(
                negative_effect="poison",
                spell_name="Яд драконов",
                spell_desc="Дорогое заклинание, наносит меньше урона чем боевые, но с каждым ходом урон удваивается из-за эффекта отравления.",
                mana_cost=100.0 * self.lvl,
                spell_damage=10.0 * self.lvl,
            ),
            "МАГИЧЕСКАЯ СТРЕЛА": AttackSpell(
                spell_name="Магическая стрела",
                spell_desc="Обычное заклинание, наносит немного урона, зато пробивает броню",
                mana_cost=25.0 * self.lvl,
                spell_damage=20.0 * self.lvl,
            ),
            "ПРЕВОЗМОГАНИЕ": HealthSpell(
                spell_name="Превозмогание",
                spell_desc="Вы собираете свои силы и превозмогаете любую боль",
                mana_cost=15.0 * self.lvl,
                healing=20.0 * self.lvl,
            ),
            "ВЕЛИКОЕ ПРЕВОЗМОГАНИЕ": HealthSpell(
                spell_name="Великое превозмогание",
                spell_desc="Теперь вы можете стерпеть любую боль, любая рана для вас синяк",
                mana_cost=150.0 * self.lvl,
                healing=100.0 * self.lvl,
            ),
            "МАЛОЕ ЗАПИТЫВАНИЕ": ManaSpell(
                spell_name="Малое запитывание",
                spell_desc="Вы запитываетесь маной из окружающей среды. Быстро, но мало",
                mana=20.0 * self.lvl,
            ),
            "СРЕДНЕЕ ЗАПИТЫВАНИЕ": ManaSpell(
                spell_name="Среднее запитывание",
                spell_desc="Вы запитываетесь маной из окружающей среды. Должно хватить",
                mana=75.0 * self.lvl,
                mana_cost=25.0 * self.lvl,
            ),
            "ВЕЛИКОЕ ЗАПИТЫВАНИЕ": ManaSpell(
                spell_name="Великое запитывание",
                spell_desc="Вы запитываетесь маной из окружающей среды. Требует концентрации",
                mana=125.0 * self.lvl,
                mana_cost=50.0 * self.lvl,
            ),
        }
        self.xp = 0

        if self.race == "эльф":
            self.mana *= 2
            self.hp *= 2
        elif self.race == "орк":
            self.hp *= 2
            self.damage *= 3
            self.mana /= 2
        elif self.race == "хоббит":
            self.money *= 2
            self.xp = (1000 * self.lvl) / 10
        elif self.race == "человек":
            self.mana += (self.mana // 10) * self.lvl
            self.hp += (self.mana // 10) * self.lvl
            self.damage += (self.mana // 10) * self.lvl
            self.money += (self.mana // 10) * self.lvl

        self.hp = round(self.hp, 2)
        self.mana = round(self.mana, 2)
        self.damage = round(self.damage, 2)

    def apply_negative_effect(self, effect_name: str, effect_damage: str):
        self.negative_effects[f"{effect_name}#{len(self.negative_effects)}"] = (
            effect_damage
        )

    def calc_additional_params(self):
        if self.race == "эльф":
            self.mana *= 3
            self.damage //= 2
            self.hp += self.hp // 10
        elif self.race == "орк":
            self.mana = self.wisdom
            self.hp *= 2
            self.damage *= 3
        elif self.race == "хоббит":
            self.money *= 5
            self.hp -= self.hp // 10
            self.damage //= 2
            self.mana //= 2

        self.hp = round(self.hp, 2)
        self.mana = round(self.mana, 2)
        self.damage = round(self.damage, 2)

    def check_life(self):
        if self.hp > 0.0:
            return True
        else:
            return False

    def take_damage(self, damage: float):
        print(f"Вы получили урон: [bold red]{damage} урона[/bold red]")
        self.hp -= damage
        self.hp = round(self.hp, 2)
        self.mana = round(self.mana, 2)
        self.damage = round(self.damage, 2)

    def take_health(self, health: float):
        print(f"Вы выздоровели: [bold green]{health} HP[/bold green]")
        self.hp += health
        self.hp = round(self.hp, 2)
        self.mana = round(self.mana, 2)
        self.damage = round(self.damage, 2)

    def get_current_weapon(self):
        return self.initial_weapon

    def pickup_item_to_inventory(self, name: str, item: Item):
        self.inventory[name] = item

    def drop_item_from_inventory(self, name):
        if name in self.inventory:
            del self.inventory[name]

    def get_item_from_inventory(self, item_name: str):
        if item_name in self.inventory:
            return self.inventory[item_name]

        return None

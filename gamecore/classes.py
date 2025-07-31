from dataclasses import dataclass
from random import randint, choice
from gamecore.constants import *
from rich import print

def round_value(value):
    return round(value, 2)

@dataclass
class AttackSpell:
    spell_name: str
    spell_desc: str
    mana_cost: float
    spell_damage: float
    element: str = None
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

@dataclass
class PassiveAbility:
    name: str
    desc: str
    param: str
    value: any

class Quest:
    def __init__(self, id: str, name: str, description: str, reward: dict, required: int = 1):
        self.id = id
        self.name = name
        self.description = description
        self.reward = reward
        self.completed: bool = False
        self.progress: int = 0
        self.required: int = required

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "reward": self.reward,
            "completed": self.completed,
            "progress": self.progress,
            "required": self.required
        }

    @classmethod
    def from_dict(cls, data, qid):
        quest = cls(
            qid,
            data["name"],
            data["description"],
            data["reward"],
            data.get("required", 1)
        )
        quest.completed = data["completed"]
        quest.progress = data["progress"]
        return quest

    def check_completion(self, enemy, player):
        if self.completed:
            return False

        if self.id == "некроманты":
            if "скелет" in enemy.name.lower():
                self.progress += 1
        elif self.id == "природа":
            if "вредитель" in enemy.name.lower():
                self.progress += 1

        if self.progress >= self.required:
            self.completed = True
            return True
        return False

class Item:
    def __init__(self, name: str, item_type: str, value: int = 0, element: str = None):
        self.name = name
        self.type = item_type
        self.value = value
        self.element = element

class Weapon(Item):
    def __init__(
        self,
        name: str,
        damage: int,
        level: int = 1,
        durability=100.0,
        element: str = None,
        crit_chance: float = 0.05,
    ):
        super().__init__(name, "weapon", damage, element)
        self.durability = min(100.0, max(0.0, durability))
        self.level = level
        self.crit_chance = crit_chance
        self.max_durability = 100.0

        level_prefixes = {
            1: "Поломанный",
            2: "Ржавый",
            3: "Старый",
            4: "Обычный",
            5: "Редкий",
            6: "Хороший",
            7: "Отличный",
            8: "Мифический",
            9: "Легендарный",
        }

        self.name = f"{level_prefixes.get(self.level, '')} {self.name}"

        try:
            self.value = max(1, round_value(damage * level * (self.durability/100)))
        except ZeroDivisionError:
            self.value = 1

        if self.element:
            self.name += f" [{self.element}]"

    def get_durability_state(self):
        if self.durability >= 90:
            return "Идеал"
        elif self.durability >= 70:
            return "Как новый"
        elif self.durability >= 50:
            return "Б/У"
        elif self.durability >= 30:
            return "Старый"
        elif self.durability >= 10:
            return "Разваливающийся"
        else:
            return "Сломанный"

    def use(self):
        self.durability = max(0, self.durability - randint(1, 3))
        self.value = max(1, self.value * (self.durability/100))
        return self.value

    def repair(self):
        self.durability = min(100, self.durability + 40)
        self.value *= 1.1

    def level_up(self):
        if self.level < 9:
            self.level += 1
            self.value *= 1.25
            level_prefixes = {
                1: "Поломанный",
                2: "Ржавый",
                3: "Старый",
                4: "Обычный",
                5: "Редкий",
                6: "Хороший",
                7: "Отличный",
                8: "Мифический",
                9: "Легендарный",
            }
            self.name = f"{level_prefixes.get(self.level, '')} {self.name.split(' ', 1)[1]}"

class Armor(Item):
    def __init__(
        self, name: str, defense: int, armor_type: str, element_resist: dict = None
    ):
        super().__init__(name, "armor", defense)
        self.armor_type = armor_type
        self.element_resist = element_resist or {}

class Enemy:
    def __init__(self, player, name: str, terrain: str = None):
        self.player = player
        self.name = name
        self.terrain = terrain or choice(TERRAINS)
        self.danger_level = randint(1, min(11, max(1, player.lvl // 2)))
        self.element_resistances = {elem: randint(-30, 30) for elem in ELEMENTS}
        self.crit_chance = 0.1
        self.crit_multiplier = 1.5
        self.max_hp = max(50, (randint(15, 60) * self.player.lvl * self.danger_level * DAMAGE_MULTIPLIER))
        self.hp = self.max_hp
        self.damage = max(3, (randint(3, 25) * self.player.lvl * self.danger_level * DAMAGE_MULTIPLIER))
        self.negative_effects = {}
        self.apply_terrain_effects()
        self.abilities = self.get_enemy_abilities()

    def get_enemy_abilities(self):
        abilities = []
        if self.danger_level >= 5:
            abilities.append("fire_breath")
        if self.danger_level >= 7:
            abilities.append("poison_cloud")
        if "некромант" in self.name.lower():
            abilities.append("summon_skeleton")
        if "лиц" in self.name.lower():
            abilities.append("life_drain")
        return abilities

    def apply_terrain_effects(self):
        effects = TERRAIN_EFFECTS.get(self.terrain, {})
        for effect, value in effects.items():
            if effect == "урон":
                self.damage = round_value(self.damage * (1 + value))
            elif effect == "защита":
                self.hp = round_value(self.hp * (1 + value))

    def apply_negative_effect(self, effect_name: str, effect_damage: str):
        self.negative_effects[f"{effect_name}@{len(self.negative_effects)}"] = effect_damage

    @property
    def damage_attack(self):
        base_damage = randint(int(self.damage * 0.8), int(self.damage * 1.2))

        crit_roll = randint(1, 100)
        if crit_roll <= (self.crit_chance * 100):
            base_damage = round_value(base_damage * self.crit_multiplier)
        return base_damage

    def take_damage(self, damage: float):
        self.hp = round_value(max(0, self.hp - damage))

    def take_health(self, health: float):
        self.hp = round_value(min(self.max_hp, self.hp + health))

    def is_dead(self):
        return self.hp <= 0

    def choose_action(self, player):
        hp_percent = self.hp / self.max_hp
        if hp_percent < 0.3 and randint(1, 100) > 70 and "heal" in self.abilities:
            return "heal"
        if self.abilities and randint(1, 100) > 60:
            return "ability"
        return "attack"

    def use_ability(self, player):
        ability = choice(self.abilities)
        if ability == "fire_breath":
            damage = self.damage * 1.8
            player.take_damage(damage)
            return f"[red]{self.name} использует Огненное дыхание! Нанесено {damage:.2f} урона![/red]"
        elif ability == "poison_cloud":
            self.apply_negative_effect("Яд", self.damage * 0.15)
            return f"[green]{self.name} создает Ядовитое облако![/green]"
        elif ability == "summon_skeleton":
            self.hp += self.max_hp * 0.2
            return f"[cyan]{self.name} призывает скелета! Восстановлено {self.max_hp * 0.2:.2f} HP[/cyan]"
        elif ability == "life_drain":
            drain = player.hp * 0.15
            player.take_damage(drain)
            self.take_health(drain)
            return f"[purple]{self.name} высасывает {drain:.2f} HP из вас![/purple]"
        return f"[yellow]{self.name} использует неизвестную способность![/yellow]"

class Player:
    def __init__(
        self,
        name: str,
        race: str,
        player_class: str,
        power: int = 5,
        agility: int = 3,
        wisdom: int = 2,
        initial_hp: float = 100.0,
        initial_weapon: Weapon = None,
    ):
        self.name = name
        self.race = race.lower()
        self.player_class = player_class.lower()
        self.lvl = 1
        self.xp = 0
        self.xp_to_next = 1000
        self.hp = initial_hp
        self.max_hp = initial_hp
        self.passive_abilities = []
        self.crit_chance = 0.05
        self.crit_multiplier = 1.5
        self.element_resistances = {elem: 0 for elem in ELEMENTS}
        self.terrain = None
        self.story_progress = 0
        self.quests = {}
        self.factions = FRACTIONS.copy()
        self.crafting_materials = {}
        self.equipment = {"weapon": None, "armor": None, "amulet": None, "ring": None}
        self.class_ability_available = True
        self.stats = {
            "enemies_killed": 0,
            "quests_completed": 0,
            "gold_earned": 0,
            "damage_dealt": 0,
        }

        self.power = power
        self.agility = agility
        self.wisdom = wisdom

        race_bonuses = {
            "орк": {"power": 3, "hp_mult": 1.25},
            "эльф": {"wisdom": 3, "mana_mult": 1.5, "agility": 1},
            "хоббит": {"agility": 3, "crit_chance": 0.08},
            "человек": {"power": 1, "wisdom": 1, "agility": 1},
            "гном": {"wisdom": 2, "hp_mult": 1.15},
            "дварф": {"power": 2, "hp_mult": 1.3},
            "демон": {"power": 3, "wisdom": 1, "hp_mult": 1.1},
        }

        class_bonuses = {
            "воин": {"power": 3, "hp_mult": 1.3},
            "маг": {"wisdom": 4, "mana_mult": 2.0, "power": -1},
            "лучник": {"agility": 4, "crit_chance": 0.15},
            "плут": {"agility": 3, "crit_multiplier": 0.3},
            "жрец": {"wisdom": 3, "mana_mult": 1.5},
            "некромант": {"wisdom": 4, "power": -1},
            "паладин": {"power": 2, "wisdom": 2, "hp_mult": 1.2},
            "друид": {"wisdom": 3, "agility": 2, "mana_mult": 1.3},
        }

        bonus = race_bonuses.get(self.race, {})
        self.power += bonus.get("power", 0)
        self.agility += bonus.get("agility", 0)
        self.wisdom += bonus.get("wisdom", 0)
        self.crit_chance += bonus.get("crit_chance", 0)

        bonus = class_bonuses.get(self.player_class, {})
        self.power += bonus.get("power", 0)
        self.agility += bonus.get("agility", 0)
        self.wisdom += bonus.get("wisdom", 0)
        self.crit_chance += bonus.get("crit_chance", 0)
        self.crit_multiplier += bonus.get("crit_multiplier", 0)

        self.hp_mult = bonus.get("hp_mult", 1.0) * race_bonuses.get(self.race, {}).get("hp_mult", 1.0)
        self.mana_mult = bonus.get("mana_mult", 1.0) * race_bonuses.get(self.race, {}).get("mana_mult", 1.0)

        self.hp = round_value(self.hp * self.hp_mult)
        self.max_hp = self.hp

        self.money = max(10, (2 * self.agility * self.lvl * 2))

        if not initial_weapon:
            initial_weapon = Weapon("Медный кинжал", 10, durability=80.0)
        self.equipment["weapon"] = initial_weapon
        self.damage = (self.power + self.equipment["weapon"].value) * DAMAGE_MULTIPLIER

        self.mana = round_value(10 * self.wisdom * self.mana_mult)
        self.max_mana = self.mana

        self.apply_race_class_abilities()
        self.calc_additional_params()

        self.negative_effects = {}
        self.inventory = {}
        self.spells = self.get_class_spells()
        self.add_starter_quest()

    def use_class_ability(self, enemy=None):
        if self.player_class == "воин":
            damage = self.damage * 2.2
            enemy.take_damage(damage)
            print(f"[bold red]Сокрушительный удар![/bold red] Нанесено {damage:.2f} урона!")
        elif self.player_class == "маг":
            self.mana += self.max_mana * 0.4
            print("[bold cyan]Концентрация магии![/bold cyan] Восстановлено 40% маны")
        elif self.player_class == "лучник":
            self.crit_chance += 0.25
            print("[bold yellow]Точный выстрел![/bold yellow] Шанс крита увеличен на 25%")
        elif self.player_class == "плут":
            print("[bold green]Теневой шаг![/bold green] Шанс уклонения увеличен на 40%")
        elif self.player_class == "жрец":
            heal_amount = self.max_hp * 0.35
            self.take_health(heal_amount)
            print(f"[bold white]Божественное исцеление![/bold white] Восстановлено {heal_amount} HP")
        elif self.player_class == "некромант":
            drain = enemy.hp * 0.15
            enemy.take_damage(drain)
            self.take_health(drain)
            print(f"[bold purple]Похищение жизни![/bold purple] Вы забрали {drain:.2f} HP у врага")
        elif self.player_class == "паладин":
            self.damage *= 1.4
            print("[bold yellow]Благословение оружия![/bold yellow] Урон увеличен на 40%")
        elif self.player_class == "друид":
            heal_amount = self.max_hp * 0.25
            self.take_health(heal_amount)
            self.mana += self.max_mana * 0.25
            print("[bold green]Сила природы![/bold green] Восстановлено 25% HP и маны")

    def get_class_spells(self):
        base_spells = {
            "ФАЕРБОЛЛ": AttackSpell(
                spell_name="Фаерболл",
                spell_desc="Наносит огненный урон",
                mana_cost=round_value(25.0 * self.lvl * DAMAGE_MULTIPLIER),
                spell_damage=round_value(40.0 * self.lvl * DAMAGE_MULTIPLIER),
                element="огонь",
            ),
            "ЛЕДЯНОЙ ШТОРМ": AttackSpell(
                spell_name="Ледяной шторм",
                spell_desc="Наносит ледяной урон",
                mana_cost=round_value(20.0 * self.lvl * DAMAGE_MULTIPLIER),
                spell_damage=round_value(35.0 * self.lvl * DAMAGE_MULTIPLIER),
                element="лед",
            ),
            "ИСЦЕЛЕНИЕ": HealthSpell(
                spell_name="Исцеление",
                spell_desc="Восстанавливает здоровье",
                mana_cost=round_value(15.0 * self.lvl * DAMAGE_MULTIPLIER),
                healing=round_value(25.0 * self.lvl * HEALING_MULTIPLIER),
            ),
            "МАЛОЕ ЗАПИТЫВАНИЕ": ManaSpell(
                spell_name="Малое запитывание",
                spell_desc="Восстанавливает ману",
                mana=round_value(20.0 * self.lvl * HEALING_MULTIPLIER),
            ),
        }

        class_spells = {
            "маг": {
                "МОЛНИЯ": AttackSpell(
                    spell_name="Молния",
                    spell_desc="Наносит урон электричеством",
                    mana_cost=round_value(35.0 * self.lvl * DAMAGE_MULTIPLIER),
                    spell_damage=round_value(50.0 * self.lvl * DAMAGE_MULTIPLIER),
                    element="электричество",
                ),
                "ТЕЛЕПОРТАЦИЯ": ManaSpell(
                    spell_name="Телепортация",
                    spell_desc="Позволяет избежать боя",
                    mana=round_value(40.0 * self.lvl * HEALING_MULTIPLIER),
                    mana_cost=round_value(25.0 * self.lvl * DAMAGE_MULTIPLIER),
                ),
            },
            "жрец": {
                "ВОСКРЕШЕНИЕ": HealthSpell(
                    spell_name="Воскрешение",
                    spell_desc="Восстанавливает большое количество здоровья",
                    mana_cost=round_value(40.0 * self.lvl * DAMAGE_MULTIPLIER),
                    healing=round_value(80.0 * self.lvl * HEALING_MULTIPLIER),
                ),
                "СВЯТОЙ ЩИТ": HealthSpell(
                    spell_name="Святой щит",
                    spell_desc="Дает временную защиту",
                    mana_cost=round_value(25.0 * self.lvl * DAMAGE_MULTIPLIER),
                    healing=0,
                ),
            },
            "некромант": {
                "ВОЗЗЫВАНИЕ МЕРТВЕЦОВ": AttackSpell(
                    spell_name="Воззвание мертвецов",
                    spell_desc="Призывает скелетов для атаки",
                    mana_cost=round_value(50.0 * self.lvl * DAMAGE_MULTIPLIER),
                    spell_damage=round_value(60.0 * self.lvl * DAMAGE_MULTIPLIER),
                    element="тьма",
                ),
                "ВЫСАСЫВАНИЕ ДУШИ": HealthSpell(
                    spell_name="Высасывание души",
                    spell_desc="Крадет здоровье у врага",
                    mana_cost=round_value(35.0 * self.lvl * DAMAGE_MULTIPLIER),
                    healing=round_value(40.0 * self.lvl * HEALING_MULTIPLIER),
                ),
            },
            "паладин": {
                "СВЯЩЕННЫЙ УДАР": AttackSpell(
                    spell_name="Священный удар",
                    spell_desc="Наносит урон светом",
                    mana_cost=round_value(30.0 * self.lvl * DAMAGE_MULTIPLIER),
                    spell_damage=round_value(45.0 * self.lvl * DAMAGE_MULTIPLIER),
                    element="свет",
                ),
                "БЛАГОСЛОВЕНИЕ": HealthSpell(
                    spell_name="Благословение",
                    spell_desc="Исцеляет и усиливает",
                    mana_cost=round_value(35.0 * self.lvl * DAMAGE_MULTIPLIER),
                    healing=round_value(35.0 * self.lvl * HEALING_MULTIPLIER),
                ),
            },
            "друид": {
                "ГНЕВ ПРИРОДЫ": AttackSpell(
                    spell_name="Гнев природы",
                    spell_desc="Наносит урон природной стихией",
                    mana_cost=round_value(25.0 * self.lvl * DAMAGE_MULTIPLIER),
                    spell_damage=round_value(40.0 * self.lvl * DAMAGE_MULTIPLIER),
                    element="природа",
                ),
                "ЦЕЛИТЕЛЬНЫЙ РОСТ": HealthSpell(
                    spell_name="Целительный рост",
                    spell_desc="Исцеляет союзников",
                    mana_cost=round_value(20.0 * self.lvl * DAMAGE_MULTIPLIER),
                    healing=round_value(30.0 * self.lvl * HEALING_MULTIPLIER),
                ),
            },
        }

        spells = base_spells
        spells.update(class_spells.get(self.player_class, {}))
        return spells

    def apply_race_class_abilities(self):
        if self.race == "человек":
            self.passive_abilities.append(
                PassiveAbility(
                    name="Универсал",
                    desc="Каждый гейм-мув вы получаете дополнительную ману, монеты или XP.",
                    param="random_additional_param",
                    value=8,
                )
            )
        elif self.race == "хоббит":
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
                    desc=f"Орочье наследие сделало вас невероятно стойким. Вы можете уходить в минус на {40 * self.lvl}HP.",
                    param="health_fortitude",
                    value=40,
                )
            )
        elif self.race == "эльф":
            self.passive_abilities.append(
                PassiveAbility(
                    name="Мания маны",
                    desc="Эльфийская душа позволяет вам получить ману за убийство врага.",
                    param="mana_loot",
                    value=1.5,
                )
            )
        elif self.race == "гном":
            self.passive_abilities.append(
                PassiveAbility(
                    name="Инженер",
                    desc="Гномы могут чинить оружие без затрат",
                    param="free_repair",
                    value=True,
                )
            )
        elif self.race == "дварф":
            self.passive_abilities.append(
                PassiveAbility(
                    name="Каменная кожа",
                    desc="Дварфы получают меньше урона",
                    param="damage_reduction",
                    value=0.12,
                )
            )
        elif self.race == "демон":
            self.passive_abilities.append(
                PassiveAbility(
                    name="Огненная аура",
                    desc="Демоны наносят дополнительный огненный урон",
                    param="fire_damage",
                    value=8,
                )
            )

        if self.player_class == "лучник":
            self.passive_abilities.append(
                PassiveAbility(
                    name="Меткий выстрел",
                    desc="Увеличивает шанс критического удара",
                    param="crit_chance",
                    value=0.08,
                )
            )
        elif self.player_class == "плут":
            self.passive_abilities.append(
                PassiveAbility(
                    name="Скрытность",
                    desc="Позволяет избегать урона",
                    param="dodge_chance",
                    value=0.15,
                )
            )
        elif self.player_class == "жрец":
            self.passive_abilities.append(
                PassiveAbility(
                    name="Божественная защита",
                    desc="Уменьшает получаемый урон",
                    param="damage_reduction",
                    value=0.08,
                )
            )
        elif self.player_class == "паладин":
            self.passive_abilities.append(
                PassiveAbility(
                    name="Светлая аура",
                    desc="Увеличивает сопротивление темной магии",
                    param="dark_resist",
                    value=0.25,
                )
            )
        elif self.player_class == "друид":
            self.passive_abilities.append(
                PassiveAbility(
                    name="Единение с природой",
                    desc="Увеличивает эффективность в природных зонах",
                    param="nature_boost",
                    value=0.15,
                )
            )

    def calc_additional_params(self):
        if self.race == "эльф":
            self.damage = round_value(self.damage * 0.95)
        elif self.race == "орк":
            self.damage = round_value(self.damage * 1.2)
        elif self.race == "хоббит":
            self.damage = round_value(self.damage * 0.85)
            self.mana = round_value(self.mana * 0.9)

    def calc_damage(self):
        base_damage = self.power + self.equipment["weapon"].value
        crit_roll = randint(1, 100)
        is_crit = crit_roll <= (self.crit_chance * 100)

        if is_crit:
            damage = round_value(base_damage * self.crit_multiplier)
            return damage, True
        return round_value(base_damage), False

    def level_up(self):
        self.lvl += 1
        self.xp_to_next = round_value(self.lvl * 1000 * XP_MULTIPLIER)

        for ability in self.passive_abilities:
            if ability.value > 0:
                ability.value = round_value(ability.value * 1.08)

        self.max_hp = round_value(self.max_hp * 1.15)
        self.hp = self.max_hp
        self.max_mana = round_value(self.max_mana * 1.2)
        self.mana = self.max_mana
        self.power += 1
        self.agility += 1
        self.wisdom += 1

        self.spells = self.get_class_spells()
        self.xp = 0
        print(f"[bold green]Вы достигли {self.lvl} уровня![/bold green]")

    def apply_negative_effect(self, effect_name: str, effect_damage: str):
        self.negative_effects[f"{effect_name}#{len(self.negative_effects)}"] = effect_damage

    def is_dead(self):
        return self.hp <= 0

    def take_damage(self, damage: float):
        reduction = 0
        for ability in self.passive_abilities:
            if ability.param == "damage_reduction":
                reduction += ability.value

        damage = max(1, damage * (1 - reduction))
        self.hp = round_value(max(0, self.hp - damage))
        self.stats["damage_dealt"] += damage

    def take_health(self, health: float):
        self.hp = min(self.max_hp, self.hp + health)
        self.hp = round_value(self.hp)

    def regen_resources(self):
        self.hp = min(self.max_hp, self.hp + self.max_hp * 0.05)
        self.mana = min(self.max_mana, self.mana + self.max_mana * 0.1)
        self.hp = round_value(self.hp)
        self.mana = round_value(self.mana)

    def get_current_weapon(self):
        return self.equipment["weapon"]

    def pickup_item(self, item: Item):
        if item.type == "material":
            self.crafting_materials[item.name] = self.crafting_materials.get(item.name, 0) + 1
        else:
            self.inventory[item.name] = item

    def drop_item(self, item_name: str):
        if item_name in self.inventory:
            del self.inventory[item_name]

    def equip_item(self, item_name: str):
        if item_name in self.inventory:
            item = self.inventory[item_name]
            if item.type in self.equipment:
                old_item = self.equipment[item.type]
                if old_item:
                    self.inventory[old_item.name] = old_item
                self.equipment[item.type] = item
                del self.inventory[item_name]
                return True
        return False

    def add_quest(self, quest_id: str):
        if quest_id in QUESTS and quest_id not in self.quests:
            quest_data = QUESTS[quest_id]
            self.quests[quest_id] = Quest(
                quest_id,
                quest_data["name"],
                quest_data["description"],
                quest_data["reward"],
                quest_data.get("required", 1)
            )
            return True
        return False

    def complete_quest(self, quest_id: str):
        if quest_id in self.quests and not self.quests[quest_id].completed:
            quest = self.quests[quest_id]
            quest.completed = True

            reward = quest.reward
            self.xp += reward.get("xp", 0)
            self.money += reward.get("money", 0)
            self.stats["gold_earned"] += reward.get("money", 0)
            self.stats["quests_completed"] += 1

            if "item" in reward:
                self.pickup_item(Item(reward["item"], "armor", randint(5, 15)))

            if "reputation" in reward:
                for faction, points in reward["reputation"].items():
                    if faction in self.factions:
                        self.factions[faction]["отношение"] = min(100, self.factions[faction]["отношение"] + points)

            if quest_id == "начало":
                self.story_progress = 1
            elif quest_id == "некроманты":
                self.story_progress = 2
            elif quest_id == "артефакт":
                self.story_progress = 3
            elif quest_id == "дракон":
                self.story_progress = 5

            # Добавление следующего квеста в цепочке
            next_quest = QUEST_CHAINS.get(quest_id)
            if next_quest and next_quest not in self.quests:
                self.add_quest(next_quest)

            return True
        return False

    def add_starter_quest(self):
        self.add_quest("начало")

    def craft_item(self, item_name: str):
        if item_name in CRAFT_RECIPES:
            recipe = CRAFT_RECIPES[item_name]
            for material, amount in recipe.items():
                if self.crafting_materials.get(material, 0) < amount:
                    return False

            for material, amount in recipe.items():
                self.crafting_materials[material] -= amount
                if self.crafting_materials[material] <= 0:
                    del self.crafting_materials[material]

            crafted_item = None
            if item_name.startswith("Зелье"):
                crafted_item = Item(item_name, "consumable", randint(20, 50) * self.lvl)
            elif item_name.startswith("Стальной"):
                crafted_item = Weapon(item_name, 15 + self.lvl * 2, 4)
            elif item_name.startswith("Мифриловые"):
                crafted_item = Armor(item_name, 20 + self.lvl * 3, "armor")

            if crafted_item:
                self.pickup_item(crafted_item)
                return True
        return False

    def get_story_progress(self):
        return STORY_PROGRESS[min(self.story_progress, len(STORY_PROGRESS) - 1)]

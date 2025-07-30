from dataclasses import dataclass
from random import randint, choice
from gamecore.constants import ELEMENTS, TERRAINS, TERRAIN_EFFECTS, QUESTS, FRACTIONS, CRAFT_RECIPES, ARMOR, STORY_PROGRESS

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

@dataclass
class Quest:
    name: str
    description: str
    reward: dict
    completed: bool = False
    progress: int = 0
    required: int = 1

class Item:
    def __init__(self, name: str, item_type: str, value: int = 0, element: str = None):
        self.name = name
        self.type = item_type
        self.value = value
        self.element = element

class Weapon(Item):
    def __init__(self, name: str, damage: int, level: int = 1,
                 initial_brokenness=0.0, breaking_value: float = 1.0,
                 element: str = None, crit_chance: float = 0.05):
        super().__init__(name, "weapon", damage, element)
        self.initial_brokenness = initial_brokenness
        self.breaking_value = breaking_value
        self.level = level
        self.crit_chance = crit_chance

        level_prefixes = {
            1: "Поломанный",
            2: "Ржавый",
            3: "Старый",
            4: "Обычный",
            5: "Редкий",
            6: "Хороший",
            7: "Отличный",
            8: "Мифический",
            9: "Легендарный"
        }

        self.name = f"{level_prefixes.get(self.level, '')} {self.name}"

        try:
            self.value = max(1, round(damage * level / max(1, self.initial_brokenness / 10), 2))
        except ZeroDivisionError:
            self.value = 1

        self.name = f"{self.name} ({self.get_brokenness_state()})"
        if self.element:
            self.name += f" [{self.element}]"

    def get_brokenness_state(self):
        if self.initial_brokenness == 0.0:
            return "Идеал"
        elif 0 < self.initial_brokenness <= 25.0:
            return "Как новый"
        elif 25.0 < self.initial_brokenness <= 50.0:
            return "Б/У"
        elif 50.0 < self.initial_brokenness <= 75.0:
            return "Старый"
        elif 75.0 < self.initial_brokenness <= 90.0:
            return "Разваливающийся"
        else:
            return "Сломанный"

    def use(self):
        self.initial_brokenness += self.breaking_value
        self.value = max(1, self.value * 0.99)
        return self.value

    def repair(self):
        self.initial_brokenness = max(0, self.initial_brokenness - 30)
        self.value *= 1.1
        self.name = " ".join(self.name.split(' ')[1:])
        self.name = f"{self.name} ({self.get_brokenness_state()})"

class Armor(Item):
    def __init__(self, name: str, defense: int, armor_type: str, element_resist: dict = None):
        super().__init__(name, "armor", defense)
        self.armor_type = armor_type
        self.element_resist = element_resist or {}

class Enemy:
    def __init__(self, player, name: str, terrain: str = None):
        self.player = player
        self.name = name
        self.terrain = terrain or choice(TERRAINS)
        self.danger_level = randint(1, min(11, max(1, player.lvl // 2)))
        self.element_resistances = {elem: randint(-50, 50) for elem in ELEMENTS}

        danger_prefixes = {
            2: "Злой ",
            3: "Гига",
            4: "Кровавый ",
            5: "Темный ",
            6: "Чернолорд ",
            7: "Лич ",
            8: "Владыка личей ",
            9: "Архилич ",
            10: "Владыка архиличей ",
            11: "Владыка хаоса "
        }

        self.name = f"{danger_prefixes.get(self.danger_level, '')}{name}"
        self.hp = max(50, (randint(5, 15) * self.player.lvl * self.danger_level))
        self.damage = max(1, (randint(1, 5) * self.player.lvl * self.danger_level))
        self.negative_effects = {}
        self.apply_terrain_effects()

    def apply_terrain_effects(self):
        effects = TERRAIN_EFFECTS.get(self.terrain, {})
        for effect, value in effects.items():
            if effect == "урон":
                self.damage *= (1 + value)
            elif effect == "защита":
                self.hp *= (1 + value)

    def apply_negative_effect(self, effect_name: str, effect_damage: str):
        self.negative_effects[f"{effect_name}@{len(self.negative_effects)}"] = effect_damage

    @property
    def damage_attack(self):
        base_damage = randint(int(self.damage * 0.8), int(self.damage * 1.2))
        return base_damage

    def take_damage(self, damage: float):
        self.hp -= damage
        self.hp = round(max(0, self.hp), 2)

    def take_health(self, health: float):
        self.hp += health
        self.hp = round(self.hp, 2)

    def is_dead(self):
        return self.hp <= 0

class Player:
    def __init__(self, name: str, race: str, player_class: str,
                 initial_hp: float = 100.0,
                 initial_weapon: Weapon = None):

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
        self.equipment = {
            "weapon": None,
            "armor": None,
            "amulet": None,
            "ring": None
        }

        self.power = randint(3, 10)
        self.agility = randint(3, 10)
        self.wisdom = randint(3, 10)

        race_bonuses = {
            "орк": {"power": 3, "hp_mult": 1.3},
            "эльф": {"wisdom": 3, "mana_mult": 1.5},
            "хоббит": {"agility": 3, "crit_chance": 0.1},
            "человек": {"power": 1, "wisdom": 1, "agility": 1},
            "гном": {"wisdom": 2, "hp_mult": 1.2},
            "дварф": {"power": 2, "hp_mult": 1.4},
            "демон": {"power": 4, "wisdom": 2, "hp_mult": 1.1}
        }

        class_bonuses = {
            "воин": {"power": 3, "hp_mult": 1.4},
            "маг": {"wisdom": 4, "mana_mult": 2.0},
            "лучник": {"agility": 4, "crit_chance": 0.15},
            "плут": {"agility": 3, "crit_multiplier": 0.3},
            "жрец": {"wisdom": 3, "mana_mult": 1.5},
            "некромант": {"wisdom": 5, "power": -1},
            "паладин": {"power": 2, "wisdom": 2, "hp_mult": 1.2},
            "друид": {"wisdom": 3, "agility": 2, "mana_mult": 1.3}
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

        self.hp = round(self.hp * self.hp_mult, 2)
        self.max_hp = self.hp

        self.money = max(10, (2 * self.agility * self.lvl * 2))

        if not initial_weapon:
            initial_weapon = Weapon("Медный кинжал", 10, initial_brokenness=50.0)
        self.equipment["weapon"] = initial_weapon

        self.damage = self.power + self.equipment["weapon"] .value

        self.mana = round(10 * self.wisdom * self.mana_mult, 2)
        self.max_mana = self.mana

        self.apply_race_class_abilities()
        self.calc_additional_params()

        self.negative_effects = {}
        self.inventory = {}
        self.spells = self.get_class_spells()
        self.add_starter_quest()

    def get_class_spells(self):
        base_spells = {
            "ФАЕРБОЛЛ": AttackSpell(
                spell_name="Фаерболл",
                spell_desc="Наносит огненный урон",
                mana_cost=30.0 * self.lvl,
                spell_damage=50.0 * self.lvl,
                element="огонь"
            ),
            "ЛЕДЯНОЙ ШТОРМ": AttackSpell(
                spell_name="Ледяной шторм",
                spell_desc="Наносит ледяной урон",
                mana_cost=25.0 * self.lvl,
                spell_damage=40.0 * self.lvl,
                element="лед"
            ),
            "ИСЦЕЛЕНИЕ": HealthSpell(
                spell_name="Исцеление",
                spell_desc="Восстанавливает здоровье",
                mana_cost=20.0 * self.lvl,
                healing=30.0 * self.lvl
            ),
            "МАЛОЕ ЗАПИТЫВАНИЕ": ManaSpell(
                spell_name="Малое запитывание",
                spell_desc="Восстанавливает ману",
                mana=25.0 * self.lvl
            )
        }

        class_spells = {
            "маг": {
                "МОЛНИЯ": AttackSpell(
                    spell_name="Молния",
                    spell_desc="Наносит урон электричеством",
                    mana_cost=40.0 * self.lvl,
                    spell_damage=60.0 * self.lvl,
                    element="электричество"
                ),
                "ТЕЛЕПОРТАЦИЯ": ManaSpell(
                    spell_name="Телепортация",
                    spell_desc="Позволяет избежать боя",
                    mana=50.0 * self.lvl,
                    mana_cost=30.0 * self.lvl
                )
            },
            "жрец": {
                "ВОСКРЕШЕНИЕ": HealthSpell(
                    spell_name="Воскрешение",
                    spell_desc="Восстанавливает большое количество здоровья",
                    mana_cost=50.0 * self.lvl,
                    healing=100.0 * self.lvl
                ),
                "СВЯТОЙ ЩИТ": HealthSpell(
                    spell_name="Святой щит",
                    spell_desc="Дает временную защиту",
                    mana_cost=30.0 * self.lvl,
                    healing=0
                )
            },
            "некромант": {
                "ВОЗЗЫВАНИЕ МЕРТВЕЦОВ": AttackSpell(
                    spell_name="Воззвание мертвецов",
                    spell_desc="Призывает скелетов для атаки",
                    mana_cost=60.0 * self.lvl,
                    spell_damage=70.0 * self.lvl,
                    element="тьма"
                ),
                "ВЫСАСЫВАНИЕ ДУШИ": HealthSpell(
                    spell_name="Высасывание души",
                    spell_desc="Крадет здоровье у врага",
                    mana_cost=40.0 * self.lvl,
                    healing=50.0 * self.lvl
                )
            },
            "паладин": {
                "СВЯЩЕННЫЙ УДАР": AttackSpell(
                    spell_name="Священный удар",
                    spell_desc="Наносит урон светом",
                    mana_cost=35.0 * self.lvl,
                    spell_damage=55.0 * self.lvl,
                    element="свет"
                ),
                "БЛАГОСЛОВЕНИЕ": HealthSpell(
                    spell_name="Благословение",
                    spell_desc="Исцеляет и усиливает",
                    mana_cost=40.0 * self.lvl,
                    healing=40.0 * self.lvl
                )
            },
            "друид": {
                "ГНЕВ ПРИРОДЫ": AttackSpell(
                    spell_name="Гнев природы",
                    spell_desc="Наносит урон природной стихией",
                    mana_cost=30.0 * self.lvl,
                    spell_damage=45.0 * self.lvl,
                    element="природа"
                ),
                "ЦЕЛИТЕЛЬНЫЙ РОСТ": HealthSpell(
                    spell_name="Целительный рост",
                    spell_desc="Исцеляет союзников",
                    mana_cost=25.0 * self.lvl,
                    healing=35.0 * self.lvl
                )
            }
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
                    value=10
                )
            )
        elif self.race == "хоббит":
            self.passive_abilities.append(
                PassiveAbility(
                    name="Скидка",
                    desc="Хоббиты обожают деньги и всегда могут получить скидку (25%).",
                    param="discount",
                    value=25
                )
            )
        elif self.race == "орк":
            self.passive_abilities.append(
                PassiveAbility(
                    name="Стойкость",
                    desc=f"Орочье наследие сделало вас невероятно стойким. Вы можете уходить в минус на {50 * self.lvl}HP.",
                    param="health_fortitude",
                    value=50
                )
            )
        elif self.race == "эльф":
            self.passive_abilities.append(
                PassiveAbility(
                    name="Мания маны",
                    desc="Эльфийская душа позволяет вам получить ману за убийство врага.",
                    param="mana_loot",
                    value=2
                )
            )
        elif self.race == "гном":
            self.passive_abilities.append(
                PassiveAbility(
                    name="Инженер",
                    desc="Гномы могут чинить оружие без затрат",
                    param="free_repair",
                    value=True
                )
            )
        elif self.race == "дварф":
            self.passive_abilities.append(
                PassiveAbility(
                    name="Каменная кожа",
                    desc="Дварфы получают меньше урона",
                    param="damage_reduction",
                    value=0.15
                )
            )
        elif self.race == "демон":
            self.passive_abilities.append(
                PassiveAbility(
                    name="Огненная аура",
                    desc="Демоны наносят дополнительный огненный урон",
                    param="fire_damage",
                    value=10
                )
            )

        if self.player_class == "лучник":
            self.passive_abilities.append(
                PassiveAbility(
                    name="Меткий выстрел",
                    desc="Увеличивает шанс критического удара",
                    param="crit_chance",
                    value=0.1
                )
            )
        elif self.player_class == "плут":
            self.passive_abilities.append(
                PassiveAbility(
                    name="Скрытность",
                    desc="Позволяет избегать урона",
                    param="dodge_chance",
                    value=0.2
                )
            )
        elif self.player_class == "жрец":
            self.passive_abilities.append(
                PassiveAbility(
                    name="Божественная защита",
                    desc="Уменьшает получаемый урон",
                    param="damage_reduction",
                    value=0.1
                )
            )
        elif self.player_class == "паладин":
            self.passive_abilities.append(
                PassiveAbility(
                    name="Светлая аура",
                    desc="Увеличивает сопротивление темной магии",
                    param="dark_resist",
                    value=0.3
                )
            )
        elif self.player_class == "друид":
            self.passive_abilities.append(
                PassiveAbility(
                    name="Единение с природой",
                    desc="Увеличивает эффективность в природных зонах",
                    param="nature_boost",
                    value=0.2
                )
            )

    def calc_additional_params(self):
        if self.race == "эльф":
            self.damage = round(self.damage * 0.9, 2)
        elif self.race == "орк":
            self.damage = round(self.damage * 1.3, 2)
        elif self.race == "хоббит":
            self.damage = round(self.damage * 0.8, 2)
            self.mana = round(self.mana * 0.8, 2)

        self.hp = round(self.hp, 2)
        self.mana = round(self.mana, 2)

    def calc_damage(self):
        base_damage = self.power + self.equipment["weapon"].value
        crit_roll = randint(1, 100)
        is_crit = crit_roll <= (self.crit_chance * 100)

        if is_crit:
            damage = base_damage * self.crit_multiplier
            return damage, True
        return base_damage, False

    def level_up(self):
        self.lvl += 1
        self.xp_to_next = self.lvl * 1000

        for ability in self.passive_abilities:
            if ability.value > 0:
                ability.value *= 1.1

        self.max_hp = round(self.max_hp * 1.2, 2)
        self.hp = self.max_hp
        self.max_mana = round(self.max_mana * 1.2, 2)
        self.mana = self.max_mana

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
        self.hp -= damage
        self.hp = round(max(0, self.hp), 2)

    def take_health(self, health: float):
        self.hp = min(self.max_hp, self.hp + health)
        self.hp = round(self.hp, 2)

    def regen_resources(self):
        self.hp = min(self.max_hp, self.hp + self.max_hp * 0.05)
        self.mana = min(self.max_mana, self.mana + self.max_mana * 0.1)
        self.hp = round(self.hp, 2)
        self.mana = round(self.mana, 2)

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
                name=quest_data["name"],
                description=quest_data["description"],
                reward=quest_data["reward"]
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
        return STORY_PROGRESS[min(self.story_progress, len(STORY_PROGRESS)-1)]

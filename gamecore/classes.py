from abc import ABC, abstractmethod, abstractproperty
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
	def __init__(self, name: str, damage: int, initial_brokenness=0.0, breaking_value: float=1.0):
		self.name = name
		self.damage = damage
		self.initial_brokenness = initial_brokenness
		self.breaking_value = breaking_value
		self.description = f'Оружие {self.name}: {self.get_brokenness_state()}'

	def get_brokenness_state(self):
		state = 'Идеал'

		if self.initial_brokenness >= 10.0 and self.initial_brokenness <= 25.0:
			state = 'Как новый'
		elif self.initial_brokenness >= 25.0 and self.initial_brokenness <= 50.0:
			state = 'Б/У'
		elif self.initial_brokenness >= 50.0 and self.initial_brokenness <= 75.0:
			state = 'Старый'
		elif self.initial_brokenness >= 75.0 and self.initial_brokenness <= 90.0:
			state = 'Разваливающийся'
		elif self.initial_brokenness > 90.0:
			state = 'Сломанный'

		return state

	def use(self):
		self.initial_brokenness -= self.breaking_value

	def repair(self):
		self.initial_brokenness = 0.0


@dataclass
class AttackSpell:
	spell_name: str
	spell_desc: str
	mana_cost: float
	spell_damage: float
	negative_effect: str = None
	spell_type: str = 'ATTACK'


@dataclass
class HealthSpell:
	spell_name: str
	spell_desc: str
	mana_cost: float
	healing: float
	spell_type: str = 'HEALTH'


class Enemy(Entity):
	def __init__(self, multiplier, player, name: str, danger_level: int):
		self.danger_level = danger_level
		self.player = player

		if self.danger_level == 1:
			self.name = name
		elif self.danger_level == 2:
			self.name = f'Злой {name}'
		elif self.danger_level == 3:
			self.name = f'Гига{name.lower()}'
		elif self.danger_level == 4:
			self.name = f'Кровавый {name.lower()}'
		elif self.danger_level == 5:
			self.name = f'Темный {name.lower()}'
		elif self.danger_level == 6:
			self.name = f'Владыка хаоса {name}'

		self.hp = (randint(10, 100) * self.player.lvl * self.danger_level) * multiplier
		self.damage = (randint(1, 10) * self.player.lvl * self.danger_level) * multiplier

		self.negative_effects = {}

	def apply_negative_effect(self, effect_name: str, effect_damage: str):
		self.negative_effects[f'{effect_name}@{len(self.negative_effects)}'] = effect_damage
	
	@property
	def damage_attack(self):
		self.damage = randint(1, 10) * self.player.lvl * self.danger_level
		return self.damage

	def take_damage(self, damage: float):
		self.hp -= damage

	def take_health(self, health: float):
		self.hp += health


class Player(Entity):
	def __init__(self, name: str, race: str, initial_hp: float=100.0, initial_weapon: Weapon=Weapon('Ржавый кинжал', 10, 25.0)):
		self.initial_weapon = initial_weapon
		self.name = name
		self.lvl = 1
		self.hp = initial_hp
		self.race = race.lower()

		self.power = randint(3, 10) + 3 if self.race == 'орк' else randint(1, 10)
		self.agility = randint(3, 10) + 3 if self.race == 'хоббит' else randint(1, 10)
		self.wisdom = randint(3, 10) + 3 if self.race == 'эльф' else randint(1, 10)

		if self.race == 'человек':
			self.power = randint(2, 10) + 1
			self.agility = randint(2, 10) + 1
			self.wisdom = randint(2, 10) + 1
		elif self.race == 'хоббит':
			self.money = 10 * self.agility
		elif self.race == 'орк':
			self.initial_weapon.damage *= 2

		self.money = 2 * self.agility * self.lvl * 2
		self.damage = self.power + self.initial_weapon.damage
		self.mana = 10 * self.wisdom

		self.calc_additional_params()

		self.negative_effects = {}

		self.inventory = {}
		self.spells = {
			'Фаерболл': AttackSpell(spell_name='Фаерболл', spell_desc='Наносит огромный урон, но требует большой сосредоточенности', mana_cost=100.0, spell_damage=50.0),
			'Звон кладбища': AttackSpell(negative_effect='necromancy', spell_name='Звон кладбища', spell_desc='Темное заклинание некромантов. Высасывает силы из существа, пока оно не иссхонет.', mana_cost=25.0, spell_damage=5.0),
			'Ядовитый дым': AttackSpell(negative_effect='poison', spell_name='Ядовитый дым', spell_desc='Дешевое заклинание, наносит мало урона, но с каждым ходом урон удваивается из-за эффекта отравления.', mana_cost=10.0, spell_damage=0.5),
			'Магическая стрела': AttackSpell(spell_name='Магическая стрела', spell_desc='Обычное заклинание, наносит немного урона, зато пробивает броню', mana_cost=25.0, spell_damage=10.0),
			'Превозмогание': HealthSpell(spell_name='Превозмогание', spell_desc='Вы собираете свои силы и превозмогаете любую боль', mana_cost=15.0, healing=20.0)
		}

	def apply_negative_effect(self, effect_name: str, effect_damage: str):
		self.negative_effects[f'{effect_name}#{len(self.negative_effects)}'] = effect_damage

	def calc_additional_params(self):
		if self.race == 'эльф':
			self.mana *= 3
			self.damage //= 2
			self.hp += self.hp // 10
		elif self.race == 'орк':
			self.mana = self.wisdom
			self.hp *= 2
			self.damage *= 3
		elif self.race == 'хоббит':
			self.money *= 5
			self.hp -= self.hp // 10
			self.damage //= 2
			self.mana //= 2

	def check_life(self):
		if self.hp > 0.0:
			return True
		else:
			return False

	def take_damage(self, damage: float):
		print(f'Вы получили урон: [bold red]{damage} урона[/bold red]')
		self.hp -= damage

	def take_health(self, health: float):
		print(f'Вы выздоровели: [bold green]{health} HP[/bold green]')
		self.hp += health

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

from gamecore.resloader.loader import ResourceLoader
from gamecore.constants import LOGO_COLORS, RIP_COLORS, ACTIONS, CITIES, ENEMIES
from gamecore.classes import Weapon, Player, Enemy
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich import print
from gamecore.ui import clear
from random import randint, choice

loader = ResourceLoader('res')
loader.add_resource('logo.txt', 'logo')
loader.add_resource('rip.txt', 'rip')
		

def game_move(player):
	if not player.check_life():
		clear()
		loader.print_resource_content('rip', colors=RIP_COLORS, background='black')
		print('Ваш персонаж [red bold]погиб[/red bold].')
		exit()

	player.mana += player.mana / 100
	player.hp += player.hp / 100

	player.hp = round(player.hp, 2)
	player.mana = round(player.mana, 2)


def print_player_panel(player):
	print(Panel(f'{player.race} {player.name}    HP: [green]{player.hp}[/green]    СИЛА: [red]{player.power}[/red]    ЛОВКОСТЬ: [blue]{player.agility}[/blue]    МУДРОСТЬ: [magenta]{player.wisdom}[/magenta]    МАНА: [cyan]{player.mana}[/cyan]    УРОН: [red]{player.damage}[/red]    ДЕНЬГИ: [yellow]{player.money}[/yellow]'))
	inventory_items = '; '.join([f'{key}: {value.name}' for key, value in player.inventory.items()])
	spells = '; '.join([f'{name}' for name in player.spells.keys()])
	print(Panel(f'Инвентарь: {inventory_items}\nЗаклинания: {spells}'))


def shop(player):
	clear()
	SHOP_ITEMS = {
		'0': {
			'price': 0,
			'description': 'Выход из магазина бесплатный',
			'type': 'exit'
		},
		'Зелье регенерации': {
			'price': randint(10, 100) * player.lvl,
			'type': 'healing',
			'healval': randint(1, 50) * player.lvl,
			'description': 'Отлично лечит, но отвратительно на вкус'
		},
		'Малая колба регенерации': {
			'price': randint(10, 70) * player.lvl,
			'type': 'healing',
			'healval': randint(1, 10) * player.lvl,
			'description': 'Вроде лечит, но отвратительно на вкус'
		},
		'Ведро зелья регенерации': {
			'price': randint(100, 500) * player.lvl,
			'type': 'healing',
			'healval': randint(50, 200) * player.lvl,
			'description': 'Лечит хорошо, но отвратительно на вкус и слишком дорого'
		},
		'Зелье "lehfrf"': {
			'price': randint(10, 1000) * player.lvl,
			'type': 'poison',
			'damageval': randint(1, 20) * player.lvl,
			'description': 'Очень странное зелье, пахнет очень вкусно, но название непонятное'
		},
		'Зелье каменных пальцев': {
			'price': randint(10, 150) * player.lvl,
			'type': 'damageup',
			'damageval': randint(5, 20) * player.lvl if player.race == 'орк' else randint(1, 10) * player.lvl,
			'description': 'Булькающее зелье силы'
		},
		'Зелье стальных кулаков': {
			'price': randint(150, 200) * player.lvl,
			'type': 'damageup',
			'damageval': randint(10, 30) * player.lvl if player.race == 'орк' else randint(5, 20) * player.lvl,
			'description': 'Тяжелое серое зелье, от которого так и веет мощью'
		},
		'Бочка мудрости': {
			'price': randint(100, 1000) * player.lvl,
			'type': 'paramup',
			'upval': randint(1, 3),
			'param': 'wisdom',
			'description': 'Огромная дорогая бочка, увеличивающая вашу мудрость. Ух уж эти эльфы-маркетологи'
		},
		'Бочка ловкости': {
			'price': randint(100, 1000) * player.lvl,
			'type': 'paramup',
			'upval': randint(1, 3),
			'param': 'agility',
			'description': 'Огромная дорогая бочка, увеличивающая вашу ловкость. Ух уж эти хоббиты-маркетологи'
		},
		'Бочка силы': {
			'price': randint(100, 1000) * player.lvl,
			'type': 'paramup',
			'upval': randint(1, 3),
			'param': 'power',
			'description': 'Огромная дорогая бочка, увеличивающая вашу силу. Ух уж эти орки-маркетологи'
		},
		'Манное зелье': {
			'price': randint(10, 100) * player.lvl,
			'type': 'manaup',
			'manaval': randint(50, 100) * player.lvl if player.race == 'эльф' else randint(10, 50) * player.lvl,
			'description': 'Странная белая каша, которая должна увеличить вашу ману'
		}
	}

	print_player_panel(player)

	items = '\n\n'.join([f'{name}: цена {item["price"]}\n{item["description"]}' for name, item in SHOP_ITEMS.items()])

	print(Panel(f'Товары магазина:\n{items}'))

	item = Prompt.ask('Товар', default='0', choices=[name for name in SHOP_ITEMS.keys()])

	item = SHOP_ITEMS[item]

	if item['type'] == 'exit':
		print('До новых встреч, покупатель!')
		return

	if player.money < item['price']:
		print('У вас не хватает денег на покупку этого товара')
		return
	else:
		if not Confirm.ask('Точно хотите купить данный товар?'):
			print('До новых встреч, покупатель!')
			return

		print('Успешная покупка!')

		player.money -= item['price']

		if item['type'] == 'healing':
			player.take_health(item['healval'])
		elif item['type'] == 'manaup':
			player.mana += item['manaval']
		elif item['type'] == 'damageup':
			player.damage += item['damageval']
		elif item['type'] == 'poison':
			player.take_damage(item['damageval'])
			print(f'Проклятие! Зелье отравило вас на {item["damageval"]} HP!')
		elif item['type'] == 'paramup':
			if item['param'] == 'wisdom':
				player.wisdom += item['upval']
				player.mana += item['upval']
			elif item['param'] == 'agility':
				player.agility += item['upval']
			elif item['param'] == 'power':
				player.power += item['upval']
				player.damage += item['upval']


def battle(player, multiplier=1):
	enemy = Enemy(multiplier, player, choice(ENEMIES), randint(1, 6))
	loot = enemy.hp // 10 * (player.lvl * enemy.danger_level) * multiplier

	if player.race == 'хоббит': loot *= 2
	if player.race == 'орк': enemy.hp -= enemy.hp // 10
	
	while enemy.hp > 0 and player.hp > 0:
		print_player_panel(player)
		print(Panel(f'Враг: {enemy.name}\tHP врага: {enemy.hp}'))
		print(Panel('Действия:\n1 - атаковать\n2 - применить заклинание\n3 - встать в блок\n4 - сбежать'))

		act = Prompt.ask('Действие: ', default="1")

		print(f'\n{"-" * 64}\n')

		if act == "1":
			enemy.take_damage(player.damage)
			print(f'Вы нанесли [bold red]{player.damage}[/bold red] урона врагу: {enemy.name}')
		elif act == '3':
			if randint(1, 2) == 1:
				print(f'Вы забежали за ближайшее препятствие и смогли обойти удар! Вы перевели дух')
				player.take_health(player.hp // 10)
				continue
			else:
				print(f'Тяжелая нога судьбы поставила вам подножку, и вы упали под ноги врагу!')
		elif act == '4':
			if randint(1, player.agility * enemy.danger_level) > 2 * enemy.danger_level:
				print('Вы смогли сбежать!')
				return
			else:
				print(f'Тяжелая нога судьбы поставила вам подножку, и вы упали под ноги врагу!')
		elif act == '2':
			spells = [f'{name}' for name in player.spells.keys()]
			spell = Prompt.ask('Название заклинания: ', choices=spells, default=spells[2])

			if player.mana < player.spells[spell].mana_cost:
				print(f'У вас не хватило маны на сотворение заклинания, вам пришлось перейти в ближний бой.')
				enemy.take_damage(player.damage)
				print(f'Вы нанесли [bold red]{player.damage}[/bold red] урона врагу: {enemy.name}')
			else:
				player.mana -= player.spells[spell].mana_cost
				print(f'Вы колдуете заклинание {spell}!\n{player.spells[spell].spell_desc}')

				if player.spells[spell].spell_type == 'HEALTH':
					player.take_health(player.spells[spell].healing)
				elif player.spells[spell].spell_type == 'ATTACK':
					spell = player.spells[spell]
					enemy.take_damage(spell.spell_damage)
					print(f'Вы нанесли [bold red]{spell.spell_damage}[/bold red] урона врагу: {enemy.name}')
					
					if spell.negative_effect is not None:
						enemy.apply_negative_effect(f'{spell.negative_effect}&{spell.spell_name}', spell.spell_damage * 2)
						print(f'Вы наложили эффект "{spell.negative_effect}" на {enemy.name}')

		print(f'\n{"-" * 64}\n')

		dmg = enemy.damage_attack
		player.take_damage(dmg)
		print(f'{enemy.name} нанес вам {dmg} урона!')

		for key, value in enemy.negative_effects.items():
			enemy.take_damage(value)
			if key.split('@')[0].split('&')[0] == 'poison':
				enemy.negative_effects[key] = value * 2

			print(f'Эффект "{key.split("@")[0].split("&")[-1]}" нанес {value} урона {enemy.name}')

		print(f'\n{"-" * 64}\n')

	print(f'Враг {enemy.name} побежден! Ваш лут: {loot} монет')
	player.money += loot
	player.hp += player.hp // 10
	game_move(player)
 

def main():
	loader.print_resource_content('logo', colors=LOGO_COLORS, background='black')
	print('Мир Тандерхейма - это мрачный мир. Не каждому по силе выжить в нем. Когда-то он был процветающим миром, но некроманты и колдуны открыли таинственную цитадель, где были запечатаны древние силы зла. Они вырвались наружу, и теперь только вы надежда этого мира...')
	input('Enter to continue . . . ')
	clear()
	name = Prompt.ask("Введите ваше имя", default="Альфанелло")
	race = Prompt.ask("Выберите расу", choices=["орк", "эльф", "хоббит", "человек"], default="человек")
	player = Player(name, race)

	if name == 'АЛЬФАЧ':
		player.money = 1000000
		player.damage = 1000000
		player.lvl = 100
		player.wisdom = 1000000
		player.agility = 1000000
		player.power = 1000000
	clear()
	while True:
		print_player_panel(player)
		print(Panel('0 - выйти\n1 - начать путешествие'))

		action = Prompt.ask('Номер действия', default="1")

		if action == '0':
			print('Выход')
			break
		elif action == '-1000H':
			player.hp = 10000000000
		elif action == '-1000M':
			player.mana = 10000000000
		elif action == '+3333B':
			battle(player, multiplier=1000000)
		elif action == '1':
			chance = randint(1, 7)

			if chance == 1:
				print(f'Вы встретили город {choice(CITIES)}')
			elif chance == 2:
				print('Вы встретили небольшой магазинчик местного купца')
				shop(player)
			elif chance == 3:
				print(f'Вы едите по дороге, и вдруг на вас выпригивает огромный монстр!')
				battle(player)
			elif chance == 4:
				money = (randint(5, 10) * player.lvl) * 2 if player.race == 'хоббит' else randint(1, 5) * player.lvl
				print(f'Вы находите на дороге {money} монет. Приятно!')
				player.money += money
			else:
				print(choice(ACTIONS))

		print('\n')
		input('Нажмите Enter')

		game_move(player)

		clear()


if __name__ == '__main__':
	main()

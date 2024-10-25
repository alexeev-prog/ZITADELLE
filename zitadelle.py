#!env python
# -- coding: utf-8 --
# -*- coding: utf-8 -*-
from gamecore.resloader.loader import ResourceLoader
from gamecore.constants import LOGO_COLORS, RIP_COLORS, ACTIONS, CITIES, ENEMIES, WEAPONS
from gamecore.classes import Player, Enemy, Weapon
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich import print
from gamecore.ui import clear
from random import randint, choice

loader = ResourceLoader("res")
loader.add_resource("logo.txt", "logo")
loader.add_resource("rip.txt", "rip")

XP_FOR_UP = 100


def game_move(player):
	player.damage = player.power + player.initial_weapon.damage

	player.calc_damage()

	if not player.check_life():
		clear()
		loader.print_resource_content("rip", colors=RIP_COLORS, background="black")
		print("Ваш персонаж [red bold]погиб[/red bold].")
		exit()

	if player.xp >= XP_FOR_UP:
		player.xp += player.xp - XP_FOR_UP
		player.level_up()

	player.mana += player.mana / 100
	player.hp += player.hp / 100

	player.hp = round(player.hp, 2)
	player.mana = round(player.mana, 2)


def print_player_panel(player, skip_submenu:bool=False):
	print(
		Panel(
			f"[italic]{player.race}[/italic] [bold]{player.name.upper()}[/bold] [blue]{player.lvl} LVL/{player.xp} XP[/blue]  HP: [green]{player.hp}[/green]  СИЛА: [red]{player.power}[/red]  ЛОВКОСТЬ: [blue]{player.agility}[/blue]  МУДРОСТЬ: [magenta]{player.wisdom}[/magenta]  МАНА: [cyan]{player.mana}[/cyan]  УРОН: [red]{player.damage}[/red]  ДЕНЬГИ: [yellow]{player.money}[/yellow]", border_style='blue'
		)
	)
	if skip_submenu:
		return
	inventory_items = "\n".join(
		[f"[bold blue]{key}:[/bold blue] {value.name}" for key, value in player.inventory.items()]
	)
	spells = "\n".join([f"[bold magenta]{name}[/bold magenta] - {spell.spell_desc} ({spell.mana_cost} MANA)" for name, spell in player.spells.items()])
	print(Panel(f"[bold]Оружие[/bold]: [red]{player.initial_weapon.name} ([italic]{player.initial_weapon.damage} урона[/italic])[/red]\n[bold]Инвентарь[/bold]:\n{inventory_items}\n[bold]Заклинания[/bold]:\n{spells}", border_style='cyan'))


def shop(player):
	clear()
	weapon_name = choice(WEAPONS)
	weapon_damage = randint(5, 50)
	weapon_level = randint(1, min([player.lvl + 1, 9]))
	weapon = Weapon(weapon_name, weapon_damage, weapon_level, randint(0, 50))

	SHOP_ITEMS = {
		"0": {
			"price": 0,
			"description": "Выход из магазина бесплатный",
			"type": "exit",
		},
		f'{weapon_name}': {
			"price": (10 * weapon_damage * weapon_level) // (max([1, weapon.initial_brokenness // 10])),
			"type": 'weapon',
			'weapon': weapon,
			'description': f'По рассказам продавца, этот {weapon_name} идеальнен для вас.'
		},
		"Зелье регенерации": {
			"price": randint(10, 150) * player.lvl,
			"type": "healing",
			"healval": randint(1, 50) * player.lvl,
			"description": "Отлично лечит, но отвратительно на вкус",
		},
		"Малая колба регенерации": {
			"price": randint(10, 70) * player.lvl,
			"type": "healing",
			"healval": randint(1, 25) * player.lvl,
			"description": "Вроде лечит, но отвратительно на вкус",
		},
		"Ведро зелья регенерации": {
			"price": randint(100, 500) * player.lvl,
			"type": "healing",
			"healval": randint(50, 200) * player.lvl,
			"description": "Лечит хорошо, но отвратительно на вкус и слишком дорого",
		},
		'Зелье lehfrf': {
			"price": randint(10, 1000) * player.lvl,
			"type": "poison",
			"damageval": randint(1, 100) * player.lvl,
			"description": "Очень странное зелье, пахнет очень вкусно, но название непонятное",
		},
		"Зелье каменных пальцев": {
			"price": randint(50, 150) * player.lvl,
			"type": "damageup",
			"damageval": randint(10, 30) * player.lvl
			if player.race == "орк"
			else randint(5, 25) * player.lvl,
			"description": "Булькающее зелье силы",
		},
		"Зелье стальных кулаков": {
			"price": randint(150, 300) * player.lvl,
			"type": "damageup",
			"damageval": randint(25, 50) * player.lvl
			if player.race == "орк"
			else randint(20, 40) * player.lvl,
			"description": "Тяжелое серое зелье, от которого так и веет мощью",
		},
		"Бочка мудрости": {
			"price": randint(150, 1000) * player.lvl,
			"type": "paramup",
			"upval": randint(1, 3),
			"param": "wisdom",
			"description": "Огромная дорогая бочка, увеличивающая вашу мудрость. Ух уж эти эльфы-маркетологи",
		},
		"Бочка ловкости": {
			"price": randint(150, 1000) * player.lvl,
			"type": "paramup",
			"upval": randint(1, 3),
			"param": "agility",
			"description": "Огромная дорогая бочка, увеличивающая вашу ловкость. Ух уж эти хоббиты-маркетологи",
		},
		"Бочка силы": {
			"price": randint(150, 1000) * player.lvl,
			"type": "paramup",
			"upval": randint(1, 3),
			"param": "power",
			"description": "Огромная дорогая бочка, увеличивающая вашу силу. Ух уж эти орки-маркетологи",
		},
		"Манное зелье": {
			"price": randint(50, 150) * player.lvl,
			"type": "manaup",
			"manaval": randint(50, 150) * player.lvl
			if player.race == "эльф"
			else randint(50, 100) * player.lvl,
			"description": "Странная белая каша, которая должна увеличить вашу ману",
		},
	}

	print_player_panel(player)

	items = "\n\n".join(
		[
			f'[bold]{name}[/bold]: цена [yellow]{item["price"]}[/yellow]\n[italic]{item["description"]}[/italic]'
			for name, item in SHOP_ITEMS.items()
		]
	)

	print(Panel(f"Товары магазина:\n{items}"))

	item = Prompt.ask(
		"Товар", default="0", choices=[name for name in SHOP_ITEMS.keys()]
	)

	item = SHOP_ITEMS[item]

	if item["type"] == "exit":
		print("До новых встреч, покупатель!")
		return

	if player.money < item["price"]:
		print("У вас [bold red]не хватает денег[/bold red] на покупку этого товара")
		return
	else:
		if not Confirm.ask("Точно хотите купить данный товар?"):
			print("До новых встреч, покупатель!")
			return

		print("[green bold]Успешная покупка![/green bold]")

		player.money -= item["price"]

		if item["type"] == "healing":
			player.take_health(item["healval"])
		elif item['type'] == 'weapon':
			player.initial_weapon = item['weapon']
		elif item["type"] == "manaup":
			player.mana += item["manaval"]
		elif item["type"] == "damageup":
			player.damage += item["damageval"]
		elif item["type"] == "poison":
			player.take_damage(item["damageval"])
			print(f'[red bold]Проклятие![/red bold] Зелье отравило вас на {item["damageval"]} HP!')
		elif item["type"] == "paramup":
			if item["param"] == "wisdom":
				player.wisdom += item["upval"]
				player.mana += item["upval"]
			elif item["param"] == "agility":
				player.agility += item["upval"]
			elif item["param"] == "power":
				player.power += item["upval"]
				player.damage += item["upval"]

	game_move(player)


def battle(player, multiplier=1):
	enemy = Enemy(multiplier, player, choice(ENEMIES), randint(1, 6))
	loot = enemy.hp // 10 * (player.lvl * enemy.danger_level) * multiplier

	if player.race == "хоббит":
		loot *= 2
	if player.race == "орк":
		enemy.hp -= enemy.hp // 10

	while enemy.hp > 0 and player.hp > 0:
		print_player_panel(player, skip_submenu=True)
		print(Panel(f"Враг: [red bold]{enemy.name}[/red bold]\tHP врага: [green]{enemy.hp}[/green]", border_style='red'))
		print(
			Panel(
				"Действия:\n1 - [red italic]атаковать[/red italic]\n2 - [magenta italic]применить заклинание[/magenta italic]\n3 - [blue italic]встать в блок[/blue italic]\n4 - [dim]сбежать[/dim]\n5 - [green italic]залечить раны[/green italic]", border_style='cyan'
			)
		)

		act = Prompt.ask("Действие: ", default="1")

		if act == "1":
			damage = randint(int(player.damage), int(max([player.damage * player.lvl, player.damage * 2])))
			enemy.take_damage(damage)
			print(
				f"Вы нанесли [bold red]{damage}[/bold red] урона врагу: {enemy.name}"
			)
		elif act == '5':
			player.take_health(randint(2 * player.lvl, 20 * player.lvl) * player.lvl)
		elif act == "3":
			if randint(1, 2) == 1:
				print(
					"Вы забежали за ближайшее препятствие и [green bold]смогли обойти удар![/green bold] Вы перевели дух"
				)
				player.take_health(player.hp // 10)
				continue
			else:
				print(
					"Тяжелая нога судьбы поставила вам подножку, и [red bold]вы упали под ноги врагу![/red bold]"
				)
		elif act == "4":
			if randint(1, player.agility * enemy.danger_level) > 2 * enemy.danger_level:
				print("Вы смогли сбежать!")
				return
			else:
				print(
					"Тяжелая нога судьбы поставила вам подножку, и [red bold]вы упали под ноги врагу![/red bold]"
				)
		elif act == "2":
			spells = "\n".join([f"[bold magenta]{name}[/bold magenta] - {spell.spell_desc} ({spell.mana_cost} MANA)" for name, spell in player.spells.items()])
			print(Panel(f"[bold]Заклинания[/bold]:\n{spells}", border_style='magenta'))
			spells = [name.lower() for name in player.spells.keys()]
			spell = Prompt.ask(
				"Название заклинания", choices=spells, default=spells[0]
			)
			spell = str(spell).upper()

			print(f'\n{"*" * 32}\n')

			if player.mana < player.spells[spell].mana_cost:
				print(
					"У вас [red bold]не хватило маны[/red bold] на сотворение заклинания, вам пришлось перейти [bold]в ближний бой.[/bold]"
				)
				damage = randint(int(player.damage), int(max([player.damage * player.lvl, player.damage * 2])))
				enemy.take_damage(damage)
				print(
					f"Вы нанесли [bold red]{damage}[/bold red] урона врагу: {enemy.name}"
				)
			else:
				player.mana -= player.spells[spell].mana_cost
				print(
					f"Вы колдуете [magenta]заклинание {spell}[/magenta]!\n[italic]{player.spells[spell].spell_desc}[/italic]"
				)

				if player.spells[spell].spell_type == "HEALTH":
					player.take_health(player.spells[spell].healing)
				elif player.spells[spell].spell_type == "MANA":
					player.mana += player.spells[spell].mana
				elif player.spells[spell].spell_type == "ATTACK":
					spell = player.spells[spell]
					enemy.take_damage(spell.spell_damage)
					print(
						f"Вы нанесли [bold red]{spell.spell_damage}[/bold red] урона врагу: {enemy.name}"
					)

					if spell.negative_effect is not None:
						enemy.apply_negative_effect(
							f"{spell.negative_effect}&{spell.spell_name}",
							spell.spell_damage * 2,
						)
						print(
							f'Вы наложили эффект [bold]"{spell.negative_effect}"[/bold] на {enemy.name}'
						)

		print(f'\n{"-" * 64}\n')

		dmg = enemy.damage_attack
		player.take_damage(dmg)
		print(f"{enemy.name} [red bold]нанес вам {dmg} урона![/red bold]")

		for key, value in enemy.negative_effects.items():
			enemy.take_damage(value)
			if key.split("@")[0].split("&")[0] == "poison":
				enemy.negative_effects[key] = value * 2

			print(
				f'Эффект "{key.split("@")[0].split("&")[-1]}" [red italic]нанес {value} урона {enemy.name}[/red italic]'
			)

		print(f'\n{"-" * 64}\n')

	print(f'\n{"*" * 32}\n')

	print(f"[bold]Враг {enemy.name} [green]побежден[/green]! Ваш лут: [yellow]{loot} монет[/yellow] и [cyan]{loot // 2} XP[/cyan]![/bold]")
	player.money += loot
	player.xp += loot // 2
	player.hp += player.hp // 10
	game_move(player)


def main():
	clear()
	loader.print_resource_content("logo", colors=LOGO_COLORS, background="black")
	print(
		"Мир Тандерхейма - это мрачный мир. Не каждому по силе выжить в нем. Когда-то он был процветающим миром, но некроманты и колдуны открыли таинственную цитадель, где были запечатаны древние силы зла. Они вырвались наружу, и теперь только вы надежда этого мира..."
	)
	print(choice(ACTIONS))
	input("Enter to continue . . . ")
	clear()
	name = Prompt.ask("Введите ваше имя", default="Альфанелло")
	race = Prompt.ask(
		"Выберите расу", choices=["орк", "эльф", "хоббит", "человек"], default="человек"
	)
	player = Player(name, race)

	if name == "АЛЬФАЧ":
		player.money = 1000000
		player.damage = 1000000
		player.lvl = 100
		player.initial_weapon.damage = 1000000
		player.wisdom = 1000000
		player.agility = 1000000
		player.power = 1000000
	elif name == 'СОСУНОК':
		player.money = 1
		player.damage = 1
		player.initial_weapon.damage = 1
		player.lvl = 1
		player.wisdom = 1
		player.agility = 1
		player.power = 1
	elif name == 'УХХХ':
		player.lvl = 0
		player.xp = -10000000
	clear()
	while True:
		print_player_panel(player)
		print(Panel("0 - выйти\n1 - начать путешествие"))

		action = Prompt.ask("Номер действия", default="1")

		if action == "0":
			print("Выход")
			break
		elif action == "-1000H":
			player.hp = 10000000000
		elif action == "-1000M":
			player.mana = 10000000000
		elif action == "+3333B":
			battle(player, multiplier=1000000)
		elif action == '$CHEATS':
			ask = Prompt.ask('Выберите параметр', choices=['damage', 'level', 'xp', 'hp', 
												'power', 'wisdom', 'agility', 'money', 'mana'], default='xp')
			num = int(Prompt.ask(f'Выберите новое значение параметра "{ask}"', default=100))

			if ask == 'damage':
				player.damage = num
			elif ask == 'level':
				player.lvl = num
			elif ask == 'xp':
				player.xp = num
			elif ask == 'hp':
				player.hp = num
			elif ask == 'power':
				player.power = num
			elif ask == 'wisdom':
				player.wisdom = num
			elif ask == 'agility':
				player.agility = num
			elif ask == 'money':
				player.money = num
			elif ask == 'mana':
				player.mana = num

			player.level_up()
		elif action == "1":
			chance = randint(1, 7)

			if chance == 1:
				print(f"Вы встретили город {choice(CITIES)}")
			elif chance == 2 or chance == 3:
				print("Вы встретили небольшой магазинчик местного купца")
				shop(player)
			elif chance == 4 or chance == 5:
				print("Вы едите по дороге, и вдруг на вас выпригивает огромный монстр!")
				battle(player)
			elif chance == 6:
				money = (
					(randint(5, 10) * player.lvl) * 2
					if player.race == "хоббит"
					else randint(1, 5) * player.lvl
				)
				print(f"Вы находите на дороге {money} монет. Приятно!")
				player.money += money
			elif chance == 7:
				price = ((2 * player.lvl) * player.initial_weapon.initial_brokenness) * player.lvl
				print(f'Кузнец хочет за небольшую плату ([yellow]{price}[/yellow]) починить ваш {player.initial_weapon.name}.')
				repair = Confirm.ask(f'Вы согласны?')

				if repair:
					if player.money < price:
						print(f'У вас [red bold]не хватает средств на починку.[/red bold]')
					else:
						print('[green bold]Успешная покупка![/green bold]')
						player.money -= price
						player.initial_weapon.repair()
			elif chance == 8 and player.initial_weapon.level < 9:
				price = ((2 * player.lvl) * player.initial_weapon.initial_brokenness) * player.lvl
				print(f'Кузнец хочет за небольшую плату ([yellow]{price}[/yellow]) улучшить ваш {player.initial_weapon.name}.')
				repair = Confirm.ask(f'Вы согласны?')

				if repair:
					if player.money < price:
						print(f'У вас [red bold]не хватает средств на починку.[/red bold]')
					else:
						print('[green bold]Успешная покупка![/green bold]')
						player.money -= price
						player.initial_weapon.damage = max([1, player.initial_weapon.damage * player.initial_weapon.level // player.initial_weapon.initial_brokenness])
			else:
				print(choice(ACTIONS))

		print("\n")
		input("Нажмите Enter")

		game_move(player)

		clear()


if __name__ == "__main__":
	main()
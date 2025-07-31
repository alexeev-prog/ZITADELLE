from gamecore.resloader.loader import ResourceLoader
from gamecore.constants import *
from gamecore.classes import Player, Enemy, Weapon, Armor, Item, Quest
from rich.panel import Panel
from rich.prompt import Prompt, Confirm, IntPrompt
from rich import print
from gamecore.ui import clear, print_player_panel
from random import randint, choice
import json
import os

loader = ResourceLoader("res")
loader.add_resource("logo.txt", "logo")
loader.add_resource("rip.txt", "rip")


def game_move(player):
    player.damage = player.power + player.equipment["weapon"].value
    player.calc_additional_params()

    for passive_ability in player.passive_abilities:
        if passive_ability.param == "random_additional_param":
            chance = randint(1, 3)
            value = randint(player.lvl, passive_ability.value * player.lvl)

            if chance == 1:
                print(f"[[bold]{passive_ability.name}[/bold]] +{value} MANA")
                player.mana = min(player.max_mana, player.mana + value)
            elif chance == 2:
                print(f"[[bold]{passive_ability.name}[/bold]] +{value} MONEY")
                player.money += value
            elif chance == 3:
                print(f"[[bold]{passive_ability.name}[/bold]] +{value} XP")
                player.xp += value

    if player.is_dead():
        clear()
        loader.print_resource_content("rip", colors=RIP_COLORS, background="black")
        print("Ваш персонаж [red bold]погиб[/red bold].")
        return False

    if player.xp >= player.xp_to_next:
        player.level_up()

    player.regen_resources()
    return True


def shop(player):
    clear()
    terrain = player.terrain or choice(TERRAINS)
    terrain_effects = TERRAIN_EFFECTS.get(terrain, {})

    inflation = 1.0 + (player.lvl * 0.05)
    item_level = max(1, min(9, player.lvl + randint(-1, 2)))

    weapon_name = choice(WEAPONS)
    weapon_damage = randint(5, 50) * item_level
    weapon_element = choice([None] + ELEMENTS)
    weapon = Weapon(
        weapon_name, weapon_damage, item_level, randint(0, 50), weapon_element
    )

    armor_name = choice(ARMOR)
    armor_defense = randint(3, 20) * item_level
    armor = Armor(armor_name, armor_defense, "armor")

    SHOP_ITEMS = {
        "0": {
            "price": 0,
            "description": "Выход из магазина",
            "type": "exit",
        },
        f"{weapon_name}": {
            "price": max(
                10,
                int(
                    (15 * weapon_damage * item_level)
                    // max(1, weapon.initial_brokenness // 10)
                    * inflation
                ),
            ),
            "type": "weapon",
            "item": weapon,
            "description": f"{weapon.name} | Урон: {weapon.value:.2f} | Ур. {item_level}",
        },
        f"{armor_name}": {
            "price": int(armor_defense * 30 * player.lvl * inflation),
            "type": "armor",
            "item": armor,
            "description": f"{armor.name} | Защита: {armor.value:.2f} | Ур. {item_level}",
        },
        "Зелье здоровья": {
            "price": int(randint(25, 120) * player.lvl * inflation),
            "type": "healing",
            "healval": randint(30, 80) * player.lvl,
            "description": "Восстанавливает здоровье",
        },
        "Зелье маны": {
            "price": int(randint(20, 90) * player.lvl * inflation),
            "type": "manaup",
            "manaval": randint(25, 60) * player.lvl,
            "description": "Восстанавливает ману",
        },
        "Набор трав": {
            "price": int(randint(7, 25) * player.lvl * inflation),
            "type": "material",
            "material": "травы",
            "amount": randint(3, 7),
            "description": "Травы для крафта",
        },
        "Железный слиток": {
            "price": int(randint(15, 35) * player.lvl * inflation),
            "type": "material",
            "material": "железо",
            "amount": 1,
            "description": "Железо для крафта",
        },
        "Улучшение оружия": {
            "price": int(150 * player.lvl * inflation),
            "type": "upgrade",
            "description": "Улучшает текущее оружие",
        },
    }

    print_player_panel(player)
    print(Panel(f"[bold]Вы находитесь в:[/bold] [cyan]{terrain}[/cyan]"))

    if terrain_effects:
        print("[bold]Эффекты местности:[/bold]")
        for effect, value in terrain_effects.items():
            print(f"- {effect}: {value * 100:.2f}%")

    for passive_ability in player.passive_abilities:
        if passive_ability.param == "discount":
            value = passive_ability.value
            print(f"[[bold]СКИДКА[/bold]] {value}%")
            for item in SHOP_ITEMS.values():
                if "price" in item:
                    item["price"] = int(item["price"] * (1 - value / 100))

    items = []
    for name, item in SHOP_ITEMS.items():
        if name == "0":
            items.append(f"[bold]{name}[/bold]: {item['description']}")
        else:
            price = item.get("price", 0)
            items.append(
                f"[bold]{name}[/bold]: [yellow]{price}[/yellow] монет\n[italic]{item['description']}[/italic]"
            )

    print(Panel("\n\n".join(items), title="Товары магазина"))

    item_choice = Prompt.ask(
        "Выберите товар",
        choices=list(SHOP_ITEMS.keys()),
        default="0",
        case_sensitive=False,
    )
    item = SHOP_ITEMS[item_choice]

    if item["type"] == "exit":
        print("До новых встреч!")
        return

    if player.money < item["price"]:
        print("У вас [red bold]не хватает денег[/red bold] на покупку этого товара")
        return

    if not Confirm.ask(
        f"Купить {item_choice} за {item['price']} монет?", case_sensitive=False
    ):
        print("Покупка отменена")
        return

    print("[green bold]Успешная покупка![/green bold]")
    player.money -= item["price"]

    if item["type"] == "weapon":
        player.pickup_item(item["item"])
        print(f"Вы купили: {item['item'].name}")
    elif item["type"] == "armor":
        player.pickup_item(item["item"])
        print(f"Вы купили: {item['item'].name}")
    elif item["type"] == "healing":
        player.take_health(item["healval"])
        print(f"Вы восстановили {item['healval']} HP")
    elif item["type"] == "manaup":
        player.mana = min(player.max_mana, player.mana + item["manaval"])
        print(f"Вы восстановили {item['manaval']} маны")
    elif item["type"] == "material":
        material = item["material"]
        amount = item["amount"]
        player.crafting_materials[material] = (
            player.crafting_materials.get(material, 0) + amount
        )
        print(f"Вы получили {amount} единиц материала: {material}")
    elif item["type"] == "upgrade":
        if player.equipment["weapon"]:
            player.equipment["weapon"].level_up()
            print(
                f"[green]Оружие улучшено до уровня {player.equipment['weapon'].level}![/green]"
            )
        else:
            print("[red]У вас нет оружия для улучшения![/red]")
            player.money += item["price"]


def battle(player, enemy=None):
    if not enemy:
        terrain = choice(TERRAINS)
        enemy = Enemy(player, choice(ENEMIES), terrain)

    loot = max(10, (enemy.hp * (player.lvl * enemy.danger_level)) / 10)
    xp_gain = max(5, loot / 2)

    if player.race == "хоббит":
        loot *= 1.5
    if player.race == "орк":
        enemy.hp -= enemy.hp * 0.1

    has_fortitude = False
    fortitude = None

    for passive_ability in player.passive_abilities:
        if passive_ability.param == "health_fortitude":
            has_fortitude = True
            fortitude = passive_ability.value * player.lvl

    print(
        Panel(
            f"[bold red]БОЙ![/bold red] [cyan]{enemy.name}[/cyan] | [green]HP: {enemy.hp:.2f}[/green] | Локация: [yellow]{enemy.terrain}[/yellow]"
        )
    )

    terrain_effects = TERRAIN_EFFECTS.get(enemy.terrain, {})
    if terrain_effects:
        print("[bold]Эффекты местности:[/bold]")
        for effect, value in terrain_effects.items():
            print(f"- {effect}: {value * 100:.2f}%")

    while enemy.hp > 0:
        if player.hp <= 0 and not has_fortitude:
            break
        elif player.hp <= 0 and has_fortitude:
            print(f"[[bold]СТОЙКОСТЬ[/bold]] Вы получили {fortitude} HP!")
            player.hp = fortitude
            has_fortitude = False

        print_player_panel(player, skip_submenu=True)
        print(
            Panel(
                f"Враг: [red bold]{enemy.name}[/red bold] | [green]HP: {enemy.hp:.2f}[/green] | Опасность: {enemy.danger_level}",
                border_style="red",
            )
        )

        actions = [
            "1 - [red italic]Атаковать[/red italic]",
            "2 - [magenta italic]Заклинание[/magenta italic]",
            "3 - [blue italic]Блок[/blue italic]",
            "4 - [dim]Сбежать[/dim]",
            "5 - [green italic]Лечение[/green italic]",
            "6 - [yellow italic]Инвентарь[/yellow italic]",
            "7 - [cyan italic]Особое умение[/cyan italic]",
        ]

        print(Panel("\n".join(actions), border_style="cyan"))

        act = Prompt.ask(
            "Действие",
            choices=["1", "2", "3", "4", "5", "6", "7"],
            default="1",
            case_sensitive=False,
        )

        if act == "1":
            damage, is_crit = player.calc_damage()
            if is_crit:
                print("[bold yellow]КРИТИЧЕСКИЙ УДАР![/bold yellow]")

            element_damage_mod = 1.0
            if player.equipment["weapon"].element:
                resistance = enemy.element_resistances.get(
                    player.equipment["weapon"].element, 0
                )
                element_damage_mod = 1.0 - (resistance / 100.0)
                if resistance > 0:
                    print(
                        f"[yellow]Враг устойчив к {player.equipment['weapon'].element}![/yellow] Урон уменьшен"
                    )
                elif resistance < 0:
                    print(
                        f"[red]Враг уязвим к {player.equipment['weapon'].element}![/red] Урон увеличен"
                    )

            damage = damage * element_damage_mod
            enemy.take_damage(damage)
            print(
                f"Вы нанесли [bold red]{damage:.2f}[/bold red] урона врагу: {enemy.name}"
            )
            player.equipment["weapon"].use()
        elif act == "5":
            heal_amount = randint(5, 15) * player.lvl
            player.take_health(heal_amount)
            print(f"Вы восстановили [green]{heal_amount}[/green] HP")
        elif act == "3":
            if randint(1, 100) <= player.agility * 5:
                print("[green bold]Успешный блок![/green bold] Вы уменьшили урон")
                continue
            else:
                print("[red bold]Блок не удался![/red bold]")
        elif act == "4":
            escape_chance = player.agility * 5
            if randint(1, 100) <= escape_chance:
                print("[green]Вы успешно сбежали![/green]")
                return
            else:
                print("[red]Попытка побега не удалась![/red]")
        elif act == "6":
            if player.inventory:
                print("[bold]Инвентарь:[/bold]")
                for item_name in player.inventory:
                    print(f"- {item_name}")
                item_use = Prompt.ask(
                    "Использовать предмет",
                    choices=list(player.inventory.keys()) + ["отмена"],
                    default="отмена",
                    case_sensitive=False,
                )
                if item_use != "отмена":
                    item = player.inventory[item_use]
                    if item.type == "consumable":
                        player.take_health(item.value)
                        print(
                            f"[green]Использовано {item_use}! Восстановлено {item.value} HP[/green]"
                        )
                        player.drop_item(item_use)
                    elif item.type == "weapon" or item.type == "armor":
                        if player.equip_item(item_use):
                            print(f"[green]Экипировано: {item_use}[/green]")
            else:
                print("Ваш инвентарь пуст")
        elif act == "2":
            spells = [
                f"[bold magenta]{name}[/bold magenta] - {spell.spell_desc} ({spell.mana_cost:.2f} маны)"
                for name, spell in player.spells.items()
            ]
            print(Panel("\n".join(spells), title="Заклинания", border_style="magenta"))
            spell_choice = Prompt.ask(
                "Выберите заклинание",
                choices=list(player.spells.keys()) + ["отмена"],
                default="отмена",
                case_sensitive=False,
            )

            if spell_choice != "отмена":
                spell = player.spells[spell_choice]

                if player.mana < spell.mana_cost:
                    print("[red bold]Недостаточно маны![/red bold]")
                    continue

                player.mana -= spell.mana_cost
                print(f"Вы используете [magenta]{spell.spell_name}[/magenta]!")

                if spell.spell_type == "HEALTH":
                    player.take_health(spell.healing)
                    print(f"[green]Восстановлено {spell.healing:.2f} HP[/green]")
                elif spell.spell_type == "MANA":
                    player.mana += spell.mana
                    print(f"[cyan]Восстановлено {spell.mana:.2f} маны[/cyan]")
                elif spell.spell_type == "ATTACK":
                    damage = spell.spell_damage

                    if spell.element:
                        resistance = enemy.element_resistances.get(spell.element, 0)
                        damage_mod = 1.0 - (resistance / 100.0)
                        damage *= damage_mod

                        if resistance > 0:
                            print(
                                f"[yellow]Враг устойчив к {spell.element}![/yellow] Урон уменьшен"
                            )
                        elif resistance < 0:
                            print(
                                f"[red]Враг уязвим к {spell.element}![/red] Урон увеличен"
                            )

                    enemy.take_damage(damage)
                    print(f"Вы нанесли [bold red]{damage:.2f} урона врагу")

                    if spell_choice == "ТЕЛЕПОРТАЦИЯ":
                        print("[green]Вы телепортировались из боя![/green]")
                        return
        elif act == "7":
            if player.class_ability_available:
                player.use_class_ability(enemy)
                player.class_ability_available = False
                print(
                    f"[bold cyan]Вы использовали {player.player_class} умение![/bold cyan]"
                )
            else:
                print("[red]Особое умение недоступно![/red]")

        print(f"\n{'-' * 64}\n")

        dmg = enemy.damage_attack
        dodge_chance = 0
        for ability in player.passive_abilities:
            if ability.param == "dodge_chance":
                dodge_chance += ability.value * 100

        if randint(1, 100) <= dodge_chance:
            print(f"[green]Вы уклонились от атаки {enemy.name}![/green]")
        else:
            player.take_damage(dmg)
            print(f"{enemy.name} [red bold]нанес вам {dmg:.2f} урона![/red bold]")

        for key, value in enemy.negative_effects.items():
            effect_damage = value * randint(80, 120) / 100
            enemy.take_damage(effect_damage)
            print(
                f'Эффект "{key.split("@")[0]}" [red italic]нанес {effect_damage:.2f} урона {enemy.name}[/red italic]'
            )

        print(f"\n{'-' * 64}\n")

    if enemy.is_dead():
        print(f"[bold]Враг {enemy.name} [green]побежден[/green]![/bold]")
        print(f"Лут: [yellow]{loot:.2f} монет[/yellow] | [cyan]{xp_gain:.2f} XP[/cyan]")

        for passive_ability in player.passive_abilities:
            if passive_ability.param == "mana_loot":
                mana_gain = loot * passive_ability.value
                print(f"[[bold]МАНИЯ МАНЫ[/bold]] +{mana_gain:.2f} маны")
                player.mana = min(player.max_mana, player.mana + mana_gain)
            if passive_ability.param == "fire_damage" and player.race == "демон":
                print("[[bold]ОГНЕННАЯ АУРА[/bold]] Дополнительный урон врагу")

        player.money += loot
        player.xp += xp_gain
        player.hp += player.max_hp * 0.03
        player.class_ability_available = True

        if "некроманты" in player.quests and not player.quests["некроманты"].completed:
            if "скелет" in enemy.name.lower():
                player.quests["некроманты"].progress += 1
                if player.quests["некроманты"].progress >= 5:
                    player.complete_quest("некроманты")
    else:
        print("[red]Вы проиграли бой![/red]")
        player.money = max(0, player.money * 0.7)
        player.xp = max(0, player.xp * 0.8)
        print("[red]Вы потеряли часть денег и опыта![/red]")
        player.class_ability_available = True


def save_game(player):
    if not os.path.exists("saves"):
        os.makedirs("saves")

    filename = f"saves/{player.name.lower().replace(' ', '_')}.json"
    data = {
        "name": player.name,
        "race": player.race,
        "class": player.player_class,
        "lvl": player.lvl,
        "xp": player.xp,
        "xp_to_next": player.xp_to_next,
        "hp": player.hp,
        "max_hp": player.max_hp,
        "mana": player.mana,
        "max_mana": player.max_mana,
        "power": player.power,
        "agility": player.agility,
        "wisdom": player.wisdom,
        "money": player.money,
        "weapon": player.equipment["weapon"].name if player.equipment["weapon"] else "",
        "armor": player.equipment["armor"].name if player.equipment["armor"] else "",
        "story_progress": player.story_progress,
        "inventory": list(player.inventory.keys()),
        "quests": {
            qid: {"completed": q.completed, "progress": q.progress}
            for qid, q in player.quests.items()
        },
        "factions": player.factions,
        "crafting_materials": player.crafting_materials,
        "stats": {
            "enemies_killed": player.stats["enemies_killed"],
            "quests_completed": player.stats["quests_completed"],
            "gold_earned": player.stats["gold_earned"],
            "damage_dealt": player.stats["damage_dealt"],
        },
    }

    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

    print(f"[green]Игра сохранена в {filename}[/green]")


def load_game():
    if not os.path.exists("saves"):
        print("[red]Нет сохранений[/red]")
        return None

    saves = [f for f in os.listdir("saves") if f.endswith(".json")]
    if not saves:
        print("[red]Нет сохранений[/red]")
        return None

    print("[bold]Доступные сохранения:[/bold]")
    for i, save in enumerate(saves, 1):
        print(f"{i}. {save.replace('.json', '').replace('_', ' ')}")

    choice = IntPrompt.ask(
        "Выберите сохранение",
        choices=[str(i) for i in range(1, len(saves) + 1)],
        case_sensitive=False,
    )
    filename = f"saves/{saves[int(choice) - 1]}"

    try:
        with open(filename, "r") as f:
            data = json.load(f)

        player = Player(data["name"], data["race"], data["class"])

        player.lvl = data["lvl"]
        player.xp = data["xp"]
        player.xp_to_next = data["xp_to_next"]
        player.hp = data["hp"]
        player.max_hp = data["max_hp"]
        player.mana = data["mana"]
        player.max_mana = data["max_mana"]
        player.power = data["power"]
        player.agility = data["agility"]
        player.wisdom = data["wisdom"]
        player.money = data["money"]
        player.story_progress = data.get("story_progress", 0)
        player.factions = data.get("factions", FRACTIONS.copy())
        player.crafting_materials = data.get("crafting_materials", {})
        player.stats = data.get(
            "stats",
            {
                "enemies_killed": 0,
                "quests_completed": 0,
                "gold_earned": 0,
                "damage_dealt": 0,
            },
        )

        if data["weapon"]:
            player.equipment["weapon"] = Weapon(data["weapon"], 10)
        if data["armor"]:
            player.equipment["armor"] = Armor(data["armor"], 5)

        for item_name in data.get("inventory", []):
            if "Зелье" in item_name:
                player.inventory[item_name] = Item(
                    item_name, "consumable", randint(20, 50)
                )
            elif any(x in item_name for x in ["меч", "топор", "щит"]):
                player.inventory[item_name] = Weapon(item_name, randint(5, 15))
            else:
                player.inventory[item_name] = Item(item_name, "armor", randint(3, 10))

        for qid, qdata in data.get("quests", {}).items():
            if qid in QUESTS:
                quest_data = QUESTS[qid]
                quest = Quest(
                    name=quest_data["name"],
                    description=quest_data["description"],
                    reward=quest_data["reward"],
                    required=quest_data.get("required", 1),
                )
                quest.completed = qdata["completed"]
                quest.progress = qdata["progress"]
                player.quests[qid] = quest

        print(f"[green]Игра загружена: {player.name}[/green]")
        return player
    except Exception as e:
        print(f"[red]Ошибка загрузки: {e}[/red]")
        return None


def craft_items(player):
    if not player.crafting_materials:
        print("[red]У вас нет материалов для крафта[/red]")
        return

    print("[bold]Доступные рецепты:[/bold]")
    for i, (item_name, recipe) in enumerate(CRAFT_RECIPES.items(), 1):
        materials = ", ".join([f"{mat} x{count}" for mat, count in recipe.items()])
        print(f"{i}. {item_name} - {materials}")

    choice = IntPrompt.ask(
        "Выберите предмет для крафта",
        choices=[str(i) for i in range(0, len(CRAFT_RECIPES) + 1)],
        default=0,
        case_sensitive=False,
    )
    item_name = list(CRAFT_RECIPES.keys())[int(choice) - 1]

    if choice != 0:
        if player.craft_item(item_name):
            print(f"[green]Вы успешно скрафтили {item_name}![/green]")
        else:
            print("[red]Недостаточно материалов[/red]")


def talk_to_npc(player, npc_type):
    if npc_type not in DIALOGUES:
        return

    dialogues = DIALOGUES[npc_type]
    for i, line in enumerate(dialogues):
        print(f"[italic]{line}[/italic]")
        if i < len(dialogues) - 1:
            input("Нажмите Enter чтобы продолжить...")

    if npc_type == "капитан_стражи":
        player.complete_quest("начало")
        if "некроманты" not in player.quests:
            player.add_quest("некроманты")
            print("[green]Получен новый квест: Угроза некромантов[/green]")
    elif npc_type == "гильдия_магов":
        if "артефакт" not in player.quests:
            player.add_quest("артефакт")
            print("[green]Получен новый квест: Потерянный артефакт[/green]")
    elif npc_type == "воровская_гильдия":
        if "воровство" not in player.quests:
            player.add_quest("воровство")
            print("[green]Получен новый квест: Воровское задание[/green]")
    elif npc_type == "друид":
        if "природа" not in player.quests:
            player.add_quest("природа")
            print("[green]Получен новый квест: Защита леса[/green]")
    elif npc_type == "некромант":
        if "некромантия" not in player.quests:
            player.add_quest("некромантия")
            print("[green]Получен новый квест: Тайны некромантии[/green]")


def main():
    clear()
    loader.print_resource_content("logo", colors=LOGO_COLORS, background="black")
    print(
        "Мир Тандерхейма - мрачный мир, где древние силы зла вырвались из Цитадели Тьмы. Только вы можете спасти этот мир..."
    )
    print(choice(ACTIONS))
    input("Нажмите Enter чтобы продолжить...")

    clear()
    action = Prompt.ask(
        "1 - Новая игра\n2 - Загрузить игру",
        choices=["1", "2"],
        default="1",
        case_sensitive=False,
    )

    if action == "2":
        player = load_game()
        if not player:
            print("Создание нового персонажа")
            action = "1"

    if action == "1":
        name = Prompt.ask("Ваше имя", default="Альфанелло")
        race = Prompt.ask(
            "Раса", choices=RACES, default="человек", case_sensitive=False
        )
        player_class = Prompt.ask(
            "Класс", choices=CLASSES, default="воин", case_sensitive=False
        )
        count = 15
        current_points = count

        while True:
            print(Panel(f"[bold]Распределите {count} очков характеристик[/bold]"))
            power = IntPrompt.ask(
                f"{current_points}/{count} Сила (влияет на урон)",
                default=5,
                choices=[str(i) for i in range(0, count)],
                case_sensitive=False,
            )
            current_points -= power
            agility = IntPrompt.ask(
                f"{current_points}/{count} Ловкость (влияет на уклонение)",
                default=3,
                choices=[str(i) for i in range(0, count)],
                case_sensitive=False,
            )
            current_points -= agility
            wisdom = IntPrompt.ask(
                f"{current_points}/{count} Мудрость (влияет на ману)",
                default=2,
                choices=[str(i) for i in range(0, count)],
                case_sensitive=False,
            )
            current_points -= wisdom

            if current_points != 0:
                print(
                    f"Вы неверно распределили очки. Вы распределили {current_points} из {count}"
                )
                current_points = count
            else:
                break

        player = Player(name, race, player_class, power, agility, wisdom)

    clear()

    while True:
        player.terrain = choice(TERRAINS)
        print_player_panel(player)
        print(
            Panel(
                f"[bold]Прогресс истории:[/bold] [cyan]{player.get_story_progress()}[/cyan]"
            )
        )
        print(Panel(f"[bold]Локация:[/bold] [yellow]{player.terrain}[/yellow]"))

        actions = [
            "0 - Выход",
            "1 - Путешествовать",
            "2 - Магазин",
            "3 - Сохранить игру",
            "4 - Квесты",
            "5 - Фракции",
            "6 - Ремесло",
            "7 - Поговорить с NPC",
            "8 - Инвентарь",
        ]

        print(Panel("\n".join(actions)))
        action = Prompt.ask(
            "Выберите действие",
            choices=["0", "1", "2", "3", "4", "5", "6", "7", "8"],
            default="1",
            case_sensitive=False,
        )

        if action == "0":
            if Confirm.ask("Точно выйти из игры?"):
                print("До новых встреч!")
                break
        elif action == "1":
            event_chance = randint(1, 10)
            terrain_effects = TERRAIN_EFFECTS.get(player.terrain, {})

            if event_chance <= 4:
                print(f"Вы встретили монстра в {player.terrain}!")
                battle(player)
            elif event_chance == 5:
                city = choice(CITIES)
                print(f"Вы прибыли в {city}.")

                npc_chance = randint(1, 5)
                if npc_chance == 1:
                    print("Вы встретили капитана стражи.")
                    talk_to_npc(player, "капитан_стражи")
                elif npc_chance == 2:
                    print("Вы встретили представителя Гильдии Магов.")
                    talk_to_npc(player, "гильдия_магов")
                elif npc_chance == 3:
                    print("К вам подошел подозрительный тип из Воровской Гильдии.")
                    talk_to_npc(player, "воровская_гильдия")
                elif npc_chance == 4:
                    print("Вы встретили друида в лесу.")
                    talk_to_npc(player, "друид")
                elif npc_chance == 5:
                    print("Таинственный некромант предлагает вам сделку.")
                    talk_to_npc(player, "некромант")

                shop_chance = randint(1, 2)
                if shop_chance == 1:
                    print("Здесь есть магазин, хотите зайти?")
                    if Confirm.ask("Посетить магазин?", case_sensitive=False):
                        shop(player)
            elif event_chance == 6:
                money = randint(5, 50) * player.lvl
                print(f"Вы нашли [yellow]{money}[/yellow] монет!")
                player.money += money
                player.stats["gold_earned"] += money
            elif event_chance == 7:
                material = choice(["травы", "железо", "кожа", "кристалл"])
                amount = randint(1, 5)
                player.crafting_materials[material] = (
                    player.crafting_materials.get(material, 0) + amount
                )
                print(f"Вы нашли {amount} единиц материала: [green]{material}[/green]")
            elif event_chance == 8:
                if player.equipment["weapon"] and player.equipment["weapon"].level < 9:
                    price = randint(50, 200) * player.lvl
                    print(
                        f"Кузнец предлагает улучшить ваше оружие за [yellow]{price}[/yellow] монет"
                    )

                    if Confirm.ask("Улучшить оружие?", case_sensitive=False):
                        if player.money >= price:
                            player.money -= price
                            player.equipment["weapon"].level_up()
                            print(
                                f"[green]Оружие улучшено до уровня {player.equipment['weapon'].level}![/green]"
                            )
                        else:
                            print("[red]Недостаточно денег[/red]")
                else:
                    print("Ваше оружие уже максимального уровня или отсутствует")
            else:
                print(choice(ACTIONS))
                if (
                    "ловушки" in terrain_effects
                    and randint(1, 100) <= terrain_effects["ловушки"] * 100
                ):
                    trap_damage = player.max_hp * 0.15
                    player.take_damage(trap_damage)
                    print(
                        f"[red]Вы попали в ловушку! Получено {trap_damage:.2f} урона[/red]"
                    )

        elif action == "2":
            shop(player)
        elif action == "3":
            save_game(player)
        elif action == "4":
            if player.quests:
                print("[bold]Активные квесты:[/bold]")
                for qid, quest in player.quests.items():
                    status = (
                        "[green]Завершен[/green]"
                        if quest.completed
                        else f"[yellow]В процессе ({quest.progress}/{quest.required})[/yellow]"
                    )
                    print(f"- {quest.name}: {quest.description} {status}")
            else:
                print("У вас нет активных квестов")
        elif action == "5":
            print("[bold]Репутация с фракциями:[/bold]")
            for faction, data in player.factions.items():
                relation = data["отношение"]
                color = (
                    "green" if relation >= 70 else "yellow" if relation >= 40 else "red"
                )
                print(f"- {faction}: [{color}]{relation}[/{color}]")
        elif action == "6":
            craft_items(player)
        elif action == "7":
            npc = Prompt.ask(
                "Выберите NPC",
                choices=[
                    "капитан_стражи",
                    "гильдия_магов",
                    "воровская_гильдия",
                    "друид",
                    "некромант",
                    "отмена",
                ],
                default="отмена",
                case_sensitive=False,
            )
            if npc != "отмена":
                talk_to_npc(player, npc)
        elif action == "8":
            if player.inventory:
                print("[bold]Инвентарь:[/bold]")
                for item_name in player.inventory:
                    print(f"- {item_name}")
                item_use = Prompt.ask(
                    "Использовать предмет",
                    choices=list(player.inventory.keys()) + ["отмена"],
                    default="отмена",
                    case_sensitive=False,
                )
                if item_use != "отмена":
                    item = player.inventory[item_use]
                    if item.type == "consumable":
                        player.take_health(item.value)
                        print(
                            f"[green]Использовано {item_use}! Восстановлено {item.value} HP[/green]"
                        )
                        player.drop_item(item_use)
                    elif item.type == "weapon" or item.type == "armor":
                        if player.equip_item(item_use):
                            print(f"[green]Экипировано: {item_use}[/green]")
            else:
                print("Ваш инвентарь пуст")

        if not game_move(player):
            break

        input("\nНажмите Enter чтобы продолжить...")
        clear()


if __name__ == "__main__":
    main()

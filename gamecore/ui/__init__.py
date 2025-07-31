import os
from rich.panel import Panel
from rich import print
from rich.progress import ProgressBar


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def print_player_panel(player, skip_submenu: bool = False):
    hp_percent = player.hp / player.max_hp if player.max_hp > 0 else 0
    mana_percent = player.mana / player.max_mana if player.max_mana > 0 else 0

    hp_color = "green" if hp_percent > 0.6 else "yellow" if hp_percent > 0.3 else "red"
    mana_color = (
        "cyan" if mana_percent > 0.6 else "blue" if mana_percent > 0.3 else "magenta"
    )

    hp_bar = f"[{hp_color}]{'█' * int(20 * hp_percent)}[/{hp_color}]{'░' * int(20 * (1 - hp_percent))}"
    mana_bar = f"[{mana_color}]{'█' * int(20 * mana_percent)}[/{mana_color}]{'░' * int(20 * (1 - mana_percent))}"

    weapon = player.equipment["weapon"].name if player.equipment["weapon"] else "Нет"
    armor = player.equipment["armor"].name if player.equipment["armor"] else "Нет"

    main_panel = (
        f"[italic]{player.race.capitalize()}[/italic] [bold]{player.name.upper()}[/bold] "
        f"[blue]{player.lvl} LVL | {player.xp:.2f}/{player.xp_to_next:.2f} XP[/blue]\n"
        f"HP: [green]{player.hp:.2f}/{player.max_hp:.2f}[/green] {hp_bar}\n"
        f"Мана: [cyan]{player.mana:.2f}/{player.max_mana:.2f}[/cyan] {mana_bar}\n"
        f"СИЛА: [red]{player.power}[/red]  ЛОВКОСТЬ: [blue]{player.agility}[/blue]  МУДРОСТЬ: [magenta]{player.wisdom}[/magenta]\n"
        f"УРОН: [red]{player.damage:.2f}[/red]  ДЕНЬГИ: [yellow]{player.money}[/yellow]\n"
        f"Оружие: [red]{weapon}[/red]  Броня: [blue]{armor}[/blue]"
    )

    print(Panel(main_panel, border_style="blue"))

    if skip_submenu:
        return

    passive_abilities = (
        "\n".join(
            [
                f"[bold cyan]{ability.name}[/bold cyan] - {ability.desc}"
                for ability in player.passive_abilities
            ]
        )
        or "Нет"
    )

    inventory = (
        "\n".join(
            [f"[bold blue]{item_name}[/bold blue]" for item_name in player.inventory]
        )
        or "Пусто"
    )

    spells = "\n".join(
        [
            f"[bold magenta]{name}[/bold magenta] - {spell.spell_desc} ({spell.mana_cost:.2f} маны)"
            for name, spell in player.spells.items()
        ]
    )

    materials = (
        "\n".join(
            [
                f"[bold green]{mat}[/bold green]: {count}"
                for mat, count in player.crafting_materials.items()
            ]
        )
        or "Нет"
    )

    sub_panel = (
        f"[bold]Пассивные способности:[/bold]\n{passive_abilities}\n\n"
        f"[bold]Инвентарь:[/bold]\n{inventory}\n\n"
        f"[bold]Материалы:[/bold]\n{materials}\n\n"
        f"[bold]Заклинания:[/bold]\n{spells}"
    )

    print(Panel(sub_panel, border_style="cyan"))

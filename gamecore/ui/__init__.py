import os
from rich.panel import Panel
from rich import print


def clear():
    os.system("clear")


def print_player_panel(player, skip_submenu: bool = False):
    print(
        Panel(
            f"[italic]{player.race}[/italic] [bold]{player.name.upper()}[/bold] [blue]{player.lvl} LVL/{player.xp} XP[/blue]  HP: [green]{player.hp}[/green]  СИЛА: [red]{player.power}[/red]  ЛОВКОСТЬ: [blue]{player.agility}[/blue]	МУДРОСТЬ: [magenta]{player.wisdom}[/magenta]  МАНА: [cyan]{player.mana}[/cyan]	УРОН: [red]{player.damage}[/red]  ДЕНЬГИ: [yellow]{player.money}[/yellow]",
            border_style="blue",
        )
    )

    if skip_submenu:
        return

    passive_abilities = "\n".join(
        [
            f"[bold cyan]{ability.name}[/bold cyan] - {ability.desc}"
            for ability in player.passive_abilities
        ]
    )
    inventory_items = "\n".join(
        [
            f"[bold blue]{key}:[/bold blue] {value.name}"
            for key, value in player.inventory.items()
        ]
    )
    spells = "\n".join(
        [
            f"[bold magenta]{name}[/bold magenta] - {spell.spell_desc} ({spell.mana_cost} MANA)"
            for name, spell in player.spells.items()
        ]
    )
    print(
        Panel(
            f"[bold]Оружие[/bold]: [red]{player.initial_weapon.name} ([italic]{player.initial_weapon.damage} урона[/italic])[/red]\n[bold]Пассивные способности:\n{passive_abilities}[/bold]\n[bold]Инвентарь[/bold]:\n{inventory_items}\n[bold]Заклинания[/bold]:\n{spells}",
            border_style="cyan",
        )
    )

from pathlib import Path
from rich import print

class ResourceLoader:
    def __init__(self, resources_dir: str):
        self.resources_dir = Path(resources_dir)
        self.resources = {}

        if not self.resources_dir.exists():
            self.resources_dir.mkdir()

    def add_resource(self, filename: str, short_name: str = None):
        if short_name is None:
            short_name = filename.lower()
        self.resources[short_name] = filename

    def print_resource_content(self, short_name: str, colors: dict = {}, background: str = None):
        if short_name not in self.resources:
            return

        file_path = self.resources_dir / self.resources[short_name]
        if not file_path.exists():
            print(f"[red]Файл {file_path} не найден[/red]")
            return

        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        if colors:
            for key, value in colors.items():
                if key == "*":
                    content = f"[{value}]{content}[/{value}]"
                else:
                    content = content.replace(key, f"[{value}]{key}[/{value}]")

        if background:
            print(f"[on {background}]{content}[/on {background}]")
        else:
            print(content)

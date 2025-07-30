from pathlib import Path
from rich import print


class ResourceLoader:
    def __init__(self, resources_dir: str):
        self.resources_dir = Path(resources_dir)
        self.resources = {}

        if not self.resources_dir.exists():
            raise FileNotFoundError(
                f"Resources directory {self.resources_dir} dont exists."
            )

    def add_resource(self, filename: str, short_name: str = None):
        if short_name is None:
            short_name = filename.lower()

        self.resources[short_name] = filename

    def print_resource_content(
        self, short_name: str, colors: dict = {}, background: str = None
    ):
        if short_name not in self.resources:
            return

        with open(f"{self.resources_dir}/{self.resources[short_name]}", "r") as file:
            content = file.read()

        if colors:
            for key, value in colors.items():
                if key == "*":
                    content = f"[{value}]{content}[/{value}]"
                else:
                    content = content.replace(key, f"[{value}]{key}[/{value}]")

        print(
            f"[on {background}]{content}[/on {background}]" if background else content
        )

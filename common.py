import sys
from pathlib import Path
from typing import Union


def is_frozen() -> bool:
    return getattr(sys, 'frozen', False)


def get_resource_path(relative_path: Union[str, Path]) -> Path:
    if is_frozen():
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).parent
    return base_path / relative_path


def get_application_path() -> Path:
    if is_frozen():
        return Path(sys.executable).parent
    return Path(__file__).parent

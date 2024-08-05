#####################################################################################################

from collections.abc import Iterable
from pathlib import Path
from typing import Final

#####################################################################################################

_FIXTURE_SUFFIX: Final = '_fixture.py'

#####################################################################################################

def _dir_walk_by_path(root_path: Path) -> Iterable[Path]:
    for path in root_path.iterdir():
        if path.is_dir():
            yield from _dir_walk_by_path(path)
        else:
            yield path.resolve()

#####################################################################################################

def _load_pytest_plugins() -> Iterable[str]:
    current_path: Final = Path(__file__).parent.resolve()
    plugins: Final = []
    for module_path in _dir_walk_by_path(current_path):
        module_path_str = str(module_path.relative_to(current_path))
        if module_path_str.endswith(_FIXTURE_SUFFIX):
            plugins.append(module_path_str.replace('\\', '.').replace('/', '.')[:-3])
    return tuple(plugins)

#####################################################################################################

pytest_plugins: Final = _load_pytest_plugins()  # pylint: disable=invalid-name

#####################################################################################################

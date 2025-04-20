from pathlib import Path
from find_applicable_talent.util.path_sourcing import resolve_highest_level_occurance_in_path, ensure_path_is_dir_or_create


PROJECT_NAME = "find_applicable_talent"


def resolve_project_source() -> Path:
    """
    Resolve the project source directory.
    """
    return resolve_highest_level_occurance_in_path(Path(__file__).resolve(), PROJECT_NAME)


@ensure_path_is_dir_or_create
def resolve_component_dirs_path(component_name: str) -> Path:
    """
    Resolves the path to the directory containing the component's subdirectories.
    :param component_name: (str): The name of the component.
    :return: (Path): The path to the component's subdirectories.
    """
    return resolve_project_source() / component_name
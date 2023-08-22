from pathlib import Path
from colorama import Fore, Style


def print_red_terminal_message(message: str) -> None:
    """
    Prints the specified message to the usual output in red font.
    :param message: The message to be printed
    :return: nothing
    """
    print(Fore.RED + message + Style.RESET_ALL)


def create_dir(directory: str) -> None:
    """
    Creates the specified directory if it does not exist
    :param directory: The path/directory/folder as string
    :return: nothing
    """
    dir_as_path = Path(directory)
    if not dir_as_path.exists():
        dir_as_path.mkdir()
        print("created", directory)


from ..ui.colors import RESET, YELLOW


class Input:
    """
    Class for validating user input.
    """

    @staticmethod
    def validate(prompt: str, valid_choices: list[str]) -> str:
        """
        Instead of using nested while loops, this function uses a single while loop
        to prompt the user for input until they enter a valid selection.
        """
        while True:
            user_input = input(prompt).lower()
            if user_input in valid_choices:
                return user_input
            else:
                print(f'{YELLOW}\n\tPlease enter a valid selection.{RESET}')

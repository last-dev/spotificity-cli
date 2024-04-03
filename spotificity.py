#!/usr/bin/env python3

from src.ui.colors import GREEN, MAGENTA, RESET
from src.utils.actions import add_artist, list_artists, quit, remove_artist
from src.utils.input_validator import Input
from src.utils.setup import InitialSetup


def title() -> None:
    print(
        fr"""
{GREEN}
    ____             __     __          __
  / ___/____  ____  / /_(_) __(_)____(_) /___  __
  \__ \/ __ \/ __ \/ __/ / /_/ / ___/ / __/ / / /
 ___/ / /_/ / /_/ / /_/ / __/ / /__/ / /_/ /_/ /
/____/ .___/\____/\__/_/_/ /_/\___/_/\__/\__, /
    /_/                                 /____/                                                                      
{RESET}"""
    )


def main_menu() -> tuple[str, dict]:
    """
    Main menu where user can select what actions they want to take
    """
    title()
    menu_choices = {
        '1': {
            'choice_name': f'\n\t[{GREEN}1{RESET}] List Out Current Monitored Artists',
            'function': list_artists,
            'token_needed': False,  # Indicates function requires access token to fetch data from Spotify API
            'continue_prompt': True,  # If called from main menu, loop back to menu when done
        },
        '2': {
            'choice_name': f'\n\t[{GREEN}2{RESET}] Add New Artist to List',
            'function': add_artist,
            'token_needed': True,
            'continue_prompt': True,
        },
        '3': {
            'choice_name': f'\n\t[{GREEN}3{RESET}] Remove Artist From List',
            'function': remove_artist,
            'token_needed': False,
            'continue_prompt': True,
        },
        '4': {
            'choice_name': f'\n\t[{GREEN}4{RESET}] Quit App',
            'function': quit,
            'token_needed': False,
            'continue_prompt': False,
        },
    }

    print(f'\n\t\t {MAGENTA}MAIN MENU{RESET}')
    print('\t\t===========')

    # List out menu choices
    for choice in menu_choices:
        print(menu_choices[choice]['choice_name'])

    # Fetch user choice. Check to make sure it is a proper selection
    valid_choices: list[str] = [menu_choice_key for menu_choice_key in menu_choices.keys()]
    user_choice: str = Input.validate(
        prompt='\nWhat would you like to do? Make a selection:\n> ', valid_choices=valid_choices
    )

    return user_choice, menu_choices


def main() -> None:
    setup = InitialSetup()
    aws_profile: str = setup.aws_profile
    apigw_base_url: str = setup.endpoint
    access_token: str = setup.access_token

    # Loop whole application until user quits
    while True:
        try:
            # Extract out user choice for next action
            user_choice, menu_choices = main_menu()

            # Process user's choice
            for menu_number, action_details in menu_choices.items():
                needs_token = action_details['token_needed']
                should_continue = action_details['continue_prompt']
                action_function = action_details['function']
                    
                if user_choice == menu_number:
                    if needs_token and should_continue:
                        action_function(access_token, apigw_base_url, aws_profile, continue_prompt=True)
                    elif should_continue:
                        action_function(apigw_base_url, aws_profile, continue_prompt=True)
                    else:
                        action_function()
        except KeyboardInterrupt:
            quit()


if __name__ == '__main__':
    main()

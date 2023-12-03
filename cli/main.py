#!/usr/bin/python3

from actions.actions import (
    get_valid_user_input,
    remove_artist,
    request_token,
    list_artists,
    add_artist,
    quit
)
from ui.colors import Style
import subprocess

def title() -> None:
    subprocess.run(['clear', '-x'])
    print(f"""{Style.GREEN}
    ____             __     __          __
  / ___/____  ____  / /_(_) __(_)____(_) /___  __
  \__ \/ __ \/ __ \/ __/ / /_/ / ___/ / __/ / / /
 ___/ / /_/ / /_/ / /_/ / __/ / /__/ / /_/ /_/ / 
/____/ .___/\____/\__/_/_/ /_/\___/_/\__/\__, /  
    /_/                                 /____/                                                                                         
{Style.RESET}""")


def main_menu() -> tuple[str, dict]:
    """
    Main menu where user can select what actions they want to take
    """
    
    title()
    menu_choices = {
        '1': {
            "choice_name": f"\n\t[{Style.GREEN}1{Style.RESET}] List Out Current Monitored Artists", 
            "function": list_artists,
            "token_needed": False,  # Indicates function requires access token to fetch data from Spotify API
            "continue_prompt": True  # If called from main menu, loop back to menu when done
        },
        '2': {
            "choice_name": f"\n\t[{Style.GREEN}2{Style.RESET}] Add New Artist to List", 
            "function": add_artist,
            "token_needed": True,
            "continue_prompt": True
        },
        '3': {
            "choice_name": f"\n\t[{Style.GREEN}3{Style.RESET}] Remove Artist From List", 
            "function": remove_artist,
            "token_needed": False,
            "continue_prompt": True
        },
        '4': {
            "choice_name": f"\n\t[{Style.GREEN}4{Style.RESET}] Quit App", 
            "function": quit,
            "token_needed": False,
            "continue_prompt": False
        },
    }
    
    print(f"\n\t\t {Style.LIGHT_MAGENTA}MAIN MENU{Style.RESET}")
    print("\t\t===========")

    # List out menu choices
    for choice in menu_choices:
        print(menu_choices[choice]["choice_name"])
    
    # Fetch user choice. Check to make sure it is a proper selection
    valid_choices: list[str] = [menu_choice_key for menu_choice_key in menu_choices.keys()]
    user_choice = get_valid_user_input(
        prompt='\nWhat would you like to do? Make a selection:\n> ',
        valid_choices=valid_choices
    )

    return user_choice, menu_choices

def main() -> None:
    
    # Immediately get access token
    access_token = request_token() 
    
    # Loop whole application until user quits
    while True:
        try:
            # Extract out user choice for next action
            user_choice, menu_choices = main_menu()
            
            # If user choice needs a token, pass it to the function
            # If user choice needs to loop back to main menu after execution, pass in True for continue_prompt
            for menu_item_num, menu_item_value in menu_choices.items():
                if user_choice == menu_item_num and menu_item_value["token_needed"] == True and menu_item_value["continue_prompt"] == True:
                    menu_item_value["function"](access_token, continue_prompt=True)
                elif user_choice == menu_item_num and menu_item_value["continue_prompt"] == True:
                    menu_item_value["function"](continue_prompt=True)                
                elif user_choice == menu_item_num:
                    menu_item_value["function"]()
        except KeyboardInterrupt:
            quit()

if __name__ == "__main__":
    main()
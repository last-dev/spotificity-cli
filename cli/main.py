#!/usr/bin/python3

from ui.colors import Colors, print_colors, colorfy
from actions.actions import (
    list_artists,
    add_artist,
    remove_artist,
    request_token,
    quit
)
import subprocess

def title() -> None:
    subprocess.run(['clear', '-x'])
    print("""\033[32m
    ____             __     __          __
  / ___/____  ____  / /_(_) __(_)____(_) /___  __
  \__ \/ __ \/ __ \/ __/ / /_/ / ___/ / __/ / / /
 ___/ / /_/ / /_/ / /_/ / __/ / /__/ / /_/ /_/ / 
/____/ .___/\____/\__/_/_/ /_/\___/_/\__/\__, /  
    /_/                                 /____/                                                                                         
\033[0m""")


def main_menu() -> tuple[int, dict]:
    """
    Main menu where user can select what actions they want to take
    """
    
    title()
    menu_choices = {
        1: {
            "choice_name": f"\n\t[{colorfy(Colors.GREEN, '1')}] List Out Current Monitored Artists", 
            "function": list_artists,
            "token_needed": False,  # Indicates function requires access token to fetch data from Spotify API
            "continue_prompt": True  # If called from main menu, loop back to menu when done
            },
        2: {
            "choice_name": f"\n\t[{colorfy(Colors.GREEN, '2')}] Add New Artist to List", 
            "function": add_artist,
            "token_needed": True,
            "continue_prompt": True
            },
        3: {
            "choice_name": f"\n\t[{colorfy(Colors.GREEN, '3')}] Remove Artist From List", 
            "function": remove_artist,
            "token_needed": False,
            "continue_prompt": True
            },
        4: {
            "choice_name": f"\n\t[{colorfy(Colors.GREEN, '4')}] Quit App", 
            "function": quit,
            "token_needed": False,
            "continue_prompt": False
            },
    }
    
    print(f"\n\t\t {colorfy(Colors.LIGHT_MAGENTA, 'MAIN MENU')}")
    print("\t\t===========")

    # List out menu choices
    for choices in menu_choices:
        print(menu_choices[choices]["choice_name"])
    
    # Fetch user choice. Check to make sure it is a proper selection
    while True:
        try:
            user_choice = int((input("\nWhat would you like to do? Make a selection:\n> ")))
            if user_choice in list(range(1, len(menu_choices.keys()) + 1)):
                return user_choice, menu_choices
            else:
                raise ValueError
        except ValueError:
            print_colors(Colors.YELLOW, "\n\tPlease enter a valid selection.")


def main() -> None:
    
    # Immediately get access token
    access_token = request_token() 
    
    # Loop whole application until user quits
    while True:
        try:
            # Extract out user choice for next action
            user_choice, menu_choices = main_menu()
            
            # If user choice needs a token, pass it to the function
            # If user choice needs to loop back to main menu once executed, pass in continue_prompt=True
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
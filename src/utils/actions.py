import json
from random import choice

from ..exceptions.error_handling import (
    FailedToAddArtistToTable,
    FailedToRemoveArtistFromTable,
    FailedToRetrieveListOfMatchesWithIDs,
    FailedToRetrieveMonitoredArtists,
)
from ..ui.colors import GREEN, RED, RESET, YELLOW
from ..utils.input_validator import Input
from .signed_requests import Requests

YES_CHOICES = ['y', 'yes', 'yeah', 'yup', 'yep', 'yea', 'ya', 'yah']
NO_CHOICES = ['n', 'no', 'nope', 'nah', 'naw', 'na']
GO_BACK_CHOICES = ['b', 'back']
CACHED_ARTIST_LIST: list = []  # Local memory storage of the current artists I am monitoring
IS_CACHE_EMPTY: bool = False


def list_artists(apigw_endpoint: str, aws_profile: str, continue_prompt=False) -> None:
    """
    Prints out a list of the current artists that are being monitored

    Parameters:
        - continue_prompt (boolean): Whether the user is returned with the main menu after function execution or not.
    """

    global CACHED_ARTIST_LIST, IS_CACHE_EMPTY

    # Check if either the cache has items or the `IS_CACHE_EMPTY` flag is set to True
    # If neither is true, invoke Lambda to fetch fresh data
    if len(CACHED_ARTIST_LIST) > 0 or IS_CACHE_EMPTY:
        if CACHED_ARTIST_LIST:
            for index, artist in enumerate(CACHED_ARTIST_LIST, start=1):
                print(f'\n\t[{GREEN}{index}{RESET}] {artist["artist_name"]}')
        else:
            print(f'{YELLOW}\n\tNo artists currently being monitored.{RESET}')
    else:
        # Fetch fresh data
        response = Requests.signed_request('GET', f'{apigw_endpoint}artist', aws_profile)

        if response.status_code == 204:
            print(f'{YELLOW}\n\tNo artists currently being monitored.{RESET}')
            CACHED_ARTIST_LIST = []
            IS_CACHE_EMPTY = True
            return None

        response_data: dict = response.json()
        if response_data.get('error_type') == 'Client':
            raise FailedToRetrieveMonitoredArtists(response_data['error'])

        print('\nCurrent monitored artists:')
        list_of_names: list[str] = response_data['artists']['current_artists_names']
        for index, artist in enumerate(list_of_names, start=1):
            print(f'\n\t[{GREEN}{index}{RESET}] {artist}')

        CACHED_ARTIST_LIST = response_data['artists']['current_artists_with_id']
        IS_CACHE_EMPTY = False

    menu_loop_prompt(continue_prompt)


def fetch_artist_id(
    artist_name: str, access_token: str, apigw_endpoint: str, aws_profile: str
) -> tuple[str, str] | None:
    """
    Queries Spotify API for the Spotify ID of the requested artist. Spotify ID of the artist
    is needed to fetch the latest musical releases.
    User is asked to confirm Spotify returned the correct artist they were looking for.

    Parameters:
        - artist_name (str): Name of the artist that the user wants to add to monitored list
        - access_token (str): Required authenticated Spotify access token to send in API request

    Returns:
        tuple[str, str]: A tuple containing the confirmed artist's Spotify ID and name
    """

    payload = json.dumps({'artist_name': artist_name, 'access_token': access_token})
    response = Requests.signed_request('POST', f'{apigw_endpoint}artist/id', aws_profile, payload=payload.encode())

    # Catch any errors that occurred during GET request to Spotify API.
    if response.json().get('error_type') == 'HTTP':
        raise FailedToRetrieveListOfMatchesWithIDs(response.json()['error'])
    elif len(response.json()['artistSearchResultsList']) == 0:
        raise FailedToRetrieveListOfMatchesWithIDs('No artists found that closely match your search.')

    first_artist_guess = {
        'artist_id': response.json()['artistSearchResultsList'][0]['id'],
        'artist_name': response.json()['artistSearchResultsList'][0]['name'],
    }

    # Serve user the most likely artist they were looking for. Ask for confirmation
    answer = Input.validate(
        prompt=f'\nIs {GREEN}{first_artist_guess["artist_name"]}{RESET} the artist you were looking for? (yes or no)\n> ',
        valid_choices=(YES_CHOICES + NO_CHOICES),
    )

    # If the user confirmed the artist, return the most likely artist's Spotify ID and name
    if answer in YES_CHOICES:
        return first_artist_guess['artist_id'], first_artist_guess['artist_name']
    elif answer in NO_CHOICES:

        # Print list of the other most likely choices and have them choose
        for index, artist in enumerate(response.json()['artistSearchResultsList'], start=1):
            print(f'\n[{GREEN}{index}{RESET}]')
            print(f'\tArtist: {artist["name"]}')

            # Format genres into a string
            genres = artist['genres']
            if genres:
                genres_str = ', '.join(genre.title() for genre in genres)
            else:
                genres_str = 'N/A'

            # Print out genres for each choice to help add context to user
            print(f'\tGenre(s): {genres_str}')

        # Prompt user for artist choice again
        user_choice = Input.validate(
            prompt=f'\nWhich artist were you looking for? Select the number. (or enter {YELLOW}`back`{RESET} to return to search prompt)\n> ',
            valid_choices=[
                str(option_index)
                for option_index, artist in enumerate(response.json()['artistSearchResultsList'], start=1)
            ]
            + GO_BACK_CHOICES,
        )

        # If user choice matches an option, then return that artist's Spotify ID and name
        for option_index, artist in enumerate(response.json()['artistSearchResultsList'], start=1):
            if user_choice in GO_BACK_CHOICES:
                return None
            elif int(user_choice) == option_index:
                return artist['id'], artist['name']


def add_artist(access_token: str, apigw_endpoint: str, aws_profile: str, continue_prompt=False) -> None:
    """
    Prompts user for which artist they want to add to be monitored.
    Then invokes a Lambda function that adds the artist to a list.

    Parameters:
        - access_token (str): Required authenticated Spotify access token to send in API request
        - continue_prompt (boolean): Whether the user is returned with the main menu after function execution or not.
    """

    global CACHED_ARTIST_LIST

    while True:

        # Show user a list of the artist they are already monitoring and then
        # ask user for which artist they want to search for
        list_artists(apigw_endpoint, aws_profile)
        user_artist_choice = input("\nWhich artist would you like to start monitoring?\n> ")

        # Query Spotify API to get a list of the closest matches to the user's search
        # User will be asked to confirm
        result = fetch_artist_id(user_artist_choice, access_token, apigw_endpoint, aws_profile)

        # Restart while loop since user wanted a new search
        if result is None:
            continue

        # If user confirmed, then prepare payload to be sent to Lambda function
        artist_id, artist_name = result
        artist = {'artist_id': artist_id, 'artist_name': artist_name}

        # Find out if artist is already in list. If not, add the artist
        if artist in CACHED_ARTIST_LIST:
            print(f'\nYou\'re already monitoring {GREEN}{artist_name}{RESET}!')
        else:
            payload = json.dumps(artist)
            response = Requests.signed_request('POST', f'{apigw_endpoint}artist', aws_profile, payload=payload.encode())

            # Catch any errors that occurred during PUT request on the DynamoDB table.
            if response.json().get('error_type') == 'Client':
                raise FailedToAddArtistToTable(response.json()['error'])
            else:

                # Update cache with new addition
                CACHED_ARTIST_LIST.append(artist)
                print(f'\n\tYou are now monitoring for {GREEN}{artist_name}{RESET}\'s new music!')
                break

    menu_loop_prompt(continue_prompt)


def remove_artist(apigw_endpoint: str, aws_profile: str, continue_prompt=False) -> None:
    """
    Removes an artist from being monitored

    Parameter:
        - continue_prompt (boolean): Whether the user is returned with the main menu after function execution or not.
    """

    global CACHED_ARTIST_LIST

    # If there are currently no artists to remove, then exit the function
    list_artists(apigw_endpoint, aws_profile)
    if not CACHED_ARTIST_LIST:
        print(f"{YELLOW}\n\tThere are no artists to remove!{RESET}")
        menu_loop_prompt(continue_prompt)
        return

    # Otherwise, ask them which artist they would like to remove
    user_choice = Input.validate(
        prompt=f'\nWhich artist would you like to remove? Make a selection: (or enter {YELLOW}`back`{RESET} to return to main menu)\n> ',
        valid_choices=[str(choice_index) for choice_index, artist in enumerate(CACHED_ARTIST_LIST, start=1)]
        + GO_BACK_CHOICES,
    )

    for choice_index, artist in enumerate(CACHED_ARTIST_LIST, start=1):
        if user_choice in GO_BACK_CHOICES:
            return
        elif int(user_choice) == choice_index:
            payload = json.dumps(
                {
                    'artist_id': CACHED_ARTIST_LIST[int(user_choice) - 1]['artist_id'],
                    'artist_name': CACHED_ARTIST_LIST[int(user_choice) - 1]['artist_name'],
                }
            )
            response = Requests.signed_request(
                'DELETE', f'{apigw_endpoint}artist', aws_profile, payload=payload.encode()
            )

            # Catch any errors that occurred during DELETE request on the DynamoDB table.
            if response.json().get('error_type') == 'Client':
                raise FailedToRemoveArtistFromTable(response.json()['error'])
            else:

                # Update cache by removing artist
                CACHED_ARTIST_LIST.pop(int(user_choice) - 1)
                print(f"\n\tRemoved {GREEN}{artist['artist_name']}{RESET} from list!")

    menu_loop_prompt(continue_prompt)


def quit() -> None:
    """
    Quits the application with a custom exit message
    """
    goodbye_list = [
        'goodbye',
        "see ya\'",
        'bye bye',
        'bye',
        'au revoir',  # French
        'adiós',  # Spanish
        'auf Wiedersehen',  # German
        'arrivederci',  # Italian
    ]
    print(f'{RED}\n\tQuitting App! {choice(goodbye_list).title()}!')
    exit()


def menu_loop_prompt(continue_prompt: bool) -> None:
    """
    If True is passed in, user will be prompted to continue to main menu.
    Otherwise, app will quit
    """
    quit_choices = ['q', 'quit', 'exit', 'done']
    go_back_choices = ['b', 'back', '']

    if continue_prompt:
        user_choice = Input.validate(
            prompt=f"\nPress {GREEN}[ENTER]{RESET} to go back to main menu... (Or enter {YELLOW}quit{RESET} to quit app)\n> ",
            valid_choices=(quit_choices + go_back_choices),
        )

        if user_choice in quit_choices:
            quit()
        elif user_choice in go_back_choices:
            return

from exceptions.error_handling import (
    FailedToRetrieveToken, 
    FailedToRetrieveMonitoredArtists,
    FailedToRetrieveListOfMatchesWithIDs,
    ExceptionDuringLambdaExecution,
    FailedToAddArtistToTable,
    FailedToRemoveArtistFromTable
)
from ui.colors import Colors, print_colors, colorfy
from botocore.exceptions import ClientError
from random import choice
import boto3
import json

# Local memory storage of the current artists I am monitoring
CACHED_ARTIST_LIST: list = []
IS_CACHE_EMPTY: bool = False

def request_token() -> str:
    """
    Invoke Lambda function that fetches an access token from the Spotify 
    `/token/` API. 
    """    
    
    lambda_name = 'GetAccessTokenHandler'
    
    try:
        lambda_ = boto3.client('lambda')
        response: dict = lambda_.invoke(
            FunctionName=lambda_name,
            InvocationType='RequestResponse'
        )
    except ClientError as err:
        print_colors(Colors.RED, f'Client Error Message: \n\t{err.response["Error"]["Code"]}\n\t{err.response["Error"]["Message"]}')
        raise
    except Exception as err:
        print_colors(Colors.RED, f'Other error occurred: \n\n{err}')
        raise
    else:
        
        # Convert botocore.response.StreamingBody object to dict
        returned_json: dict = json.load(response['Payload'])
        
        # Raise exception if payload is None, otherwise return access token
        if returned_json.get('access_token') is None:
            raise FailedToRetrieveToken
        else:
            return returned_json['access_token']


def get_valid_user_input(prompt: str, valid_choices: list[str]) -> str:
    """
    Instead of using nested while loops, this function uses a single while loop
    to prompt the user for input until they enter a valid selection. 
    """
    while True:
        user_input = input(prompt).lower()
        if user_input in valid_choices:
            return user_input
        else:
            print_colors(Colors.YELLOW, '\n\tPlease enter a valid selection.')


def list_artists(continue_prompt=False) -> None:
    """
    Prints out a list of the current artists that are being monitored
    """

    global CACHED_ARTIST_LIST, IS_CACHE_EMPTY
    lambda_name = 'FetchArtistsHandler'

    # Check if either the cache has items or the `IS_CACHE_EMPTY` flag is set to True
    # If neither is true, invoke Lambda to fetch fresh data
    if len(CACHED_ARTIST_LIST) > 0 or IS_CACHE_EMPTY:
        if CACHED_ARTIST_LIST:
            for index, artist in enumerate(CACHED_ARTIST_LIST, start=1):
                print(f'\n\t[{colorfy(Colors.LIGHT_GREEN, str(index))}] {artist["artist_name"]}')
        else:
            print_colors(Colors.YELLOW, '\n\tNo artists currently being monitored.')
    else: 
        
        # Invoke Lambda to fetch fresh data
        try:
            lambda_ = boto3.client('lambda')
            response = lambda_.invoke(
                FunctionName=lambda_name,
                InvocationType='RequestResponse'
            )    
        except ClientError as err:
            print_colors(Colors.RED, f'Client Error Message: \n\t{err.response["Error"]["Code"]}\n\t{err.response["Error"]["Message"]}')
            raise
        except Exception as err:
            print_colors(Colors.RED, f'Other error occurred: \n\n{err}')
            raise
        else:

            # Convert botocore.response.StreamingBody object to dict
            returned_payload: dict = json.load(response['Payload'])

            # Catch any errors that occurred during `FetchArtistsHandler` execution
            if returned_payload.get('errorMessage'):
                raise ExceptionDuringLambdaExecution(lambda_name, returned_payload['errorMessage'])

            # Catch any errors that occurred during scan operation on DynamoDB table. 
            elif returned_payload['payload'].get('error'):
                raise FailedToRetrieveMonitoredArtists(returned_payload['payload']['error'])
            
           # Print out list of artists
            elif returned_payload['status_code'] == 204:
                print_colors(Colors.YELLOW, '\n\tNo artists currently being monitored.')
                
                # Update cache to be an empty list  
                CACHED_ARTIST_LIST = []
                IS_CACHE_EMPTY = True
            else:
                print('\nCurrent monitored artists:')
                list_of_names: list[str] = returned_payload['payload']['artists']['current_artists_names']
                
                # Print out list of current artists
                for index, artist in enumerate(list_of_names, start=1):
                    print(f'\n\t[{colorfy(Colors.LIGHT_GREEN, str(index))}] {artist}')

                # Update cache with current artists list
                CACHED_ARTIST_LIST = returned_payload['payload']['artists']['current_artists_with_id']
                IS_CACHE_EMPTY = False

    menu_loop_prompt(continue_prompt)


def fetch_artist_id(artist_name: str, access_token: str) -> tuple[str, str] | None:
    """
    Queries Spotify API for close matches to the users search
    Also returns each potential artist's Spotify ID.
    """

    # Prep payload
    lambda_name = 'GetArtist-IDHandler'
    payload = json.dumps({
        'artist_name': artist_name,
        'access_token': access_token    
    })
    
    try:
        lambda_ = boto3.client('lambda')
        response = lambda_.invoke(
            FunctionName=lambda_name,
            InvocationType='RequestResponse',
            Payload=payload.encode()
        )    
    except ClientError as err:
        print_colors(Colors.RED, f'Client Error Message: \n\t{err.response["Error"]["Code"]}\n\t{err.response["Error"]["Message"]}')
        raise
    except Exception as err:
        print_colors(Colors.RED, f'Other error occurred: \n\n{err}')
        raise
    else:
        
        # Convert botocore.response.StreamingBody object to dict
        returned_payload: dict = json.load(response['Payload'])
        
        # Catch any errors that occurred during `GetArtist-IDHandler` execution
        if returned_payload.get('errorMessage'):
            raise ExceptionDuringLambdaExecution(lambda_name, returned_payload['errorMessage'])
        
        # Catch any errors that occurred during GET request to Spotify API. 
        elif returned_payload['payload'].get('error'):
            raise FailedToRetrieveListOfMatchesWithIDs(returned_payload['payload']['error'])

        first_artist_guess = {
            'artist_id': returned_payload['payload']['artistSearchResultsList'][0]['id'],
            'artist_name': returned_payload['payload']['artistSearchResultsList'][0]['name']
        }

        # Define valid choices for user to enter
        yes_choices = ['y', 'yes', 'yeah', 'yup', 'yep', 'yea', 'ya', 'yah']
        no_choices = ['n', 'no', 'nope', 'nah', 'naw', 'na']
        go_back_choices = ['b', 'back']
        
        # Serve user the most likely artist they were looking for. Ask for confirmation
        answer = get_valid_user_input(
            prompt=f'\nIs {colorfy(Colors.LIGHT_GREEN, first_artist_guess["artist_name"])} the artist you were looking for? (yes or no)\n> ',
            valid_choices=(yes_choices + no_choices)
        )
        
        # If the user entered a valid selection, then return the most likely artist's Spotify ID and name
        if answer in yes_choices:
            return first_artist_guess['artist_id'], first_artist_guess['artist_name']
        elif answer in no_choices:
            
            # Print list of the other most likely choices and have them choose
            for index, artist in enumerate(returned_payload['payload']['artistSearchResultsList'], start=1):
                print(f'\n[{colorfy(Colors.LIGHT_GREEN, str(index))}]')
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
            user_choice = get_valid_user_input(
                prompt=f'\nWhich artist were you looking for? Select the number. (or enter `b` or `back` to return to search prompt)\n> ',
                valid_choices=[
                    str(option_index) for option_index, artist in enumerate(returned_payload['payload']['artistSearchResultsList'], start=1)
                ] + go_back_choices
            )              
            
            # If user choice matches an option, then return that artist's Spotify ID and name
            for option_index, artist in enumerate(returned_payload['payload']['artistSearchResultsList'], start=1):
                if int(user_choice) == option_index:
                    return artist['id'], artist['name']  
                
                # Otherwise, send user back to search menu if they enter `b` or `back`
                elif user_choice in go_back_choices:
                    return None                    


def add_artist(access_token: str, continue_prompt=False) -> None:
    """
    Prompts user for which artist they want to add to be monitored. 
    Then invokes a Lambda function that adds the artist to a list.
    """
    
    global CACHED_ARTIST_LIST
    lambda_name = 'AddArtistsHandler'

    while True:
        
        # Ask user for which artist they want to search for 
        list_artists()
        user_artist_choice = input("\nWhich artist would you like to start monitoring?\n> ")

        # Queries Spotify API to get a list of the closest matches to the user's search
        # User will be asked to confirm
        result = fetch_artist_id(user_artist_choice, access_token)
        
        # Restart while loop since user wanted a new search
        if result is None:
            continue
        
        # If user confirmed, then prepare payload to be sent to Lambda function
        artist_id, artist_name = result
        artist = {'artist_id': artist_id, 'artist_name': artist_name}
        
        # Find out if artist is already in list. If not, add the artist
        if artist in CACHED_ARTIST_LIST:
            print(f'\nYou\'re already monitoring {colorfy(Colors.LIGHT_GREEN, artist_name)}!')
        else:
            
            # Prep payload
            payload = json.dumps({
                'artist_id': artist_id,
                'artist_name': artist_name  
            })
            
            try:
                lambda_ = boto3.client('lambda')
                response = lambda_.invoke(
                    FunctionName=lambda_name,
                    InvocationType='RequestResponse',
                    Payload=payload.encode()
                )    
            except ClientError as err:
                print_colors(Colors.RED, f'Client Error Message: \n\t{err.response["Error"]["Code"]}\n\t{err.response["Error"]["Message"]}')
                raise
            except Exception as err:
                print_colors(Colors.RED, f'Other error occurred: \n\n{err}')
                raise
            else:

                # Convert botocore.response.StreamingBody object to dict
                returned_payload: dict = json.load(response['Payload'])

                # Catch any errors that occurred during `GetArtist-IDHandler` execution
                if returned_payload.get('errorMessage'):
                    raise ExceptionDuringLambdaExecution(lambda_name, returned_payload['errorMessage'])

                # Catch any errors that occurred during PUT request on the DynamoDB table.
                elif returned_payload['payload'].get('error'):
                    raise FailedToAddArtistToTable(returned_payload['payload']['error'])
                else:

                    # Update cache with new addition
                    CACHED_ARTIST_LIST.append(artist)
                    print(f'\n\tYou are now monitoring for {colorfy(Colors.LIGHT_GREEN, artist_name)}\'s new music!')
                    break
                
    menu_loop_prompt(continue_prompt)


def remove_artist(continue_prompt=False) -> None:
    """
    Removes an artist from the monitored list
    """
    
    global CACHED_ARTIST_LIST
    lambda_name = 'RemoveArtistsHandler'

    # If there are currently no artists to remove, then exit the function
    list_artists()
    if not CACHED_ARTIST_LIST:
        print_colors(Colors.YELLOW, "\n\tThere are no artists to remove!")
        menu_loop_prompt(continue_prompt)
        return

    # Otherwise, ask them which artist they would like to remove
    go_back_choices = ['b', 'back']
    user_choice = get_valid_user_input(
        prompt='\nWhich artist would you like to remove? Make a selection: (or enter `b` or `back` to return to main menu)\n> ',
        valid_choices=[
            str(choice_index) for choice_index, artist in enumerate(CACHED_ARTIST_LIST, start=1)
        ] + go_back_choices
    )

    for choice_index, artist in enumerate(CACHED_ARTIST_LIST, start=1):
        if user_choice in go_back_choices:
            return
        elif int(user_choice) == choice_index:
            
            # Prep payload to be sent to Lambda function
            payload = json.dumps({
                'artist_id': CACHED_ARTIST_LIST[int(user_choice) - 1]['artist_id'],
                'artist_name': CACHED_ARTIST_LIST[int(user_choice) - 1]['artist_name']
            })

            # Invoke a lambda function that performs a DELETE request on the DynamoDB table.
            try:
                lambda_ = boto3.client('lambda')
                response = lambda_.invoke(
                    FunctionName=lambda_name,
                    InvocationType='RequestResponse',
                    Payload=payload.encode()
                    )
            except ClientError as err:
                print_colors(Colors.RED, f'Client Error Message: \n\t{err.response["Error"]["Code"]}\n\t{err.response["Error"]["Message"]}')
                raise
            except Exception as err:
                print_colors(Colors.RED, f'Other error occurred: \n\n{err}')
                raise
            else:
                
                # Convert botocore.response.StreamingBody object to dict
                returned_payload: dict = json.load(response['Payload'])

                # Catch any errors that occurred during `RemoveArtistsHandler` execution
                if returned_payload.get('errorMessage'):
                    raise ExceptionDuringLambdaExecution(lambda_name, returned_payload['errorMessage'])

                # Catch any errors that occurred during DELETE request on the DynamoDB table.
                elif returned_payload['payload'].get('error'):
                    raise FailedToRemoveArtistFromTable(returned_payload['payload']['error'])
                else:
                    
                    # Update cache by removing artist
                    CACHED_ARTIST_LIST.pop(int(user_choice) - 1)
                    print(f"\n\tRemoved {colorfy(Colors.LIGHT_GREEN, artist['artist_name'])} from list!")

    menu_loop_prompt(continue_prompt)
    

def quit() -> None:
    """
    Quits the application with a custom exit message
    """
    
    goodbye_list = [
        'goodbye',
        "see ya\n'",
        'bye bye',
        'bye',
        'au revoir',  # French
        'adiós',  # Spanish
        'auf Wiedersehen',  # German
        'arrivederci',  # Italian
    ]
    print_colors(Colors.RED, f'\n\tQuitting App! {choice(goodbye_list).title()}!')
    exit()


def menu_loop_prompt(continue_prompt: bool) -> None:
    """
    If True is passed in, user will be prompted to continue to main menu.
    Otherwise, app will quit
    """

    quit_choices = ['q', 'quit', 'exit', 'done']
    go_back_choices = ['b', 'back', '']
    
    if continue_prompt:
        user_choice = get_valid_user_input(
            prompt=f"\nPress {colorfy(Colors.LIGHT_GREEN, '[ENTER]')} to go back to main menu... (Or enter {colorfy(Colors.YELLOW, 'quit')} to quit app)\n> ",
            valid_choices=(quit_choices + go_back_choices)
        )

        if user_choice in quit_choices:
            quit() 
        elif user_choice in go_back_choices:
            return
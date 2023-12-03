from exceptions.error_handling import (
    FailedToRetrieveListOfMatchesWithIDs,
    FailedToRetrieveMonitoredArtists,
    ExceptionDuringLambdaExecution,
    FailedToRemoveArtistFromTable,
    FailedToAddArtistToTable,
    FailedToRetrieveEndpoint,
    FailedToRetrieveToken
)
from botocore.exceptions import ClientError
from requests_aws4auth import AWS4Auth
from ui.colors import Style
from random import choice
import requests
import boto3
import json
import os

YES_CHOICES = ['y', 'yes', 'yeah', 'yup', 'yep', 'yea', 'ya', 'yah']
NO_CHOICES = ['n', 'no', 'nope', 'nah', 'naw', 'na']
GO_BACK_CHOICES = ['b', 'back']
CACHED_ARTIST_LIST: list = []  # Local memory storage of the current artists I am monitoring
IS_CACHE_EMPTY: bool = False

def get_api_endpoint() -> str:
    """
    Retrieve API Gateway endpoint Url from SSM Parameter Store
    """
    
    try:
        ssm = boto3.client('ssm')
        parameter = ssm.get_parameter(Name='/Spotificity/ApiGatewayEndpoint/prod', WithDecryption=True)
    except ClientError as err:
        print(f'{Style.RED}Client Error Message: {err.response["Error"]["Message"]}')
        print(f'{Style.RED}Client Error Code: {err.response["Error"]["Code"]}')
        raise FailedToRetrieveEndpoint(err.response["Error"]["Message"]) 
    except Exception as err:
        print(f'Other error occurred: {err}')
        raise
    else:
        return parameter['Parameter']['Value']
API_ENDPOINT: str = get_api_endpoint()

def send_signed_request(
    method: str, 
    url: str, 
    service='execute-api', 
    region=os.getenv('CDK_DEFAULT_REGION'), 
    payload=None
    ) -> requests.Response:
    """
    Sends a signed HTTP request to a specified AWS service endpoint. This function will use the AWS 
    credentials available from the boto3 session to sign the HTTP request using AWS Signature Version 4.

    Parameters:
        - method (str): 'GET', 'POST', 'PUT', or 'DELETE'
        - url (str): The full URL to the endpoint where the request will be sent.
        - service (str, optional): The AWS service code for request signing. Default is 'execute-api' for API Gateway.
        - region (str, optional): The AWS region where the request should be sent. 
        - payload (str, optional): The payload body for 'POST' or 'PUT' requests. Default is None.

    Returns:
        - response (requests.Response): The HTTP response received from the endpoint.
    """
    
    # Create a boto3 session and fetch AWS credentials
    credentials = boto3.Session().get_credentials()
    auth = AWS4Auth(
        credentials.access_key, 
        credentials.secret_key, 
        region, service, session_token=credentials.token
    )
    
    # Define a dictionary to map HTTP method strings to their corresponding functions
    http_method_map = {
        'GET': requests.get,
        'POST': requests.post,
        'PUT': requests.put,
        'DELETE': requests.delete
    }
    http_request_method = http_method_map[method]

    # Make the HTTP request. Additional Error catching is done within the Lambda function.
    try:
        response = http_request_method(
            url, 
            auth=auth, 
            data=payload, 
            headers={
                'Content-Type': 'application/json'
            }
        )
    except Exception as err:
        print(f'{Style.RED}Other error occurred: \n\n{err}')
        raise
    else:
        return response

def request_token() -> str:
    """
    Invoke Lambda function that fetches an access token from the Spotify 
    `/token/` API.
    
    Returns:  
        - str: Authenticated Spotify access token needed for all future API calls to spotify. 
    """    
    
    response = send_signed_request('GET', f'{API_ENDPOINT}/token')
    
    # Raise exception if payload is None, otherwise return access token
    if response.json().get('access_token') is None:
        raise FailedToRetrieveToken
    else:
        return response.json()['access_token']

def get_valid_user_input(prompt: str, valid_choices: list[str]) -> str:
    """
    Instead of using nested while loops, this function uses a single while loop
    to prompt the user for input until they enter a valid selection. 
    
    Parameters:
        - prompt (str): The string that is displayed to the user.
        - valid_choices (list[str]): A list of strings representing valid inputs
    
    Returns:
        - str: The validated input from the user, converted to lowercase
    """
    
    while True:
        user_input = input(prompt).lower()
        if user_input in valid_choices:
            return user_input
        else:
            print(f'{Style.YELLOW}\n\tPlease enter a valid selection.{Style.RESET}')

def list_artists(continue_prompt=False) -> None:
    """
    Prints out a list of the current artists that are being monitored
    
    Parameters:
        - continue_prompt (boolean): Whether the user is returned with the main menu after function execution or not. 
    """

    global CACHED_ARTIST_LIST, IS_CACHE_EMPTY
    lambda_name = 'FetchArtistsHandler'

    # Check if either the cache has items or the `IS_CACHE_EMPTY` flag is set to True
    # If neither is true, invoke Lambda to fetch fresh data
    if len(CACHED_ARTIST_LIST) > 0 or IS_CACHE_EMPTY:
        if CACHED_ARTIST_LIST:
            for index, artist in enumerate(CACHED_ARTIST_LIST, start=1):
                print(f'\n\t[{Style.LIGHT_GREEN}{index}{Style.RESET}] {artist["artist_name"]}')
        else:
            print(f'{Style.YELLOW}\n\tNo artists currently being monitored.{Style.RESET}')
    else: 
        
        # Invoke Lambda to fetch fresh data
        response = send_signed_request('GET', f'{API_ENDPOINT}/artist')

        # Catch any errors that occurred during Lambda execution
        if response.json().get('error_type') == 'Other':
            raise ExceptionDuringLambdaExecution(lambda_name, response.json()['error'])

        # Catch any errors that occurred during scan operation on DynamoDB table. 
        elif response.json().get('error_type') == 'Client':
            raise FailedToRetrieveMonitoredArtists(response.json()['error'])
        
        # Print out list of artists
        elif response.status_code == 204:
            print(f'{Style.YELLOW}\n\tNo artists currently being monitored.{Style.RESET}')
            
            # Update cache to be an empty list  
            CACHED_ARTIST_LIST = []
            IS_CACHE_EMPTY = True
        else:
            print('\nCurrent monitored artists:')
            list_of_names: list[str] = response.json()['artists']['current_artists_names']
            
            for index, artist in enumerate(list_of_names, start=1):
                print(f'\n\t[{Style.LIGHT_GREEN}{index}{Style.RESET}] {artist}')

            # Update cache with current artists list
            CACHED_ARTIST_LIST = response.json()['artists']['current_artists_with_id']
            IS_CACHE_EMPTY = False

    menu_loop_prompt(continue_prompt)

def fetch_artist_id(artist_name: str, access_token: str) -> tuple[str, str] | None:
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

    # Prep payload. Payload is a JSON formatted string
    lambda_name = 'GetArtist-IDHandler'
    payload = json.dumps({
        'artist_name': artist_name,
        'access_token': access_token    
    })
    
    response = send_signed_request('POST', f'{API_ENDPOINT}/artist/id', payload=payload.encode())  
    
    # Catch any errors that occurred during lambda execution
    if response.json().get('error_type') == 'Other':
        raise ExceptionDuringLambdaExecution(lambda_name, response.json()['error'])
    
    # Catch any errors that occurred during GET request to Spotify API. 
    elif response.json().get('error_type') == 'HTTP':
        raise FailedToRetrieveListOfMatchesWithIDs(response.json()['error'])
    elif len(response.json()['artistSearchResultsList']) == 0:
        raise FailedToRetrieveListOfMatchesWithIDs('No artists found that closely match your search.')

    first_artist_guess = {
        'artist_id': response.json()['artistSearchResultsList'][0]['id'],
        'artist_name': response.json()['artistSearchResultsList'][0]['name']
    }
    
    # Serve user the most likely artist they were looking for. Ask for confirmation
    answer = get_valid_user_input(
        prompt=f'\nIs {Style.LIGHT_GREEN}{first_artist_guess["artist_name"]}{Style.RESET} the artist you were looking for? (yes or no)\n> ',
        valid_choices=(YES_CHOICES + NO_CHOICES)
    )

    # If the user confirmed the artist, return the most likely artist's Spotify ID and name
    if answer in YES_CHOICES:
        return first_artist_guess['artist_id'], first_artist_guess['artist_name']
    elif answer in NO_CHOICES:
        
        # Print list of the other most likely choices and have them choose
        for index, artist in enumerate(response.json()['artistSearchResultsList'], start=1):
            print(f'\n[{Style.LIGHT_GREEN}{index}{Style.RESET}]')
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
            prompt=f'\nWhich artist were you looking for? Select the number. (or enter {Style.YELLOW}`back`{Style.RESET} to return to search prompt)\n> ',
            valid_choices=[
                str(option_index) for option_index, artist in enumerate(response.json()['artistSearchResultsList'], start=1)
            ] + GO_BACK_CHOICES
        )              
        
        # If user choice matches an option, then return that artist's Spotify ID and name
        for option_index, artist in enumerate(response.json()['artistSearchResultsList'], start=1):
            if user_choice in GO_BACK_CHOICES:
                return None   
            elif int(user_choice) == option_index:
                return artist['id'], artist['name']         

def add_artist(access_token: str, continue_prompt=False) -> None:
    """
    Prompts user for which artist they want to add to be monitored. 
    Then invokes a Lambda function that adds the artist to a list.\
    
    Parameters:
        - access_token (str): Required authenticated Spotify access token to send in API request
        - continue_prompt (boolean): Whether the user is returned with the main menu after function execution or not. 
    """
    
    global CACHED_ARTIST_LIST
    lambda_name = 'AddArtistsHandler'

    while True:
        
        # Show user a list of the artist they are already monitoring and then 
        # ask user for which artist they want to search for 
        list_artists()
        user_artist_choice = input("\nWhich artist would you like to start monitoring?\n> ")

        # Query Spotify API to get a list of the closest matches to the user's search
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
            print(f'\nYou\'re already monitoring {Style.LIGHT_GREEN}{artist_name}{Style.RESET}!')
        else:
            payload = json.dumps(artist)
            
            # Invoke a lambda to add artist to be monitored
            response = send_signed_request('POST', f'{API_ENDPOINT}/artist', payload=payload.encode())

            # Catch any errors that occurred during Lambda execution
            if response.json().get('error_type') == 'Other':
                raise ExceptionDuringLambdaExecution(lambda_name, response.json()['error'])

            # Catch any errors that occurred during PUT request on the DynamoDB table.
            elif response.json().get('error_type') == 'Client':
                raise FailedToAddArtistToTable(response.json()['error'])
            else:

                # Update cache with new addition
                CACHED_ARTIST_LIST.append(artist)
                print(f'\n\tYou are now monitoring for {Style.LIGHT_GREEN}{artist_name}{Style.RESET}\'s new music!')
                break
                
    menu_loop_prompt(continue_prompt)

def remove_artist(continue_prompt=False) -> None:
    """
    Removes an artist from being monitored
    
    Parameter:
        - continue_prompt (boolean): Whether the user is returned with the main menu after function execution or not. 
    """
    
    global CACHED_ARTIST_LIST
    lambda_name = 'RemoveArtistsHandler'

    # If there are currently no artists to remove, then exit the function
    list_artists()
    if not CACHED_ARTIST_LIST:
        print(f"{Style.YELLOW}\n\tThere are no artists to remove!{Style.RESET}")
        menu_loop_prompt(continue_prompt)
        return

    # Otherwise, ask them which artist they would like to remove
    user_choice = get_valid_user_input(
        prompt=f'\nWhich artist would you like to remove? Make a selection: (or enter {Style.YELLOW}`back`{Style.RESET} to return to main menu)\n> ',
        valid_choices=[
            str(choice_index) for choice_index, artist in enumerate(CACHED_ARTIST_LIST, start=1)
        ] + GO_BACK_CHOICES
    )

    for choice_index, artist in enumerate(CACHED_ARTIST_LIST, start=1):
        if user_choice in GO_BACK_CHOICES:
            return
        elif int(user_choice) == choice_index:
            
            # Prep payload to be sent to Lambda function
            payload = json.dumps({
                'artist_id': CACHED_ARTIST_LIST[int(user_choice) - 1]['artist_id'],
                'artist_name': CACHED_ARTIST_LIST[int(user_choice) - 1]['artist_name']
            })

            # Invoke a lambda function that performs a DELETE request on the DynamoDB table.
            response = send_signed_request('DELETE', f'{API_ENDPOINT}/artist', payload=payload.encode())

            # Catch any errors that occurred during Lambda execution
            if response.json().get('error_type') == 'Other':
                raise ExceptionDuringLambdaExecution(lambda_name, response.json()['error'])

            # Catch any errors that occurred during DELETE request on the DynamoDB table.
            elif response.json().get('error_type') == 'Client':
                raise FailedToRemoveArtistFromTable(response.json()['error'])
            else:
                
                # Update cache by removing artist
                CACHED_ARTIST_LIST.pop(int(user_choice) - 1)
                print(f"\n\tRemoved {Style.LIGHT_GREEN}{artist['artist_name']}{Style.RESET} from list!")

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
    print(f'{Style.RED}\n\tQuitting App! {choice(goodbye_list).title()}!')
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
            prompt=f"\nPress {Style.LIGHT_GREEN}[ENTER]{Style.RESET} to go back to main menu... (Or enter {Style.YELLOW}quit{Style.RESET} to quit app)\n> ",
            valid_choices=(quit_choices + go_back_choices)
        )

        if user_choice in quit_choices:
            quit() 
        elif user_choice in go_back_choices:
            return
from requests.exceptions import HTTPError
import requests

def handler(event: dict, context) -> dict:
    """
    Queries the Spotify `Search` API for the artist's Spotify ID. 
    """
    
    print(f'Passed in artist payload: {event}')
    artist_name: str = event['artist_name']
    access_token: str = event['access_token']
    endpoint: str = 'https://api.spotify.com/v1/search'
    
    try:
        print('Initiating GET request for artist ID...')
        
        response = requests.get(
            url=endpoint,
            params={
                'q': artist_name,
                'type': 'artist',
                'limit': 5,
                'offset': 0,
                'market': 'US'
            },
            headers={
                'Authorization': f'Bearer {access_token}'
            }
        )
        
        # Catch any HTTP errors
        response.raise_for_status()
    except HTTPError as err:
        print(f'HTTP Error occurred: {err}')
        raise
    except Exception as err:
        print(f'Other error occurred: {err}')
        raise
    else:
        print(f'Successfully received response from Spotify `Search` API. HTTP Status code: {response.status_code}')
        print(f'Returned Payload: {response.json()}')
        artist_search_results: dict = response.json()
        
        # Check if error occurred while attempting to fetch list of artists with their details
        if artist_search_results.get('error'):
            print(f'Unsuccessful retrieval from Spotify `Search` API. Returning error to client.')
            return {
                'statusCode': artist_search_results['error']['status'],
                'payload': {
                    'error': artist_search_results['error']
                }
            }
        else:
            print('Successfully retrieved list of artists with their respective Spotify IDs. Returning list to client.')
            return {
                'statusCode': 200,
                'payload': {
                    'artistSearchResultsList': artist_search_results['artists']['items']
                }
            }
    
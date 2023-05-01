from requests.exceptions import HTTPError
import requests

def handler(event: dict, context) -> dict:
    """
    Queries the Spotify `Search` API for the artist's Spotify ID. 
    """
    
    endpoint = 'https://api.spotify.com/v1/search'
    artist_name: str = event['artist_name']
    access_token: str = event['access_token']
    
    try:
        print('Initiating GET request for artist ID...')
        
        response = requests.get(
            url=endpoint,
            params={
                'q': artist_name,
                'type': 'artist',
                'limit': 3
            },
            headers={
                'Authorization': f'Bearer {access_token}'
            }
        )
        
        # Catch any HTTP errors
        response.raise_for_status()
    except HTTPError as err:
        print(f'HTTP Error occurred: {err}')
    except Exception as err:
        print(f'Other error occurred: {err}')
    else:
        print('Parsing JSON...')
        
        # Convert response object to dictionary
        artist_search_results: dict = response.json()
        
        return {
            'statusCode': 200,
            'payload': {
                'artistSearchResultsList': artist_search_results['artists']['items'],
                'firstArtistGuess': {
                    'artist_id': artist_search_results['artists']['items'][0]['id'],
                    'artist_name': artist_search_results['artists']['items'][0]['name']
                }
            }
        }
    
    return {}
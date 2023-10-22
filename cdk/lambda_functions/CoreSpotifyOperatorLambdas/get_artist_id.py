from requests.exceptions import HTTPError
import requests
import json

def handler(event: dict, context) -> dict:
    """
    Queries the Spotify `Search` API for the artist's Spotify ID. 
    """
    
    print(f'Passed in artist payload: {event["body"]}')
    payload: dict = json.loads(event['body'])
    artist_name: str = payload['artist_name']
    access_token: str = payload['access_token']
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
        print(f'Unsuccessful retrieval from Spotify `Search` API. Returning error to client.')
        return {
            'statusCode': err.response.status_code,
            'headers': {
                'Content-Type': 'application/json'
            },                
            'body': json.dumps({
                'error': err.response.text,
                'error_type': 'HTTP'
            })
        }
    except Exception as err:
        print(f'Other error occurred: {err}')
        return {
            'statusCode': 405,
            'headers': {
                'Content-Type': 'application/json'
            },                
            'body': json.dumps({
                'error': str(err),
                'error_type': 'Other'
            })
        }
    else:
        print(f'Successfully received response from Spotify `Search` API. HTTP Status code: {response.status_code}')
        print(f'Returned Payload: {response.json()}')
        artist_search_results: dict = response.json()
        
        print('Successfully retrieved list of artists with their respective Spotify IDs. Returning list to client.')
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'artistSearchResultsList': artist_search_results['artists']['items']
            })
        }
    
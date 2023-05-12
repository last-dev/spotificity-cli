from requests.exceptions import HTTPError
import requests

def handler(event: dict, context) -> dict:
    """
    Queries a couple of Spotify's APIs to return back the latest musical releases
    for the artists.
    """
    
    print(f'Passed in event: {event}')
    
    access_token: str = event['access_token']
    current_artists: list[dict] = event['artists']['current_artists_with_id']
    latest_music: list[dict] = []
        
    # For each artist, fetch the latest musical releases
    print('Starting iteration through artist list...')
    for artist in current_artists:
        artist_id: str = artist['artist_id']
        artist_name: str = artist['artist_name']
        
        # Get latest musical releases
        last_album_details: dict = get_latest_album(artist_id, artist_name, access_token)
        last_single_details: dict = get_latest_single(artist_id, artist_name, access_token)
        
        # Add to list of latest musical releases
        print(f'Adding {artist_name}\'s information to return payload...')
        latest_music.append({
            'artist_id': artist_id,
            'artist_name': artist_name,
            'last_album_details': last_album_details,
            'last_single_details': last_single_details
        })
        
    # Return list of latest musical releases
    print('Successfully retrieved latest musical releases for all artists.')
    return {
        'latest_music': latest_music
    }
      
def get_latest_album(artist_id: str, artist_name: str, access_token: str) -> dict:
    """
    Queries the Spotify API to return the last album released by the
    artist.
    """
    
    endpoint: str = f'https://api.spotify.com/v1/artists/{artist_id}/albums'
    
    try:
        print(f'Initiating GET request for the {artist_name}\'s last album...')
        
        response = requests.get(
            url=endpoint,
            params={
                'limit': 1,
                'offset': 0,
                'include_groups': 'album',
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
        print('Parsing returned payload...')
        album_search_results: dict = response.json()

        # Catch any errors that may occur when searching for the last album
        if album_search_results.get('error'):
            print(f'Error occurred: {album_search_results["error"]}')
            raise Exception(f'Error occurred: {album_search_results["error"]}')
        elif len(album_search_results['items']) == 0:
            print(f'No albums found for {artist_name}.')
            raise Exception('No albums found')
        
        # Extract out the last album's details
        last_album: dict = album_search_results['items'][0]
        last_album_artists: list[str] = [artist['name'] for artist in last_album['artists']]
        
        print('Successfully retrieved last album details.')
        
        return {
            'last_album_name': last_album['name'],
            'last_album_release_date': last_album['release_date'],
            'last_album_artists': last_album_artists
        }

def get_latest_single(artist_id: str, artist_name: str, access_token: str) -> dict:
    """
    Queries the Spotify API to return the last single released by the
    artist.
    """
    
    endpoint: str = f'https://api.spotify.com/v1/artists/{artist_id}/albums'
    
    try:
        print(f'Initiating GET request for the {artist_name}\'s last single...')
        
        response = requests.get(
            url=endpoint,
            params={
                'limit': 1,
                'offset': 0,
                'include_groups': 'single',
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
        print('Parsing returned payload...')
        single_search_results: dict = response.json()

        # Catch any errors that may occur when searching for the last single
        if single_search_results.get('error'):
            print(f'Error occurred: {single_search_results["error"]}')
            raise Exception(f'Error occurred: {single_search_results["error"]}')
        elif len(single_search_results['items']) == 0:
            print(f'No singles found for {artist_name}.')
            raise Exception('No singles found')
        
        # Extract out the last single's details
        last_single: dict = single_search_results['items'][0]
        last_single_artists: list[str] = [artist['name'] for artist in last_single['artists']]
        
        print('Successfully retrieved last single details.')
        
        return {
            'last_single_name': last_single['name'],
            'last_single_release_date': last_single['release_date'],
            'last_single_artists': last_single_artists
        }
        

"""
Unfortunately it turns out Spotify does not have a way to filter by songs the artist is featured on.
Until then, this will be commented out. 
"""

# def get_latest_tracks_artist_featured_on(artist_name: str, access_token: str) -> dict:
#     """
#     Queries the Spotify API to return the last track the artist was 
#     featured on
#     """
    
#     endpoint: str = 'https://api.spotify.com/v1/search'
    
#     try:
#         print(f'Initiating GET request for the last track {artist_name} was featured on...')
        
#         response = requests.get(
#             url=endpoint,
#             params={
#                 'q': f'featured:{artist_name}',
#                 'type': 'track',
#                 'limit': 100,
#                 'offset': 0,
#                 'market': 'US'
#             },
#             headers={
#                 'Authorization': f'Bearer {access_token}'
#             }
#         )
        
#         # Catch any HTTP errors
#         response.raise_for_status()
#     except HTTPError as err:
#         print(f'HTTP Error occurred: {err}')
#         raise
#     except Exception as err:
#         print(f'Other error occurred: {err}')
#         raise
#     else:
#         print('Parsing JSON...')
        
#         # Sort the featured tracks by release date (descending)   
#         featured_tracks: dict = response.json()
#         sorted_tracks: list = sorted(
#             featured_tracks['tracks']['items'],
#             key=lambda x: x['album']['release_date'],
#             reverse=True
#         )

#         # Only keep songs where artist is featured
#         songs: list = [
#             track for track in sorted_tracks
#             if any(artist['name'] == artist_name and artist != track['artists'][0] for artist in track['artists'])
#         ]

#         return {
#             'last_2_featured_tracks': songs[:2]
#         }
                
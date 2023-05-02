from requests.exceptions import HTTPError
from botocore.exceptions import ClientError
import requests
import boto3
import json
import os

def handler(event: dict, context) -> dict:
    """
    Queries a couple of Spotify's APIs to return back the latest musical releases
    for the artist.
    """
    
    print(f'Passed in event: {event}')
    
    # If no INSERT event in batch of records, don't continue execution.
    if not any(record['eventName'] == 'INSERT' for record in event['Records']):
        print('No INSERT events in batch of records. Exiting.')
        return {}
    
    # If access token is passed in, use it. Otherwise, invoke Lambda that will return one.
    try:
        access_token: str = event['access_token']
    except KeyError:
        print('Access token not passed in. Fetching new one.')
        access_token = request_token()
        
    # Keeps track of how many artists have been processed from the stream batch
    # This is me over-engineering for when I have the ability to add multiple artists at once
    artists_processed: int = 0
        
    # Iterate through DynamoDB records to get artist_id and artist_name for each record.
    # For each record, invoke Lambda function that will update the DynamoDB table.
    for record in event['Records']:
        if record['eventName'] == 'INSERT':
            artist_id: str = record['dynamodb']['NewImage']['artist_id']['S']
            artist_name: str = record['dynamodb']['NewImage']['artist_name']['S']
        
            # Get latest musical releases
            last_album_details: dict = get_latest_album(artist_id, artist_name, access_token)
            last_single_details: dict = get_latest_single(artist_id, artist_name, access_token)
            
            # Update DynamoDB with latest musical releases
            try:
                lambda_name = os.getenv('UPDATE_TABLE_MUSIC_LAMBDA')
                lambda_ = boto3.client('lambda')
                
                response: dict = lambda_.invoke(
                    FunctionName=lambda_name,
                    InvocationType='RequestResponse',
                    Payload=json.dumps({
                        'artist_id': artist_id,
                        'artist_name': artist_name,
                        'last_album_details': last_album_details,
                        'last_single_details': last_single_details
                    })
                )
            except ClientError as err:
                print(f'Client Error Message: {err.response["Error"]["Message"]}')
                print(f'Client Error Code: {err.response["Error"]["Code"]}')
                print(f'HTTP Code: {err.response["ResponseMetadata"]["HTTPStatusCode"]}')
                raise
            except Exception as err:
                print(f'Other Error Occurred: {err}')
                raise
            else:
                print(f'Successfully invoked {lambda_name} to update the DynamoDB table.')
                
                # Convert botocore.response.StreamingBody object to dict
                returned_json: dict = json.load(response['Payload'])
                
                print(returned_json)
                artists_processed += 1
    
                return {
                    'artists_processed': artists_processed
                }
    
    return {}
    
def request_token() -> str:
    """
    Invoke Lambda function that sends a POST request to Spotify `Token` 
    API to get an access token. 
    """    
    
    lambda_name = os.getenv('GET_ACCESS_TOKEN_LAMBDA')
    
    try:
        print('Initiating POST request to Spotify\'s Token API...')        
        
        lambda_ = boto3.client('lambda')
        response: dict = lambda_.invoke(
            FunctionName=lambda_name,
            InvocationType='RequestResponse'
        )
    except ClientError as err:
        print(f'\nClient Error Message: \n\t{err.response["Error"]["Message"]}')
        print(f'Client Error Code: \n\t{err.response["Error"]["Code"]}')
        raise
    except Exception as err:
        print(f'\n\tOther error occurred: \n\t{err}')
        raise
    else:
        print('Successfully received access token from Spotify\'s Token API.')
        
        # Convert botocore.response.StreamingBody object to dict
        returned_json: dict = json.load(response['Payload'])
        
        return returned_json['payload']['access_token']
     
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
        print('Parsing JSON...')
        
        album_search_results: dict = response.json()
        
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
        print('Parsing JSON...')
        
        # Extract out the last single's details
        last_single: dict = response.json()['items'][0]
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
                
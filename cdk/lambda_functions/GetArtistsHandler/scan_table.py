from botocore.exceptions import ClientError
import boto3
import os

def handler(event: dict, context) -> dict:
    """
    Handler for Lambda that will returns a list of all current artists 
    being monitored in "Monitored Artists" DynamoDB table 
    """

    # Create a DynamoDB client
    ddb = boto3.client('dynamodb')
    table = os.getenv('ARTIST_TABLE_NAME')

    try:
      # Scans specified table and returns all items in a list within a dict
      print(f'Sending scan request to {table}...')
      response = ddb.scan(  
          TableName=table,
          Select='ALL_ATTRIBUTES',
          ReturnConsumedCapacity='TOTAL'
      )
    except ClientError as err:
      print(f'Client Error Message: {err.response["Error"]["Message"]}')
      print(f'Client Error Code: {err.response["Error"]["Code"]}')
      print(f'HTTP Code: {err.response["ResponseMetadata"]["HTTPStatusCode"]}')
    except Exception as err:
      print(f'Other Error Occurred: {err}')
    else: 

      print('Prepping return payload. Adding artists to list...')

      # Extract out only artist ID and name. Then add all artists into a list of dicts
      current_artists_with_id: list[dict] = []
      for artist in response['Items']:
        current_artists_with_id.append({'artist_id': artist['artist_id']['S'], 'artist_name': artist['artist_name']['S']})

      # Extract out only artist name. Then add all artists into a list
      current_artists_names: list[str] = [artist['artist_name']['S'] for artist in response['Items']]
      
      # Construct returning payload
      payload = {
        'current_artists_names': current_artists_names,
        'current_artists_with_id': current_artists_with_id
      }
      
      print('GET request successful. Returning list of artists to client.')
      return {
          'statusCode': 200,
          'payload': {
            'artists': {
              'current_artists_names': current_artists_names,
              'current_artists_with_id': current_artists_with_id
            }},
          'headers': {'Content-Type': 'text/plain'}
      }
    
    # Sentinel Value used to appease Pylance.
    return {}
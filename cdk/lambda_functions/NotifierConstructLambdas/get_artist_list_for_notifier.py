from botocore.exceptions import ClientError
import boto3
import os

def handler(event: dict, context) -> dict:
    """
    Returns a list of all current artists being monitored. 
    """

    try:
        ddb = boto3.client('dynamodb')
        table = os.getenv('ARTIST_TABLE_NAME')
        print(f'Sending scan request to {table}...')

        response = ddb.scan(  
            TableName=table,
            Select='ALL_ATTRIBUTES',
            ReturnConsumedCapacity='TOTAL'
        )
    except ClientError as err:
        print(f'Client Error Message: {err.response["Error"]["Message"]}')
        print(f'Client Error Code: {err.response["Error"]["Code"]}')
        raise
    except Exception as err:
        print(f'Other Error Occurred: {err}')
        raise
    else: 
        print('Parsing returned payload...')

        # Catch any errors that may have occurred
        if response.get('Error'):
            print('Error occurred while trying to scan table.')
            return {
                'payload': {
                    'status_code': response['ResponseMetadata']['HTTPStatusCode'],
                    'error': response['Error']
                }
            }
        elif len(response['Items']) == 0:
            print('No artists found.')
            return {
                'payload': {
                    'status_code': 204, 
                    'artists': []
                }
            }
        else:
            print('Successfully received list of artists. Sending list to next task in step function.')

            # Extract out only artist ID and name. Then add all artists into a list of dicts
            current_artists_with_id: list[dict] = [{'artist_id': artist['artist_id']['S'], 'artist_name': artist['artist_name']['S']} for artist in response['Items']]

            # Extract out only artist name. Then add all artists into a list
            current_artists_names: list[str] = [artist['artist_name']['S'] for artist in response['Items']]

            return {
                'payload': {
                    'status_code': 200,
                    'access_token': event,
                    'artists': {
                        'current_artists_names': current_artists_names,
                        'current_artists_with_id': current_artists_with_id
                    }
                }
            }
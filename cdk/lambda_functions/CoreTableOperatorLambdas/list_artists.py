from botocore.exceptions import ClientError
import boto3
import json
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
        return {
            'statusCode': err.response['ResponseMetadata']['HTTPStatusCode'],
            'headers': {
                'Content-Type': 'application/json'
            },                
            'body': json.dumps({
                'error': err.response['Error']
            })
        }
    except Exception as err:
        print(f'Other Error Occurred: {err}')
        return {
            'statusCode': 403,
            'headers': {
                'Content-Type': 'application/json'
            },                
            'body': json.dumps({
                'error': str(err)
            })
        }
    else: 
        print('Parsing returned payload...')

        if len(response['Items']) == 0:
            print('No artists found. Returning empty list to client.')
            return {
                'statusCode': 204, 
                'headers': {
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({
                    'artists': []
                })
            }
        else:
            print('Successfully received list of artists. Returning list to client.')

            # Extract out only artist ID and name. Then add all artists into a list of dicts
            current_artists_with_id: list[dict] = [{'artist_id': artist['artist_id']['S'], 'artist_name': artist['artist_name']['S']} for artist in response['Items']]

            # Extract out only artist name. Then add all artists into a list
            current_artists_names: list[str] = [artist['artist_name']['S'] for artist in response['Items']]

            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({
                    'artists': {
                        'current_artists_names': current_artists_names,
                        'current_artists_with_id': current_artists_with_id
                    }
                })
            }
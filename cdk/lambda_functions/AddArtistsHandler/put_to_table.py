from botocore.exceptions import ClientError
import boto3
import os

def handler(event: dict, context) -> dict:
    """
    Adds a new artist to the "Monitored Artists" DynamoDB table
    """

    print(f'Passed in artist payload: {event}')
    artist_name: str = event['artist_name']
    access_id: str = event['artist_id']

    try:
        # Create a DynamoDB client
        ddb = boto3.client('dynamodb')
        table = os.getenv('ARTIST_TABLE_NAME')
        print(f'Attempting to add {artist_name} to {table}...')
      
        response = ddb.put_item(
            TableName=table,
            Item={
                'artist_id': {
                    'S': access_id
                },
                'artist_name': {
                    'S': artist_name
                }
            },
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
            print('Error occurred while trying to add artist. Returning error message to client.')
            return {
                'status_code': response['ResponseMetadata']['HTTPStatusCode'],
                'payload': {
                    'error': response['Error']
                }
            }
        else:
            print(f'PUT request successful. Now monitoring {artist_name}. Returning payload to client.')
        
            return {
                'status_code': 200,
                'payload': {
                    'returned_response_from_put': response
                }
            }

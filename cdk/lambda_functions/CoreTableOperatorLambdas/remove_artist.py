from botocore.exceptions import ClientError
import boto3
import json
import os

def handler(event: dict, context) -> dict:
    """
    Removes an artist from the "Monitored Artists" DynamoDB table
    """
    
    print(f'Passed in artist payload: {event["body"]}')
    payload: dict = json.loads(event['body'])
    artist_name: str = payload['artist_name']
    artist_id: str = payload['artist_id']

    try:
        # Create a DynamoDB client
        ddb = boto3.client('dynamodb')
        table = os.getenv('ARTIST_TABLE_NAME')
        print(f'Attempting to remove {artist_name} from {table}...')
            
        response = ddb.delete_item(
            TableName=table,
            Key={
                'artist_id': {
                    'S': artist_id
                }
            },
            ReturnConsumedCapacity='TOTAL'
        )
    except ClientError as err:
        print(f'Client Error Message: {err.response["Error"]["Message"]}')
        print(f'Client Error Code: {err.response["Error"]["Code"]}')
        print('Error occurred while trying to remove artist. Returning error message to client.')
        return {
            'statusCode': err.response['ResponseMetadata']['HTTPStatusCode'],
            'headers': {
                'Content-Type': 'application/json'
            },                
            'body': json.dumps({
                'error': err.response['Error'],
                'error_type': 'Client'
            })
        }
    except Exception as err:
        print(f'Other Error Occurred: {err}')
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
        print(f'DELETE request successful. {artist_name} successfully removed. Returning payload to client.')
    
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'returned_response_from_delete': response
            })
        }
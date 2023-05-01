from botocore.exceptions import ClientError
import boto3
import os

def handler(event: dict, context) -> dict:
    """
    Handler for Lambda that will remove an artist from 
    the "Monitored Artists" DynamoDB table
    """
    
    print(f'Passed in payload: {event}')
    artist_name: str = event['artist_name']
    artist_id: str = event['artist_id']
    
    # Create a DynamoDB client
    ddb = boto3.client('dynamodb')
    table = os.getenv('ARTIST_TABLE_NAME')

    try:
      print(f'Removing {artist_name} from {table}...')
      
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
      print(f'HTTP Code: {err.response["ResponseMetadata"]["HTTPStatusCode"]}')
    except Exception as err:
      print(f'Other Error Occurred: {err}')
    else: 
      print('DELETE request successful. Returning payload to client.')
      
      return {
          'statusCode': 200,
          'payload': {
            'artistRemovedFromTable': artist_name,
            'returnPayloadFromDelete': response
          }
      }
    
    return {}
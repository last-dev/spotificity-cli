from botocore.exceptions import ClientError
import boto3
import os

def handler(event: dict, context) -> dict:
    """
    Handler for Lambda that will add a new artist to 
    the "Monitored Artists" DynamoDB table
    """

    print(f'Passed in artist payload: {event}')
    artist_name: str = event['artist_name']
    access_id: str = event['artist_id']

    # Create a DynamoDB client
    ddb = boto3.client('dynamodb')
    table = os.getenv('ARTIST_TABLE_NAME')

    try:
      print(f'Adding {artist_name} to {table}...')
      
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
      print(f'HTTP Code: {err.response["ResponseMetadata"]["HTTPStatusCode"]}')
    except Exception as err:
      print(f'Other Error Occurred: {err}')
    else: 
      print('PUT request successful. Returning payload to client.')
      
      return {
          'statusCode': 200,
          'payload': {
            'artistAddedToTable': artist_name,
            'returnPayloadFromPut': response
          }
      }

    return {}
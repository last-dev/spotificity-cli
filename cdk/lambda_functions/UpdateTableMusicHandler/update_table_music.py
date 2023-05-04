from botocore.exceptions import ClientError
import boto3
import os

def handler(event: dict, context) -> dict:
    """
    Handler for Lambda that will update the attributes for each
    artist in the "Monitored Artists" DynamoDB table with the latest musical releases
    """

    print(f'Passed in artist payload: {event}')
    artist_name: str = event['artist_name']
    artist_id: str = event['artist_id']
    last_album_details: dict = event['last_album_details']
    last_single_details: dict = event['last_single_details']
    
    # Create a DynamoDB client
    ddb = boto3.client('dynamodb')
    table = os.getenv('ARTIST_TABLE_NAME')

    try:
        print(f'Initiating PUT request to update {table} with {artist_name}\'s latest releases...')

        response = ddb.update_item(
            TableName=table,
            Key={
                'artist_id': {
                    'S': artist_id
                }       
            },
            UpdateExpression='SET last_album_details = :last_album_details, last_single_details = :last_single_details',
            ExpressionAttributeValues={
                ':last_album_details': {
                    'M': {
                        'last_album_name': {
                            'S': last_album_details['last_album_name']
                        },
                        'last_album_release_date': {
                            'S': last_album_details['last_album_release_date']
                        },
                        'last_album_artists': {
                            'L': [{'S': artist} for artist in last_album_details['last_album_artists']]
                        }
                    }
                },
                ':last_single_details': {
                    'M': {
                        'last_single_name': {
                            'S': last_single_details['last_single_name']
                        },
                        'last_single_release_date': {
                            'S': last_single_details['last_single_release_date']
                        },
                        'last_single_artists': {
                            'L': [{'S': artist} for artist in last_single_details['last_single_artists']]
                        }
                    }
                }
            },
            ReturnConsumedCapacity='TOTAL',
            ReturnValues='UPDATED_OLD'
        )
    except ClientError as err:
        print(f'Client Error Message: {err.response["Error"]["Message"]}')
        print(f'Client Error Code: {err.response["Error"]["Code"]}')
        raise
    except Exception as err:
        print(f'Other Error Occurred: {err}')
        raise
    else: 
        print('PUT request successful.')
        
        # TODO: Add logic to compare old and new values to see if any attributes changed to prepare SNS message

        return {
            'statusCode': 200,
            'payload': {
                'returnPayloadFromUpdate': response
            }
        }

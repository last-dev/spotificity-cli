from botocore.exceptions import ClientError
import boto3
import json
import os

def handler(event, context) -> None:
    """
    This Lambda publishes a message to a SNS topic when there are
    no artists in the table being monitored. 
    """
    
    # Confirm email is subscribed
    confirm_email_subscription()
    
    # Publish message to SNS topic
    try:
        print ('Attempting to publish email to SNS topic...')
        topic_arn = os.getenv('SNS_TOPIC_ARN')
        sns = boto3.client('sns')
        
        response = sns.publish(
            TopicArn=topic_arn,
            Subject='Spotificity: ❌ No Artists Found In List ❌',
            Message='There are no artists currently being monitored. No new music to report!\n Please run Spotificity CLI to add artists to the list.'
        )
    except ClientError as err:
        print(f'Client Error Message: {err.response["Error"]["Message"]}')
        print(f'Client Error Code: {err.response["Error"]["Code"]}')
        raise
    except Exception as err:
        print(f'Other Error Occurred: {err}')
        raise
    else: 
        print('Successfully published email to SNS topic.') 
        print(f'Published message ID is: {response["MessageId"]}')
        
def confirm_email_subscription() -> None:
    """
    This function checks to see if my email is already subscribed to the
    SNS topic. If not, it will raise an exception. I'll manually confirm it
    in the AWS Console
    """

    print('Checking to see if my email is already subscribed...')
            
    try:
        print('Attempting to pull my email from AWS Secrets Manager...')

        # Creates a Secrets Manager client
        ssm = boto3.client('secretsmanager')

        response = ssm.get_secret_value(
            SecretId='EmailSecret'
        )
    except ClientError as err:
        print(f'Client Error Message: {err.response["Error"]["Message"]}')
        print(f'Client Error Code: {err.response["Error"]["Code"]}')
        raise
    except Exception as err:
        print(f'Other Error Occurred: {err}')
        raise
    else: 
        print('Successfully retrieved email from AWS Secrets Manager.')
        
        # Extract email from returned payload
        email_secret_payload: dict = json.loads(response['SecretString'])
        my_email: str = email_secret_payload['MY_EMAIL']
    
    # Check if my email is already subscribed to the SNS topic
    try:
        print('Pulling list of subscriptions from SNS topic...')
        
        topic_arn = os.getenv('SNS_TOPIC_ARN')
        sns = boto3.client('sns')
        
        response = sns.list_subscriptions_by_topic(
            TopicArn=topic_arn
        )
    except ClientError as err:
        print(f'Client Error Message: {err.response["Error"]["Message"]}')
        print(f'Client Error Code: {err.response["Error"]["Code"]}')
        raise
    except Exception as err:
        print(f'Other Error Occurred: {err}')
        raise
    else: 
        print('Successfully pulled list of subscriptions from SNS topic.')    
        
        print('Checking to see if my email is already subscribed...')
        subscriptions: list[dict] = response['Subscriptions']
        for subscription in subscriptions:
            if subscription['Endpoint'] == my_email:
                print('My email is already subscribed to the SNS topic.')
            else:
                print('My email is not subscribed to the SNS topic.')
                raise Exception('My email is not subscribed to the SNS topic.')
                
            
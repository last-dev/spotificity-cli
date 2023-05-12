"""
Custom construct for all resources that will enable the
app to email me every other week with any new music that is released 
by any of the artists I follow.
"""

from constructs import Construct
from aws_cdk import (
    aws_lambda as lambda_,
    aws_events as event,
    aws_events_targets as target,
    aws_dynamodb as ddb,
    aws_stepfunctions as stepfunction,
    aws_stepfunctions_tasks as task,
    aws_sns as sns,
    aws_sns_subscriptions as subs,
    aws_secretsmanager as ssm,
    aws_iam as iam
)

class NotifierConstruct(Construct):
    def __init__(self, scope: Construct, id: str, artist_table: ddb.Table, requests_layer: lambda_.LayerVersion, access_token_lambda: lambda_.Function, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
   
        # Lambda to pull the current list of artists being monitored
        _fetch_artists_lambda = lambda_.Function(
            self, 'GetArtistListForNotifierHandler',
            function_name='GetArtistListForNotifierHandler',
            runtime=lambda_.Runtime.PYTHON_3_10,
            code=lambda_.Code.from_asset('lambda_functions/NotifierConstructLambdas'),
            handler='get_artist_list_for_notifier.handler',
            layers=[requests_layer],
            environment={
                'ARTIST_TABLE_NAME': artist_table.table_name
            }
        )
        
        # Topic to publish my messages to   
        _topic = sns.Topic(
            self, 'NotifierTopic',
            topic_name='SpotificityNotifierTopic'
        ) 
        
        # Lambda function that will publish a message to SNS topic if there are currently no artists in the table
        _sms_if_no_artists_lambda = lambda_.Function(
            self, 'MessageIfNoArtistsHandler',
            function_name='MessageIfNoArtistsHandler',
            runtime=lambda_.Runtime.PYTHON_3_10,
            code=lambda_.Code.from_asset('lambda_functions/NotifierConstructLambdas'),
            handler='message_if_no_artists.handler',
            environment={
                'SNS_TOPIC_ARN': _topic.topic_arn
            }
        )

        # Lambda to fetch the latest music released by any of the artists being monitored
        _fetch_music_lambda = lambda_.Function(
            self, 'GetLatestMusicForNotifierHandler',
            function_name='GetLatestMusicForNotifierHandler',
            runtime=lambda_.Runtime.PYTHON_3_10,
            code=lambda_.Code.from_asset('lambda_functions/NotifierConstructLambdas'),
            handler='get_latest_music_for_notifier.handler',
            layers=[requests_layer],
        )

        # Tasks within our Step Function workflow 
        _fetch_access_token_task = task.LambdaInvoke(
            self, 'FetchAccessToken',
            lambda_function=access_token_lambda,  # type: ignore
            output_path='$.access_token',
            payload_response_only=True
        )

        _scan_task = task.LambdaInvoke(
            self, 'ScanArtistTable',
            lambda_function=_fetch_artists_lambda,  # type: ignore
            output_path='$.payload.status_code',
            payload_response_only=True
        )

        # If `_scan_task` returns with a status code of 204, we immediately publish SNS message to the topic.
        # Otherwise, we invoke the lambda to fetch the latest music released all artists 
        _choice_state = stepfunction.Choice(self, 'Artists in the list, or not?')
        
        # Define states for choice state 
        _if_no_artists_publish_task = task.LambdaInvoke(
            self, 'PublishEmailIfNoArtists',
            lambda_function=_sms_if_no_artists_lambda  # type: ignore
        )
        
        _fetch_latest_music_task = task.LambdaInvoke(
            self, 'FetchLatestMusic',
            lambda_function=_fetch_music_lambda,  # type: ignore
            payload_response_only=True
        )

        # Add conditions to the choice state 
        _choice_state.when(stepfunction.Condition.number_equals('$.payload.status_code', 204), _if_no_artists_publish_task)
        _choice_state.otherwise(_fetch_latest_music_task)

        # Connect tasks 
        _fetch_access_token_task.next(_scan_task)
        _scan_task.next(_choice_state)
        # _fetch_latest_music_task.next()

        # StateMachine for our entire step function workflow
        _state_machine = stepfunction.StateMachine(
            self, 'NotifierStateMachine',
            state_machine_name='NotifierStateMachine',
            definition=_fetch_access_token_task  # The initial task to invoke
        )

        # EventBridge rule to trigger Lambda StepFunction routine every week 
        _rule = event.Rule(
            self, "Rule",
            rule_name='WeeklyMusicFetchNotificationRule',
            schedule=event.Schedule.expression('rate(7 days)'),
            description='Triggers Lambda every week to fetch the latest musical releases from my list of artists.',
            targets=[target.SfnStateMachine(_state_machine)]   
        )
        
        # Import my email address to grant 'MessageIfNoArtistsHandler' Lambda permissions to pull secrets
        __my_email = ssm.Secret.from_secret_name_v2(
            self, 'ImportedEmailAddress',
            secret_name='EmailSecret'
        )
        
        # Give 'MessageIfNoArtistsHandler' permissions to read secrets
        __my_email.grant_read(_sms_if_no_artists_lambda)

        # Grant 'GetArtistListForNotifierHandler' Lambda permissions to read from the Artist table
        artist_table.grant_read_data(_fetch_artists_lambda)
        
        # Grant ListSubscriptionByTopic and Publish permissions to 'MessageIfNoArtistsHandler' Lambda
        _sms_if_no_artists_lambda.add_to_role_policy(
            iam.PolicyStatement(
                actions=[
                    'sns:ListSubscriptionsByTopic', 
                    'sns:Publish'
                ],
                resources=[_topic.topic_arn]
            )
        )
        
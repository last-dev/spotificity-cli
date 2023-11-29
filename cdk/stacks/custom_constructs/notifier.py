"""
Custom construct for all resources that will enable the
app to email me every week with any new music that is released 
by any of the artists I follow.
"""

from constructs import Construct
from aws_cdk import (
    aws_stepfunctions as stepfunction,
    aws_stepfunctions_tasks as task,
    aws_events_targets as target,
    aws_secretsmanager as ssm,
    aws_lambda as lambda_,
    aws_dynamodb as ddb,
    aws_events as event,
    aws_sns as sns,
    aws_iam as iam,
    Duration
)

class NotifierConstruct(Construct):
    def __init__(self, scope: Construct, id: str, artist_table: ddb.Table, requests_layer: lambda_.LayerVersion, access_token_lambda: lambda_.Function, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
   
        # All Lambdas throughout our StepFunction
        _fetch_artists_lambda = lambda_.Function(
            self, 'GetArtistListForNotifierHandler',
            description='Pulls the current list of artists being monitored',
            function_name='GetArtistListForNotifierHandler',
            runtime=lambda_.Runtime.PYTHON_3_10,
            code=lambda_.Code.from_asset('lambda_functions/NotifierConstructLambdas'),
            handler='get_artist_list_for_notifier.handler',
            layers=[requests_layer],
            environment={
                'ARTIST_TABLE_NAME': artist_table.table_name
            }
        )
        
        # Topic to publish my messages to. Instantiating this now so I can pass it into the next Lambda function as an environment variable.
        _topic = sns.Topic(
            self, 'NotifierTopic',
            topic_name='SpotificityNotifierTopic'
        ) 
        
        _email_if_no_artists_lambda = lambda_.Function(
            self, 'MessageIfNoArtistsHandler',
            description='Publishes a message to a SNS topic if there are currently no artists in the table',
            function_name='MessageIfNoArtistsHandler',
            runtime=lambda_.Runtime.PYTHON_3_10,
            code=lambda_.Code.from_asset('lambda_functions/NotifierConstructLambdas'),
            handler='message_if_no_artists.handler',
            environment={
                'SNS_TOPIC_ARN': _topic.topic_arn
            }
        )

        _fetch_music_lambda = lambda_.Function(
            self, 'GetLatestMusicForNotifierHandler',
            description='Fetches the latest music released by any of the artists being monitored',
            function_name='GetLatestMusicForNotifierHandler',
            runtime=lambda_.Runtime.PYTHON_3_10,
            timeout=Duration.seconds(45),
            code=lambda_.Code.from_asset('lambda_functions/NotifierConstructLambdas'),
            handler='get_latest_music_for_notifier.handler',
            layers=[requests_layer],
        )
        
        _update_table_music_lambda = lambda_.Function(
            self, 'UpdateTableMusicForNotifierHandler',
            description=f'Updates {artist_table.table_name} with the latest music released by all of the artists being monitored',
            function_name='UpdateTableMusicForNotifierHandler',
            runtime=lambda_.Runtime.PYTHON_3_10,
            timeout=Duration.seconds(45),
            code=lambda_.Code.from_asset('lambda_functions/NotifierConstructLambdas'),
            handler='update_table_music_for_notifier.handler',
            environment={
                'ARTIST_TABLE_NAME': artist_table.table_name
            }
        )
        
        _email_new_music_lambda = lambda_.Function(
            self, 'MessageNewMusicHandler',
            description='Publishes a message to a SNS topic with new music.',
            function_name='MessageNewMusicHandler',
            runtime=lambda_.Runtime.PYTHON_3_10,
            code=lambda_.Code.from_asset('lambda_functions/NotifierConstructLambdas'),
            handler='message_new_music.handler',
            environment={
                'SNS_TOPIC_ARN': _topic.topic_arn
            }
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
            output_path='$.payload',
            payload_response_only=True
        )

        # If `_scan_task` returns with a status code of 204, we immediately publish SNS message to the topic.
        # Otherwise, we invoke the lambda to fetch the latest music released all artists 
        _choice_state = stepfunction.Choice(self, 'Artists in the list, or not?')
        
        # Define tasks for choice state 
        _if_no_artists_publish_task = task.LambdaInvoke(
            self, 'PublishEmailIfNoArtists',
            lambda_function=_email_if_no_artists_lambda  # type: ignore
        )
        
        _fetch_latest_music_task = task.LambdaInvoke(
            self, 'FetchLatestMusic',
            lambda_function=_fetch_music_lambda,  # type: ignore
            output_path='$.latest_music',
            payload_response_only=True
        )

        # Add conditions to the choice state 
        _choice_state.when(stepfunction.Condition.number_equals('$.status_code', 204), _if_no_artists_publish_task)
        _choice_state.otherwise(_fetch_latest_music_task)
        
        # Continue listing the rest of the tasks in our Step Function workflow
        _update_table_task = task.LambdaInvoke(
            self, 'UpdateTableMusic',
            lambda_function=_update_table_music_lambda,  # type: ignore
            output_path='$.new_music',
            payload_response_only=True
        )
        
        _publish_results_task = task.LambdaInvoke(
            self, 'PublishResults',
            lambda_function=_email_new_music_lambda  # type: ignore
        )

        # Connect tasks to be in order
        _fetch_access_token_task.next(_scan_task)
        _scan_task.next(_choice_state)
        _fetch_latest_music_task.next(_update_table_task)
        _update_table_task.next(_publish_results_task)

        # StateMachine for our entire step function workflow
        _state_machine = stepfunction.StateMachine(
            self, 'NotifierStateMachine',
            state_machine_name='NotifierStateMachine',
            definition=_fetch_access_token_task  # The initial task to invoke
        )

        # EventBridge rule to trigger Lambda StepFunction routine every Sunday at 8AM EST
        _rule = event.Rule(
            self, "Rule",
            rule_name='WeeklyMusicFetchNotificationRule',
            schedule=event.Schedule.cron(minute='0', hour='12', week_day='SUN'),
            description='Triggers Lambda every week to fetch the latest musical releases from my list of artists.',
            targets=[target.SfnStateMachine(_state_machine)]   
        )
        
        # Import my email address to grant some Lambdas permission to pull secrets
        __my_email = ssm.Secret.from_secret_name_v2(
            self, 'ImportedEmailAddress',
            secret_name='EmailSecret'
        )
        
        # Give 'MessageIfNoArtistsHandler' and 'MessageNewMusicHandler' permissions to read my email secrets
        __my_email.grant_read(_email_if_no_artists_lambda)
        __my_email.grant_read(_email_new_music_lambda)

        # Grant 'GetArtistListForNotifierHandler' and 'UpdateTableMusicForNotifierHandler' permissions 
        # perform tasks on the Artist table
        artist_table.grant_read_data(_fetch_artists_lambda)
        artist_table.grant_write_data(_update_table_music_lambda)
        
        # Grant ListSubscriptionByTopic and Publish permissions to 'MessageIfNoArtistsHandler' and 'MessageNewMusicHandler' 
        _email_if_no_artists_lambda.add_to_role_policy(
            iam.PolicyStatement(
                actions=[
                    'sns:ListSubscriptionsByTopic', 
                    'sns:Publish'
                ],
                resources=[_topic.topic_arn]
            )
        )
        _email_new_music_lambda.add_to_role_policy(
            iam.PolicyStatement(
                actions=[
                    'sns:ListSubscriptionsByTopic',
                    'sns:Publish'
                ],
                resources=[_topic.topic_arn]
            )
        )
        

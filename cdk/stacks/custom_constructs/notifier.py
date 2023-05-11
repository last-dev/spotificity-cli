"""
Custom construct for all resources that will enable the
app to text me every week with any new music that is released 
by any of the artists I follow.
"""

from constructs import Construct
from aws_cdk import (
    aws_lambda as lambda_,
    aws_events as event,
    aws_events_targets as target,
    aws_dynamodb as ddb,
    aws_stepfunctions as stepfunction,
    aws_stepfunctions_tasks as task
)

class NotifierConstruct(Construct):
    def __init__(self, scope: Construct, id: str, artist_table: ddb.Table, requests_layer: lambda_.LayerVersion, access_token_lambda: lambda_.Function, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
   
        # Lambda to pull the current list of artists being monitored
        _fetch_artists_lambda = lambda_.Function(
            self, 'GetArtistListForNotifierHandler',
            function_name='GetArtistListForNotifierHandler',
            runtime=lambda_.Runtime.PYTHON_3_10,
            code=lambda_.Code.from_asset('lambda_functions/GetArtistListForNotifierHandler'),
            handler='get_artist_list_for_notifier.handler',
            layers=[requests_layer],
            environment={
                'ARTIST_TABLE_NAME': artist_table.table_name
            }
        )

        # Lambda to fetch the latest music released by any of the artists being monitored
        _fetch_music_lambda = lambda_.Function(
            self, 'GetLatestMusicForNotifierHandler',
            function_name='GetLatestMusicForNotifierHandler',
            runtime=lambda_.Runtime.PYTHON_3_10,
            code=lambda_.Code.from_asset('lambda_functions/GetLatestMusicForNotifierHandler'),
            handler='get_latest_music_for_notifier.handler',
            layers=[requests_layer],
        )

        """ Tasks within our Step Function workflow """
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

        # TODO: If _scan_task returns with a status code of 204, we immediately publish SNS message to the topic.
        # Otherwise, we invoke the lambda to fetch the latest music released all artists 
        _choice_state = stepfunction.Choice(self, 'Artists or not...')

        """ Define states for choice state """
        _fetch_latest_music_task = task.LambdaInvoke(
            self, 'FetchLatestMusic',
            lambda_function=_fetch_music_lambda,  # type: ignore
            payload_response_only=True
        )

        _no_artists_publish_task = task.SnsPublish()

        """ Add conditions to the choice state """
        _choice_state.when(stepfunction.Condition.number_equals('$.payload.status_code', 204), _no_artists_publish_task)
        _choice_state.otherwise(_fetch_latest_music_task)

        """ Connect tasks """
        _fetch_access_token_task.next(_scan_task)
        _scan_task.next(_choice_state)

        # StateMachine for our entire step function workflow
        _state_machine = stepfunction.StateMachine(
            self, 'NotifierStepFunction',
            state_machine_name='NotifierStepFunction',
            definition=_fetch_access_token_task  # The initial task to invoke
        )

        # EventBridge rule to trigger Lambda StepFunction routine every week 
        # _rule = event.Rule(
        #     self, "Rule",
        #     rule_name='WeeklyMusicFetchNotificationRule',
        #     schedule=event.Schedule.expression('rate(7 days)'),
        #     description='Triggers Lambda every week to fetch the latest musical releases from my list of artists.',
        #     targets=[_state_machine] 
        # )

        # Grant the Lambda function to read from the Artist table
        artist_table.grant_read_data(_fetch_artists_lambda)
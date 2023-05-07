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
    def __init__(self, scope: Construct, id: str, artist_table: ddb.Table, requests_layer: lambda_.LayerVersion, **kwargs) -> None:
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

        # Tasks within our Step Function workflow
        _scan_task = task.LambdaInvoke(
            self, 'InvokeLambdaStep1',
            lambda_function=_fetch_artists_lambda,  # type: ignore
            payload_response_only=True
        )

        # _fetch_latest_music_task = task.LambdaInvoke(
        #     self, 'InvokeLambdaStep2',
        #     lambda_function=_fetch_music_lambda,  # type: ignore
        #     payload_response_only=True
        # )

        # StateMachine for our entire step function workflow
        _state_machine = stepfunction.StateMachine(
            self, 'NotifierStepFunction',
            state_machine_name='NotifierStepFunction',
            definition=_scan_task  # The initial task to invoke
        )

        # EventBridge rule to trigger Lambda StepFunction routine every week 
        # _rule = event.Rule(
        #     self, "Rule",
        #     rule_name='WeeklyMusicFetchNotificationRule',
        #     schedule=event.Schedule.expression('rate(7 days)'),
        #     description='Triggers Lambda every week to fetch the latest musical releases from my list of artists.',
        #     targets=[_state_machine] 
        # )
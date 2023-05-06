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
    aws_stepfunctions as stepfunc,
    aws_stepfunctions_tasks as tasks
)

class NotifierConstruct(Construct):
    def __init__(self, scope: Construct, id: str, artist_table: ddb.Table, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
   
        # Lambda to pull the current list of artists being monitored
        _fetch_artists_lambda = lambda_.Function(
            self, 'GetLatestMusicForNotifierHandler',
            function_name='GetLatestMusicForNotifierHandler',
            runtime=lambda_.Runtime.PYTHON_3_10,
            code=lambda_.Code.from_asset('lambda_functions/GetLatestMusicForNotifierHandler'),
            handler='fetch_artist_list_notify.handler',
            # layers=,
            environment={
                'ARTIST_TABLE_NAME': artist_table.table_name
            }
        )
        
        # EventBridge rule to trigger Lambda StepFunction routine every week 
        _rule = event.Rule(
            self, "Rule",
            rule_name='WeeklyMusicFetchNotificationRule',
            schedule=event.Schedule.expression('rate(7 days)'),
            description='Triggers Lambda every week to fetch the latest musical releases from my list of artists.',
            targets=[target.LambdaFunction(_fetch_artists_lambda)]  # type: ignore
        )
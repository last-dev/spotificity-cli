from stacks.custom_constructs.spotify_operators import CoreSpotifyOperatorsConstruct
from stacks.custom_constructs.table_operators import CoreTableOperatorsConstruct
from stacks.custom_constructs.api_gateway import ApiGatewayConstruct
from stacks.custom_constructs.notifier import NotifierConstruct
from constructs import Construct
from aws_cdk import (
    Stack,
    aws_dynamodb as ddb,
    aws_lambda as lambda_,
)

class BackendStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, monitored_artist_table: ddb.Table, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Lambda layer that bundles `requests` module 
        requests_layer = lambda_.LayerVersion(
            self, 'RequestsLayer',
            code=lambda_.Code.from_asset('lambda_layers/requests_v2-28-2.zip'),
            layer_version_name='Requests_v2-28-2',
            description='Bundles the "requests" module.',
            compatible_runtimes=[lambda_.Runtime.PYTHON_3_10]
        )
        
        # Custom construct with setter, getter, and deleter Lambda functions 
        # for manipulating 'Monitored Artists' DynamoDB table
        table_operators = CoreTableOperatorsConstruct(
            self, 'TableManipulatorsConstruct',
            artist_table=monitored_artist_table
        )
        
        # Custom construct for the resources that will interact with the Spotify API
        spotify_operators = CoreSpotifyOperatorsConstruct(
            self, 'SpotifyOperatorsConstruct',
            artist_table_arn=monitored_artist_table.table_arn,
            artist_table_stream_arn=monitored_artist_table.table_stream_arn,  # type: ignore
            update_table_music_lambda=table_operators.update_table_music_lambda,
            requests_layer=requests_layer
        )

        # Custom construct for the step function workflow that will be triggered by an EventBridge rate expression
        notify_feature = NotifierConstruct(
            self, 'NotifierConstruct',
            artist_table=monitored_artist_table,
            requests_layer=requests_layer,
            access_token_lambda=spotify_operators.get_access_token_lambda
        )
        
        # Custom construct for the API Gateway that will be used to invoke the Lambda functions
        api_gateway = ApiGatewayConstruct(
            self, 'ApiGatewayConstruct',
            fetch_artists_lambda=table_operators.fetch_artists_lambda,
            add_artists_lambda=table_operators.add_artist_lambda,
            remove_artists_lambda=table_operators.remove_artist_lambda,
            access_token_lambda=spotify_operators.get_access_token_lambda,
            get_artist_id_lambda=spotify_operators.get_artist_id_lambda
        )
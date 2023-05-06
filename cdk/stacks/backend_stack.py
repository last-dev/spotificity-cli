from stacks.custom_constructs.table_operators import CoreTableOperatorsConstruct
from stacks.custom_constructs.spotify_operators import CoreSpotifyOperatorsConstruct
from constructs import Construct
from aws_cdk import (
    Stack,
    aws_dynamodb as ddb
)

class BackendStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, monitored_artist_table: ddb.Table, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
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
            update_table_music_lambda=table_operators.update_table_music_lambda
        )
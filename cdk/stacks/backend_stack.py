from stacks.custom_constructs.table_manipulators import TableManipulatorsConstruct
from stacks.custom_constructs.spotify_operators import SpotifyOperatorsConstruct
from constructs import Construct
from aws_cdk import (
    Stack,
    aws_dynamodb as ddb,
    Fn
)

class BackendStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, monitored_artist_table: ddb.Table, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Custom construct with setter, getter, and deleter Lambda functions 
        # for manipulating 'Monitored Artists' DynamoDB table
        table_manipulators = TableManipulatorsConstruct(
            self, 'TableManipulatorsConstruct',
            artist_table=monitored_artist_table
        )
        
        # Custom construct for the resources that will interact with the Spotify API
        spotify_operators = SpotifyOperatorsConstruct(
            self, 'SpotifyOperatorsConstruct',
            artist_table_arn=monitored_artist_table.table_arn,
            artist_table_stream_arn=monitored_artist_table.table_stream_arn,  # type: ignore
            update_table_music_lambda=table_manipulators.update_table_music_lambda
        )

from stacks.custom_constructs.table_manipulators import TableManipulatorsConstruct
from stacks.custom_constructs.spotify_operators import SpotifyOperatorsConstruct
from constructs import Construct
from aws_cdk import (
    Stack,
)

class BackendStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Custom construct with setter, getter, and deleter Lambda functions 
        # for manipulating 'Monitored Artists' DynamoDB table
        self.table_manipulators = TableManipulatorsConstruct(
            self, 'TableManipulatorsConstruct'
        )
        
        # Custom construct for the resources that will interact with the Spotify API
        self.spotify_operators = SpotifyOperatorsConstruct(
            self, 'SpotifyOperatorsConstruct'
        )
        
        
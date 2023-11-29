from constructs import Construct
from aws_cdk import (
    Stack,
    RemovalPolicy,
    aws_dynamodb as ddb,
)

class DatabaseStack(Stack):    
    
    @property
    def artist_table(self) -> ddb.Table:
        """ Returns the DynamoDB table name that holds the monitored artists. """
        return self._artist_table
    
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # DynamoDB table that stores all monitored artists
        self._artist_table = ddb.Table(
            self, 'MonitoredArtists', 
            partition_key={
                'name': 'artist_id',
                'type': ddb.AttributeType.STRING
            },
            stream=ddb.StreamViewType.NEW_IMAGE,  # Enable stream for lambda invocations
            encryption=ddb.TableEncryption.AWS_MANAGED,
            removal_policy=RemovalPolicy.RETAIN
        )



        

        


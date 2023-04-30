from constructs import Construct
from aws_cdk import (
    Stack,
    aws_dynamodb as ddb,
    aws_lambda as _lambda,
    RemovalPolicy,
    CfnOutput
)

class DatabaseStack(Stack):    
    def __init__(
            self, scope: Construct, construct_id: str, 
            get_artist_lambda: _lambda.Function, 
            add_artist_lambda: _lambda.Function, 
            remove_artist_lambda: _lambda.Function, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # DynamoDB table that stores all monitored artists
        self._artist_table = ddb.Table(
            self, 'MonitoredArtists', 
            partition_key={
                'name': 'artist_id',
                'type': ddb.AttributeType.STRING},
            encryption=ddb.TableEncryption.AWS_MANAGED,
            removal_policy=RemovalPolicy.DESTROY
        )

        # Export Artist table name as Cloudformation resource to be used in BackendStack
        CfnOutput(
            self, 'ArtistTableName',
            value=self._artist_table.table_name,
            export_name='ArtistTableName',
            description='Name of the DynamoDB table that holds Spotificity\'s monitored artists.'
        )

        # Give Lambda functions specific permissions to do their operations
        self._artist_table.grant_read_data(get_artist_lambda)
        self._artist_table.grant_write_data(add_artist_lambda)
        self._artist_table.grant_write_data(remove_artist_lambda)


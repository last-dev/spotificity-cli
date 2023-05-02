"""
Custom construct for the Setter, Getter, and Deleter Lambda 
functions for the DynamoDB table that stores the current 
monitored artists.
"""

from constructs import Construct
from aws_cdk import (
    aws_lambda as lambda_,
    aws_dynamodb as ddb,
    CfnOutput
)

class TableManipulatorsConstruct(Construct):  
    
    @property
    def update_table_music_lambda(self) -> lambda_.Function:
        """ Returns lambda Function object for 'UpdateTableMusicHandler' """
        return self._update_table_music_lambda
        
    def __init__(self, scope: Construct, id: str, artist_table: ddb.Table, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
        # Getter Lambda function for 'Monitored Artists' Table
        _get_artist_lambda = lambda_.Function(
            self, 'GetArtists',
            runtime=lambda_.Runtime.PYTHON_3_10,
            code=lambda_.Code.from_asset('lambda_functions/GetArtistsHandler'),
            handler='scan_table.handler',
            environment={
                'ARTIST_TABLE_NAME': artist_table.table_name
            },
            function_name='GetArtistsHandler',
            description=f'Returns a list of all current artists being monitored in "Monitored Artists" DynamoDB table ({artist_table.table_name}).'
        )

        # Setter Lambda function for 'Monitored Artists' Table
        _add_artist_lambda = lambda_.Function(
            self, 'AddArtists',
            runtime=lambda_.Runtime.PYTHON_3_10,
            code=lambda_.Code.from_asset('lambda_functions/AddArtistsHandler'),
            handler='put_to_table.handler',
            environment={
                'ARTIST_TABLE_NAME': artist_table.table_name
            },
            function_name='AddArtistsHandler',
            description=f'Adds a new artist to the "Monitored Artists" DynamoDB table ({artist_table.table_name}).'
        )
        
        # Deleter Lambda function for 'Monitored Artists' Table
        _remove_artist_lambda = lambda_.Function(
            self, 'RemoveArtists',
            runtime=lambda_.Runtime.PYTHON_3_10,
            code=lambda_.Code.from_asset('lambda_functions/RemoveArtistsHandler'),
            handler='remove_from_table.handler',
            environment={
                'ARTIST_TABLE_NAME': artist_table.table_name
            },
            function_name='RemoveArtistsHandler',
            description=f'Removes an artist from the "Monitored Artists" DynamoDB table ({artist_table.table_name}).'
        )
        
        # Lambda function that will update the 'Monitored Artists' table with the latest musical release for each artist
        self._update_table_music_lambda = lambda_.Function(
            self, 'UpdateTableMusic',
            runtime=lambda_.Runtime.PYTHON_3_10,
            code=lambda_.Code.from_asset('lambda_functions/UpdateTableMusicHandler'),
            handler='update_table_music.handler',
            environment={
                'ARTIST_TABLE_NAME': artist_table.table_name
            },
            function_name='UpdateTableMusicHandler',
            description=f'Once the latest musical release is pulled by "GetArtistLatestMusic" Lambda, this updates {artist_table.table_name}\'s artist attributes.'
        )

        # Give Lambda functions specific permissions to do their operations against the table
        artist_table.grant_read_data(_get_artist_lambda)
        artist_table.grant_write_data(_add_artist_lambda)
        artist_table.grant_write_data(_remove_artist_lambda)
        artist_table.grant_write_data(self._update_table_music_lambda)


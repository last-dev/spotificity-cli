"""
Custom construct for the Setter, Getter, and Deleter Lambda 
functions for the DynamoDB table that stores the current 
monitored artists.
"""

from constructs import Construct
from aws_cdk import (
    aws_lambda as lambda_,
    CfnOutput, Fn
)

class TableManipulatorsConstruct(Construct):
    
    @property
    def get_artists_lambda(self) -> lambda_.Function:
        """ Returns GetArtistHandler Lambda Function """
        return self._get_artist_lambda
    
    @property
    def add_artists_lambda(self) -> lambda_.Function:
        """ Returns AddArtistHandler Lambda Function """
        return self._add_artist_lambda
    
    @property
    def remove_artists_lambda(self) -> lambda_.Function:
        """ Returns RemoveArtistHandler Lambda Function """
        return self._remove_artist_lambda
    
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
        # Getter Lambda function for 'Monitored Artists' Table
        self._get_artist_lambda = lambda_.Function(
            self, 'GetArtistsHandler',
            runtime=lambda_.Runtime.PYTHON_3_10,
            code=lambda_.Code.from_asset('lambda_functions/GetArtistsHandler'),
            handler='scan_table.handler',
            environment={
                'ARTIST_TABLE_NAME': Fn.import_value('ArtistTableName')
            },
            function_name='GetArtistsHandler',
            description=f'Returns a list of all current artists being monitored in "Monitored Artists" DynamoDB table ({Fn.import_value("ArtistTableName")}).'
        )

        # Setter Lambda function for 'Monitored Artists' Table
        self._add_artist_lambda = lambda_.Function(
            self, 'AddArtistsHandler',
            runtime=lambda_.Runtime.PYTHON_3_10,
            code=lambda_.Code.from_asset('lambda_functions/AddArtistsHandler'),
            handler='put_to_table.handler',
            environment={
                'ARTIST_TABLE_NAME': Fn.import_value('ArtistTableName')
            },
            function_name='AddArtistsHandler',
            description=f'Adds a new artist to the "Monitored Artists" DynamoDB table ({Fn.import_value("ArtistTableName")}).'
        )
        
        # Deleter Lambda function for 'Monitored Artists' Table
        self._remove_artist_lambda = lambda_.Function(
            self, 'RemoveArtistsHandler',
            runtime=lambda_.Runtime.PYTHON_3_10,
            code=lambda_.Code.from_asset('lambda_functions/RemoveArtistsHandler'),
            handler='remove_from_table.handler',
            environment={
                'ARTIST_TABLE_NAME': Fn.import_value('ArtistTableName')
            },
            function_name='RemoveArtistsHandler',
            description=f'Removes an artist from the "Monitored Artists" DynamoDB table ({Fn.import_value("ArtistTableName")}).'
        )

        # Export Lambda Function names as Cloudformation resources to be used in BackendStack
        CfnOutput(
            self, 'GetArtistsLambdaName',
            value=self._get_artist_lambda.function_name,
            export_name='GetArtistsLambda',
            description='Name of Lambda function that list\'s all monitored artists.'
        )

        CfnOutput(
            self, 'AddArtistsLambdaName',
            value=self._add_artist_lambda.function_name,
            export_name='AddArtistsLambda',
            description='Name of Lambda function that adds a new artist to be monitored.'
        )

        CfnOutput(
            self, 'RemoveArtistsLambdaName',
            value=self._remove_artist_lambda.function_name,
            export_name='RemoveArtistsLambda',
            description='Name of Lambda function that removes an artist from being monitored.'
        )
"""
Custom construct for the resources that will interact with
the Spotify API. 
"""

from constructs import Construct
from aws_cdk import (
    aws_lambda as lambda_,
    aws_secretsmanager as ssm, 
)

class SpotifyOperatorsConstruct(Construct):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
        # Lambda layer that bundles `requests` module 
        _requests_layer = lambda_.LayerVersion(
            self, 'RequestsLayer',
            code=lambda_.Code.from_asset('lambda_layers/requests_v2-28-2.zip'),
            layer_version_name='Requests_v2-28-2',
            description='Bundles the "requests" module.',
            compatible_runtimes=[lambda_.Runtime.PYTHON_3_10]
        )
        
        # Spotify access token 'getter' Lambda Function
        self._get_access_token_lambda = lambda_.Function(
            self, 'GetAccessToken',
            runtime=lambda_.Runtime.PYTHON_3_10,
            code=lambda_.Code.from_asset('lambda_functions/GetAccessTokenHandler'),
            handler='get_access_token.handler',
            function_name='GetAccessTokenHandler',
            description=f'Calls Spotify\'s "/token" API endpoint to get an access token.',
            layers=[_requests_layer]
        )
        
        # Spotify artist_id 'getter' Lambda Function
        self._get_artist_id_lambda = lambda_.Function(
            self, 'GetArtistID',
            runtime=lambda_.Runtime.PYTHON_3_10,
            code=lambda_.Code.from_asset('lambda_functions/GetArtist-IDHandler'),
            handler='get_artist_id.handler',
            function_name='GetArtist-IDHandler',
            description=f'Queries the Spotify "/search" API endpoint for the artist ID.',
            layers=[_requests_layer]
        )
        
        # Import existent Spotify Secret to grant the associated Lambda permissions below 
        __spotify_secrets = ssm.Secret.from_secret_name_v2(
            self, 'ImportedSpotifySecrets',
            secret_name='SpotifySecrets'
        )
        
        # Give 'GetAccessTokenHandler' Lambda permissions to read secret
        __spotify_secrets.grant_read(self._get_access_token_lambda)
        

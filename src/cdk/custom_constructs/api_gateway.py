"""
Custom construct for API Gateway resources that will be used 
to invoke `CoreTableOperator` Lambda functions.
"""

from constructs import Construct
from aws_cdk import (
    aws_apigateway as api_gw,
    aws_lambda as lambda_,
    aws_iam as iam,
    CfnOutput
)

class ApiGatewayConstruct(Construct):
    def __init__(self, scope: Construct, id: str, 
                 fetch_artists_lambda: lambda_.Function,
                 add_artists_lambda: lambda_.Function,
                 remove_artists_lambda: lambda_.Function, 
                 access_token_lambda: lambda_.Function, 
                 get_artist_id_lambda: lambda_.Function, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
        # Create an IAM Role for API Gateway to assume. We'll use this to 
        # allow API Gateway to invoke our Lambdas
        api_gateway_role = iam.Role(
            self, 'ApiGatewayRole',
            assumed_by=iam.ServicePrincipal('apigateway.amazonaws.com')
        )
        
        # Create API Gateway
        self.api = api_gw.RestApi(
            self, "ApiForClientInvokes",
            description="API Gateway for Lambdas invoked from client.",
            policy=api_gateway_role.assume_role_policy
        )
        
        # Lambda Integrations 
        fetch_artists_integration = api_gw.LambdaIntegration(fetch_artists_lambda)  # type: ignore
        add_artists_integration = api_gw.LambdaIntegration(add_artists_lambda)  # type: ignore
        remove_artists_integration = api_gw.LambdaIntegration(remove_artists_lambda)  # type: ignore
        access_token_integration = api_gw.LambdaIntegration(access_token_lambda)  # type: ignore
        get_artist_id_integration = api_gw.LambdaIntegration(get_artist_id_lambda)  # type: ignore
        
        """
        Define resources and methods for all CoreTableOperator Lambda functions.
        Making sure that IAM Authentication is enabled for each Gateway method
        """
        # GET /token
        token_resource = self.api.root.add_resource('token')
        token_resource.add_method('GET', access_token_integration, authorization_type=api_gw.AuthorizationType.IAM)
        
        # GET /artist
        artist_resource = self.api.root.add_resource('artist')
        artist_resource.add_method('GET', fetch_artists_integration, authorization_type=api_gw.AuthorizationType.IAM)
        
        # POST/artist/id
        get_artist_id_resource = artist_resource.add_resource('id')
        get_artist_id_resource.add_method('POST', get_artist_id_integration, authorization_type=api_gw.AuthorizationType.IAM)

        # POST /artist
        add_artist_resource = artist_resource
        add_artist_resource.add_method('POST', add_artists_integration, authorization_type=api_gw.AuthorizationType.IAM)

        # DELETE /artist  
        remove_artist_resource = artist_resource
        remove_artist_resource.add_method('DELETE', remove_artists_integration, authorization_type=api_gw.AuthorizationType.IAM)
        
        # Give permissions to APIGateway's assumed IAM role to invoke lambdas
        fetch_artists_lambda.grant_invoke(api_gateway_role)
        add_artists_lambda.grant_invoke(api_gateway_role)
        remove_artists_lambda.grant_invoke(api_gateway_role)
        access_token_lambda.grant_invoke(api_gateway_role)
        get_artist_id_lambda.grant_invoke(api_gateway_role)
        
        # Output the API Gateway URL
        CfnOutput(
            self, "ApiGatewayEndpoint", 
            value=self.api.url,
            description="Api Gateway Endpoint URL Export"
        )

        
        

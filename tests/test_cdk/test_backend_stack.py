from cdk.stacks.backend_stack import BackendStack
import aws_cdk as cdk
from aws_cdk import assertions
import pytest

def setup_backend_stack() -> assertions.Template:
    """
    Setup Backend Stack for each unit test to cut-back on code duplication.
    
    Return: Assertion Template
    """
    app = cdk.App()
    stack = BackendStack(app, "SpotificityBackendStack")
    return assertions.Template.from_stack(stack)


def test_lambda_functions_created() -> None:
    """
    Test that Lambda resources are created
    """
    template = setup_backend_stack()
    
    template.resource_count_is("AWS::Lambda::Function", 5) 


def test_lambda_layers_created() -> None:
    """
    Test that the Lambda layer is created
    """
    template = setup_backend_stack()

    template.resource_count_is("AWS::Lambda::LayerVersion", 1)


def test_lambda_layer_properties() -> None:
    """
    Test that the Lambda layer has the correct properties
    """
    template = setup_backend_stack()

    template.has_resource_properties("AWS::Lambda::LayerVersion", {
        "LayerName": "Requests_v2-28-2",
        "CompatibleRuntimes": ["python3.10"],
    })


def test_get_access_token_lambda_has_layer() -> None:
    """
    Test that GetAccessTokenHandler Lambda has the Requests layer
    """
    template = setup_backend_stack()

    template.has_resource_properties("AWS::Lambda::Function", {
        "Handler": "get_access_token.handler",
        "Layers": [{"Ref": "SpotifyOperatorsConstructRequestsLayer1038E257"}]
    })

def test_get_artist_id_lambda_has_layer() -> None:
    """
    Test that GetArtist-IDHandler Lambda has the Requests layer
    """
    template = setup_backend_stack()

    template.has_resource_properties("AWS::Lambda::Function", {
        "Handler": "get_artist_id.handler",
        "Layers": [{"Ref": "SpotifyOperatorsConstructRequestsLayer1038E257"}]
    })


def test_get_artists_lambda_has_env_vars() -> None:
    """
    Test that GetArtistsHandler Lambda has proper environmental variables
    """
    template = setup_backend_stack()
    get_artists_env_capture = assertions.Capture()

    template.has_resource_properties("AWS::Lambda::Function", {
        "Handler": "scan_table.handler",
        "Environment": get_artists_env_capture
    })

    assert get_artists_env_capture.as_object() == {
        "Variables": {
            "ARTIST_TABLE_NAME": {'Fn::ImportValue': 'ArtistTableName'}
        },
    }


def test_add_artists_lambda_has_env_vars() -> None:
    """
    Test that AddArtistsHandler Lambda has proper environmental variables
    """
    template = setup_backend_stack()
    add_artists_env_capture = assertions.Capture()

    template.has_resource_properties("AWS::Lambda::Function", {
        "Handler": "put_to_table.handler",
        "Environment": add_artists_env_capture
    })

    assert add_artists_env_capture.as_object() == {
        "Variables": {
            "ARTIST_TABLE_NAME": {'Fn::ImportValue': 'ArtistTableName'}
        },
    }


def test_remove_artists_lambda_has_env_vars() -> None:
    """
    Test that RemoveArtistsHandler Lambda has proper environmental variables
    """
    template = setup_backend_stack()
    remove_artists_env_capture = assertions.Capture()

    template.has_resource_properties("AWS::Lambda::Function", {
        "Handler": "remove_from_table.handler",
        "Environment": remove_artists_env_capture
    })

    assert remove_artists_env_capture.as_object() == {
        "Variables": {
            "ARTIST_TABLE_NAME": {'Fn::ImportValue': 'ArtistTableName'}
        },
    }


# def test_secrets_policy_created() -> None:
#     """
#     Test to confirm IAM Policy that allows GetAccessTokenHandler Lambda to read Secrets Manager is created
#     """
#     template = setup_backend_stack()

#     template.has_resource_properties("AWS::IAM::Policy", {
#         "PolicyDocument": {
#             "Statement": [
#                 {
#                     "Action": [
#                         "secretsmanager:GetSecretValue",
#                         "secretsmanager:DescribeSecret",
#                     ],
#                     "Effect": "Allow",
#                     "Resource": {"Fn::Sub": "arn:${AWS::Partition}:secretsmanager:${AWS::Region}:${AWS::AccountId}:secret:SpotifySecrets-*"}
#                 }
#             ]
#         }
#     })

# def test_get_artists_lambda_has_permissions() -> None:
#     """
#     Test that GetArtistsHandler Lambda has an service role IAM policy that allows it read
#     access to ImportValue: SpotificityDatabaseStack:ExportsOutputFnGetAttMonitoredArtistsF43162C1Arn42E05247
#     """
#     template = setup_backend_stack()

#     template.has_resource_properties("AWS::Lambda::Function", {
#         "Permissions": [
#             {
#                 "Action": "dynamodb:Scan",
#                 "Effect": "Allow",
#                 "Resource": {
#                     "Fn::ImportValue": "SpotificityDatabaseStack:ExportsOutputFnGetAttMonitoredArtistsF43162C1Arn42E05247"
#                 }
#             }
#         ]
#     })
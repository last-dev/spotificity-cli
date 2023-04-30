from cdk.stacks.backend_stack import BackendStack
from cdk.stacks.database_stack import DatabaseStack
import aws_cdk as cdk
from aws_cdk import assertions
import pytest

def setup_database_stack() -> assertions.Template:
    """
    Setup Database Stack for each unit test to cut-back on code duplication.
    
    Return: Assertion Template
    """
    app = cdk.App()
    backend_stack = BackendStack(app, "TestBackendStack")
    stack = DatabaseStack(
        app, "TestDatabaseStack",
        get_artist_lambda=backend_stack.table_manipulators.get_artists_lambda,
        add_artist_lambda=backend_stack.table_manipulators.add_artists_lambda,
        remove_artist_lambda=backend_stack.table_manipulators.remove_artists_lambda,
    )
    return assertions.Template.from_stack(stack)

def test_dynamodb_table_created() -> None:
    """
    Test that Dynamodb resource for monitored artists is created
    """
    template = setup_database_stack()
    
    template.resource_count_is("AWS::DynamoDB::Table", 1)
    
def test_dynamodb_with_encryption() -> None:
    """
    Test that Dynamodb resource for monitored artists is 
    created with encryption enabled
    """
    template = setup_database_stack()
    
    template.has_resource_properties("AWS::DynamoDB::Table", {
    "SSESpecification": {
        "SSEEnabled": True,
        },
    })

def test_dynamodb_table_partition_key() -> None:
    """
    Test that the DynamoDB table has the correct partition key
    """
    template = setup_database_stack()

    template.has_resource_properties("AWS::DynamoDB::Table", {
        "KeySchema": [
            {
                "AttributeName": "artist_id",
                "KeyType": "HASH"
            }
        ],
        "AttributeDefinitions": [
            {
                "AttributeName": "artist_id",
                "AttributeType": "S"
            }
        ]
    })

def test_dynamodb_table_removal_policy() -> None:
    """
    Test that the DynamoDB table has the correct removal policy
    """
    template = setup_database_stack()

    template.has_resource("AWS::DynamoDB::Table", {
        "DeletionPolicy": "Delete"
    })

def test_dynamodb_table_name_output() -> None:
    """
    Test that the DynamoDB table has a CfnOutput for its name
    """
    template = setup_database_stack()

    template.has_output("ArtistTableName", {
        "Export": {
            "Name": "ArtistTableName"
        },
        "Value": {
            "Ref": "MonitoredArtists73108B5E"
        }
    })
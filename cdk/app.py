#!/usr/bin/env python3

from stacks.backend_stack import BackendStack
from stacks.database_stack import DatabaseStack
import os
import aws_cdk as cdk

# Use my personal AWS account
default_account = cdk.Environment(
        account=os.getenv('CDK_DEFAULT_ACCOUNT'), 
        region=os.getenv('CDK_DEFAULT_REGION')
    )

app = cdk.App()
backend_stack = BackendStack(
    app, 'SpotificityBackendStack',
    env=default_account
)
database_stack = DatabaseStack(
    app, 'SpotificityDatabaseStack', 
    get_artist_lambda=backend_stack.table_manipulators.get_artists_lambda,
    add_artist_lambda=backend_stack.table_manipulators.add_artists_lambda, 
    remove_artist_lambda=backend_stack.table_manipulators.remove_artists_lambda,
    env=default_account
)

# Establishing that the BackendStack depends on the DatabaseStack. 
# This ensures that the DatabaseStack is deployed before the BackendStack
backend_stack.add_dependency(database_stack)

app.synth()

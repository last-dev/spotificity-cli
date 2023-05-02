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
database_stack = DatabaseStack(
    app, 'SpotificityDatabaseStack',
    env=default_account
)
backend_stack = BackendStack(
    app, 'SpotificityBackendStack',
    env=default_account,
    monitored_artist_table=database_stack.artist_table
)

# Establishing that the BackendStack depends on the DatabaseStack. 
# This ensures that the DatabaseStack is deployed before the BackendStack
backend_stack.add_dependency(database_stack)

app.synth()

#!/usr/bin/env python3

import os

from aws_cdk import App, Environment
from stacks.backend_stack import BackendStack
from stacks.database_stack import DatabaseStack

default_account = Environment(
    account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')
)

app = App()
database_stack = DatabaseStack(app, 'DatabaseStack', env=default_account)
backend_stack = BackendStack(
    app,
    'BackendStack',
    env=default_account,
    monitored_artist_table=database_stack.artist_table,
)
backend_stack.add_dependency(database_stack)

app.synth()

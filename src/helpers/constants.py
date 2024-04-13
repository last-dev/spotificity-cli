import os
from dataclasses import dataclass
from enum import Enum


class Stage(Enum):
    Dev = 'Dev'
    Prod = 'Prod'
    Beta = 'Beta'


@dataclass(frozen=True)
class Account:
    account_id: str
    stage: Stage
    region: str
    api_gw_endpoint_ssm_param_name: str


# Define my development accounts for each stage
accounts: dict[str, Account] = {
    'Beta': Account(
        account_id=os.environ['SPOTIFICITY_BETA_ACCT'],
        stage=Stage.Beta,
        region='us-east-1',
        api_gw_endpoint_ssm_param_name='/Spotificity/ApiGatewayEndpointUrl/beta',
    ),
    'Prod': Account(
        account_id=os.environ['SPOTIFICITY_PROD_ACCT'],
        stage=Stage.Prod,
        region='us-east-1',
        api_gw_endpoint_ssm_param_name='/Spotificity/ApiGatewayEndpointUrl/prod',
    ),
}

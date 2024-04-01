import os
from dataclasses import dataclass
from enum import Enum


class Stage(Enum):
    Dev = 'Dev'
    Prod = 'Prod'
    Beta = 'Beta'


class AwsRegion(Enum):
    IAD = 'us-east-1'


@dataclass(frozen=True)
class Account:
    account_id: str
    stage: Stage
    region: AwsRegion
    disambiguator: str


# Define my development accounts for each stage
accounts: dict[str, Account] = {
    'Beta': Account(
        account_id=os.environ['SPOTIFICITY_BETA_ACCT'],
        stage=Stage.Beta,
        region=AwsRegion.IAD,
        disambiguator='beta',
    ),
    'Prod': Account(
        account_id=os.environ['SPOTIFICITY_PROD_ACCT'],
        stage=Stage.Prod,
        region=AwsRegion.IAD,
        disambiguator='prod',
    ),
}

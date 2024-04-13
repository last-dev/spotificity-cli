from boto3 import Session
from botocore.exceptions import ClientError

from ..helpers.constants import Account, accounts
from ..ui.colors import RED
from .argparser import ArgParser
from .signed_requests import Requests


class FailedToRetrieveEndpoint(Exception):
    """
    Raised when app fails to retrieve endpoint from SSM Parameter Store
    """

    def __init__(self, error_message: ClientError) -> None:
        self.err = error_message

    def __str__(self) -> str:
        return f'{RED}\n\nFailed to retrieve API Gateway endpoint url from SSM:\n{self.err}'


class FailedToRetrieveToken(Exception):
    """
    Raised when Lambda function returns None for an access token
    """

    def __str__(self) -> str:
        return f'{RED}\n\nFailed to return access token from Spotify. Check Lambda logs.'


class InitialSetup:
    """
    Class to handle initial setup of application.
    """

    def __init__(self) -> None:
        argparser = ArgParser()
        self._aws_profile = argparser.profile_name

        for stage in accounts.keys():
            if stage.lower() in self._aws_profile:
                self._account: Account = accounts[stage]
                break

        self._endpoint = self.get_apigw_endpoint(self._aws_profile, self._account)
        self._access_token = self.request_access_token(self._endpoint, self.aws_profile)

    def get_apigw_endpoint(self, aws_profile: str, account: Account) -> str:
        """
        Retrieve API Gateway endpoint Url from SSM Parameter Store
        """
        try:
            session = Session(profile_name=aws_profile)
            ssm = session.client('ssm')
            parameter = ssm.get_parameter(Name=account.api_gw_endpoint_ssm_param_name, WithDecryption=True)
        except ClientError as err:
            raise FailedToRetrieveEndpoint(err)
        else:
            return parameter['Parameter']['Value']

    def request_access_token(self, apigw_endpoint: str, aws_profile: str) -> str:
        """
        Invoke Lambda function that fetches an Authenticated access token
        needed for all future API calls to Spotify.
        """
        response = Requests.signed_request('GET', f'{apigw_endpoint}token', aws_profile)

        if response.json().get('access_token') is None:
            raise FailedToRetrieveToken
        else:
            return response.json()['access_token']

    @property
    def account(self) -> Account:
        """AWS profile account configs"""
        return self._account

    @property
    def endpoint(self) -> str:
        """API Gateway base URL endpoint"""
        return self._endpoint

    @property
    def aws_profile(self) -> str:
        """AWSCli profile to use for all Boto3 calls"""
        return self._aws_profile

    @property
    def access_token(self) -> str:
        """Authenticated Spotify access token"""
        return self._access_token

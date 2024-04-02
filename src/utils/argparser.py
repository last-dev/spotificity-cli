from argparse import ArgumentParser
from configparser import ConfigParser
from pathlib import Path

from ..ui.colors import RED


class AwsProfileDoesNotExist(Exception):
    """
    Raised when the given awscli profile does not exist in the config file
    """

    def __init__(self, profile: str, config_path: Path) -> None:
        self.profile = profile
        self.config_path = config_path

    def __str__(self) -> str:
        return f'{RED}\n\nProfile "{self.profile}" not found in: {self.config_path.resolve()}'


class AwsCliConfigDoesNotExist(Exception):
    """
    Raised when the awscli config file does not exists in ~/.aws
    """

    def __init__(self, config_path: Path) -> None:
        self.config_path = config_path

    def __str__(self) -> str:
        return f'{RED}\n\nAwsCLI config file not found at: {self.config_path.resolve()}\
            \nConsider running "aws configure --profile [profile-name]"'


class ArgParser:
    """
    Class to parse passed in cli arg to ensure it is an awscli profile name that exists
    within the awscli config file.
    """

    @property
    def profile_name(self) -> str:
        return self._profile_name

    def __init__(self) -> None:
        self._profile_name: str = self.parse_cli_args()
        self.check_aws_profile_exists(self._profile_name)

    def parse_cli_args(self) -> str:
        parser = ArgumentParser(
            prog='spotificity.py',
            description='Built with AWS\'s CDK, this app will notify me on a weekly basis if \
                any of the artists I follow have released a new track or album.',
        )
        parser.add_argument(
            '-p',
            '--profile',
            dest='profile',
            type=str,
            help='AWS CLI profile to be used for all Boto3 calls in the script.',
            required=True,
        )
        args = parser.parse_args()
        return args.profile

    def check_aws_profile_exists(self, profile_name: str) -> None:
        config = ConfigParser()
        aws_config_path = Path.home() / '.aws' / 'config'

        if not aws_config_path.exists():
            raise AwsCliConfigDoesNotExist(aws_config_path)

        config.read(aws_config_path)
        if f'profile {profile_name}' not in config.sections():
            raise AwsProfileDoesNotExist(profile_name, aws_config_path)

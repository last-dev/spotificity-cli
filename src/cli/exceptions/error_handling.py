from ui.colors import RED


class FailedToRetrieveToken(Exception):
    """
    Raised when Lambda function returns None for an access token
    """
    def __str__(self) -> str:
        return f'{RED}\n\nFailed to return access_token from "GetAccessTokenHandler"'


class FailedToRetrieveMonitoredArtists(Exception):
    """
    Raised when scan operation against DynamoDB table fails
    """
    def __init__(self, error_message: str) -> None:
        self.error_message = error_message

    def __str__(self) -> str:
        return f'{RED}\nFailed to retrieve list of artists from DynamoDB table: \n\n{self.error_message}'


class FailedToRetrieveListOfMatchesWithIDs(Exception):
    """
    Raised when a GET request to the Spotify API fails
    """
    def __init__(self, error_message: str) -> None:
        self.error_message = error_message

    def __str__(self) -> str:
        return f'{RED}\nFailed to retrieve list of close matches to user choice from Spotify API: \n\n{self.error_message}'


class FailedToAddArtistToTable(Exception):
    """
    Raised when PUT operation on DynamoDB table fails
    """
    def __init__(self, error_message: str) -> None:
        self.error_message = error_message

    def __str__(self) -> str:
        return f'{RED}\nFailed to add artist to DynamoDB table: \n\n{self.error_message}'


class FailedToRemoveArtistFromTable(Exception):
    """
    Raised when DELETE operation on DynamoDB table fails
    """
    def __init__(self, error_message: str) -> None:
        self.error_message = error_message

    def __str__(self) -> str:
        return f'{RED}\nFailed to remove artist from DynamoDB table: \n\n{self.error_message}'


class FailedToRetrieveEndpoint(Exception):
    """
    Raised when app fails to retrieve endpoint from SSM Parameter Store
    """
    def __init__(self, error_message: str) -> None:
        self.error_message = error_message

    def __str__(self) -> str:
        return f'{RED}\nFailed to retrieve API Gateway endpoint Url from SSM Parameter Store: \n\n{self.error_message}'

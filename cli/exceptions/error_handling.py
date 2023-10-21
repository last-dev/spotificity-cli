from ui.colors import Style

class FailedToRetrieveToken(Exception):
    """
    Raised when Lambda function returns None for an access token
    """        
    def __str__(self) -> str:
        return f'{Style.RED}\n\nFailed to return access_token from "GetAccessTokenHandler"'
    
class FailedToRetrieveMonitoredArtists(Exception):
    """
    Raised when scan operation against DynamoDB table fails
    """
    def __init__(self, error_message: str) -> None:
        self.error_message = error_message

    def __str__(self) -> str:
        return f'{Style.RED}\nFailed to retrieve list of artists from DynamoDB table: \n\n{self.error_message}'
    
class ExceptionDuringLambdaExecution(Exception):
    """
    When an exception is raised during execution of a Lambda function, this exception is raised here at the client
    """
    def __init__(self, lambda_name: str, error_message: str) -> None:
        self.error_message = error_message
        self.lambda_name = lambda_name

    def __str__(self) -> str:
        return f'{Style.RED}\nWhile executing {self.lambda_name}, an exception was raised: \n\n{self.error_message}'
        
class FailedToRetrieveListOfMatchesWithIDs(Exception):
    """
    Raised when a GET request to the Spotify API fails
    """
    def __init__(self, error_message: str) -> None:
        self.error_message = error_message

    def __str__(self) -> str:
        return f'{Style.RED}\nFailed to retrieve list of close matches to user choice from Spotify API: \n\n{self.error_message}'
    
class FailedToAddArtistToTable(Exception):
    """
    Raised when PUT operation on DynamoDB table fails
    """
    def __init__(self, error_message: str) -> None:
        self.error_message = error_message

    def __str__(self) -> str:
        return f'{Style.RED}\nFailed to add artist to DynamoDB table: \n\n{self.error_message}'
    
class FailedToRemoveArtistFromTable(Exception):
    """
    Raised when DELETE operation on DynamoDB table fails
    """
    def __init__(self, error_message: str) -> None:
        self.error_message = error_message

    def __str__(self) -> str:
        return f'{Style.RED}\nFailed to remove artist from DynamoDB table: \n\n{self.error_message}'
from ui.colors import Colors, print_colors, colorfy

class FailedToRetrieveToken(Exception):
    """
    Raised when Lambda function returns None for an access token
    """        
    def __str__(self) -> str:
        return colorfy(Colors.RED, '\n\nFailed to return access_token from "GetAccessTokenHandler"')
    
class FailedToRetrieveListOfArtists(Exception):
    """
    Raised when scan operation against DynamoDB table fails
    """
    def __init__(self, error_message: str) -> None:
        self.error_message = error_message

    def __str__(self) -> str:
        return colorfy(Colors.RED, f'\nFailed to retrieve list of artists from DynamoDB table: \n\n{self.error_message}')
    
class ExceptionDuringLambdaExecution(Exception):
    """
    Raised when an exception is raised during execution of a Lambda function
    """
    def __init__(self, lambda_name: str, error_message: str) -> None:
        self.error_message = error_message
        self.lambda_name = lambda_name

    def __str__(self) -> str:
        return colorfy(Colors.RED, f'\nWhile executing {self.lambda_name}, an exception was raised: \n\n{self.error_message}')
        

    
class FailedToRetrieveToken(Exception):
    """
    Raised when Lambda function returns None for an access token
    """        
    def __str__(self) -> str:
        return '\n\nFailed to return access_token from "GetAccessTokenHandler"'
    

    
import requests
from boto3 import Session
from requests import HTTPError, Response
from requests_aws4auth import AWS4Auth


class Requests:
    """
    Class for sending signed HTTP requests to AWS services.
    """

    @staticmethod
    def signed_request(method: str, url: str, aws_profile: str, payload=None) -> Response:
        credentials = Session(profile_name=aws_profile).get_credentials()
        auth = AWS4Auth(
            credentials.access_key,
            credentials.secret_key,
            region='us-east-1',
            service='execute-api',
            session_token=credentials.token,
        )

        http_method_map = {
            'GET': requests.get,
            'POST': requests.post,
            'PUT': requests.put,
            'DELETE': requests.delete,
        }
        http_request_method = http_method_map[method]

        try:
            response: Response = http_request_method(
                url, auth=auth, data=payload, headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
        except HTTPError as err:
            print(f'HTTP Error occurred: {err}')
            raise
        else:
            return response

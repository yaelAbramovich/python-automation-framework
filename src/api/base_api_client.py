import json
from abc import ABC
from enum import Enum
from typing import Any, Optional

from playwright.sync_api import APIRequestContext, APIResponse

from src.infrastructure.logger import Logger


class HttpMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


class HttpRequestOptions:
    def __init__(
        self,
        query_parameters: Optional[dict[str, Any]] = None,
        request_headers: Optional[dict[str, str]] = None,
        json_request_body: Optional[Any] = None,
    ) -> None:
        self.query_parameters = query_parameters
        self.request_headers = request_headers
        self.json_request_body = json_request_body


class BaseApiClient(ABC):
    """
    BaseApiClient wraps Playwright's APIRequestContext and adds consistent
    logging for every request and response. Concrete clients (e.g. a
    UsersApiClient) extend this class and expose endpoint-specific methods.
    """

    def __init__(self, request_context: APIRequestContext, client_logger_name: str) -> None:
        if type(self) is BaseApiClient:
            raise TypeError("BaseApiClient cannot be instantiated directly")
        self._request_context = request_context
        self._logger = Logger(client_logger_name)

    def _send_http_request(
        self,
        http_method: HttpMethod,
        request_url_path: str,
        request_options: Optional[HttpRequestOptions] = None,
    ) -> APIResponse:
        request_options = request_options or HttpRequestOptions()
        self._logger.info(f"Sending {http_method.value} request to: {request_url_path}")

        api_response = self._request_context.fetch(
            request_url_path,
            method=http_method.value,
            params=request_options.query_parameters,
            headers=request_options.request_headers,
            data=request_options.json_request_body,
        )

        self._logger.info(
            f"Received HTTP {api_response.status} response from: {request_url_path}"
        )

        return api_response

    def _parse_response_as_json(self, api_response: APIResponse) -> Any:
        response_body_text = api_response.text()
        try:
            return json.loads(response_body_text)
        except json.JSONDecodeError as parse_error:
            self._logger.error(
                f"Failed to parse response body as JSON. Raw body: {response_body_text}",
                parse_error,
            )
            raise

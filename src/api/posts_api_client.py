from typing import Any

from playwright.sync_api import APIRequestContext, APIResponse

from src.api.base_api_client import BaseApiClient, HttpMethod


class PostsApiClient(BaseApiClient):
    _SINGLE_POST_PATH_TEMPLATE = "/posts/{post_id}"

    def __init__(self, request_context: APIRequestContext) -> None:
        super().__init__(request_context, "PostsApiClient")

    def get_post_by_id(self, post_id: int) -> tuple[APIResponse, dict[str, Any]]:
        response = self._send_http_request(
            HttpMethod.GET, self._SINGLE_POST_PATH_TEMPLATE.format(post_id=post_id)
        )
        return response, self._parse_response_as_json(response)

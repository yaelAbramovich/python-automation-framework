from playwright.sync_api import APIRequestContext

from src.api.base_api_client import BaseApiClient, HttpMethod


class _ExamplePostsApiClient(BaseApiClient):
    """
    Minimal concrete API client demonstrating BaseApiClient against
    jsonplaceholder.typicode.com. Local to this example test, not part of
    the reusable src/api framework.
    """

    _SINGLE_POST_PATH_TEMPLATE = "/posts/{post_id}"

    def __init__(self, request_context: APIRequestContext) -> None:
        super().__init__(request_context, "ExamplePostsApiClient")

    def get_post_by_id(self, post_id: int):
        response = self._send_http_request(
            HttpMethod.GET, self._SINGLE_POST_PATH_TEMPLATE.format(post_id=post_id)
        )
        return response, self._parse_response_as_json(response)


def test_get_post_by_id_returns_matching_post(api_request_context: APIRequestContext) -> None:
    client = _ExamplePostsApiClient(api_request_context)

    response, post = client.get_post_by_id(1)

    assert response.ok
    assert post["id"] == 1
    assert "title" in post

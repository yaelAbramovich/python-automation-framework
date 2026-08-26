from playwright.sync_api import APIRequestContext

from src.api.posts_api_client import PostsApiClient


def test_get_post_by_id_returns_matching_post(api_request_context: APIRequestContext) -> None:
    client = PostsApiClient(api_request_context)

    response, post_body = client.get_post_by_id(1)

    client.assert_post_retrieved_successfully(response)
    assert post_body["id"] == 1, f"Expected post id 1 but got {post_body['id']}"
    assert "title" in post_body, f"Expected response body to contain a 'title' field: {post_body}"

from playwright.sync_api import APIRequestContext

from src.api.posts_api_client import PostsApiClient


def test_get_post_by_id_returns_matching_post(api_request_context: APIRequestContext) -> None:
    client = PostsApiClient(api_request_context)

    response, post = client.get_post_by_id(1)

    assert response.ok
    assert post["id"] == 1
    assert "title" in post

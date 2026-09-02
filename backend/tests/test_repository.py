import httpx
import respx
from fastapi.testclient import TestClient

from app.main import app

MOCK_REPO = {
    "name": "hello-world",
    "full_name": "octocat/hello-world",
    "description": "My first repository",
    "html_url": "https://github.com/octocat/hello-world",
    "homepage": None,
    "stargazers_count": 100,
    "forks_count": 20,
    "subscribers_count": 5,
    "open_issues_count": 3,
    "default_branch": "main",
    "language": "Python",
    "topics": ["demo", "example"],
    "archived": False,
    "fork": False,
    "license": {"name": "MIT License"},
    "created_at": "2020-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "pushed_at": "2024-01-01T00:00:00Z",
    "owner": {
        "login": "octocat",
        "avatar_url": "https://avatars.githubusercontent.com/u/1",
        "html_url": "https://github.com/octocat",
        "type": "User",
    },
}
MOCK_LANGUAGES = {"Python": 800, "TypeScript": 200}


def test_get_repository_returns_normalized_overview():
    with respx.mock(assert_all_called=False) as router:
        router.get("https://api.github.com/repos/octocat/hello-world").mock(
            return_value=httpx.Response(200, json=MOCK_REPO)
        )
        router.get(
            "https://api.github.com/repos/octocat/hello-world/languages"
        ).mock(return_value=httpx.Response(200, json=MOCK_LANGUAGES))

        with TestClient(app) as client:
            response = client.get("/api/repositories/octocat/hello-world")

    assert response.status_code == 200
    body = response.json()
    assert body["full_name"] == "octocat/hello-world"
    assert body["stars"] == 100
    assert body["languages"][0]["name"] == "Python"
    assert body["languages"][0]["percentage"] == 80.0


def test_get_repository_returns_friendly_404():
    with respx.mock(assert_all_called=False) as router:
        router.get("https://api.github.com/repos/octocat/missing").mock(
            return_value=httpx.Response(404, json={"message": "Not Found"})
        )

        with TestClient(app) as client:
            response = client.get("/api/repositories/octocat/missing")

    assert response.status_code == 404
    body = response.json()
    assert body["error"] == "repository_not_found"
    assert "octocat/missing" in body["detail"]
    assert "Traceback" not in response.text


def test_get_repository_returns_friendly_rate_limit_error():
    with respx.mock(assert_all_called=False) as router:
        router.get("https://api.github.com/repos/octocat/hello-world").mock(
            return_value=httpx.Response(
                403,
                json={"message": "rate limited"},
                headers={"x-ratelimit-remaining": "0"},
            )
        )

        with TestClient(app) as client:
            response = client.get("/api/repositories/octocat/hello-world")

    assert response.status_code == 429
    assert response.json()["error"] == "rate_limit_exceeded"


def test_get_languages_endpoint():
    with respx.mock(assert_all_called=False) as router:
        router.get(
            "https://api.github.com/repos/octocat/hello-world/languages"
        ).mock(return_value=httpx.Response(200, json=MOCK_LANGUAGES))

        with TestClient(app) as client:
            response = client.get("/api/repositories/octocat/hello-world/languages")

    assert response.status_code == 200
    body = response.json()
    assert body["languages"][0]["name"] == "Python"

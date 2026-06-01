from backend.secret_redaction import REDACTED_SECRET_VALUE

TEST_BEARER_SECRET = "Bearer nested-secret-token"
TEST_EXPLICIT_SECRET = "explicit-secret"
TEST_GITHUB_REVIEW_SECRET = "ghp_localreviewsecret0000000000"
TEST_NESTED_API_KEY = "sk-nested-review-secret"
TEST_OBSERVABILITY_API_KEY = "sk-observability-review-secret"
TEST_OBSERVABILITY_BEARER_SECRET = "Bearer observability-secret-token"
TEST_OBSERVABILITY_SLACK_TOKEN = "xoxb-observability-review-secret"
TEST_SLACK_REVIEW_TOKEN = "xoxb-nested-review-secret"


def nested_secret_payload() -> dict[str, object]:
    return {
        "authorization": TEST_BEARER_SECRET,
        "nested": {
            "provider": {"api_key": TEST_NESTED_API_KEY},
            "items": [{"token": TEST_SLACK_REVIEW_TOKEN}, {"status": "ok"}],
        },
        "message": f"adapter returned {TEST_GITHUB_REVIEW_SECRET}",
    }


def audit_secret_payload() -> dict[str, object]:
    payload = nested_secret_payload()
    payload["tool"] = "slack.post_message"
    payload["diagnostic"] = "adapter returned xoxb-should-not-store-value"
    payload["items"] = [
        {"token": "xoxb-should-not-store"},
        {"note": "fallback used sk-should-not-store-value"},
        {"result": "ok"},
    ]
    return payload


def observability_secret_fields() -> dict[str, object]:
    return {
        "provider": {"api_key": TEST_OBSERVABILITY_API_KEY},
        "headers": {"authorization": TEST_OBSERVABILITY_BEARER_SECRET},
        "items": [{"token": TEST_OBSERVABILITY_SLACK_TOKEN}],
        "status": "ok",
    }


def workspace_secret_lines() -> list[str]:
    return [
        "deepseek-open-art=sk-local-review-secret",
        f"github_token: {TEST_GITHUB_REVIEW_SECRET}",
        "slack = xoxb-local-review-secret",
        "password = keepthissecret",
    ]


def side_effect_secret_client_response(*, status: str) -> dict[str, object]:
    return {
        "authorization": "Bearer side-effect-secret",
        "debug": {"api_key": "sk-side-effect-secret"},
        "status": status,
    }


def assert_no_known_nested_secrets(serialized: str) -> None:
    for secret in (
        TEST_GITHUB_REVIEW_SECRET,
        TEST_NESTED_API_KEY,
        TEST_OBSERVABILITY_API_KEY,
        TEST_OBSERVABILITY_BEARER_SECRET,
        TEST_OBSERVABILITY_SLACK_TOKEN,
        TEST_SLACK_REVIEW_TOKEN,
    ):
        assert secret not in serialized


def assert_nested_payload_redacted(redacted: dict[str, object]) -> None:
    assert redacted["authorization"] == REDACTED_SECRET_VALUE
    nested = redacted["nested"]
    assert isinstance(nested, dict)
    provider = nested["provider"]
    assert isinstance(provider, dict)
    assert provider["api_key"] == REDACTED_SECRET_VALUE
    items = nested["items"]
    assert isinstance(items, list)
    assert items[0]["token"] == REDACTED_SECRET_VALUE
    assert items[1]["status"] == "ok"

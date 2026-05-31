from backend.secret_redaction import (
    LOWER_REDACTED_SECRET_VALUE,
    REDACTED_SECRET_VALUE,
    contains_secret_like_value,
    looks_secret_key,
    redact_secret_text,
    redact_secret_value,
)


def test_redact_secret_value_redacts_keys_nested_values_and_secret_shapes() -> None:
    redacted = redact_secret_value(
        {
            "authorization": "Bearer explicit-secret",
            "nested": {
                "api_key": "sk-nested-secret",
                "status": "ok",
            },
            "items": [
                {"token": "xoxb-local-secret-token"},
                {"message": "adapter echoed ghp_localreviewsecret0000000000"},
            ],
        },
        explicit_secrets=("explicit-secret",),
    )

    assert redacted["authorization"] == REDACTED_SECRET_VALUE
    assert redacted["nested"]["api_key"] == REDACTED_SECRET_VALUE
    assert redacted["nested"]["status"] == "ok"
    assert redacted["items"][0]["token"] == REDACTED_SECRET_VALUE
    assert redacted["items"][1]["message"] == f"adapter echoed {REDACTED_SECRET_VALUE}"
    assert "explicit-secret" not in repr(redacted)
    assert "ghp_localreviewsecret0000000000" not in repr(redacted)


def test_redact_secret_text_supports_lowercase_replacement_for_slack() -> None:
    redacted = redact_secret_text(
        "Do not leak xoxp-unexpected-outbound-secret-123456 or explicit",
        explicit_secrets=("explicit",),
        replacement=LOWER_REDACTED_SECRET_VALUE,
    )

    assert redacted == "Do not leak [redacted] or [redacted]"


def test_redact_secret_value_can_only_redact_keys_for_structured_request_snapshots() -> None:
    redacted = redact_secret_value(
        {"api_key": "secret", "message": "Bearer non-key-value"},
        redact_string_values=False,
    )

    assert redacted == {"api_key": REDACTED_SECRET_VALUE, "message": "Bearer non-key-value"}


def test_looks_secret_key_covers_adapter_secret_terms() -> None:
    assert looks_secret_key("oauth_token")
    assert looks_secret_key("private_webhook_secret")
    assert looks_secret_key("Authorization")
    assert not looks_secret_key("model")


def test_contains_secret_like_value_covers_tokens_and_assignments() -> None:
    assert contains_secret_like_value("token: keepthissecret")
    assert contains_secret_like_value("Bearer nested-secret-token")
    assert contains_secret_like_value("github_token: ghp_localreviewsecret0000000000")
    assert not contains_secret_like_value("model: deepseek-v4-pro")

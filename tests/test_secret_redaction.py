from backend.secret_redaction import (
    LOWER_REDACTED_SECRET_VALUE,
    REDACTED_SECRET_VALUE,
    contains_secret_like_value,
    contains_unredacted_secret_value,
    is_redacted_secret_value,
    looks_secret_key,
    redact_secret_text,
    redact_secret_value,
    secret_key_value_is_unredacted,
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


def test_contains_unredacted_secret_value_covers_structured_payloads() -> None:
    assert contains_unredacted_secret_value({"api_key": "plain-secret"})
    assert contains_unredacted_secret_value({"metadata": {"token": "xoxb-local-secret-token"}})
    assert contains_unredacted_secret_value(["message ghp_localreviewsecret0000000000"])
    assert not contains_unredacted_secret_value(
        {
            "api_key": REDACTED_SECRET_VALUE,
            "oauth_token": LOWER_REDACTED_SECRET_VALUE,
            "optional_secret": "",
            "missing_token": None,
            "message": "model: deepseek-v4-pro",
        }
    )


def test_secret_key_value_unredacted_check_ignores_empty_or_redacted_values() -> None:
    assert secret_key_value_is_unredacted("plain-secret")
    assert not secret_key_value_is_unredacted("")
    assert not secret_key_value_is_unredacted(None)
    assert not secret_key_value_is_unredacted(REDACTED_SECRET_VALUE)
    assert not secret_key_value_is_unredacted(LOWER_REDACTED_SECRET_VALUE)


def test_is_redacted_secret_value_accepts_standard_replacements() -> None:
    assert is_redacted_secret_value(REDACTED_SECRET_VALUE)
    assert is_redacted_secret_value(LOWER_REDACTED_SECRET_VALUE)
    assert not is_redacted_secret_value("plain-secret")

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from typing import Any, cast, get_args

from pydantic import BaseModel

from backend.health_contracts import health_response_payload
from backend.interface_types import Operation, RequestKind
from backend.request_scope_contracts import DEFAULT_POLICY_SCOPE, DEFAULT_REQUESTER_SCOPE
from backend.schemas import (
    ClassifyRequest,
    ExecutionEnvelopeRequest,
    HumanApproval,
    PolicyEvaluateRequest,
    SourceFreshness,
)
from backend.service import classify_request, create_execution_envelope, evaluate_policy


JSON_INDENT = 2
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000


def _json_response(payload: BaseModel | dict[str, Any]) -> str:
    if isinstance(payload, BaseModel):
        return payload.model_dump_json(indent=JSON_INDENT)
    return json.dumps(payload, indent=JSON_INDENT, sort_keys=True)


def _source_freshness(changed_source_count: int) -> SourceFreshness:
    return SourceFreshness(
        all_required_sources_unchanged=changed_source_count == 0,
        changed_source_count=changed_source_count,
    )


def _print_payload(payload: BaseModel | dict[str, Any]) -> None:
    print(_json_response(payload))


def health_command(_args: argparse.Namespace) -> int:
    _print_payload(health_response_payload())
    return 0


def classify_command(args: argparse.Namespace) -> int:
    response = classify_request(
        ClassifyRequest(
            request_text=args.request_text,
            operation=cast(Operation | None, args.operation),
        )
    )
    _print_payload(response)
    return 0


def policy_command(args: argparse.Namespace) -> int:
    response = evaluate_policy(
        PolicyEvaluateRequest(
            request_kind=cast(RequestKind, args.request_kind),
            operation=cast(Operation, args.operation),
            requester_scope=args.requester_scope,
            policy_scope=args.policy_scope,
            requires_human_approval=args.requires_human_approval,
            source_freshness=_source_freshness(args.changed_source_count),
        )
    )
    _print_payload(response)
    return 0


def envelope_command(args: argparse.Namespace) -> int:
    classified = classify_request(
        ClassifyRequest(
            request_text=args.request_text,
            operation=cast(Operation | None, args.operation),
        )
    )
    response = create_execution_envelope(
        ExecutionEnvelopeRequest(
            request_id=classified.request_id,
            request_kind=classified.request_kind,
            operation=classified.operation,
            requester_scope=args.requester_scope,
            policy_scope=args.policy_scope,
            target=args.target,
            human_approval=HumanApproval(
                approved=args.approved,
                approver_scope=args.approver_scope,
            ),
            source_freshness=_source_freshness(args.changed_source_count),
        )
    )
    _print_payload(response)
    return 0


def serve_command(args: argparse.Namespace) -> int:
    import uvicorn

    uvicorn.run(
        "backend.app:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )
    return 0


def _add_common_scope_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--requester-scope", default=DEFAULT_REQUESTER_SCOPE)
    parser.add_argument("--policy-scope", default=DEFAULT_POLICY_SCOPE)


def _add_source_freshness_option(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--changed-source-count",
        type=int,
        default=0,
        help="Number of changed required sources; non-zero marks freshness as failed.",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ai-artist",
        description="Use the AI-Artist safety service from the command line.",
    )
    subcommands = parser.add_subparsers(dest="command", required=True)

    health_parser = subcommands.add_parser("health", help="Print local service health JSON.")
    health_parser.set_defaults(func=health_command)

    classify_parser = subcommands.add_parser("classify", help="Classify a request.")
    classify_parser.add_argument("request_text")
    classify_parser.add_argument("--operation", choices=get_args(Operation))
    classify_parser.set_defaults(func=classify_command)

    policy_parser = subcommands.add_parser("policy", help="Evaluate a policy decision.")
    policy_parser.add_argument("--request-kind", required=True, choices=get_args(RequestKind))
    policy_parser.add_argument("--operation", required=True, choices=get_args(Operation))
    _add_common_scope_options(policy_parser)
    policy_parser.add_argument(
        "--requires-human-approval",
        action=argparse.BooleanOptionalAction,
        default=True,
    )
    _add_source_freshness_option(policy_parser)
    policy_parser.set_defaults(func=policy_command)

    envelope_parser = subcommands.add_parser(
        "envelope",
        help="Classify a request and create an execution envelope.",
    )
    envelope_parser.add_argument("request_text")
    envelope_parser.add_argument("--target", required=True)
    envelope_parser.add_argument("--operation", choices=get_args(Operation))
    _add_common_scope_options(envelope_parser)
    _add_source_freshness_option(envelope_parser)
    envelope_parser.add_argument("--approved", action="store_true")
    envelope_parser.add_argument("--approver-scope")
    envelope_parser.set_defaults(func=envelope_command)

    serve_parser = subcommands.add_parser("serve", help="Run the FastAPI service with uvicorn.")
    serve_parser.add_argument("--host", default=DEFAULT_HOST)
    serve_parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    serve_parser.add_argument("--reload", action="store_true")
    serve_parser.set_defaults(func=serve_command)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return cast(int, args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "build_parser",
    "main",
]

from backend.runtime_field_contracts import STATUS_FIELD, TASK_ID_FIELD
from backend.subagent_output_contracts import (
    SUBAGENT_AGENT_NAME_FIELD,
    SUBAGENT_ARTIFACTS_FIELD,
    SUBAGENT_CONFIDENCE_FIELD,
    SUBAGENT_ERRORS_FIELD,
    SUBAGENT_POLICY_NOTES_FIELD,
    SUBAGENT_SOURCES_FIELD,
    SUBAGENT_SUMMARY_FIELD,
)
from backend.subagent_status import SUBAGENT_STATUS_OK


def valid_subagent_output_payload_for_test() -> dict[str, object]:
    return {
        TASK_ID_FIELD: "88888888-8888-8888-8888-888888888888",
        SUBAGENT_AGENT_NAME_FIELD: "knowledge",
        STATUS_FIELD: SUBAGENT_STATUS_OK,
        SUBAGENT_SUMMARY_FIELD: "Retrieved two source-backed context notes.",
        SUBAGENT_ARTIFACTS_FIELD: [
            {
                "artifact_type": "research_note",
                "artifact_id": "note-001",
                "uri": "minio://ai-artist/artifacts/note-001.json",
                "metadata": {"format": "json"},
            }
        ],
        SUBAGENT_SOURCES_FIELD: [
            {
                "source_id": "source-001",
                "title": "Internal style guide",
                "uri": "minio://ai-artist/sources/style-guide.md",
            }
        ],
        SUBAGENT_POLICY_NOTES_FIELD: ["No external write requested."],
        SUBAGENT_CONFIDENCE_FIELD: 0.84,
        SUBAGENT_ERRORS_FIELD: [],
    }

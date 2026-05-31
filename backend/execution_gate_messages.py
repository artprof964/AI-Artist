EXECUTION_ENVELOPE_INVALID = "execution envelope is invalid"
EXECUTION_ENVELOPE_NOT_VALID = "execution envelope is not valid"
EXECUTION_ENVELOPE_NOT_ALLOWED = "execution envelope does not allow execution"
EXECUTION_ENVELOPE_REQUIRES_HUMAN_APPROVAL = "execution envelope requires human approval"
EXECUTION_ENVELOPE_MISSING_SIGNATURE = "execution envelope must include a signature"
EXECUTION_ENVELOPE_EXPIRED = "execution envelope is expired"


def execution_envelope_operation_mismatch(operation: str) -> str:
    return f"execution envelope operation must be {operation}"


def execution_envelope_target_mismatch(target_label: str) -> str:
    return f"execution envelope target does not match {target_label}"


def operation_requires_human_approval(operation: str) -> str:
    return f"{operation} requires human approval"

package ai_artist

default allow = false

write_operations = {"write", "publish", "delete", "github_write"}

allow {
	input.operation == "read"
	input.request_kind == "read"
}

allow {
	input.operation == "reuse"
	input.request_kind == "read"
	input.source_freshness.all_required_sources_unchanged == true
	input.source_freshness.changed_source_count == 0
}

allow {
	input.operation == "image_generate"
	input.execution_envelope.valid == true
	input.execution_envelope.operation == input.operation
}

allow {
	write_operations[_] == input.operation
	input.execution_envelope.valid == true
	input.execution_envelope.operation == input.operation
	valid_human_approval
}

requires_human_approval {
	write_operations[_] == input.operation
}

requires_human_approval {
	input.operation == "image_generate"
	input.review_required == true
}

valid_human_approval {
	input.human_approval.approved == true
	input.human_approval.approver_scope != ""
}

deny_reason = "operation denied by default policy" {
	not allow
}

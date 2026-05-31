$ErrorActionPreference = "Stop"

$python = if (Test-Path ".\.venv\Scripts\python.exe") {
    ".\.venv\Scripts\python.exe"
} else {
    "python"
}

function Invoke-NativeCommand {
    param(
        [Parameter(Mandatory = $true)]
        [scriptblock]$Command
    )

    & $Command
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
}

Invoke-NativeCommand {
    & $python -m pytest `
        -p no:cacheprovider `
        --cov=backend.app `
        --cov=backend.audit `
        --cov=backend.response_cache `
        --cov=backend.schemas `
        --cov=backend.service `
        --cov=backend.source_freshness `
        --cov-report=term-missing `
        --cov-fail-under=90 `
        tests\test_safety_service_units.py `
        tests\test_safety_service_endpoints.py `
        tests\test_opa_policy.py `
        tests\test_response_cache.py `
        tests\test_source_freshness.py `
        tests\test_audit_event_log.py
}

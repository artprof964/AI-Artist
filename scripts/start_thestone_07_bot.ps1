$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$ComposeFile = Join-Path $ProjectRoot "docker-compose.yml"

if (-not (Test-Path -LiteralPath $ComposeFile)) {
    throw "Missing docker-compose.yml at $ComposeFile"
}

function Get-EnvValue {
    param([Parameter(Mandatory = $true)][string]$Name)

    $value = [Environment]::GetEnvironmentVariable($Name, "Process")
    if (-not [string]::IsNullOrWhiteSpace($value)) {
        return $value.Trim()
    }

    $value = [Environment]::GetEnvironmentVariable($Name, "User")
    if (-not [string]::IsNullOrWhiteSpace($value)) {
        return $value.Trim()
    }

    $value = [Environment]::GetEnvironmentVariable($Name, "Machine")
    if (-not [string]::IsNullOrWhiteSpace($value)) {
        return $value.Trim()
    }

    return ""
}

$telegramToken = Get-EnvValue "tele_thestone_07"
if ([string]::IsNullOrWhiteSpace($telegramToken)) {
    throw "Missing required Telegram token env var: tele_thestone_07"
}

$deepseekKey = Get-EnvValue "DEEPSEEK_OPEN_ART"
if ([string]::IsNullOrWhiteSpace($deepseekKey)) {
    $deepseekKey = Get-EnvValue "deepseek-open-art"
}
if ([string]::IsNullOrWhiteSpace($deepseekKey)) {
    $deepseekKey = Get-EnvValue "DEEPSEEK_API_KEY"
}
if ([string]::IsNullOrWhiteSpace($deepseekKey)) {
    throw "Missing required DeepSeek key env var: DEEPSEEK_OPEN_ART, deepseek-open-art, or DEEPSEEK_API_KEY"
}

$env:tele_thestone_07 = $telegramToken
$env:DEEPSEEK_OPEN_ART = $deepseekKey

$thestone01Token = Get-EnvValue "tele_thestone_01"
if ([string]::IsNullOrWhiteSpace($thestone01Token)) {
    $env:tele_thestone_01 = "__compose_config_unused_thestone_01__"
}
else {
    $env:tele_thestone_01 = $thestone01Token
}

$thestone04Token = Get-EnvValue "tele_thestone_04"
if ([string]::IsNullOrWhiteSpace($thestone04Token)) {
    $env:tele_thestone_04 = "__compose_config_unused_thestone_04__"
}
else {
    $env:tele_thestone_04 = $thestone04Token
}

Push-Location $ProjectRoot
try {
    docker compose config --quiet
    docker compose up -d thestone_07-bot
    docker compose ps thestone_07-bot
    docker compose logs --tail=80 thestone_07-bot
}
finally {
    Pop-Location
}

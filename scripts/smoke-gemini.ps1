param(
    [Parameter(Mandatory = $false)]
    [ValidateSet("single", "dialogue")]
    [string]$Case = "single",

    [switch]$Execute
)

$ErrorActionPreference = "Stop"

$config = if ($Case -eq "dialogue") {
    "examples/dialogue.json"
} else {
    "examples/single-speaker.json"
}

if (-not $Execute) {
    Write-Host "DRY RUN ONLY - no Gemini request will be sent."
    ai-voice render $config
    exit $LASTEXITCODE
}

if (-not $env:GEMINI_API_KEY) {
    throw "GEMINI_API_KEY must be set before -Execute is allowed."
}

$out = "output/smoke-$Case.wav"
Write-Host "LIVE GEMINI SMOKE TEST: $Case -> $out"
ai-voice render $config --execute --out $out
exit $LASTEXITCODE

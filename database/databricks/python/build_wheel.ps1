$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$distDir = Join-Path $repoRoot "dist"

if (!(Test-Path $distDir)) {
    New-Item -ItemType Directory -Path $distDir | Out-Null
}

Push-Location $repoRoot
try {
    try {
        python -m build --wheel --no-isolation --outdir $distDir
    }
    catch {
        python setup.py bdist_wheel --dist-dir $distDir
    }
}
finally {
    Pop-Location
}

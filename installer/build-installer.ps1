[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$installerDirectory = Split-Path -Parent $PSCommandPath
$projectDirectory = Split-Path -Parent $installerDirectory
$manifestPath = Join-Path $projectDirectory 'fusion_addin\FrameKit\FrameKit.manifest'
$scriptPath = Join-Path $installerDirectory 'FrameKit.iss'
$compilerCandidates = @(
    (Join-Path ${env:ProgramFiles(x86)} 'Inno Setup 6\ISCC.exe'),
    (Join-Path $env:ProgramFiles 'Inno Setup 6\ISCC.exe')
)
$compiler = $compilerCandidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1

if (-not $compiler) {
    throw 'Inno Setup 6 was not found. Install it from https://jrsoftware.org/isinfo.php.'
}

$manifestText = Get-Content -LiteralPath $manifestPath -Raw
$manifestVersionMatch = [regex]::Match($manifestText, '"version"\s*:\s*"([^"]+)"')
if (-not $manifestVersionMatch.Success) {
    throw "No version was found in $manifestPath."
}
$manifestVersion = $manifestVersionMatch.Groups[1].Value
$versionDefinition = Select-String -LiteralPath $scriptPath -Pattern '^#define MyAppVersion "([^"]+)"$'
if (-not $versionDefinition -or $versionDefinition.Matches[0].Groups[1].Value -ne $manifestVersion) {
    throw "Installer and manifest versions do not match. Expected $manifestVersion."
}

$versionPath = Join-Path $projectDirectory 'fusion_addin\FrameKit\version.py'
$pythonVersionMatch = [regex]::Match((Get-Content -LiteralPath $versionPath -Raw), "__version__\s*=\s*'([^']+)'")
if (-not $pythonVersionMatch.Success -or $pythonVersionMatch.Groups[1].Value -ne $manifestVersion) {
    throw 'version.py and manifest versions do not match.'
}

& $compiler $scriptPath
if ($LASTEXITCODE -ne 0) {
    throw "Inno Setup failed with exit code $LASTEXITCODE."
}

$outputPath = Join-Path $installerDirectory "dist\FrameKit-Setup-$manifestVersion.exe"
if (-not (Test-Path -LiteralPath $outputPath)) {
    throw "Installer output was not created: $outputPath"
}

$hash = (Get-FileHash -LiteralPath $outputPath -Algorithm SHA256).Hash.ToLowerInvariant()
$checksumPath = $outputPath + '.sha256'
[IO.File]::WriteAllText($checksumPath, "$hash  $([IO.Path]::GetFileName($outputPath))`n", [Text.Encoding]::ASCII)
Write-Output "Created $outputPath"
Write-Output "SHA256 $hash"

# Compatible with Windows PowerShell 5.1 and PowerShell 7.
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Show-Usage {
    @'
Usage:
  .\bin\create_project.ps1 TARGET_DIR [DISPLAY_NAME]
  bin\create_project.bat TARGET_DIR [DISPLAY_NAME]

Examples:
  .\bin\create_project.ps1 ..\ragapi
  .\bin\create_project.ps1 ..\ragapi "RAG API"
'@
}

if ($args.Count -gt 0 -and $args[0] -in @('-h', '--help')) {
    Show-Usage
    exit 0
}
if ($args.Count -lt 1 -or $args.Count -gt 2) {
    [Console]::Error.WriteLine((Show-Usage))
    exit 1
}

try {
    $sourceDir = Split-Path -Parent $PSScriptRoot
    $targetDir = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($args[0])
    $targetDir = $targetDir.TrimEnd([IO.Path]::DirectorySeparatorChar, [IO.Path]::AltDirectorySeparatorChar)
    if (Test-Path -LiteralPath $targetDir) {
        throw "Target already exists: $targetDir"
    }

    $targetBasename = [IO.Path]::GetFileName($targetDir)
    $projectSlug = ($targetBasename.ToLowerInvariant() -replace '[^a-z0-9_]+', '_') -replace '_+', '_'
    $projectSlug = $projectSlug.Trim('_')
    if ($projectSlug -cnotmatch '^[a-z][a-z0-9_]*$') {
        throw "Target directory name must produce a valid snake_case project name: $targetBasename"
    }
    if (-not (Get-Command git -CommandType Application -ErrorAction SilentlyContinue)) {
        throw 'This script requires Git on PATH.'
    }

    $displayName = if ($args.Count -eq 2 -and $args[1]) {
        [string]$args[1]
    } else {
        ($projectSlug.Split('_') | ForEach-Object {
            $_.Substring(0, 1).ToUpperInvariant() + $_.Substring(1)
        }) -join ' '
    }
    $dockerName = $projectSlug.Replace('_', '-')
    $rootExclusions = @(
        '.git', '.env', '.env.local', 'env', 'venv', '.venv', 'ENV',
        '__pycache__', '.pytest_cache', 'storage', 'storage_test', 'htmlcov', '.coverage'
    )
    $fileExclusions = @(
        'bin/create_project.sh', 'bin/create_project.ps1', 'bin/create_project.bat',
        'spec/system/test_create_project.py'
    )
    # Strict UTF-8 decoding avoids changing binary files or silently corrupting bytes.
    # Reading/writing bytes also preserves existing line endings and UTF-8 BOMs.
    $utf8 = New-Object System.Text.UTF8Encoding($false, $true)

    function Copy-Template([string]$from, [string]$to, [string]$relative = '') {
        [IO.Directory]::CreateDirectory($to) | Out-Null
        foreach ($item in Get-ChildItem -LiteralPath $from -Force) {
            $path = if ($relative) { "$relative/$($item.Name)" } else { $item.Name }
            if ((-not $relative -and $item.Name -in $rootExclusions) -or
                $path -in $fileExclusions -or
                $item.Name -match '\.(db|sqlite|sqlite3)(-.*)?$' -or
                $item.FullName -eq $targetDir) {
                continue
            }
            $destination = Join-Path $to $item.Name
            if ($item.PSIsContainer) {
                Copy-Template $item.FullName $destination $path
                continue
            }
            $bytes = [IO.File]::ReadAllBytes($item.FullName)
            if ($path -notmatch '(^|/)(\.git|env|venv|\.venv|__pycache__)/' -and
                $bytes -notcontains 0) {
                $content = $null
                try {
                    $content = $utf8.GetString($bytes)
                } catch [System.Text.DecoderFallbackException] {
                    # Non-UTF-8 files are copied unchanged.
                }
                if ($null -ne $content) {
                    $content = $content.Replace('default_api_fast', $projectSlug)
                    $content = $content.Replace('default-api-fast-secret', "$projectSlug-secret")
                    $content = $content.Replace('Default API Fast', $displayName)
                    $content = $content.Replace('default-fast-api', $dockerName)
                    $bytes = $utf8.GetBytes($content)
                }
            }
            [IO.File]::WriteAllBytes($destination, $bytes)
        }
    }

    Copy-Template $sourceDir $targetDir
    Copy-Item -LiteralPath (Join-Path $targetDir '.env.example') -Destination (Join-Path $targetDir '.env')
    & git -C $targetDir init --quiet
    if ($LASTEXITCODE -ne 0) {
        throw "git init failed with exit code $LASTEXITCODE"
    }

    @"
Created $displayName at $targetDir

Next steps (PowerShell):
  cd "$targetDir"
  python -m venv env
  .\env\Scripts\Activate.ps1
  pip install -r requirements.txt
  python -m app.cli db:create
  python -m app.cli db:upgrade
  python -m app.cli system:seed
  python -m app.cli spec

In Command Prompt, activate the environment with env\Scripts\activate.bat.
"@
    exit 0
} catch {
    [Console]::Error.WriteLine($_.Exception.Message)
    exit 1
}

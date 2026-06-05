# Configure the current user's PowerShell profile to use UTF-8 console IO.
# Run once from PowerShell:
#   .\tools\setup_powershell_utf8_profile.ps1

$profilePath = $PROFILE
$profileDir = Split-Path -Parent $profilePath

if (-not (Test-Path -LiteralPath $profileDir)) {
    New-Item -ItemType Directory -Force -Path $profileDir | Out-Null
}

if (-not (Test-Path -LiteralPath $profilePath)) {
    New-Item -ItemType File -Force -Path $profilePath | Out-Null
}

$start = '# >>> color_science_toolbox UTF-8 console setup >>>'
$end = '# <<< color_science_toolbox UTF-8 console setup <<<'

$blockLines = @(
    $start,
    'try { chcp 65001 | Out-Null } catch {}',
    '[Console]::InputEncoding = [System.Text.Encoding]::UTF8',
    '[Console]::OutputEncoding = [System.Text.Encoding]::UTF8',
    '$OutputEncoding = [System.Text.Encoding]::UTF8',
    $end
)

$block = $blockLines -join [Environment]::NewLine
$content = Get-Content -LiteralPath $profilePath -Raw -Encoding UTF8
if ($null -eq $content) {
    $content = ''
}

$pattern = [regex]::Escape($start) + '(?s).*?' + [regex]::Escape($end)

if ([regex]::IsMatch($content, $pattern)) {
    $content = [regex]::Replace(
        $content,
        $pattern,
        [System.Text.RegularExpressions.MatchEvaluator]{ param($m) $block }
    )
} elseif ($content.Trim().Length -gt 0) {
    $content = $content.TrimEnd() + [Environment]::NewLine + [Environment]::NewLine + $block + [Environment]::NewLine
} else {
    $content = $block + [Environment]::NewLine
}

Set-Content -LiteralPath $profilePath -Value $content -Encoding UTF8

Write-Output "Updated PowerShell profile: $profilePath"
Write-Output "The UTF-8 setup will apply to new PowerShell sessions."

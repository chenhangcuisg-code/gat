<#
GAT installer (Windows / PowerShell) — wire a game repo to run the Godot Agent Team.

    pwsh -File install.ps1 -Runtime both   -Target C:\path\to\my-game
    pwsh -File install.ps1 -Runtime claude -Target .

The GAT toolkit stays where it is (this repo); the installer just points a game repo at it.
On Windows, skills/agents are COPIED (symlinks need admin/dev-mode).
#>
param(
  [ValidateSet('claude','codex','both')] [string]$Runtime = 'both',
  [Parameter(Mandatory=$true)] [string]$Target
)
$ErrorActionPreference = 'Stop'
$GatHome = Split-Path -Parent $MyInvocation.MyCommand.Path
$Target  = (Resolve-Path $Target).Path
Write-Host "GAT_HOME = $GatHome"
Write-Host "target   = $Target"
Write-Host "runtime  = $Runtime"

function Install-Claude {
  Write-Host "== Claude Code =="
  New-Item -ItemType Directory -Force -Path "$Target\.claude\skills","$Target\.claude\agents" | Out-Null
  Get-ChildItem "$GatHome\skills" -Directory | ForEach-Object {
    $dst = "$Target\.claude\skills\$($_.Name)"
    if (Test-Path $dst) { Remove-Item $dst -Recurse -Force }
    Copy-Item $_.FullName $dst -Recurse -Force
  }
  Copy-Item "$GatHome\agents\*.md" "$Target\.claude\agents\" -Force
  $claudeMd = "$Target\CLAUDE.md"
  $marker = '<!-- gat-rules -->'
  if (-not ((Test-Path $claudeMd) -and (Select-String -Path $claudeMd -SimpleMatch $marker -Quiet))) {
    Add-Content -Path $claudeMd -Encoding utf8 -Value @"

$marker
@$GatHome\runtimes\claude\RULES.md
GAT toolkit: $GatHome  -  workflow: @$GatHome\docs\workflow.md
"@
    Write-Host "  wrote CLAUDE.md include"
  } else { Write-Host "  CLAUDE.md already includes GAT rules" }
}

function Install-Codex {
  Write-Host "== Codex =="
  (Get-Content "$GatHome\runtimes\codex\AGENTS.md.template" -Raw).Replace('{{GAT_HOME}}', $GatHome) |
    Set-Content "$Target\AGENTS.md" -Encoding utf8
  Write-Host "  wrote $Target\AGENTS.md"
  $pdir = if ($env:CODEX_HOME) { "$env:CODEX_HOME\prompts" } else { "$env:USERPROFILE\.codex\prompts" }
  New-Item -ItemType Directory -Force -Path $pdir | Out-Null
  $n = 0
  Get-ChildItem "$GatHome\skills" -Directory | ForEach-Object {
    $name = $_.Name
    @"
Read the GAT skill at ``$GatHome\skills\$name\SKILL.md`` and execute its steps exactly,
following the GAT working rules at ``$GatHome\runtimes\claude\RULES.md``.
Arguments: `$ARGUMENTS
"@ | Set-Content "$pdir\$name.md" -Encoding utf8
    $n++
  }
  Write-Host "  wrote $n prompts to $pdir"
}

# per-project self-evolving journal
New-Item -ItemType Directory -Force -Path "$Target\.gat" | Out-Null
if (-not (Test-Path "$Target\.gat\journal.md")) {
  "# $(Split-Path $Target -Leaf) - GAT project journal`n`n_Per-game memory. Paradigm choices, balance bands, conventions, open questions._" |
    Set-Content "$Target\.gat\journal.md" -Encoding utf8
}
if (-not (Test-Path "$Target\.gat\decisions.md")) {
  "# $(Split-Path $Target -Leaf) - decisions log`n" | Set-Content "$Target\.gat\decisions.md" -Encoding utf8
}

switch ($Runtime) {
  'claude' { Install-Claude }
  'codex'  { Install-Codex }
  'both'   { Install-Claude; Install-Codex }
}
Write-Host "`nDone. Next:  cd $Target  ;  run /gat-workflow-start"

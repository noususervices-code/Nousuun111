<#
.SYNOPSIS
Publish Nousuun.fi static site to GitHub Pages.

.DESCRIPTION
Commits local changes in Website_v4_repo, pushes main to origin, and verifies
that both the custom domain and GitHub Pages URL respond with HTTP 200.

.EXAMPLE
powershell -ExecutionPolicy Bypass -File .\scripts\publish_github_pages.ps1

.EXAMPLE
powershell -ExecutionPolicy Bypass -File .\scripts\publish_github_pages.ps1 -Message "Update events and homepage"

.EXAMPLE
powershell -ExecutionPolicy Bypass -File .\scripts\publish_github_pages.ps1 -SkipCommit
#>

param(
    [string]$RepoPath = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path,
    [string]$Branch = "main",
    [string]$Remote = "origin",
    [string]$Message = "Publish Nousuun.fi update",
    [string[]]$VerifyUrls = @(
        "https://nousuun.fi/",
        "https://noususervices-code.github.io/Nousuun111/"
    ),
    [switch]$SkipCommit,
    [switch]$SkipVerify
)

$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Text)
    Write-Host ""
    Write-Host "==> $Text" -ForegroundColor Cyan
}

function Assert-Command {
    param([string]$Name)
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Required command not found: $Name"
    }
}

function Invoke-Git {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Args)
    & git -C $RepoPath @Args
    if ($LASTEXITCODE -ne 0) {
        throw "Git command failed: git -C `"$RepoPath`" $($Args -join ' ')"
    }
}

Assert-Command "git"

if (-not (Test-Path -LiteralPath (Join-Path $RepoPath ".git"))) {
    throw "RepoPath is not a git repository: $RepoPath"
}

Write-Step "Repository"
Write-Host "Path:   $RepoPath"
Write-Host "Remote: $Remote"
Write-Host "Branch: $Branch"

$currentBranch = (& git -C $RepoPath branch --show-current).Trim()
if ($LASTEXITCODE -ne 0) {
    throw "Could not read current branch."
}

if ($currentBranch -ne $Branch) {
    throw "Current branch is '$currentBranch'. Expected '$Branch'. Switch branches before publishing."
}

Write-Step "Working tree status"
Invoke-Git status --short --branch

if (-not $SkipCommit) {
    $changes = (& git -C $RepoPath status --porcelain)
    if ($LASTEXITCODE -ne 0) {
        throw "Could not read git status."
    }

    if ($changes) {
        Write-Step "Committing changes"
        Invoke-Git add -A
        Invoke-Git commit -m $Message
    }
    else {
        Write-Host "No local changes to commit."
    }
}
else {
    Write-Host "Skipping commit because -SkipCommit was provided."
}

Write-Step "Pushing to GitHub"
Invoke-Git push $Remote $Branch

Write-Step "Post-push status"
Invoke-Git status --short --branch

if (-not $SkipVerify) {
    Write-Step "Waiting briefly for GitHub Pages"
    Start-Sleep -Seconds 12

    Write-Step "Verifying live URLs"
    foreach ($url in $VerifyUrls) {
        try {
            $response = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 25
            $titleMatch = [regex]::Match($response.Content, "<title>(.*?)</title>", "IgnoreCase")
            $title = if ($titleMatch.Success) { $titleMatch.Groups[1].Value } else { "(no title found)" }
            Write-Host "[OK] $url -> $($response.StatusCode) / $title" -ForegroundColor Green
        }
        catch {
            Write-Warning "[CHECK MANUALLY] $url -> $($_.Exception.Message)"
        }
    }
}
else {
    Write-Host "Skipping URL verification because -SkipVerify was provided."
}

Write-Step "Done"
Write-Host "Publish script finished."

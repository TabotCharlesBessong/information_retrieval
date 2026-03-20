param(
    [string]$Owner = "TabotCharlesBessong",
    [string]$Repo = "information_retrieval",
    [string]$Token = $env:GITHUB_TOKEN,
    [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$phaseSettings = @{
    "Phase A" = @{ Color = "1D76DB"; Weeks = "Weeks 1-3" }
    "Phase B" = @{ Color = "0E8A16"; Weeks = "Weeks 3-6" }
    "Phase C" = @{ Color = "FBCA04"; Weeks = "Weeks 6-8" }
    "Phase D" = @{ Color = "D876E3"; Weeks = "Weeks 8-10" }
    "Phase E" = @{ Color = "B60205"; Weeks = "Weeks 10-12" }
    "Phase F" = @{ Color = "5319E7"; Weeks = "Weeks 12-13+" }
}

$issues = @(
    @{ Phase = "Phase A"; Weeks = "Weeks 1-3"; Activity = "Define domain corpus, relevance assumptions, and success criteria." },
    @{ Phase = "Phase A"; Weeks = "Weeks 1-3"; Activity = "Produce architecture baseline: text acquisition, transformation, indexing, interaction, ranking, evaluation." },
    @{ Phase = "Phase A"; Weeks = "Weeks 1-3"; Activity = "Set up development stack: Python, FastAPI, Elasticsearch, PostgreSQL, Docker." },

    @{ Phase = "Phase B"; Weeks = "Weeks 3-6"; Activity = "Implement web/document feed ingestion and crawl-state tracking." },
    @{ Phase = "Phase B"; Weeks = "Weeks 3-6"; Activity = "Add duplicate detection and noise removal." },
    @{ Phase = "Phase B"; Weeks = "Weeks 3-6"; Activity = "Implement parsing, tokenization, stopping, stemming, and n-gram extraction." },
    @{ Phase = "Phase B"; Weeks = "Weeks 3-6"; Activity = "Add text-statistics instrumentation (frequency distribution and vocabulary growth)." },

    @{ Phase = "Phase C"; Weeks = "Weeks 6-8"; Activity = "Build inverted index and query-processing path." },
    @{ Phase = "Phase C"; Weeks = "Weeks 6-8"; Activity = "Implement baseline retrieval models (Boolean and vector-space/BM25)." },
    @{ Phase = "Phase C"; Weeks = "Weeks 6-8"; Activity = "Expose /search API with pagination and snippets." },

    @{ Phase = "Phase D"; Weeks = "Weeks 8-10"; Activity = "Add query transformation, spell suggestions, and refinement." },
    @{ Phase = "Phase D"; Weeks = "Weeks 8-10"; Activity = "Implement phrase queries, filters, and faceting." },
    @{ Phase = "Phase D"; Weeks = "Weeks 8-10"; Activity = "Extend ranking to probabilistic model variant and compare with baseline." },
    @{ Phase = "Phase D"; Weeks = "Weeks 8-10"; Activity = "Build UI features for result snippets and relevance-oriented interaction." },

    @{ Phase = "Phase E"; Weeks = "Weeks 10-12"; Activity = "Build evaluation corpus and relevance judgements." },
    @{ Phase = "Phase E"; Weeks = "Weeks 10-12"; Activity = "Compute effectiveness metrics: Recall, Precision, MAP/NDCG, top-k quality." },
    @{ Phase = "Phase E"; Weeks = "Weeks 10-12"; Activity = "Add efficiency checks: indexing time, latency, throughput." },
    @{ Phase = "Phase E"; Weeks = "Weeks 10-12"; Activity = "Run parameter tuning and significance checks." },

    @{ Phase = "Phase F"; Weeks = "Weeks 12-13+"; Activity = "Implement filtering module (rule-based and profile-aware)." },
    @{ Phase = "Phase F"; Weeks = "Weeks 12-13+"; Activity = "Add recommendation prototype (content-based first, collaborative optional)." },
    @{ Phase = "Phase F"; Weeks = "Weeks 12-13+"; Activity = "Final documentation, revision, and release packaging." }
)

if ($DryRun) {
    Write-Host "DRY RUN: would create $($issues.Count) issues in $Owner/$Repo"
    Write-Host "DRY RUN: would ensure labels: roadmap + Phase A..F"
    Write-Host "DRY RUN: would ensure milestones: one per phase"
    $i = 1
    foreach ($issue in $issues) {
        Write-Host ("[{0}] {1}: {2}" -f $i, $issue.Phase, $issue.Activity)
        $i++
    }
    exit 0
}

if ([string]::IsNullOrWhiteSpace($Token)) {
    $secureToken = Read-Host "Enter GitHub PAT (repo scope)" -AsSecureString
    $bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureToken)
    try {
        $Token = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
    }
    finally {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
    }
}

if ([string]::IsNullOrWhiteSpace($Token)) {
    throw "No GitHub token provided. Set GITHUB_TOKEN or pass -Token <PAT>."
}

$headers = @{
    Accept = "application/vnd.github+json"
    Authorization = "Bearer $Token"
    "X-GitHub-Api-Version" = "2022-11-28"
}

$baseRepoUrl = "https://api.github.com/repos/$Owner/$Repo"
$repoUrl = "$baseRepoUrl/issues"
$created = @()

function Ensure-Label {
    param(
        [string]$Name,
        [string]$Color,
        [string]$Description
    )

    $encodedName = [System.Uri]::EscapeDataString($Name)
    $labelUrl = "$baseRepoUrl/labels/$encodedName"

    try {
        # Update if it exists to keep settings in sync.
        $patchPayload = @{
            new_name = $Name
            color = $Color
            description = $Description
        } | ConvertTo-Json -Depth 5
        Invoke-RestMethod -Method Patch -Uri $labelUrl -Headers $headers -Body $patchPayload | Out-Null
        Write-Host "Label ready: $Name"
        return
    }
    catch {
        $statusCode = $_.Exception.Response.StatusCode.value__
        if ($statusCode -ne 404) {
            throw
        }
    }

    $createLabelPayload = @{
        name = $Name
        color = $Color
        description = $Description
    } | ConvertTo-Json -Depth 5

    Invoke-RestMethod -Method Post -Uri "$baseRepoUrl/labels" -Headers $headers -Body $createLabelPayload | Out-Null
    Write-Host "Label created: $Name"
}

function Get-OrCreate-MilestoneNumber {
    param(
        [string]$Title,
        [string]$Description
    )

    $milestones = Invoke-RestMethod -Method Get -Uri "$baseRepoUrl/milestones?state=all&per_page=100" -Headers $headers
    $existing = $milestones | Where-Object { $_.title -eq $Title } | Select-Object -First 1
    if ($null -ne $existing) {
        Write-Host "Milestone ready: $Title"
        return [int]$existing.number
    }

    $payload = @{
        title = $Title
        description = $Description
    } | ConvertTo-Json -Depth 5

    $createdMilestone = Invoke-RestMethod -Method Post -Uri "$baseRepoUrl/milestones" -Headers $headers -Body $payload
    Write-Host "Milestone created: $Title"
    return [int]$createdMilestone.number
}

# Ensure labels exist first.
Ensure-Label -Name "roadmap" -Color "0052CC" -Description "Roadmap-generated work items"
foreach ($phase in $phaseSettings.Keys) {
    Ensure-Label -Name $phase -Color $phaseSettings[$phase].Color -Description "Roadmap phase"
}

# Ensure one milestone per phase and keep the mapping.
$phaseMilestones = @{}
foreach ($phase in $phaseSettings.Keys) {
    $milestoneTitle = "$phase ($($phaseSettings[$phase].Weeks))"
    $milestoneDescription = "Roadmap phase milestone for $phase covering $($phaseSettings[$phase].Weeks)."
    $phaseMilestones[$phase] = Get-OrCreate-MilestoneNumber -Title $milestoneTitle -Description $milestoneDescription
}

# Pull existing issue titles once to avoid duplicates on rerun.
$existingIssueTitles = @{}
$existingIssues = Invoke-RestMethod -Method Get -Uri "$repoUrl?state=all&per_page=100" -Headers $headers
foreach ($item in $existingIssues) {
    if ($null -eq $item.pull_request) {
        $existingIssueTitles[$item.title] = $true
    }
}

foreach ($issue in $issues) {
    $title = "[$($issue.Phase)] $($issue.Activity)"
    if ($existingIssueTitles.ContainsKey($title)) {
        Write-Host "Skipped (already exists): $title"
        continue
    }

    $body = @"
Roadmap source: roadmap.md

Phase: $($issue.Phase)
Target window: $($issue.Weeks)

Key activity:
- $($issue.Activity)

Definition of done:
- [ ] Implementation complete
- [ ] Tests added/updated
- [ ] Documentation updated
"@

    $payload = @{
        title = $title
        body = $body
        labels = @("roadmap", $issue.Phase)
        milestone = $phaseMilestones[$issue.Phase]
    } | ConvertTo-Json -Depth 5

    $response = Invoke-RestMethod -Method Post -Uri $repoUrl -Headers $headers -Body $payload
    $created += $response.html_url
    $existingIssueTitles[$title] = $true
    Write-Host "Created: $($response.html_url)"
}

Write-Host "Done. Created $($created.Count) issues."

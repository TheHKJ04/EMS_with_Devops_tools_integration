
param(
    [switch]$Apply
)

$ErrorActionPreference = "Stop"

# ---------------------------------------------------------
# EMS Kubernetes Manifest Hardening
# Default: Preview only
# -Apply: Create backups and modify the YAML files
# ---------------------------------------------------------

$ProjectRoot = (Get-Location).Path
$DatabaseFile = Join-Path $ProjectRoot "k8s\01-database.yaml"
$MigrationFile = Join-Path $ProjectRoot "k8s\02-migration.yaml"
$BackupDirectory = Join-Path $ProjectRoot "k8s\backup-before-hardening"

Write-Host "`n=== EMS Kubernetes Hardening ===" -ForegroundColor Cyan
Write-Host "Project: $ProjectRoot"

# 1. Check project files
foreach ($File in @($DatabaseFile, $MigrationFile)) {
    if (-not (Test-Path $File)) {
        throw "Required file not found: $File"
    }
}

# 2. Read original contents
$DatabaseOriginal = [System.IO.File]::ReadAllText($DatabaseFile)
$MigrationOriginal = [System.IO.File]::ReadAllText($MigrationFile)

$Database = $DatabaseOriginal
$Migration = $MigrationOriginal

# Helper: replace exactly one occurrence, or skip
# if the desired replacement is already present.

function Replace-Once {
    param(
        [string]$Content,
        [string]$Old,
        [string]$New,
        [string]$Description
    )

    # Normalise line endings so LF and CRLF files both work.
    $Content = $Content -replace "`r?`n", "`r`n"
    $Old = $Old -replace "`r?`n", "`r`n"
    $New = $New -replace "`r?`n", "`r`n"

    if ($Content.Contains($New)) {
        Write-Host "[Already applied] $Description" -ForegroundColor DarkGray
        return $Content
    }

    $Count = ([regex]::Matches(
        $Content,
        [regex]::Escape($Old)
    )).Count

    if ($Count -ne 1) {
        throw "Expected exactly one match for '$Description'; found $Count. No files have been written."
    }

    Write-Host "[Planned] $Description" -ForegroundColor Green

    return $Content.Replace($Old, $New)
}

# =========================================================
# A. MYSQL DATABASE MANIFEST
# =========================================================

# Add pod-level security configuration.
$Database = Replace-Once `
    $Database `
    "    spec:`r`n      containers:`r`n        - name: mysql" `
    "    spec:`r`n      automountServiceAccountToken: false`r`n      securityContext:`r`n        seccompProfile:`r`n          type: RuntimeDefault`r`n      containers:`r`n        - name: mysql" `
    "MySQL pod security settings"

# Add container privilege-escalation restriction.
$Database = Replace-Once `
    $Database `
    "          imagePullPolicy: IfNotPresent`r`n          ports:" `
    "          imagePullPolicy: IfNotPresent`r`n          securityContext:`r`n            allowPrivilegeEscalation: false`r`n          ports:" `
    "MySQL container security settings"

# Improve startup probe.
$OldStartupProbe = @'
          startupProbe:
            exec:
              command:
                - sh
                - -c
                - 'mysqladmin ping -h 127.0.0.1 -uroot -p"$MYSQL_ROOT_PASSWORD" --silent'
            periodSeconds: 10
            failureThreshold: 30
'@

$NewStartupProbe = @'
          startupProbe:
            exec:
              command:
                - sh
                - -c
                - 'mysqladmin ping -h 127.0.0.1 --silent'
            periodSeconds: 10
            timeoutSeconds: 5
            failureThreshold: 30
'@

$Database = Replace-Once `
    $Database `
    $OldStartupProbe `
    $NewStartupProbe `
    "MySQL startup probe"

# Improve readiness probe.
$OldReadinessProbe = @'
          readinessProbe:
            exec:
              command:
                - sh
                - -c
                - 'mysqladmin ping -h 127.0.0.1 -uroot -p"$MYSQL_ROOT_PASSWORD" --silent'
            periodSeconds: 10
            timeoutSeconds: 5
            failureThreshold: 6
'@

$NewReadinessProbe = @'
          readinessProbe:
            exec:
              command:
                - sh
                - -c
                - 'mysqladmin ping -h 127.0.0.1 --silent'
            periodSeconds: 10
            timeoutSeconds: 5
            failureThreshold: 6
'@

$Database = Replace-Once `
    $Database `
    $OldReadinessProbe `
    $NewReadinessProbe `
    "MySQL readiness probe"

# =========================================================
# B. DATABASE MIGRATION JOB
# =========================================================

# Pod-level non-root identity and security configuration.
$Migration = Replace-Once `
    $Migration `
    "      restartPolicy: Never`r`n      containers:" `
    "      restartPolicy: Never`r`n      automountServiceAccountToken: false`r`n      securityContext:`r`n        runAsNonRoot: true`r`n        runAsUser: 100`r`n        runAsGroup: 101`r`n        seccompProfile:`r`n          type: RuntimeDefault`r`n      containers:" `
    "Migration pod security settings"

# Container-level restrictions.
$Migration = Replace-Once `
    $Migration `
    "          imagePullPolicy: IfNotPresent`r`n          command:" `
    "          imagePullPolicy: IfNotPresent`r`n          securityContext:`r`n            allowPrivilegeEscalation: false`r`n            readOnlyRootFilesystem: true`r`n            capabilities:`r`n              drop:`r`n                - ALL`r`n          command:" `
    "Migration container security settings"

# Writable temporary directory.
$Migration = Replace-Once `
    $Migration `
    "          envFrom:" `
    "          volumeMounts:`r`n            - name: migration-tmp`r`n              mountPath: /tmp`r`n          envFrom:" `
    "Migration temporary volume mount"



# Add pod-level emptyDir volume.

# This is the actual pod-level volume definition.
$MigrationVolume = @'

      volumes:
        - name: migration-tmp
          emptyDir:
            sizeLimit: 64Mi
'@

# Check specifically for the pod-level volume.
$VolumeDefinitionPattern = '(?ms)^      volumes:\s+- name:\s*migration-tmp\s+emptyDir:\s+sizeLimit:\s*64Mi\s*$'

if ($Migration -match '(?m)^      volumes:\s*$') {

    if ($Migration -match $VolumeDefinitionPattern) {
        Write-Host "[Already applied] Migration temporary volume" -ForegroundColor DarkGray
    }
    else {
        throw "A pod-level volumes section exists but migration-tmp is not correctly configured. Manual review required."
    }

}
else {

    $Migration = $Migration.TrimEnd() + $MigrationVolume

    Write-Host "[Planned] Migration temporary volume" -ForegroundColor Green
}

# =========================================================
# C. BASIC POST-EDIT VALIDATION
# =========================================================

$Checks = @(
    @{
        Name = "MySQL service account token disabled"
        Content = $Database
        Pattern = 'automountServiceAccountToken:\s*false'
    },
    @{
        Name = "MySQL seccomp profile"
        Content = $Database
        Pattern = 'type:\s*RuntimeDefault'
    },
    @{
        Name = "MySQL startup probe timeout"
        Content = $Database
        Pattern = 'startupProbe:[\s\S]*?timeoutSeconds:\s*5'
    },
    @{
        Name = "MySQL password-free ping"
        Content = $Database
        Pattern = 'mysqladmin ping -h 127\.0\.0\.1 --silent'
    },
    @{
        Name = "Migration non-root identity"
        Content = $Migration
        Pattern = 'runAsUser:\s*100'
    },
    @{
        Name = "Migration read-only root filesystem"
        Content = $Migration
        Pattern = 'readOnlyRootFilesystem:\s*true'
    },
    @{
        Name = "Migration privilege escalation disabled"
        Content = $Migration
        Pattern = 'allowPrivilegeEscalation:\s*false'
    },
    @{
        Name = "Migration writable temporary volume"
        Content = $Migration
        Pattern = 'mountPath:\s*/tmp'
    },
    @{
    Name = "Migration temporary volume definition"
    Content = $Migration
    Pattern = '(?ms)^      volumes:\s+- name:\s*migration-tmp\s+emptyDir:\s+sizeLimit:\s*64Mi\s*$'
}
)

foreach ($Check in $Checks) {
    if ($Check.Content -notmatch $Check.Pattern) {
        throw "Validation failed: $($Check.Name). No files have been written."
    }

    Write-Host "[PASS] $($Check.Name)" -ForegroundColor Green
}

# =========================================================
# D. PREVIEW OR APPLY
# =========================================================

if (-not $Apply) {
    Write-Host "`nPREVIEW ONLY: No files were changed." -ForegroundColor Yellow
    Write-Host "Review the proposed changes with:"
    Write-Host "  git diff -- k8s/01-database.yaml k8s/02-migration.yaml"
    Write-Host "`nTo apply, run:"
    Write-Host "  .\scripts\harden-kubernetes-manifests.ps1 -Apply"
    return
}

# Refuse to overwrite an existing backup directory.
if (Test-Path $BackupDirectory) {
    throw "Backup directory already exists: $BackupDirectory. Choose a new backup directory before applying."
}

# Create backups before writing.
New-Item -ItemType Directory -Path $BackupDirectory | Out-Null

Copy-Item $DatabaseFile $BackupDirectory
Copy-Item $MigrationFile $BackupDirectory

try {
    # Write using UTF-8 without BOM.
    $Utf8NoBom = New-Object System.Text.UTF8Encoding($false)

    [System.IO.File]::WriteAllText(
        $DatabaseFile,
        $Database,
        $Utf8NoBom
    )

    [System.IO.File]::WriteAllText(
        $MigrationFile,
        $Migration,
        $Utf8NoBom
    )
}
catch {
    Write-Warning "Write failed. Restoring original manifests from backup."

    Copy-Item (Join-Path $BackupDirectory "01-database.yaml") $DatabaseFile -Force
    Copy-Item (Join-Path $BackupDirectory "02-migration.yaml") $MigrationFile -Force

    throw
}

Write-Host "`nSUCCESS: Manifest changes written." -ForegroundColor Green
Write-Host "Backups: $BackupDirectory"

Write-Host "`nModified files:"
Write-Host "  k8s/01-database.yaml"
Write-Host "  k8s/02-migration.yaml"

Write-Host "`nNo Kubernetes resources were applied or restarted." -ForegroundColor Yellow

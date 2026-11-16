#Requires -Version 5.1
[CmdletBinding()]
param(
    [string]$Root = 'D:\WORK\RESEARCH\TokenToModel-Lab',
    [string]$Zip = ''
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$branch = 'docs/learningbooks-dive-into-llms-vi-20261116'
$minimumBase = '740f331ff7e354edca0a69fa11f2afca965c3bf4'
$expectedZip = '73b10765deb7e932e6e8a16ca1f96709b8a6f9149d6c803937ed0417bfc1788e'
$subpath = 'docs/learningbooks/dive-into-llms/PDF11_VI'
if (-not $Zip) {
  $Zip = Join-Path $Root '_tmp\learningbooks\dive-into-llms-11pdfs-VI-bilingual-20261116.zip'
}
$Root=[IO.Path]::GetFullPath($Root).TrimEnd('\')
$gitRoot=(& git -C $Root rev-parse --show-toplevel)
if ($LASTEXITCODE -ne 0) { throw 'ROOT_IS_NOT_GIT' }
if (-not [string]::Equals(([IO.Path]::GetFullPath($gitRoot.Trim()).TrimEnd('\')), $Root, [StringComparison]::OrdinalIgnoreCase)) {
  throw 'REPO_ROOT_MISMATCH'
}
$origin = (& git -C $Root remote get-url origin)
if ($LASTEXITCODE -ne 0 -or $origin -notmatch '(?i)github\.com[:/]minhtri22/TokenToModel-Lab(\.git)?$') {
  throw 'GITHUB_ORIGIN_MISMATCH'
}
if (-not (Test-Path -LiteralPath $Zip -PathType Leaf)) {
  throw ('ZIP_NOT_FOUND: '+$Zip)
}
$gotZip = (Get-FileHash -LiteralPath $Zip -Algorithm SHA256).Hash.ToLowerInvariant()
if ($gotZip -ne $expectedZip) { throw ('WRONG_BINARY_ZIP_SHA256: '+$gotZip) }
Add-Type -AssemblyName System.IO.Compression.FileSystem
$wanted=@('README_VI.md','TRANSLATION_MANIFEST.json')
for($n=1;$n -le 11;$n++) {
  $c=('{0:D2}' -f $n)
  $wanted+=('chapter'+$c+'_VI_bilingual.pdf')
  $wanted+=('GHI_CHU_TIENg_VIET/chapter'+$c+'_VI_by_slide.md')
}
$archive=[IO.Compression.ZipFile]::OpenRead($Zip)
try {
  $names=@($archive.Entries | Where-Object { $_.Name -ne '' } | ForEach-Object { $_.FullName.Replace('\','/') })
  if ($names.Count -ne 24) { throw ('ZIP_ENTRY_COUNT_MISMATCH: '+$names.Count) }
  foreach($name in $names) { if (-not ($wanted -ccontains $name)) { throw ('UNEXPECTED_ZIP_PATH: '+$name) } }
  foreach($name in $wanted) { if (-not ($names -ccontains $name)) { throw ('ZIP_PATH_MISSING: '+$name) } }
} finally { $archive.Dispose() }
$stage=Join-Path $Root '_tmp\learningbooks\pdf11-vi-stage-20261116'
$worktree=Join-Path $Root '_tmp\learningbooks\wt-pdf11-vi-20261116'
if ((Test-Path -LiteralPath $stage) -or (Test-Path -LiteralPath $worktree)) {
  throw 'STAGE_OR_WORKTREE_ALREADY_EXISTS_NO_OVERWRITE'
}
Expand-Archive -LiteralPath $Zip -DestinationPath $stage
$manifestPath=Join-Path $stage 'TRANSLATION_MANIFEST.json'
$manifest=Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
if ($manifest.source_upstream_git_commit -ne 'f84c04268794ef94f8949808bbc14ab8636763a0' -or $manifest.papers.Count -ne 11) {
  throw 'PIN_OR_PAPER_COUNT_MISMATCH'
}
foreach($item in $manifest.papers) {
  $expectedFiles=@(
    @([string]$item.bilingual_pdf_path,[string]$item.bilingual_pdf_sha256),
    @([string]$item.editable_vi_notes_path,[string]$item.editable_vi_notes_sha256)
  )
  foreach($pair in $expectedFiles) {
    $path=Join-Path $stage ($pair[0].Replace('/','\'))
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw ('MISSING_SOURCE_ASSET: '+$path) }
    $hash=(Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($hash -ne $pair[1]) { throw ('ASSET_SHA256_MISMATCH: '+$path) }
  }
}
& git -C $Root fetch origin ('refs/heads/'+$branch+':refs/remotes/origin/'+$branch)
if ($LASTEXITCODE -ne 0) { throw 'FETCH_FAILED' }
$remoteHead=(& git -C $Root rev-parse ('refs/remotes/origin/'+$branch))
if ($LASTEXITCODE -ne 0) { throw 'REMOTE_HEAD_LOOKUP_FAILED' }
& git -C $Root merge-base --is-ancestor $minimumBase $remoteHead
if ($LASTEXITCODE -ne 0) { throw ('UNRELATED_BRANCH_HEAD: '+$remoteHead) }
& git -C $Root worktree add --detach -- $worktree $remoteHead
if ($LASTEXITCODE -ne 0) { throw 'CREATE_WORKTREE_FAILED' }
$target=Join-Path $worktree ($subpath.Replace('/','\'))
if (-not (Test-Path -LiteralPath $target)) { throw 'DOCS_DESTINATION_MISSING' }
Copy-Item -LiteralPath (Join-Path $stage 'README_VI.md') -Destination (Join-Path $target 'PACKAGE_README_VI.md')
Copy-Item -LiteralPath $manifestPath -Destination (Join-Path $target 'TRANSLATION_MANIFEST.json')
foreach($item in $manifest.papers) {
  foreach($name in @([string]$item.bilingual_pdf_path,[string]$item.editable_vi_notes_path)) {
    $src=Join-Path $stage ($name.Replace('/','\'))
    $dst=Join-Path $target ($name.Replace('/','\'))
    $dstDir=Split-Path -Parent $dst
    if (-not (Test-Path -LiteralPath $dstDir)) { New-Item -ItemType Directory -Path $dstDir -Force | Out-Null }
    if (Test-Path -LiteralPath $dst) { throw ('DESTINATION_ALREADY_EXISTS: '+$dst) }
    Copy-Item -LiteralPath $src -Destination $dst
  }
}
& git -C $worktree -c core.autocrlf=false add -- $subpath
if ($LASTEXITCODE -ne 0) { throw 'GIT_ADD_FAILED' }
$staged=@(& git -C $worktree diff --cached --name-only)
if ($staged.Count -ne 24) { throw ('STAGED_COUNT_NOT_24: '+$staged.Count) }
foreach($path in $staged) {
  if (-not $path.StartsWith($subpath+'/')) { throw ('UNEXPECTED_STAGED_PATH: '+$path) }
}
& git -C $worktree -c commit.gpgsign=false commit -m 'docs(learningbooks): add 11 source-pinned bilingual PDFs and slide notes as HOLD candidates'
if ($LASTEXITCODE -ne 0) { throw 'GIT_COMMIT_FAILED' }
$head=(& git -C $worktree rev-parse HEAD)
& git -C $worktree push origin ('HEAD:refs/heads/'+$branch)
if ($LASTEXITCODE -ne 0) { throw 'GIT_PUSH_FAILED_OR_BRANCH_MOVED' }
Write-Output 'PDF11_BINARY_PUSH=PASS'
Write-Output ('COMMIT='+$head)
Write-Output 'PDF_COUNT=11'
Write-Output 'EDITABLE_VI_MD_COUNT=11'
Write-Output 'PACKAGE_METADATA_COUNT=2'
Write-Output 'FIDELITY_STATUS=HOLD_FIDELITY_PENDING_REMEDIATION'
Write-Output 'NO_MAIN_MERGE=TRUE; NO_SCIENCE=TRUE; NO_LINEAGE_CHANGE=TRUE'

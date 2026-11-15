#requires -Version 5.1
<#
TTM VM V4 R8 G2 — bounded exact venv wheel RECORD integrity diagnostic.
READ ONLY. No installation, environment mutation, key access, private receipt
content publication, GitHub write, G_pre, G3, or case generation.
Only the verified R8_G2_EXACT venv; no fallback to another Python.
#>
[CmdletBinding()]
param([string]$ProjectRoot='D:\WORK\RESEARCH\TokenToModel-Lab')
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$Root=[IO.Path]::GetFullPath($ProjectRoot).TrimEnd('\')
$Receipt=Join-Path $Root '_private\r8_custody\receipts\g2-owner-windows-protected-trust-boundary-preexec-20261115.json'
$ReceiptSHA='c0bf90955d09501b5dcdb7ab912635a666895b23c5c855494ddfb7381ce37795'
$ExeSHA='0b471133e110cfb53a061cad528ce8e517d7b9ac41a0a396c39ad795a487fc14'
$Venv=Join-Path $Root '_tmp\TTM_VM_R8_G2_EXACT_RUNTIME_20261115\venv'
$Python=Join-Path $Venv 'Scripts\python.exe'
$Source=Join-Path $Root '_private\r8_custody\source'
$SourceHashes=[ordered]@{
 'folds_raters.py'='02626f9f0def5af90b57c2930898e96dbc8f6206c441bb4aaa4c4278ce0dddae'
 'r8_production_caller.py'='3a9b249bced1b4ceaa5746d63367c017410ef82ded21ef386c3be2b1ee76b206'
 'test_g0_algorithm_version_binding.py'='2ce86fe549e1625790fcab72c076df2f12d648b048a350570d5c97a026431ae2'
 'gold_contract.py'='8e8b81ce2d0bc47cc60c29abc7156fe9d97613e67983e43b7f587615d68015a5'
 'restricted_oracles.py'='34ab74d36b822703e4d8cbdf281e142273d55d181243d904b55fd31a0e6382a1'
}
function Get-ReadOnlyHash([string]$File){
  $Item=Get-Item -LiteralPath $File -Force -ErrorAction Stop
  if($Item.PSIsContainer -or (($Item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0)){
    throw 'HASH_TARGET_NOT_NORMAL_FILE_OR_REPARSE'
  }
  return (Get-FileHash -LiteralPath $File -Algorithm SHA256 -ErrorAction Stop).Hash.ToLowerInvariant()
}
if((Get-ReadOnlyHash $Receipt) -cne $ReceiptSHA){throw 'ORIGINAL_G2_RECEIPT_MISMATCH'}
Write-Host 'ORIGINAL_G2_RECEIPT=PASS_SHA256_UNCHANGED'
if((Get-ReadOnlyHash $Python) -cne $ExeSHA){throw 'R8_G2_EXACT_PYTHON_EXE_HASH_MISMATCH'}
Write-Host 'R8_G2_EXACT_EXE=PASS_SHA256_HISTORICAL_PIN'
$C=0
foreach($Entry in $SourceHashes.GetEnumerator()){
  $Path=Join-Path $Source $Entry.Key
  if((Get-ReadOnlyHash $Path) -cne $Entry.Value){throw 'FROZEN_SOURCE_HASH_MISMATCH'}
  $C++
}
if($C -ne 5){throw 'FROZEN_SOURCE_COUNT_INVALID'}
Write-Host 'FROZEN_SOURCE_5_OF_5=PASS_READONLY_SHA256'

$Code=@'
import base64, hashlib, hmac, importlib.metadata as m, json, pathlib, sys

EXPECTED = {
    'numpy':'2.3.5', 'scipy':'1.17.0', 'scikit-learn':'1.8.0',
    'joblib':'1.5.3', 'threadpoolctl':'3.6.0'
}
def inside(p, root):
    try:
        p.relative_to(root)
        return True
    except ValueError:
        return False

result={
 'python_version':'.'.join(map(str,sys.version_info[:3])),
 'sys_prefix_match':False,
 'versions_match':True,
 'versions':{},
 'wheel_record_has_hash':0,
 'wheel_record_missing':0,
 'wheel_record_mismatch':0,
 'wheel_record_outside_prefix':0,
 'wheel_record_symlinks':0,
 'wheel_record_unsupported_hash':0,
 'wheel_record_unhashed':0,
 'native_extension_records_verified':0,
 'all_record_hashes_verified':False
}
expected_root=pathlib.Path(sys.argv[1]).resolve(strict=True)
prefix=pathlib.Path(sys.prefix).resolve(strict=True)
result['sys_prefix_match']=(prefix==expected_root)
if not result['sys_prefix_match']:
    result['status']='HOLD_PREFIX_MISMATCH'
    print(json.dumps(result,sort_keys=True))
    sys.exit(0)

for package, expected_version in EXPECTED.items():
    try:
        dist=m.distribution(package)
    except m.PackageNotFoundError:
        result['versions'][package]='NOT_INSTALLED'
        result['versions_match']=False
        continue
    actual=dist.version
    result['versions'][package]=actual
    if actual != expected_version:
        result['versions_match']=False
    files=dist.files
    if files is None:
        result['wheel_record_missing']+=1
        continue
    for entry in files:
        try:
            path=pathlib.Path(dist.locate_file(entry))
            if path.is_symlink():
                result['wheel_record_symlinks']+=1
                continue
            resolved=path.resolve(strict=False)
            if not inside(resolved,prefix):
                result['wheel_record_outside_prefix']+=1
                continue
            if not resolved.is_file():
                result['wheel_record_missing']+=1
                continue
            if entry.hash is None:
                result['wheel_record_unhashed']+=1
                continue
            if entry.hash.mode!='sha256':
                result['wheel_record_unsupported_hash']+=1
                continue
            expected=base64.urlsafe_b64decode(entry.hash.value+'='*(-len(entry.hash.value)%4))
            actual_hash=hashlib.sha256(resolved.read_bytes()).digest()
            if not hmac.compare_digest(actual_hash,expected):
                result['wheel_record_mismatch']+=1
                continue
            result['wheel_record_has_hash']+=1
            if resolved.suffix.lower()=='.pyd':
                result['native_extension_records_verified']+=1
        except (OSError, ValueError, TypeError):
            result['wheel_record_mismatch']+=1

result['all_record_hashes_verified']=(
    result['python_version']=='3.12.10'
    and result['sys_prefix_match']
    and result['versions_match']
    and result['wheel_record_has_hash']>0
    and all(result[k]==0 for k in (
      'wheel_record_missing','wheel_record_mismatch','wheel_record_outside_prefix',
      'wheel_record_symlinks','wheel_record_unsupported_hash'))
)
result['status']=(
 'PASS_SCOPED_INSTALLED_RECORD_BYTES'
 if result['all_record_hashes_verified']
 else 'HOLD_RUNTIME_RECORD_OR_VERSION')
print(json.dumps(result,sort_keys=True))
'@
$Prior=$ErrorActionPreference
$Output=@()
$Exit=$null
try{
  $ErrorActionPreference='Continue'
  $Output=@(& $Python -I -B -c $Code $Venv 2>&1)
  $Exit=$LASTEXITCODE
} finally {
  $ErrorActionPreference=$Prior
}
if($Exit -ne 0){
  Write-Host 'R8_G2_RUNTIME_RECORD=HOLD_PYTHON_PROCESS_NONZERO'
} else {
  $Lines=@($Output | Where-Object {$_ -is [string]} |
    ForEach-Object {$_.Trim()} |
    Where-Object {$_.StartsWith('{') -and $_.EndsWith('}')})
  if($Lines.Count -ne 1){
    Write-Host 'R8_G2_RUNTIME_RECORD=HOLD_UNEXPECTED_PYTHON_OUTPUT'
  }else{
    try{
      $Data=$Lines[0] | ConvertFrom-Json -ErrorAction Stop
      Write-Host ('R8_G2_RUNTIME_RECORD=' + $Data.status)
      Write-Host ('R8_G2_PYTHON_VERSION=' + $Data.python_version)
      Write-Host ('R8_G2_PREFIX_MATCH=' + $Data.sys_prefix_match)
      Write-Host ('R8_G2_VERSION_MATCH=' + $Data.versions_match)
      Write-Host ('R8_G2_RECORD_HASHED_COUNT=' + $Data.wheel_record_has_hash)
      Write-Host ('R8_G2_RECORD_MISSING=' + $Data.wheel_record_missing)
      Write-Host ('R8_G2_RECORD_HASH_MISMATCH=' + $Data.wheel_record_mismatch)
      Write-Host ('R8_G2_RECORD_OUTSIDE_PREFIX=' + $Data.wheel_record_outside_prefix)
      Write-Host ('R8_G2_RECORD_REPARSE=' + $Data.wheel_record_symlinks)
      Write-Host ('R8_G2_RECORD_UNSUPPORTED_HASH=' + $Data.wheel_record_unsupported_hash)
      Write-Host ('R8_G2_RECORD_UNHASHED=' + $Data.wheel_record_unhashed)
      Write-Host ('R8_G2_NATIVE_EXTENSION_RECORDS_VERIFIED=' + $Data.native_extension_records_verified)
      if($Data.wheel_record_has_hash -eq 3636 -and $Data.status -eq 'PASS_SCOPED_INSTALLED_RECORD_BYTES'){
        Write-Host 'R8_G2_HISTORICAL_RECORD_COUNT=PASS_SCOPED_COUNT_3636'
      }else{
        Write-Host 'R8_G2_HISTORICAL_RECORD_COUNT=NOT_ATTESTED_OR_COUNT_DIFFERS'
      }
    }catch{
      Write-Host 'R8_G2_RUNTIME_RECORD=HOLD_JSON_DIAGNOSTIC'
    }
  }
}
$After=(Get-ReadOnlyHash $Receipt)
if($After -cne $ReceiptSHA){throw 'ORIGINAL_G2_RECEIPT_MUTATED_DURING_READBACK'}
Write-Host 'ORIGINAL_G2_RECEIPT_AFTER=PASS_SHA256_UNCHANGED'
Write-Host 'ORIGINAL_RUNTIME_MANIFEST_EXACT_SHA=NOT_ATTESTED'
Write-Host 'ACTUAL_LOADED_NATIVE_MODULE_SHA=NOT_ATTESTED'
Write-Host 'HMAC_V2_KEY_READ=NOT_EXECUTED'
Write-Host 'R8=NOT_GENERATED'
Write-Host 'G3=NOT_EXECUTED'
Write-Host 'G2=HOLD_INTEGRATED'

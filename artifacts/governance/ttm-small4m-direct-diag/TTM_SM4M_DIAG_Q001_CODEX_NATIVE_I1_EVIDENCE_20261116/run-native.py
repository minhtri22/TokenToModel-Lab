import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import sys

root = Path.cwd()
src = root / "tools/pilot_t4/direct_failure_diag_q001/preexec_candidate_20261116"
evidence = root / "_tmp/codex-i1-evidence"
out = evidence / sys.argv[1]
out.mkdir()
ps51 = Path(os.environ["SystemRoot"]) / "System32/WindowsPowerShell/v1.0/powershell.exe"
shell = [str(ps51), "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass"]
v4 = json.loads((evidence / "preflight.json").read_text(encoding="utf-8-sig"))
pins = {Path(file["path"]).name: file["sha256"] for file in v4["files"]}
tested = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
          for p in src.iterdir() if p.suffix in (".ps1", ".py")}
if sys.argv[1] == "baseline":
    assert all(pins[name] == value for name, value in tested.items())
pins.update(tested)
env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
commands = {}
def capture(name, cmd, *, cwd=root):
    try:
        result = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, timeout=45)
        stdout, stderr, code = result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired as error:
        stdout, stderr, code = error.stdout or b"", error.stderr or b"", "TIMEOUT"
    (out / (name + ".stdout.txt")).write_bytes(stdout)
    (out / (name + ".stderr.txt")).write_bytes(stderr)
    commands[name] = {"argv": cmd, "exit_code": code}
    return code

ps_parser = r"""
$rows=@(Get-ChildItem -File -Filter *.ps1 | ForEach-Object {
 $tokens=$null; $errors=$null
 $ast=[System.Management.Automation.Language.Parser]::ParseFile($_.FullName,[ref]$tokens,[ref]$errors)
 [ordered]@{file=$_.Name;errors=@($errors|ForEach-Object { [ordered]@{line=$_.Extent.StartLineNumber;error_id=$_.ErrorId;message=$_.Message} })}
})
[ordered]@{computer=[Environment]::MachineName;os=[Environment]::OSVersion.VersionString;is64bit=[Environment]::Is64BitProcess;ps=$PSVersionTable.PSVersion.ToString();scripts=$rows} | ConvertTo-Json -Depth 8
if (@($rows|Where-Object {$_.errors.Count}).Count) { exit 2 }
"""
capture("parser", shell + ["-Command", ps_parser], cwd=src)
capture("source-qa", [sys.executable, str(src / "ttm_sm4m_diag_q001.py"), "source-qa"])
capture("author-negative", [sys.executable, str(src / "independent_negative_qa_v3.py")])
watchdog = "Watch-TTM-SM4M-ProcessTree-PS51.ps1"
native = "Invoke-DIAG-Q001-Watchdog-NativeNegativeQA-PS51.ps1"
capture("onepack", shell + ["-File", str(src / "Invoke-DIAG-Q001-I1-NativeSourceOnePack-PS51.ps1"),
    "-ProjectRoot", str(root), "-ExpectedRunnerSHA256", pins["ttm_sm4m_diag_q001.py"],
    "-ExpectedLauncherSHA256", pins["Run-Approved-OneShot-PS51.ps1"],
    "-ExpectedWatchdogSHA256", pins[watchdog],
    "-ExpectedNegativeQaSHA256", pins["independent_negative_qa_v3.py"], "-ExpectedNativeWatchQaSHA256", pins[native]])
capture("watchdog", shell + ["-File", str(src / native), "-ProjectRoot", str(root),
                            "-ExpectedWatchdogSHA256", pins[watchdog]])
assert sys.version_info[:2] == (3, 12)
(out / "commands.json").write_text(json.dumps({
    "driver_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    "python_exe": sys.executable, "python_version": sys.version,
    "python_exe_sha256": hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest(),
    "python_bits": struct.calcsize("P")*8,
    "ps51_exe_sha256": hashlib.sha256(ps51.read_bytes()).hexdigest(),
    "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
    "source_hashes": tested, "commands": commands}, indent=2) + "\n", encoding="utf-8")

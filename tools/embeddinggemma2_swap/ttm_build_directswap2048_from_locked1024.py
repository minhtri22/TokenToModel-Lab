#!/usr/bin/env python3
"""Recreate SHA256-frozen GPU2048 source from an immutable GPU1024 source archive.

Infrastructure only; never executes training, reads datasets or contacts a GPU.
No source file may be silently overwritten. New experiment is a separate run ID.
"""
from __future__ import annotations
import argparse
import hashlib
import io
from pathlib import Path
import py_compile
import urllib.request
import zipfile

SRC_COMMIT = 'a22a7d3913b049b93006efa9475ca574ab2877a9'
OLD_BUNDLE = 'TTM_GEMMA2_DIRECTSWAP_GPU1024_SOURCE_20261109.zip'
OLD_BUNDLE_SHA256 = 'e544c645635a28fe140802421d03a7928a7f0446d2df33bbfe4ec129e3a6ea27'
OLD_RUNNER_SHA256 = '00416c0ff5b2afdcca2780a20315dd2da0af93554cd2b32b6c94efb630dc5d3b'
NEW_RUNNER_SHA256 = '0994f0cd91cb504f2db8478f55963813a85469807f2921e38c196248f323759e'
SOURCE_PINS = {
    'p02_exact.py': 'e0fcac285918b66b13c8f694e6d625a0691c9b59221b43043e63f46b25ddcc07',
    'ttm_embeddinggemma2_swap.py': 'd11da61e9d7bb040f3263e680f026817a513553c186ab243e184ffaf6e68cd39',
    'ttm_directswap1024_gpu_once.py': OLD_RUNNER_SHA256,
}
NEW_RUN_ID = 'ttm_small4m_gemma2_directswap_2048x4096_t4_gpu_20261109_v1'
NEW_PREREG = 'd942c32ed3da053a57e8ff22b1bc00d412a88ea7'


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def exact_replace(text: str, old: str, new: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError('SOURCE_PATCH_NOT_EXACTLY_ONCE:' + old[:55] + f':count={n}')
    return text.replace(old, new)


def produce(bundle: bytes, destination: Path) -> str:
    if sha256(bundle) != OLD_BUNDLE_SHA256:
        raise RuntimeError('STOP_SOURCE_BUNDLE_SHA256_MISMATCH')
    with zipfile.ZipFile(io.BytesIO(bundle)) as archive:
        if set(archive.namelist()) != set(SOURCE_PINS):
            raise RuntimeError('STOP_SOURCE_BUNDLE_ENTRY_SET_CHANGED')
        entries = {name: archive.read(name) for name in SOURCE_PINS}
    for name, expected in SOURCE_PINS.items():
        if sha256(entries[name]) != expected:
            raise RuntimeError('STOP_SOURCE_ENTRY_SHA256:' + name)
    s = entries['ttm_directswap1024_gpu_once.py'].decode('utf-8')
    # Exactly mirror the prepublished GPU2048 candidate's byte generation.
    patch = [
        ('One 1024x4096 per arm CUDA T4 continuation experiment with exact-resume.',
         'One NEW 2048x4096 per arm CUDA T4 continuation experiment with exact-resume.'),
        ('ttm_small4m_gemma2_directswap_1024x4096_t4_gpu_20261109_v1', NEW_RUN_ID),
        ('6715c0a46aa30c3e4fee8647d4540d523d26c619', NEW_PREREG),
        ('STEPS = 1024', 'STEPS = 2048'),
        ('CHECKPOINT_STEPS = (256, 512, 768, 1024)',
         'CHECKPOINT_STEPS = (512, 1024, 1536, 2048)'),
        ('"1024 additional updates starting from original T4 trained step1024 weights, not training from scratch"',
         '"2048 additional updates starting from original T4 trained step1024 weights, not training from scratch"'),
        ('after ALL arms have a complete step1024 READY',
         'after ALL arms have a complete step2048 READY'),
        ('in (1, 64, 128, 256, 512, 768, 1024)',
         'in (1, 64, 128, 256, 512, 768, 1024, 1536, 2048)'),
        ('DIRECT_SWAP_1024_POSITIVE_EXPLORATORY', 'DIRECT_SWAP_2048_POSITIVE_EXPLORATORY'),
        ('DIRECT_SWAP_1024_BENEFIT_NOT_ESTABLISHED', 'DIRECT_SWAP_2048_BENEFIT_NOT_ESTABLISHED'),
    ]
    for a, b in patch:
        s = exact_replace(s, a, b)
    # These appear several times in schemas/log lines and must all change together.
    s = s.replace('directswap1024.', 'directswap2048.')
    s = s.replace('TTM_GPU1024', 'TTM_GPU2048')
    s = exact_replace(s, "        previous = latest_ready(args, arm, schedule_sha, source_sha)\n        if previous:\n", "        previous = latest_ready(args, arm, schedule_sha, source_sha)\n        # Arm-start marker prevents silent replay of consumed optimizer work\n        # when a Colab interruption occurs before the first READY checkpoint.\n        arm_marker = args.output / \"ARM_STARTS\" / (arm + \".json\")\n        expected_marker = {\"run_id\": RUN_ID, \"arm\": arm,\n                           \"schedule_sha256\": schedule_sha, \"source_sha256\": source_sha}\n        if previous:\n            if (not arm_marker.is_file()\n                    or json.loads(arm_marker.read_text(\"utf-8\")) != expected_marker):\n                raise RuntimeError(\"RESUME_ARM_MARKER_MISSING_OR_MISMATCH\")\n        elif arm_marker.exists():\n            raise RuntimeError(\"STARTED_ARM_WITHOUT_READY_NO_AUTO_REPLAY\")\n        else:\n            arm_marker.parent.mkdir(parents=True, exist_ok=True)\n            write_json_new(arm_marker, expected_marker)\n        if previous:\n")
    if 'TTM_GPU1024' in s or 'directswap1024.gpu' in s or 'STEPS = 1024' in s:
        raise RuntimeError('STOP_OLD_EXPERIMENT_IDENTIFIER_LEFT_OVER')
    updated = s.encode('utf-8')
    if sha256(updated) != NEW_RUNNER_SHA256:
        raise RuntimeError('STOP_NEW_RUNNER_SHA256_INCORRECT:' + sha256(updated))
    out = {
        'p02_exact.py': entries['p02_exact.py'],
        'ttm_embeddinggemma2_swap.py': entries['ttm_embeddinggemma2_swap.py'],
        'ttm_directswap2048_gpu_once.py': updated,
    }
    destination.mkdir(parents=True, exist_ok=True)
    if destination.is_symlink():
        raise RuntimeError('STOP_SYMLINK_OUTPUT')
    for name, data in out.items():
        p = destination / name
        if p.exists():
            if not p.is_file() or sha256(p.read_bytes()) != sha256(data):
                raise RuntimeError('STOP_EXISTING_SOURCE_MISMATCH:' + name)
        else:
            with p.open('xb') as f:
                f.write(data)
        if sha256(p.read_bytes()) != sha256(data):
            raise RuntimeError('STOP_SOURCE_WRITE_READBACK_FAIL:' + name)
    py_compile.compile(str(destination / 'ttm_directswap2048_gpu_once.py'), doraise=True)
    return NEW_RUNNER_SHA256


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--source-dir', type=Path, required=True)
    p.add_argument('--offline-bundle', type=Path)
    args = p.parse_args()
    if args.offline_bundle:
        raw = args.offline_bundle.read_bytes()
    else:
        url = ('https://raw.githubusercontent.com/minhtri22/TokenToModel-Lab/'
               + SRC_COMMIT + '/tools/embeddinggemma2_swap/' + OLD_BUNDLE)
        with urllib.request.urlopen(url, timeout=120) as response:
            raw = response.read()
    digest = produce(raw, args.source_dir)
    print('TTM_GPU2048_SOURCE=PASS_SHA256_' + digest, flush=True)


if __name__ == '__main__':
    main()

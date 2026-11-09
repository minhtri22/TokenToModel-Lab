# TTM CAUSAL6 — one-time Colab recovery cell AFTER ZIP_PATH_REFUSED.
# This cell does NOT create science CLAIM and does NOT run the model.
# Requires source_zip, EXPECTED_PRIVATE_ZIP_SHA256, OWNER_VERIFIED_DRIVE_FREE_GIB,
# OWNER_FREE_COLAB_ONLY, MODE from the previously executed configuration cell.
from pathlib import Path, PurePosixPath
import hashlib, json, os, re, shutil, stat, zipfile

assert OWNER_FREE_COLAB_ONLY, 'HOLD_FREE_ONLY'
assert MODE == 'execute', 'HOLD_REVIEW_RESUME_SEPARATELY'
assert OWNER_VERIFIED_DRIVE_FREE_GIB >= 4, 'HOLD_DRIVE_QUOTA'
source_zip = Path('/content/drive/MyDrive/TTM/ttm-small-pilot/TTM_GEMMA2_CAUSAL6_INPUT_PRIVATE_V1_20261109.zip')
work = Path('/content/ttm_causal6_source_v1')
run = Path('/content/drive/MyDrive/TTM/ttm-small-pilot/ttm_small4m_gemma2_causal6_2048x4096_free_t4_20261109_v1')
assert not run.exists(), 'HOLD_EXISTING_SCIENCE_RUN_OR_CLAIM_DO_NOT_RESTART'
assert source_zip.is_file(), 'HOLD_PRIVATE_ZIP_NOT_FOUND'
assert re.fullmatch('[0-9a-fA-F]{64}', EXPECTED_PRIVATE_ZIP_SHA256), 'HOLD_SOURCE_SHA_NOT_SPECIFIED'
h = hashlib.sha256()
with source_zip.open('rb') as f:
    for chunk in iter(lambda: f.read(1 << 20), b''):
        h.update(chunk)
assert h.hexdigest() == EXPECTED_PRIVATE_ZIP_SHA256.lower(), 'HOLD_PRIVATE_ZIP_SHA256_MISMATCH'

# The failed original cell created this folder just before its first ZIP assertion.
# Reuse it ONLY if it is the exact controlled path and is empty. Never erase content.
assert not work.is_symlink(), 'HOLD_TEMP_SOURCE_SYMLINK'
if work.exists():
    assert work.is_dir() and not any(work.iterdir()), 'HOLD_TEMP_SOURCE_NONEMPTY_NO_AUTOCLEAN'
else:
    work.mkdir(parents=True, exist_ok=False)

with zipfile.ZipFile(source_zip) as z:
    entries = z.infolist()
    print('CAUSAL6_ZIP_RAW_NAME_PREVIEW=', [repr(x.filename) for x in entries[:12]])
    assert entries and len(entries) <= 250, 'HOLD_BAD_ZIP_ENTRY_COUNT'
    assert sum(x.file_size for x in entries) <= 2_000_000_000, 'HOLD_ZIP_TOO_LARGE'
    normalized = []
    seen = set()
    for item in entries:
        raw = item.filename
        assert '\x00' not in raw, 'ZIP_PATH_NUL_REFUSED'
        # Windows Compress-Archive may use backslashes, unlike Linux zipfile.Path.
        name = raw.replace('\\', '/')
        assert not name.startswith('/'), 'ZIP_ABSOLUTE_PATH_REFUSED'
        assert not re.match(r'^[A-Za-z]:', name), 'ZIP_DRIVE_PATH_REFUSED'
        parts_raw = name.split('/')
        assert not any(p in ('.', '..') for p in parts_raw), 'ZIP_TRAVERSAL_REFUSED'
        parts = tuple(p for p in parts_raw if p)
        assert parts and parts[0] in ('input', 'code'), 'ZIP_UNEXPECTED_TOP_LEVEL'
        rel = PurePosixPath(*parts)
        mode = (item.external_attr >> 16) & 0o170000
        assert not stat.S_ISLNK(mode), 'ZIP_SYMLINK_REFUSED'
        key = str(rel).casefold()
        assert key not in seen, 'ZIP_DUPLICATE_TARGET_REFUSED'
        seen.add(key)
        normalized.append((item, rel, item.is_dir() or raw.endswith(('/', '\\'))))
    assert z.testzip() is None, 'ZIP_CRC_ERROR'
    for item, rel, is_dir in normalized:
        dest = work.joinpath(*rel.parts)
        if is_dir:
            dest.mkdir(parents=True, exist_ok=True)
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            with z.open(item) as fin, dest.open('xb') as fout:
                shutil.copyfileobj(fin, fout, length=1 << 20)

input_dir = work / 'input'
h512 = input_dir / 'h512'
runner = work / 'code' / 'ttm_causal6_colab_free_t4_one_shot.py'
reviewer = work / 'code' / 'ttm_causal6_independent_readback.py'
seal_file = h512 / 'H512_PUBLIC_SEAL.json'
assert all(x.is_file() for x in (runner, reviewer, seal_file)), 'HOLD_REQUIRED_SOURCE_MISSING'
seal = json.loads(seal_file.read_text(encoding='utf-8'))
assert seal.get('status') == 'H512_SEALED_NOT_SCORED', 'HOLD_H512_STATUS'
assert (seal.get('stories'), seal.get('windows'), seal.get('targets')) == (512, 651, 119856), 'HOLD_H512_COUNTS'
assert seal.get('model_forward_calls') == 0, 'HOLD_H512_ALREADY_SCORED'
os.environ['CUBLAS_WORKSPACE_CONFIG'] = ':4096:8'
print('TTM_CAUSAL6_SOURCE_ZIP=VERIFIED_NORMALIZED_WINDOWS_LINUX_PATHS')
print('TTM_CAUSAL6_CLAIM=NOT_CREATED_BY_THIS_CELL')
# Now run the ORIGINAL notebook PRE-CLAIM cell; don't run science before PASS.

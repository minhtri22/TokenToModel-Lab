#!/usr/bin/env python3
"""Rebuild byte-identical PDF candidate assets from source-verified binary Git blobs.

Runs in a single GitHub Actions job only on the named docs branch. No science run.
"""
from pathlib import Path
import hashlib, json, sys, re
ROOT=Path("docs/learningbooks/dive-into-llms/PDF11_VI")
data=json.loads((ROOT/"INTEGRATION_MANIFEST_20261116.json").read_text(encoding="utf-8"))
chunks=json.loads((ROOT/"_upload_parts/CHUNK_MANIFEST.json").read_text(encoding="utf-8"))
assert data["source_commit"]=="f84c04268794ef94f8949808bbc14ab8636763a0"
assert data["bilingual_zip_sha256"]=="73b10765deb7e932e6e8a16ca1f96709b8a6f9149d6c803937ed0417bfc1788e"
assert len(data["files"])==11
assert set(chunks["parts"])=={f"{i:02}" for i in range(1,12) if i!=7}
note_data=(ROOT/"VI_SLIDE_NOTES_ALL_495.md").read_text(encoding="utf-8")
sections=note_data.split("\n\n---\n\n")
assert len(sections)==11, f"NOTE_SECTION_COUNT={len(sections)}"
verified=[]
for x in data["files"]:
    n=int(x["chapter"]); ch=f"{n:02}"
    pdf=ROOT / x["bilingual_path"]
    if n!=7:
        chunk_dir=ROOT/"_upload_parts"/f"chapter{ch}"
        names=[chunk_dir/f"part{i:02}.bin" for i in range(1,len(chunks["parts"][ch])+1)]
        assert all(p.is_file() for p in names), f"MISSING_PDF_PARTS {ch}"
        # Compare exact Git blob IDs (not just the reference names).
        def git_blob_sha(path):
            content=path.read_bytes()
            return hashlib.sha1(b"blob "+str(len(content)).encode()+b"\0"+content).hexdigest()
        for path,expected in zip(names,chunks["parts"][ch]):
            assert git_blob_sha(path)==expected,f"PART_HASH_MISMATCH {path}"
        with pdf.open("wb") as out:
            for path in names:out.write(path.read_bytes())
    pdf_bytes=pdf.read_bytes()
    pdf_sha=hashlib.sha256(pdf_bytes).hexdigest()
    assert pdf_sha==x["bilingual_sha256"],f"PDF_SHA256_MISMATCH {ch} {pdf_sha}"
    target=ROOT/x["notes_path"]
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(sections[n-1],encoding="utf-8",newline="")
    notes_sha=hashlib.sha256(target.read_bytes()).hexdigest()
    assert notes_sha==x["notes_sha256"],f"NOTES_SHA256_MISMATCH {ch}"
    verified.append({"chapter":n,"pdf":str(pdf),"pdf_sha256":pdf_sha,"pdf_bytes":len(pdf_bytes),"notes_sha256":notes_sha,"pages":x["pages"]})
assert sum(x["pages"] for x in verified)==495
receipt={
 "operation":"DIVE_INTO_LLMS_11PDF_BINARY_GITHUB_READBACK_ONEPACK",
 "source_commit":data["source_commit"],
 "source_zip_sha256":chunks["source_zip_sha256"],
 "pdf_count":len(verified),
 "notes_count":len(verified),
 "pages":sum(x["pages"] for x in verified),
 "byte_custody":"PASS_11_OF_11_PDF_AND_MARKDOWN_SHA256",
 "translation_fidelity":"HOLD_F01_F02_F03",
 "independent_linguistic_qa":"NOT_EXECUTED",
 "science_execution":False,
 "documents":verified}
(ROOT/"BINARY_UPLOAD_RECEIPT_20261116.json").write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("PDF11_REASSEMBLY_PASS=11/11; MARKDOWN=11/11; PAGES=495; FIDELITY=HOLD")

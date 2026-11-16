#!/usr/bin/env python3
"""Exact one-page formula-symbol corrigendum with preserved page count."""
from pathlib import Path
import fitz,hashlib,json,csv
from build_v2 import ROOT,V2,build_page,parse_notes
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    manifest_path=V2/"REMEDIATION_V2_MANIFEST.json"
    manifest=json.loads(manifest_path.read_text(encoding="utf-8"))
    patches=json.loads((V2/"SOURCE_ANCHORED_REPLACEMENTS.json").read_text(encoding="utf-8"))
    record=next(x for x in manifest["files"] if x["chapter"]==11)
    pdf=ROOT/record["pdf_path"];note=ROOT/record["md_path"]
    assert sha(pdf)==record["pdf_sha256"],"PINNED_PDF_MISMATCH"
    pages=parse_notes(note.read_text(encoding="utf-8"),24)
    assert pages[17]==patches["11:17"].strip(),"NEW_CORRECTION_MISMATCH"
    assert "∇R̄θ = (1/N)" in pages[17] and "∇R̄θ ≈ (1/N)" not in pages[17]
    before=fitz.open(pdf);out=fitz.open()
    font=Path("/usr/share/fonts/truetype/dejavu")
    for i in range(24):
        if i==16:
            amended,height=build_page(fitz.Archive(str(font)),before,i,pages[17])
            out.insert_pdf(amended,from_page=0,to_page=0)
            amended.close()
        else:
            out.insert_pdf(before,from_page=i,to_page=i)
    assert len(out)==len(before)==24
    clip=fitz.Rect(0,0,1280,752)
    for i in range(24):
        assert before[i].get_text(clip=clip)==out[i].get_text(clip=clip),"UPPER_TEXT_DRIFT"
    p=pdf.with_suffix(".corrected.pdf")
    out.save(p,garbage=4,deflate=True)
    out.close();before.close();p.replace(pdf)
    record["pdf_sha256"]=sha(pdf);record["md_sha256"]=sha(note)
    record["formula_correction"]="11:17, gradient estimator equality sign source-verified"
    manifest["formula_symbol_exactness"]="11:17 '=' matches source"
    manifest["independent_human_qa"]="NOT_EXECUTED"
    manifest["literal_full_translation"]="HOLD_UNVERIFIED"
    manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    path=V2/"EXTERNAL_RATER_QUEUE_495.csv"
    with path.open(encoding="utf-8",newline="") as f:
        reader=csv.DictReader(f);fields=reader.fieldnames;rows=list(reader)
    assert len(rows)==495
    n=0
    for row in rows:
        if row["chapter"]=="11" and row["page"]=="17":
            row["target_note_sha256"]=hashlib.sha256(pages[17].encode("utf-8")).hexdigest()
            row["target_note_chars"]=str(len(pages[17]))
            n+=1
    assert n==1
    with path.open("w",encoding="utf-8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)
    print("FORMULA_SOURCE_EQUALITY_CORRECTION=PASS; CH11_PAGE17; HUMAN_QA_NOT_EXECUTED",flush=True)
if __name__=="__main__":main()

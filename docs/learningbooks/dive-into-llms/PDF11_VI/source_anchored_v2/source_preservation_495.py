#!/usr/bin/env python3
"""Read-only full-coverage PDF source-region comparator vs historical docs HEAD."""
from pathlib import Path
import fitz, hashlib, json
ROOT=Path("docs/learningbooks/dive-into-llms/PDF11_VI")
V2=ROOT/"source_anchored_v2"
OLD=Path("/tmp/pdf11_v2_historical")

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    baseline=json.loads((ROOT/"REMEDIATION_MANIFEST_20261116.json").read_text(encoding="utf8"))
    v2=json.loads((V2/"REMEDIATION_V2_MANIFEST.json").read_text(encoding="utf8"))
    assert len(baseline["output_files"])==len(v2["files"])==11
    out=[];mismatch=[];total=0
    for b,n in zip(baseline["output_files"],v2["files"]):
        ch=int(b["chapter"]);assert ch==int(n["chapter"])
        a=OLD/b["pdf_path"];p=ROOT/n["pdf_path"]
        assert digest(a)==b["pdf_sha256"],f"OLD_PDF_SHA_MISMATCH_{ch}"
        assert digest(p)==n["pdf_sha256"],f"NEW_PDF_SHA_MISMATCH_{ch}"
        old=fitz.open(a);new=fitz.open(p);assert len(old)==len(new)==n["pages"]
        for i in range(len(old)):
            clip=fitz.Rect(0,0,1280,752)
            ot=old[i].get_text(clip=clip)
            nt=new[i].get_text(clip=clip)
            if ot!=nt:mismatch.append([ch,i+1,"upper_text"])
            pix1=old[i].get_pixmap(matrix=fitz.Matrix(.33,.33),clip=clip,colorspace=fitz.csRGB,alpha=False)
            pix2=new[i].get_pixmap(matrix=fitz.Matrix(.33,.33),clip=clip,colorspace=fitz.csRGB,alpha=False)
            if pix1.width!=pix2.width or pix1.height!=pix2.height or pix1.samples!=pix2.samples:
                mismatch.append([ch,i+1,"upper_raster"])
            total+=1
        out.append({"chapter":ch,"pages":len(old),"baseline_pdf_sha256":digest(a),"current_pdf_sha256":digest(p)})
        old.close();new.close()
        print(f"SOURCE_REGION_CHECK CH{ch:02} pages={n['pages']}",flush=True)
    receipt={"operation":"PDF11_V2_FULL_SOURCE_REGION_COMPARISON",
      "historical_head":"9544b06b9c95a319cae764957bad2c7450b11a9f",
      "source_commit":"f84c04268794ef94f8949808bbc14ab8636763a0",
      "scope":"UPPER_SOURCE_REGION_TEXT_AND_PIXELS_495_495",
      "pages":total,"mismatches":mismatch,
      "source_region_qa":"PASS" if total==495 and not mismatch else "FAIL",
      "independent_language_qa":"NOT_EXECUTED","full_literal_fidelity":"HOLD",
      "documents":out,"science_executed":False}
    (V2/"EXACT_SOURCE_SLIDE_READBACK_495.json").write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps({"source_region_qa":receipt["source_region_qa"],"pages":total,"mismatches":len(mismatch),"categories":{k:sum(x[2]==k for x in mismatch) for k in set(x[2] for x in mismatch)},"first_examples":mismatch[:16]}),flush=True)
    if mismatch or total!=495:raise SystemExit(1)
if __name__=="__main__":main()

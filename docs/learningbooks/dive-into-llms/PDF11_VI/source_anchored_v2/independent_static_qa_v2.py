#!/usr/bin/env python3
"""Independent static verifier, does not import the PDF builder. Not a human rater."""
from pathlib import Path
import collections,csv,fitz,hashlib,json,re,unicodedata

ROOT=Path("docs/learningbooks/dive-into-llms/PDF11_VI")
V2=ROOT/"source_anchored_v2"
PIN="f84c04268794ef94f8949808bbc14ab8636763a0"
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def tokens(s):
    return collections.Counter(re.findall(r"[\w\u00c0-\u1ef9]+",unicodedata.normalize("NFKC",s).lower()))
def parse_notes(s):
    ms=list(re.finditer(r"(?m)^## Trang (\d+)/(\d+)\s*\n",s))
    return {int(m.group(1)):s[m.end():(ms[i+1].start() if i+1<len(ms) else len(s))].strip() for i,m in enumerate(ms)}
def main():
    base=json.loads((ROOT/"REMEDIATION_MANIFEST_20261116.json").read_text(encoding="utf-8"))
    amended=json.loads((V2/"AMENDMENT_MANIFEST.json").read_text(encoding="utf-8"))
    changes=json.loads((V2/"SOURCE_ANCHORED_REPLACEMENTS.json").read_text(encoding="utf-8"))
    m=json.loads((V2/"REMEDIATION_V2_MANIFEST.json").read_text(encoding="utf-8"))
    rows=list(csv.DictReader((V2/"EXTERNAL_RATER_QUEUE_495.csv").open(encoding="utf-8",newline="")))
    prior=list(csv.DictReader((ROOT/"independent_adjudication"/"PAGE_SCREEN_495.csv").open(encoding="utf-8",newline="")))
    errors=[];rpt=[];bad_chars=[];low_overlap=[];source_drift=[];samples=[]
    if len(rows)!=495 or len(prior)!=495:errors.append("QUEUE_COUNT")
    if len(changes)!=13 or len(m["files"])!=11:errors.append("MANIFEST_COUNT")
    if m["source_pin"]!=PIN:errors.append("SOURCE_PIN")
    for row,prev in zip(rows,prior):
        if (row["chapter"],row["page"],row["source_text_sha256"])!=(prev["chapter"],prev["page"],prev["source_text_sha256"]):
            errors.append("SOURCE_QUEUE_DRIFT")
            break
        if row["rater_id"] or row["target_verdict"]:errors.append("PREMATURE_RATER_VERDICT")
    for n,(old,new) in enumerate(zip(base["output_files"],m["files"]),start=1):
        if old["chapter"]!=new["chapter"] or old["pages"]!=new["pages"]:errors.append("INDEX_MISMATCH")
        p=ROOT/new["pdf_path"];md=ROOT/new["md_path"]
        if sha(p)!=new["pdf_sha256"] or sha(md)!=new["md_sha256"]:errors.append(f"FILE_SHA_MISMATCH:{n}")
        doc=fitz.open(p);notes=parse_notes(md.read_text(encoding="utf-8"))
        if len(doc)!=new["pages"] or len(notes)!=new["pages"]:errors.append(f"PAGE_COUNT:{n}")
        for idx in range(len(doc)):
            page=doc[idx];text=page.get_text(sort=True)
            vi=text.split("NỘI DUNG TIẾNG VIỆT",1)[-1]
            if "NỘI DUNG TIẾNG VIỆT" not in text or PIN not in text:errors.append(f"MISSING_LABEL:{n}:{idx+1}")
            bad=[c for c in vi if (unicodedata.category(c)=="Cc" and c not in "\r\n\t") or c=="\ufffd"]
            if bad:bad_chars.append([n,idx+1])
            body=notes[idx+1]
            # The PDF spells out two emoji icons in ch06, leaving all meaningful words unchanged.
            body=body.replace("[🔒🔒classic]","[classic, biểu tượng ổ khóa]").replace("[🔓🔓Jailbreak]","[Jailbreak, biểu tượng mở khóa]")
            ref=tokens(body);got=tokens(vi);overlap=sum((ref&got).values())/max(1,sum(ref.values()))
            if overlap<.95:low_overlap.append([n,idx+1,round(overlap,3)])
            if (n,idx+1) in {(1,20),(1,43),(6,22),(6,27),(8,7),(9,14),(10,8),(11,17)}:
                key=f"{n:02}:{idx+1:02}"
                if notes[idx+1]!=changes[key].strip():errors.append("PATCH_CONTENT_MISMATCH:"+key)
            if idx in {0,len(doc)//2,len(doc)-1}:samples.append([n,idx+1,round(page.rect.height)])
        doc.close()
        rpt.append({"chapter":n,"pages":new["pages"],"pdf_sha256":sha(p),"notes_sha256":sha(md)})
    if bad_chars:errors.append("BAD_UNICODE")
    if low_overlap:errors.append("MISSING_TARGET_NOTE_IN_PDF")
    result={"operation":m["operation"],"review_mode":"INDEPENDENT_STATIC_CODE_PATH_ONLY",
      "total_pages":sum(x["pages"] for x in rpt),"tested_pages":495,"amended_pages":len(changes),
      "source_anchor_rows":len(rows),"font_control_fail_pages":bad_chars,
      "target_content_mismatch_pages":low_overlap,"errors":errors,"static_qa":"PASS" if not errors else "FAIL",
      "external_human_rater":"NOT_EXECUTED","external_rater_verified_pages":0,
      "full_literal_fidelity":"HOLD","science_executed":False,"documents":rpt}
    (V2/"REMEDIATION_V2_STATIC_QA.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"static_qa":result["static_qa"],"pages":result["tested_pages"],
      "bad_unicode":len(bad_chars),"missing_content":len(low_overlap),"errors":errors[:12]},ensure_ascii=False),flush=True)
    if errors:raise SystemExit(1)
if __name__=="__main__":main()

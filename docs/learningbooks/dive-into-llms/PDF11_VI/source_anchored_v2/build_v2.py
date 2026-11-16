#!/usr/bin/env python3
"""PDF11 docs-only source-anchored note reflow; preserves source slide XObjects.
Not an independent translation evaluation or science execution.
"""
import csv, hashlib, html, json, re, unicodedata
from pathlib import Path
import fitz

ROOT=Path("docs/learningbooks/dive-into-llms/PDF11_VI")
V2=ROOT/"source_anchored_v2"
PIN="f84c04268794ef94f8949808bbc14ab8636763a0"
SIZES=(1210,1400,1660,1960,2360,2860,3500,4400,5500)
WIDTH=1280
SOURCE_END=752
CSS='''@font-face {font-family:VN;src:url("DejaVuSans.ttf");}
*{font-family:VN;color:#1c2738;}
h2{font-size:23px;line-height:1.30;margin:0 0 12px 0;}
p{font-size:19.0px;line-height:1.36;margin:0 0 6px 0;}
p.item{padding-left:10px;}'''
LABELCSS='''@font-face {font-family:VN;src:url("DejaVuSans.ttf");}
*{font-family:VN;color:#213452;}h3{font-size:20px;margin:0;}p{font-size:11px;margin:0;}'''

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def parse_notes(content,n):
    heads=list(re.finditer(r"(?m)^## Trang (\d+)/(\d+)\s*\n",content))
    assert len(heads)==n,f"HEAD_COUNT {len(heads)} not {n}"
    notes={}
    for i,m in enumerate(heads):
        p,decl=int(m.group(1)),int(m.group(2))
        assert (p,decl)==(i+1,n)
        notes[p]=content[m.end():(heads[i+1].start() if i+1<len(heads) else len(content))].strip()
    return notes

def marked_html(note):
    rows=[x.strip() for x in note.splitlines() if x.strip()]
    assert rows
    # DejaVu Sans contains Greek/math but may not render color emoji in old
    # jailbreak example; preserve source notation in Markdown.
    rows=[x.replace("[🔒🔒classic]","[classic, biểu tượng ổ khóa]")
           .replace("[🔓🔓Jailbreak]","[Jailbreak, biểu tượng mở khóa]")
           for x in rows]
    header="<h2>"+html.escape(rows[0])+"</h2>"
    ps=[]
    for row in rows[1:]:
        kind=' class="item"' if re.match(r"^(?:[•*\-]|\d+\.)",row) else ""
        ps.append("<p"+kind+">"+html.escape(row)+"</p>")
    return header+"".join(ps)

def build_page(archive,old,i,note):
    for height in SIZES:
        scratch=fitz.open()
        page=scratch.new_page(width=WIDTH,height=height)
        clip=fitz.Rect(0,0,WIDTH,SOURCE_END)
        page.show_pdf_page(clip,old,i,clip=clip,keep_proportion=False)
        page.draw_rect(fitz.Rect(0,SOURCE_END,WIDTH,height),fill=(1,1,1),color=None,overlay=True)
        page.draw_line(fitz.Point(35,SOURCE_END+8),fitz.Point(WIDTH-35,SOURCE_END+8),color=(.78,.8,.83),width=1)
        free_a,scale_a=page.insert_htmlbox(fitz.Rect(35,772,1245,811),
          "<h3>NỘI DUNG TIẾNG VIỆT</h3>",css=LABELCSS,archive=archive,scale_low=1)
        free_b,scale_b=page.insert_htmlbox(fitz.Rect(35,810,1245,height-53),
          marked_html(note),css=CSS,archive=archive,scale_low=1)
        foot=f"Nguồn: Lordog/dive-into-llms · {PIN} | Ứng viên chuyển ngữ, chưa đạt QA độc lập"
        free_c,scale_c=page.insert_htmlbox(fitz.Rect(35,height-42,1245,height-7),
          "<p>"+html.escape(foot)+"</p>",css=LABELCSS,archive=archive,scale_low=1)
        if free_a>=0 and free_b>=0 and free_c>=0:
            return scratch,height
        scratch.close()
    raise RuntimeError(f"UNFITTING_CONTENT page={i+1} chars={len(note)} maxheight={max(SIZES)}")

def main():
    base=json.loads((ROOT/"REMEDIATION_MANIFEST_20261116.json").read_text(encoding="utf-8"))
    screen=ROOT/"independent_adjudication"/"PAGE_SCREEN_495.csv"
    amend=json.loads((V2/"AMENDMENT_MANIFEST.json").read_text(encoding="utf-8"))
    changes=json.loads((V2/"SOURCE_ANCHORED_REPLACEMENTS.json").read_text(encoding="utf-8"))
    assert amend["source_pin"]==PIN and base["source_pin"]==PIN
    assert len(base["output_files"])==11 and len(changes)==13
    changed={int(k.split(":")[0]) for k in changes}
    font=Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    assert font.is_file(),"DEJAVU_FONT_MISSING"
    archive=fitz.Archive(str(font.parent))
    records=[]
    page_info={}
    for rec in base["output_files"]:
        ch=int(rec["chapter"]);n=int(rec["pages"]);pdf=ROOT/rec["pdf_path"]
        note_path=ROOT/rec["md_path"]
        if digest(pdf)!=rec["pdf_sha256"]:raise RuntimeError(f"BASE_PDF_MISMATCH {ch}")
        note=note_path.read_text(encoding="utf-8")
        pages=parse_notes(note,n)
        for key,expected in changes.items():
            c,p=map(int,key.split(":"))
            if c==ch and pages[p]!=expected.strip():
                raise RuntimeError(f"NOTE_PATCH_MISMATCH CH{ch:02} P{p}")
        doc=fitz.open(pdf)
        assert len(doc)==n
        heights=[]
        if ch in changed:
            assembled=fitz.open()
            for i in range(n):
                scratch,height=build_page(archive,doc,i,pages[i+1])
                assembled.insert_pdf(scratch,from_page=0,to_page=0)
                scratch.close()
                heights.append(height)
            target=pdf.with_suffix(".next.pdf")
            assembled.save(target,garbage=4,deflate=True)
            assembled.close();doc.close()
            target.replace(pdf)
        else:
            heights=[round(float(x.rect.height)) for x in doc]
            doc.close()
        records.append({"chapter":ch,"pages":n,"pdf_path":rec["pdf_path"],"md_path":rec["md_path"],
            "pdf_sha256":digest(pdf),"md_sha256":digest(note_path),
            "source_pdf_before_sha256":rec["pdf_sha256"],"page_height_min":min(heights),
            "page_height_max":max(heights),"was_reflowed":ch in changed})
        page_info[ch]=pages
        print(f"PDF_V2 CH{ch:02} pages={n} reflowed={ch in changed} height={max(heights)}",flush=True)
    assert sum(x["pages"] for x in records)==495
    old_rows=list(csv.DictReader(screen.open(encoding="utf-8",newline="")))
    assert len(old_rows)==495
    path=V2/"EXTERNAL_RATER_QUEUE_495.csv"
    fields=["chapter","page","source_path","source_text_sha256","target_note_sha256",
       "target_note_chars","source_text_chars","source_image_objects","source_vector_drawings",
       "heuristic_flags","prior_manual_assessment","prior_finding_id","amended_page",
       "rater_id","rater_date","paragraphs","table_cells","formulae","diagram_labels",
       "semantic_accuracy","omissions","target_verdict","evidence_url"]
    with path.open("w",encoding="utf-8",newline="") as f:
        out=csv.DictWriter(f,fieldnames=fields);out.writeheader()
        for row in old_rows:
            ch,p=int(row["chapter"]),int(row["page"])
            body=page_info[ch][p]
            output={k:"" for k in fields}
            output.update({"chapter":ch,"page":p,"source_path":row["source_path"],
                "source_text_sha256":row["source_text_sha256"],
                "target_note_sha256":hashlib.sha256(body.encode("utf-8")).hexdigest(),
                "target_note_chars":len(body),"source_text_chars":row["source_text_chars"],
                "source_image_objects":row["source_image_objects"],
                "source_vector_drawings":row["source_vector_drawings"],
                "heuristic_flags":row["screen_flags"],"prior_manual_assessment":row["manual_assessment"],
                "prior_finding_id":row["manual_finding_id"],
                "amended_page":str(f"{ch:02}:{p:02}" in changes).lower()})
            out.writerow(output)
    manifest={"operation":"DIVE_INTO_LLMS_11PDF_VI_SOURCE_ANCHORED_CONTENT_REMEDIATION_AND_EXTERNAL_RATER_FULL_COVERAGE_ONEPACK",
      "source_pin":PIN,"historical_baseline_manifest":"REMEDIATION_MANIFEST_20261116.json",
      "amended_page_count":len(changes),"amended_pages":sorted(changes),
      "total_pages":495,"pdf_count":11,"pdf_reflowed_count":len(changed),
      "external_rater_queue":str(path.relative_to(ROOT)),
      "external_rater_verified_pages":0,
      "literal_full_translation":"HOLD_UNVERIFIED",
      "independent_human_qa":"NOT_EXECUTED",
      "science_executed":False,"files":records}
    (V2/"REMEDIATION_V2_MANIFEST.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("V2_BUILD_COMPLETED_495_PAGES_EXTERNAL_RATER_NOT_EXECUTED",flush=True)

if __name__=="__main__":main()

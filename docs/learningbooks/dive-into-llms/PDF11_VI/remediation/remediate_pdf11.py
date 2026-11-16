#!/usr/bin/env python3
"""Deterministic, source-preserving reflow of 11 *existing* PDF candidate documents.

Inputs: 11 pre-existing bilingual PDFs and Markdown notes, manifest, scoped text
corrections. Each PDF's upper source slide is reused from its original GitHub
candidate; no source slide is synthesized, redrawn or retranslated.

This is a layout/glyph and seven-page textual remediation, NOT a certification of
full literal translation. Does not execute notebooks or model training.
"""
from __future__ import annotations
import argparse
import hashlib
import html
import json
import os
import re
import shutil
import sys
import unicodedata
from pathlib import Path

import fitz

PIN = "f84c04268794ef94f8949808bbc14ab8636763a0"
HEADER = "NỘI DUNG TIẾNG VIỆT"
CHAPTERS = list(range(1,12))
PAGE_WIDTH, PAGE_HEIGHT, SOURCE_CROP_BOTTOM = 1280, 1210, 752
ROOT_DEFAULT = Path(__file__).parent


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def read_notes(content: str, ch: int, total: int):
    pat = r"(?m)^## Trang (\d+)/(\d+)\s*\n"
    matches = list(re.finditer(pat, content))
    if len(matches) != total:
        raise ValueError(f"chapter {ch:02} headings count {len(matches)} != {total}")
    block = {}
    for i, m in enumerate(matches):
        page, declared_total = int(m.group(1)), int(m.group(2))
        if page != i+1 or declared_total != total:
            raise ValueError(f"chapter {ch:02} invalid heading {page}/{declared_total}")
        end = matches[i+1].start() if i+1 < len(matches) else len(content)
        block[page] = content[m.end():end].strip()
    return block, content[:matches[0].start()]


def make_notes(header: str, pages: dict[int,str], total: int):
    return header.rstrip()+"\n\n" + "\n\n".join(f"## Trang {p}/{total}\n\n{pages[p]}" for p in range(1,total+1)) + "\n"


def render_inline(text: str):
    esc=html.escape(text,quote=True)
    esc=re.sub(r"\*\*(.+?)\*\*",r"<strong>\1</strong>",esc)
    esc=re.sub(r"(?<!\*)`([^`]+)`(?!\*)",r"<code>\1</code>",esc)
    return esc


def as_html(text: str):
    rows=[x.strip() for x in text.splitlines() if x.strip()]
    if not rows:raise ValueError("empty paragraph")
    title=render_inline(rows[0])
    body=[]
    for line in rows[1:]:
        cls='list' if re.match(r'^(?:[•▪*\-]|\d+[.])',line) else 'plain'
        body.append(f'<p class="{cls}">{render_inline(line)}</p>')
    return f'<h2>{title}</h2>'+''.join(body)


def find_dejavu():
    from pathlib import Path
    options=[Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'),
             Path('/usr/local/share/fonts/DejaVuSans.ttf')]
    return next((p for p in options if p.exists()),None)


def validate_supported_chars(text:str):
    issues=[(hex(ord(c)),unicodedata.name(c,'UNKNOWN')) for c in text
            if unicodedata.category(c)=='Cc' and c not in '\r\n\t']
    if issues:raise ValueError(f'UNRESOLVED_CONTROL_CHARS={issues[:10]}')


def main():
    a=argparse.ArgumentParser()
    a.add_argument('--root',required=True,help='Existing PDF11_VI directory')
    a.add_argument('--out',required=True,help='Staging directory; may equal root only after checks')
    a.add_argument('--overrides',required=True)
    a.add_argument('--expected-json',default='',help='optional exact source input manifest')
    args=a.parse_args()
    root=Path(args.root).resolve()
    out=Path(args.out).resolve()
    out.mkdir(parents=True,exist_ok=True)
    if find_dejavu() is None:raise SystemExit('REQUIRED_DEJAVU_FONT_MISSING')
    fontdir=find_dejavu().parent
    ar=fitz.Archive(str(fontdir))
    css='''
    @font-face {font-family: "VnDejaVu";src:url("DejaVuSans.ttf");}
    * {font-family: "VnDejaVu", sans-serif; color: #1c2738;}
    h2 {font-size: 23px; line-height: 1.35; margin: 0 0 13px 0; font-weight:bold;}
    p {font-size: 19.7px; line-height: 1.34; margin:0 0 5px 0;}
    p.list {margin-left: 12px;}
    strong {font-weight:bold;}
    code {font-family:"VnDejaVu"; font-size:19.3px;}
    '''
    css_label='''@font-face {font-family: "VnDejaVu";src:url("DejaVuSans.ttf");}
    * {font-family:"VnDejaVu";color:#213452;}h3{font-size:20px;margin:0;}p{font-size:10.5px;margin:0;}'''
    overrides=json.loads(Path(args.overrides).read_text(encoding='utf-8'))
    expected_manifest=json.loads((root/'INTEGRATION_MANIFEST_20261116.json').read_text(encoding='utf-8'))
    if expected_manifest['source_commit']!=PIN or len(expected_manifest['files'])!=11:
        raise SystemExit('MISMATCH_PIN_OR_EXPECTED_FILES')
    pdfs=[];detail=[]
    for rec in expected_manifest['files']:
        chapter=int(rec['chapter']);ch=f'{chapter:02}'
        pdf_name=rec['bilingual_path']; md_name=rec['notes_path']
        oldpdf=root/pdf_name;oldmd=root/md_name
        if sha(oldpdf)!=rec['bilingual_sha256'] or sha(oldmd)!=rec['notes_sha256']:
            raise SystemExit('EXACT_BASE_CUSTODY_FAIL '+ch)
        olddoc=fitz.open(oldpdf)
        notes=oldmd.read_text(encoding='utf-8')
        pages,hdr=read_notes(notes,chapter,rec['pages'])
        revised={}
        for p,body in pages.items():
            if f'{ch}:{p}' in overrides:body=overrides[f'{ch}:{p}']
            # Catch an unrelated U+0014 in original MD, fail unless corrected.
            validate_supported_chars(body)
            revised[p]=body
        out_md=out/md_name
        out_md.parent.mkdir(parents=True,exist_ok=True)
        out_md.write_text(make_notes(hdr,revised,rec['pages']),encoding='utf-8')
        outdoc=fitz.open(); scales=[]
        for i in range(rec['pages']):
            content=revised[i+1]
            page=outdoc.new_page(width=PAGE_WIDTH,height=PAGE_HEIGHT)
            old_page=olddoc[i]
            # Maintain upper section as a real PDF Form XObject (vector and images).
            upper=fitz.Rect(0,0,PAGE_WIDTH,SOURCE_CROP_BOTTOM)
            page.show_pdf_page(upper,olddoc,i,clip=upper,keep_proportion=False)
            page.draw_rect(fitz.Rect(0,752,PAGE_WIDTH,1210),color=None,fill=(1,1,1),overlay=True)
            page.draw_line(fitz.Point(35,760),fitz.Point(1245,760),color=(0.77,0.80,0.84),width=1)
            # Header and the entire note use DejaVu so Greek/math arrows are extractable.
            top,ks=page.insert_htmlbox(fitz.Rect(35,772,1245,810),
                '<h3>NỘI DUNG TIẾNG VIỆT</h3>',css=css_label,archive=ar,scale_low=1)
            if top<0:raise ValueError(f'MARKER_CANNOT_FIT {ch} {i+1}')
            free,scl=page.insert_htmlbox(fitz.Rect(35,812,1245,1168),
                as_html(content),css=css,archive=ar,scale_low=.87)
            if free<0 or scl<.87:raise ValueError(f'ANNOTATION_OVERFLOW {ch} {i+1} scale={scl:.3f}')
            foot=(f'Nguồn: Lordog/dive-into-llms  ·  {PIN}  |  '
                 'Bản song ngữ tham khảo · Chưa đạt QA dịch nguyên văn')
            spare,foot_scale=page.insert_htmlbox(fitz.Rect(35,1182,1248,1206),
                f'<p>{html.escape(foot)}</p>',css=css_label,archive=ar,scale_low=1)
            if spare<0: raise ValueError(f'FOOTER_CANNOT_FIT {ch} {i+1}')
            scales.append(round(scl,5))
        out_pdf=out/pdf_name
        outdoc.save(out_pdf,garbage=4,deflate=True)
        outdoc.close(); olddoc.close()
        pdfs.append({'chapter':chapter,'pages':rec['pages'],'pdf_path':pdf_name,'pdf_sha256':sha(out_pdf),
                     'pdf_bytes':out_pdf.stat().st_size,'md_path':md_name,'md_sha256':sha(out_md),
                     'min_scale':min(scales),'scales_under_0_95':sum(x<.95 for x in scales),'overrides':[p for p in revised if f'{ch}:{p}' in overrides]})
        detail.append({'chapter':chapter,'scales':scales})
        print(f'CHAPTER={ch} PAGES={rec["pages"]} MIN_SCALE={min(scales):.4f} PDF_SHA256={sha(out_pdf)}',flush=True)
    manifest={
      'operation':'DIVE_INTO_LLMS_11PDF_VI_FIDELITY_REMEDIATION_AND_INDEPENDENT_LANGUAGE_QA_ONEPACK',
      'status':'REMEDIATION_CANDIDATE_PENDING_INDEPENDENT_QA',
      'source_pin':PIN,'source_zip_sha256':'251d0d49601e536bf1eb94deb727da665693126a3ef7d04d8efff9f3550406fe',
      'prior_bilingual_zip_sha256':'73b10765deb7e932e6e8a16ca1f96709b8a6f9149d6c803937ed0417bfc1788e',
      'input_custody':'PASS_22_OF_22','output_files':pdfs,
      'upstream_slide_preservation':'UPPER_REGION_COPIED_AS_PDF_FORM_XOBJECT_FROM_EXACT_OLD_CANDIDATE',
      'literal_complete_translation':False,
      'independent_linguistic_qa':'NOT_EXECUTED',
      'science_executed':False}
    (out/'REMEDIATION_MANIFEST_20261116.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (out/'REMEDIATION_LAYOUT_DETAIL_20261116.json').write_text(json.dumps(detail,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('REMEDIATION_CANDIDATE_GENERATED=11_PDF_11_NOTES; NO_FULL_FIDELITY_CLAIM',flush=True)

if __name__=='__main__':main()

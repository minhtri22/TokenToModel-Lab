#!/usr/bin/env python3
"""Strict C01-C04 signed FP32 parity: independent, no model loads, no reruns."""
import argparse,hashlib,json,math,zipfile
from pathlib import Path

PREREG="82fdd9fe716579181db648caa69170fb63d115a6"
REF_ZIP="e5d522bd5234c46af77dbb85990779bd09e25d35be587538cec577ee486c5996"
REF_RAW="dbebd9e5261ad4857b72ff16cf9383ce243dab9ca72ade5332e8325ea2c48e25"
REF_NAME="TTM_T5_C01_C04_P02_FP32_FROZEN_REFERENCE_20261110.jsonl"
LIMIT=0.001
FIX={
"C01":[1531,1448],
"C02":[1656,1282,646,1827],
"C03":[1781,1116,686,656,1421,1258,1286,2029,1493,1645,485],
"C04":[1906,950,726,1919,386,2019,849,482,889,1037,1758,785,1969,754,1900,1892,727]}

def digest(data):return hashlib.sha256(data).hexdigest()
def sha(path):return digest(path.read_bytes())
def blob(path):
    data=path.read_bytes()
    return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
def parse4(data):
    text=data.decode("utf-8")
    lines=text.splitlines()
    if len(lines)!=4 or not text.endswith("\n"):raise ValueError("EXACT_FOUR_JSONL_LINES_REQUIRED")
    return [json.loads(t) for t in lines]
def checked(rows,origin):
    found={}
    for row in rows:
        k=row.get("fixture_id")
        if k not in FIX or k in found or row.get("token_ids")!=FIX[k]:
            raise ValueError("FIXTURE_ID_TOKEN_OR_DUPLICATE:"+origin)
        vals=row.get("logits")
        if not isinstance(vals,list) or len(vals)!=2048 or any(
            type(x) not in (float,int) or not math.isfinite(x) for x in vals):
            raise ValueError("LOGITS_NONFINITE_OR_WRONG_LENGTH:"+origin)
        if origin=="native" and (
            row.get("arm_id")!="S1_F32_NO_FLASH" or row.get("kv_type")!="F32" or
            row.get("flash")!="DISABLED" or row.get("flash_nodes_observed")!=0):
            raise ValueError("NATIVE_CONTEXT_NOT_F32_FLASH_OFF")
        if origin=="reference" and row.get("source")!="P02_F32_STEP1024_GELU_ERF":
            raise ValueError("REFERENCE_NOT_TRUE_P02")
        found[k]=vals
    if set(found)!=set(FIX):raise ValueError("MISSING_HELDOUT_FIXTURES")
    return found

def main():
    a=argparse.ArgumentParser()
    for flag in ("prereg","reference_zip","native_logits","native_trace","output"):
        a.add_argument("--"+flag.replace("_","-"),type=Path,required=True)
    opts=a.parse_args()
    if opts.output.exists():raise FileExistsError("REPORT_EXISTS_NO_OVERWRITE")
    if blob(opts.prereg)!=PREREG:raise ValueError("PREREG_SOURCE_NOT_PINNED")
    frozen=json.loads(opts.prereg.read_text("utf-8"))
    if ({x["fixture_id"]:x["token_ids"] for x in frozen["fixtures"] if x["partition"]=="confirmatory"}!=FIX
        or frozen["source_pins"]["previously_approved_strict_threshold"]!=LIMIT):
        raise ValueError("HELDOUT_PREREG_CHANGED")
    if sha(opts.reference_zip)!=REF_ZIP:raise ValueError("REFERENCE_ZIP_SHA_MISMATCH")
    with zipfile.ZipFile(opts.reference_zip) as archive:
        if archive.namelist()!=[REF_NAME]:raise ValueError("EXACT_REFERENCE_ENTRY_REQUIRED")
        raw=archive.read(REF_NAME)
    if digest(raw)!=REF_RAW:raise ValueError("REFERENCE_JSONL_SHA_MISMATCH")
    ref=checked(parse4(raw),"reference")
    native=checked(parse4(opts.native_logits.read_bytes()),"native")
    erf=set()
    with opts.native_trace.open("r",encoding="utf-8") as f:
        for line in f:
            if not line.strip():raise ValueError("EMPTY_TRACE_LINE")
            row=json.loads(line)
            if row.get("actual_node_name")=="ffn_gelu_erf-0":
                fid=row.get("fixture_id")
                if fid not in FIX or fid in erf or row.get("stage")!="ffn_gelu-0":
                    raise ValueError("ACTUAL_ERF_NODE_BAD_OR_DUPLICATED")
                erf.add(fid)
    if erf!=set(FIX):raise ValueError("ERF_GRAPH_NOT_ATTESTED_4_OF_4")
    results=[]
    for fid in FIX:
        diffs=[b-a for a,b in zip(ref[fid],native[fid])]
        index=max(range(2048),key=lambda i:abs(diffs[i]))
        err=abs(diffs[index])
        results.append({
            "fixture_id":fid,"tokens":len(FIX[fid]),
            "max_abs":err,"mean_abs":sum(abs(d) for d in diffs)/2048,
            "signed_peak_native_minus_P02":diffs[index],
            "peak_logit_index":index,
            "strict_pass":err<=LIMIT,
            "top1_equal":max(range(2048),key=lambda j:ref[fid][j])==
                         max(range(2048),key=lambda j:native[fid][j])})
    passes=sum(row["strict_pass"] for row in results)
    receipt={
        "schema":"ttm.t5.C01_C04.GELU_ERF.independent_strict_confirmation.v1",
        "status":"STRICT_PASS_4_OF_4" if passes==4 else f"STRICT_FAIL_{4-passes}_OF_4",
        "rows":results,"strict_threshold":LIMIT,
        "pre_registration_git_blob":PREREG,
        "logits_per_fixture":2048,"real_ERF_nodes":len(erf),
        "native_sha256":sha(opts.native_logits),"native_trace_sha256":sha(opts.native_trace),
        "reference_zip_sha256":REF_ZIP,"reference_jsonl_sha256":REF_RAW,
        "confirmatory_replayed":False,"old_inputs_replayed":False,
        "training":False,"TEST_or_Q1Q2":False,"merge":"HOLD_PENDING_INDEPENDENT_REVIEW"}
    with opts.output.open("x",encoding="utf-8",newline="\n") as out:
        json.dump(receipt,out,sort_keys=True,indent=2)
        out.write("\n")
    print("CONFIRMATORY_STATUS="+receipt["status"])
    print("CONFIRMATORY_AUDIT_SHA256="+sha(opts.output))

if __name__=="__main__":
    try:main()
    except (ValueError,KeyError,TypeError,OSError,RuntimeError,zipfile.BadZipFile) as exc:
        print("CONFIRMATORY_TECHNICAL_HOLD:"+type(exc).__name__+":"+str(exc))
        raise SystemExit(2)

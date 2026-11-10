#!/usr/bin/env python3
"""Independent read-only signed elementwise Torch/GGML first-op trace auditor.

Consumes NEW D01 D02 only. Refuses shape coercion or "best effort" mapping.
Does not run models/TEST, write existing evidence, or adjudicate causal proof.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

PREREG_BLOB="82fdd9fe716579181db648caa69170fb63d115a6"
SENSITIVITY=1e-5
STRICT_LIMIT=0.001
FIXTURES={"D01":[1281],"D02":[1406,971,566,1092,1587]}
REQUIRED=(
    "inpL","attn_norm-0","wqkv_b-0","kqv-0",
    "attn_wo_mm-0","attn_wo_out-0","ffn_inp-0",
    "ffn_up_b-0","ffn_gelu-0","result_output"
)
ORDER=(
    "inpL","attn_norm-0","wqkv_b-0",
    "Qcur-0","Kcur-0","Vcur-0","kq-0","kq_soft_max-0",
    "kqv-0","kqv_out-0","attn_wo_mm-0","attn_wo_out-0",
    "ffn_inp-0","ffn_norm-0","ffn_up_b-0","ffn_gelu-0",
    "ffn_out-0","result_norm","result_output"
)
MATRIX_WIDTHS={
    "inpL":256,"attn_norm-0":256,"wqkv_b-0":768,
    "kqv_out-0":256,"attn_wo_mm-0":256,"attn_wo_out-0":256,
    "ffn_inp-0":256,"ffn_norm-0":256,"ffn_up_b-0":1024,
    "ffn_gelu-0":1024,"ffn_out-0":256
}

def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1<<20),b""):h.update(chunk)
    return h.hexdigest()

def blob(path):
    b=path.read_bytes()
    return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()

def read_jsonl(path,maxrows):
    rows=[]
    with path.open("r",encoding="utf-8") as f:
        for line in f:
            if not line.strip():raise ValueError("BLANK_JSONL_LINE")
            rows.append(json.loads(line))
            if len(rows)>maxrows:raise ValueError("EXCESS_JSONL_ROWS")
    return rows

def tensor_dict(rows,origin):
    data={}
    for row in rows:
        key=(row.get("fixture_id"),row.get("stage"))
        if key in data:raise ValueError("DUPLICATE_STAGE:"+str(key))
        if key[0] not in FIXTURES:raise ValueError("NOT_NEW_DISCOVERY_FIXTURE")
        if key[1] not in ORDER and not key[1].startswith("result_output_gelu_tanh") and not key[1].startswith("ffn_gelu_tanh"):
            raise ValueError("UNKNOWN_STAGE:"+str(key))
        if row.get("dtype")!="F32":raise ValueError("NON_F32_STAGE")
        vals=row.get("values")
        if not isinstance(vals,list) or not vals or any(
                isinstance(x,bool) or not isinstance(x,(int,float)) or not math.isfinite(x)
                for x in vals):
            raise ValueError("INVALID_F32_TENSOR")
        meta=row.get("ne") if origin=="native" else row.get("torch_shape")
        if not isinstance(meta,list) or any(not isinstance(x,int) or x<1 for x in meta):
            raise ValueError("INVALID_SHAPE")
        product=1
        for x in meta:product*=x
        if product!=len(vals):raise ValueError("VALUE_COUNT_SHAPE_MISMATCH:"+str(key))
        data[key]=row
    return data

def align_values(stage,ref,native,length):
    expected=ref["values"]
    shape=ref["torch_shape"]
    n=native["ne"]
    if len(n)!=4:raise ValueError("NATIVE_NE_4_REQUIRED")
    if stage in MATRIX_WIDTHS:
        w=MATRIX_WIDTHS[stage]
        if shape!=[length,w] or n!=[w,length,1,1]:
            raise ValueError("MATRIX_SHAPE_NOT_ALIGNED:"+stage+":"+str((shape,n)))
        return expected,native["values"]
    if stage in ("Qcur-0","Kcur-0","Vcur-0"):
        if shape!=[length,4,64] or n!=[64,4,length,1]:
            raise ValueError("QKV_SHAPE_NOT_ALIGNED:"+stage)
        return expected,native["values"]
    if stage=="kqv-0":
        if shape!=[4,length,64] or n!=[64,length,4,1]:
            raise ValueError("KQV_SHAPE_NOT_ALIGNED")
        return expected,native["values"]
    if stage in ("kq-0","kq_soft_max-0"):
        if shape!=[4,length,length] or n[0]<length or n[1:]!=[length,4,1]:
            raise ValueError("PADDED_KQ_SHAPE_NOT_RECONCILED:"+str(n))
        picked=[]
        for h in range(4):
            for q in range(length):
                offset=(h*length+q)*n[0]
                picked.extend(native["values"][offset:offset+length])
        return expected,picked
    if stage in ("result_norm","result_output"):
        w=256 if stage=="result_norm" else 2048
        if shape!=[w] or n!=[w,1,1,1]:
            raise ValueError("FINAL_STAGE_SHAPE_NOT_ALIGNED:"+stage)
        return expected,native["values"]
    raise ValueError("STAGE_NOT_MAPPED:"+stage)

def compare(ref,got):
    if len(ref)!=len(got):raise ValueError("ALIGNED_VALUE_COUNTS_DIFFER")
    diff=[float(a)-float(b) for a,b in zip(got,ref)]
    worst=max(range(len(diff)),key=lambda i:abs(diff[i]))
    return {"element_count":len(diff),
       "max_abs":abs(diff[worst]),"mean_abs":sum(abs(x) for x in diff)/len(diff),
       "signed_peak":diff[worst],"peak_index":worst,
       "sign":1 if diff[worst]>0 else -1 if diff[worst]<0 else 0}

def main():
    p=argparse.ArgumentParser()
    for name in ("prereg","reference","native_trace","native_logits","output"):
        p.add_argument("--"+name.replace("_","-"),type=Path,required=True)
    a=p.parse_args()
    if blob(a.prereg)!=PREREG_BLOB:raise ValueError("PREREG_PIN_MISMATCH")
    contract=json.loads(a.prereg.read_text("utf-8"))
    discovery={x["fixture_id"]:x["token_ids"] for x in contract["fixtures"]
               if x["partition"]=="discovery"}
    if discovery!=FIXTURES:raise ValueError("DISCOVERY_IDS_CHANGED")
    ref=tensor_dict(read_jsonl(a.reference,60),"torch")
    native=tensor_dict(read_jsonl(a.native_trace,60),"native")
    output=read_jsonl(a.native_logits,2)
    if len(output)!=2:raise ValueError("NATIVE_ROWS_NOT_TWO")
    if a.output.exists():raise FileExistsError("AUDIT_ALREADY_EXISTS")
    all_rows={}
    for name,ids in FIXTURES.items():
        n=len(ids)
        row=next((r for r in output if r.get("fixture_id")==name),None)
        if row is None or row.get("token_ids")!=ids or row.get("arm_id")!="S1_F32_NO_FLASH":
            raise ValueError("NATIVE_FIXTURE_OR_ARM_MISMATCH")
        if row.get("kv_type")!="F32" or row.get("flash")!="DISABLED" or row.get("flash_nodes_observed")!=0:
            raise ValueError("WRONG_NATIVE_KV_FLASH_PATH")
        if len(row.get("logits",[]))!=2048 or not all(math.isfinite(x) for x in row["logits"]):
            raise ValueError("NATIVE_LOGITS_BAD")
        for stage in REQUIRED:
            if (name,stage) not in ref or (name,stage) not in native:
                raise ValueError("REQUIRED_STAGE_MISSING:"+name+":"+stage)
        summary=[]
        for stage in ORDER:
            key=name,stage
            if key not in ref or key not in native:continue
            e,g=align_values(stage,ref[key],native[key],n)
            summary.append({"stage":stage,**compare(e,g)})
        if not summary or summary[-1]["stage"]!="result_output":
            raise ValueError("OUTPUT_TRACE_MISSING")
        first=next((x["stage"] for x in summary if x["max_abs"]>SENSITIVITY),None)
        eref=ref[(name,"result_output")]["values"]
        actual=compare(eref,row["logits"])
        trace_consistency=compare(row["logits"],native[(name,"result_output")]["values"])
        if trace_consistency["max_abs"]>1e-6:
            raise ValueError("TENSOR_TRACE_VS_NATIVE_LOGITS_INCONSISTENT")
        all_rows[name]={"fixture_id":name,"n_tokens":n,
          "first_over_1e_minus_5":first,"stages":summary,
          "strict_max_abs":actual["max_abs"],
          "strict_pass":actual["max_abs"]<=STRICT_LIMIT,
          "native_top1_equal":max(range(2048),key=lambda k:row["logits"][k])==
                max(range(2048),key=lambda k:eref[k])}
    output_record={"schema":"ttm.t5.firstop.scoped_independent_signed_tensor_comparison.v1",
       "status":"PASS_TRACE_PROTOCOL_MEASURED_CAUSE_NOT_PROVEN",
       "frozen_prereg_blob":PREREG_BLOB,
       "input_sha256":{"P02_reference":sha(a.reference),
         "native_trace":sha(a.native_trace),"native_2_logits":sha(a.native_logits)},
       "sensitivity_diagnostic_only":SENSITIVITY,"strict_threshold":STRICT_LIMIT,
       "rows":all_rows,"actual_native_decodes":2,
       "confirmatory_not_accessed":True,"historical_8_32_not_replayed":True,
       "root_cause":"REQUIRES_TARGETED_ABLATION_AND_CONFIRMATORY_PASS",
       "no_training":True,"no_TEST":True}
    with a.output.open("x",encoding="utf-8",newline="\n") as f:
        json.dump(output_record,f,sort_keys=True,ensure_ascii=False,indent=2)
        f.write("\n")
    print(json.dumps({"status":output_record["status"],
       "first_op":{k:v["first_over_1e_minus_5"] for k,v in all_rows.items()},
       "strict":{k:v["strict_max_abs"] for k,v in all_rows.items()},
       "result_sha256":sha(a.output)},sort_keys=True))

if __name__=="__main__":
    try:main()
    except (ValueError,KeyError,TypeError,OSError) as e:
        print("FIRSTOP_AUDIT_FAIL_CLOSED:"+str(e),file=sys.stderr)
        raise SystemExit(2)

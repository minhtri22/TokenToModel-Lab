"""Synthetic-only B0/B1 Track B runner. All writes stay under repo/_tmp/."""
from __future__ import annotations
import argparse
from dataclasses import asdict
import json
import os
from pathlib import Path
import platform
import sys
import time
import torch
from . import scaffold as b


def roots(config_path, output_path):
    repo = Path.cwd().resolve(strict=True)
    config_path = b.safe_file(Path(config_path).absolute(), repo)
    raw_out = Path(output_path).absolute()
    if any(x.is_symlink() for x in [raw_out, *raw_out.parents] if x.is_relative_to(repo)):
        raise ValueError("OUTPUT_SYMLINK")
    out = raw_out.resolve(strict=False)
    allowed = repo/'_tmp'/'track_b_runs'
    if not out.is_relative_to(allowed) or out == allowed:
        raise ValueError("OUTPUT_OUTSIDE_REPO_SCOPED_TMP")
    if any(x.is_symlink() for x in [out, *out.parents] if x.is_relative_to(repo)):
        raise ValueError("OUTPUT_SYMLINK")
    return repo, config_path, out


def load_config(path):
    raw = Path(path).read_bytes()
    config = json.loads(raw)
    b.spec(config)
    return config, b.digest(b.canonical(config))


def load_pack(out, config):
    path = b.safe_file((out/'SYNTHETIC_PACK.json').absolute(), out)
    pack = json.loads(path.read_text('utf-8'))
    b.validate_pack(pack, config['context'], pack.get('data_sha256'))
    return pack


def prepare(out, config, config_hash):
    if out.exists():
        raise FileExistsError("ONE_SHOT_OUTPUT_DIR_ALREADY_EXISTS")
    out.mkdir(parents=True, exist_ok=False)
    pack = b.prepare(config)
    data_file_sha = b.write_new(out/'SYNTHETIC_PACK.json', b.canonical(pack))
    run = {"schema": "ttm.track_b.synthetic.run.v1", "science_executed": False,
           "checkpoint_weights_public": False, "tokenizer_kind": pack['tokenizer']['kind'],
           "config_sha256": config_hash, "pack_file_sha256": data_file_sha,
           "data_sha256": pack['data_sha256'], "p02_git_blob": b.P02_GIT_BLOB,
           "env": {"python": platform.python_version(), "torch": str(torch.__version__),
                   "platform": platform.platform()}, "status": "PREPARED_NO_SCIENCE"}
    b.write_new(out/'RUN_MANIFEST.json', b.canonical(run))
    return {"status": "PREPARED", "pack_sha256": data_file_sha, "windows": {s:len(pack['windows'][s]) for s in ('TRAIN','VAL')}}


def ready_checkpoint(out, step):
    ready_path = b.safe_file((out/f'READY_step_{step}.json').absolute(), out)
    ready = json.loads(ready_path.read_text('utf-8'))
    if ready != {"schema": "ttm.track_b.checkpoint.ready.v1", "step":step,
                 "checkpoint": f'checkpoint_step_{step}.pt', "sha256": ready.get('sha256')}:
        raise ValueError("BAD_CHECKPOINT_READY")
    b.require_sha(ready['sha256'])
    p = b.safe_file((out/ready['checkpoint']).absolute(), out)
    if b.file_hash(p) != ready['sha256']:
        raise ValueError("CHECKPOINT_SHA_MISMATCH")
    return p, ready['sha256']


def new_model_from_step(out, config, config_hash, pack, step):
    model, opt, scheduler, sampler = b.train_state(config)
    ckpt, sha = ready_checkpoint(out, step)
    loaded_step = b.load_training_checkpoint(ckpt, sha, model, opt, scheduler, sampler, config_hash, pack['data_sha256'])
    if loaded_step != step:
        raise ValueError("RESUME_STEP_MISMATCH")
    return model, opt, scheduler, sampler


def run_train(out, config, config_hash, until, resume_step, max_seconds):
    if not out.is_dir():
        raise ValueError("PREPARE_FIRST")
    pack = load_pack(out, config)
    run = json.loads((out/'RUN_MANIFEST.json').read_text('utf-8'))
    if run['config_sha256'] != config_hash or run['data_sha256'] != pack['data_sha256'] or b.file_hash(out/'SYNTHETIC_PACK.json') != run['pack_file_sha256']:
        raise ValueError("RUN_INPUT_PIN_MISMATCH")
    if type(until) is not int or not 1 <= until <= config['steps'] or type(resume_step) is not int or not 0 <= resume_step < until:
        raise ValueError("TRAIN_STEP_BOUNDS")
    if resume_step == 0:
        model, opt, scheduler, sampler = b.train_state(config)
    else:
        model, opt, scheduler, sampler = new_model_from_step(out, config, config_hash, pack, resume_step)
    if (out/f'READY_step_{until}.json').exists() or (out/f'TRAIN_RESULT_step_{until}.json').exists():
        raise FileExistsError("TRAIN_RESULT_ALREADY_EXISTS")
    start = time.perf_counter()
    first_params = [p.detach().clone() for p in model.parameters()]
    steps = []
    for step in range(resume_step+1, until+1):
        if time.perf_counter()-start > max_seconds:
            raise TimeoutError("SYNTHETIC_TIME_CAP")
        metrics = b.train_step(model,opt,scheduler,sampler,pack,config)
        steps.append({"step":step, **metrics})
    delta = max(float((p.detach()-old).abs().max().item()) for p,old in zip(model.parameters(),first_params))
    cp_sha = b.save_training_checkpoint(out/f'checkpoint_step_{until}.pt',
            b.checkpoint_payload(model,opt,scheduler,sampler,until,config_hash,pack['data_sha256']))
    b.write_new(out/f'READY_step_{until}.json', b.canonical({"schema":"ttm.track_b.checkpoint.ready.v1",
                    "step":until,"checkpoint":f'checkpoint_step_{until}.pt',"sha256":cp_sha}))
    result = {"status":"SYNTHETIC_ENGINEERING_ONLY", "from_step":resume_step, "to_step":until,
              "steps": steps, "max_parameter_delta":delta,
              "scored_target_tokens_processed":sum(s['valid_targets'] for s in steps),
              "train_unique_target_tokens":sum(r['target_tokens'] for r in pack['splits']['TRAIN']),
              "checkpoint_sha256":cp_sha,
              "wall_seconds":time.perf_counter()-start, "scientific_meaning":"NONE"}
    result['train_target_reuse_factor'] = result['scored_target_tokens_processed']/result['train_unique_target_tokens']
    b.write_new(out/f'TRAIN_RESULT_step_{until}.json',b.canonical(result))
    return {k:v for k,v in result.items() if k!='steps'}


def finished_model(out,config,config_hash,step):
    pack=load_pack(out,config)
    model,_,_,_ = new_model_from_step(out,config,config_hash,pack,step)
    return model,pack


def main(argv=None):
    ap=argparse.ArgumentParser()
    ap.add_argument('operation',choices=['prepare','train','evaluate','sample'])
    ap.add_argument('--config',default='configs/ttm/track_b_synthetic_smoke.json')
    ap.add_argument('--out',default='_tmp/track_b_runs/smoke')
    ap.add_argument('--stop-after',type=int)
    ap.add_argument('--resume-from-step',type=int,default=0)
    ap.add_argument('--checkpoint-step',type=int)
    ap.add_argument('--max-seconds',type=int,default=120)
    args=ap.parse_args(argv)
    if sys.version_info[:2] != (3,12):
        # Development fallback permitted; never label a non-3.12 run Windows gate PASS.
        print('WARNING_PYTHON312_NOT_VERIFIED='+platform.python_version(),file=sys.stderr)
    torch.set_num_threads(2)
    _,config_path,out = roots(args.config,args.out)
    config,config_hash = load_config(config_path)
    if args.operation == 'prepare':
        result=prepare(out,config,config_hash)
    elif args.operation == 'train':
        if args.max_seconds <= 0 or args.max_seconds > 600:
            raise ValueError('TIME_CAP_MAX_600_SECONDS')
        result=run_train(out,config,config_hash,args.stop_after or config['steps'],args.resume_from_step,args.max_seconds)
    else:
        step=args.checkpoint_step or config['steps']
        if step < 1 or step > config['steps']:
            raise ValueError('CHECKPOINT_STEP_INVALID')
        model,pack=finished_model(out,config,config_hash,step)
        if args.operation=='evaluate':
            result=b.evaluate(model,pack)
            b.write_new(out/f'EVAL_RESULT_step_{step}.json',b.canonical(result))
        else:
            result={"status":"SYNTHETIC_SAMPLE_ONLY","seed":13,"top_k":1,
                    "tokens":b.sample(model,[65,97],max_new=6,seed=13,top_k=1),
                    "science_claim":"NONE"}
            b.write_new(out/f'SAMPLE_RESULT_step_{step}.json',b.canonical(result))
    print(json.dumps(result,sort_keys=True,ensure_ascii=False))

if __name__=='__main__':
    main()

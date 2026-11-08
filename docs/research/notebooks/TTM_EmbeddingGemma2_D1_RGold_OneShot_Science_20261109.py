"""TTM EmbeddingGemma2 D1 — frozen Qwen R_gold screening, one scientific RunID.
The act of running this owner-side script from Google Colab is the science execution decision.
Only R_gold; it never runs R1/R2/R3, does not use EmbeddingGemma, and does not train.
"""
import datetime
import hashlib
import importlib.metadata
import json
import math
import os
import pathlib
import random
import shutil
import sys
import time
import unicodedata
import urllib.request

import numpy as np
import torch
from huggingface_hub import snapshot_download
from transformers import AutoModelForCausalLM, AutoTokenizer

# Single frozen science run (do not change after observing any science result).
RUN_ID = 'ttm_embedgemma2_d1_rgold_one_shot_20261109_v1'
PROJECT = 'minhtri22/TokenToModel-Lab'
FIXTURE_GIT_COMMIT = 'b10deb62567571dc4aa68e5aad9fe06b55d1e23b'
FIXTURE_PATH = 'docs/research/fixtures/TTM_EMBEDDINGGEMMA2_D1_R_GOLD_60_GROUPS_LOCK_CANDIDATE_20261108.jsonl'
FIXTURE_SHA256 = '0215719de94f86a4f2b7a48959ca81343014c127e74799f737901a57b33f341a'
FIXTURE_URL = f'https://raw.githubusercontent.com/{PROJECT}/{FIXTURE_GIT_COMMIT}/{FIXTURE_PATH}'
QWEN_REPO = 'Qwen/Qwen2.5-0.5B-Instruct'
QWEN_REVISION = '7ae557604adf67be50417f59c2c2f167def9a775'
SOURCE_SHA256 = os.environ.get('TTM_RGOLD_SCIENCE_SCRIPT_SHA256', 'UNPINNED')
V3 = 'ttm_embedgemma2_d1_t4_preflight_st610_once_v1'
QWEN_FOLLOW = 'ttm_embedgemma2_d1_t4_qwen_tokenizer_followup_once_v1'
ANCESTOR = pathlib.Path('/content/drive/MyDrive/TTM_EmbeddingGemma2_D1_Preflight')
SCIENCE_BASE = pathlib.Path('/content/drive/MyDrive/TTM_EmbeddingGemma2_D1_Science')
OUT = SCIENCE_BASE / RUN_ID
MODEL_DIR = SCIENCE_BASE / 'Qwen2.5-0.5B-Instruct_pinned'
LOCAL_MODEL_DIR = pathlib.Path('/content/ttm_embeddinggemma2_d1_science_qwen_local')
V3_QWEN_SNAPSHOT = (pathlib.Path('/content/ttm_embeddinggemma2_d1_preflight_st610_v1/hf_cache') /
    'models--Qwen--Qwen2.5-0.5B-Instruct' / 'snapshots' / QWEN_REVISION)
CLAIM = OUT / 'CLAIM.json'
RESULT = OUT / 'RESULT.json'
PROGRESS = OUT / 'groups'
LIMIT_SECONDS = 1800
MAX_NEW_STORAGE = 8 * 1024**3
MAX_PLANNED_DOWNLOAD = 5 * 1024**3
MIN_FREE_RAM = 3 * 1024**3
MIN_FREE_VRAM = 3 * 1024**3
MIN_FREE_LOCAL_DISK = 3 * 1024**3
BOOTSTRAP_REPLICATES = 10000
BOOTSTRAP_SEED = 20261108
MAX_NEW_TOKENS = 24
MODEL_FILES = {
  'config.json': (659, '18e18afcaccafade98daf13a54092927904649e1dd4eba8299ab717d5d94ff45'),
  'generation_config.json': (242, 'e558847a8b4402616f1273797b015104dc266fe4b520056fca88823ba8f8ebe6'),
  'model.safetensors': (988097824, 'fdf756fa7fcbe7404d5c60e26bff1a0c8b8aa1f72ced49e7dd0210fe288fb7fe'),
  'tokenizer.json': (7031645, 'c0382117ea329cdf097041132f6d735924b697924d6f6fc3945713e96ce87539'),
  'tokenizer_config.json': (7305, '5b5d4f65d0acd3b2d56a35b56d374a36cbc1c8fa5cf3b3febbbfabf22f359583'),
  'merges.txt': (1671839, '599bab54075088774b1733fde865d5bd747cbcc7a547c5bc12610e874e26f5e3'),
  'vocab.json': (2776833, 'ca10d7e9fb3ed18575dd1e277a2579c16d108e32f27439684afa0e10b1440910'),
  'LICENSE': (11343, '832dd9e00a68dd83b3c3fb9f5588dad7dcf337a0db50f7d9483f310cd292e92e'),
}
ORIGINAL_RECEIPTS = {
 V3 + '_CLAIM.json': '2ce14ab0c890a53042862c2b376ab12e2927c15ae1c1d1d3e9075f386b4a5999',
 V3 + '_RESULT.json': 'ce693326af246fdf2a3806427b46d89ce05e944a4c99e442b24004677e892427',
 QWEN_FOLLOW + '_CLAIM.json': '70d36ee614990697eda18264c0c130704197fe9b28b13343cf1970fe9468b55d',
 QWEN_FOLLOW + '_RESULT.json': 'b9f859bc639bd953893b3443b437f23182231e3297149c3cbaaa3bad2b84b2cd',
}
SYSTEM = (
    'Answer questions using only evidence explicitly provided. '
    'Reply with only the requested short value. '
    'If the evidence does not specify the requested value, reply UNKNOWN. '
    'Do not explain your answer.'
)
PROMPT_PREFIX = 'Evidence:\n'
PROMPT_MIDDLE = '\n\nQuestion:\n'
PROMPT_SUFFIX = '\nAnswer:'
SPLITS = ('R0', 'R_gold', 'R_wrong')


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256_file(path):
    h = hashlib.sha256()
    with pathlib.Path(path).open('rb') as fp:
        for b in iter(lambda: fp.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def stamp():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def write_exclusive_json(path, obj):
    path = pathlib.Path(path)
    fd = os.open(str(path), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(fd, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())


def canonical_json_sha(obj):
    return sha256_bytes(json.dumps(obj, sort_keys=True, ensure_ascii=False,
                                   separators=(',', ':')).encode('utf-8'))


def normalize_answer(s):
    return unicodedata.normalize('NFKC', s).casefold().strip().rstrip('.!?').strip()


def bootstrap_group_ci(deltas, replicates=BOOTSTRAP_REPLICATES, seed=BOOTSTRAP_SEED):
    x = np.asarray(deltas, dtype=np.float64)
    assert x.shape == (48,) and np.all(np.isfinite(x))
    gen = np.random.default_rng(seed)
    indices = gen.integers(0, x.size, (replicates, x.size))
    means = x[indices].mean(axis=1)
    return (float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5)))


def validate_fixture(rows):
    if len(rows) != 60:
        raise ValueError('R_gold group count must equal 60')
    seen_group, seen_question = set(), set()
    pos, neg = 0, 0
    for row in rows:
        gid = row['group_id']
        if gid in seen_group or len(row['questions']) != 2:
            raise ValueError('duplicate group or invalid question count')
        seen_group.add(gid)
        expected_cohort = 'answerable' if gid.startswith('RG-P-') else 'unanswerable'
        if row['cohort'] != expected_cohort:
            raise ValueError('cohort mismatch')
        if row.get('science_consumed') is not False or row.get('schema') != 'ttm.rgold.group.v1':
            raise ValueError('fixture provenance/schema mismatch')
        if not row.get('gold_evidence') or not row.get('wrong_evidence'):
            raise ValueError('evidence missing')
        for q in row['questions']:
            qid = q['question_id']
            if qid in seen_question or not q['text'] or q['target_answer'] != row['gold_answer']:
                raise ValueError('question/answer mismatch')
            seen_question.add(qid)
        if expected_cohort == 'answerable':
            pos += 1
            if row['gold_answer'].casefold() not in row['gold_evidence'].casefold():
                raise ValueError('gold evidence does not contain annotated answer')
            if row['gold_answer'].casefold() in row['wrong_evidence'].casefold():
                raise ValueError('wrong evidence leaks annotated answer')
        else:
            neg += 1
            if row['gold_answer'] != 'UNKNOWN':
                raise ValueError('negative group missing UNKNOWN')
    if (pos, neg, len(seen_question)) != (48, 12, 120):
        raise ValueError('cohort or question IDs wrong')
    return {'positive_groups': pos, 'negative_groups': neg, 'questions': len(seen_question)}


def model_prompt(question, evidence):
    # Does not contain the target answer except when it legitimately appears inside R_gold evidence.
    message = PROMPT_PREFIX + (evidence if evidence is not None else '(none)')
    message += PROMPT_MIDDLE + question + PROMPT_SUFFIX
    return [{'role': 'system', 'content': SYSTEM}, {'role': 'user', 'content': message}]


def flat_token_ids(value):
    if isinstance(value, dict) or hasattr(value, 'keys'):
        value = value['input_ids']
    if hasattr(value, 'tolist'):
        value = value.tolist()
    if isinstance(value, tuple):
        value = list(value)
    if isinstance(value, list) and len(value) == 1 and isinstance(value[0], (list, tuple)):
        value = list(value[0])
    if not isinstance(value, list) or not value or any(type(i) is not int for i in value):
        raise ValueError('unsupported Transformers 5 token-id response shape')
    return value


def evaluate_preclaim_tokenization(rows, tok, model_config):
    model_vocab = int(model_config['vocab_size'])
    context_limit = int(model_config['max_position_embeddings'])
    end_id = tok.convert_tokens_to_ids('<|im_end|>')
    if not isinstance(end_id, int) or end_id < 0 or end_id >= model_vocab:
        raise ValueError('invalid Qwen assistant end token')
    max_length = 0
    for row in rows:
        for q in row['questions']:
            answer = flat_token_ids(tok.encode(q['target_answer'], add_special_tokens=False))
            for arm in (SPLITS if row['cohort'] == 'answerable' else ('R_gold',)):
                evidence = {'R0': None, 'R_gold': row['gold_evidence'],
                            'R_wrong': row['wrong_evidence']}[arm]
                prefix = flat_token_ids(tok.apply_chat_template(
                    model_prompt(q['text'], evidence), tokenize=True,
                    add_generation_prompt=True, return_dict=False))
                if any(t < 0 or t >= model_vocab for t in prefix + answer):
                    raise ValueError('token ID outside model embedding')
                required = len(prefix) + len(answer) + 1 + MAX_NEW_TOKENS
                if required > context_limit:
                    raise ValueError('context overflow: stop, do not drop group')
                max_length = max(max_length, required)
    return {'max_required_context_with_generation': max_length,
            'model_context_limit': context_limit, 'im_end_id': end_id}


def checked_time(start):
    if time.monotonic() - start > LIMIT_SECONDS:
        raise TimeoutError('30-minute total budget exceeded; stop without changing cohort')


def masked_answer_nll_from_logits(logits, labels, expected_scored):
    # Unit-testable core: last PROMPT logit predicts first ANSWER token.
    shift = logits[:, :-1, :].float().contiguous()
    targets = labels[:, 1:].contiguous()
    total = torch.nn.functional.cross_entropy(
        shift.view(-1, shift.shape[-1]), targets.view(-1),
        ignore_index=-100, reduction='sum')
    n_target = int((targets != -100).sum().item())
    if n_target != expected_scored or n_target < 2:
        raise AssertionError('teacher-forced answer/EOS mask mismatch')
    nll = float(total.item() / n_target)
    if not math.isfinite(nll):
        raise FloatingPointError('nonfinite answer+EOS loss')
    return {'nll': nll, 'answer_token_count_including_eos': n_target}


def answer_nll(model, tok, question, evidence, target, end_id):
    prefix = flat_token_ids(tok.apply_chat_template(
        model_prompt(question, evidence), tokenize=True,
        add_generation_prompt=True, return_dict=False))
    answer = flat_token_ids(tok.encode(target, add_special_tokens=False))
    ids = torch.tensor([prefix + answer + [end_id]], dtype=torch.long, device='cuda')
    labels = ids.clone()
    labels[:, :len(prefix)] = -100
    with torch.inference_mode():
        logits = model(input_ids=ids, use_cache=False).logits
        return masked_answer_nll_from_logits(logits, labels, len(answer) + 1)


def greedy_text(model, tok, question, evidence, end_ids):
    prefix = flat_token_ids(tok.apply_chat_template(
        model_prompt(question, evidence), tokenize=True,
        add_generation_prompt=True, return_dict=False))
    prefix_tensor = torch.tensor([prefix], dtype=torch.long, device='cuda')
    ids = model.generate(prefix_tensor, max_new_tokens=MAX_NEW_TOKENS,
                         do_sample=False, num_beams=1,
                         eos_token_id=list(end_ids),
                         pad_token_id=tok.eos_token_id,
                         return_dict_in_generate=False)
    generated = ids[0, len(prefix):].tolist()
    while generated and generated[-1] in end_ids:
        generated.pop()
    return tok.decode(generated, skip_special_tokens=True)


def aggregate_results(records):
    if len(records) != 60:
        raise ValueError('not all 60 groups scored')
    answerable = [r for r in records if r['cohort'] == 'answerable']
    negative = [r for r in records if r['cohort'] == 'unanswerable']
    if len(answerable) != 48 or len(negative) != 12:
        raise ValueError('missing cohort')
    group_deltas = [float(np.mean([q['nll']['R0']['nll'] - q['nll']['R_gold']['nll']
                                  for q in r['questions']])) for r in answerable]
    wrong_group = [float(np.mean([q['nll']['R_wrong']['nll'] - q['nll']['R_gold']['nll']
                                 for q in r['questions']])) for r in answerable]
    pos_questions = [q for r in answerable for q in r['questions']]
    neg_questions = [q for r in negative for q in r['questions']]
    assert len(pos_questions) == 96 and len(neg_questions) == 24
    em_gold = float(np.mean([q['em']['R_gold'] for q in pos_questions]))
    em_r0 = float(np.mean([q['em']['R0'] for q in pos_questions]))
    nonexact_neg = sum(q['prediction_normalized'] != 'unknown' for q in neg_questions)
    negative_groups_with_nonexact = sum(any(q['prediction_normalized'] != 'unknown'
                                           for q in r['questions']) for r in negative)
    ci_low, ci_high = bootstrap_group_ci(group_deltas)
    primary_pass = ci_low > 0.10
    em_pass = em_gold >= 0.60 and em_gold - em_r0 >= 0.10
    wrong_pass = float(np.mean(wrong_group)) > 0.0
    # A nonexact abstention may be safe. Do not silently classify it as a factual hallucination.
    if not (primary_pass and em_pass and wrong_pass):
        verdict = 'MODEL_CAPABILITY_GAP_SCOPED_R_GOLD'
    elif nonexact_neg > 6:
        verdict = 'INCONCLUSIVE_NEGATIVE_GUARD_REQUIRES_BLIND_FACTUAL_RESPONSE_REVIEW'
    else:
        verdict = 'RGOLD_SCREEN_PASS_CONSERVATIVE_NONEXACT_GUARD'
    return {'verdict_unadjudicated': verdict,
            'positive_groups': 48, 'positive_questions': 96,
            'negative_groups': 12, 'negative_questions': 24,
            'mean_group_nll_improvement': float(np.mean(group_deltas)),
            'primary_95pct_group_bootstrap_ci': [ci_low, ci_high],
            'primary_ci_lower_gt_0p10': primary_pass,
            'exact_match_gold': em_gold, 'exact_match_r0': em_r0,
            'exact_match_delta': em_gold - em_r0, 'em_guards_pass': em_pass,
            'mean_group_wrong_minus_gold_nll': float(np.mean(wrong_group)),
            'wrong_evidence_guard_pass': wrong_pass,
            'negative_nonexact_UNKNOWN_count_conservative': nonexact_neg,
            'negative_groups_with_nonexact': negative_groups_with_nonexact,
            'negative_conservative_guard_pass': nonexact_neg <= 6,
            'negative_factual_response_classification': 'REQUIRES_INDEPENDENT_REVIEW_IF_NONEXACT_GT_6',
            'bootstrap_replicates': BOOTSTRAP_REPLICATES, 'bootstrap_seed': BOOTSTRAP_SEED,
            'strict_group_count': 60}


def main():
    start = time.monotonic()
    print('TTM_RGOLD_SCIENCE_SCOPE=R_GOLD_ONLY_NO_R1_R2_R3_NO_TRAIN')
    if SOURCE_SHA256 == 'UNPINNED':
        raise RuntimeError('Bootstrap must pin SHA256 of runner; refuse unpinned code')
    if not sys.platform.startswith('linux') or not pathlib.Path('/content').is_dir():
        raise EnvironmentError('Execute only on Google Colab Linux runtime')
    import google.colab  # noqa: F401
    if not torch.cuda.is_available() or torch.cuda.get_device_name(0) != 'Tesla T4':
        raise EnvironmentError('Requires Tesla T4; do not use other paid GPU or local machine')
    if importlib.metadata.version('transformers') != '5.22.1':
        raise RuntimeError('Requires transformers==5.22.1, install/restart before science')
    if shutil.disk_usage('/content').free < MIN_FREE_LOCAL_DISK:
        raise RuntimeError('Insufficient local free disk')
    if torch.cuda.mem_get_info()[0] < MIN_FREE_VRAM:
        raise RuntimeError('Insufficient free T4 VRAM')
    try:
        import psutil
        if psutil.virtual_memory().available < MIN_FREE_RAM:
            raise RuntimeError('Insufficient free system RAM')
    except ImportError:
        raise RuntimeError('Missing psutil; setup before science')
    from google.colab import drive
    drive.mount('/content/drive')
    if not ANCESTOR.is_dir():
        raise RuntimeError('Original technical evidence folder missing')
    for name, expected in ORIGINAL_RECEIPTS.items():
        file = ANCESTOR / name
        if not file.is_file() or sha256_file(file) != expected:
            raise RuntimeError('Original technical receipt missing/changed: ' + name)
    qwen_result = json.loads((ANCESTOR / (QWEN_FOLLOW + '_RESULT.json')).read_text('utf-8'))
    v3_result = json.loads((ANCESTOR / (V3 + '_RESULT.json')).read_text('utf-8'))
    if qwen_result['status'] != 'PASS_TARGETED_QWEN_TECHNICAL_ONLY_NO_SCIENCE' or \
       v3_result['embedding_smoke']['finite'] is not True or \
       v3_result['squad_validation']['sha256'] != v3_result['squad_validation']['expected_sha256']:
        raise RuntimeError('Technical-core evidence not aligned with PASS_SCOPED')
    checked_time(start)
    fixture_bytes = urllib.request.urlopen(FIXTURE_URL, timeout=30).read()
    if sha256_bytes(fixture_bytes) != FIXTURE_SHA256:
        raise RuntimeError('Frozen R_gold fixture mismatch; STOP before science claim')
    rows = [json.loads(x) for x in fixture_bytes.decode('utf-8').splitlines() if x.strip()]
    fixture_info = validate_fixture(rows)
    if sum(size for size, _ in MODEL_FILES.values()) > MAX_PLANNED_DOWNLOAD:
        raise RuntimeError('Qwen planned download exceeds 5 GiB allowance')
    SCIENCE_BASE.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    PROGRESS.mkdir(parents=True, exist_ok=True)
    if RESULT.exists():
        raise FileExistsError('R_gold one-shot science already terminal; no rerun')
    checked_time(start)
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    if not all((MODEL_DIR / name).is_file() and sha256_file(MODEL_DIR / name) == digest
               for name, (_, digest) in MODEL_FILES.items()):
        # Reuse an exact, already-verified V3 runtime cache if still present.
        if all((V3_QWEN_SNAPSHOT / name).is_file() and
               sha256_file(V3_QWEN_SNAPSHOT / name) == digest
               for name, (_, digest) in MODEL_FILES.items()):
            for name in MODEL_FILES:
                shutil.copy2(V3_QWEN_SNAPSHOT / name, MODEL_DIR / name)
        else:
            snapshot_download(repo_id=QWEN_REPO, revision=QWEN_REVISION,
                              local_dir=str(MODEL_DIR), allow_patterns=list(MODEL_FILES),
                              max_workers=3)
    for name, (size, digest) in MODEL_FILES.items():
        path = MODEL_DIR / name
        if not path.is_file() or path.stat().st_size != size or sha256_file(path) != digest:
            raise RuntimeError('Qwen model weight/tokenizer SHA mismatch: ' + name)
    local_size = sum(f.stat().st_size for f in SCIENCE_BASE.rglob('*') if f.is_file())
    if local_size > MAX_NEW_STORAGE:
        raise RuntimeError('R_gold project Drive storage over 8 GiB before claim')
    checked_time(start)
    # Drive is durable evidence storage, but safetensors memory-mapping on FUSE can be unreliable.
    # Copy exact pinned bytes to ephemeral /content before loading; never change Drive bytes.
    LOCAL_MODEL_DIR.mkdir(parents=True, exist_ok=True)
    for name, (size, digest) in MODEL_FILES.items():
        dest = LOCAL_MODEL_DIR / name
        if not dest.is_file() or dest.stat().st_size != size or sha256_file(dest) != digest:
            shutil.copy2(MODEL_DIR / name, dest)
        if dest.stat().st_size != size or sha256_file(dest) != digest:
            raise RuntimeError('Local pinned Qwen copy mismatch before claim: ' + name)
    checked_time(start)
    # Exactly pinned tokenization/prompt and all 60 groups validated BEFORE scientific inference.
    tok = AutoTokenizer.from_pretrained(str(LOCAL_MODEL_DIR), local_files_only=True)
    model_config = json.loads((LOCAL_MODEL_DIR / 'config.json').read_text('utf-8'))
    token_contract = evaluate_preclaim_tokenization(rows, tok, model_config)
    # No model inference has occurred: model loading is technical readiness, then claim before scoring.
    model = AutoModelForCausalLM.from_pretrained(str(LOCAL_MODEL_DIR), local_files_only=True,
                                                  dtype=torch.float16).to('cuda').eval()
    for param in model.parameters():
        param.requires_grad_(False)
    torch.manual_seed(20261108)
    torch.backends.cuda.matmul.allow_tf32 = False
    checked_time(start)
    config = {
      'run_id': RUN_ID, 'source_sha256': SOURCE_SHA256,
      'qwen_revision': QWEN_REVISION, 'fixture_sha256': FIXTURE_SHA256,
      'fixture_commit': FIXTURE_GIT_COMMIT, 'system_prompt': SYSTEM,
      'prompt_prefix': PROMPT_PREFIX, 'prompt_middle': PROMPT_MIDDLE,
      'prompt_suffix': PROMPT_SUFFIX,
      'scoring': 'target_answer_tokens_plus_im_end; EOS included in denominator; shift causal',
      'generation': {'do_sample': False, 'max_new_tokens': MAX_NEW_TOKENS},
      'bootstrap': {'B': BOOTSTRAP_REPLICATES, 'seed': BOOTSTRAP_SEED, 'unit': 'group'},
      'gates': {'CI_lower_gt': 0.10, 'EM_gold_at_least': 0.60,
                'EM_delta_at_least': 0.10, 'wrong_nll_positive': True,
                'negative_nonexact_count_max_conservative': 6},
    }
    config_sha = canonical_json_sha(config)
    prior_groups = sorted(PROGRESS.glob('*.json'))
    if CLAIM.exists():
        old = json.loads(CLAIM.read_text('utf-8'))
        if old.get('run_id') != RUN_ID or old.get('config_sha256') != config_sha:
            raise RuntimeError('Existing science claim differs; no rerun or parameter change')
        print('TTM_RGOLD_RESUME_SAME_RUN=YES; completed groups:', len(prior_groups))
    else:
        if prior_groups:
            raise RuntimeError('Found group outputs without original CLAIM')
        write_exclusive_json(CLAIM, {'run_id': RUN_ID, 'science_started_utc': stamp(),
                                     'config_sha256': config_sha, 'protocol': config,
                                     'scope': 'R_gold one-shot scientific screening ONLY',
                                     'parent_v3_result_sha256': ORIGINAL_RECEIPTS[V3 + '_RESULT.json'],
                                     'parent_qwen_result_sha256': ORIGINAL_RECEIPTS[QWEN_FOLLOW + '_RESULT.json']})
    print('TTM_RGOLD_SCIENCE_CLAIM=CONSUMED', 'run=', RUN_ID)
    receipt = {'schema': 'ttm.embeddinggemma2.d1.rgold.science.v1', 'run_id': RUN_ID,
               'fixture_sha256': FIXTURE_SHA256, 'source_sha256': SOURCE_SHA256,
               'config_sha256': config_sha, 'scope': 'R_gold only; no R1/R2/R3',
               'science_executed': True, 'model_training': False,
               'retrieval_evaluation': False, 'test_scored': False,
               'source_rights': 'project-authored fictitious screening; rights and human review caveat',
               'gpu': torch.cuda.get_device_name(0),
               'torch': torch.__version__,
               'transformers': importlib.metadata.version('transformers'),
               'fixture_info': fixture_info, 'token_contract': token_contract,
               'started_utc': stamp(), 'status': 'RUNNING'}
    end_ids = {token_contract['im_end_id']}
    if tok.eos_token_id is not None:
        end_ids.add(tok.eos_token_id)
    try:
        for row in rows:
            checked_time(start)
            gid = row['group_id']
            output_file = PROGRESS / (gid + '.json')
            if output_file.exists():
                old = json.loads(output_file.read_text('utf-8'))
                if old.get('group_id') != gid or old.get('config_sha256') != config_sha:
                    raise RuntimeError('Persisted group incompatible with frozen run')
                continue
            result = {'group_id': gid, 'cohort': row['cohort'],
                      'config_sha256': config_sha, 'questions': [], 'completed_utc': None}
            for q in row['questions']:
                checked_time(start)
                evidence = {'R0': None, 'R_gold': row['gold_evidence'],
                            'R_wrong': row['wrong_evidence']}
                item = {'question_id': q['question_id'], 'target_answer': q['target_answer']}
                if row['cohort'] == 'answerable':
                    item['nll'] = {arm: answer_nll(model, tok, q['text'], evidence[arm],
                                                   q['target_answer'], token_contract['im_end_id'])
                                   for arm in SPLITS}
                    texts = {arm: greedy_text(model, tok, q['text'], evidence[arm], end_ids)
                             for arm in ('R0', 'R_gold')}
                    item['predictions'] = texts
                    item['em'] = {arm: normalize_answer(pred) == normalize_answer(q['target_answer'])
                                  for arm, pred in texts.items()}
                else:
                    pred = greedy_text(model, tok, q['text'], evidence['R_gold'], end_ids)
                    item['prediction'] = pred
                    item['prediction_normalized'] = normalize_answer(pred)
                result['questions'].append(item)
            result['completed_utc'] = stamp()
            write_exclusive_json(output_file, result)
            print('TTM_RGOLD_GROUP_SAVED=' + gid, flush=True)
            storage = sum(f.stat().st_size for f in SCIENCE_BASE.rglob('*') if f.is_file())
            if storage > MAX_NEW_STORAGE:
                raise RuntimeError('Drive storage 8GiB limit exceeded')
        files = sorted(PROGRESS.glob('RG-*.json'))
        if len(files) != 60:
            raise RuntimeError('Unexpected number of group files')
        records = [json.loads(p.read_text('utf-8')) for p in files]
        metrics = aggregate_results(records)
        receipt['metrics'] = metrics
        receipt['status'] = 'COMPLETED_UNADJUDICATED_' + metrics['verdict_unadjudicated']
        receipt['groups_saved'] = 60
        receipt['per_group_sha256'] = {p.name: sha256_file(p) for p in files}
    except BaseException as ex:
        receipt['status'] = 'INCONCLUSIVE_ABORTED_OR_INCOMPLETE'
        receipt['error'] = {'type': type(ex).__name__, 'message': str(ex)[:500]}
        receipt['groups_saved'] = len(list(PROGRESS.glob('RG-*.json')))
    finally:
        receipt['ended_utc'] = stamp()
        receipt['elapsed_seconds'] = round(time.monotonic() - start, 3)
        receipt['max_gpu_memory_allocated_bytes'] = int(torch.cuda.max_memory_allocated())
        receipt['project_persistent_bytes'] = sum(f.stat().st_size for f in SCIENCE_BASE.rglob('*') if f.is_file())
        # Terminal evidence written only once; no overwrite even when run failed.
        write_exclusive_json(RESULT, receipt)
        print('TTM_RGOLD_SCIENCE_STATUS=' + receipt['status'])
        print('TTM_RGOLD_SCIENCE_RESULT=' + str(RESULT))


if __name__ == '__main__':
    main()

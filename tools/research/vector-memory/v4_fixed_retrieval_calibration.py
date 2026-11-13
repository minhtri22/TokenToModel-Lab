#!/usr/bin/env python3
"""V4 source-only retrieval scoring and CAL thresholding; never runs real CAL/PROBE on import.

Only question and 32-card public index may enter score methods. This file does
not read source labels, gold answer, private Reader, V2/V3 PROBE or sealed TEST.
No network on model load. CAL labels are consumed only by calibration/scorer.
"""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence
import hashlib
import math
import os
import re
import unicodedata

UPSTREAM_MODEL_ID = "BAAI/bge-small-en-v1.5"
UPSTREAM_REVISION = "5c38ec7c405ec4b44b94cc5a9bb96e735b38267a"
EXPECTED_SAFETENSORS_SHA256 = "3c9f31665447c8911517620762200d2245a2518d6e7208acc78cd9db317e21ad"
MODEL_LICENSE = "MIT"
METHODS = ("R_BM25_LEXICAL", "R_CHAR3GRAM_LEXICAL",
           "R_T1_MEAN_COSINE", "R_V4_BGE_SMALL_FROZEN")
CAL_STRATA = ("P0_SEEN_WIRING_CONTROL", "P1_UNSEEN_NL_PARAPHRASE",
    "P2_CROSS_SENTENCE_RELATION", "P3_PROVENANCE_TEMPORAL",
    "N0_RELATION_UNDERSPECIFIED", "N1_CONFLICTING_EVIDENCE",
    "N2_FALSE_PREMISE_NO_SUPPORT", "N3_NEAR_DUPLICATE_AMBIGUOUS")
CAL_PRIMARY = frozenset(CAL_STRATA[1:4])
CAL_NEGATIVE = frozenset(CAL_STRATA[4:])
CAL_GRID = tuple(round(i / 200, 3) for i in range(1, 201))
ALLOWED_CARD_FIELDS = frozenset(("key", "source_id", "retrieval_text", "timestamp"))
REQUIRED_CARD_FIELDS = frozenset(("key", "source_id", "retrieval_text"))
WORD_RE = re.compile(r"(?u)\b\w+\b")
SOURCE_CODE_ONLY = True


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as file:
        for chunk in iter(lambda: file.read(1048576), b""):
            h.update(chunk)
    return h.hexdigest()


def normalize(value: str) -> str:
    if not isinstance(value, str):
        raise ValueError("NON_STRING_TEXT")
    return " ".join(unicodedata.normalize("NFKC", value).casefold().split())


def public_input(question: str, public_index: Sequence[Mapping]) -> tuple[str, list[dict]]:
    """Reject any private fields (gold, answer, value, outcome, stratum, case_id)."""
    if not isinstance(question, str) or not 1 <= len(question) <= 1024:
        raise ValueError("BAD_PUBLIC_QUERY")
    if not isinstance(public_index, (list, tuple)) or len(public_index) != 32:
        raise ValueError("BANK_NOT_32")
    out = []
    for card in public_index:
        if not isinstance(card, Mapping):
            raise ValueError("BAD_PUBLIC_CARD")
        names = set(card)
        if not REQUIRED_CARD_FIELDS.issubset(names) or not names.issubset(ALLOWED_CARD_FIELDS):
            raise ValueError("PUBLIC_INDEX_PRIVATE_FIELD_OR_MISSING_REQUIRED")
        if any(not isinstance(card[k], str) or not card[k] for k in REQUIRED_CARD_FIELDS):
            raise ValueError("EMPTY_PUBLIC_FIELD")
        if len(card["retrieval_text"]) > 1024:
            raise ValueError("CARD_TOO_LONG")
        if "timestamp" in card and (not isinstance(card["timestamp"], str) or not card["timestamp"]):
            raise ValueError("BAD_PUBLIC_TIMESTAMP")
        out.append(dict(card))
    if len({c["key"] for c in out}) != 32:
        raise ValueError("PUBLIC_INDEX_DUPLICATE_KEY")
    return question, out


def words(text: str) -> list[str]:
    return WORD_RE.findall(normalize(text))


def bm25_scores(question: str, public_index: Sequence[Mapping]) -> list[float]:
    """Self-contained BM25 with IDF scoped to the SAME 32 public cards."""
    q, cards = public_input(question, public_index)
    docs = [words(c["retrieval_text"]) for c in cards]
    n = len(docs)
    avgdl = max(1.0, sum(len(d) for d in docs) / n)
    df = Counter()
    for doc in docs:
        df.update(set(doc))
    k1, b = 1.2, 0.75
    scores = []
    for doc in docs:
        tf = Counter(doc)
        length = len(doc)
        score = 0.0
        for term in set(words(q)):
            if term not in df:
                continue
            idf = math.log(1.0 + (n - df[term] + 0.5) / (df[term] + 0.5))
            freq = tf.get(term, 0)
            if freq:
                score += idf * (freq * (k1 + 1)) / (
                    freq + k1 * (1 - b + b * length / avgdl))
        scores.append(float(score))
    return scores


def character_ngrams(text: str, n: int = 3) -> Counter:
    t = normalize(text)
    return Counter(t[i:i+n] for i in range(max(0, len(t)-n+1)))


def char3gram_scores(question: str, public_index: Sequence[Mapping]) -> list[float]:
    """TF-IDF cosine on Unicode NFKC case-folded character trigrams."""
    q, cards = public_input(question, public_index)
    docs = [character_ngrams(c["retrieval_text"]) for c in cards]
    query = character_ngrams(q)
    df = Counter()
    for d in docs:
        df.update(d.keys())
    idf = {g: 1.0 + math.log((33.0) / (v+1.0)) for g,v in df.items()}
    def vector(c: Counter) -> dict[str,float]:
        return {k: float(v) * idf.get(k, 1.0 + math.log(33.0))
                for k,v in c.items()}
    qv = vector(query)
    qnorm = math.sqrt(sum(v*v for v in qv.values()))
    scores = []
    for d in docs:
        dv = vector(d)
        norm = math.sqrt(sum(v*v for v in dv.values()))
        dot = sum(v*dv.get(k,0.0) for k,v in qv.items())
        scores.append(float(dot/(qnorm*norm)) if qnorm and norm else 0.0)
    return scores


def t1_mean_cosine_scores(question: str, public_index: Sequence[Mapping],
                          text_to_ids, frozen_embedding) -> list[float]:
    """Pinned legacy helper; supplied tokenizer and T1/P02 embedding, NO training."""
    q, cards = public_input(question, public_index)
    from v2_nontest_retrievers import frozen_description_cosine
    return list(frozen_description_cosine(q, cards, text_to_ids, frozen_embedding))


class LocalBGE:
    """Pretrained BGE v1.5 CLS encoder, FP32 CPU, LOCAL FILES ONLY, no imports on mock."""
    def __init__(self, model_dir: Path, tokenizer_sha256: str):
        import torch
        from transformers import AutoTokenizer, AutoModel
        if not isinstance(tokenizer_sha256, str) or len(tokenizer_sha256) != 64:
            raise ValueError("TOKENIZER_HASH_MUST_BE_FROZEN_BEFORE_CAL")
        root = Path(model_dir).resolve(strict=True)
        weight = root / "model.safetensors"
        tok = root / "tokenizer.json"
        if not weight.is_file() or not tok.is_file():
            raise FileNotFoundError("FROZEN_BGE_FILES_MISSING")
        if sha256_file(weight) != EXPECTED_SAFETENSORS_SHA256:
            raise ValueError("BGE_WEIGHT_SHA256_MISMATCH")
        if sha256_file(tok) != tokenizer_sha256:
            raise ValueError("BGE_TOKENIZER_SHA256_MISMATCH")
        if torch.cuda.is_initialized():
            raise ValueError("CUDA_INITIALIZED_FOR_CPU_ONLY")
        os.environ["HF_HUB_OFFLINE"] = "1"
        os.environ["TRANSFORMERS_OFFLINE"] = "1"
        torch.set_num_threads(2)
        self.torch = torch
        self.tok = AutoTokenizer.from_pretrained(str(root), local_files_only=True,
                                                  trust_remote_code=False, use_fast=True)
        self.model = AutoModel.from_pretrained(str(root), local_files_only=True,
                                               trust_remote_code=False,
                                               use_safetensors=True).cpu().float().eval()
        self.model.requires_grad_(False)
        if self.model.config.hidden_size != 384:
            raise ValueError("UNEXPECTED_BGE_HIDDEN_SIZE")
        self.model_dir = root

    def embed(self, texts: Sequence[str]):
        torch = self.torch
        if not texts or any(not isinstance(x,str) or not x for x in texts):
            raise ValueError("BAD_EMBED_INPUT")
        with torch.inference_mode():
            toks = self.tok(list(texts), return_tensors="pt", padding=True,
                            truncation=True, max_length=256)
            last = self.model(**toks).last_hidden_state
            z = last[:,0,:].float()
            z = torch.nn.functional.normalize(z, p=2, dim=-1)
            if not bool(torch.isfinite(z).all()):
                raise ValueError("NONFINITE_BGE_EMBEDDING")
            return z.cpu()

    def scores(self, question: str, public_index: Sequence[Mapping]) -> list[float]:
        q,cards = public_input(question, public_index)
        text = [q] + [c["retrieval_text"] for c in cards]
        v = self.embed(text)
        return [float(x) for x in (v[1:] @ v[0]).tolist()]


@dataclass(frozen=True)
class Decision:
    status: str
    selected_index: int | None
    selected_key: str | None
    reason_code: str
    confidence: float
    threshold: float
    method: str


def score_margin(scores: Sequence[float]) -> float:
    if len(scores) != 32 or any(not isinstance(x,(int,float)) or
                                not math.isfinite(x) for x in scores):
        raise ValueError("BAD_SCORE_VECTOR")
    vals = sorted((float(x) for x in scores), reverse=True)
    gap = vals[0] - vals[1]
    return float(gap / (1 + abs(vals[0]) + abs(vals[1])))


def decision_from_scores(scores: Sequence[float], public_index: Sequence[Mapping],
                         threshold: float, method: str) -> Decision:
    _, cards = public_input("VALID PUBLIC QUERY", public_index)
    if method not in METHODS:
        raise ValueError("UNKNOWN_RETRIEVAL_METHOD")
    if not isinstance(threshold,(int,float)) or math.isnan(threshold) or threshold < 0:
        raise ValueError("INVALID_THRESHOLD")
    margin = score_margin(scores)
    if threshold == math.inf:
        return Decision("ABSTAIN",None,None,"CAL_ALWAYS_ABSTAIN",margin,threshold,method)
    if margin <= 0 or margin < threshold:
        return Decision("ABSTAIN",None,None,"INSUFFICIENT_TOP1_TOP2_MARGIN",margin,threshold,method)
    rank = sorted(range(32),key=lambda i:(-float(scores[i]),cards[i]["key"]))
    idx = rank[0]
    return Decision("SELECT",idx,cards[idx]["key"],"UNIQUE_CAL_MARGIN",margin,threshold,method)


def validate_cal(cases: Sequence[Mapping]) -> None:
    if len(cases) != 64:
        raise ValueError("CAL_MUST_HAVE_64")
    if Counter(x["stratum"] for x in cases) != Counter({s:8 for s in CAL_STRATA}):
        raise ValueError("CAL_STRATA_8_EACH")
    if len({x["case_id"] for x in cases}) != 64:
        raise ValueError("CAL_DUPLICATE_CASE_ID")
    for row in cases:
        public_input(row["question"],row["public_index"])
        positive = row["stratum"] not in CAL_NEGATIVE
        if (row["gold_action"]=="SELECT") != positive:
            raise ValueError("CAL_GOLD_ACTION_MISMATCH")
        keys = {c["key"] for c in row["public_index"]}
        if positive and row.get("gold_target_key") not in keys:
            raise ValueError("CAL_POSITIVE_GOLD_KEY_INVALID")
        if not positive and row.get("gold_target_key") is not None:
            raise ValueError("CAL_NEGATIVE_HAS_TARGET")


def calibrate_one(cases: Sequence[Mapping], score_vectors: Sequence[Sequence[float]],
                  method: str) -> dict:
    """Allowed for CAL ONLY; not for PROBE. No training, no candidate source access."""
    validate_cal(cases)
    if method not in METHODS or len(score_vectors)!=64:
        raise ValueError("CAL_METHOD_OR_SCORE_COUNT_INVALID")
    if any(len(x)!=32 for x in score_vectors):
        raise ValueError("CAL_SCORE_VECTOR_LENGTH_INVALID")
    candidates = list(CAL_GRID) + [math.inf]
    ranked = []
    for threshold in candidates:
        actions = [decision_from_scores(z,row["public_index"],threshold,method)
                   for row,z in zip(cases,score_vectors)]
        false_select = sum(d.status=="SELECT" for row,d in zip(cases,actions)
                           if row["stratum"] in CAL_NEGATIVE)
        if false_select > 1:
            continue
        hits = sum(d.status=="SELECT" and d.selected_key==row["gold_target_key"]
                   for row,d in zip(cases,actions) if row["stratum"] in CAL_PRIMARY)
        coverage = sum(d.status=="SELECT" for d in actions)
        # Select max hits, then lower coverage, then stricter threshold.
        ranked.append((hits,-coverage,threshold,coverage,false_select))
    if not ranked:
        raise AssertionError("ALWAYS_ABSTAIN_MUST_BE_ELIGIBLE")
    hits,_,thr,cov,fp = max(ranked)
    return {"method":method,"threshold":("ALWAYS_ABSTAIN" if thr==math.inf else thr),
            "cal_correct_primary":hits,"cal_primary_n":24,
            "cal_negative_false_select":fp,"cal_negative_n":32,
            "cal_total_coverage":cov,"cal_cases":64,
            "selection_rule":"MAX_CORRECT_THEN_LOW_COVERAGE_THEN_STRICTER_THRESHOLD"}


def choose_best_baseline(cal_receipts: Mapping[str,Mapping]) -> str:
    choices = METHODS[:3]
    if set(cal_receipts) != set(choices):
        raise ValueError("MUST_INCLUDE_ALL_THREE_CAL_BASELINES")
    # By design: among safety-qualified methods, maximize correct CAL positives;
    # tie by priority BM25 > CHAR3GRAM > T1 (do not use PROBE).
    return max(choices,key=lambda m:(cal_receipts[m]["cal_correct_primary"],
                                     -cal_receipts[m]["cal_negative_false_select"],
                                     -choices.index(m)))

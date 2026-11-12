#!/usr/bin/env python3
"""Frozen H-DEC-R1 R1 endpoint and candidate gate. Only safe to use AFTER score freeze.

No model execution, no private file IO, no reviewer impersonation. Math routines only.
Prerequisite: numpy==2.3.5; 20k paired prompt bootstrap resamples with seed 20261112.
"""
from __future__ import annotations
import re
import numpy as np

WORD_RE = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")
BOOTSTRAP_SEED=20261112
BOOTSTRAP_RESAMPLES=20_000
FROZEN_NUMPY_VERSION='2.3.5'

def words(text: str) -> list[str]:
    return WORD_RE.findall(text.lower())

def repeat_fraction(text: str) -> float:
    w=words(text)
    if len(w)<3:return 0.0
    tri=[tuple(w[i:i+3]) for i in range(len(w)-2)]
    return 1.0-len(set(tri))/len(tri)

def ci_paired(deltas: list[float]) -> tuple[float,float]:
    if np.__version__!=FROZEN_NUMPY_VERSION:
        raise RuntimeError('FROZEN_NUMPY_VERSION_MISMATCH')
    if len(deltas)!=24:raise ValueError('MUST_BE_EXACT_24_PAIRED_PROMPTS')
    a=np.asarray(deltas,dtype=np.float64)
    if not np.all(np.isfinite(a)):raise ValueError('NON_FINITE_DELTAS')
    rng=np.random.default_rng(BOOTSTRAP_SEED)
    draws=rng.choice(a,size=(BOOTSTRAP_RESAMPLES,24),replace=True)
    means=np.mean(draws,axis=1)
    # NumPy's linear percentile quantile, not alternative estimators.
    return (float(np.quantile(means,0.025,method='linear')),float(np.quantile(means,0.975,method='linear')))

def candidate_gate(rows: list[dict],rater_score_rows: list[dict]) -> dict:
    """Use only after rater blind score file SHA freeze and owner AES unblind.

    rows: 24 owner-only items with D0/D1 text (never publish per-pair arm map).
    rater_score_rows: 24 mapped owner-only score dicts {'D0':{axis:0..3}, 'D1':...}.
    """
    if len(rows)!=24 or len(rater_score_rows)!=24:raise ValueError('REQUIRE_24_PAIRED_RECORDS')
    if [x['pair_id'] for x in rows] != [f'R{i:02d}' for i in range(1,25)]:raise ValueError('PAIR_ID_DRIFT')
    metrics=[];short0=short1=0
    for row in rows:
        x,y=row['D0'],row['D1']
        if not (isinstance(x,str) and isinstance(y,str)):raise TypeError('TEXT_REQUIRED')
        metrics.append(repeat_fraction(y)-repeat_fraction(x))
        short0+=len(words(x))<8
        short1+=len(words(y))<8
    gates={
      'mean_delta_le_minus_0_10':sum(metrics)/24<=-0.10,
      'D1_strict_better_ge_16':sum(x<0 for x in metrics)>=16,
      'bootstrap_upper_lt_zero':ci_paired(metrics)[1]<0,
      'no_D1_short_under8_excess':short1<=short0,
    }
    for axis in ('prompt_adherence','coherence','consistency'):
        for row in rater_score_rows:
            for arm in ('D0','D1'):
                x=row[arm][axis]
                if type(x) is not int or x not in (0,1,2,3):raise ValueError('INVALID_RATER_SCORE')
        avg=sum(row['D1'][axis]-row['D0'][axis] for row in rater_score_rows)/24
        gates[axis+'_drop_not_below_minus_0_25']=avg>=-0.25
    return {'gates':gates,'candidate_pass':all(gates.values()),'mean_repeat_delta':sum(metrics)/24,'wins_D1':sum(x<0 for x in metrics),'wins_D0':sum(x>0 for x in metrics),'ties':sum(x==0 for x in metrics),'CI95_descriptive':list(ci_paired(metrics)),'D0_under8_words':short0,'D1_under8_words':short1}

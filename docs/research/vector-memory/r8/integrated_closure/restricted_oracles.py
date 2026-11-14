"""Executable O1-O8 restricted, CPU-only contract functions; NON-R8 inputs only.
Dependency versions are runtime readbacks, NOT G2 owner/custodian source authorization.
All training uses supplied TRAIN components. No hyperparameter search or posthoc label flips.
"""
from __future__ import annotations
import math,re,sys,unicodedata
from collections import Counter,defaultdict

SEED=20261114
PATTERN=r"(?u)\b\w+\b"
MARKERS=("applicable signed record","signed","approved","pending","countersigned",
         "reconciled","authorized","received")
PRIMARY=("O2","O3","O4","O5","O6")
ALPHA=.05
C=1.0
MAX_ITER=1000
K1=1.2
B=.75
FEATURE_BOUNDARIES={
 "O1":"card order/card count only; no labels in features",
 "O2":"length, ID character class, source format/marker, displayed position",
 "O3":"status/authority marker tokens and precommitted marker ngrams",
 "O4":"question-only and question+O2; no card text as semantic evidence",
 "O5":"per-card marker/length/status/authority, only TRAIN SELECT gold",
 "O6":"O2+O3+O4 action; O5 key conditional on SELECT",
 "O7":"allowed question-card lexical TF-IDF and BM25 comparator",
 "O8":"frozen R7 phrase/ID/source/slot/date-location rule probes",
}

def norm(s):
    return unicodedata.normalize("NFKC",str(s)).lower()
def words(s):
    return re.findall(PATTERN,norm(s))
def _imports():
    import sklearn,numpy,scipy
    from sklearn.feature_extraction import DictVectorizer
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from scipy.sparse import hstack
    return sklearn,numpy,scipy,DictVectorizer,TfidfVectorizer,LogisticRegression,hstack
def runtime():
    try:
        sklearn,np,sp,*_=_imports()
        return {"python":sys.version.split()[0],"scikit_learn":sklearn.__version__,
                "numpy":np.__version__,"scipy":sp.__version__,"seed":SEED,
                "token_pattern":PATTERN,"fixed_C":C,"solver":"liblinear",
                "max_iter":MAX_ITER,"tfidf_ngrams":[1,2],
                "tfidf_max_features":2000,"bm25_k1":K1,"bm25_b":B}
    except ImportError as e:
        return {"status":"NOT_AVAILABLE","detail":str(e),"python":sys.version.split()[0]}

def _card_meta(card,i):
    k=norm(card["key"]);sid=norm(card.get("source_id",""))
    return {"key_len":len(k),"key_digits":sum(x.isdigit() for x in k),
            "key_alpha":sum(x.isalpha() for x in k),"src_len":len(sid),
            "txt_len_bucket5":len(words(card.get("text","")))//5,
            "pos":i,"src_marker="+norm(card.get("source_marker","")):1.0,
            "src_format="+norm(card.get("source_format","")):1.0}

def _o1_features(case):
    """Public row decile cannot be inferred from a train/test list index."""
    position = case.get("public_row_position")
    total = case.get("public_case_count")
    if type(position) is not int or type(total) is not int or total < 1 or not (0 <= position < total):
        raise ValueError("PUBLIC_ROW_POSITION_REQUIRED_FOR_O1")
    return {
        "row_position_decile": min(9, (10 * position) // total),
        "card_count": len(case["cards"]),
        "first_key_length": len(case["cards"][0]["key"]),
        "last_key_length": len(case["cards"][-1]["key"])
    }


def _o2_features(case):
    """Public metadata plus non-constant card-position interactions.

    Summing the position of all 32 cards is always 496, so is not a valid
    position-leakage control. Preserve marker/source distributions and
    where in the visible index those values appear.
    """
    cards = case["cards"]
    z = {"card_count": len(cards)}
    for i, card in enumerate(cards):
        d = _card_meta(card, i)
        for k, v in d.items():
            if k == "pos":
                continue  # Constant sum for every 32-card case.
            if k.startswith(("src_marker=", "src_format=")):
                z[k] = z.get(k, 0) + 1
                z[k + "_quartile_" + str((4 * i) // max(len(cards), 1))] = (
                    z.get(k + "_quartile_" + str((4 * i) // max(len(cards), 1)), 0) + 1
                )
            elif isinstance(v, (int, float)):
                z[k + "_sum"] = z.get(k + "_sum", 0) + v
        rank = i + 1
        z["rank_weighted_key_length"] = (
            z.get("rank_weighted_key_length", 0) + rank * d["key_len"]
        )
        z["rank_weighted_text_bucket"] = (
            z.get("rank_weighted_text_bucket", 0) + rank * d["txt_len_bucket5"]
        )
    z["first_key_length"] = len(cards[0]["key"])
    z["last_key_length"] = len(cards[-1]["key"])
    z["first_source_id_length"] = len(cards[0].get("source_id", ""))
    z["last_source_id_length"] = len(cards[-1].get("source_id", ""))
    return z

def _o3_features(case):
    z={}
    for c in case["cards"]:
        t=norm(c.get("text","")+" "+c.get("status","")+" "+c.get("authority_role",""))
        for term in MARKERS:z["marker="+term]=z.get("marker="+term,0)+t.count(term)
        for field in ("status","authority_role","source_format"):
            key=field+"="+norm(c.get(field,""))
            z[key]=z.get(key,0)+1
        w=words(t)
        for n in (1,2):
            for i in range(len(w)-n+1):
                # counts of status/source marker ngrams, not full semantic card text
                seq=" ".join(w[i:i+n])
                if any(x in seq for x in MARKERS):
                    key="markergram="+seq
                    z[key]=z.get(key,0)+1
    return z
def _o5_features(card):
    text=norm(card.get("text",""))
    z={"len_bucket5":len(words(text))//5,
       "key_len":len(card["key"])}
    for m in MARKERS:z["marker="+m]=text.count(m)
    for field in ("status","authority_role","source_marker","source_format"):
        z[field+"="+norm(card.get(field,""))]=1
    return z

def validate_split(train,test):
    if not train or not test:return "NOT_ESTIMABLE_EMPTY_SPLIT"
    allrows=train+test
    if any(len(c.get("cards",[]))!=32 for c in allrows):
        return "INVALID_CARDINALITY_NOT_32"
    if any(len({x["key"] for x in c["cards"]})!=32 for c in allrows):
        return "INVALID_DUPLICATE_CARD_KEYS"
    if any(c.get("action") not in ("SELECT","ABSTAIN") for c in allrows):
        return "INVALID_ACTION"
    for c in allrows:
        key=c.get("target_key")
        if c["action"]=="SELECT" and key not in {x["key"] for x in c["cards"]}:
            return "INVALID_SELECT_TARGET"
        if c["action"]=="ABSTAIN" and key is not None:return "INVALID_ABSTAIN_KEY"
    tc={c["component_id_pre"] for c in train}
    ec={c["component_id_pre"] for c in test}
    if tc & ec:return "FOLD_LEAK_CV_INVALID"
    if len(tc | ec)<4:return "NOT_ESTIMABLE_FEWER_THAN_4_COMPONENTS"
    if {c["action"] for c in train}!={"SELECT","ABSTAIN"}:
        return "NOT_ESTIMABLE_ONE_CLASS_TRAIN"
    order_rows = [(c.get("public_row_position"), c.get("public_case_count")) for c in allrows]
    if any(type(pos) is not int or type(total) is not int or total < 1 or
           not 0 <= pos < total for pos, total in order_rows):
        return "NOT_ESTIMABLE_PUBLIC_ORDER_MISSING"
    if len({pos for pos, _ in order_rows}) != len(order_rows):
        return "INVALID_PUBLIC_ROW_POSITION_DUPLICATE"
    if len({total for _, total in order_rows}) != 1:
        return "INVALID_PUBLIC_CASE_COUNT_INCONSISTENT"
    return "VALID_SOURCE_ONLY_SPLIT"

def _fit_dict(train_features,train_y,test_features,weights=None):
    _,_,_,DictVectorizer,_,LogisticRegression,_=_imports()
    vec=DictVectorizer(sparse=True)
    x=vec.fit_transform(train_features)
    y=vec.transform(test_features)
    model=LogisticRegression(C=C,solver="liblinear",max_iter=MAX_ITER,
                              random_state=SEED)
    model.fit(x,train_y,sample_weight=weights)
    return model.predict(y).tolist(),model.predict_proba(y).tolist()

def _binary_result(train,test,features,question=False,with_meta=False):
    labels=[int(c["action"]=="SELECT") for c in train]
    tr=[features(c) for c in train];te=[features(c) for c in test]
    if not question:
        pred,proba=_fit_dict(tr,labels,te)
    else:
        _,_,_,DictVectorizer,TfidfVectorizer,LogisticRegression,hstack=_imports()
        v=TfidfVectorizer(ngram_range=(1,2),max_features=2000,
                          min_df=1,sublinear_tf=False,token_pattern=PATTERN,
                          lowercase=True,strip_accents=None)
        qtr=v.fit_transform([norm(c["question"]) for c in train])
        qte=v.transform([norm(c["question"]) for c in test])
        if with_meta:
            dv=DictVectorizer(sparse=True)
            qtr=hstack([qtr,dv.fit_transform(tr)]).tocsr()
            qte=hstack([qte,dv.transform(te)]).tocsr()
        model=LogisticRegression(C=C,solver="liblinear",max_iter=MAX_ITER,
                                  random_state=SEED)
        model.fit(qtr,labels)
        pred=model.predict(qte).tolist()
    correct=sum(int(bool(p)==(c["action"]=="SELECT")) for p,c in zip(pred,test))
    return {"status":"EXECUTED_NON_R8_SYNTHETIC_ONLY","correct":correct,"n":len(test),
            "action_accuracy":correct/len(test),
            "predictions":["SELECT" if p else "ABSTAIN" for p in pred]}

def _o1(train,test):
    counts=defaultdict(Counter)
    for c in train:counts[str(_o1_features(c))][c["action"]]+=1
    predictions=[]
    for c in test:
        cts=counts.get(str(_o1_features(c)),Counter())
        predictions.append("SELECT" if cts["SELECT"]>cts["ABSTAIN"] else "ABSTAIN")
    return {"status":"EXECUTED_NON_R8_SYNTHETIC_ONLY","predictions":predictions,
            "n":len(test),"action_accuracy":sum(x==c["action"] for x,c in zip(predictions,test))/len(test),
            "ties_abstain":True}

def _o5(train, test):
    """Train-only key selector; held-out key predictions ignore held-out action."""
    select = [c for c in train if c["action"] == "SELECT"]
    if not select:
        return {"status": "NOT_ESTIMABLE_NO_TRAIN_SELECT"}
    xf, labs, weights = [], [], []
    for case in select:
        for card in case["cards"]:
            positive = card["key"] == case["target_key"]
            xf.append(_o5_features(card))
            labs.append(int(positive))
            weights.append(.5 if positive else .5 / 31)
    _, _, _, DictVectorizer, _, LogisticRegression, _ = _imports()
    vec = DictVectorizer(sparse=True)
    model = LogisticRegression(C=C, solver="liblinear", max_iter=MAX_ITER,
                               random_state=SEED)
    model.fit(vec.fit_transform(xf), labs, sample_weight=weights)
    answers, outcomes = {}, []
    tiecount, hits, n = 0, 0, 0
    for case in test:
        probs = model.predict_proba(
            vec.transform([_o5_features(x) for x in case["cards"]])
        )[:, 1]
        maximum = max(probs)
        idx = [i for i, value in enumerate(probs) if abs(value - maximum) < 1e-12]
        key = case["cards"][idx[0]]["key"]
        answers[case["id"]] = key
        if case["action"] == "SELECT":
            correct = key == case["target_key"]
            tiecount += int(len(idx) > 1)
            hits += int(correct)
            n += 1
            # Private QA bookkeeping; never write IDs/keys to public reports.
            outcomes.append({"case_id": case["id"], "correct": bool(correct)})
    return {
        "status": "EXECUTED_NON_R8_SYNTHETIC_ONLY",
        "select_n": n, "correct": hits,
        "conditional_key_accuracy": hits / n if n else None,
        "null_per_card": 1 / 32,
        "tie_count": tiecount, "keys": answers,
        "select_case_outcomes": outcomes,
        "training_weight_each_select_case": 1.0,
        "training_positive": .5, "training_negative_each": .5 / 31,
        # Descriptive per-fold warning, not a statistical test or R8 release.
        "fold_key_signal_warning": n > 0 and hits / n >= 20 / 32,
        "fold_warning_interpretation": "DESCRIPTIVE_ONLY_NOT_HOLM_OR_P_VALUE",
        "high_signal_hold_review": n > 0 and hits / n >= 20 / 32
    }


def aggregate_o5_folds(fold_results, expected_select_cases=32):
    """One predeclared out-of-fold key alarm; never interpret as a p-value.

    20/32 is a descriptive reviewer trigger from the original R8 V4
    design discussion, NOT a valid significance test in dependent groups.
    Disjoint held-out case identities must be checked before aggregation.
    """
    if type(expected_select_cases) is not int or expected_select_cases <= 0:
        raise ValueError("INVALID_EXPECTED_SELECT_COUNT")
    if not fold_results:
        return {"status": "NOT_ESTIMABLE_EMPTY_OOF"}
    seen, hits = set(), 0
    for result in fold_results:
        if result.get("status") != "EXECUTED_NON_R8_SYNTHETIC_ONLY":
            return {"status": "NOT_ESTIMABLE_FOLD_MISSING"}
        rows = result.get("select_case_outcomes")
        if not isinstance(rows, list) or len(rows) != result.get("select_n"):
            return {"status": "INVALID_OOF_CASE_ACCOUNTING"}
        for row in rows:
            cid = row["case_id"]
            if cid in seen:
                return {"status": "INVALID_OOF_DUPLICATE_CASE"}
            seen.add(cid)
            hits += int(row["correct"])
    n = len(seen)
    if n > expected_select_cases:
        return {"status": "INVALID_OOF_EXCEEDS_PREDECLARED_N"}
    complete = n == expected_select_cases
    return {
        "status": "OOF_COMPLETE_DESCRIPTIVE_ONLY" if complete else "OOF_PARTIAL_NOT_ESTIMABLE",
        "select_n": n, "correct": hits,
        "conditional_key_accuracy": hits / n if n else None,
        "expected_select_cases": expected_select_cases,
        "uniform_key_null": 1 / 32,
        "high_signal_hold_review": n > 0 and hits / n >= 20 / 32,
        "predeclared_raw_alarm": "accuracy>=20/32",
        "inferential_status": "NOT_ESTIMABLE_UNLESS_CLUSTER_EXCHANGEABILITY_ATTESTED",
        "not_an_independent_sample_count": True
    }

def _o7(train,test):
    _,_,_,_,TfidfVectorizer,_,_=_imports()
    v=TfidfVectorizer(ngram_range=(1,2),max_features=2000,token_pattern=PATTERN)
    train_text=[norm(k["text"]) for c in train for k in c["cards"]]
    v.fit(train_text)
    freq=Counter();lens=[]
    for t in train_text:
        tok=words(t);lens.append(len(tok));freq.update(set(tok))
    N=len(train_text);avgl=sum(lens)/max(N,1)
    rows=[]
    for case in test:
        q=norm(case["question"])
        texts=[norm(x["text"]) for x in case["cards"]]
        sim=(v.transform(texts)@v.transform([q]).T).toarray().ravel()
        tfidf_key=case["cards"][int(sim.argmax())]["key"]
        qterms=words(q)
        bs=[]
        for t in texts:
            tok=words(t);count=Counter(tok);L=len(tok);sc=0.0
            for term in qterms:
                n=freq[term];idf=math.log(1+(N-n+.5)/(n+.5))
                f=count[term]
                if f:sc+=idf*f*(K1+1)/(f+K1*(1-B+B*L/max(avgl,1)))
            bs.append(sc)
        bm25_key=case["cards"][max(range(len(bs)),key=lambda j:bs[j])]["key"]
        rows.append((tfidf_key,bm25_key,case["target_key"] if case["action"]=="SELECT" else None))
    sel=[r for r,c in zip(rows,test) if c["action"]=="SELECT"]
    return {"status":"EXECUTED_NON_R8_SYNTHETIC_ONLY","select_n":len(sel),
            "tfidf_correct":sum(a==target for a,_,target in sel),
            "bm25_correct":sum(b==target for _,b,target in sel),
            "role":"ALLOWED_LEXICAL_COMPARATOR_NOT_PRIMARY_LEAKAGE_ORACLE"}

def _o8(cases):
    found=Counter()
    for c in cases:
        cards=c["cards"]
        text=" ".join(norm(x.get("text","")) for x in cards)
        if "applicable signed record" in text:found["R7_APPLICABLE_SIGNED_RECORD"]+=1
        if any(re.search(r"(?:src|source)[-_]?\d+",norm(x.get("source_id",""))) for x in cards):
            found["ID_SOURCE_REGEX"]+=1
        if c.get("action")=="SELECT" and c["target_key"]==cards[0]["key"]:
            found["POSITION_FIRST"]+=1
        if re.search(r"\b\d{4}-\d{2}-\d{2}\b",text) and re.search(r"\b(?:location|site)\b",text):
            found["DATE_LOCATION_MAP"]+=1
    return {"status":"EXECUTED_NON_R8_SYNTHETIC_ONLY","positive_rule_triggers":dict(found),
            "r7_frozen_actual_data":"NOT_ACCESSED","rules_are_alarms_not_gold_predictors":True}

def holm_primary(pvalues,exchangeable=False):
    """Only compute corrected decisions if p-values came from justified blocked null."""
    if not exchangeable or set(pvalues)!=set(PRIMARY):
        return {"status":"NOT_ESTIMABLE","reason":"GROUPED_EXCHANGEABILITY_NOT_ATTESTED_OR_MISSING_P"}
    if any(p<0 or p>1 for p in pvalues.values()):raise ValueError("P_OUT_OF_RANGE")
    ranked=sorted(pvalues.items(),key=lambda z:z[1])
    results={};previous=True
    for i,(name,p) in enumerate(ranked):
        cutoff=ALPHA/(len(ranked)-i)
        previous=previous and p<=cutoff
        results[name]={"p":p,"cutoff":cutoff,"reject":previous}
    return {"status":"HOLM_WITH_ATTESTED_GROUP_EXCHANGEABILITY","tests":results,
            "FWER":ALPHA,"first_cutoff":.01}

def evaluate(train,test):
    """No CV fitting if validation fails; callers must predeclare split and units."""
    state=validate_split(train,test)
    if state!="VALID_SOURCE_ONLY_SPLIT":
        return {"status":state,"oracles":{f"O{i}":"NOT_EXECUTED" for i in range(1,9)}}
    try:_imports()
    except ImportError as e:
        return {"status":"DEPENDENCY_NOT_AVAILABLE","detail":str(e),
                "oracles":{f"O{i}":"NOT_EXECUTED" for i in range(1,9)}}
    o1=_o1(train,test)
    o2=_binary_result(train,test,_o2_features)
    o3=_binary_result(train,test,_o3_features)
    q=_binary_result(train,test,lambda _: {},question=True)
    qm=_binary_result(train,test,_o2_features,question=True,with_meta=True)
    o5=_o5(train,test)
    o6_action=_binary_result(train,test,
                   lambda c:{**_o2_features(c),**{"o3_"+k:v for k,v in _o3_features(c).items()}},
                   question=True,with_meta=True)
    action_hits=0;joint_hits=0;eligible=0;key_hits=0
    for pred,c in zip(o6_action["predictions"],test):
        action_hits+=int(pred==c["action"])
        if pred=="ABSTAIN" and c["action"]=="ABSTAIN":joint_hits+=1
        if pred=="SELECT":
            if c["action"]=="SELECT":
                eligible+=1
                match=o5["keys"].get(c["id"])==c["target_key"]
                key_hits+=int(match);joint_hits+=int(match)
    o6={"status":"EXECUTED_NON_R8_SYNTHETIC_ONLY","action_correct":action_hits,
        "action_n":len(test),"conditional_key_correct":key_hits,
        "conditional_key_n":eligible,"joint_correct":joint_hits,
        "joint_n":len(test),"action_accuracy":action_hits/len(test),
        "conditional_key_accuracy":key_hits/eligible if eligible else None,
        "joint_accuracy":joint_hits/len(test),
        "abstention_handled":True}
    return {"status":"EXECUTED_NON_R8_SYNTHETIC_ONLY","runtime":runtime(),
            "oracles":{"O1":o1,"O2":o2,"O3":o3,
                       "O4":{"question_only":q,"question_plus_metadata":qm},
                       "O5":o5,"O6":o6,"O7":_o7(train,test),
                       "O8":_o8(train+test)},
            "primary_statistics":holm_primary({},exchangeable=False),
            "source_only_not_science":True}

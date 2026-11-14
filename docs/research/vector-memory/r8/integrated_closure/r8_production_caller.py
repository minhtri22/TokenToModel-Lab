"""V4 R8 protected production preflight entrypoint (no authoring/no science).

No other R8 production caller is registered in this tree. Future R8 authoring
MUST use precommit_before_G3 followed by verify_after_G3_before_CV in this
order, with a custodian-held key and externally timestamped durable receipt.
This file does not create any cases, gold, fold secret or evaluation packets.
"""
from __future__ import annotations
import folds_raters as guarded

def precommit_before_G3(blueprints,private_hmac_key):
    """G_pre gate BEFORE any R8 text exists; requires authenticated storage."""
    lock=guarded.preassign_r8(blueprints,private_hmac_key)
    if lock["cv_status"]!="PREFOLD_READY_NOT_VALIDATED":
        raise ValueError("R8_CV_NOT_ESTIMABLE_PREASSIGNMENT")
    return lock

def verify_after_G3_before_CV(cases,blueprints,locked_preassignment,private_hmac_key):
    """Mandatory G_post gateway; fail closed on leakage, no re-partition."""
    checked=guarded.postcheck_r8(cases,blueprints,locked_preassignment,private_hmac_key)
    if checked["cv_status"]!="POST_GRAPH_NO_CROSSFOLD_EDGE":
        raise ValueError("FOLD_LEAK_CV_INVALID")
    return {"cv_status":"POST_GRAPH_NO_CROSSFOLD_EDGE",
            "post_case_count":checked["post_case_count"],
            "crossfold_post_edges":0,
            "no_repartition":True}

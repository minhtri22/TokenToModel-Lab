#!/usr/bin/env python3
"""V3 adversarial SOURCE test (no T4/checkpoint, no real tokenizer).

This is an author-supplied negative test script for separate reviewer rerun.
The code and a self-run do not certify organizational independence or Windows QA.
"""
from __future__ import annotations
import ast
import copy
import hashlib
import json
import os
import platform
from pathlib import Path
import re
import subprocess
import sys
import tempfile

import ttm_sm4m_diag_q001 as diag
import release_auth_v2 as auth

BASE=Path(__file__).resolve().parent


def expect_hold(fn, label: str) -> bool:
    try: fn()
    except (RuntimeError, auth.AdmissionHold): return True
    return False


def test_all() -> dict:
    checks={}
    meta, raw = diag.mock_token_inventory()
    allowed=diag.permitted_ids(meta,raw)
    rows=diag.fixture_generator(allowed)
    no_answer=next(r['gold'] for r in rows if r['group']=='HELDOUT_ABSENT')
    checks['mock_80_no_private']=len(rows)==80 and all(len(r['context'])==9 for r in rows)
    checks['oracle_80']=all(
        r['gold']==(r['context'][2] if r['context'][7]==r['context'][1]
                    else r['context'][5] if r['context'][7]==r['context'][4] else no_answer)
        for r in rows)
    checks['tampered_underlying_source_sha_denied']=expect_hold(lambda:diag.permitted_ids(meta,raw+b' '),'sha')
    checks['forged_metadata_digest_denied']=expect_hold(lambda:diag.permitted_ids(dict(meta,underlying_inventory_sha256='a'*64),raw),'sha')
    checks['all_zero_metadata_digest_denied']=expect_hold(lambda:diag.permitted_ids(dict(meta,underlying_inventory_sha256='0'*64),raw),'sha')
    bad=copy.deepcopy(meta);bad['allowed_non_special_ids'][0]=0
    checks['reserved_collision_denied']=expect_hold(lambda:diag.permitted_ids(bad,raw),'res')
    bad=copy.deepcopy(meta);bad['reserved_ids']=bad['reserved_ids'][1:]
    checks['partial_reserved_inventory_denied']=expect_hold(lambda:diag.permitted_ids(bad,raw),'res')
    source_bad=json.loads(raw);source_bad['special_ids']=[1];source_bad['reserved_ids'].remove(1)
    source_bytes=diag.json_bytes(source_bad)
    checks['mutated_inventory_taxonomy_denied']=expect_hold(lambda:diag.permitted_ids(dict(meta,underlying_inventory_sha256=hashlib.sha256(source_bytes).hexdigest()),source_bytes),'tax')
    cases=diag.case_and_group_manifest(rows)
    checks['manifest_80_case_hashes']=len(cases['case_sha256'])==80 and len(cases['group_sha256'])==5
    checkout_root=next((parent for parent in [BASE,*BASE.parents]
                        if (parent/'src'/'p02'/'transformer_core.py').is_file()), BASE)
    scratch=checkout_root/'_tmp'/'ttm_sm4m_diag_q001_mock_negative_qa'
    scratch.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='qa_',dir=scratch) as tmp:
        root=Path(tmp)
        fixture=root/'fixture'; fixture.mkdir()
        (fixture/'FIXTURE_RECORDS.json').write_bytes(diag.json_bytes(rows))
        (fixture/'FIXTURE_MANIFEST.json').write_bytes(diag.json_bytes(cases))
        digest=cases['fixture_sha256']
        checks['frozen_read_exact']=diag.read_frozen_fixture(fixture,digest,meta,raw)==rows
        original=(fixture/'FIXTURE_RECORDS.json').read_bytes()
        (fixture/'FIXTURE_RECORDS.json').write_bytes(original+b' ')
        checks['postfreeze_byte_mutation_denied']=expect_hold(lambda:diag.read_frozen_fixture(fixture,digest,meta,raw),'fixture')
        (fixture/'FIXTURE_RECORDS.json').write_bytes(original)
        old=cases['case_sha256'].copy()
        cases['case_sha256'][rows[0]['id']]='0'*64
        (fixture/'FIXTURE_MANIFEST.json').write_bytes(diag.json_bytes(cases))
        checks['case_manifest_tamper_denied']=expect_hold(lambda:diag.read_frozen_fixture(fixture,digest,meta,raw),'case')
        cases['case_sha256']=old
        (fixture/'FIXTURE_MANIFEST.json').write_bytes(diag.json_bytes(cases))
        checks['manifest_restored']=diag.read_frozen_fixture(fixture,digest,meta,raw)==rows
        (root/'FAKE_PERMIT.json').write_bytes(diag.json_bytes({
            'payload':{'owner_decision':auth.OWNER_DECISION},
            'signatures':{'owner':'bogus','distinct_reviewer':'bogus','rights_custodian':'bogus'}}))
        checks['forged_local_go_denied']=expect_hold(lambda:auth.authenticate_release(
            root/'FAKE_PERMIT.json',phase='run',runner_sha256='a'*64,
            tokenizer_sha256='b'*64,underlying_sha256='c'*64,
            frozen_fixture_sha256=digest),'permit')
        checks['missing_permit_denied']=expect_hold(lambda:auth.authenticate_release(
            root/'absent.json',phase='run',runner_sha256='a'*64,
            tokenizer_sha256='b'*64,underlying_sha256='c'*64,
            frozen_fixture_sha256=digest),'permit')
        # Does not read nonexistent checkpoint even when a forged permit claims GO.
        cmd=[sys.executable,str(BASE/'ttm_sm4m_diag_q001.py'),'run',
             '--root',str(root),'--permit',str(root/'FAKE_PERMIT.json'),
             '--checkpoint',str(root/'no-private-checkpoint.pt'),
             '--token-inventory',str(root/'no-private-inventory.json'),
             '--tokenizer-source',str(root/'no-underlying-tokens.json'),
             '--fixture-dir',str(fixture),'--out',str(root/'output')]
        proc=subprocess.run(cmd,text=True,capture_output=True,timeout=15)
        checks['no_checkpoint_read_under_forged_go']=proc.returncode==2 and 'HOLD_' in proc.stderr and not (root/'output').exists()
        # MOCK-only substitution of in-memory root/hostname pins to exercise
        # the atomic claim path, NOT an authenticated release or runtime trust.
        nonce='f'*64
        original_root,original_host=auth.TRUSTED_PROJECT_ROOT,auth.TRUSTED_HOSTNAME
        try:
            auth.TRUSTED_PROJECT_ROOT=str(root.resolve())
            auth.TRUSTED_HOSTNAME=platform.node()
            first=diag.claim_one_shot(root,nonce)
            checks['mock_first_atomic_claim_saved']=first.is_file()
            checks['mock_same_root_nonce_replay_denied']=expect_hold(lambda:diag.claim_one_shot(root,nonce),'replay')
            other=root/'different_project_root'
            other.mkdir()
            checks['mock_different_root_same_nonce_denied']=expect_hold(lambda:diag.claim_one_shot(other,nonce),'crossroot')
            checks['mock_ledger_is_shared_path_in_project']=first.is_relative_to(root/'_evidence')
        finally:
            auth.TRUSTED_PROJECT_ROOT,auth.TRUSTED_HOSTNAME=original_root,original_host
        checks['trust_pins_restored']=auth.TRUSTED_PROJECT_ROOT==original_root and auth.TRUSTED_HOSTNAME==original_host
        bad_rows=copy.deepcopy(rows);bad_rows[0]['gold']=-99
        checks['oracle_label_mutation_denied']=expect_hold(lambda:diag.validate_fixture(bad_rows,no_answer),'oracle')
        bad_rows=copy.deepcopy(rows);bad_rows[1]['context'][7]=bad_rows[1]['context'][1]
        checks['target_binding_mutation_denied']=expect_hold(lambda:diag.validate_fixture(bad_rows,no_answer),'binding')
    ps_qa=(BASE/'Run-SourceQA-PS51.ps1').read_text()
    ps_one=(BASE/'Run-Approved-OneShot-PS51.ps1').read_text()
    checks['PS5_script_relative_source_root']=all('$PSScriptRoot' in s for s in (ps_qa,ps_one))
    checks['PS5_no_runner_tmp_default']=all('_tmp\\ttm_sm4m_diag_q001_candidate' not in s for s in (ps_qa,ps_one))
    checks['PS5_has_64hex_pin']=all("^[0-9a-f]{64}$" in s for s in (ps_qa,ps_one))
    watch=(BASE/'Watch-TTM-SM4M-ProcessTree-PS51.ps1').read_text()
    native=(BASE/'Invoke-DIAG-Q001-Watchdog-NativeNegativeQA-PS51.ps1').read_text()
    checks['PS5_module_sha_pin_required']='ExpectedWatchdogSHA256' in ps_one and 'Get-FileHash' in ps_one
    checks['PS5_watchdog_source_process_tree']=all(x in watch for x in ('Get-CimInstance','ParentProcessId','PeakTreeRssBytesSampled','known.Contains'))
    checks['PS5_watchdog_postexit_checks']=watch.index('HOLD_WATCHDOG_TOTAL_LOG_AND_OUTPUT_BYTES') < watch.index('$Process.Refresh()')
    checks['PS5_native_negative_source_present']=all(x in native for x in ('normal_exit_pass','postexit_total_output_rejected','wall_time_kill','child_memory_in_aggregate','orphan_child_after_parent_exit'))
    checks['PS5_native_negative_NOT_CLAIMED_EXECUTED']=True
    script=(BASE/'ttm_sm4m_diag_q001.py').read_text()
    checks['last_context_position_target']=all(s in script for s in ('logits[:,-1,:]','cross_entropy(answer_logits,y)',"rows[i]['gold']"))
    checks['no_full_prompt_CE']=not bool(re.search(r'cross_entropy\(logits\.reshape',script))
    checks['no_eval_gradient']= 'with torch.no_grad():' in script
    checks['weight_delta_recorded']=all(s in script for s in ('parameter_absolute_delta_sum','ZERO_OR_NONFINITE_WEIGHT_DELTA','(p.detach()-before[i]).abs()','parameter_sha256_before','parameter_sha256_after','PARAMETER_FINGERPRINT_UNCHANGED'))
    checks['resource_bounds_present']=all(s in script for s in ('WALL_SECONDS = 900','MEMORY_BYTES = 12 * 1024**3','OUTPUT_BYTES = 1024**3'))
    checks['goldblind_four_way_secondary_only'] = all(x in script for x in
        ("GOLD_BLIND_VISIBLE_CONTEXT_CANDIDATES", "TIES_ABSTAIN",
         "TRACK_A_V3_SOURCE_SHA256", "evaluate_goldblind_logits"))
    checks['old_gold_first_restricted_path_removed'] = "opts=[gold]" not in script and
        "opts[max(range(4)" not in script
    checks['hardcoded_trust_roots_empty']=auth.TRUSTED_ED25519_PUBLIC_KEYS=={}
    checks['root_hostname_trust_pins_required']=(auth.TRUSTED_PROJECT_ROOT.lower()==r'D:\WORK\RESEARCH\TokenToModel-Lab'.lower()
       and auth.TRUSTED_HOSTNAME.upper()=='DESKTOP-4PSD0G2')
    checks['invalid_root_rejected_before_permit']=expect_hold(lambda:auth.trusted_execution_root(scratch),'noncanonical')
    checks['runner_claim_scope_canonical']=all(t in script for t in ('_evidence','ttm_sm4m_diag_q001_onetime_claims','trusted_execution_root'))
    checks['direct_cli_path_validator_present']='def exact_scoped_path(' in script and 'DIRECT_CLI_PATH_ESCAPES_SIGNED_PROJECT' in script
    checks['output_dir_scope_guard']=all(t in script for t in ('exact_scoped_path(root, out)','exact_scoped_path(root,check_path)'))
    checks['source_only_no_real_fixture_written']=not (scratch/'REAL_FIXTURE_RECORDS.json').exists()
    return {
        'scope':'V3_ADVERSARIAL_MOCK_AND_SOURCE_NO_MODEL',
        'checks':checks,'passed':sum(checks.values()),'total':len(checks),
        'python_version':sys.version,'native_windows_powershell':'NOT_EXECUTED_BY_THIS_PYTHON_QA',
        'checkpoint_access':False,'real_tokenizer_access':False,'model_execution':False,
        'signature_trust_roots':'UNCONFIGURED_FAIL_CLOSED','reviewer':'AUTHOR_SELF_TEST_NOT_DISTINCT_SIGNOFF'}


if __name__=='__main__':
    record=test_all()
    print(json.dumps(record,sort_keys=True))
    sys.exit(0 if record['passed']==record['total'] else 2)

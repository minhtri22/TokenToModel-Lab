#!/usr/bin/env python3
"""CPU-only negative suite; keys random in RAM; never model, dataset or TEST."""
from __future__ import annotations
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
from unittest.mock import patch

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

import g1_signed_boundary_contract_v1e_candidate as g

RUN = 'synthetic_g1_20261110'
WORK = 'SYNTHETIC_NO_REAL_PATH'
NOW = 1800000000
SIG_KEYS = ('owner','writer','witness')

@pytest.fixture
def identities():
    # No private keys, permits, raw IDs or test bytes written to disk.
    keys = {n:Ed25519PrivateKey.generate() for n in SIG_KEYS}
    pub={n:keys[n].public_key().public_bytes(Encoding.Raw, PublicFormat.Raw) for n in SIG_KEYS}
    pins={n:hashlib.sha256(pub[n]).hexdigest() for n in SIG_KEYS}
    def sign(name, payload):
        return {'payload':deepcopy(payload), 'public_key_hex':pub[name].hex(),
                'signature_hex':keys[name].sign(g.canonical(payload)).hex()}
    return {'keys':keys,'pub':pub,'pins':pins,'sign':sign}

@pytest.fixture
def owner():
    return {
        'schema':'ttm.six.g1.owner_admission.v1e_candidate',
        'decision':'QUALIFY_G1_PREEXECUTION_ONLY',
        'reviewed_v1c_head':g.FROZEN_V1C_HEAD,
        'reviewed_v1c_blobs':deepcopy(g.V1C_BLOBS),
        'manifest_sha256':g.MANIFEST_SHA256,
        't1_sha256':g.T1_SHA256,
        'run_id':RUN,'workspace':WORK,'phase':'PREEXECUTION_ONLY',
        'data_rights':'T1_TRAIN_METADATA_ONLY_NO_PRIVATE_TEST',
        'allow_real_science':False,'allow_private_test':False,
        'allow_teacher_download':False,
        'owner_id':'synthetic-owner','reviewer_id':'distinct-reviewer',
        'author_id':'code-author', 'issued_utc':NOW-5,
        'expires_utc':NOW+120,'launcher_commit_sha':'a'*40,
        'method_amendment_sha256':'b'*64,
    }

@pytest.fixture
def writer():
    return {'schema':'ttm.six.g1.external_writer_pack.v1e_candidate',
            'run_id':RUN,'stage':'TRAIN','manifest_sha256':g.MANIFEST_SHA256,
            'pack_sha256':hashlib.sha256(b'synthetic-unclassified-pack').hexdigest(),
            'ids_sha256':'c'*64,'witness_prev_ack':'d'*64,
            'seq':1,'status':'PACK_COMMITTED'}

@pytest.fixture
def witness():
    return {'schema':'ttm.six.g1.external_monotonic_ack.v1e_candidate',
            'run_id':RUN,'event_sha256':'e'*64,'prev_ack_sha256':'d'*64,
            'seq':1,'challenge_nonce':'1'*32,'status':'DURABLE_ACK',
            'issued_utc':NOW-1,'expires_utc':NOW+20}


def _owner(identities,p, now=NOW):
    return g.verify_owner_admission(identities['sign']('owner',p),
              externally_pinned_owner_sha256=identities['pins']['owner'],
              run_id=RUN,workspace=WORK,now=now)

def _writer(identities,p, source_bytes=b'synthetic-unclassified-pack'):
    return g.verify_signed_writer_receipt(identities['sign']('writer',p),
             writer_pubkey_pin=identities['pins']['writer'],run_id=RUN,
             stage='TRAIN',source_bytes=source_bytes,ids_sha256='c'*64,
             expected_seq=1,expected_prior_ack='d'*64)

def _witness(identities,p,now=NOW):
    return g.verify_signed_witness_ack(identities['sign']('witness',p),
            witness_pubkey_pin=identities['pins']['witness'],run_id=RUN,
            event_sha256='e'*64,previous_ack_sha256='d'*64,
            expected_seq=1,challenge_nonce='1'*32,now=now)


def test_01_positive_synthetic_authority(identities, owner):
    assert _owner(identities,owner)=={'synthetic_contract_verified':True,
            'science_authorized':False,'test_opened':False,'run_id':RUN}

def test_02_positive_synthetic_writer(identities,writer):
    assert _writer(identities,writer)['production_provenance_qualified'] is False

def test_03_positive_synthetic_witness(identities,witness):
    assert _witness(identities,witness)['external_monotonicity_proven'] is False

def test_04_three_distinct_signing_keys(identities):
    assert g.verify_distinct_anchor_pins(**{k:identities['pins'][k] for k in SIG_KEYS})

def test_05_no_owner_pin_production():
    assert g.status()['owner_pin_provisioned'] is False

def test_06_no_writer_pin_production():
    assert g.status()['writer_pin_provisioned'] is False

def test_07_no_witness_pin_production():
    assert g.status()['witness_pin_provisioned'] is False

def test_08_real_release_never_executed():
    with pytest.raises(g.BoundaryStop,match='RELEASE_NOT_IMPLEMENTED'):
        g.authorize_real_science(owner_authorized=True,independent_review=True)

def test_09_bad_owner_signature(identities,owner):
    e=identities['sign']('owner',owner);e['signature_hex']='00'*64
    with pytest.raises(g.BoundaryStop,match='SIGNATURE_INVALID'):
        g.verify_envelope(e,identities['pins']['owner'])

def test_10_owner_pinned_wrong_key(identities,owner):
    e=identities['sign']('owner',owner)
    with pytest.raises(g.BoundaryStop,match='SIGNER_NOT_TRUSTED'):
        g.verify_envelope(e,identities['pins']['witness'])

def test_11_signed_payload_mutation(identities,owner):
    e=identities['sign']('owner',owner);e['payload']['allow_private_test']=True
    with pytest.raises(g.BoundaryStop,match='SIGNATURE_INVALID'):
        g.verify_envelope(e,identities['pins']['owner'])

@pytest.mark.parametrize('field,value,code',[
    ('reviewed_v1c_head','f'*40,'OWNER_FIELD_REVIEWED_V1C_HEAD'),
    ('reviewed_v1c_blobs',{'guard':'e'*40},'OWNER_FIELD_REVIEWED_V1C_BLOBS'),
    ('manifest_sha256','f'*64,'OWNER_FIELD_MANIFEST_SHA256'),
    ('t1_sha256','f'*64,'OWNER_FIELD_T1_SHA256'),
    ('phase','TEST_EXTRACT','OWNER_FIELD_PHASE'),
    ('allow_real_science',True,'OWNER_FIELD_ALLOW_REAL_SCIENCE'),
    ('allow_real_science',0,'OWNER_FIELD_ALLOW_REAL_SCIENCE'),
    ('allow_private_test',True,'OWNER_FIELD_ALLOW_PRIVATE_TEST'),
    ('allow_teacher_download',True,'OWNER_FIELD_ALLOW_TEACHER_DOWNLOAD'),
    ('data_rights','FULL_CORPUS_TEST','OWNER_FIELD_DATA_RIGHTS'),
    ('launcher_commit_sha','BAD','LAUNCHER_PIN'),
    ('method_amendment_sha256','BAD','SHA_FORMAT_METHOD_AMENDMENT'),
    ('owner_id','code-author','OWNER_REVIEWER_AUTHOR_NOT_DISTINCT'),
    ('expires_utc',NOW-1,'OWNER_EXPIRY'),
    ('expires_utc',NOW+5000,'OWNER_EXPIRY'),
])
def test_signed_owner_contract_rejections(identities,owner,field,value,code):
    owner[field]=value
    with pytest.raises(g.BoundaryStop,match=code):_owner(identities,owner)

@pytest.mark.parametrize('field', ['reviewer_id','author_id','owner_id','issued_utc'])
def test_signed_owner_missing_fields(identities,owner,field):
    del owner[field]
    with pytest.raises(g.BoundaryStop,match='OWNER_SCOPE_KEYSET'):_owner(identities,owner)

def test_signed_owner_extra_field(identities,owner):
    owner['skip_gate']='PASS'
    with pytest.raises(g.BoundaryStop,match='OWNER_SCOPE_KEYSET'):_owner(identities,owner)

@pytest.mark.parametrize('field,value,code',[
    ('pack_sha256','f'*64,'WRITER_FIELD_PACK_SHA256'),
    ('ids_sha256','b'*64,'WRITER_FIELD_IDS_SHA256'),
    ('witness_prev_ack','e'*64,'WRITER_FIELD_WITNESS_PREV_ACK'),
    ('stage','TEST','WRITER_FIELD_STAGE'),
    ('status','PACK_PENDING','WRITER_FIELD_STATUS'),
    ('seq',True,'WRITER_FIELD_SEQ'),
    ('run_id','other_run_x','WRITER_FIELD_RUN_ID'),
])
def test_signed_writer_mismatch(identities,writer,field,value,code):
    writer[field]=value
    with pytest.raises(g.BoundaryStop,match=code):_writer(identities,writer)

def test_writer_bytes_swap(identities,writer):
    with pytest.raises(g.BoundaryStop,match='WRITER_FIELD_PACK_SHA256'):
        _writer(identities,writer,b'synthetic-pack-REPLACED')

def test_writer_self_signed_not_trusted(identities,writer):
    forged=identities['sign']('owner',writer)
    with pytest.raises(g.BoundaryStop,match='SIGNER_NOT_TRUSTED'):
        g.verify_signed_writer_receipt(forged,writer_pubkey_pin=identities['pins']['writer'],
          run_id=RUN,stage='TRAIN',source_bytes=b'synthetic-unclassified-pack',
          ids_sha256='c'*64,expected_seq=1,expected_prior_ack='d'*64)

@pytest.mark.parametrize('field,value,code',[
    ('event_sha256','f'*64,'WITNESS_FIELD_EVENT_SHA256'),
    ('prev_ack_sha256','f'*64,'WITNESS_FIELD_PREV_ACK_SHA256'),
    ('challenge_nonce','a'*32,'WITNESS_FIELD_CHALLENGE_NONCE'),
    ('seq',2,'WITNESS_FIELD_SEQ'),
    ('run_id','another_run','WITNESS_FIELD_RUN_ID'),
    ('status','UNCERTAIN','WITNESS_FIELD_STATUS'),
    ('expires_utc',NOW-1,'WITNESS_ACK_STALE'),
    ('expires_utc',NOW+100,'WITNESS_ACK_STALE'),
])
def test_witness_signed_ack_negative(identities,witness,field,value,code):
    witness[field]=value
    with pytest.raises(g.BoundaryStop,match=code):_witness(identities,witness)

def test_witness_replay_with_new_challenge(identities,witness):
    # Signed but replayed response cannot satisfy a fresh 2nd request nonce.
    e=identities['sign']('witness',witness)
    with pytest.raises(g.BoundaryStop,match='WITNESS_FIELD_CHALLENGE_NONCE'):
        g.verify_signed_witness_ack(e,witness_pubkey_pin=identities['pins']['witness'],
          run_id=RUN,event_sha256='e'*64,previous_ack_sha256='d'*64,
          expected_seq=1,challenge_nonce='2'*32,now=NOW)

def test_signer_anchor_duplicate_rejected(identities):
    with pytest.raises(g.BoundaryStop,match='TRUST_ANCHORS_NOT_DISTINCT'):
        g.verify_distinct_anchor_pins(identities['pins']['owner'],
                                     identities['pins']['owner'],
                                     identities['pins']['witness'])

def test_crypto_nan_rejected(identities):
    with pytest.raises(g.BoundaryStop,match='SIGNED_RECORD_CANONICAL'):
        identities['sign']('writer',{'value':float('nan')})

def test_missing_owner_pin_argument_rejected(identities,owner):
    with pytest.raises(g.BoundaryStop,match='SHA_FORMAT_AUTHORITY_PIN'):
        g.verify_envelope(identities['sign']('owner',owner),None)

def test_no_real_model_or_private_read_entrypoint():
    assert g.SCIENCE_LOCK=='HOLD' and not g.PRODUCTION_LAUNCHER_QUALIFIED
    assert g.status()['private_test_opened'] is False

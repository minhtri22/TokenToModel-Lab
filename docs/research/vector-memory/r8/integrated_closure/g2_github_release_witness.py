"""Optional GitHub immutable-release external one-shot witness candidate.

No release is created by importing or testing this file. Calling reserve_once
is a real GitHub write and is ONLY valid after independent acceptance and the
explicit separate authorization of prospective G3. This is NOT a WORM service:
GitHub administrators can delete releases, so permanent anti-rollback against
admin deletion is NOT ATTESTED. Loss of the witness must invalidate R8-D output.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile
from g2_production_boundary import (GateDenied, REPO, SOURCE_COMMIT, WitnessReceipt,
                                     sha, exact_json, safe_read)

SESSION_RE=re.compile(r'[A-Za-z0-9_-]{12,128}\Z')
DIGEST_RE=re.compile(r'[0-9a-f]{64}\Z')
ASSET='ttm-r8-g3-consumed-public.json'
TAG_PREFIX='ttm-vm-v4-r8-g3-consumed-'

class GitHubReleaseWitness:
    """One unique tag per session; signed remote release/asset readback.

    A competing or retried create fails because the tag/release is already in
    use; it must never overwrite/clobber. A deleted release can be recreated,
    so a separate accepted retention/invalidation policy is still mandatory.
    """
    def __init__(self, gh_binary: Path, scratch_root: Path, *, runner=None):
        self.gh=str(gh_binary)
        self.scratch=Path(scratch_root)
        self.runner=runner or subprocess.run

    def _run(self,args):
        try:
            out=self.runner([self.gh,*args],shell=False,timeout=35,
                            capture_output=True,text=True,check=False)
        except (OSError,subprocess.TimeoutExpired) as exc:
            raise GateDenied('EXTERNAL_GITHUB_WITNESS_UNAVAILABLE') from exc
        if out.returncode!=0 or len(out.stdout)>200000:
            raise GateDenied('EXTERNAL_GITHUB_WITNESS_OPERATION_FAILED')
        return out.stdout

    def _identity(self,session_id,digest=None):
        if type(session_id) is not str or not SESSION_RE.fullmatch(session_id):
            raise GateDenied('EXTERNAL_WITNESS_SESSION_INVALID')
        if digest is not None and (type(digest) is not str or not DIGEST_RE.fullmatch(digest)):
            raise GateDenied('EXTERNAL_WITNESS_DIGEST_INVALID')
        # Session-only tag, never digest-based: distinct digests MUST conflict.
        return TAG_PREFIX+sha(session_id.encode())[:40]

    def _payload(self,session_id,digest):
        return json.dumps({'schema':'TTM_VM_R8_ONE_SHOT_WITNESS_V1',
                           'session_id':session_id,'commitment_digest':digest,
                           'source_commit':SOURCE_COMMIT},
                          sort_keys=True,separators=(',',':')).encode('utf-8')

    def reserve_once(self,session_id,digest):
        tag=self._identity(session_id,digest)
        if not self.scratch.is_dir() or self.scratch.is_symlink():
            raise GateDenied('EXTERNAL_WITNESS_SCRATCH_NOT_AUTHORIZED')
        with tempfile.TemporaryDirectory(prefix='g3-public-witness-',dir=self.scratch) as tmp:
            asset=Path(tmp)/ASSET
            asset.write_bytes(self._payload(session_id,digest))
            # GitHub release creation is a write and can race: duplicate tag
            # creation MUST fail. No --clobber; never reuse an existing tag.
            self._run(['release','create',tag,str(asset),'-R',REPO,
                       '--target',SOURCE_COMMIT,'--prerelease',
                       '--title','TTM VM R8 G3 one-shot public witness',
                       '--notes','Public digest only. R8-D exploratory; no case/key/gold.'])
        return self.read_verified(session_id,digest)

    def read_verified(self,session_id,digest=None):
        tag=self._identity(session_id,digest)
        meta=json.loads(self._run(['api',f'repos/{REPO}/releases/tags/{tag}']))
        if (not isinstance(meta,dict) or meta.get('immutable') is not True or
            meta.get('tag_name')!=tag or type(meta.get('id')) is not int or
            not meta.get('published_at')):
            raise GateDenied('EXTERNAL_WITNESS_RELEASE_NOT_IMMUTABLE')
        assets=[a for a in meta.get('assets',[]) if isinstance(a,dict) and a.get('name')==ASSET]
        if len(assets)!=1 or not isinstance(assets[0].get('digest'),str):
            raise GateDenied('EXTERNAL_WITNESS_ASSET_UNPINNED')
        self._run(['release','verify',tag,'-R',REPO])
        with tempfile.TemporaryDirectory(prefix='g3-readback-',dir=self.scratch) as tmp:
            self._run(['release','download',tag,'-R',REPO,'--pattern',ASSET,'--dir',tmp])
            path=Path(tmp)/ASSET
            blob=safe_read(path,assets[0]['digest'].removeprefix('sha256:'))
            self._run(['release','verify-asset',tag,str(path),'-R',REPO])
        payload=exact_json(blob)
        if (not isinstance(payload,dict) or
            set(payload)!={'schema','session_id','commitment_digest','source_commit'} or
            payload['schema']!='TTM_VM_R8_ONE_SHOT_WITNESS_V1' or
            payload['session_id']!=session_id or payload['source_commit']!=SOURCE_COMMIT or
            (digest is not None and payload['commitment_digest']!=digest) or
            type(payload['commitment_digest']) is not str or
            not DIGEST_RE.fullmatch(payload['commitment_digest'])):
            raise GateDenied('EXTERNAL_WITNESS_DIGEST_IDENTITY_MISMATCH')
        # Signer identity validated via `gh release verify(-asset)` (GitHub).
        return WitnessReceipt(session_id,payload['commitment_digest'],
                              'github-immutable-release:'+str(meta['id']),True)

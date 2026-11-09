"""T6 off-host synthetic CPU QA; P02/P05/P06 source files unmodified."""
import io
import sys
import unittest
from contextlib import redirect_stderr
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.p02.transformer_core import GPT, P02Config
from src.p05.dense_kv_cache import DenseKVCache, dense_forward_tokens
from src.p06.paged_kv_manager import PagedKVCache, paged_forward_tokens
from tools.t6.cache_ab_benchmark_fixture import (
    WORKLOADS, PINNED_GIT_BLOBS, _cache_memory, _ensure_safe_output,
    dual_request_memory, forward_last, git_blob, measure_workload,
    new_cache, run_once, source_pins, validate_triplet,
)


class T6CacheABFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        torch.set_num_threads(2)
        torch.use_deterministic_algorithms(True)

    def setUp(self):
        torch.manual_seed(60609)
        self.m = GPT(P02Config(max_seq_len=32, n_embd=64, n_layer=2, n_head=4)).cpu().eval()

    def test_original_source_git_blobs_exact(self):
        pins = source_pins()
        self.assertEqual({k: v["git_blob"] for k,v in pins.items()}, PINNED_GIT_BLOBS)

    def test_correctness_short_medium_cross_pages(self):
        for name,spec in WORKLOADS.items():
            with self.subTest(workload=name):
                runs = {mode: run_once(self.m, mode, spec['prompt'], spec['continuation_tokens'])
                        for mode in ('no_cache','dense','paged')}
                result = validate_triplet(runs)
                self.assertEqual(result['paged']['matched_generated_tokens'],6)
                self.assertLess(result['paged']['max_abs_logit_error_vs_no_cache'],2e-5)

    def test_layernorm_and_rmsnorm_parity(self):
        for norm in ('layernorm','rmsnorm'):
            torch.manual_seed(60609)
            model = GPT(P02Config(norm_type=norm, max_seq_len=32)).cpu().eval()
            runs = {mode: run_once(model, mode, [12,2047,18,17,32],5,block_size=3)
                    for mode in ('no_cache','dense','paged')}
            self.assertEqual(len(validate_triplet(runs)),3)

    def test_cache_tpot_count_and_nonnegative_times(self):
        for mode in ('no_cache','dense','paged'):
            r=run_once(self.m, mode,[1,7,2047,9],6)
            self.assertEqual(len(r['tpot_step_ms']),5)
            self.assertGreater(r['ttft_ms'],0)
            self.assertTrue(all(t>0 for t in r['tpot_step_ms']))
            self.assertEqual(len(r['all_logits']),6)

    def test_no_cache_no_persistent_kv(self):
        r=run_once(self.m,'no_cache',[1,2,3],4)
        self.assertEqual(r['prefill_kv']['kv_pool_allocated_bytes'],0)
        self.assertEqual(r['after_decode_kv']['kv_used_logical_bytes'],0)

    def test_dense_exact_cache_bytes(self):
        cache=new_cache(self.m,'dense',block_size=4)
        cache.start('a')
        dense_forward_tokens(self.m,[1,2,3],cache,'a')
        bpt=2*2*4*16*4
        s=_cache_memory(cache,'dense')
        self.assertEqual(s['kv_used_logical_bytes'],3*bpt)
        self.assertEqual(s['kv_pool_allocated_bytes'],32*bpt)
        self.assertEqual(s['kv_request_reserved_bytes'],32*bpt)
        cache.release('a')
        self.assertEqual(cache.stats()['active_requests'],0)

    def test_paged_exact_cache_fragmentation_and_scrub(self):
        cache=new_cache(self.m,'paged',block_size=4)
        cache.start('a')
        paged_forward_tokens(self.m,[1,2,3,4,5],cache,'a')
        bpt=2*2*4*16*4
        s=_cache_memory(cache,'paged')
        self.assertEqual(s['kv_used_logical_bytes'],5*bpt)
        self.assertEqual(s['kv_request_reserved_bytes'],8*bpt)
        self.assertEqual(s['kv_fragmented_bytes'],3*bpt)
        self.assertEqual(s['kv_pool_allocated_bytes'],32*bpt)
        used=cache.page_table('a')
        cache.release('a')
        self.assertEqual(cache.stats()['used_blocks'],0)
        for pg in used:
            self.assertEqual(torch.count_nonzero(cache.storage[:,:,pg]).item(),0)

    def test_two_request_interleaved_isolation(self):
        result=dual_request_memory(self.m,block_size=4)
        self.assertTrue(result['zeroed_after_release'])
        self.assertEqual(result['request_tokens'],{'a':13,'b':5})
        self.assertEqual(result['paged']['kv_used_logical_bytes'],result['dense']['kv_used_logical_bytes'])

    def test_paged_out_of_memory_no_partial_append(self):
        p=PagedKVCache(n_layers=2,n_blocks=1,block_size=2,n_heads=4,head_dim=16,max_seq_len=32)
        p.start('a');p.start('b')
        paged_forward_tokens(self.m,[1,2],p,'a')
        before=p.stats().copy(); table=p.page_table('a');data=p.storage.clone()
        with self.assertRaises(MemoryError):
            paged_forward_tokens(self.m,[3,4,5],p,'b')
        self.assertEqual(before,p.stats())
        self.assertEqual(table,p.page_table('a'))
        torch.testing.assert_close(p.storage,data,atol=0,rtol=0)

    def test_invalid_token_rejected_without_allocation(self):
        p=new_cache(self.m,'paged',block_size=4);p.start('a')
        before=p.stats().copy()
        for tokens in ([2048],[-1],[True],[1.2],[]):
            with self.subTest(tokens=tokens):
                with self.assertRaises(ValueError):
                    paged_forward_tokens(self.m,tokens,p,'a')
        self.assertEqual(before,p.stats())

    def test_context_overflow_denied_before_append(self):
        p=new_cache(self.m,'paged',block_size=4);p.start('a')
        with self.assertRaises(ValueError):
            paged_forward_tokens(self.m,list(range(33)),p,'a')
        self.assertEqual(p.stats()['live_tokens'],0)
        d=new_cache(self.m,'dense',block_size=4);d.start('a')
        with self.assertRaises(ValueError):
            dense_forward_tokens(self.m,list(range(33)),d,'a')
        self.assertEqual(d.stats()['used_logical_bytes'],0)

    def test_bad_output_path_rejected(self):
        for path in ('/tmp/x.json','../x.json','artifacts/qa/wrong/x.json','artifacts/qa/t6/bad.txt',
                     'artifacts/qa/t6/../../secrets.json','C:\\x.json'):
            with self.subTest(path=path):
                with self.assertRaises(ValueError):_ensure_safe_output(path)

    def test_repeat_measurement_samples_present(self):
        r=measure_workload(self.m,'short',WORKLOADS['short'],repeats=2,warmups=0,block_size=4)
        for mode in ('no_cache','dense','paged'):
            perf=r['performance'][mode]
            self.assertGreater(perf['ttft']['median_ms'],0)
            self.assertGreater(perf['tpot_per_request_mean_ms']['median_ms'],0)
            self.assertEqual(r['measured_repeats_per_mode'],2)

    def test_guard_detects_generated_token_drift(self):
        runs={m:run_once(self.m,m,[1,2,3],4) for m in ('no_cache','dense','paged')}
        runs['paged']['generated_tokens'][0] = (runs['paged']['generated_tokens'][0]+1)%2048
        with self.assertRaisesRegex(AssertionError,'GENERATED_TOKEN_IDS_DIFFER'):
            validate_triplet(runs)

    def test_guard_detects_logits_corruption(self):
        runs={m:run_once(self.m,m,[1,2,3],4) for m in ('no_cache','dense','paged')}
        # Inference-mode tensors are immutable outside InferenceMode; make a safe normal copy.
        corrupted = runs['dense']['all_logits'][0].clone()
        with torch.inference_mode():
            corrupted[0] += 10
        runs['dense']['all_logits'][0] = corrupted
        with self.assertRaisesRegex(AssertionError,'LOGITS_PARITY_FAIL'):
            validate_triplet(runs)

    def test_train_mode_not_benchmark_eligible(self):
        self.m.train()
        with self.assertRaises(ValueError):run_once(self.m,'dense',[1,2],3)


if __name__=='__main__':unittest.main()

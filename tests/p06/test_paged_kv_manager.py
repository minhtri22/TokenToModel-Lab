"""P06 synthetic CPU functional QA; no corpus, optimizer, checkpoint, or P07 GPU."""
import math
from pathlib import Path
import sys
import unittest

import torch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from src.p02.transformer_core import GPT, P02Config
from src.p05.dense_kv_cache import DenseKVCache, dense_forward_tokens
from src.p06.paged_kv_manager import PagedKVCache, paged_forward_tokens, benchmark_paged_vs_dense


class P06PagedKVTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        torch.set_num_threads(2)

    def setUp(self):
        torch.manual_seed(606)
        self.cfg = P02Config()
        self.model = GPT(self.cfg).eval()

    def cache(self, **kw):
        return PagedKVCache(n_layers=2, n_blocks=16, block_size=3,
                            n_heads=4, head_dim=16, max_seq_len=32,
                            max_requests=3, **kw)

    def test_logits_agree_p05_dense_and_p02_uncached_cross_pages(self):
        for norm in ('layernorm', 'rmsnorm'):
            torch.manual_seed(61)
            model = GPT(P02Config(norm_type=norm)).eval()
            paged = self.cache()
            dense = DenseKVCache(n_layers=2, max_seq_len=32, n_heads=4,
                                 head_dim=16, max_requests=1)
            paged.start('a'); dense.start('a')
            ids = [256, 2047, 2, 10, 1023, 8, 777, 12, 1499, 42]
            for idx, token in enumerate(ids, 1):
                with self.subTest(norm=norm,position=idx):
                    a = paged_forward_tokens(model, [token], paged, 'a')
                    b = dense_forward_tokens(model, [token], dense, 'a')
                    full, _ = model(torch.tensor([ids[:idx]]))
                    torch.testing.assert_close(a, b, atol=2e-5, rtol=2e-5)
                    torch.testing.assert_close(a, full[0, -1], atol=2e-5, rtol=2e-5)
            self.assertEqual(paged.page_table('a'), (0, 1, 2, 3))
            dense.release('a'); paged.release('a')

    def test_interleaved_requests_and_release_reuse_scrub(self):
        p = self.cache()
        p.start('one'); p.start('two')
        streams = {'one': [0, 256, 700, 2047, 88], 'two': [500, 1900, 12, 19, 20, 30]}
        seen = {'one': [], 'two': []}
        for step in range(6):
            for r in ('one', 'two'):
                if step < len(streams[r]):
                    seen[r].append(streams[r][step])
                    got = paged_forward_tokens(self.model, [streams[r][step]], p, r)
                    full, _ = self.model(torch.tensor([seen[r]]))
                    torch.testing.assert_close(got, full[0, -1], atol=2e-5, rtol=2e-5)
            tables = (set(p.page_table('one')), set(p.page_table('two')))
            self.assertFalse(tables[0] & tables[1])
        freed = p.page_table('one')
        p.release('one')
        for page in freed:
            self.assertEqual(torch.count_nonzero(p.storage[:, :, page]).item(), 0)
        p.start('three')
        paged_forward_tokens(self.model, [777, 19, 101], p, 'three')
        self.assertFalse(set(p.page_table('two')) & set(p.page_table('three')))
        p.release('two'); p.release('three')
        stats = p.stats()
        self.assertEqual(stats['used_blocks'], 0)
        self.assertEqual(stats['free_blocks'], 16)
        self.assertEqual(torch.count_nonzero(p.storage).item(), 0)

    def test_fragmentation_and_page_statistics_are_exact(self):
        p = PagedKVCache(n_layers=2, n_blocks=5, block_size=4,
                         n_heads=4, head_dim=16, max_seq_len=20)
        p.start('a'); p.start('b')
        p.allocate_token('a')
        for _ in range(5):p.allocate_token('b')
        s=p.stats()
        self.assertEqual((s['total_blocks'],s['used_blocks'],s['free_blocks']),(5,3,2))
        self.assertEqual((s['live_tokens'],s['reserved_slots'],s['fragmented_slots']),(6,12,6))
        self.assertEqual(s['bytes_per_token'],2*2*4*16*4)
        self.assertEqual(s['fragmented_bytes'],6*s['bytes_per_token'])
        self.assertEqual(s['reserved_bytes'],s['used_logical_bytes']+s['fragmented_bytes'])
        self.assertEqual(s['allocated_bytes'],s['total_blocks']*4*s['bytes_per_token'])
        p.release('a');p.release('b')
        self.assertEqual(p.stats()['fragmented_slots'],0)

    def test_oom_and_context_preflight_do_not_mutate(self):
        p = PagedKVCache(n_layers=2,n_blocks=1,block_size=2,n_heads=4,
                         head_dim=16,max_seq_len=6,max_requests=2)
        p.start('a');p.start('b')
        paged_forward_tokens(self.model,[2,3],p,'a')
        before=(p.stats().copy(),p.page_table('a'),p.page_table('b'),p.storage.clone())
        with self.assertRaises(MemoryError):
            paged_forward_tokens(self.model,[9, 10, 11],p,'b')
        with self.assertRaises(MemoryError):
            paged_forward_tokens(self.model,[7],p,'a')
        self.assertEqual(p.stats(),before[0]);self.assertEqual(p.page_table('a'),before[1]);self.assertEqual(p.page_table('b'),before[2])
        torch.testing.assert_close(p.storage,before[3],atol=0,rtol=0)
        # Context preflight is rejected before any mutation even when a free block exists.
        q=PagedKVCache(n_layers=2,n_blocks=3,block_size=2,n_heads=4,
                       head_dim=16,max_seq_len=2)
        q.start('q')
        with self.assertRaises(ValueError):
            paged_forward_tokens(self.model,[1,2,3],q,'q')
        self.assertEqual(q.stats()['used_blocks'],0)

    def test_invalid_inputs_do_not_write_to_storage(self):
        p=self.cache();p.start('a')
        before=p.storage.clone()
        for v in ([2048],[-1],[1.0],[],[True]):
            with self.assertRaises(ValueError):paged_forward_tokens(self.model,v,p,'a')
        for v in ('',0,None):
            with self.assertRaises(ValueError):p.start(v)
        with self.assertRaises(ValueError):p.start('a')
        with self.assertRaises(KeyError):p.allocate_token('bad')
        with self.assertRaises(KeyError):p.release('bad')
        with self.assertRaises(IndexError):p.write(0,'a',0,torch.zeros(4,16),torch.zeros(4,16))
        with self.assertRaises(IndexError):p.read(-1,'a')
        p.allocate_token('a')
        with self.assertRaises(ValueError):p.write(0,'a',0,torch.ones(4,16,dtype=torch.float64),torch.ones(4,16))
        with self.assertRaises(ValueError):p.write(0,'a',0,torch.ones(3,16),torch.ones(4,16))
        torch.testing.assert_close(p.storage,before,atol=0,rtol=0)
        with self.assertRaises(ValueError):PagedKVCache(n_layers=2,n_blocks=1,block_size=4,n_heads=4,head_dim=16,max_allocated_bytes=1)

    def test_read_page_table_is_immutable_and_request_scoped(self):
        p=self.cache();p.start('a');p.start('b')
        self.assertEqual(tuple(p.page_table('a')),tuple())
        self.assertEqual(p.read(0,'a')[0].shape,(0,4,16))
        for _ in range(4):p.allocate_token('a')
        for _ in range(2):p.allocate_token('b')
        self.assertFalse(set(p.page_table('a')) & set(p.page_table('b')))
        table=p.page_table('a');self.assertIsInstance(table,tuple)
        with self.assertRaises(AttributeError):table.append(4)
        a=p.read(0,'a')[0]
        self.assertEqual(tuple(a.shape),(4,4,16))
        # Copies returned to caller must not allow writing back into shared pool.
        a.fill_(5)
        self.assertEqual(torch.count_nonzero(p.storage).item(),0)
        with self.assertRaises(KeyError):p.page_table('unknown')
        with self.assertRaises(IndexError):p.write(0,'a',4,torch.zeros(4,16),torch.zeros(4,16))

    def test_multitoken_append_matches_tokenwise_and_no_misrouting(self):
        p=self.cache(); q=self.cache();p.start('a');q.start('a')
        ids=[2047,256,1,800,4,1200,9]
        batched=paged_forward_tokens(self.model,ids,p,'a')
        for v in ids:
            sequential=paged_forward_tokens(self.model,[v],q,'a')
        torch.testing.assert_close(batched,sequential,atol=0,rtol=0)
        self.assertEqual(p.page_table('a'),q.page_table('a'))
        self.assertEqual(p.stats(),q.stats())

    def test_benchmark_measurements_are_synthetic_not_speedup_claim(self):
        report=benchmark_paged_vs_dense(self.model,[1,256,2047,3,7,99],block_size=4,repeats=2)
        self.assertEqual(report['status'],'P06_CPU_MEASURED_NO_SPEEDUP_CLAIM')
        self.assertEqual(report['sequence_length'],6)
        self.assertEqual(report['repeats'],2)
        self.assertEqual(report['used_logical_bytes'],6*2*2*4*16*4)
        self.assertEqual(report['fragmented_bytes'],2*2*2*4*16*4)
        for k in ('dense_ms','paged_ms','recompute_ms'):
            self.assertEqual(len(report[k]),2)
            self.assertTrue(all(math.isfinite(t) and t>0 for t in report[k]))
        for k in ('dense_allocated_bytes','paged_allocated_bytes'):
            self.assertGreater(report[k],0)
        with self.assertRaises(ValueError):benchmark_paged_vs_dense(self.model,[1],repeats=0)


if __name__=='__main__':unittest.main()

"""Track B B0/B1 author QA; no private data, no science."""
from __future__ import annotations
from copy import deepcopy
from dataclasses import asdict
import json
from pathlib import Path
import tempfile
import unittest
import torch
from torch.nn import functional as F
from src.p02.transformer_core import GPT, P02Config
from src.p03.train_loop import TrainConfig,scheduled_lr
from src.ttm_track_b import scaffold as b
from src.ttm_track_b import cli

CFG=json.loads((Path(__file__).resolve().parents[1]/'configs/ttm/track_b_synthetic_smoke.json').read_text('utf-8'))

class TestContracts(unittest.TestCase):
    def setUp(self):
        torch.set_num_threads(2)
        self.pack=b.prepare(CFG)

    def test_01_byte_roundtrip_eos_and_group_disjoint(self):
        self.assertTrue(b.validate_pack(self.pack,16,self.pack['data_sha256']))
        self.assertEqual(self.pack['tokenizer']['eos_id'],256)
        self.assertTrue(set(x['group_id'] for x in self.pack['splits']['TRAIN']).isdisjoint(x['group_id'] for x in self.pack['splits']['VAL']))
        self.assertEqual(sum(x['utf8_bytes'] for x in self.pack['splits']['VAL']),84)

    def test_02_reject_tokenizer_tamper(self):
        pack=deepcopy(self.pack);pack['tokenizer']['eos_id']=0
        with self.assertRaisesRegex(ValueError,'TOKENIZER'):b.validate_pack(pack,16)

    def test_03_reject_split_overlap(self):
        pack=deepcopy(self.pack);pack['splits']['VAL'][0]['group_id']=pack['splits']['TRAIN'][0]['group_id']
        with self.assertRaisesRegex(ValueError,'SPLIT_OVERLAP'):b.validate_pack(pack,16)

    def test_04_reject_off_by_one_y(self):
        pack=deepcopy(self.pack);pack['windows']['TRAIN'][0]['y'][0]=255
        with self.assertRaisesRegex(ValueError,'SHIFTED_TARGET_ALIGNMENT|SOURCE_BYTE_SHA'):b.validate_pack(pack,16)

    def test_05_reject_padding_unmasked(self):
        pack=deepcopy(self.pack)
        short=next(w for w in pack['windows']['TRAIN'] if w['valid']<16)
        short['y'][-1]=1
        with self.assertRaisesRegex(ValueError,'MASK_OR_PADDING'):b.validate_pack(pack,16)

    def test_06_reject_data_manifest_hash(self):
        pack=deepcopy(self.pack);pack['data_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'DATA_HASH'):b.validate_pack(pack,16,pack['data_sha256'])

    def test_07_loss_ignore_exact_reference(self):
        logits=torch.tensor([[[3.,0.,1.], [0.,1.,3.], [1.,2.,3.]]],requires_grad=True)
        targets=torch.tensor([[0,2,-100]])
        actual=b.cross_entropy_valid(logits,targets)
        oracle=(F.cross_entropy(logits[0,0],torch.tensor(0))+F.cross_entropy(logits[0,1],torch.tensor(2)))/2
        self.assertAlmostEqual(actual.item(),oracle.item(),places=6)
        actual.backward();self.assertTrue(torch.equal(logits.grad[0,2],torch.zeros(3)))

    def test_08_reject_bad_ignore_label(self):
        with self.assertRaisesRegex(ValueError,'BAD_IGNORE'):
            b.cross_entropy_valid(torch.zeros(1,2,3),torch.tensor([[0,-1]]))

    def test_09_causal_future_isolation(self):
        torch.manual_seed(1)
        model=GPT(P02Config(vocab_size=2048,max_seq_len=16,n_embd=32,n_layer=1,n_head=4))
        model.eval()
        x=torch.tensor([[3,4,5,6,7]],dtype=torch.long)
        alt=x.clone();alt[0,-1]=34
        with torch.inference_mode():
            a=model(x)[0];c=model(alt)[0]
        self.assertTrue(torch.allclose(a[:,:-1],c[:,:-1],atol=0,rtol=0))
        self.assertGreater(float((a[:,-1]-c[:,-1]).abs().max()),0)

    def test_10_accumulation_matches_fullbatch(self):
        model,opt,sch,samp=b.train_state(CFG)
        x,y=b.sample_batch(self.pack,samp,4)
        reference=deepcopy(model);accum=deepcopy(model)
        def calc(m,chunks):
            m.zero_grad(set_to_none=True)
            valid=int((y!=-100).sum())
            for a,bb in chunks:
                logits,_=m(x[a:bb])
                (F.cross_entropy(logits.reshape(-1,2048),y[a:bb].reshape(-1),ignore_index=-100,reduction='sum')/valid).backward()
            return [p.grad.detach().clone() for p in m.parameters()]
        direct=calc(reference,[(0,4)]);micro=calc(accum,[(0,2),(2,4)])
        maximum=max(float((v-w).abs().max()) for v,w in zip(direct,micro))
        self.assertLess(maximum,2e-6,'Predeclared FP32 gradient abs tol 2e-6')

    def test_11_lr_warmup_cosine(self):
        tr=TrainConfig(steps=8,peak_lr=.003,warmup_steps=2,min_lr_ratio=.1)
        self.assertAlmostEqual(scheduled_lr(0,tr),.0015)
        self.assertAlmostEqual(scheduled_lr(1,tr),.003)
        self.assertAlmostEqual(scheduled_lr(7,tr),.0003)
        self.assertTrue(all(scheduled_lr(i,tr)>=.0003-1e-12 for i in range(8)))

    def test_12_weight_delta_grad_finite_and_clip(self):
        model,opt,sch,sampler=b.train_state(CFG)
        old=next(model.parameters()).detach().clone()
        met=b.train_step(model,opt,sch,sampler,self.pack,CFG)
        self.assertTrue(all(torch.isfinite(p).all().item() for p in model.parameters()))
        self.assertGreater(met['valid_targets'],0)
        self.assertGreater(met['raw_grad_norm'],0)
        self.assertGreater(float((next(model.parameters()).detach()-old).abs().max()),0)

    def test_13_overfit_fixed_one_window(self):
        cfg={**CFG,'steps':32,'peak_lr':.008,'weight_decay':0.0}
        model,opt,sch,sampler=b.train_state(cfg)
        pack=deepcopy(b.prepare(cfg))
        one=pack['windows']['TRAIN'][0]
        pack['windows']['TRAIN']=[one]
        x=torch.tensor([one['x']],dtype=torch.long);y=torch.tensor([one['y']],dtype=torch.long)
        with torch.no_grad(): initial=float(b.cross_entropy_valid(model(x)[0],y).item())
        for _ in range(32):b.train_step(model,opt,sch,sampler,pack,cfg)
        with torch.no_grad(): final=float(b.cross_entropy_valid(model(x)[0],y).item())
        self.assertLess(final,initial)

    def test_14_resume_exact_8_vs_3_plus_5(self):
        cfg=CFG
        cfg_hash=b.digest(b.canonical(cfg)); data_hash=self.pack['data_sha256']
        m1,o1,s1,g1=b.train_state(cfg)
        m2,o2,s2,g2=b.train_state(cfg)
        losses1=[];losses2=[]
        for i in range(8):losses1.append(b.train_step(m1,o1,s1,g1,self.pack,cfg)['train_loss'])
        for i in range(3):losses2.append(b.train_step(m2,o2,s2,g2,self.pack,cfg)['train_loss'])
        with tempfile.TemporaryDirectory() as tmp:
            file=Path(tmp)/'ckpt.pt'
            sha=b.save_training_checkpoint(file,b.checkpoint_payload(m2,o2,s2,g2,3,cfg_hash,data_hash))
            m3,o3,s3,g3=b.train_state(cfg)
            self.assertEqual(b.load_training_checkpoint(file,sha,m3,o3,s3,g3,cfg_hash,data_hash),3)
            for i in range(5):losses2.append(b.train_step(m3,o3,s3,g3,self.pack,cfg)['train_loss'])
            self.assertEqual(losses1,losses2)
            self.assertTrue(all(torch.equal(a,bb) for a,bb in zip(m1.parameters(),m3.parameters())))
            self.assertEqual(s1.state_dict(),s3.state_dict())
            self.assertEqual(o1.param_groups[0]['lr'],o3.param_groups[0]['lr'])
            self.assertTrue(torch.equal(g1.get_state(),g3.get_state()))
            with self.assertRaises(FileExistsError):b.save_training_checkpoint(file,{})
            with self.assertRaisesRegex(ValueError,'SHA_MISMATCH'):
                b.load_training_checkpoint(file,'0'*64,m3,o3,s3,g3,cfg_hash,data_hash)

    def test_15_p04_exact_schema_adapter(self):
        cfg=dict(vocab_size=2048,max_seq_len=16,n_embd=32,n_layer=1,n_head=4,norm_type='layernorm')
        model=GPT(P02Config(**cfg));tok_sha='a'*64
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'historical_p04.pt'
            torch.save({'schema':b.P04_SCHEMA,'config':cfg,'bpe_merges_sha256':tok_sha,'state_dict':model.state_dict()},path)
            sha=b.file_hash(path)
            loaded=b.read_historical_checkpoint(path,sha,cfg,tok_sha,schema=b.P04_SCHEMA,root=d)
            self.assertTrue(all(torch.equal(a,bb) for a,bb in zip(model.parameters(),loaded.parameters())))
            with self.assertRaisesRegex(ValueError,'P04_TOKENIZER'):b.read_historical_checkpoint(path,sha,cfg,'f'*64,schema=b.P04_SCHEMA,root=d)
            with self.assertRaisesRegex(ValueError,'HISTORICAL_CONFIG'):b.read_historical_checkpoint(path,sha,{**cfg,'n_embd':64},tok_sha,schema=b.P04_SCHEMA,root=d)

    def test_16_t4_exact_schema_adapter(self):
        # Synthetic T4-shaped checkpoint (3,749,376 params), never original model weights.
        model=GPT(P02Config(**b.T4_CONFIG));pack_sha='c'*64
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'synthetic_t4.pt'
            torch.save({'schema':b.T4_SCHEMA,'config':b.T4_CONFIG,'model':model.state_dict(),
                        'p02_git_blob':b.P02_GIT_BLOB,'science_lock_sha256':'a'*64,
                        'train_pack_sha256':pack_sha},path)
            sha=b.file_hash(path)
            loaded=b.read_historical_checkpoint(path,sha,b.T4_CONFIG,pack_sha,schema=b.T4_SCHEMA,root=d)
            self.assertEqual(sum(p.numel() for p in loaded.parameters()),3749376)
            with self.assertRaisesRegex(ValueError,'T4_PACK_PIN'):
                b.read_historical_checkpoint(path,sha,b.T4_CONFIG,'f'*64,schema=b.T4_SCHEMA,root=d)

    def test_17_val_full_vocab_nll_byte_denominator_reference(self):
        model,*_=b.train_state(CFG)
        result=b.evaluate(model,self.pack)
        self.assertEqual(result['scored_target_tokens'],84)
        self.assertEqual(result['scored_utf8_bytes_excluding_first_byte_and_eos'],81)
        total=0.0;bytes_sum=0
        with torch.no_grad():
            for win in self.pack['windows']['VAL']:
                logits=model(torch.tensor([win['x']]))[0][0]
                for i,t in enumerate(win['y']):
                    if t!=-100 and t!=256:
                        total+=float((torch.logsumexp(logits[i].double(),0)-logits[i,t].double()).item())
                        bytes_sum+=1
        self.assertAlmostEqual(result['bpb_excluding_first_byte_and_eos'],total/(bytes_sum*__import__('math').log(2)),places=6)

    def test_18_sampling_deterministic_context(self):
        model,*_=b.train_state(CFG)
        self.assertEqual(b.sample(model,[65],6,13,4),b.sample(model,[65],6,13,4))
        with self.assertRaisesRegex(ValueError,'CONTEXT_EXCEEDED'):b.sample(model,[2]*16,1)

    def test_19_cli_end_to_end_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/'run'; cfg_hash=b.digest(b.canonical(CFG))
            cli.prepare(out,CFG,cfg_hash)
            partial=cli.run_train(out,CFG,cfg_hash,3,0,120)
            finished=cli.run_train(out,CFG,cfg_hash,8,3,120)
            self.assertGreater(finished['max_parameter_delta'],0)
            m,pack=cli.finished_model(out,CFG,cfg_hash,8)
            self.assertEqual(b.evaluate(m,pack)['scored_target_tokens'],84)
            with self.assertRaises(FileExistsError):cli.prepare(out,CFG,cfg_hash)
            with self.assertRaises(FileExistsError):cli.run_train(out,CFG,cfg_hash,8,3,120)

    def test_20_wrong_config_pin_rejects_resume(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/'run';cfg_hash=b.digest(b.canonical(CFG))
            cli.prepare(out,CFG,cfg_hash)
            cli.run_train(out,CFG,cfg_hash,3,0,120)
            with self.assertRaisesRegex(ValueError,'RUN_INPUT_PIN'):
                cli.run_train(out,CFG,'f'*64,8,3,120)

    def test_21_reject_label_leak(self):
        # Label at masked position must not contribute to loss/gradient.
        logits=torch.randn(1,2,2048,requires_grad=True)
        targets=torch.tensor([[7,-100]])
        loss=b.cross_entropy_valid(logits,targets);loss.backward()
        self.assertTrue(torch.all(logits.grad[:,1]==0).item())
        leak=targets.clone();leak[0,1]=7
        self.assertNotEqual(float(b.cross_entropy_valid(logits.detach(),targets).item()),float(b.cross_entropy_valid(logits.detach(),leak).item()))

if __name__=='__main__':unittest.main()

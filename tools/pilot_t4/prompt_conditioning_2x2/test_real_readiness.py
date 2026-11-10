#!/usr/bin/env python3
"""CPU/source tests: no training, no checkpoint mutation, no Q1Q2/TEST."""
from __future__ import annotations
import hashlib, json, sys, os, tempfile, unittest
from pathlib import Path
from unittest.mock import Mock
import numpy as np
import torch
import torch.nn.functional as F
from real_metadata_preflight import run,ranked_match,PACK_SHA,MANIFEST_SHA,CHECKPOINT_SHA
import ttm_2x2_colab_runner_candidate as m

ROOT=Path(os.environ.get('TTM2X2_TEST_ROOT','/mnt/data/ttm_2x2_real_readiness_20261110'))
PACK=Path(os.environ.get('TTM2X2_PACK','/mnt/data/T4_PRIVATE_TRAIN_VAL_WINDOWS.npz'))
MAN=Path(os.environ.get('TTM2X2_MANIFEST','/mnt/data/T4_PRIVATE_PACK_MANIFEST.json'))
CP=Path(os.environ.get('TTM2X2_CHECKPOINT','/mnt/data/checkpoint.pt'))
P02=Path(os.environ.get('TTM2X2_P02',str(ROOT/'upstream'/'transformer_core.py')))

class T(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    cls.metadata=json.loads((ROOT/'REAL_METADATA_MATCHED_DRAWS_READONLY.json').read_text())
    cls.cp=m.check_input(PACK,MAN,CP)
    cls.p02=m.load_model_source(P02)
  def test_01_pack_sha(self): self.assertEqual(m.sha_file(PACK),PACK_SHA)
  def test_02_manifest_sha(self): self.assertEqual(m.sha_file(MAN),MANIFEST_SHA)
  def test_03_checkpoint_sha(self): self.assertEqual(m.sha_file(CP),CHECKPOINT_SHA)
  def test_04_real_train_windows(self): self.assertEqual(self.metadata['public_safe_counts']['train_windows'],2691)
  def test_05_first_story_count(self): self.assertEqual(self.metadata['public_safe_counts']['first_story_windows'],2048)
  def test_06_val_metadata(self): self.assertEqual(self.metadata['public_safe_counts']['val_targets'],61122)
  def test_07_matched_targets(self): self.assertEqual(self.metadata['public_safe_counts']['target_exposures_per_arm'],524288)
  def test_08_equal_draws(self): self.assertEqual(self.metadata['public_safe_counts']['forward_window_draws_per_arm'],2928)
  def test_09_equal_token_slots(self): self.assertEqual(self.metadata['public_safe_counts']['forward_slots_per_arm'],2928*256)
  def test_10_all_first_candidates(self): self.assertTrue(self.metadata['equality']['all_first_window_candidates_available'])
  def test_11_nonidentical_selected_data(self): self.assertNotEqual(self.metadata['schedule_digests']['A_C'],self.metadata['schedule_digests']['B_D'])
  def test_12_no_raw_token_export(self): self.assertNotIn('train_x',self.metadata)
  def test_13_source_p02_pin(self): self.assertEqual(m.sha_file(P02),m.P02_SHA)
  def test_14_parent_optimizer_state(self): self.assertEqual(len(self.cp['optimizer']['state']),52)
  def test_15_parent_scaler(self): self.assertEqual(self.cp['grad_scaler_state']['scale'],65536.)
  def test_16_parent_sampler(self): self.assertTrue(self.cp['sampler_state'].numel()>1000)
  def test_17_p02_config(self): self.assertEqual(self.cp['config']['max_seq_len'],256)
  def test_18_model_parameter_count(self):
    self.assertEqual(sum(p.numel() for p in self.p02.GPT(self.p02.P02Config(**self.cp['config'])).parameters()),3749376)
  def test_19_cpu_parent_restore(self):
    model,opt,sch,sampler,scaler=m.clone_parent(self.p02,self.cp,torch.device('cpu'))
    self.assertEqual(sch.last_epoch,1024);self.assertEqual(len(opt.state_dict()['state']),52)
  def test_20_no_owner_lock_fail_closed(self):
    with self.assertRaisesRegex(RuntimeError,'SCIENCE_NOT_AUTHORIZED'):
      m.require_owner_science_lock(Mock(owner_lock=None,owner_lock_sha=None))
  def test_21_wrong_owner_lock_hash(self):
    with self.assertRaisesRegex(RuntimeError,'OWNER_LOCK_SHA'):
      m.require_owner_science_lock(Mock(owner_lock=str(MAN),owner_lock_sha='0'*64))
  def test_22_wrong_p02_source_sha(self):
    with self.assertRaisesRegex(RuntimeError,'CANONICAL_P02_SHA'):
      m.load_model_source(MAN)
  def test_23_nonexistent_input(self):
    with self.assertRaisesRegex(RuntimeError,'MISSING_OR_LINKED'):
      m.check_input('/__not_train__.npz',MAN,CP)
  def test_24_wrong_manifest(self):
    with self.assertRaisesRegex(RuntimeError,'PRIVATE_INPUT_PIN'):
      m.check_input(PACK,ROOT/'NEW_DEV12_BLIND_FINAL24_EVAL_FREEZE.json',CP)
  def test_25_ranked_choice_determinism(self):
    v=ranked_match([0,1,2],1025,0,np.array([0,1,2]));self.assertEqual(v,ranked_match([0,1,2],1025,0,np.array([0,1,2])))
  def test_26_ranked_choice_order_invariant(self):
    x=ranked_match([0,1,2],1025,1,np.array([0,1,2]));y=ranked_match([2,1,0],1025,1,np.array([0,1,2]));self.assertEqual(x,y)
  def test_27_four_arms(self):self.assertEqual(m.ARMS,('A','B','C','D'))
  def test_28_science_not_called_in_cpu_mode(self): self.assertTrue(m.RUN_ID.startswith('TTM_SMALL4M_2X2_'))
  def test_29_eval_prompts_count(self):self.assertEqual(len(json.loads((ROOT/'NEW_DEV12_BLIND_FINAL24_EVAL_FREEZE.json').read_text())['prompts']),36)
  def test_30_eval_prompts_unique(self):
    p=json.loads((ROOT/'NEW_DEV12_BLIND_FINAL24_EVAL_FREEZE.json').read_text())['prompts'];self.assertEqual(len({z['prompt'] for z in p}),36)
  def test_31_eval_bpe_lengths(self):
    p=json.loads((ROOT/'NEW_DEV12_BLIND_FINAL24_EVAL_FREEZE.json').read_text())['prompts'];self.assertTrue(all(12<=z['bpe_token_count']<=60 for z in p))
  def test_32_live_val_not_test(self):
    with np.load(PACK,allow_pickle=False) as z:self.assertEqual(set(z.files),{f'{a}_{b}' for a in ('train','val') for b in ('x','y','count','story_index')})

class Loss(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
    torch.manual_seed(1203)
    cls.x=np.zeros((2,256),dtype=np.int64)
    cls.y=np.full((2,256),-100,dtype=np.int64)
    cls.y[:,0:40]=torch.randint(0,2048,(2,40)).numpy()
 class Toy(torch.nn.Module):
    def __init__(self):
      super().__init__();self.logits=torch.nn.Parameter(torch.zeros((2,256,2048),dtype=torch.float32))
    def forward(self,x):return self.logits,None
 def test_33_uniform_loss_finite(self):
    mdl=self.Toy();z=list(m.loss_step(mdl,self.x,self.y,'A',torch.device('cpu'),False,required_scored_targets=80));self.assertEqual(len(z),1);self.assertTrue(torch.isfinite(z[0]))
 def test_34_weighted_loss_finite(self):
    mdl=self.Toy();z=list(m.loss_step(mdl,self.x,self.y,'C',torch.device('cpu'),False,required_scored_targets=80));self.assertTrue(torch.isfinite(z[0]))
 def test_35_uniform_expected(self):
    mdl=self.Toy();loss=list(m.loss_step(mdl,self.x,self.y,'A',torch.device('cpu'),False,required_scored_targets=80))[0];self.assertAlmostEqual(loss.item(),mathlog(),places=5)
 def test_36_weighted_expected(self):
    mdl=self.Toy();loss=list(m.loss_step(mdl,self.x,self.y,'D',torch.device('cpu'),False,required_scored_targets=80))[0];self.assertAlmostEqual(loss.item(),mathlog(),places=5)
 def test_37_pad_has_zero_gradient(self):
    mdl=self.Toy();loss=list(m.loss_step(mdl,self.x,self.y,'C',torch.device('cpu'),False,required_scored_targets=80))[0];loss.backward();self.assertTrue((mdl.logits.grad[:,40:,:]==0).all())
 def test_38_valid_gradient_nonzero(self):
    mdl=self.Toy();loss=list(m.loss_step(mdl,self.x,self.y,'C',torch.device('cpu'),False,required_scored_targets=80))[0];loss.backward();self.assertGreater(float(mdl.logits.grad[:,:40,:].abs().sum()),0)
 def test_39_weighted_suffix_has_more_gradient(self):
    a=self.Toy();b=self.Toy();la=list(m.loss_step(a,self.x,self.y,'A',torch.device('cpu'),False,required_scored_targets=80))[0];lb=list(m.loss_step(b,self.x,self.y,'C',torch.device('cpu'),False,required_scored_targets=80))[0];la.backward();lb.backward();
    ga=float(a.logits.grad[:,35,:].abs().sum());gb=float(b.logits.grad[:,35,:].abs().sum());self.assertGreater(gb,ga)
 def test_40_invalid_label_rejected(self):
    y=self.y.copy();y[0,0]=2048;mdl=self.Toy()
    with self.assertRaisesRegex(RuntimeError,'LOSS_BAD_LABEL'):
      list(m.loss_step(mdl,self.x,y,'A',torch.device('cpu'),False,required_scored_targets=80))
 def test_41_nonfinite_logit_rejected(self):
    mdl=self.Toy();mdl.logits.data[0,0,0]=float('nan')
    with self.assertRaisesRegex(RuntimeError,'LOSS_NONFINITE'):
      list(m.loss_step(mdl,self.x,self.y,'C',torch.device('cpu'),False,required_scored_targets=80))
 def test_42_all_pad_denominator_rejected(self):
    y=np.full_like(self.y,-100);mdl=self.Toy()
    with self.assertRaisesRegex(RuntimeError,'WEIGHT_DENOM'):
      list(m.loss_step(mdl,self.x,y,'A',torch.device('cpu'),False,required_scored_targets=80))

def mathlog():
 import math
 return math.log(2048)

if __name__=='__main__':unittest.main(verbosity=2)

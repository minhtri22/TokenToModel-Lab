#!/usr/bin/env python3
"""Independent scoped unit/negative tests for synthetic 2x2 preflight only.

No real TRAIN/VAL/TEST, checkpoint or optimizer updates. No model is trained.
"""
from __future__ import annotations

import hashlib
import math
import unittest
from dataclasses import replace

import torch
from torch.nn import functional as F

import ttm_2x2_equal_budget_synthetic as m


class FixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ws=m.synthetic_windows()

    def test_01_fixture_is_train_only(self):
        self.assertEqual({w.split for w in self.ws},{'TRAIN'})
    def test_02_fixture_has_40_stories(self):
        self.assertEqual(len({w.story_id for w in self.ws}),40)
    def test_03_fixture_has_64_windows(self):
        self.assertEqual(len(self.ws),64)
    def test_04_first_windows_exact(self):
        self.assertEqual(sum(w.offset==0 for w in self.ws),40)
    def test_05_later_windows_exact(self):
        self.assertEqual(sum(w.offset!=0 for w in self.ws),24)
    def test_06_valid_lengths_bounded(self):
        self.assertTrue(all(0<w.count<=256 for w in self.ws))
    def test_07_at_least_one_full_length_candidate(self):
        self.assertGreater(sum(w.offset==0 and w.count==256 for w in self.ws),0)
    def test_08_padding_targets_ignored(self):
        self.assertTrue(all(all(y==-100 for y in w.y[w.count:]) for w in self.ws))
    def test_09_label_shift_valid(self):
        self.assertTrue(all(all(w.y[i]==w.x[i+1] for i in range(w.count-1)) for w in self.ws))
    def test_10_window_ids_unique(self):
        self.assertEqual(len({w.window_id for w in self.ws}),64)
    def test_11_validation_accepts_fixture(self):
        m.validate_windows(self.ws)
    def test_12_reject_val_source(self):
        with self.assertRaisesRegex(m.ContractError,'NON_TRAIN'):
            m.validate_windows(self.ws+[m.make_window(999,0,64,'VAL')])
    def test_13_reject_test_source(self):
        with self.assertRaisesRegex(m.ContractError,'NON_TRAIN'):
            m.validate_windows(self.ws+[m.make_window(999,0,64,'TEST')])
    def test_14_reject_fake_duplicate_id(self):
        with self.assertRaisesRegex(m.ContractError,'DUPLICATE'):
            m.validate_windows(self.ws+[self.ws[0]])
    def test_15_reject_corrupted_label_shift(self):
        w=self.ws[0];y=list(w.y);y[0]=(y[0]+1)%2048
        with self.assertRaisesRegex(m.ContractError,'LABEL_SHIFT'):
            m.validate_windows([replace(w,y=tuple(y)),self.ws[1]])
    def test_16_reject_corrupted_padding_mask(self):
        w=self.ws[0];y=list(w.y);y[w.count]=12
        with self.assertRaisesRegex(m.ContractError,'PADDING_MASK'):
            m.validate_windows([replace(w,y=tuple(y)),self.ws[1]])
    def test_17_reject_out_of_vocab_x(self):
        w=self.ws[0];x=list(w.x);x[0]=2048
        with self.assertRaisesRegex(m.ContractError,'OUT_OF_VOCAB'):
            m.validate_windows([replace(w,x=tuple(x)),self.ws[1]])
    def test_18_reject_unaligned_story_offset(self):
        with self.assertRaisesRegex(m.ContractError,'OFFSET'):
            m.validate_windows([replace(self.ws[0],offset=1),self.ws[1]])
    def test_19_reject_multiple_first_windows_same_story(self):
        extra=replace(self.ws[0],window_id='different-id')
        with self.assertRaisesRegex(m.ContractError,'MULTIPLE_FIRST'):
            m.validate_windows(self.ws+[extra])
    def test_20_reject_empty_window_source(self):
        with self.assertRaisesRegex(m.ContractError,'NOT_ENOUGH'):
            m.validate_windows([])


class SamplerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ws=m.synthetic_windows()
        cls.sample=m.baseline_step(cls.ws,torch.Generator().manual_seed(20261110))
        cls.repl=m.first_story_replace(cls.ws,cls.sample,step=1025)

    def test_21_baseline_4096_valid_targets(self):
        self.assertEqual(sum(d.scored for d in self.sample),4096)
    def test_22_baseline_random_replay(self):
        r=m.baseline_step(self.ws,torch.Generator().manual_seed(20261110))
        self.assertEqual(r,self.sample)
    def test_23_baseline_residual_does_not_overcount(self):
        self.assertLessEqual(self.sample[-1].scored,self.ws[self.sample[-1].window_index].count)
    def test_24_replacement_first_only(self):
        self.assertTrue(all(self.ws[d.window_index].offset==0 for d in self.repl))
    def test_25_replacement_exact_vector_counts(self):
        self.assertEqual([d.scored for d in self.sample],[d.scored for d in self.repl])
    def test_26_replacement_exact_forward_count(self):
        self.assertEqual(len(self.sample),len(self.repl))
    def test_27_replacement_deterministic(self):
        self.assertEqual(self.repl,m.first_story_replace(self.ws,self.sample,step=1025))
    def test_28_replacement_has_actual_selection_effect(self):
        self.assertGreater(sum(a.window_index!=b.window_index for a,b in zip(self.sample,self.repl)),0)
    def test_29_layout_A_equals_C(self):
        l=m.arm_layout(self.ws,self.sample,self.repl)
        self.assertEqual(l['A'],l['C'])
    def test_30_layout_B_equals_D(self):
        l=m.arm_layout(self.ws,self.sample,self.repl)
        self.assertEqual(l['B'],l['D'])
    def test_31_all_four_budget_equal(self):
        l=m.arm_layout(self.ws,self.sample,self.repl)
        self.assertEqual({sum(d.scored for d in plan) for plan in l.values()},{4096})
    def test_32_all_microbatch_counts_equal(self):
        l=m.arm_layout(self.ws,self.sample,self.repl)
        self.assertEqual({(len(plan)+7)//8 for plan in l.values()}, {(len(self.sample)+7)//8})
    def test_33_hash_same_for_A_and_C(self):
        l=m.arm_layout(self.ws,self.sample,self.repl)
        self.assertEqual(m.hash_plan(l['A']),m.hash_plan(l['C']))
    def test_34_loss_labels_are_truncated(self):
        mat=m.masked_targets(self.ws,self.sample)
        self.assertEqual(tuple(mat.shape),(len(self.sample),256))
        self.assertEqual(int(mat.ne(-100).sum()),4096)
        self.assertTrue(all(torch.all(mat[i, d.scored:]==-100).item()
                            for i,d in enumerate(self.sample)))
    def test_35_reject_missing_candidate_count(self):
        # First windows all have <256 valid targets, late window 256.
        ws=[m.make_window(i,0,64) for i in range(3)]+[m.make_window(3,256,256)]
        with self.assertRaisesRegex(m.ContractError,'NO_COUNT_MATCHED'):
            m.first_story_replace(ws,(m.Draw(3,256),),step=1025)
    def test_36_reject_late_window_as_first_only(self):
        with self.assertRaisesRegex(m.ContractError,'NOT_FIRST_STORY'):
            m.validate_draw_plan(self.ws,self.sample,first_only=True)
    def test_37_reject_total_budget_shortfall(self):
        with self.assertRaisesRegex(m.ContractError,'WRONG_PER_STEP'):
            m.validate_draw_plan(self.ws,(m.Draw(0,1),))
    def test_38_reject_source_index_outside_pack(self):
        with self.assertRaisesRegex(m.ContractError,'WINDOW_INDEX'):
            m.validate_draw_plan(self.ws,(m.Draw(999,4096),))
    def test_39_reject_draw_longer_than_window_count(self):
        with self.assertRaisesRegex(m.ContractError,'BASELINE_DRAW_COUNT'):
            m.first_story_replace(self.ws,(m.Draw(0,self.ws[0].count+1),),step=1025)
    def test_40_reject_count_changed_even_if_4096_total(self):
        a=list(self.repl)
        i=next(i for i,d in enumerate(a) if d.scored>1)
        j=next(j for j,d in enumerate(a) if j!=i and d.scored < self.ws[d.window_index].count)
        a[i]=m.Draw(a[i].window_index,a[i].scored-1)
        a[j]=m.Draw(a[j].window_index,a[j].scored+1)
        with self.assertRaisesRegex(m.ContractError,'UNFAIR_FORWARD'):
            m.arm_layout(self.ws,self.repl,tuple(a))
    def test_41_reject_negative_step_index(self):
        with self.assertRaisesRegex(m.ContractError,'INVALID_STEP'):
            m.first_story_replace(self.ws,self.sample,step=0)
    def test_42_reject_val_in_replacement_pack(self):
        ws=list(self.ws)
        ws[-1]=replace(ws[-1],split='VAL')
        with self.assertRaisesRegex(m.ContractError,'NON_TRAIN'):
            m.first_story_replace(ws,self.sample,step=1025)


class LossTests(unittest.TestCase):
    @staticmethod
    def synthetic_logits_labels():
        torch.manual_seed(71)
        logits=torch.randn(3,256,7,dtype=torch.float64,requires_grad=True)
        labels=torch.full((3,256),-100,dtype=torch.long)
        labels[0,:4]=torch.tensor([0,1,2,3]); labels[0,31:35]=torch.tensor([4,5,6,1])
        labels[1,:2]=torch.tensor([3,2]); labels[1,40:44]=torch.tensor([1,4,2,5])
        labels[2,:3]=torch.tensor([0,4,6]); labels[2,60:64]=torch.tensor([2,1,1,6])
        return logits,labels

    def test_43_uniform_matches_pytorch_reference(self):
        x,y=self.synthetic_logits_labels()
        actual=m.weighted_step_loss(x,y,suffix_weighted=False)
        ref=F.cross_entropy(x.float().reshape(-1,7),y.reshape(-1),ignore_index=-100)
        self.assertAlmostEqual(float(actual),float(ref),places=6)
    def test_44_weighted_matches_independent_logsumexp(self):
        x,y=self.synthetic_logits_labels()
        actual=m.weighted_step_loss(x,y,suffix_weighted=True)
        vals=[];ws=[]
        for i in range(3):
            for j in range(256):
                if y[i,j]>=0:
                    # This is a separate numeric implementation, not F.cross_entropy.
                    v=x[i,j].detach().float()
                    vals.append(float(torch.logsumexp(v,dim=0)-v[int(y[i,j])]))
                    ws.append(3 if j>=32 else 1)
        self.assertAlmostEqual(float(actual),sum(v*w for v,w in zip(vals,ws))/sum(ws),places=6)
    def test_45_weighted_emphasis_changes_nonuniform_loss(self):
        x,y=self.synthetic_logits_labels()
        self.assertGreater(abs(float(m.weighted_step_loss(x,y,suffix_weighted=True)-m.weighted_step_loss(x,y,suffix_weighted=False))),1e-4)
    def test_46_all_constant_ce_loss_is_normalized(self):
        x,y=self.synthetic_logits_labels()
        x=torch.zeros_like(x,requires_grad=True)
        self.assertAlmostEqual(float(m.weighted_step_loss(x,y,suffix_weighted=True)),math.log(7),places=6)
    def test_47_pad_has_zero_gradient_uniform(self):
        x,y=self.synthetic_logits_labels()
        m.weighted_step_loss(x,y,suffix_weighted=False).backward()
        self.assertEqual(int(torch.count_nonzero(x.grad[y==-100]).item()),0)
    def test_48_pad_has_zero_gradient_weighted(self):
        x,y=self.synthetic_logits_labels()
        m.weighted_step_loss(x,y,suffix_weighted=True).backward()
        self.assertEqual(int(torch.count_nonzero(x.grad[y==-100]).item()),0)
    def test_49_suffix_gradient_three_times_prefix_for_uniform_logits(self):
        _,y=self.synthetic_logits_labels()
        y[:]=-100; y[0,0]=1; y[0,32]=1
        logits=torch.zeros((3,256,7),dtype=torch.float64,requires_grad=True)
        m.weighted_step_loss(logits,y,suffix_weighted=True).backward()
        r=(logits.grad[0,32,1]/logits.grad[0,0,1]).item()
        self.assertAlmostEqual(r,3.0,places=5)
    def test_50_uniform_gradient_nonzero_on_valid_tokens(self):
        x,y=self.synthetic_logits_labels()
        m.weighted_step_loss(x,y,suffix_weighted=False).backward()
        self.assertTrue(torch.all(torch.linalg.vector_norm(x.grad[y!=-100],dim=1)>0).item())
    def test_51_step_normalization_not_microbatch_average(self):
        x,y=self.synthetic_logits_labels()
        actual=m.weighted_step_loss(x,y,suffix_weighted=True)
        bad=(m.weighted_step_loss(x[:1],y[:1],suffix_weighted=True)+
             m.weighted_step_loss(x[1:],y[1:],suffix_weighted=True))/2
        self.assertGreater(abs(float(actual-bad)),1e-4)
    def test_52_single_microbatch_equals_reference(self):
        x,y=self.synthetic_logits_labels()
        v=m.weighted_step_loss(x,y,suffix_weighted=True)
        # Independent microbatch aggregation with GLOBAL denominator.
        num=torch.tensor(0.); den=0
        for i in range(len(y)):
            for j in range(256):
                if y[i,j]!=-100:
                    w=3 if j>=32 else 1
                    num+=w*F.cross_entropy(x[i,j].float().unsqueeze(0),y[i,j].unsqueeze(0),reduction='sum')
                    den+=w
        self.assertAlmostEqual(float(v),float(num/den),places=6)
    def test_53_reject_loss_no_valid_labels(self):
        x,y=self.synthetic_logits_labels(); y[:]=-100
        with self.assertRaisesRegex(m.ContractError,'NO_VALID'):
            m.weighted_step_loss(x,y,suffix_weighted=True)
    def test_54_reject_invalid_label_id(self):
        x,y=self.synthetic_logits_labels();y[0,0]=99
        with self.assertRaisesRegex(m.ContractError,'BAD_LABEL_ID'):
            m.weighted_step_loss(x,y,suffix_weighted=True)
    def test_55_reject_nonfinite_logits(self):
        x,y=self.synthetic_logits_labels();x=x.detach().clone();x[0,0,0]=float('nan')
        with self.assertRaisesRegex(m.ContractError,'NONFINITE'):
            m.weighted_step_loss(x,y,suffix_weighted=True)
    def test_56_reject_wrong_loss_shape(self):
        x,y=self.synthetic_logits_labels()
        with self.assertRaisesRegex(m.ContractError,'SHAPE_INVALID'):
            m.weighted_step_loss(x[:2],y,suffix_weighted=True)
    def test_57_reject_negative_nonpadding_label(self):
        x,y=self.synthetic_logits_labels();y[0,0]=-2
        with self.assertRaisesRegex(m.ContractError,'BAD_LABEL_ID'):
            m.weighted_step_loss(x,y,suffix_weighted=True)


class FullIntegratedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r=m.synthetic_run()
    def test_58_status_synthetic_only(self):
        self.assertEqual(self.r['status'],'SYNTHETIC_SAMPLER_PASS_NOT_TRAINING')
    def test_59_completed_128_steps(self):
        self.assertEqual(len(self.r['per_step']),128)
    def test_60_per_step_all_4096(self):
        self.assertTrue(all(all(z[a]['targets']==4096 for a in 'ABCD') for z in self.r['per_step']))
    def test_61_per_arm_exact_exposure(self):
        self.assertEqual(set(self.r['total_valid_label_exposures'].values()),{128*4096})
    def test_62_total_four_arm_exposures(self):
        self.assertEqual(sum(self.r['total_valid_label_exposures'].values()),4*128*4096)
    def test_63_forward_count_equal(self):
        self.assertEqual(len(set(self.r['total_forward_windows'].values())),1)
    def test_64_forward_slots_equal(self):
        self.assertEqual(len(set(self.r['total_forward_token_slots'].values())),1)
    def test_65_plan_A_C_digest_equal(self):
        x=self.r['plan_digest_by_arm'];self.assertEqual(x['A'],x['C'])
    def test_66_plan_B_D_digest_equal(self):
        x=self.r['plan_digest_by_arm'];self.assertEqual(x['B'],x['D'])
    def test_67_data_change_nontrivial(self):
        self.assertGreater(self.r['replacement_count_changed_window_id'],0)
    def test_68_B_D_all_drawn_windows_first(self):
        d=self.r['total_forward_windows'];z=self.r['first_story_window_draw_counts']
        self.assertEqual(z['B'],d['B']);self.assertEqual(z['D'],d['D'])
    def test_69_A_C_same_first_count(self):
        z=self.r['first_story_window_draw_counts'];self.assertEqual(z['A'],z['C'])
    def test_70_no_real_pack_or_training(self):
        self.assertFalse(self.r['real_TRAIN_VAL_pack_read'])
        self.assertFalse(self.r['model_weights_loaded'])
        self.assertEqual(self.r['optimizer_updates'],0)
        self.assertFalse(self.r['GPU_training'])
    def test_71_no_science_inference(self):
        self.assertFalse(self.r['science_inference'])
    def test_72_explicit_uncertainty_about_real_data(self):
        self.assertIn('NOT ESTABLISHED',self.r['caveat'])


if __name__=='__main__':
    unittest.main(verbosity=2)

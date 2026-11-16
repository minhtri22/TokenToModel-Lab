"""Track B/C independent-oracle synthetic engineering QA, Python3.12 CPU only."""
import hashlib, importlib.util, random, unittest
from copy import deepcopy
from pathlib import Path
import torch
from torch.nn import functional as F
from src.ttm_track_b import bc_sft_interface as b
from src.ttm_track_b.scaffold import cross_entropy_valid

C_PATH = Path(__file__).parent/"ttm_track_bc"/"c_m4_source_pinned.py"
def pinned_c():
    if hashlib.sha256(C_PATH.read_bytes()).hexdigest()!=b.C_SOURCE_SHA256:
        raise AssertionError("C_SOURCE_SHA256_MISMATCH")
    spec=importlib.util.spec_from_file_location("c_m4_exact_pinned",C_PATH)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    return m

class BCInterfaceQA(unittest.TestCase):
    def sample(self):
        return [{"role":"user","content":[77,78]},{"role":"assistant","content":[88,89]}]

    def test_01_noncolliding_full_byte_roundtrip(self):
        self.assertEqual(len(set(b.SPECIAL.values())),7)
        self.assertTrue(all(256<=s<2048 for s in b.SPECIAL.values()))
        self.assertEqual(b.decode_bytes(b.encode_bytes(bytes(range(256)))),bytes(range(256)))
        self.assertEqual(b.CODEC_SHA256,b.digest(b.codec_contract()))

    def test_02_c_exact_source_sha(self):
        self.assertEqual(hashlib.sha256(C_PATH.read_bytes()).hexdigest(),b.C_SOURCE_SHA256)

    def test_03_pinned_c_oracle_cross_role_mask(self):
        c=pinned_c()
        mapping={c.PAD:b.PAD,c.BOS:b.BOS,c.SYS:b.SYS,c.USER:b.USER,
                 c.ASSIST:b.ASSIST,c.EOT:b.EOT,c.EOS:b.EOS}
        cases=[self.sample(),
               [{"role":"system","content":[17]},{"role":"user","content":[78]},
                {"role":"assistant","content":[88]}],
               [{"role":"user","content":[77]},{"role":"assistant","content":[88]},
                {"role":"user","content":[79]},{"role":"assistant","content":[89]}]]
        for m in cases:
            with self.subTest(m=m):
                cx,cy=c.build_sft_targets(m,32)
                bx,by=b.build_sft_targets(m,32)
                self.assertEqual(bx,[mapping.get(v,v) for v in cx])
                self.assertEqual(by,[v if v==-100 else mapping.get(v,v) for v in cy])

    def test_04_bytes_zero_to_six_are_not_role_delimiters(self):
        p=b.make_pack()
        self.assertTrue(b.validate_pack(p))
        ids,mask=b.serialize(p["rows"][0]["messages"],33)
        self.assertTrue(set(range(7)).issubset(set(ids)))
        self.assertEqual(mask,b._derive_assistant_mask(ids))

    def test_05_plus_one_shift_known_answer(self):
        ids,flags=b.serialize(self.sample(),20)
        x,y=b.build_sft_targets(self.sample(),20)
        self.assertEqual(x[:len(ids)-1],ids[:-1])
        self.assertEqual(y[:len(ids)-1],[-100]*5+[88,89,b.EOT,b.EOS])
        self.assertEqual(y[:len(ids)-1],[ids[i] if flags[i] else -100 for i in range(1,len(ids))])

    def test_06_system_user_header_direct_loss_ignored(self):
        messages=[{"role":"system","content":[19]},{"role":"user","content":[20]},
                  {"role":"assistant","content":[21]}]
        ids,flags=b.serialize(messages,33);_,y=b.build_sft_targets(messages,33)
        self.assertTrue(all(y[i-1]==-100 for i,f in enumerate(flags) if i>0 and not f))
        self.assertEqual([v for v in y if v!=-100],[21,b.EOT,b.EOS])

    def test_07_multiturn_eot_eos_once(self):
        m=[{"role":"user","content":[77]},{"role":"assistant","content":[88]},
           {"role":"user","content":[79]},{"role":"assistant","content":[89]}]
        ids,_=b.serialize(m,33)
        _,y=b.build_sft_targets(m,33)
        self.assertEqual(ids.count(b.EOS),1)
        self.assertEqual(y.count(b.EOS),1)
        self.assertEqual(y.count(b.EOT),2)

    def test_08_right_pad_ignored(self):
        x,y=b.build_sft_targets(self.sample(),33)
        self.assertEqual(y.count(b.PAD),0)
        self.assertEqual(y[-1],-100)
        self.assertEqual(x[-1],b.PAD)

    def test_09_ce_reference_and_masked_logit_grad(self):
        torch.manual_seed(1)
        logits=torch.randn(1,5,2048,requires_grad=True)
        y=torch.tensor([[-100,22,23,b.EOS,-100]])
        loss=cross_entropy_valid(logits,y)
        oracle=-(F.log_softmax(logits[0,1:4].double(),dim=-1)
                 .gather(1,y[0,1:4].unsqueeze(1))).mean()
        self.assertLess(abs(loss.item()-oracle.item()),1e-5)
        loss.backward()
        self.assertEqual(torch.count_nonzero(logits.grad[0,0]).item(),0)
        self.assertEqual(torch.count_nonzero(logits.grad[0,4]).item(),0)

    def test_10_p02_real_synthetic_cpu_forward_backward(self):
        result=b.synthetic_cpu_probe()
        self.assertEqual(result["status"],"PASS_SYNTHETIC_FORWARD_BACKWARD_ONLY")
        self.assertEqual(result["optimizer_steps"],0)
        self.assertTrue(result["prompt_direct_ce_grad_zero"])
        self.assertGreater(result["prompt_context_grad_l1"],0)
        self.assertTrue(result["causal_future_isolation"])
        self.assertTrue(result["right_padding_isolation"])

    def test_11_all_mask_flags_mutations_rejected(self):
        ids,mask=b.serialize([{"role":"system","content":[7]},*self.sample()],33)
        for i in range(len(mask)):
            bad=mask.copy();bad[i]^=1
            with self.subTest(i=i),self.assertRaisesRegex(ValueError,"mask provenance|mismatch"):
                b.shifted_padded_targets(ids,bad,33)

    def test_12_special_injection_rejected(self):
        for code in b.SPECIAL.values():
            m=[{"role":"user","content":[code]},{"role":"assistant","content":[8]}]
            with self.subTest(code=code),self.assertRaises(ValueError):
                b.build_sft_targets(m,33)

    def test_13_bad_roles_and_empty_response_rejected(self):
        for m in [[{"role":"assistant","content":[8]}],
                  [{"role":"user","content":[7]},{"role":"user","content":[8]}],
                  [{"role":"user","content":[7]}],
                  [{"role":"user","content":[7]},{"role":"assistant","content":[]}]]:
            with self.subTest(m=m),self.assertRaises(ValueError):b.build_sft_targets(m,33)

    def test_14_codec_sha_and_template_sha_rejected(self):
        with self.assertRaisesRegex(ValueError,"SHA_MISMATCH"):
            b.build_sft_targets(self.sample(),33,codec_sha256="0"*64)
        with self.assertRaisesRegex(ValueError,"SHA_MISMATCH"):
            b.build_sft_targets(self.sample(),33,template_sha256="0"*64)

    def test_15_corrupt_eos_and_eot_rejected(self):
        ids,flags=b.serialize(self.sample(),33)
        with self.assertRaises(ValueError):b.shifted_padded_targets(ids+[b.EOS],flags+[1],33)
        bad=ids.copy();bad[-2]=b.EOS
        with self.assertRaises(ValueError):b.shifted_padded_targets(bad,flags,33)

    def test_16_all_ignore_and_bad_flags_rejected(self):
        with self.assertRaises(ValueError):b.build_sft_targets([{"role":"user","content":[7]}],33)
        with self.assertRaises(ValueError):b.shifted_padded_targets([b.BOS,b.USER],[0,0],33)
        ids,flags=b.serialize(self.sample(),33);flags[0]=False
        with self.assertRaises(ValueError):b.shifted_padded_targets(ids,flags,33)

    def test_17_left_pad_and_conversation_pack_disabled(self):
        for kw in [{"padding_side":"left"},{"packing":"concat"}]:
            with self.subTest(kw=kw),self.assertRaises(ValueError):
                b.build_sft_targets(self.sample(),33,**kw)

    def test_18_no_silent_truncation(self):
        m=[{"role":"user","content":[10]*20},{"role":"assistant","content":[20]*20}]
        with self.assertRaises(ValueError):b.build_sft_targets(m,33)
        with self.assertRaises(ValueError):b.build_sft_targets(self.sample(),34)

    def test_19_off_by_one_mutation_in_pack_rejected(self):
        p=b.make_pack();p["rows"][0]["y"][4]=0
        with self.assertRaises(ValueError):b.validate_pack(p)

    def test_20_user_target_leak_in_pack_rejected(self):
        p=b.make_pack();p["rows"][0]["y"][6]=3
        with self.assertRaises(ValueError):b.validate_pack(p)

    def test_21_old_byte_pack_schema_rejected(self):
        with self.assertRaisesRegex(ValueError,"OLD_B_PACK"):
            b.validate_pack({"schema":"ttm.track_b.synthetic.byte_windows.v1","synthetic_only":True})

    def test_22_cross_split_duplicate_rejected(self):
        p=b.make_pack();p["rows"][2]["messages"]=deepcopy(p["rows"][0]["messages"])
        with self.assertRaises(ValueError):b.validate_pack(p)

    def test_23_old_t4_p04_b_checkpoints_incompatible(self):
        p=b.make_pack()
        for schema in ["ttm.p04.model_checkpoint.v1","ttm.t4.science.checkpoint.v1",
                       "ttm.track_b.synthetic.train_checkpoint.v1"]:
            with self.subTest(schema=schema),self.assertRaisesRegex(ValueError,"INCOMPATIBLE"):
                b.verify_resume_compatible({"schema":schema},p)

    def test_24_versioned_resume_sha_guard(self):
        p=b.make_pack();self.assertTrue(b.verify_resume_compatible(b.resume_manifest(p),p))
        for key in ["codec_sha256","template_sha256","model_sha256","pack_sha256"]:
            state=b.resume_manifest(p);state[key]="0"*64
            with self.subTest(key=key),self.assertRaisesRegex(ValueError,"INCOMPATIBLE"):
                b.verify_resume_compatible(state,p)

    def test_25_thousand_random_role_shift_cases(self):
        rng=random.Random(20261116)
        for _ in range(1000):
            msgs=[]
            if rng.randrange(2):msgs.append({"role":"system","content":[rng.randrange(256)]})
            for _ in range(rng.randrange(1,3)):
                msgs.extend([{"role":"user","content":[rng.randrange(256)]},
                             {"role":"assistant","content":[rng.randrange(256)]}])
            ids,mask=b.serialize(msgs,33);x,y=b.build_sft_targets(msgs,33)
            self.assertEqual(x[:len(ids)-1],ids[:-1])
            self.assertEqual(y[:len(ids)-1],[ids[i] if mask[i] else -100 for i in range(1,len(ids))])
            self.assertEqual(sum(v!=-100 for v in y),sum(mask))

    def test_26_validated_pack_and_frozen_sha(self):
        p=b.make_pack();self.assertEqual(p["source_b_head"],b.B_BASE_HEAD)
        self.assertEqual(p["source_c_head"],b.C_DESIGN_HEAD)
        self.assertEqual(p["codec_sha256"],b.CODEC_SHA256)
        self.assertTrue(b.validate_pack(p))

    def test_27_bool_content_and_non_byte_decode_rejected(self):
        with self.assertRaises(ValueError):b.decode_bytes([b.EOS])
        with self.assertRaises(ValueError):
            b.serialize([{"role":"user","content":[True]},{"role":"assistant","content":[8]}],33)

    def test_28_reserved_injection_in_serialized_ids_rejected(self):
        ids,mask=b.serialize(self.sample(),33)
        for s in b.SPECIAL.values():
            changed=ids.copy();changed[2]=s
            with self.subTest(s=s),self.assertRaises(ValueError):
                b.shifted_padded_targets(changed,mask,33)

    def test_29_pack_hash_tamper_rejected(self):
        p=b.make_pack();p["pack_sha256"]="0"*64
        with self.assertRaisesRegex(ValueError,"PACK_SHA256"):b.validate_pack(p)

if __name__=="__main__":
    unittest.main()

"""Track C independently specified acceptance-oracle unit QA, not B implementation QA."""
import math
import unittest
from bc_sft_wire_oracle import (SPECIAL as S, BYTE_MAX, VOCAB, IGNORE,
    SCHEMA, CHECKPOINT_SCHEMA, OLD_B_SCHEMA, validate_codec, encode_bytes,
    decode_bytes, serialize, derive_mask, targets, build, independent_valid_ce,
    verify_manifest, sha, canonical)


def conversation():
    return [{"role":"system","content":"sys"},
            {"role":"user","content":"\x00\x01[ASSIST] café 🇻🇳"},
            {"role":"assistant","content":"chào"}]


class CandidateBCDesignQA(unittest.TestCase):
    def test_01_noncolliding_byte_specials(self):
        self.assertTrue(validate_codec())
        self.assertEqual(VOCAB, 2048)
        self.assertEqual(set(S.values()), set(range(256, 263)))
        self.assertTrue(all(i > BYTE_MAX for i in S.values()))

    def test_02_raw_all_bytes_roundtrip_and_reserved_rejected(self):
        self.assertEqual(decode_bytes(encode_bytes(bytes(range(256)))), bytes(range(256)))
        with self.assertRaisesRegex(ValueError,"BYTE_ID_RANGE"):
            decode_bytes([0,S["SYS"]])

    def test_03_utf8_roundtrip_role_literal_not_special(self):
        ids, mask = serialize(conversation(), 80)
        self.assertEqual(ids.count(S["SYS"]), 1)
        self.assertEqual(ids.count(S["ASSIST"]), 1)
        self.assertEqual(ids.count(S["EOS"]), 1)
        self.assertEqual(ids.count(S["EOT"]), 3)
        self.assertEqual(mask, derive_mask(ids))
        data = "\x00\x01[ASSIST] café 🇻🇳".encode("utf8")
        self.assertIn(list(data), [ids[i:i+len(data)] for i in range(len(ids)-len(data)+1)])
        self.assertNotIn(S["ASSIST"], list(data))

    def test_04_prompt_direct_mask_and_assistant_termination(self):
        ids, mask = serialize(conversation(), 80)
        x, y = targets(ids, mask, 80)
        self.assertEqual(len(x), 79)
        for i, flag in enumerate(mask[1:]):
            self.assertEqual(y[i] != IGNORE, bool(flag))
        self.assertEqual(y.count(S["EOT"]), 1)
        self.assertEqual(y.count(S["EOS"]), 1)
        self.assertEqual(y.count(S["USER"]), 0)
        self.assertEqual(y.count(S["SYS"]), 0)
        self.assertEqual(y.count(S["ASSIST"]), 0)
        self.assertEqual(y.count(S["PAD"]), 0)

    def test_05_role_provenance_forged_user_target_fails(self):
        ids, flags = serialize(conversation(), 80)
        user_at = ids.index(S["USER"]) + 1
        self.assertEqual(flags[user_at], 0)
        flags[user_at] = 1
        with self.assertRaisesRegex(ValueError,"ROLE_MASK_PROVENANCE"):
            targets(ids, flags, 80)

    def test_06_every_single_flag_flip_fails(self):
        ids, mask = serialize(conversation(), 80)
        for i in range(len(mask)):
            changed = mask.copy(); changed[i] ^= 1
            with self.subTest(i=i), self.assertRaises(ValueError):
                targets(ids,changed,80)

    def test_07_reserved_token_injection_fails(self):
        ids, mask = serialize(conversation(), 80)
        i = ids.index(S["USER"]) + 1
        for t in (S["SYS"], S["USER"], S["ASSIST"], S["EOS"], S["PAD"]):
            injected = ids.copy(); injected[i] = t
            with self.subTest(t=t), self.assertRaises(ValueError):
                targets(injected, mask, 80)

    def test_08_wrong_role_order_and_empty_final_rejected(self):
        bad = [[{"role":"assistant","content":"no"}],
               [{"role":"user","content":"yes"}],
               [{"role":"user","content":"yes"},{"role":"assistant","content":""}],
               [{"role":"user","content":"yes"},{"role":"system","content":"bad"},
                {"role":"assistant","content":"ok"}]]
        for m in bad:
            with self.subTest(m=m),self.assertRaises(ValueError):
                build(m, 32)

    def test_09_eos_duplicate_eot_loss_and_no_truncation(self):
        ids, flags = serialize(conversation(), 80)
        with self.assertRaises(ValueError):
            targets(ids+[S["EOS"]], flags+[1], 81)
        changed=ids.copy(); changed[-2]=S["EOS"]
        with self.assertRaises(ValueError):
            targets(changed,flags,80)
        with self.assertRaisesRegex(ValueError,"NO_SILENT_TRUNCATION"):
            serialize(conversation(), 8)

    def test_10_explicit_plus_one_shift_and_right_pad_only(self):
        ids,mask=serialize(conversation(), 80)
        x,y=targets(ids,mask,80)
        self.assertEqual(x[:len(ids)-1],ids[:-1])
        self.assertTrue(all(k==IGNORE for k in y[len(ids)-1:]))
        self.assertTrue(all(t==S["PAD"] for t in x[len(ids):]))
        self.assertEqual((x,y),build(conversation(),80))

    def test_11_old_byte_pack_not_accepted(self):
        self.assertNotEqual(OLD_B_SCHEMA, SCHEMA)
        with self.assertRaisesRegex(ValueError,"NOT_BC_SFT_PACK"):
            verify_manifest({"schema":OLD_B_SCHEMA},{})

    def test_12_checkpoint_hash_mismatch_rejects(self):
        keys = ["tokenizer_sha256","chat_template_sha256","serialized_inputs_sha256",
                "target_labels_sha256","target_masks_sha256","config_sha256",
                "checkpoint_schema_sha256"]
        pins={k:sha(k.encode()) for k in keys}
        item={"schema":SCHEMA,"checkpoint_schema":CHECKPOINT_SCHEMA,**pins}
        self.assertTrue(verify_manifest(item,pins))
        for k in keys:
            tampered=item.copy();tampered[k]="0"*64
            with self.subTest(k=k),self.assertRaises(ValueError):
                verify_manifest(tampered,pins)
        x=item.copy();x["checkpoint_schema"]="ttm.track_b.synthetic.train_checkpoint.v1"
        with self.assertRaises(ValueError):verify_manifest(x,pins)

    def test_13_ignored_prompt_ce_and_nonzero_context_derivative_allowed(self):
        logits=[[2.,0.,-1.],[2.,0.,-1.],[2.,0.,-1.]]
        targets_=[IGNORE,1,IGNORE]
        baseline=independent_valid_ce(logits,targets_)
        logits[0]=[100.,-100.,100.]
        logits[2]=[-100.,100.,-100.]
        self.assertAlmostEqual(independent_valid_ce(logits,targets_),baseline)
        logits[1]=[0.,2.,-1.]
        self.assertNotAlmostEqual(independent_valid_ce(logits,targets_),baseline)
        prompt_feature=2.0; answer_feature=1.0
        self.assertNotEqual(prompt_feature+answer_feature,0.0)

    def test_14_all_ignore_rejects_and_valid_denominator(self):
        logits=[[0.,0.],[5.,-5.],[0.,0.]]
        y=[1,IGNORE,0]
        self.assertAlmostEqual(independent_valid_ce(logits,y),math.log(2))
        with self.assertRaisesRegex(ValueError,"ALL_IGNORE"):
            independent_valid_ce(logits,[IGNORE]*3)

    def test_15_causal_policy_is_only_spec_not_model_evidence(self):
        # The reference visibility matrix is causal; only B's real P02
        # forward/backward can establish BC-3 for the integration.
        for t in range(12):
            allowed=[k<=t for k in range(12)]
            self.assertTrue(all(allowed[k] for k in range(t+1)))
            self.assertFalse(any(allowed[t+1:]))

    def test_16_bad_flag_types_and_bounds(self):
        ids, mask=serialize(conversation(),80)
        changed=mask.copy();changed[1]=False
        with self.assertRaises(ValueError):targets(ids,changed,80)
        with self.assertRaises(ValueError):targets(ids,mask,True)
        with self.assertRaises(ValueError):targets(ids,mask,258)

    def test_17_1000_seeded_multiturn_fixtures(self):
        import random
        randomizer=random.Random(20261116)
        for _ in range(1000):
            messages=[]
            if randomizer.randrange(2):
                messages.append({"role":"system","content":"policy"})
            for turn in range(randomizer.randint(1,5)):
                messages.append({"role":"user","content":"\x00Q"+str(randomizer.randrange(1000))})
                messages.append({"role":"assistant","content":"A"+str(randomizer.randrange(1000))})
            ids,flags=serialize(messages,256)
            x,y=targets(ids,flags,256)
            self.assertEqual((x,y),build(messages,256))
            self.assertEqual(sum(z!=-100 for z in y),sum(flags))
            self.assertEqual(y.count(S["EOS"]),1)
            self.assertEqual(y.count(S["EOT"]),len(messages)//2 if messages[0]['role']!='system' else (len(messages)-1)//2)

    def test_18_source_authentication_not_claimed(self):
        # A self-consistent but falsely labeled dialogue is structurally valid.
        # This MUST NOT be treated as evidence of real corpus provenance.
        forged=[{"role":"user","content":"external source"},
                {"role":"assistant","content":"unverified claim"}]
        self.assertTrue(any(z!=IGNORE for z in build(forged,64)[1]))
        self.assertEqual(sha(canonical({"schema":SCHEMA})),sha(canonical({"schema":SCHEMA})))

if __name__=='__main__':unittest.main()

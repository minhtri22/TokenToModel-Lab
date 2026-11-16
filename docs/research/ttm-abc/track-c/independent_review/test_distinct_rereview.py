"""Distinct reviewer oracle on exact Track-C M4 toy source (stdlib only).
This test belongs to this independent review, not the author's 26-test count.
"""
import random
import unittest
from synthetic_contract import (
    BOS, SYS, USER, ASSIST, EOT, EOS, PAD, IGNORE,
    serialize, shifted_padded_targets, build_sft_targets, audit_toy_records,
)

class DistinctReviewerQA(unittest.TestCase):
    def _oracle(self, messages, pad_to):
        # Build the desired labels independently from the role-bearing messages,
        # rather than trusting the implementation's flags or parser.
        ids = [BOS]
        direct = [0]
        for m in messages:
            role_code = {'system': SYS, 'user': USER, 'assistant': ASSIST}[m['role']]
            assistant = int(m['role'] == 'assistant')
            ids.extend([role_code] + list(m['content']) + [EOT])
            direct.extend([0] + [assistant] * len(m['content']) + [assistant])
        ids.append(EOS); direct.append(1)
        padded = ids + [PAD]*(pad_to - len(ids))
        flags = direct + [0]*(pad_to - len(ids))
        return padded[:-1], [padded[j] if flags[j] else IGNORE for j in range(1, pad_to)], ids, direct

    def test_independent_role_oracle_5000_synthetic_dialogues(self):
        rng = random.Random(913577)
        for _ in range(5000):
            msgs=[]
            if rng.random() < .5:
                msgs.append({'role': 'system', 'content': [rng.randrange(1000, 10000) for __ in range(rng.randrange(1,7))]})
            for __ in range(rng.randrange(1,7)):
                msgs.append({'role':'user','content':[rng.randrange(10000, 20000) for ___ in range(rng.randrange(1,7))]})
                msgs.append({'role':'assistant','content':[rng.randrange(20000, 30000) for ___ in range(rng.randrange(1,7))]})
            expected_x, expected_y, ids, flags = self._oracle(msgs, 128)
            self.assertEqual(build_sft_targets(msgs,128),(expected_x,expected_y))
            self.assertEqual(shifted_padded_targets(ids,flags,128),(expected_x,expected_y))
            self.assertEqual(expected_y.count(EOS),1)
            self.assertEqual(expected_y.count(EOT),sum(m['role']=='assistant' for m in msgs))

    def test_every_flag_bit_flip_rejected(self):
        msgs=[{'role':'system','content':[7,8]},{'role':'user','content':[9,10]},
              {'role':'assistant','content':[11,12]}, {'role':'user','content':[13]},
              {'role':'assistant','content':[14]}]
        ids, flags=serialize(msgs,40)
        for i in range(len(flags)):
            altered=flags.copy(); altered[i]=1-altered[i]
            with self.subTest(i=i), self.assertRaises(ValueError):
                shifted_padded_targets(ids,altered,40)

    def test_original_review_counterexample_rejected(self):
        ids,flags=serialize([{'role':'user','content':[77]}, {'role':'assistant','content':[88]}], 12)
        flags[2]=1
        with self.assertRaisesRegex(ValueError,'mask provenance'):
            shifted_padded_targets(ids, flags,12)

    def test_invalid_special_token_injection_fails_closed(self):
        ids,flags=serialize([{'role':'user','content':[77]}, {'role':'assistant','content':[88]}], 12)
        for idx in (2, 6):
            for special in (PAD, BOS, SYS, USER, ASSIST, EOT, EOS):
                tampered=ids.copy();tampered[idx]=special
                if special == ids[idx]:
                    continue  # unchanged EOT is not an injection
                with self.subTest(index=idx,special=special), self.assertRaises(ValueError):
                    shifted_padded_targets(tampered,flags,12)

    def test_boundary_no_truncation_and_eos_supervised(self):
        msgs=[{'role':'user','content':[77]}, {'role':'assistant','content':[88]}]
        x,y=build_sft_targets(msgs,8)
        self.assertEqual(len(x),7);self.assertEqual(len(y),7)
        self.assertEqual(y[-1],EOS)
        for max_len in (0, 1, 5, 7, True, 1.5):
            with self.subTest(max_len=max_len),self.assertRaises(ValueError):
                build_sft_targets(msgs,max_len)

    def test_tampered_complete_flag_mismatch_even_if_same_count(self):
        ids,flags=serialize([{'role':'user','content':[77,78]}, {'role':'assistant','content':[88,89]}],18)
        # Move direct supervision from an assistant target to a user target.
        altered=flags.copy(); altered[2]=1;altered[6]=0
        self.assertEqual(sum(altered),sum(flags))
        with self.assertRaisesRegex(ValueError,'mask provenance'):
            shifted_padded_targets(ids,altered,18)

    def test_nfc_cross_split_and_raw_hash_distinction(self):
        rows=[{'id':'1','split':'train','text':'e\u0301'},
              {'id':'2','split':'val','text':'É'},
              {'id':'3','split':'test','text':'x'}]
        result=audit_toy_records(rows)
        self.assertEqual(result['cross_split_exact_groups'],0)
        self.assertEqual(result['cross_split_normalized_groups'],1)
        self.assertEqual(result['near_duplicate_groups'],'NOT_IMPLEMENTED_TOY_ONLY')

    def test_user_content_must_remain_context_not_direct_loss(self):
        msgs=[{'role':'system','content':[17]},{'role':'user','content':[18,19]},
              {'role':'assistant','content':[20]}, {'role':'user','content':[21]},
              {'role':'assistant','content':[22,23]}]
        x,y,ids,direct=self._oracle(msgs,32)
        self.assertEqual((x,y),build_sft_targets(msgs,32))
        for j in range(1,len(ids)):
            if not direct[j]:
                self.assertEqual(y[j-1],IGNORE)
        self.assertEqual(sum(t!=IGNORE for t in y),sum(direct))

    def test_source_authenticity_not_proved_by_structural_mask(self):
        # A coherent but self-authored role sequence is structurally accepted.
        # Not a defect in this toy contract: the protocol explicitly requires
        # separately attested corpus, roles, tokenizer, splits and B integration.
        forged=[BOS,USER,77,EOT,ASSIST,88,EOT,EOS]
        flags=[0,0,0,0,0,1,1,1]
        _,targets=shifted_padded_targets(forged,flags,8)
        self.assertIn(88,targets)
        self.assertNotIn(77,targets)

if __name__=='__main__':
    unittest.main()

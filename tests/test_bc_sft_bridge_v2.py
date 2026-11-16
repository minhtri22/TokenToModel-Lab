"""BC-F01..F04 source-owned regression, negative QA, 7 real file readbacks."""
from __future__ import annotations
import copy, hashlib, json, random, tempfile, unittest
from pathlib import Path
from src.ttm_track_b import bc_sft_bridge_v2 as b
from src.ttm_track_b import bc_sft_interface as old

def sample():
    return [
        {"role":"system","content":"P"},
        {"role":"user","content":"\x00[ASSIST] café 🇻🇳"},
        {"role":"assistant","content":"chào"}]

class BCCandidateV2QA(unittest.TestCase):
    def test_01_new_names_are_additive_and_old_unchanged(self):
        self.assertEqual(b.SCHEMA,"ttm.bc.synthetic.sft_pack.v2")
        self.assertEqual(b.CHECKPOINT_SCHEMA,"ttm.bc.synthetic.sft_checkpoint.v2")
        self.assertEqual(b.CHAT_TEMPLATE_SCHEMA,"ttm.bc.synthetic.chat_template.v2")
        self.assertNotEqual(old.PACK_SCHEMA,b.SCHEMA)
        self.assertEqual(old.CODEC_SHA256, old.digest(old.codec_contract()))
        self.assertEqual(old.B_BASE_HEAD,b.B_BASE_HEAD)

    def test_02_all_raw_bytes_roundtrip_and_zero_to_six_are_data(self):
        data=bytes(range(256))
        self.assertEqual(b.decode_bytes(b.encode_bytes(data)),data)
        self.assertTrue(all(i in b.encode_bytes(data) for i in range(7)))
        self.assertEqual(set(b.SPECIAL.values()),set(range(256,263)))
        self.assertTrue(b.validate_codec())

    def test_03_text_bridge_with_null_unicode_emoji_literal(self):
        messages=sample()
        out=b.to_byte_messages(messages)
        self.assertEqual(b.from_byte_messages(out),messages)
        self.assertEqual(out[1]["content"],list(messages[1]["content"].encode("utf-8")))
        ids,mask=b.serialize(messages,100)
        self.assertEqual(ids.count(b.SPECIAL["ASSIST"]),1)
        self.assertEqual(ids.count(b.SPECIAL["EOS"]),1)
        self.assertEqual(ids.count(b.SPECIAL["EOT"]),3)
        self.assertEqual(mask,b.derive_mask(ids))
        self.assertEqual((b.targets(ids,mask,100)),b.build(messages,100))

    def test_04_text_vs_raw_bytes_strict_paths(self):
        with self.assertRaises((UnicodeError,ValueError)):
            b.from_byte_messages([{"role":"user","content":[255]},
                                  {"role":"assistant","content":[65]}])
        with self.assertRaises(ValueError):
            b.to_byte_messages([{"role":"user","content":[65]},
                                {"role":"assistant","content":"ok"}])
        with self.assertRaises(ValueError):
            b.raw_b_byte_only(sample(),33)
        self.assertEqual(len(b.raw_b_byte_only([{"role":"user","content":[255]},
              {"role":"assistant","content":[254]}],33)[0]),32)

    def test_05_surrogate_not_replaced_no_lossy_roundtrip(self):
        for invalid in ["\ud800","\udfff"]:
            msg=[{"role":"user","content":invalid},{"role":"assistant","content":"ok"}]
            with self.subTest(invalid=repr(invalid)),self.assertRaises(UnicodeEncodeError):
                b.to_byte_messages(msg)

    def test_06_no_implicit_unicode_normalization(self):
        a="é";nfd="e\u0301"
        self.assertNotEqual(b.to_byte_messages([{"role":"user","content":a}]),
                            b.to_byte_messages([{"role":"user","content":nfd}]))
        self.assertNotEqual(b.canonical({"x":a}),b.canonical({"x":nfd}))
        self.assertNotEqual(b.sha(b.canonical({"x":a})),b.sha(b.canonical({"x":nfd})))

    def test_07_typed_malformed_role_objects_negative(self):
        cases=[{"role":"user","content":b"x"}, {"role":"user","content":3},
               {"role":"user","content":""}, {"role":1,"content":"a"},
               {"role":"tool","content":"a"}, {"role":"user","content":"a","flag":1},
               {"role":"user"},{"content":"x"}]
        for bad in cases:
            with self.subTest(bad=str(bad)),self.assertRaises(ValueError):
                b.to_byte_messages([bad])

    def test_08_roles_and_every_flag_bit_negative(self):
        ids,mask=b.serialize(sample(),100)
        for i in range(len(mask)):
            bad=mask.copy();bad[i]^=1
            with self.subTest(i=i),self.assertRaisesRegex(ValueError,"ROLE_MASK_PROVENANCE"):
                b.targets(ids,bad,100)

    def test_09_injected_specials_are_not_text_payload(self):
        ids,mask=b.serialize(sample(),100)
        for value in b.SPECIAL.values():
            bad=ids.copy();bad[ids.index(b.SPECIAL["USER"])+1]=value
            with self.subTest(value=value),self.assertRaises(ValueError):
                b.targets(bad,mask,100)

    def test_10_shift_stop_system_and_user_ignored(self):
        ids,mask=b.serialize(sample(),100)
        x,y=b.build(sample(),100)
        self.assertEqual(x[:len(ids)-1],ids[:-1])
        self.assertEqual(y[:len(ids)-1],
                         [ids[i] if mask[i] else -100 for i in range(1,len(ids))])
        self.assertEqual(y.count(b.SPECIAL["EOT"]),1)
        self.assertEqual(y.count(b.SPECIAL["EOS"]),1)
        self.assertEqual(y.count(b.SPECIAL["USER"]),0)
        self.assertEqual(y.count(b.SPECIAL["SYS"]),0)
        self.assertEqual(y.count(b.SPECIAL["PAD"]),0)

    def test_11_no_truncation_and_bad_padding(self):
        with self.assertRaisesRegex(ValueError,"NO_SILENT_TRUNCATION"):
            b.build(sample(),33)
        with self.assertRaises(ValueError): b.build(sample(),True)
        with self.assertRaises(ValueError): b.build(sample(),258)
        ids,mask=b.serialize(sample(),100)
        with self.assertRaises(ValueError): b.targets(ids+[b.SPECIAL["EOS"]],mask+[1],100)

    def test_12_lf_is_new_versioned_canonical_not_old_sha(self):
        document={"y":"🇻🇳","\u0000":"é","x":1}
        v2=b.canonical(document)
        old_bytes=json.dumps(document,sort_keys=True,ensure_ascii=False,
                       separators=(",",":"),allow_nan=False).encode("utf-8")
        self.assertEqual(v2,old_bytes+b"\n")
        self.assertNotEqual(b.sha(v2),b.sha(old_bytes))
        self.assertNotEqual(b.sha(v2),b.sha(v2.replace(b"\n",b"\r\n")))
        with self.assertRaises(UnicodeEncodeError):b.canonical({"invalid":"\ud800"})

    def test_13_new_schema_rejects_all_prior_schemas(self):
        for schema in [b.OLD_B_SCHEMA,b.OLD_BC_SCHEMA,b.C_V1_SCHEMA,
                       "ttm.bc.synthetic.sft.resume.v1",
                       "ttm.bc.synthetic.sft_checkpoint.v1",
                       "ttm.t4.science.checkpoint.v1"]:
            with self.subTest(schema=schema),self.assertRaises(ValueError):
                b.verify_legacy_rejected({"schema":schema})

    def test_14_seven_real_artifacts_produced_read_back(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"bundle"
            m=b.write_bundle(path)
            self.assertEqual(set(m).intersection(b.REQUIRED),b.REQUIRED)
            self.assertEqual(b.verify_bundle(path),m)
            for field,name in b.ARTIFACT_NAMES.items():
                raw=(path/name).read_bytes()
                self.assertEqual(m[field],hashlib.sha256(raw).hexdigest())
                self.assertEqual(raw,b.canonical(json.loads(raw.decode("utf-8"))))
            self.assertNotIn("weights",m)
            self.assertTrue(m["no_science"])
            self.assertEqual(m["source_b_head"],b.B_BASE_HEAD)
            self.assertEqual(m["source_c_oracle_head"],b.C_ORACLE_HEAD)

    def test_15_all_seven_file_byte_mutations_fail(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"bundle";b.write_bundle(path)
            for key,name in b.ARTIFACT_NAMES.items():
                target=path/name;original=target.read_bytes()
                try:
                    target.write_bytes(original[:-1]+b" ")
                    with self.subTest(key=key),self.assertRaises(ValueError):
                        b.verify_bundle(path)
                finally:
                    target.write_bytes(original)
                self.assertEqual(b.verify_bundle(path)["schema"],b.SCHEMA)

    def test_16_all_seven_hash_fields_manifest_mutation_fail(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"bundle";b.write_bundle(path)
            target=path/"manifest.json";raw=target.read_bytes()
            for key in sorted(b.REQUIRED):
                m=json.loads(raw)
                m[key]="0"*64
                try:
                    target.write_bytes(b.canonical(m))
                    with self.subTest(key=key),self.assertRaisesRegex(ValueError,"SHA_READBACK_MISMATCH"):
                        b.verify_bundle(path)
                finally:
                    target.write_bytes(raw)

    def test_17_recomputed_tampered_manifest_cannot_forge_fixture(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"bundle";b.write_bundle(path)
            target=path/b.ARTIFACT_NAMES["target_labels_sha256"]
            labels=json.loads(target.read_bytes())
            labels["rows"][0]["y"][0]=55
            raw=b.canonical(labels)
            target.write_bytes(raw)
            m=json.loads((path/"manifest.json").read_bytes())
            m["target_labels_sha256"]=hashlib.sha256(raw).hexdigest()
            (path/"manifest.json").write_bytes(b.canonical(m))
            with self.assertRaisesRegex(ValueError,"WRONG_TARGET_LABELS|FROZEN_DOCUMENTS"):
                b.verify_bundle(path)

    def test_18_manifest_line_endings_and_lf_file_failure(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"bundle";b.write_bundle(path)
            manifest=path/"manifest.json";raw=manifest.read_bytes()
            manifest.write_bytes(raw.replace(b"\n",b"\r\n"))
            with self.assertRaisesRegex(ValueError,"MANIFEST_CANONICAL_BYTES"):
                b.verify_bundle(path)

    def test_19_refuse_overwrite_and_forged_directory_files(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"bundle";b.write_bundle(path)
            with self.assertRaises(FileExistsError):b.write_bundle(path)
            (path/"EXTRA").write_text("forgery",encoding="utf8")
            with self.assertRaisesRegex(ValueError,"BUNDLE_FILE_SET_MISMATCH"):
                b.verify_bundle(path)

    def test_20_cross_c_role_seeded_thousand_conversations(self):
        rng=random.Random(20261116)
        for _ in range(1000):
            m=[]
            if rng.randrange(2):m.append({"role":"system","content":"policy"})
            for _ in range(rng.randint(1,5)):
                m.extend([{"role":"user","content":"\x00Q"+str(rng.randrange(1000))},
                          {"role":"assistant","content":"A"+str(rng.randrange(1000))}])
            ids,flags=b.serialize(m,256)
            self.assertEqual(b.build(m,256),b.targets(ids,flags,256))
            x,y=b.targets(ids,flags,256)
            self.assertEqual(x[:len(ids)-1],ids[:-1])
            self.assertEqual(sum(v!=-100 for v in y),sum(flags))

    def test_21_independent_ce_oracle_with_valid_targets_only(self):
        from tests.ttm_track_bc.b_v2_c_oracle_compat import independent_valid_ce
        import torch
        from src.ttm_track_b.scaffold import cross_entropy_valid
        logits=torch.tensor([[[2.,0.,-1.],[3.,4.,0.],[-7.,8.,1.]]],requires_grad=True)
        targets=torch.tensor([[-100,1,-100]])
        result=cross_entropy_valid(logits,targets)
        oracle=independent_valid_ce(logits.detach()[0].tolist(),targets[0].tolist())
        self.assertAlmostEqual(result.item(),oracle,places=5)
        result.backward()
        self.assertEqual(logits.grad[0,0].abs().sum().item(),0)
        self.assertEqual(logits.grad[0,2].abs().sum().item(),0)

    def test_22_new_v2_c_text_p02_cpu_backward(self):
        r=b.synthetic_cpu_probe_v2()
        self.assertTrue(r["direct_prompt_target_ce_zero"])
        self.assertTrue(r["causal_isolated"])
        self.assertTrue(r["padding_isolated"])
        self.assertGreater(r["prompt_context_grad_l1"],0)
        self.assertEqual(r["optimizer_steps"],0)
        self.assertFalse(r["science_executed"])

    def test_23_structurally_consistent_roles_not_authenticity(self):
        forged=[{"role":"user","content":"fabricated source"},
                {"role":"assistant","content":"fabricated answer"}]
        self.assertTrue(any(v!=-100 for v in b.build(forged,33)[1]))
        doc=b._bundle_documents()["serialized_inputs_sha256"]
        self.assertEqual(doc["source_role_authenticity"],"DECLARED_UNVERIFIED")
        self.assertTrue(all(r["declared_roles_authenticated"] is False for r in doc["rows"]))

    def test_24_c_source_boundary_and_hash_named_fields(self):
        self.assertEqual(b.C_ORACLE_HEAD,"56c18e2a00714c8a1c118dabc0ede9d2a1b34b17")
        self.assertEqual(b.C_ORACLE_BLOB,"233c678c89afc3471af4addc55f827e0c52b0383")
        self.assertEqual(len(b.REQUIRED),7)
        self.assertEqual(b.CANONICAL_SCHEMA,"ttm.bc.canonical_json_utf8_sorted_compact_lf.v2")

if __name__=="__main__": unittest.main()

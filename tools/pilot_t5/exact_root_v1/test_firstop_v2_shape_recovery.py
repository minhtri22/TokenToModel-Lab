#!/usr/bin/env python3
"""Eight standalone auditor-v2 unit tests. No model, no science rerun."""
from pathlib import Path
import importlib.util
import unittest

P=Path(__file__).with_name("independent_firstop_signed_tensor_audit_v2.py")
spec=importlib.util.spec_from_file_location("ttm_t5_auditor_v2",P)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def fake_ref(shape,count):
    return {"torch_shape":shape,"values":[float(i%11)/11 for i in range(count)]}

def fake_native(ne,count):
    return {"ne":ne,"values":[float(i%11)/11 for i in range(count)]}

class ExactFinalShapeAuditV2(unittest.TestCase):
    def test_01_result_norm_retained_batch(self):
        r,n=fake_ref([1,256],256),fake_native([256,1,1,1],256)
        a,b=m.align_values("result_norm",r,n,1)
        self.assertEqual(len(a),256)
        self.assertEqual(a,b)

    def test_02_result_output_retained_batch(self):
        r,n=fake_ref([1,2048],2048),fake_native([2048,1,1,1],2048)
        a,b=m.align_values("result_output",r,n,5)
        self.assertEqual(len(a),2048)
        self.assertEqual(a,b)

    def test_03_flat_reference_legacy_valid(self):
        a,b=m.align_values("result_norm",fake_ref([256],256),
                fake_native([256,1,1,1],256),5)
        self.assertEqual(a,b)

    def test_04_non_singleton_batch_rejected(self):
        with self.assertRaisesRegex(ValueError,"FINAL_STAGE_SHAPE_NOT_ALIGNED"):
            m.align_values("result_norm",fake_ref([2,128],256),
                           fake_native([256,1,1,1],256),1)

    def test_05_wrong_native_shape_rejected(self):
        with self.assertRaisesRegex(ValueError,"FINAL_STAGE_SHAPE_NOT_ALIGNED"):
            m.align_values("result_output",fake_ref([1,2048],2048),
                           fake_native([1024,2,1,1],2048),1)

    def test_06_too_many_batch_dims_rejected(self):
        with self.assertRaisesRegex(ValueError,"FINAL_STAGE_SHAPE_NOT_ALIGNED"):
            m.align_values("result_norm",fake_ref([1,1,256],256),
                           fake_native([256,1,1,1],256),1)

    def test_07_signed_elementwise_delta_not_just_max(self):
        x=m.compare([1.0,-2.0],[0.8,-2.6])
        self.assertAlmostEqual(x["max_abs"],0.6,places=12)
        self.assertAlmostEqual(x["signed_peak"],-0.6,places=12)
        self.assertEqual(x["peak_index"],1)

    def test_08_threshold_and_old_auditor_not_changed(self):
        self.assertEqual(m.STRICT_LIMIT,0.001)
        self.assertEqual(m.SENSITIVITY,1e-5)
        self.assertIn("V2_SINGLETON_BATCH_FINAL_NORM_AND_OUTPUT_ONLY",P.read_text("utf-8"))

if __name__=="__main__":unittest.main(verbosity=2)

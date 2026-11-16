# TTM — Ứng viên bổ sung lineage A/B/C (không chỉnh `lineage.md`)

**Status:** `PROPOSAL_NOT_APPENDED` · **Source snapshot:** main `f7a0a5874e8fd895c8ea8d17ceff393a4d4917a3`; main `lineage.md` Git blob `3409e036241deb1da6674619a2abc834bea8a2d6`; L0000–L0029 (30 mục).

Đây là bản **chỉ mục dự kiến append**, không phải lineage chính thức, không phải merge, không chứa quyết định chạy khoa học mới. **Không cấp số L0030–L0034 bây giờ.** Khi owner phê duyệt cập nhật lineage ở lượt riêng, phải đọc lại main HEAD/lineage blob, cấp số mới tăng dần theo tail thực tế, và giữ từng byte các entry lịch sử. Mọi nguồn giữ SHA chính xác theo báo cáo ở thời điểm nhận.

## ABC-CAND-001 — Track A M0 v3 I1 measurement closure

- **Loại:** `MEASUREMENT_VALIDITY_INDEPENDENT_QA_SCOPED`.
- **Nguồn:** Draft [PR #33](https://github.com/minhtri22/TokenToModel-Lab/pull/33) HEAD `771314c07ba061ebeb1baa87018248ed73181079`, stacked trên Draft PR #28 `ebdc54575eed1ff60c402eecf60289f408bb38ca`; mã đo đã review `ec197b5f00d3a037420390edd11ee55047e1d37f`.
- **Bằng chứng:** [distinct review](https://github.com/minhtri22/TokenToModel-Lab/blob/e3e1c802815f4db1534e92d9848d6015eb9203cc/artifacts/ttm-abc/track-a/M0_V3_POST_HOLD_DISTINCT_I1_20261117/REVIEW.md); 35/35 F01/F02, 38/38 native custody, 80/80 case, 5/5 group; fixture SHA256 `823a08dd4be0da7748cb258b9bf5b2841dd1fdbac84956eb204be7ba57f8c55d`.
- **Quyết định:** `I1_PASS_SCOPED_MEASUREMENT`; `I2_NOT_EXECUTED`, `RELEASE_PREFLIGHT_HOLD_OWNER_INTERNAL_I1_NOT_PASS` exit2. Giữ lịch sử I1 HOLD trước sửa; TOCTOU và freeze receipt admission chưa đóng.
- **Không suy diễn:** NLL/mô hình tốt hơn, I2 đã được cấp GO hoặc đã merge.

## ABC-CAND-002 — Track B M3 GPT Core engineering

- **Loại:** `SYNTHETIC_ENGINEERING_ADJUDICATION_WITH_REVIEWER_DISSENT`.
- **Nguồn:** Draft [PR #34](https://github.com/minhtri22/TokenToModel-Lab/pull/34) exact `43896bcd034c82e8433bc6a2b53eefbd936616fb`; [PM review](https://github.com/minhtri22/TokenToModel-Lab/blob/fdffbf2cc3c517d25dddae89501c091c58f2608d/docs/research/ttm-abc/track-b/independent_review/B_G5_G6_V3_FULL_RECEIPT_INTEGRATED_PM_ADJUDICATION_20261116.md).
- **Quyết định:** `B_M3_PASS_ENGINEERING_BASELINE_SCOPED_BY_PM_ADJUDICATION`; không đổi native V3 original `HOLD_NATIVE_QA` (negative MemoryError nhưng `PeakJobMemoryUsed=429174784 > cap=268435456`); original receipt SHA256 `063bb5770c92881ab8fd0ae485f007026594495109c0c0b0359a0ba686c22188`; differential 3/3 native rejection, reviewer vẫn `HOLD_PEAK_ACCOUNTING`. Bảo toàn song song các góc nhìn.
- **Không suy diễn:** V3 script PASS, peak metric đã được kernel giải thích, mô hình ngôn ngữ khoa học được huấn luyện, quyền sử dụng hard-resource M3 cho SFT mới.

## ABC-CAND-003 — Track C M4 design-only validation

- **Loại:** `DESIGN_INDEPENDENT_QA_SCOPED`.
- **Nguồn:** Draft [PR #35](https://github.com/minhtri22/TokenToModel-Lab/pull/35) HEAD `00afd25aa2234e30f7602592d49d5d9f2947965b`, design source `185d465c31f5f4bef6220be95e39dac1ae81c5b8`, [review](https://github.com/minhtri22/TokenToModel-Lab/blob/9fac5a675955d8b91d6855d27907f239cbfb745f/docs/research/ttm-abc/track-c/independent_review/C_M4_EXACT_AMENDMENT_DISTINCT_REREVIEW_20261116.md).
- **Bằng chứng:** synthetic 35/35 distinct review, 5.000 hội thoại seeded và C-F01/F02 fixed theo contract, chưa kiểm chứng real corpus.
- **Quyết định:** `C_M4_PASS_DESIGN_SCOPED`; C-G1 `HOLD_REAL_DATA_UNAVAILABLE`; C-G2 `DESIGN_VALIDITY_UNPROVEN`; C-G7 `NOT_AUTHORIZED`, C-G8 `NOT_EXECUTED`.
- **Không suy diễn:** data rights đủ cho scientific study, rubric gold thật đạt, equal-compute đã đo, SFT khoa học thực thi.

## ABC-CAND-004 — B–C v2 interface and independent F01–F06 close

- **Loại:** `SYNTHETIC_INTERFACE_ENGINEERING_DISTINCT_QA_SCOPED`.
- **Nguồn:** Draft [PR #36](https://github.com/minhtri22/TokenToModel-Lab/pull/36) HEAD `09de6a46574146d863f416e056fcf01091f3efb8`, code CI `a83e1526bce842761f3051dad28b90a55395a6aa`, stacked trên PR #34. C contract final [report](https://github.com/minhtri22/TokenToModel-Lab/blob/9578291ae7c64ac58960fca679356e956ad9d51b/docs/research/ttm-abc/track-c/independent_review/C_BC_V2_F05_F06_EXACT_HEAD_REVIEW_20261117.md).
- **Bằng chứng:** B author CI 29/29 v1 + 26/26 v2 + 18/18 routed C each OS; C distinct-from-B Part B 34/34 each OS; PM third-actor [12/12 Windows và 12/12 Linux](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43937370201), 0 skip; 8/8 unchanged Git blobs, 7 actual-byte SHA rehashed; original [pre-fix 1 PASS / 2 FAIL](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43923286066) retained.
- **Quyết định:** `BC_INTERFACE_PASS_ENGINEERING_SCOPED`, F01–F06 closed for trusted immutable synthetic CPU bundle. [PM final](https://github.com/minhtri22/TokenToModel-Lab/blob/82aaf2a881bd677afd8f6e600eb570aea897fdba/docs/research/ttm-abc/bc-sft/independent_review/BC_V2_F05_F06_PM_FINAL_DISTINCT_ENGINEERING_ADJUDICATION_20261117.md).
- **Không suy diễn:** metadata checkpoint v2 là real weights, năng lực SFT, paths vô hiệu hóa tất cả Windows reparse/race, owner-native SFT budget, GPU/TEST license.

## ABC-CAND-005 — PM integrated release barrier design

- **Loại:** `PROGRAM_GOVERNANCE_DESIGN_ONLY`.
- **Nguồn:** bản thiết kế tổng hợp trên nhánh governance riêng (trỏ bằng exact commit sau khi đã tạo receipt); main tại snapshot `f7a0a5874e8fd895c8ea8d17ceff393a4d4917a3`.
- **Quyết định:** `PASS_SCOPED_ABC_ENGINEERING_AND_DESIGN_INVENTORY`; `HOLD_ALL_PROSPECTIVE_RELEASES`. Có ma trận barrier R0–R8 cho hai luồng I2 và SFT thật; không phát hành permit hay thay đổi scientific prereg. PR #28/#33/#34/#35/#36 vẫn Draft.
- **Không suy diễn:** bất kỳ GO science/merge/production nào.

## Cây nghiên cứu và quan hệ nguồn

```text
TTM main (L0000–L0029 preserved; includes earlier T4 science and negative studies)
└─ PM A/B/C program #32 (coordination)
   ├─ A M0 measurement -> I1 PASS scoped -> I2 HOLD (PR28 -> PR33)
   ├─ B M3 synthetic core -> PM PASS scoped + V3 historical HOLD/dissent (PR34)
   ├─ C M4 source/design -> PASS_DESIGN_SCOPED (PR35)
   └─ B/C interface v2 -> PASS_ENGINEERING_SCOPED (PR34 -> PR36; C reviewer PR35)
      └─ future real SFT only after rights, checkpoint compatibility, release barriers
```

**Quy tắc:** Cây thể hiện phụ thuộc nghiên cứu, không nói các nhánh đã được merge. Không nhập các ID Lxxxx trùng trên branch-local lineages làm ID global. Nếu phát hiện nguồn chưa nằm trong main, dùng external SHA links, không tạo source metadata giả. Chỉ append khi owner phê duyệt và việc merge/lineage được audit riêng.

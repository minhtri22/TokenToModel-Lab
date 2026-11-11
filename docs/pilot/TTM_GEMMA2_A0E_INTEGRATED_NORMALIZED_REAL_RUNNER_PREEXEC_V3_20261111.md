# TTM GEMMA2 A0E — Integrated normalized source / 4-arm trainer / lexical scorer preexecution v3

**Operation:** \`TTM_GEMMA2_A0E_TWO_PARTY_SOURCE_NORMALIZED_PN_AND_REAL_RUNNER_FINAL_ONE_PACKET_PREEXEC\`
**Ngày:** 2026-11-11
**Scope:** PROSPECTIVE PREEXEC; no model forward, gold unblinding, VAL NLL, GPU or training.
**Parent frozen:** original A0E prereg Git blob \`d6e5d82709b2bc31458f73e7720cdae1e5f5e54e\`, two-party amendment Git blob \`95257120d1450cf05871c9b134a62fb3c84bf890\`.

## Thay đổi hiện thực
- Thêm CPU source verifier tự đọc đúng SHA các ma trận gốc P-A / 3×P-C / 3×N-A / 3×N-C, pinned candidate/model source và chỉ đọc TRAIN windows (không mở VAL labels), xác minh projector, mapped mask và tính alpha trên 1.917 token. Khi có đúng private tensor, script tạo normalized 12 arm-by-seed tensor rows với SHA cho từng mảng, covariance, trace, eigenspectrum, effective rank, TRAIN frequency-vs-norm; không chấm gold.
- Bộ chấm lexical 37 cặp \`word-disjoint\` với 10.000 bootstrap draws, seed 71031, hai contrast L_origin và L_disruption, Holm step-down p + Bonferroni simultaneous intervals conservative. \`--score\` bị chặn nếu không có external Git commit readback receipt trước unblind. Tệp vector/cặp/gold private.
- Bộ huấn luyện 4×3 nguồn thật (mã v1), cùng model TTM gốc, projector trainable, source frozen, optimizer và schedule do manifest khóa, 512 step × 4.096 target, checkpoint READY mỗi 128 step, resume exact claim, chấm fresh VAL sau 12 final checkpoint. \`--execute\` cần explicit owner release \`GO_FOR_A0E_T4\` + marker; \`--fixture\`/ \`--preflight\` không train/infer.
- Guard v3 xác minh cả SHA, schema, status, relationship với prereg, thứ tự seed, 11 loại bằng chứng, không tự động cấp quyền T4. Vẫn giữ guard v1/v2 và tất cả QA cũ nguyên vẹn.

## Chứng cứ thiếu và phán quyết
Private A0E N/P matrices trong thư gốc sinh từ isolated assistant container, chưa được chứng minh có mặt tại Windows owner, không nằm trên GitHub. Thiếu source tensor bundle thực, raw-rights/near-dup và fresh VAL roster, official raw pretrained extraction, đầy đủ input dependencies, optimizer config đã ký, review full covariance/eigenspectrum + morphology/length SMD, kiểm chứng số học trainer và independent scorer trên fixture có ngữ nghĩa. Do vậy mã nguồn có đường thực thi không được phân loại là validated science runner.

**T4 = NO_GO_HOLD**, kể cả khi source fixture CI đạt PASS: các fixture không thể thay thế dữ liệu thực. Không ghi \`lineage.md\` (chỉ scientific results mới được append), không merge main, không tạo L0022. Bảo toàn đầy đủ L0020/L0021 và amendment/HOLD cũ.

**Bước thực hiện tiếp theo:** \`TTM_GEMMA2_A0E_OWNER_PRIVATE_SOURCE_TENSOR_REBIND_AND_INDEPENDENT_FULL_RUNNER_READBACK_ONE_SHOT\` — chỉ nguồn riêng đã SHA và phép kiểm tra hợp đồng còn thiếu; không thêm micro-permit.

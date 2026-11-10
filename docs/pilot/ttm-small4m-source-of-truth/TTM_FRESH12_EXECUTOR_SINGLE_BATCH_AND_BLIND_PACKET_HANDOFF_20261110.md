# TTM-Small-4M FRESH12 — Executor 48/48, bộ chấm A/B vô danh đã bàn giao

**Ngày:** 2026-11-10 · **Task:** `TTM_SMALL4M_FRESH12_EXECUTOR_SINGLE_48_OUTPUT_BATCH_AND_BLINDED_PACKET_HANDOFF`  
**Phạm vi:** một lượt suy luận thật (greedy trên CPU), **chưa chấm khoa học, chưa giải mù**.

## Nguồn và thứ tự bất biến

1. [Tiền đăng ký FRESH12](../../../artifacts/qa/ttm-original1280/fresh12/TTM_SMALL4M_FRESH12_PUBLIC_PREREG_GITHUB_CANONICAL_20261109.json) đã được commit từ trước, Git blob `919c43f2c919fa733b20a9be5d6b965e9649339c`. 12 prompt F01–F12, 2 checkpoint, 2 điều kiện (chỉ khác **một dấu cách ASCII cuối**), greedy argmax, max64, EOS256.
2. [Amendment A01 trước lượt suy luận](TTM_FRESH12_A01_NEUTRAL_PAIR_IDS_AND_CUSTODY_PRE_RUN_20261110.md) commit `cf0b11db6862c16bfe4a8690c6137a92f1d67a3b`. Reviewer `Codex AI (GPT-6)` đã xác nhận `REVIEWER_ONLY` trong [PR issue comment 6757097604](https://github.com/minhtri22/TokenToModel-Lab/pull/13#issuecomment-6757097604), lúc đó packet chưa tồn tại.
3. P02 source Git blob `9762343e06cf800b50574c2871ae1ed58537fb18`; checkpoint step1024 SHA256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`; step1280 SHA256 `ee723407b2c25a18be20e26387a3dd8e4a18e2942d469279b6f0748ff86af0dc`; tokenizer `[tokens,merges]` SHA256 `aea0e2a1a1bc1943f20b767ba2f879e3a47f0cb43b8b66026b1a34a038e014af`.
4. Tiền kiểm: checkpoint `torch.load(..., weights_only=True)`, nạp trọng số `strict=True`, 3.749.376 tham số, 12/12 SHA prompt, BPE roundtrip và 1 dấu cách token ID32; khóa seed escrow đã xác minh SHA. Torch CPU 2.10.0; **không sử dụng Colab/GPU**.
5. Tạo **một** claim nguồn có SHA256 `đã ghi trong biên bản kỹ thuật và bản raw được mã hóa` trước lúc chạy. Sinh **48/48** đầu ra trong 14,31 giây; tất cả có token IDs, checkpoint, điều kiện, stop_reason và text riêng tư; SHA256 file raw `729bb83d177835e8283262210d857e6a012db44c2beed62e967fa8f8fa5a4fa5`. Tổng cộng 2.729 token phần sinh, **7** trường hợp dừng EOS sớm (tổng hợp không phân điều kiện). Không sinh thêm mẫu nào.
6. Chuẩn bị 24 cặp A/B bằng seed gốc đã mã hóa; `A=trimmed` đúng **12/24**, tại mỗi checkpoint **6/12**, đảo cột theo prompt. Xáo thứ tự cặp bằng HMAC domain khác, gán ID `R01`–`R24`, chỉ hiển thị prompt sạch và văn bản A/B; cắt whitespace đầu hai bản theo cùng `lstrip`. 48 đầu ra không bị sửa ở kho raw gốc.
7. Bộ kiểm toán kỹ thuật **tách riêng** đạt `PASS_37_OF_37_AUTHOR_SIDE_SEPARATE_TECHNICAL_AUDIT`. Đây không phải phản biện khoa học độc lập, không chứng minh cải thiện chất lượng. `SCORING=0/144`.

## Hai tệp duy nhất dành cho Codex reviewer (chưa giải mù)

- **[Gói 24 cặp văn bản ẩn nhãn](../../../artifacts/qa/ttm-original1280/fresh12/reviewer/TTM_FRESH12_BLINDED_REVIEWER_PACKET_R01_R24_20261110.md)**, SHA256 UTF-8 `85fec5d290d6639809ca6ba437982fa8bb11cd5e7e0fbcf412d40f7bc9c3a037`. Không có mã `Fxx-C1024/C1280`, tên checkpoint, điều kiện, xác suất hoặc token IDs.
- **[Mẫu điểm 24 × 2 × 3 = 144 ô trống](../../../artifacts/qa/ttm-original1280/fresh12/reviewer/TTM_FRESH12_REVIEWER_SCORE_TEMPLATE_R01_R24_20261110.csv)**, SHA256 `82adbde1d9d942fee9c1761be6f7bf0860cf409725d8b523aedf82022ed2a37d`.

Codex chỉ nhận hai đường trên, rubric đã khóa (đã nhắc trong packet). Không gửi Codex file có nhãn, escrow plaintext, mapping hoặc báo cáo cũ. Không mời Codex đọc file encrypted raw/receipt có metadata trước khi chấm để giảm thiên lệch.

## GitHub source of truth và kho khóa

- **[Raw 48 đầu ra và ánh xạ riêng tư dưới dạng AES-256-GCM](../../../artifacts/qa/ttm-original1280/fresh12/escrow/TTM_FRESH12_ENCRYPTED_RAW48_AND_PRIVATE_MAPPING_20261110.json)**. **Không có khóa giải mã trên GitHub công khai**; khóa owner là tệp riêng đã bàn giao, SHA256 `36ee3b169f507dabe85fa902c6c0a1963bee0973cd334cc79c57d5d8fe929ca7`. Ciphertext receipt SHA256 `3097d66900b0027edcc1c0f81c8467f31e0dbbc8b2d80365fb7c798b2ee64435`.
- [Biên bản packet QA](../../../artifacts/qa/ttm-original1280/fresh12/TTM_FRESH12_EXECUTOR_PACKET_QA_20261110.json), SHA256 `9bc80b2108a6d298cb7522dd891810cad3a329a3046db1cf1326e24a30fd8a6d`; [kiểm toán 37/37](../../../artifacts/qa/ttm-original1280/fresh12/TTM_FRESH12_AUTHOR_SIDE_SEPARATE_AUDIT_20261110.json), SHA256 `542f74984b5f52a149ba46f38db7454c823bada846b1d4b879d702e6c49e4eaa`.
- Nguồn thực thi đã dùng, có thể đối chiếu tại `tools/pilot_t4/fresh12/`: CPU one-shot SHA256 `068b39a0a55e5bd4b6248ae1c3af347f728e9f83b3f4a2ecb2f403d7de431192`; adapter BPE dữ liệu riêng tư SHA256 `84c7c09591423da28cfb9015469ddb748086011e2c9c69367b247197facdd7c1`; packet-builder SHA256 `847302feb2dd055353eceeffeb42f07352e15f490e576e3eb24aaeed298ee685`; material-audit SHA256 `ec41ffae2270a53889461986ce67077c11a58ea101f8a23cf1409f08da83b8dd`. **Không** commit dãy 1.791 private pair IDs; chỉ SHA commitment.
- Riêng original private mapping checksum `ed22...` là chứng chỉ file lịch sử. Phần tái tạo hiện tại đã kiểm seed gốc và thuật toán, nhưng không có bản file lịch sử để khẳng định byte-equal đúng SHA đó; đã ghi rõ giới hạn này trong encrypted raw.

## Điều kiện Codex có thể bắt đầu

`REVIEWER_PACKET=READY` · `EXECUTED=48/48` · `REVIEWER_QUESTIONNAIRE=0/144` · `UNBLIND=NO`. Reviewer chấm 144 điểm nguyên 0–3, công bố CSV+SHA trên GitHub theo quyền hạn, **dừng lại trước giải mù**. Custodian chỉ mở nhãn sau khi SHA phiếu điểm đã khóa.

**Bước thực hiện tiếp theo:** `TTM_SMALL4M_FRESH12_CODEX_AI_BLIND_144_SCORE_SHA_FREEZE_THEN_OWNER_UNBLIND`. Không huấn luyện, không đọc TEST/Q1Q2, giữ PR #13 draft/HOLD, `main` và `lineage.md` bất biến.

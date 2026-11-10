# TTM_GEMMA2 — OOD256 / 12 checkpoint frozen: tiền kiểm tích hợp trước suy luận

**Ngày:** 2026-11-11  
**Operation:** `TTM_GEMMA2_OOD_12_FROZEN_CHECKPOINT_SHA_SCORER_COMPATIBILITY_PREEXEC_GATE`  
**Phán quyết:** `PREEXEC=PASS_SCOPED_STATIC_AND_SYNTHETIC` · `12_CHECKPOINT_BYTE_SHA256=PASS_REAL_12_12` · `12_READY=PASS_METADATA_12_12` · `SCORER_INTERFACE_FIXTURE=PASS_6` · `OOD256_PUBLIC_SEAL=UNCHANGED` · `OOD_INFERENCE=NOT_EXECUTED`. Đây là kiểm tra tiền thực thi (pre-execution gate), không phải một OOD scientific CLAIM.

## 1. Ranh giới quản trị

Nghiên cứu trên **TTM_SMALL_4M_EMBEDDINGGEMMA2**, không hội tụ về TTM `main`. Nhánh: `research/ttm-small4m-embeddinggemma2-ood-design-20261111`. Không sửa, merge, rebase, xóa nhánh khoa học gốc `research/ttm-small4m-embeddinggemma2-token-swap-minimal-proof-20261109`; không thay `lineage.md` L0017–L0020. Không chọn checkpoint, không huấn luyện lại và không tính NLL nào.

Bằng chứng đã đóng băng từ L0020:
- `artifacts/qa/ttm-embeddinggemma2/TTM_SEMANTIC4X3_FINAL_SCIENTIFIC_ADJUDICATION_PUBLIC_20261111.json`, Git blob `23ec04b6fecb014e75066610a0807b92463d56a5`.
- `artifacts/qa/ttm-embeddinggemma2/TTM_SEMANTIC4X3_INDEPENDENT_READBACK_PUBLIC_20261111.json`, Git blob `8f9ca359e33304bef299472603f52c522009c0d9`.
- StudyID chính xác: `ttm_gemma2_semantic4x3_3seed_2048x4096_h768_20261110_v2`.

## 2. SHA-256 byte thực của 12 checkpoint

Đã tìm đúng thư mục nghiên cứu trên Google Drive liên kết, đi theo `S1/S2/S3 → checkpoints → [arm] → step_2048`, thấy mỗi thư mục có đúng `READY.json` và `checkpoint.pt`. Tải **riêng từng checkpoint** (~52.947.597 bytes/tệp) về container kiểm tra tạm; chạy SHA-256 trên byte tải về và so đúng bản L0020. Nạp riêng từng tệp bằng `torch.load(..., weights_only=True, map_location="cpu")` để đọc metadata và tensor shapes, **không tạo mô hình, không gọi forward**. Không commit tệp checkpoint và không sao chép nội dung riêng tư lên GitHub.

| Seed | Arm | SHA-256 đã băm lại thực |
|---|---|---|
| S1 | PT-REAL | `cf3e6863215555b639fd4d3582f77f2b997c05dc5269cd411342bf660632cf46` |
| S1 | PT-PERM | `dd62bf4695ec9dd4175817c1e3c663389b1282ead560a267f02c7d97a54960fb` |
| S1 | NULL-REAL | `59bb203f5ba2a02e56778200d21ec26c2898bed12a2644d9c860ae06aaffe9fb` |
| S1 | NULL-PERM | `9365403b0a2f4499405f348639d8ebd37e9d8997d0d10894ef23d0d57dbddb21` |
| S2 | PT-REAL | `1ea877b7c62e0b17fc757881a54cd1a4bd829128c0e406543723e871c6f432f1` |
| S2 | PT-PERM | `f1dba5a83772d2346222083039012f928917351ba48bdf843f8d4814dc24b60a` |
| S2 | NULL-REAL | `10ad0ffa8ffd58bee5276374562140e9e3bf580695a5a2e4f4d4bfc08ea42b25` |
| S2 | NULL-PERM | `a2740d762abdf760483f460716464631caf68f577491946de6d264b206a4aa5f` |
| S3 | PT-REAL | `272fd3987d5f5505807662ab62153ede927d76f1c87333affa98df8c6f55fb93` |
| S3 | PT-PERM | `c51a947f1d075e90a5199130e79a671c5257714d66a511fc2d9e78bbc7eac89d` |
| S3 | NULL-REAL | `b58a17f65d6ec949095a0d3d1ac3a91f26d3c71c7246a1ea64d2a4d224341c1e` |
| S3 | NULL-PERM | `ac6fe6ed4510eb6212609c1e913d6102782a78dcb4cfc2aa7743f6151ef07235` |

**Kết quả:** 12/12 SHA đúng; 12/12 `READY.json` đọc trực tiếp từ Drive có `step=2048`, seed/arm và SHA đúng, nguồn runner SHA-256 `a3182549739cda848ce0f7f449b1f1455e06419d72295dcee96f0e8a7822f676`. 12/12 checkpoint đều có `schema=ttm.semantic4x3.checkpoint.v1`, 56 tensors, `tok.fallback=(2048,256)`, `tok.source.weight=(2048,512)`, `tok.proj.weight=(256,512)`, `pos.weight=(256,256)`, `head.weight=(2048,256)`, `sampler_cursor=2048` và 2048 train losses. Không thực hiện `optimizer.step` hoặc `model.forward`.

## 3. Kiểm tra giao diện scorer — tuyệt đối không inference

**Không tái sử dụng trực tiếp** `story_score(m,h768)` hay `compute_science(...)` của runner SEMANTIC4X3 vì mã cũ cố định `768` truyện, `1000` cửa sổ và `186655` nhãn; việc dùng trực tiếp là **HOLD_INCOMPATIBLE_H768_HARDCODE**.

Đã tạo giao diện riêng:
`tools/embeddinggemma2_swap/ood_wikitext2_v1/ttm_ood256_scorer_interface_cpu_fixture.py` (Git blob `0ec741687827ba85e4f435d83a9b12207894ed07`; SHA-256 `38c322e297b315480f9f8aa933752f346b7ed42b022f9d3fcdd94c24d72c5dcf`).

Fixture CPU đã chạy thật trên mã **trùng Git blob**: **PASS_6** với logits tổng hợp không phụ thuộc mô hình:
- Kiểm shape cửa sổ 512×256, nhãn 131.072, 2 cửa sổ/bài.
- Kiểm phép dịch next-token trong mỗi cửa sổ và qua ranh giới hai cửa sổ.
- Kiểm NLL uniform `log(2048)` trên logits zeros có sẵn và phép cộng loss vào đúng bài.
- Từ chối nhãn ngoài vocab, shape logits sai, NaN logits, thứ tự bài sai.
- Kiểm tra tĩnh `validate_ckpt_header` trên checkpoint thật (một mẫu), **không forward**; 12/12 checkpoint trước đó đã qua kiểm tra state-shape riêng.

**Giới hạn:** dynamic `make_model`/real-logits/scorer binding chưa chạy, vì như vậy sẽ mở suy luận. Module này là scorer-interface contract, không phải runner thực thi OOD đã được phê duyệt. Khi owner cấp permit, science runner phải khóa đúng source/weights, thực thi scorer 12 arm trên cùng OOD256, với preflight riêng tích hợp trong một lượt; không được sử dụng scorer H768 trực tiếp.

## 4. Bất biến OOD256

Đọc lại từ Windows workspace:
`D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\ttm_gemma2_ood_wikitext2_cpu_v1_20261111`.

- `OOD256_PUBLIC_SEAL.json` vẫn ghi `SEALED_SOURCE_ONLY_NOT_SCORED`, 256 bài, 512 cửa sổ, 131.072 nhãn, không forward.
- Dữ liệu công khai đọc lại có cùng digest SHA-256 chuẩn hoá như seal đã công bố: `0091b56b27c68f1bb724b63181097434d6c7c5922e5cc1de929423b5b0c45438`.
- Private membership SHA-256 gắn trong seal: `627c99db8b39b6479fdb074a82b0ab7eea0367dde49bf0072c29ff410ecdcd5f`.
- Private window SHA-256 gắn trong seal: `3ec7655c512c5d13d4c0d04d1ddbae80b8ea0106aee82064e8dd806786d8336a`.
- Log `SOURCE_CPU_RUN_LOG.txt` và `INDEPENDENT_CPU_READBACK_LOG.txt` từ lượt CPU trước vẫn thể hiện PASS nguồn và độc lập, cùng public seal SHA.

**Giới hạn:** Không băm lại byte của hai tệp private OOD qua RemoteDesktop trong đúng lượt tiền kiểm này; công cụ remote chỉ đọc text, nên kế thừa cổng SHA private đã PASS ngay từ lượt CPU seal trước. Không tự tuyên bố `PRIVATE_OOD_SHA_REHASH_CURRENT=PASS` khi chưa thực hiện.

## 5. Quyết định một lần cho owner

**Kết luận tiền kiểm**: `PASS_SCOPED_STATIC_AND_SYNTHETIC`, đủ để trình một quyết định cho phép **triển khai và thực thi OOD inference-only trên 12 checkpoint frozen**, với các điều kiện bất biến:

1. Không train/resume/finetune, không đổi 12 SHA, 256 tài liệu, tokenizer T1, source revision, 512 target/doc, 2.000 paired-document bootstrap draws hay seed tiền đăng ký `2026111198`.
2. Trước model forward trong science run: một preflight duy nhất xác minh lại 3 SHA của OOD public seal/private membership/private windows, 12 READY/SHA checkpoint, model source bundle/architecture exact, serializer/scorer shape và tài nguyên; lỗi → HOLD, không tiêu thụ CLAIM.
3. Dùng đúng `tau_residual` và `gamma_real` của hợp đồng OOD: 3/3 seed dương cho cả hai, CI95 paired-document bootstrap lower >0 cho cả hai mới PASS; science FAIL hợp lệ không thay L0020.
4. Không được dùng OOD để chọn lại checkpoint/corpus. Giữ per-document loss và các tệp nhạy cảm trong Google Drive riêng tư; chỉ công khai receipt/aggregates và adjudication. Không GGUF/application.
5. Permit tiếp theo là **riêng cho một đợt scoring**, không mở lại training hay cấp quyền GPU tự động trước owner.

**Owner permit:** `NOT_ISSUED` · **OOD inference:** `NOT_EXECUTED` · **OOD scientific CLAIM:** `NOT_CREATED`. Không thêm L0021 cho QA kỹ thuật.

**Bước thực hiện tiếp theo:** `TTM_GEMMA2_OOD_12ARM_INFERENCE_ONLY_ONE_SHOT_OWNER_PERMIT_AND_FROZEN_SCORER_SOURCE_QA`. Một quyết định chủ dự án bao gồm nguồn scorer, QA và chấm OOD 12 arms; không tách thành các micro-permit kỹ thuật.

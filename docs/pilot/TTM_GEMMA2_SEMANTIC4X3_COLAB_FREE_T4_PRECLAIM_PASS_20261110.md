# TTM Gemma2 SEMANTIC4X3 — Colab Free T4 pre-CLAIM PASS và xác minh H768 trực tiếp
**Ngày:** 10/11/2026 · **Study:** `ttm_gemma2_semantic4x3_3seed_2048x4096_h768_20261110_v2`.

**Kết quả kỹ thuật:** `PASS_NO_SCIENCE_CONSUMED`. Người dùng đã chạy notebook chỉ tiền kiểm; `PREFLIGHT_EXIT_CODE=0`. Chưa tạo `STUDY_CLAIM.json`, chưa train, chưa chấm H768. Source PIN hiện tại `9a824e453195cafc530e2289d3b8a87e354faf8905ca73b2f29b79144d657a8d` và H768 public/private PIN theo frozen manifest.

## Các điều kiện đã kiểm
- ZIP `TTM_SEMANTIC4X3_H768_PRIVATE_V1_20261110.zip` hiện trong Google Drive `MyDrive/TTM/ttm-small-pilot`, size **426988 bytes**. Đã tải lại trực tiếp và đọc tất cả ba ZIP entries (dạng backslash trong ZIP Windows được notebook chuẩn hóa khi giải nén), `testzip()==None`.
- `H768_PUBLIC_SEAL.json` SHA256 `9725b1254cde81b77e23b85ab479a08cafc14af0a7a536c7722ca87c7f2a5aa0`, `H768_MEMBERSHIP_PRIVATE.json` SHA256 `0ab671ae59ff4300d8257f2689261d6328afd7563c0aa66b363bc22348c1628f`, `H768_WINDOWS_PRIVATE.npz` SHA256 `1eb5b54b4bb7744e23fffd0fd755d5c91853a773dcc0d2219f777b47ba6a53df` — **3/3 byte-exact** với bản đóng băng. Không xuất bản dữ liệu private.
- Synthetic fixture: runner PASS 8 checks; independent readback PASS 6 checks; dual-matched donor null PASS 6 checks; source parity C2048 PASS exact state/synthetic logits.
- T4 Colab owner output: Tesla T4, torch `2.14.1+cu130`, CUDA `13.0`, VRAM visible 15637086208 bytes, synthetic peak **303281152 bytes**; 768 stories, 186655 targets, 1000 windows.
- 3 TRAIN schedule digests: S1 `35080993e5c0d21cd12235fd5133a1169a19c57bb86e3e07301a2af3e77aa6c6`; S2 `9ec59ae161c2dd40eed7c8f14cdb39da73020a8a38f41274329854df9385fc5b`; S3 `688c0b8f08432e2ed89e74b6c55dd504695acfa47c90dbf224841dc95b9f8c0a`.
- Direct Drive quota check exists in frozen source and is a required fail-closed gate (`storageQuota.limit-usage`); preflight success implies required budget gate passed. **Exact remaining quota GiB not emitted** by owner log. No extra separate quota step required.
- Two `httplib2` per-request timeout messages in stderr are nonfatal in this report; actual preflight exit code 0.

## Ranh giới khoa học

`CLAIM=NOT_CREATED` · `SCIENCE_TRAINING=NOT_EXECUTED` · `H768=SEALED_NOT_SCORED` · `LINEAGE=L0019_UNCHANGED`.
**Không cấp phép science trong commit này.** Runner có `--owner-science-approved` bắt buộc cho `--mode execute`.

24.576 optimizer updates / 12 arms trên Free T4 là ngân sách lớn; QA pre-CLAIM không bảo đảm thời lượng Colab đủ. Frozen anti-replay guard không tự phục hồi chunk 256 steps bị ngắt giữa chừng. Nếu interruption sau CLAIM, không tạo RunID mới hoặc lặp science tự động; giữ evidence để adjudicate.

**Bước thực hiện tiếp theo:** `TTM_SEMANTIC4X3_OWNER_SCIENCE_EXECUTION_DECISION`. Nếu chủ dự án phê duyệt science, cung cấp ô thực thi one-shot sử dụng chính source và inputs đã qua QA; không chạy lại preflight hay H768 seal.

# TTM Small4M A/C — Final integrated owner rights, reviewer, escrow & native Resume preexec closeout

**Ngày:** 2026-11-11 (Asia/Bangkok)  
**Operation:** `TTM_SMALL4M_AC_FINAL_OWNER_RIGHTS_REVIEWER_ESCROW_AND_NATIVE_RESUME_PREEXEC_CLOSEOUT`  
**Final decision:** **`NO_GO_PREEXEC_EXTERNAL_AND_NATIVE_GATES_OPEN`**. Đây là quyết định **tiền thực thi**, không phải FAIL về năng lực mô hình.

## Phạm vi bất biến

- Repo: `minhtri22/TokenToModel-Lab`; nhánh duy nhất `research/ttm-small4m-prompt-conditioning-objective-design-20261110`; base `main=5d52e32f20021e36f08f284ef9864d3ba36dbead` quan sát trong lượt đối chiếu.
- A/C: Parent step1024 checkpoint SHA256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b` và private TRAIN/VAL pack SHA256 `184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913` từ báo cáo trước; checkpoint và pack **không được tải lại hoặc forward** trong lượt này.
- A: uniform valid-token CE; C: suffix-weighted CE (vị trí 0–31 weight1, từ 32 weight3), 128 optimizer steps/arm × 4096 valid labels/step, dữ liệu/lịch lấy mẫu/tensor slots/AdamW/seed/architecture bằng nhau; 1.048.576 lượt target labels trên hai arm **dự kiến, 0 thực thi**.
- Không huấn luyện, không inference Small4M, không đọc hoặc chấm lại TEST, OOD256, Q1/Q2, FRESH12. Không tạo CLAIM khoa học, không đụng private corpus, `lineage.md`, `main`, PR13 hoặc học lại checkpoint. Không tạo nhánh/PR mới.

## 1. Rights: quyền văn bản license ≠ attestation owner

**Nguồn được xác minh:**
- Hugging Face dataset repo `roneneldan/TinyStories` công bố metadata `CDLA-Sharing-1.0`, nguồn `https://huggingface.co/datasets/roneneldan/TinyStories`.
- Văn bản chính thức `https://cdla.dev/sharing-1-0/`: §1.2 định nghĩa `Computational Use`; §1.13 định nghĩa `Use`; §2.1 cấp quyền Use/Publish tuân theo §3; §3.1–3.3 về điều kiện nếu Publish Data/Enhanced Data; §3.5 nói không áp hạn chế riêng về Use/Publication of Results. Đây là rà soát văn bản chứ không phải ý kiến pháp lý.
- Nghiên cứu A/C chỉ chuẩn bị *internal training* trên private pack đã khóa, không phát hành raw corpus, tokenized windows hoặc checkpoint lên GitHub.

**Kết quả:** `LICENSE_COMPUTATIONAL_USE_TEXT=PASS_SCOPED`; `PRIVATE_PACK_PROVENANCE=PINNED_PRIOR_AUDIT_NOT_REHASHED_TODAY`; **`OWNER_SIGNED_SCOPE_ATTESTATION=NOT_RECEIVED`**. Không giả lập chữ ký. Bản ký xác nhận cần đủ việc sử dụng private pack chỉ cho thí nghiệm A/C, thực hiện bên trong repo/Drive, tuân thủ giới hạn không phát hành raw.

## 2. Blind-24: escrow đã thực sự được tạo và mã hóa

- 24 prompt FINAL (Q01..Q24) lấy từ tệp đã khóa `docs/research/TTM_SMALL4M_2X2_NEW_DEV12_BLIND_FINAL24_PROMPTS_FROZEN_20261110.json`, Git blob `f08f15c5049baf77771bed463a5119136566373b` (không tạo tập TEST mới từ dữ liệu TEST cũ).
- 32-byte CSPRNG seed; rank 24 prompt IDs qua HMAC-SHA256; 12 prompt A ở trái và 12 prompt C ở trái; 24/24 IDs duy nhất; không thay thứ tự R01–R24.
- Ánh xạ và seed được mã hóa AES-256-GCM (nonce 96-bit, authenticated associated data gắn run ID và nguồn prompt blob). Hợp đồng công khai nằm ở `artifacts/qa/ttm-small4m-prompt-conditioning/ac_preexec/TTM_SMALL4M_AC_BLIND24_ENCRYPTED_ESCROW_PUBLIC_20261111.json` trên nhánh hiện hữu.
- **SHA-256 public ciphertext package = `519f3185d6202052ce1e5c98a7e7fa58a813d87ce9d9e2d173eb25f6a05f9f1c`**, tính lại từ chính nội dung GitHub readback bằng SHA256 khác với công cụ tạo escrow, **MATCH_EXACT**.
- **SHA-256 decrypted private plaintext = `68d4e303efd2c5809bf0e89f5564f70e1114349b463b5458174c1407e8deda1d`**. Đã kiểm encrypt/decrypt, SHA và cân bằng 12/12 trong sandbox trước upload; không công bố plaintext hay khóa.
- Khóa owner-only lưu tại conversation artifact `TTM_SMALL4M_AC_BLIND24_OWNER_PRIVATE_KEY_20261111.json` (file riêng tư, KHÔNG trong GitHub). Cần owner **tải về `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp` và hạn chế ACL**; chưa có bằng chứng tệp đã được lưu trên máy Windows, vì công cụ RemoteDesktop write bị lỗi. Cấm công bố key hoặc chuyển cho reviewer trước scoring freeze.

**Phán quyết:** `BLIND_RANDOMIZATION=PASS_24_OF_24_BALANCED_12_12`; `ENCRYPTED_GITHUB_ESCROW=PASS_SHA256_EXACT`; **`PRIVATE_OWNER_LOCAL_CUSTODY=HOLD_NOT_VERIFIED`**.

## 3. Reviewer độc lập

- **Chưa thể chỉ định một người chấm hoặc agent độc lập có danh tính được xác minh** từ các kết nối hiện có. Không giả nhận Codex FRESH12 đã chấp thuận nghiên cứu A/C.
- Mẫu owner rights và reviewer acceptance được commit ở `docs/research/TTM_SMALL4M_AC_OWNER_RIGHTS_AND_INDEPENDENT_REVIEWER_SIGNOFF_TEMPLATE_20261111.md`.
- Reviewer cần nhận packet trung tính R01..R24 sau inference, chấm 144 điểm nguyên 0–3 (24 prompt × 2 outputs × 3 axes), khóa score SHA **trước** unblind; reviewer không nhận key/arm mapping, không chính là trainer/prompt author. Nếu AI reviewer thì chỉ có claim exploratory scoped; không gọi human independent QA.

**Phán quyết:** `REVIEWER_IDENTITY=UNASSIGNED`, `INDEPENDENCE_RECEIPT=NOT_RECEIVED`, **`REVIEWER_GATE=HOLD`**.

## 4. Mã nguồn và exact native QA

**Nguồn được bảo toàn trên cùng nhánh:**
- `tools/pilot_t4/prompt_conditioning_2x2/ttm_ac_objective_runner_candidate.py` (Git blob `ad7d88672c65c6778f5956e6fc7aa656b78b998f`), ARM A/C only; khóa owner+rights+eval+reviewer+resume QA+T4 smoke trước science. `--mode source-qa` mặc định không model forward.
- `ttm_ac_resume_store.py` blob `8b02db35854cf24e77246d81dba6a8b8fe2d746e`; `test_ttm_ac_resume_synthetic.py` blob `0c6f89518b919532e1ebc8a8021f79893c4ca10d`; các nguồn kế thừa 4-arm giữ nguyên.
- Từ lượt trước: `STATIC_SOURCE_QA=PASS_23_OF_23` và `CPU_SYNTHETIC_TOY_RESUME=PASS_6_OF_6` chỉ trong phạm vi CPU đồ chơi. **Không** gọi đây là exact native T4 P02 resume.
- Lượt này thêm script `tools/pilot_t4/prompt_conditioning_2x2/Invoke-TTM-AC-Final-Preexec-PS51.ps1`. Script một lần tải 5 source files từ GitHub **pinned commit `6628401b08ea7682cf34aa5078546e1d18e4d2cc`**, so từng Git blob theo bản GitHub, dùng Python3.12 để py_compile/source-qa/6 synthetic tests, xuất JSON vào `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp`. Không đọc TRAIN/TEST hoặc forward TTM; không tự cài thư viện, không overwrite.
- RemoteDesktop `run_command` báo `managed mode requires task_job_submit`; thử `write_file` và device inventory có lỗi nội bộ. **Không có Windows native execute thành công** trong lượt này, cũng không dispatch job/task/science mới.
- Vì chưa có T4, **`FP16_T4_ZERO_STEP_SMOKE=NOT_EXECUTED`**, `ACTUAL_SMALL4M_INTERRUPTED_RESUME_PARITY=NOT_EXECUTED`. Cơ chế checkpoint READY mỗi 32 bước đã staged nhưng từ chối tự động replay khi có journal không được READY xác nhận; do đó chưa có bảo đảm phục hồi toàn diện sau ngắt giữa các mốc.

**Phán quyết:** `SOURCE_SHA_PIN_READY=PASS`; `WINDOWS_PY312_NATIVE_QA=NOT_EXECUTED`; `ACTUAL_T4_RESUME=NOT_EXECUTED`; **`NATIVE_GATE=HOLD`**. Không claim PASS nếu người vận hành chưa gửi `NATIVE_SOURCE_QA_RESULT.json` và biên bản FP16 T4.

## 5. Ma trận cổng cuối

| Gate | Evidence hiện tại | Trạng thái |
|---|---|---|
| Chính xác model/data/schedule A vs C, nguyên checkpoint | Established prior source/pin + SHA | **PASS_SCOPED_SOURCE** |
| Quyền tính toán trên TinyStories theo license | HF metadata + CDLA §§1–3 | **PASS_SCOPED_TEXT** |
| Owner xác nhận sử dụng private pack | Mẫu signoff, không chữ ký | **HOLD** |
| 24 prompt + rubric đã khóa | Source QA trước, không đọc TEST | **PASS_SCOPED** |
| AES-256-GCM 24-pair escrow/12–12 | CSPRNG, encrypt/decrypt, GitHub SHA readback | **PASS** |
| Khóa escrow đã bàn giao lên máy owner | Chỉ có private conversation file | **HOLD** |
| Reviewer độc lập nhận trách nhiệm | Mẫu attestation, chưa reviewer | **HOLD** |
| Windows exact Python312/source/6 toy tests | One-shot PS source pinned, chưa chạy | **HOLD** |
| Colab T4 FP16 + actual interrupted resume parity | Chưa chạy | **HOLD** |
| New owner science lock/CLAIM | Không cấp | **NOT_GRANTED** |

**Quyết định đơn nhất:** `NO_GO_NOW_PREEXEC_HOLD`. Không được thay bằng GO vì escrow PASS; không được gọi FAIL khoa học vì chưa thử can thiệp lên mô hình. Không mở nghiên cứu mới, không đào tạo thêm, không inference, không đọc TEST/OOD/Q1Q2.

**Thay đổi GitHub:** chỉ trên cùng nhánh research, gồm encrypted public escrow, một script native QA, một mẫu signoff, biên bản này. PR13 vẫn DRAFT, `main` và `lineage.md` giữ nguyên. `MERGE_DECISION=HOLD`.

## Bước thực hiện tiếp theo

`TTM_SMALL4M_AC_OWNER_CUSTODY_NATIVE_QA_AND_REVIEWER_ATTESTATION_SINGLE_READBACK`

Một lần **đọc lại và đóng các receipt còn thiếu**: owner tải key private và xác nhận lưu vào TTM workspace; chạy một batch native PS51 source+6 toy Resume QA; nhận owner rights attestation và danh tính/reviewer acceptance; sau đó **chỉ trình science GO/NO-GO một lần** sau khi Colab T4 zero-step smoke và same-run actual Small4M resume parity có bằng chứng. Không tự chạy science, không dùng lại one-shot, không sửa thiết kế hoặc ngưỡng đã khóa.

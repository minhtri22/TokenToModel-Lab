# TTM_GEMMA2 OOD256 — Owner permit, frozen scorer source and one-shot dispatch handoff

**Ngày:** 2026-11-11. **Operation:** `TTM_GEMMA2_OOD_12ARM_INFERENCE_ONLY_ONE_SHOT_OWNER_PERMIT_AND_FROZEN_SCORER_SOURCE_QA`.

## Quyết định của chủ dự án

Owner cho phép **chính xác một lượt suy luận OOD** trên 12 checkpoint frozen từ L0020, với điều kiện tất cả cổng tiền thực thi phải PASS. Không huấn luyện lại, không thay đổi hoặc lựa chọn checkpoint, không thay WikiText-2 OOD256, không chạy GGUF/ứng dụng và không tự thay đổi kết luận L0020. Phán quyết OOD độc lập sau khi có kết quả science và QA.

`OWNER_PERMIT=GRANTED_CONDITIONAL_ON_EXECUTION_GATES`. **Chưa tiêu thụ CLAIM; không có suy luận khoa học trong lượt chuẩn bị mã và notebook này.**

## Nguồn science và kiểm tra tĩnh đã khóa

Đã commit riêng trên `research/ttm-small4m-embeddinggemma2-ood-design-20261111`:
- `tools/embeddinggemma2_swap/ood_wikitext2_v1/ttm_ood256_inference_only_12arm.py`; Git blob `7f6cd35a149569016391128ea6e048ad2930cc80`; create commit `44721a6ac0d206756a0e45db5fd36f60cb177fd6`.
- `tools/embeddinggemma2_swap/ood_wikitext2_v1/ttm_ood256_independent_science_readback.py`; blob `2c278a1e8ce3597307e988a866178981cc81f5f1`; create commit `3f49d16a98d008f2ddb976ce0f8e4d316ce7b2e2`.
- `tools/embeddinggemma2_swap/ood_wikitext2_v1/TTM_GEMMA2_OOD_12ARM_ONE_SHOT_INFERENCE_ONLY_20261111.ipynb`; blob `ef974045e1dbcdf71418077666d9e8812b63a2d9`; create commit `1c012321f326beb23d85badc7acf11aeae6ca4d4`.
- `tools/embeddinggemma2_swap/ood_wikitext2_v1/Prepare-TTM-GEMMA2-OOD256-Private-Colab-Transfer-PS51.ps1`; blob `e8639a526320786f74b8a117e01a85922d239a57`; create commit `d7bc69c90cc95931b12a2e9e94e387491c0b5c1e`.

**Tĩnh qua GitHub connector:** 12/12 SHA frozen literal khớp adjudication L0020; 3 pin OOD match seal; seed bootstrap `2026111198`, 2.000 draws; owner flag trước execute; code chạy preflight trước khi ghi `CLAIM.json`; đúng một callsite tạo logits từ model, chỉ trong execute; không có optimizer step/backward/train_chunk; QA độc lập không forward; notebook JSON parse được, đúng 5 cell và kiểm Git blob. Kiểm thử bằng Python/Colab thực của mã mới **chưa thực thi ở đây**; notebook thực hiện các fixture tự động trước bất cứ forward nào.

## Dữ liệu và checkpoint

Nguồn checkpoint 12 × `step_2048` trên Google Drive cá nhân đã đạt đối chiếu SHA thực 12/12 ở lượt preexec. Mọi checkpoint phải được **băm lại** trong lượt preflight ở Colab, đúng study gốc, metadata và kiến trúc. Gói donor/source `TTM_GEMMA2_CAUSAL6_INPUT_PRIVATE_V1_20261109.zip` pin SHA-256 `2c6cb72f35eba72d6014f15914d6e9792cbf0bf6774d93e3ff5c53e5c6b9ba9a`. Chỉ trích hai file mã nguồn `p02_exact.py` và `ttm_embeddinggemma2_swap.py`, với các SHA-256 gốc; không load TRAIN/H512/H768.

Nguồn OOD256 sealed hiện nằm duy nhất trên Windows:
`D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\ttm_gemma2_ood_wikitext2_cpu_v1_20261111`.
Một PowerShell `Prepare-TTM-GEMMA2-OOD256-Private-Colab-Transfer-PS51.ps1` đã được đặt tại `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp`, đã có exact textual readback. Script tạo gói ZIP ba file OOD private sau khi kiểm SHA ba tệp. **Chưa chạy script đóng gói ở lượt này**; chưa đưa ZIP vào Colab/Drive. Không tải dữ liệu private lên GitHub.

Colab notebook đọc tại `/content/drive/MyDrive/TTM/ttm-small-pilot` (study/zip đã có trong Drive). Mỗi gói riêng tư được upload tương tác, xét exact member list/SHA và lưu trong thư mục Drive private cùng root nghiên cứu. Colab GPU T4, bộ code Python từ commit SHA/Git blob pinned. Khi cell chạy toàn bộ fixture PASS và preflight SHA/source/model GPU PASS, notebook dùng cờ owner approval sẵn có để tạo CLAIM **một lần duy nhất**, sau đó chấm cả 12 arm và ghi private receipts. Không auto retry nếu CLAIM đã tồn tại; phải adjudicate một sự cố trước khi chạy tiếp.

## Công thức khoa học bất biến

512 next-token labels/doc × 256 docs = 131.072 labels. `delta_PRE=L(PT-PERM)-L(PT-REAL)`; `delta_NULL=L(NULL-PERM)-L(NULL-REAL)`; `tau_residual=delta_PRE-delta_NULL`; `gamma_real=L(NULL-REAL)-L(PT-REAL)`. Đánh giá trên 3 seed × 4 arm; bootstrap *paired-document* đúng 2.000 draws, seed 2026111198, condition on 3 seeds. Yêu cầu 3/3 seed dương cho hai estimand và CI95 lower >0 cho cả hai để được candidate PASS. Nếu không đạt: **science FAIL**, không được chọn lại data/checkpoint. Kết quả `RESULT.json` luôn `COMPLETED_PENDING_INDEPENDENT_ADJUDICATION`; independent scorer khác sẽ kiểm tra lại per-doc và CI, chỉ sau đó xem xét dòng khoa học mới trong `lineage.md`. Không động L0020.

## Trạng thái và dispatch

`OWNER_PERMIT=GRANTED`; `FROZEN_SOURCES=COMMITTED`; `GITHUB_STATIC_PIN_QA=PASS_SCOPED`; `LIVE_SOURCE_SYNTHETIC_QA=NOT_EXECUTED`; `PRIVATE_TRANSFER_TO_COLAB=NOT_EXECUTED`; `LIVE_ALL_PREEXEC_GATES=NOT_EXECUTED`; `CLAIM=NOT_CREATED`; `OOD_INFERENCE=NOT_EXECUTED`; `SCIENCE_ADJUDICATION=NOT_EXECUTED`.

Không tuyên bố đã chạy inference cho đến khi nhận và đọc lại `CLAIM.json`, `RESULT.json`, `PER_DOCUMENT_PRIVATE.json` và independent receipt từ đúng StudyID; chỉ công khai các SHA/aggregates và phán quyết, không đưa private text/loss lên GitHub.

**Bước thực hiện tiếp theo:** owner chạy đúng PowerShell đã stage để tạo ZIP private, mở đúng notebook GitHub trong Colab có GPU T4, chọn Run all một lần và upload đúng ZIP. Không cần xin permit lần hai; nếu không có T4 hoặc bất kỳ pin nào sai, báo HOLD trước CLAIM.

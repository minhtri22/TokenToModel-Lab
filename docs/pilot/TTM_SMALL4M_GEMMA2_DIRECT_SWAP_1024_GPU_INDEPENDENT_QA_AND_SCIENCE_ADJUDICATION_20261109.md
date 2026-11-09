# TTM-Small-4M × EmbeddingGemma 2 — 1.024 bước GPU: kiểm định độc lập và kết luận khoa học

**Ngày:** 2026-11-09. **Run ID duy nhất:** `ttm_small4m_gemma2_directswap_1024x4096_t4_gpu_20261109_v1`.
**Phán quyết:** `DIRECT_SWAP_1024_BENEFIT_NOT_ESTABLISHED` (**không đạt điều kiện cải thiện đã khóa**).
**QA độc lập:** `PASS_INDEPENDENT_SCOPED_CPU_REPLAY` (khác biệt FP32 GPU/CPU cho NLL < 4×10⁻⁸; không chạy lại huấn luyện).
**Môi trường được báo cáo:** **Tesla T4**, CUDA FP32, PyTorch `2.14.1+cu130` theo CLAIM gốc.

## 1. Phạm vi thực hiện và nguồn đã khóa trước kết quả

- [Hợp đồng tiền đăng ký 1024×4096](TTM_SMALL4M_GEMMA2_DIRECT_SWAP_FINAL_1024_GPU_EQUAL_EXPOSURE_PREREG_20261109.md), commit **`6715c0a46aa30c3e4fee8647d4540d523d26c619`**.
- [Mã nguồn phát hành có SHA](TTM_SMALL4M_GEMMA2_DIRECTSWAP_FINAL1024_GPU_SOURCE_RELEASE_AND_HANDOFF_20261109.md); runner `ttm_directswap1024_gpu_once.py`, SHA-256 **`00416c0ff5b2afdcca2780a20315dd2da0af93554cd2b32b6c94efb630dc5d3b`**; P02 SHA256 `e0fcac285918b66b13c8f694e6d625a0691c9b59221b43043e63f46b25ddcc07`, module donor SHA256 `d11da61e9d7bb040f3263e680f026817a513553c186ab243e184ffaf6e68cd39`. Source-release ZIP SHA256 `e544c645635a28fe140802421d03a7928a7f0446d2df33bbfe4ec129e3a6ea27`.
- Checkpoint TTM 1.024 bước **trước thử nghiệm** `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`; mapped Gemma candidate `c9fc798d8880c7e76636258052e9885dbb086d7b462a5b6bee5cff8b582973c3`. Dữ liệu TRAIN/VAL `184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913`; manifest `ef2e6e67d49b1d5a921b1051df329f15574f1c10cece0ce49468acb53322d650`. Không chứa TEST.
- Ngân sách đầy đủ: **4 nhánh × 1.024 optimizer steps × 4.096 valid TRAIN targets/step**, tức **4.194.304 lượt nhãn mỗi nhánh**, **16.777.216 tổng lượt nhãn**. A tied baseline, B untied control, C donor thật + ridge adapter, D hoán vị donor cùng kiến trúc. Cùng lịch TRAIN SHA256 `19ddc05128c188b86bda2f02de6389946944fe287c26abbf7d24cc5f9681e8f2`, AdamW mới cho mọi nhánh; không tải lại donor và không dùng GPU ngoài lượt này.
- Các nhánh **tiếp tục từ checkpoint TTM vốn đã huấn luyện 1.024 bước**; đây là 1.024 bước **bổ sung**, không phải huấn luyện từ đầu. Số bước/nhãn bằng nhau, FLOPs không hoàn toàn bằng nhau.
- Thư mục bằng chứng riêng tư trên [Google Drive](https://drive.google.com/drive/folders/1JeRva6DWqT8b0ltC9R3SIz7ZhXEyuNe4), chứa [CLAIM](https://drive.google.com/file/d/1gd47rTuXCUuOJ_9Il56r_HVu0cDPJPej/view), [RESULT](https://drive.google.com/file/d/1WNcmugx6hF9lpALiiw5PKNEUU8yB82QJ/view), [PER_STORY_PRIVATE](https://drive.google.com/file/d/1gfNeiCmTJpe8b_XWw8n6LHhUiAzHJ1OT/view), TRAIN schedule riêng tư và 16 checkpoint tiến trình/READY mốc 256/512/768/1024.
- SHA256 nguyên bản **CLAIM** `d7e99b831dcb69688e4a1483732f174125f8e1a10d5e73cea5c4ef9efcfb3011`, **RESULT** `46a93c888063c27711541c067d168ded31bbf22f6c46ba6efe45051cdc9c0bec`, **PER_STORY_PRIVATE** `3d23e6d2502060f3b7b134e6247a249dc7dd59f8dff89049764f8841a68f42da`. Mã hash per-story trong RESULT trùng khi tính lại bytes.

## 2. Kết quả chính — VAL không mới, một seed, thăm dò

Chỉ sau khi **4/4 nhánh đều có step1024 READY** mới tính NLL trên cùng 328 VALIDATION windows, 256 câu chuyện, 61.122 nhãn.

| Nhánh | NLL cuối (nats/target) |
|---|---:|
| **A — tied TTM gốc** | **3.3501216607592945** |
| **B — untied** | **3.3132221934441275** |
| **C — donor EmbeddingGemma2** | **3.3604018255302230** |
| **D — donor hoán vị** | **3.4754170724567890** |

Bootstrap ghép cặp ở mức **256 truyện**, 1.000 lượt, seed20261109; dấu dương là C tốt hơn nhánh đứng trước:

| Chênh lệch | Giá trị | 95% bootstrap CI | Đạt cận dưới >0? |
|---|---:|---|---|
| A−C | **−0.010280164771** | [−0.017725554696; −0.002999991324] | **Không** |
| B−C | **−0.047179632086** | [−0.055777096957; −0.038942255236] | **Không** |
| D−C | **+0.115015246927** | [+0.106598415283; +0.123453865859] | **Có** |

Điều kiện prereg yêu cầu cả **ba** cận dưới >0. Chỉ D−C đạt. Kết luận **`DIRECT_SWAP_1024_BENEFIT_NOT_ESTABLISHED`** là kết quả âm tính theo phạm vi này, không phải lỗi mô hình. C gần A hơn nhiều so với lượt 64 bước nhưng vẫn **kém A và B**, do đó không được nâng kết quả lên PASS.

**Giới hạn:** VALIDATION đã dùng trong T4 và các lượt 64-step trước; dữ liệu này không còn độc lập với quá trình lựa chọn hướng nghiên cứu. Một seed, chưa có đánh giá unseen TEST mới, không kết luận cải thiện tổng quát hoặc sản phẩm công nghiệp.

## 3. Kiểm toán độc lập nguồn và checkpoint

- Đã đọc đủ **4 checkpoint step1024** từ Drive và tính SHA256 byte thực:
  - A `95bb69de752bf051958f0d8e19a388528d2cc102f02258c88d756526a9406aa2`, 45.100.187 bytes.
  - B `8ecca1e181726965d4f6e76c8e725b612706d5242accd408a9386964939191d1`, 51.393.267 bytes.
  - C `cb77a5c2e435dd8cf1f61259f560a22964bc8c8c06889b0494cb961ed76bc9ac`, 52.969.605 bytes.
  - D `81003fa2fe194a7e22b30d1b3e330fc65ec0ae486a08511d17c367ec5c25f69f`, 52.969.605 bytes.
- Từng checkpoint `torch.load(..., weights_only=True)` nạp được, meta `step=1024`, `run_id`, arm, schedule SHA256, source SHA256, input pins và 1.024 giá trị loss đều khớp; model/optimizer state tồn tại. A/B model 53 tensor keys, C/D 56 keys.
- **CPU model-forward replay độc lập:** dựng model và nạp state dict trực tiếp, tính lại cross-entropy trên đúng VAL bằng mã riêng, không dùng evaluator của runner GPU. NLL CPU lần lượt A `3.350121660634`, B `3.313222156313`, C `3.360401818181`, D `3.475417075082`. Chênh lệch tuyệt đối so với GPU lần lượt `1.25e−10`, `3.71e−8`, `7.35e−9`, `2.63e−9`. Tối đa sai lệch loss-sum theo truyện < `0.0002` nats, chấp nhận khác biệt FP32 CPU/GPU.
- **Bootstrap QA độc lập:** đọc 256 tổng loss/truyện gốc từ Drive, tính lại NLL của mọi arm chính xác, so sánh ba hiệu ứng và tái lấy mẫu 1.000 lần cùng seed, **khoảng tin cậy khớp bitwise ở Python double** với RESULT. Mọi nhãn đều từ VAL trong pack TRAIN/VAL; không đọc TEST.
- Biên bản QA JSON độc lập có SHA256 `9dc722ae8363fd325118332353396e888faef0f74715eaf976597017b9ad914e` (mã kiểm tra cũng được lưu ngoài repo, chỉ công bố số tổng hợp). **Đây là independently executed CPU re-evaluation, không phải chạy lại GPU training và không phải review bởi bên thứ ba bên ngoài.**

## 4. Quyết định đúng nguyện vọng người sở hữu

**STOP** mở rộng thêm phương án naive direct swap `E_TTM = W E_Gemma(t)`; đây là lượt GPU 1.024 bước cuối đã được ủy quyền, không đạt lợi ích NLL trước TTM gốc theo tiêu chí đã khóa. **GO cho hướng residual/gated embedding chỉ ở giai đoạn thiết kế**, theo [review cơ chế đã có](TTM_SMALL4M_EMBEDDINGGEMMA2_MECHANISM_REVIEW_AND_STOP_GO_DESIGN_ONLY_20261109.md): giữ `E_original`, học hiệu chỉnh `E_original + tanh(a) ⊙ (W E_Gemma−E_original)`, gate zero-init. Không tự chạy 32/128/1024 bước hoặc mở TEST theo kết luận này.

- **TTM-Small T5 vẫn ưu tiên hàng đầu**; không merge hoặc sửa PR #12.
- Giữ `D1_G4_R1_R2_R3=DEFERRED`.
- Kết quả khoa học này được nối thêm `lineage.md` một mục L0015, không sửa L0000–L0014.
- CHECKPOINT, RESULT, per-story dữ liệu gốc giữ nguyên ở Drive; không đưa token VAL/weights cá nhân vào GitHub.

**Cuối:** `GPU1024=COMPLETED_4_OF_4` · `QA=PASS_INDEPENDENT_SCOPED_CPU_REPLAY` · `PRIMARY_GAIN=FAIL_WITHIN_SCOPE` · `DIRECT_SWAP=STOP` · `GATED_RESIDUAL=GO_DESIGN_ONLY` · `TEST=UNCHANGED` · `NEW_TRAINING=NOT_AUTHORIZED`.

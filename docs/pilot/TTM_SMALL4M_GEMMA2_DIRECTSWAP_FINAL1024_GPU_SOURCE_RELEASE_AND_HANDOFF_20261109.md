# TTM-Small-4M × EmbeddingGemma 2 — handoff một lượt GPU 1.024 bước

**Ngày:** 2026-11-09. **Quyết định người sở hữu:** thực hiện **một phép thử cuối cho phương án thay token embedding trực tiếp**, với **1.024 bước GPU** thay cho kết luận dựa duy nhất vào 64 bước. Nếu sau thử nghiệm mới vẫn không vượt mô hình TTM gốc, **dừng direct swap và chuyển tới thiết kế residual/gated embedding đã đề xuất**. Quyết định này điều chỉnh ưu tiên `DIRECT_SWAP=STOP` trong báo cáo thiết kế ngày 09/11 thành `DIRECT_SWAP=ONE_FINAL_OWNER_AUTHORIZED_1024_GPU_TEST`; không xóa hay thay phán quyết khoa học 64 bước.

## Source lock và sẵn sàng chạy

- **Phạm vi khoa học khóa trước mã chạy:** [preregistration 1024×4096](TTM_SMALL4M_GEMMA2_DIRECT_SWAP_FINAL_1024_GPU_EQUAL_EXPOSURE_PREREG_20261109.md), commit `6715c0a46aa30c3e4fee8647d4540d523d26c619`.
- **Mã nguồn đã ghim**: `tools/embeddinggemma2_swap/TTM_GEMMA2_DIRECTSWAP_GPU1024_SOURCE_20261109.zip`, immutable Git commit `a22a7d3913b049b93006efa9475ca574ab2877a9`, Git blob `6f9ea49b808f4b5a443978907acfed2de3f9cf1e`, **SHA256 `e544c645635a28fe140802421d03a7928a7f0446d2df33bbfe4ec129e3a6ea27`**; chứa chính xác ba nguồn `p02_exact.py`, `ttm_embeddinggemma2_swap.py`, `ttm_directswap1024_gpu_once.py`.
- Runner Python **SHA256 `00416c0ff5b2afdcca2780a20315dd2da0af93554cd2b32b6c94efb630dc5d3b`**. P02/Swap module lần lượt `e0fcac285918b66b13c8f694e6d625a0691c9b59221b43043e63f46b25ddcc07` và `d11da61e9d7bb040f3263e680f026817a513553c186ab243e184ffaf6e68cd39`.
- **Notebook Colab**: [TTM_GEMMA2_DIRECTSWAP_GPU1024_COLAB_20261109.ipynb](../../tools/embeddinggemma2_swap/TTM_GEMMA2_DIRECTSWAP_GPU1024_COLAB_20261109.ipynb); Git blob `4e95ec0ef5c0888508ed5de77d1ce7841655fe9a`. Notebook tự lấy ZIP đúng commit+SHA; **không cần người dùng tải ZIP**.
- **Bản sao nguồn Drive (không cần tải):** https://drive.google.com/file/d/1WYhjTWLio4pv4RdqPSQABn21A4kD75yF/view .

## Bằng chứng kỹ thuật trước lượt huấn luyện

Trên CPU, chỉ kiểm tra nguồn và khớp hình dạng, **chưa có optimizer step nào của thí nghiệm thật**:
- 6/6 tệp nguồn/đầu vào SHA256 verified theo manifest đã khóa.
- Tạo lịch TRAIN-only bằng NumPy `default_rng(20261180)`: **1.024 bước**, tổng **4.194.304 nhãn mỗi arm**, mỗi bước đúng 4.096 và số cửa sổ/bước từ 19–30. **Schedule SHA256 `19ddc05128c188b86bda2f02de6389946944fe287c26abbf7d24cc5f9681e8f2`**; không chứa TEST.
- A/B logits ban đầu trùng bitwise; C/D nạp có shape `[1,6,2048]`, finite, C≠D.
- Hợp đồng fail-closed không có CUDA: không tạo CLAIM. Một bước fake TRAIN cho A và C (dữ liệu **giả lập**, không phải TinyStories) cho gradient finite; mô phỏng checkpoint READY-last tại mốc 256, đọc lại SHA và optimizer/model state thành công. Không dùng GPU, không viết vào Drive hoặc nhánh main trong các kiểm thử này.

## Cách chạy — đúng một lần trên Colab Free Tesla T4

1. Mở notebook GitHub nói trên trong Google Colab, chọn **Runtime → Change runtime type → T4 GPU**; chỉ dùng khi không tranh tài nguyên với TTM-Small T5. Không đổi `RESUME=False` trong lượt đầu.
2. Chạy **Run all**. Code kiểm SHA256 của **checkpoint gốc** `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`, **candidate donor thật** `c9fc798d8880c7e76636258052e9885dbb086d7b462a5b6bee5cff8b582973c3` và TRAIN+VAL pack `184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913` trước khi tiêu thụ RUN_ID.
3. Lượt khoa học duy nhất `ttm_small4m_gemma2_directswap_1024x4096_t4_gpu_20261109_v1`: **4 arms A/B/C/D × 1.024 bước × 4.096 nhãn = 16.777.216 lượt nhãn**, chung lịch TRAIN, AdamW mới lr1e-4/gradient clip1/CPU FP32? **Chính xác CUDA FP32**. Không tái sử dụng optimizer T4 cũ; không tải lại raw EmbeddingGemma2.
4. Mỗi arm ghi checkpoint **256/512/768/1024** vào **thư mục riêng** dưới `MyDrive/TTM_Small4M_EmbeddingSwap/<RUN_ID>/checkpoints/<arm>`, SHA được đọc lại rồi mới ghi READY. **Khi Colab ngắt**, đổi `RESUME=True`, chạy lại đúng notebook và **cùng RUN_ID**; không tạo science ID mới. Nếu `RESULT.json` tồn tại thì không chạy lại.
5. Chỉ khi cả bốn arm đạt 1.024 bước mới chấm VALIDATION một lần: `RESULT.json` (aggregate) và `PER_STORY_PRIVATE.json` (chỉ trên Drive), cùng 256 truyện/61.122 nhãn. **T4 TEST không được đọc lại**. Sau khi có kết quả, kiểm định độc lập các checkpoint và phép tính NLL/bootstrap, rồi mới ghi `lineage.md` nối thêm.

**Cổng diễn giải khoa học duy nhất:** CI95% dưới `A−C>0`, `B−C>0`, `D−C>0` đồng thời trên VALIDATION. Nếu không đạt: `DIRECT_SWAP_1024_BENEFIT_NOT_ESTABLISHED` → **STOP phương án thay trực tiếp, GO thiết kế zero-gated residual (chưa mở training tự động)**. Nếu đạt: `DIRECT_SWAP_1024_POSITIVE_EXPLORATORY`, cần đánh giá độc lập mới; không suy diễn TEST/production-ready.

**Ranh giới quan trọng:** đây là **1.024 bước thích nghi thêm từ checkpoint vốn đã train 1.024 bước**, không phải 1.024 từ đầu. Ngân sách bằng nhau về bước/nhãn giữa bốn nhánh, không bằng nhau về FLOPs. VALIDATION đã được dùng trong các nghiên cứu trước; chỉ gọi bằng chứng thăm dò.

## Trạng thái hiện tại

`DESIGN_PREREG=FROZEN` · `SOURCE_COMMIT=PINNED` · `STATIC_QA=PASS_SYNTHETIC` · `T4_GPU_TRAINING=NOT_EXECUTED` · `NEW_CLAIM=NOT_CREATED` · `TEST=SEALED` · `G4_RAG=DEFERRED` · `TTM_SMALL_T5=PRIORITY_FIRST`.

Không thay checkpoint gốc, không merge, không thay PR #12, không dọn nhánh hoặc append `lineage.md` vì chưa có kết quả khoa học mới.

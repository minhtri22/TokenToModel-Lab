# TTM-Small-4M T4 — Model Card (bản nghiên cứu, chưa phát hành)

**Ngày:** 2026-11-09 · **Mô hình:** TTM-Small-4M original T4 · **Tình trạng:** `RESEARCH_ONLY / WEIGHTS_PUBLIC_RELEASE_HOLD` · **Độ tin cậy:** nguồn GitHub đã ghim, kết quả khoa học/QA phân biệt riêng.

> Đây là bản thông tin mô hình (**model card**) phục vụ người nghiên cứu và reviewer; **không** phải tuyên bố mô hình sẵn sàng sản phẩm, hướng dẫn y tế/tài chính hay giấy phép phân phối checkpoint. Không gắn `license: mit/apache-2.0` khi chưa xác lập giấy phép TTM.

## 1. Mục đích và nguồn gốc

TTM-Small-4M là mô hình Transformer **decoder-only** tự xây từ các lớp PyTorch P02 nhằm học cách dự đoán token tiếp theo trên một tập nhỏ TinyStories tiếng Anh. Không kế thừa trọng số pretrained của TinyStories-1M/3M, EmbeddingGemma2 hay các mô hình lớn khác. Các nhánh EmbeddingGemma2/SIX là nghiên cứu riêng, không thay đổi model card này.

- Mã nguồn P02 chính xác: Git blob `9762343e06cf800b50574c2871ae1ed58537fb18`, xem [mã P02](../../src/p02/transformer_core.py).
- Kiến trúc: **3.749.376 tham số**, vocab BPE-2048, context 256 token, embedding width 256, 4 block, 4 heads, LayerNorm, causal attention, tied embedding/head; khởi tạo trọng số từ đầu.
- Tokenizer: GPT-2-style byte-level pretokenization + BPE **TRAIN-only**, 768 truyện để khớp 1.791 merges; EOS ID 256.
- Tập nghiên cứu: TinyStories `roneneldan/TinyStories`, bản ghim `f54c09fd23315a6f9c86f9dc80f725de7d8f9c64`, tách TRAIN 2.048 / VAL 256 / TEST 64. Giới hạn chống trùng gần chỉ được chứng nhận **trên các tập con được nhận vào pilot**. Xem [dataset card](../data_governance/TTM_SMALL4M_TINYSTORIES_DATASET_CARD_20261109.md).

## 2. Tập trọng số và nguồn bằng chứng

| Đối tượng | Trạng thái | SHA-256 |
|---|---|---|
| Checkpoint T4 chính step **1024** | Đã huấn luyện & có H1 khoa học trên VAL | `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b` |
| Checkpoint gốc tiếp tục **1280** | Chạy tiếp 256 bước, VAL thăm dò | `ee723407b2c25a18be20e26387a3dd8e4a18e2942d469279b6f0748ff86af0dc` |
| GGUF F32 được xuất từ step1024 | 52/52 tensor exporter readback, Ollama import/sinh thành công | `5bdc904e6c51af04a4223219f36e6bc2e687f60fd6e17dc24508f3eb7489e4e5` |

Các SHA chỉ xác định hiện vật; **trọng số gốc, bộ token TRAIN/VAL, GGUF không được upload lên GitHub public**, và đường dẫn lưu riêng không phải tuyên bố quyền phân phối. Checkpoint 1280 không thay thế checkpoint step1024 được lựa chọn trước cho H1 chính.

## 3. Huấn luyện

- Nền tảng thực nghiệm: **Google Colab Free Tesla T4** cho lần huấn luyện gốc; checkpoint và `READY` được xác minh bằng SHA từ Drive, không chạy lại chỉ để tạo card.
- Run H1 step1024: 1.024 optimizer steps × **4.096 vị trí nhãn hợp lệ/bước** = 4.194.304 lượt nhãn; **AdamW**, peak LR `3e-4`, warmup 32, cosine đến `3e-5`, FP16, microbatch 8 cửa sổ và gradient accumulation động, seed `20261108`. Kiểm định VAL mỗi 128 bước; checkpoint 256/512/768/1024.
- Hợp đồng phục hồi lưu **model + optimizer + scheduler + sampler/cursor + RNG Python/NumPy/PyTorch CPU/CUDA + GradScaler**; đây là khả năng hồi phục kỹ thuật, không khẳng định huấn luyện đa seed.
- TRAIN có 498.287 vị trí nhãn gốc; số lượt dùng danh nghĩa ở 1024 bước khoảng **8,417×**. Tiếp tục 1280 bước đưa tổng ngân sách lên 5.242.880 lượt nhãn (~10,52×); không đồng nghĩa mỗi vị trí được thấy đều nhau.
- Mã chạy và prereg tham chiếu: [A2 protocol](../pilot/TTM_T4_A2_CONTINUOUS_1024_STEPS_PROTOCOL_AMENDMENT_20261108.md), [formal H1 adjudication](../pilot/TTM_T4_A2_REAL_SCIENCE_H1_FORMAL_ADJUDICATION_20261108.md).

## 4. Kết quả khoa học và kết quả kỹ thuật **phải tách riêng**

| Kết quả | Bằng chứng | Diễn giải được phép |
|---|---|---|
| **H1 VAL confirmatory scoped** | Step1024 Model VAL NLL `3.5223388517`; TRAIN-only add-α=0.1 bigram `3.9972314169`; giảm NLL tương đối **11,8805%**; CI95 bootstrap theo truyện của lợi thế bigram−model `[0.45818675,0.49406158]` | PASS so với bigram đúng **pilot/VAL**, 1 seed; không suy ra chất lượng trò chuyện |
| **TEST descriptive one-shot** | 64 truyện / 14.669 nhãn; model NLL `3.4835910733`; bigram `3.9736037453` | Một phép đo TEST đã tiêu thụ; **không chạy lại, không chọn model từ TEST**, không có độc lập per-token recompute |
| **1280 exploratory VAL** | Model VAL NLL `3.4980890267` so với step1024 `3.5223388569`; Δ giảm khoảng `0.02425` | Tín hiệu huấn luyện thêm cải thiện NLL, **không chứng minh cải thiện sinh** |
| **Sinh truyện / semantic prompt adherence** | 8 prompt ban đầu, đánh giá AI chấm mù; hậu kiểm 32 cặp về bỏ dấu cách, `SEMANTIC_GAIN=INDICATIVE_NOT_CONFIRMED` | Khả năng bám prompt yếu; một AI reviewer và A/B mất cân bằng ở lượt trước; không tuyên bố cải thiện xác nhận |
| **GGUF/Ollama integration** | Ollama tạo model và trả 32 token thực tế | **PASS compatibility only**; strict llama.cpp vs PyTorch trained logits **FAIL 7/8 vẫn giữ nguyên** |

Tài liệu tham chiếu: [H1](../pilot/TTM_T4_A2_REAL_SCIENCE_H1_FORMAL_ADJUDICATION_20261108.md), [TEST](../pilot/TTM_T4_TEST_64_SCIENCE_ADJUDICATION_AND_T5_TRAINED_F32_EXPORT_20261108.md), [Ollama](../pilot/TTM_T5_OLLAMA_IMPORT_AND_INFERENCE_COMPATIBILITY_FINAL_ADJUDICATION_20261109.md), [nhánh đánh giá chất lượng PR #13](https://github.com/minhtri22/TokenToModel-Lab/pull/13).

## 5. Cách sử dụng dự kiến và không dự kiến

**Dùng cho:** tái lập nghiên cứu trên dữ liệu nhỏ, minh họa quá trình tokenize/train/save/resume, đánh giá NLL, đối chiếu CPU/GGUF, thiết kế cache Dense/Paged, dạy các giới hạn của mô hình nhỏ.

**Không dùng cho:** chatbot trợ lý tin cậy, thực hiện chỉ dẫn phức tạp, suy luận kiến thức thế giới, sản xuất/vận hành, nội dung cho trẻ em không kiểm duyệt, an toàn/giáo dục/luật/y tế/tài chính quyết định tự động. Không tuyên bố an toàn vì nguồn là “truyện thiếu nhi”.

**Giới hạn:** tiếng Anh truyện ngắn đơn giản; dữ liệu nhỏ và nhiều lần lặp; 1 seed H1; các tên/sự kiện lạ ít được học; prompt có dấu cách cuối gây biến dạng phân bố token đầu; không có systematic red-team, fairness, privacy, memorization/PII extraction audit hoặc người chấm độc lập. Không kiểm chứng multilingual competency. Không định lượng bảo đảm chất lượng trường hợp xấu nhất.

## 6. Quyền, công bố và hỗ trợ tái lập

- Corpus gốc khai báo `CDLA-Sharing-1.0`. Xem [hồ sơ quyền nguồn](../data_governance/TTM_SOURCE_RIGHTS_AND_RELEASE_MATRIX_20261109.md) và [văn bản CDLA](https://cdla.dev/sharing-1-0/). Không đồng nhất dataset license với quyền phân phối **trọng số** hay **mã nguồn**.
- Repository chưa có LICENSE ở `main` tại thời điểm audit; mã nguồn **publicly visible ≠ licensed for redistribution**. Quyền code, third-party notices và quyết định license trọng số cần phê duyệt riêng.
- **Công bố được phép hiện tại:** báo cáo/mã băm/biên bản công khai; **HOLD phát hành weights/GGUF, TRAIN/VAL/TEST và merge tokenizer**, đợi review quyền sở hữu, memorization và điều khoản dữ liệu/third-party.
- [Hướng dẫn tái lập](../reproducibility/TTM_SMALL4M_T4_REPRODUCIBILITY_MANIFEST_20261109.md) chỉ cho phép source-only kiểm tra/verify checksum; full rerun khoa học cần quyền dữ liệu, checkpoint escrow, cùng runtime và permit riêng, không tự chạy lại TEST đã dùng.

**Tình trạng kết luận:** `MODEL_CARD=DOCUMENTED_SCOPED` · `SCIENCE_H1_VAL=PASS_SCOPED` · `SEMANTIC_GAIN=NOT_CONFIRMED` · `WEIGHT_RELEASE=HOLD` · `PRODUCT_READY=NO`.

**Bước thực hiện tiếp theo:** xác minh thêm quyền công bố checkpoint/merge và policy PII/memorization; làm QA tài liệu trên nhánh riêng. Không huấn luyện, không đổi `main` hoặc `lineage.md`.

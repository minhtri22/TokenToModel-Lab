# TTM Small4M T4 A2 — Adjudication of the actual TinyStories science run

**Ngày:** 2026-11-08. **Loại:** KẾT QUẢ KHOA HỌC / SCIENTIFIC EXPERIMENT (không phải kiểm thử synthetic). **Phán quyết:** `PASS_H1_CONFIRMATORY_VAL_SCOPE`. **Số seed:** 1. **RunID:** `t4_science_4m_1024_a2_20261108_v1`.

## Câu hỏi đã đăng ký trước khi nhìn kết quả

Mô hình Transformer decoder-only P02 3.749.376 tham số, vocab 2048, context 256, 4 block, 4 heads, embedding256, dùng BPE huấn luyện từ 768 truyện TRAIN; trên tập pilot TinyStories 2.048 TRAIN, 256 VAL và 64 TEST niêm phong. **H1**: NLL trung bình theo token mục tiêu ở VAL của checkpoint cuối **step1024** phải thấp hơn bigram Add-α=0.1 fit **chỉ từ TRAIN** ít nhất **5%**, đồng thời cận dưới 95% bootstrap **theo truyện** (1.000 lượt, seed 20261109) của chênh lệch tuyệt đối `bigram_nll - model_nll` phải **>0**. Không được chọn checkpoint theo VAL; TEST chưa dùng.

- Mô hình gốc P02 Git blob `9762343e06cf800b50574c2871ae1ed58537fb18` (SHA256 `e0fcac285918b66b13c8f694e6d625a0691c9b59221b43043e63f46b25ddcc07`).
- Huấn luyện thực: **1.024 optimizer steps**, **4.096 valid labels mỗi bước** = **4.194.304 target exposures**, seed `20261108`, FP16 / microbatch windows 8 / accumulation động. Không có giới hạn 55/90 phút cứng; chính sách `COLAB_FREE_RUN_UNTIL_1024_OR_PREEMPTED`, không dừng dự kiến tại 256.
- Tập TRAIN có **498.287 vị trí nhãn** trong 2.691 cửa sổ; số lượt tái sử dụng nhãn trung bình **8,417×**. VALID có 61.122 vị trí nhãn trên 256 truyện; giới hạn tránh trùng gần chỉ áp dụng cho bộ mẫu pilot đã chọn, không phải toàn corpus.
- Quyền khoa học được ghim bởi `T4_SCIENCE_LOCK_A2_1024.json` SHA256 `fd183ade2a696d40313aae19b63429d4ef3edd8abf25c899c8cc496836d36817`; bộ token TRAIN/VAL riêng tư SHA256 `184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913`; manifest SHA256 `ef2e6e67d49b1d5a921b1051df329f15574f1c10cece0ce49468acb53322d650`. **Không đưa token/npz hoặc checkpoint vào GitHub**.

## Kết quả và đối chiếu độc lập

Colab Tesla T4 hoàn thành đúng **1.024/1.024**. Bản gốc `T4_FINAL_UNADJUDICATED.json` SHA256 `5a6c0ab4da808bbe0bfaa0b6cde085277c1a8eb0735b73d24a3700e3f34f62c4`. Nhật ký 1.024 bước liên tiếp, mọi bước `exact_scored_targets=4096`; TRAIN loss bước 1 từ **7,677356** xuống **3,282975** ở bước 1.024. Báo cáo GPU `elapsed_gpu_seconds=74.2535` **chỉ là bộ đếm compute+VAL trong trainer**, không chứng minh tổng thời gian phiên/Drive.

| Thước đo, VAL 256 truyện / 61.122 targets | Colab | Tính lại từ checkpoint trên CPU |
|---|---:|---:|
| Model VAL NLL | 3.5223388569 | **3.5223388517** |
| Bigram Add-0.1 VAL NLL | 3.99723141696 | **3.99723141696** |
| Lợi thế NLL tuyệt đối | 0.47489256008 | **0.47489256527** |
| Cải thiện NLL tương đối | 11.880537% | **11.880537%** |
| 95% bootstrap story-level CI của lợi thế | [0.45818671, 0.49406155] | **[0.45818675, 0.49406158]** |

CPU dùng PyTorch 2.10.0 và chính checkpoint FP16-đã-huấn-luyện nhưng tính inference FP32. Model được nạp `strict=True`, không có optimizer step, không đọc TEST. Bigram được fit lại từ toàn bộ nhãn TRAIN đúng 1 lần (không dùng frequency oversampling khi train model). So sánh lệch Model NLL chỉ ~`5.19e-9`, lệch cận bootstrap <`3.4e-8`. **Hai điều kiện H1 đã đăng ký đều PASS rõ rệt**. Kết quả tính lại chi tiết: `evidence/pilot/t4-science/T4_H1_INDEPENDENT_CPU_RECOMPUTE.json` (SHA256 `c3b60ea5f2c1398fec2d86be1438c9e153f0702d9cbef5bbbddbf0b8f148a6de`).

### Tính toàn vẹn checkpoint và nhật ký

Checkpoint thực cùng hồ sơ READY-last được đọc lại qua Google Drive. Tất cả **4/4 checkpoint** có tệp 45.074.891 byte đúng SHA256 trong READY; toàn bộ tệp mở được qua `torch.load(weights_only=True,map_location='cpu')`, chứa model/optimizer/scheduler/sampler/Python+NumPy+PyTorch CPU/CUDA RNG/scaler. Nhật ký của mỗi checkpoint là **tiền tố hoàn toàn chính xác** của 1.024 bản ghi cuối.

| Bước | SHA256 checkpoint | SHA256 progress |
|---|---|---|
| 256 | `9d183d481e46e1dd5edc284a6998af6748c697048b4e8e59dd831c43a77401dd` | `db51e8c39b6daed8c6def36fcb3aee3380eb46d05cecaa6e243d9a4771d7bfe0` |
| 512 | `6cb2789f8e2b6fbf2fb59cb18cab07ed045ba980f6fe945fc5bbe25f61da02aa` | `b47ce4fb6f7a7113df1f51ecd3332b600cebd108bd8d7866818eebc4447b67a8` |
| 768 | `01a700ec792e87b783377d29cd715bd2566a327d173d62646a3b1f51bb10615a` | `09eab05258001d5d1641f0f890f05378eb8188565d26694e4f9bf9c2ec14aafb` |
| 1024 | `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b` | `5517cc691fc803eaa69db4078f1f3b3ed78f99fa3c012cb17fd8655123c606ec` |

Đầy đủ biên bản `evidence/pilot/t4-science/T4_A2_FINAL_INDEPENDENT_SCIENCE_ADJUDICATION.json` SHA256 `a5e76621b8dee312cd49ffe9fc6489548c3451ad4cd6baf8af3a7e0d0749219e`. Drive: https://drive.google.com/drive/folders/1GK6OtQxyq5u1ALkXKdFygFT8uvhnL5-d . Không chạy lại TRAIN.

## Phán quyết và ranh giới diễn giải

**`PASS_H1_CONFIRMATORY_VAL_SCOPE`**: trong phạm vi pilot TinyStories và đối chứng bigram đã tiền đăng ký, mô hình 3,75M học được phân bố token kế tiếp có NLL VAL thấp hơn bigram 11,88%. **Đây là kết quả khoa học thật, không còn là synthetic/demo**. Tuy nhiên không chứng minh khả năng sinh văn bản tốt với con người, không chứng minh kết quả trên held-out TEST hoặc toàn bộ TinyStories, chưa đánh giá nhiều seed, chưa kiểm thử mô hình đã train qua GGUF F32/llama.cpp/Ollama. F16 GGUF bị chặn tùy chọn không làm mất giá trị kết quả H1.

Không mở TEST trong lượt adjudication này. Khi tiếp tục, dùng **chính checkpoint step1024 đã khóa**, đánh giá TEST 64 truyện **một lần duy nhất** theo hợp đồng trước khi chuyển sang T5 xuất GGUF, và ghi cả PASS lẫn FAIL vào lineage append-only. Không đổi cấu hình H1 dựa trên TEST.

**Bước thực hiện tiếp theo:** `TTM_T4_SEALED_TEST_ONE_SHOT_AND_T5_TRAINED_GGUF_HANDOFF`. Không rerun T1–T4 hoặc TRAIN; PR #12 vẫn DRAFT, main unchanged; append một entry khoa học vào `lineage.md` khi readback receipt hoàn tất.

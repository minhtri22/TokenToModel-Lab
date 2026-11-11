# TTM-Small-4M × EmbeddingGemma 2 — A0B/A0C integrated CPU gate

**Operation:** TTM_GEMMA2_SEMANTICS_ORIGIN_A0B_COVARIANCE_MATCH_AND_A0C_NONPRETRAINED_SOURCE_LEXICAL_PROBE_INTEGRATED_CPU_GATE  
**Ngày:** 2026-11-11  
**Nhánh:** research/ttm-gemma2-token-alignment-pretraining-causality-20261111  
**Phân loại:** TECHNICAL_FEASIBILITY_ONLY; không inference, không train, không sửa L0020/L0021.  
**Một quyết định cuối duy nhất:** **T4_PILOT_2X2 = HOLD_A0C_NONPRETRAINED_AND_LEXICAL_PROBE_NOT_ADMITTED**.

## 1. Điều đã được kiểm trên nguồn private thật, không chấm NLL

Đã kiểm hash thực của file nguồn ZIP `TTM_GEMMA2_CAUSAL6_INPUT_PRIVATE_V1_20261109.zip` (SHA256 `2c6cb72f35eba72d6014f15914d6e9792cbf0bf6774d93e3ff5c53e5c6b9ba9a`), `candidate_initialization.pt` (`c9fc798d8880c7e76636258052e9885dbb086d7b462a5b6bee5cff8b582973c3`) và T4 TRAIN input pack (`184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913`). Không xem OOD256 per-doc hoặc H768/TEST; không sử dụng loss để tối ưu đối chứng.

Source có đúng 1.917 vector donor có khả năng mapping trong tổng 2.048 token TTM, chiều input embedding 512, Ridge projection 256, rank(P)=256. Theo mã frozen `ttm_embeddinggemma2_swap.py`, đây là donor **input token embedding** của `google/embeddinggemma-2`, không phải contextual output 768d. Cùng mã ghi historical source revision `f9972ac22e696a105c482202646979e33e4b5a1e`, donor safetensors SHA256 `197a32965d4b1105faf060417baa899e193fb73cd401f42ec9295234d5553d79`, donor config SHA256 `b8f1e9931b57fbc054acdb445c41765d55b0074c58d145fa82839941ad1b5bb3`, donor tokenizer SHA256 `4d777ef5bdc1aa36227abdfb77c3e49e7b9c892d16e1b6bda41c393504828be4`. Có chứng cứ nguồn donor **đã tiền huấn luyện** trong lịch sử, chưa có actual non-pretrained counterpart.

## 2. A0B — thay hoán vị thô bằng ràng buộc đồng thời moment và row norm

Lượt đầu dùng random residual derangement trong 16 strata theo TRAIN frequency/norm, giữ `X_i Pᵀ` và norm từng token, nhưng covariance relative Fro drift **0,48401038**; thất bại cổng đối sánh. CPU test thêm hoán vị tối ưu theo khoảng cách projection trong cùng 16 strata cải thiện drift xuống **0,34406972**, vẫn chưa đạt.

**Phương pháp A0B mới:** Tách `X=A+R`, với `A` thuộc rowspace(P) và `R` thuộc nullspace(P). Xây ma trận B là cơ sở của span bao gồm 1, projection coordinates, `log1p(freq TRAIN)`, bình phương và quartile dummies theo frequency/norm. Đặt `H=BᵀR`, `W=R-BH`, `G=WᵀW`. Tìm `R'=BH+W'` theo một phép ngẫu nhiên seed khóa `2026111142`, với `BᵀW'=0`, `W'ᵀW'=G` và `||R'_i||=||R_i||` cho từng token. Lặp luân phiên ràng buộc row norm và Stiefel/Gram tới hội tụ trên **đầu vào hình học + frequency TRAIN-only**, không chạm bất kỳ science loss nào.

Điều này giữ `XPᵀ`, row norms, mean, covariance toàn cục, và cross-moments với frequency/train covariates; đồng thời randomized token residual pairwise neighborhood. **Không bảo toàn local semantic topology** là can thiệp chủ đích, không phải thiếu kiểm toán. Không có bảo đảm giữ được morphology/semantic labels: hai điều này cần A0C.

**Đo bằng Python CPU độc lập trên chính 1.917 donor private vectors:**

| Đại lượng | Giá trị |
|---|---:|
| Max projected-input deviation FP64 | 2.220446049250313e-16 |
| Max per-token norm deviation FP64 | 4.440892098500626e-16 |
| Max projected-input deviation FP32 | 1.1920928955078125e-7 |
| Max per-token norm deviation FP32 | 1.1920928955078125e-7 |
| Global covariance relative Fro drift | **2.6087363779834547e-15** |
| Global mean relative L2 drift | 1.9099629417728523e-15 |
| Mean residual cosine/angular change (1−cos) | 0.7665599696536823 |
| Residual top-10 nearest-neighbor overlap | **0.034220135628586335** |
| Portion with residual angular change (1−cos) > 0.3 | 100% |

**Phán quyết:** `A0B_MATHEMATICAL_FEASIBILITY=PASS_SCOPED`. Đã vượt cổng kỹ thuật target covariance ≤0,05 nhưng chỉ chứng minh tính khả thi toán học; **không gọi đây là chứng minh pretrained semantics**. Phép hoán đổi residual không phải thuần random permutation nữa mà là conditioned nullspace randomization; A1 arm cần sửa tên thành `P-C (constrained residual null)` và `N-C` theo nguồn tương ứng. Khóa seed/recipe trước khi chấm NLL mới.

Mã công khai: `tools/embeddinggemma2_swap/semantics_origin_a0/ttm_a0b_constrained_moment_residual_cpu.py`. GitHub Actions run `42954626798`: **SUCCESS** Python syntax + synthetic positive and negative math fixtures. Phép audit private thực hiện bằng một triển khai Python CPU tương đương độc lập (đã chạy tới 150 iteration kiểm hội tụ, với sai số ổn định sau khoảng 20–40), **không phải xác nhận đã chạy chính xác file GitHub mới trên private source trong Colab/Windows**. Do đó cần source-integrated private readback trước khi mở A1. Không public vector/token ID/private data.

## 3. A0C — nguồn non-pretrained và khả năng lexical probe

### 3.1. Provenance nguồn

Tài liệu chính thức Google và cấu hình Hugging Face xác nhận EmbeddingGemma 2 có 24 text layers, input hidden size 512, vocab 262.144, pooled contextual embedding output 768. Xem `https://ai.google.dev/gemma/docs/embeddinggemma/model_card_2`, `https://huggingface.co/google/embeddinggemma-2/blob/main/config.json` và `https://huggingface.co/docs/transformers/model_doc/embedding_gemma2`. Kiến trúc/config cho phép **tạo** một khởi tạo non-pretrained cùng kiến trúc với seed và phiên bản thư viện pin; nhưng kiểm tra này CHƯA tạo tensor theo đúng config gốc và CHƯA khóa SHA của counterpart đó.

Không tìm thấy/bằng chứng hiện có chưa cung cấp một actual **same-architecture untrained checkpoint SHA** với mapping donor-tokenizer, Ridge fitting và matched source geometry tương đương pretrained. **Không được lấy synthetic Gaussian 1917×512 và tự gọi đó là full-model untrained EmbeddingGemma 2**. Kết luận `A0C_NONPRETRAINED_SOURCE=HOLD_NOT_ADMITTED`.

### 3.2. Độ phủ lexical/semantic probe

Từ private candidate metadata và T4 TRAIN input counts:

| Hạng mục | Kết quả audit |
|---|---:|
| 2.048 token TTM | 2.048 |
| Valid UTF-8 mapped donor | 1.917 |
| Fragment UTF-8 không đầy đủ | 130 |
| EOS/fallback special | 1 |
| Mapped bằng 1 donor-token ID | 1.867 |
| Mapped bằng nhiều donor-token IDs | 50 |
| Token mapped từng xuất hiện trong T4 TRAIN input | 1.822 |
| Mapped TRAIN frequency ≥10 | **1.718** |
| Mapped TRAIN frequency ≥50 | 1.309 |
| Mapped TRAIN frequency ≥100 | 790 |
| Whole-word lexical anchors có bản ghi và xác minh độc lập | **CHƯA ĐƯỢC THIẾT LẬP** |
| Cặp semantic relatedness/synonyms đã được xác minh | **0 cặp được chấp nhận** |
| Lexical semantic probe và random-label control thực thi | **NOT_EXECUTED** |

**Quan trọng:** `1718` chỉ là trần số token nếu lọc tần suất TRAIN≥10. Nó không đồng nghĩa 1718 token là từ hoàn chỉnh, có nhãn semantic hay thuộc một bộ đánh giá độc lập. Candidate source ZIP có `mapping_counts` nhưng không chứa nguyên T1 manifest `tokens`; manifest SHA từ nguồn gốc là `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc`. Không đoán token strings hoặc mượn OOD256 làm semantic labels.

Điều kiện admission A0C là đọc exact T1 manifest bytes, lọc whole-word boundaries/UTF-8/special, gán nhãn synonym/relatedness **không rút ra từ model loss hoặc tập TEST đã tiêu thụ**, dùng frequency/length/shape negative controls và random-label probe. Nếu thiếu anchors, `HOLD_LEXICAL_PROBE` thay vì PASS giả.

## 4. Một quyết định duy nhất cho T4

**T4_PILOT_2X2 = HOLD_A0C_NONPRETRAINED_AND_LEXICAL_PROBE_NOT_ADMITTED.**

Lý do: A0B đã giải quyết rào cản covariance/row-norm về mặt toán học, nhưng H-B `PRETRAINED-ORIGIN` chưa có tensor đối chứng chưa tiền huấn luyện thực sự được admit và semantic probe chưa chứng minh tồn tại tập anchor đáng tin. Chạy T4 2×2 lúc này có nguy cơ chỉ tái đo tác dụng hình học hoặc nguồn phân phối khác mà không trả lời câu hỏi gốc. Đây **không phải khoa học FAIL**, không ghi `lineage.md`, không cần các micro-permit kỹ thuật.

Nếu A0C đạt trong lượt CPU kế tiếp, pilot 2×2 dự kiến `P-A/P-C/N-A/N-C` × 3 seed × 512 steps × 4.096 labels = **25.165.824 token-target presentations** trên Colab T4, lưu Drive, TRAIN-only, fresh DEV/TEST. Cần đóng băng exact source, SHA, independent QA và đăng ký nghiên cứu trước khi chạy; không được dùng OOD256/H768 cũ làm confirmatory dataset mới.

## 5. Quy tắc đóng nghiên cứu trước

- `L0020`: không thay đổi, `PASS_SCOPED_DONOR_RESIDUAL_STRUCTURE`.
- `L0021`: không thay đổi, `PASS_SCOPED_OOD_RESIDUAL_TRANSPORT`.
- `OOD256`: CLAIM đã tiêu thụ; không re-score, không thay corpus/selection/threshold.
- `lineage.md`: kỹ thuật A0B/A0C không phát sinh PASS/FAIL khoa học nên **giữ nguyên**; không mở L0022.
- `main` và science branch cũ: không merge, không sửa.
- `TRAINING=0`, `MODEL_FORWARD=0`, `GPU=0`, `NEW_SCIENTIFIC_CLAIM=NONE`, `NO_PRIVATE_DATA_PUBLISHED`.

**Bước thực hiện tiếp theo:** `TTM_GEMMA2_SEMANTICS_ORIGIN_A0C_T1_LEXICAL_MANIFEST_AND_SEEDED_SAME_ARCH_UNTRAINED_SOURCE_CPU_ADMISSION`. Một lượt CPU chỉ nhằm nạp exact T1 manifest/private donor tokenizer (không TRAIN/VAL/TEST), dựng một source initialized từ config gốc với seed và SHA rõ ràng, kiểm token mapping và lexical label/control coverage, cùng integrated independent QA. Chỉ nếu PASS mới trình một quyết định T4; không tự động dispatch.

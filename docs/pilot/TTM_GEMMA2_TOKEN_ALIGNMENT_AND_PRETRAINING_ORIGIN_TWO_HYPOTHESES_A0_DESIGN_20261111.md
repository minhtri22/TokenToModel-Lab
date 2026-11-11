# TTM-Small-4M × EmbeddingGemma 2 — hai giả thuyết độc lập

**Operation:** TTM_GEMMA2_TOKEN_ALIGNMENT_AND_PRETRAINING_ORIGIN_TWO_HYPOTHESES_A0  
**Ngày:** 2026-11-11  
**Trạng thái:** DESIGN_ONLY · A0_CPU_PARTIAL_PASS · SEMANTIC_IDENTIFICATION_HOLD  
**Nhánh:** research/ttm-gemma2-token-alignment-pretraining-causality-20261111  
**Gốc:** OOD256 closure HEAD d4550cb9c88103ccfb4ce0b3683c13f4136e4bd1.

## 1. Câu hỏi khoa học

L0020 và L0021 đã PASS có phạm vi: donor residual structure có tín hiệu trên H768 cùng miền và OOD256 WikiText-2 khác miền. Chúng KHÔNG cô lập lợi ích thuần từ semantic pretraining.

Donor đang dùng là trọng số INPUT token embedding 512 chiều (tok.source.weight) từ EmbeddingGemma 2, được ánh xạ sang 1.917 token hợp lệ của TTM vocab 2.048. Đây KHÔNG phải contextual sentence embedding 768 chiều ở đầu ra của EmbeddingGemma 2. Các tín hiệu trong đầu vào có thể do morphology, token frequency, row norm, projection geometry, training dynamics hoặc semantic pretrained structure.

### H-A — Token–residual assignment

Hỏi: Liên kết đúng token ID với donor residual có cải thiện next-token NLL trên heldout MỚI so với liên kết hoán vị đã đối sánh, trong khi giữ nguyên projected input và per-token norm và kiểm covariance/topology?

Estimand: D_align = NLL(P-shuffled)-NLL(P-aligned). PASS chỉ diễn giải được là token-specific residual information under audited geometry, không phải pretrained semantic causality.

### H-B — Pretraining-origin advantage

Hỏi: Lợi ích liên kết token đó có lớn hơn khi nguồn donor thật sự PRETRAINED, so với nguồn NON-PRETRAINED cùng kiến trúc/tokenizer và hình học được kiểm soát?

Estimand: D_pretrain = [NLL(P-shuffled)-NLL(P-aligned)] - [NLL(N-shuffled)-NLL(N-aligned)]. Dương là sự gia tăng tương đối gắn với pretrained origin, không tự chứng minh pure semantics nếu vẫn tồn tại morphology/frequency/geometry hoặc training data overlap.

Cần thêm semantic lexical probe độc lập với control labels, nếu không H-B chỉ có thể được gọi là PRETRAINING-ASSOCIATED TOKEN-SPECIFIC EFFECT, không phải causal pure semantics.

## 2. Rà soát thực tế A0, đọc donor thật chỉ bằng CPU

Nguồn pin: TTM_GEMMA2_CAUSAL6_INPUT_PRIVATE_V1_20261109.zip SHA256 2c6cb72f35eba72d6014f15914d6e9792cbf0bf6774d93e3ff5c53e5c6b9ba9a; candidate_initialization.pt SHA256 c9fc798d8880c7e76636258052e9885dbb086d7b462a5b6bee5cff8b582973c3. Không đọc OOD256 loss/holdout hoặc gọi LM.

X shape (1917,512), P shape (256,512), rank(P)=256, residual nullspace dim=256. Dựng X_parallel từ orthonormal rowspace(P); R=X-X_parallel sao cho R Pᵀ≈0. Sau đó trong 16 nhóm cố định theo tần suất token TRAIN-only × residual-norm (4×4 phân vị), hoán vị π không có điểm cố định:

X_mix,i = X_parallel,i + ||R_i|| × R_{π(i)}/||R_{π(i)}||.

Các phép đo CPU độc lập trên 1.917 vector thật, seed 2026111137:

| Thuộc tính | Giá trị |
|---|---:|
| Mapped tokens được hoán vị | 1917/1917 |
| Strata | 16 (nhóm nhỏ nhất 83, lớn nhất 180) |
| Max projected-input drift | 2.2638141361497333e-16 |
| Max per-token L2 norm drift | 3.3306690738754696e-16 |
| Mean-relative L2 drift | 0.0070256652939474145 |
| **Global covariance relative Fro drift** | **0.48401038004373853 (48,40%)** |
| Mean residual angular/cosine change | 0.9684996960115265 |

**Diễn giải:** PASS toán học với projected input và norm từng token; COVARIANCE chưa được đối sánh (drift 48,4%), lexical token class và local topology chưa kiểm. Bởi vậy KHÔNG được quy bất cứ chênh NLL tương lai nào từ đối chứng thô này thành ngữ nghĩa. A0 verdict: PARTIAL_A0_MATH_PASS_SEMANTIC_ISOLATION_HOLD, không phải science FAIL.

Mã nguồn CPU: tools/embeddinggemma2_swap/semantics_origin_a0/ttm_semantics_origin_a0_cpu_geometry.py. GitHub Actions 42949232448: Python 3.12 syntax + 8 synthetic/negative fixtures PASS, không dùng private bytes. Đo donor thật thực hiện bằng Python CPU audit riêng độc lập; công bố chỉ các thống kê tổng hợp trong artifacts/qa/ttm-embeddinggemma2/TTM_GEMMA2_SEMANTICS_ORIGIN_A0_REAL_DONOR_GEOMETRY_AUDIT_20261111.json.

## 3. Thiết kế 2 × 2 và đối chứng bổ sung

| Arm mới | Donor | Token–residual association | Vai trò |
|---|---|---|---|
| P-A | Pretrained EmbeddingGemma 2 (pinned) | Aligned | Baseline đúng token |
| P-S | Cùng pretrained | Matched residual shuffle | H-A, giữ projected input, norm; covariance/topology phải đạt gate |
| N-A | Same-architecture NON-PRETRAINED (nếu admit) | Aligned | H-B, nguồn chưa tiền huấn luyện |
| N-S | Cùng non-pretrained | Matched residual shuffle | Difference-in-differences H-B |
| G-R | Pretrained, rotated within null(P) | Giữ pairwise residual Gram; thay basis | Kiểm basis sensitivity; không xóa semantic topology |
| G-N | Synthetic geometry-matched random | Không có token–semantic correspondence | Negative control, KHÔNG tự nhận là same-architecture untrained |

Không dùng whole-vector PT-PERM đã tiêu thụ như một thí nghiệm mới; phép đó phá projected input. Mọi đối chứng phải dùng TTM checkpoint khởi tạo frozen giống nhau, T1 tokenizer, TRAIN-only fitting, các seed/schedule, optimizer và target-token budget bằng nhau. Giữ 131 fallback/special IDs không đổi.

Nếu không tìm được non-pretrained source có provenance hợp lệ thì H-B = HOLD_NONPRETRAINED_SOURCE, dù H-A có PASS.

## 4. Ba cổng bắt buộc trước T4, không micro-permit

**A0B — Geometry matching bằng CPU:** Tối ưu lại constrained assignment hoặc optimal transport từ X và TRAIN-only features, tuyệt đối không nhìn NLL để điều chỉnh. Đề xuất tiêu chuẩn thiết kế cho lần mới (CHƯA phải pre-reg khoa học): relative global covariance Fro ≤0,05; max per-row projection và norm drift ≤1e-5; báo cáo mean, spectrum, pairwise local neighbor overlap, angular change và mapping coverage. Nếu không khả thi, HOLD_IDENTIFICATION và không chạy pilot. Không thể đồng thời giữ full Gram cùng token mapping mà xóa mọi relative semantic neighborhood, nên không được tuyên bố pure semantic isolation tuyệt đối.

**A0C — Provenance và semantic independent probes:** Pin donor model.safetensors, config/tokenizer exact SHA và kiểm điểm gốc embedding input 512d. Tìm non-pretrained initialization cùng kiến trúc/tokenizer, seed và chính xác luật khởi tạo; nếu chỉ tạo random surrogate thì ghi SYNTHETIC_NOT_ACTUAL_UNTRAINED, kiểm mean/norm/cov/matching. Lấy T1 token strings từ manifest pinned; chỉ dùng lexical whole-word anchors có chứng cứ, không lấy BPE fragments/EOS hoặc nhãn từ OOD. Phân nhóm dựa trên length/case/byte shape/frequency và thực hiện semantic relatedness/synonym probe với control-label randomization. Probe dùng nhãn lexical độc lập, thẩm định quyền và độ phủ trước NLL. Bài nghiên cứu Hewitt & Liang (2019) về control tasks hỗ trợ yêu cầu kiểm selectivity; probe PASS cũng không đủ để chứng minh tác động lên NLL. Link: https://aclanthology.org/D19-1275/.

**A1 — Pilot T4 khi A0B/C PASS:** dự kiến 4 arm P-A/P-S/N-A/N-S × 3 seeds × 512 steps × 4096 target/step = 25.165.824 target-token presentations; Colab T4 + Google Drive. Đây là phạm vi feasibility; không có permit science/training trong lượt này. Nếu chỉ đủ P-A/P-S thì H-A là nghiên cứu riêng và H-B vẫn HOLD.

**A2 — Confirmatory:** chỉ khi thiết kế/đối chứng đạt, khóa nguồn mới TRAIN/DEV/TEST không tái dùng H768 và OOD256. Trước khi CLAIM mới phải đóng băng contrast sign, CI, bootstrap unit, replication seeds, source SHA, cross-domain leakage và admissibility. OOD256 là PRIOR EVIDENCE, không phải confirmatory test thứ hai.

## 5. Quản trị kết luận

- L0020 và L0021 cùng PASS cũ, bất biến; OOD256 closure pinned SHA manifest, không re-score.
- A0 kỹ thuật: MATH_PASS · COVARIANCE_GEOMETRY_HOLD · LEXICAL_NOT_CHECKED · NONPRETRAINED_NOT_ADMITTED.
- H-A và H-B: NEW_DESIGN_ONLY, không có kết quả khoa học; không thêm dòng PASS/FAIL mới trong lineage.md.
- TRAINING=0, INFERENCE=0, GPU=0, NEW_CLAIM=NONE, GGUF/APP=NOT_OPENED.
- Không merge vào main, không thay science source branch. Không công khai donor rows, private membership, raw text hoặc loss.

**Bước thực hiện tiếp theo:** TTM_GEMMA2_SEMANTICS_ORIGIN_A0B_COVARIANCE_MATCH_AND_A0C_NONPRETRAINED_SOURCE_LEXICAL_PROBE_INTEGRATED_CPU_GATE. Thực hiện một lượt integrated CPU/source QA A0B+A0C rồi quyết định duy nhất về pilot T4; không cấp phép lại từng kiểm thử kỹ thuật nhỏ.

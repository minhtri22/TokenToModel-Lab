# TTM-Small-4M × EmbeddingGemma 2 — Đóng băng sau phân xử SEMANTIC4X3 / rà soát đóng nhánh

**Ngày rà soát:** 11/11/2026  
**Operation:** `TTM_SEMANTIC4X3_POST_ADJUDICATION_FREEZE_AND_BRANCH_CLOSURE_REVIEW`  
**Quyết định:** `SCIENTIFIC_WORKSTREAM=CLOSED_PASS_SCOPED` · `GIT_BRANCH=PRESERVED_NOT_MERGED` · `NEXT_PRIORITY=OOD_SOURCE_PREREG_DESIGN_ONLY`.

## 1. Kết luận khoa học bất biến

- Phán quyết đã ghi tại **L0020**: `PASS_SCOPED_DONOR_RESIDUAL_STRUCTURE` theo **hai co-primary tiền đăng ký** và frozen independent QA `PASS_INDEPENDENT_12_ARM_STORY_BOOTSTRAP_READBACK`.
- Một **StudyID** `ttm_gemma2_semantic4x3_3seed_2048x4096_h768_20261110_v2`, 3 seed × 4 arm × 2.048 updates = **24.576 steps**, 4.096 next-token labels/update; nguồn donor EmbeddingGemma 2, TTM bước 1.024, 12 checkpoint cuối và 96 READY. H768 mới: **768 truyện, 1.000 cửa sổ, 186.655 nhãn**.
- `tau_residual=+0.0110025124`, paired-story bootstrap CI95 `[+0.0080061404,+0.0142235373]`; `gamma_real=+0.0046110883`, CI95 `[+0.0026581795,+0.0067166239]`. Cả ba seed dương với hai co-primary; S3 có `tau_residual=+0.0000483432` (**gần như 0**). Bootstrap 2.000 mẫu theo **truyện**, CI có điều kiện trên đúng ba seed.
- QA độc lập có **96 READY**, đối chiếu chính xác SHA-256 của 12 binary checkpoint cuối (bên cạnh thẩm định scoped tải/băm trước đó), `model_forward_calls=0`, `science_training_reexecuted=false`.
- Đây là bằng chứng **cấu trúc hữu ích trong phần dư donor ngoài embedding Ridge tại bước0**, không chứng minh riêng ngữ nghĩa tiền huấn luyện. Mức row norm/higher-order moments của null chưa khớp hoàn toàn; chưa biết donor pretraining overlap hoặc khái quát OOD.
- **Không thêm L0021:** biên bản này chỉ đóng băng một kết quả khoa học đã PASS, không tạo kết quả thí nghiệm mới. `lineage.md` tại Git blob `3bd60e32e28cc358740953df5bd0ad180862a9fc`, đúng một L0019 và L0020, giữ nguyên L0017/L0018.

## 2. Chuỗi SHA và vị trí chứng cứ

| Tài liệu nguồn công khai | Git blob SHA-1 |
|---|---|
| L0017–L0020 trong `lineage.md` | `3bd60e32e28cc358740953df5bd0ad180862a9fc` |
| Tiền đăng ký V2 | `d2627ad9086c9a34a8bf99af7b44ef529cb1861c` |
| Bản sửa resume trước CLAIM | `3eac8d5346fe60182298294a033fc258953c167c` |
| Báo cáo phân xử L0020 | `fb62de5ac869dee311b47aca6017cd6ee6167ef6` |
| JSON phán quyết L0020 | `23ec04b6fecb014e75066610a0807b92463d56a5` |
| Đọc lại độc lập 96 READY | `8f9ca359e33304bef299472603f52c522009c0d9` |
| `RESULT_PUBLIC` | `5db0da79bf2de5bdce0e7e1853edb82d069d8c08` |
| `STUDY_CLAIM_PUBLIC` | `7056c17ba6d357e2c34799dedf58f64d0b3afa1c` |
| Frozen runner science | `4e1fecc1f83c0ec5ba0566201f1114703e9f81c8` |
| Frozen independent checker | `df3781940e51bbe6caa23fd974f88847561b35e6` |

SHA-256 dữ liệu khoa học niêm phong:
- Runner Python `a3182549739cda848ce0f7f449b1f1455e06419d72295dcee96f0e8a7822f676`.
- CLAIM `5c76c4da3d1d1c0532f04a7ff557fd0f8e46279e7e1590dd34cf7801368b47a2`; RESULT `d60f8e206b20b30a5b83f324427fa0b206a9d00174661419abf2185401022610`; independent readback `386ec3bdab72cecc31455998951cc2afbb51bd7e3d9023cbc65027d5dd80a513`.
- H768 membership `0ab671ae59ff4300d8257f2689261d6328afd7563c0aa66b363bc22348c1628f`, private per-story `e51f9b840cd6d9b324257efdda56b781663d488cf47cfc92ced4101de93ebcf2`.

Số liệu hoàn chỉnh, 12 NLL và digest từng checkpoint giữ trong hai JSON phán quyết/đọc lại đã pin. Checkpoint binary, optimizer/RNG, dữ liệu H768 và loss theo truyện ở Google Drive riêng tư: **không chuyển vào GitHub và không xóa**. Không đọc lại H768, tính bootstrap, chạy checker, inference hay GPU trong lượt đóng băng.

## 3. Kết luận về đóng nhánh Git

- Nhánh `research/ttm-small4m-embeddinggemma2-token-swap-minimal-proof-20261109` HEAD trước review `5b27d797f255d0253de0e4818fe0ebf9549d9ee7`; `main` tại `5d52e32f20021e36f08f284ef9864d3ba36dbead`.
- GitHub compare cho `status=diverged`: **71 commit ahead**, **160 commit behind**, **132 file khác biệt**; merge-base `a167d41ff9ad46eb82d2137e796c2249bfa89fc8`. Không có pull request từ nhánh này tại thời điểm kiểm tra.
- **Đóng phần khoa học, không đóng/xóa nhánh Git:** KEEP branch immutable as evidence reference, không tự merge/rebase/cherry-pick. Mặc dù code và report có QA, compare `main` còn chứa nhiều thay đổi ngoài SEMANTIC4X3, nên cần sau này làm **một PR tích hợp tuyển chọn** với kiểm tra nguồn, tài liệu, phạm vi thay đổi, conflict và QA độc lập. Không giả định có thể fast-forward.
- `semantic4x3_v2/README_VI.md` vẫn ghi trạng thái pre-CLAIM và “chưa có training runner” từ giai đoạn thiết kế. Đó là **metadata tài liệu lỗi thời**; biên bản đóng băng này và L0020 là nguồn trạng thái sau science. Không sửa README trong lượt freeze để tránh thay đổi nguồn lịch sử.
- Nhánh còn chứa notebook, ZIP nguồn và các tài liệu từ giai đoạn trước. Chưa kiểm toán toàn bộ nội dung 132 file về quyền dữ liệu/secret hoặc giải quyết conflict; vì thế **không** tuyên bố `INTEGRATION_QA=PASS`.

**Branch closure verdict:** `SCIENTIFIC_CLOSED`; `GIT_MERGE_HOLD_DIVERGED`; `BRANCH_PRESERVED`; `MAIN_UNCHANGED`.

## 4. So sánh và ưu tiên bước nghiên cứu tiếp theo

| Tiêu chí | **A. OOD: kiểm định ngoài miền** | B. Tách thêm ngữ nghĩa donor |
|---|---|---|
| Câu hỏi có thể bác bỏ | Lợi thế residual donor có còn trên **miền văn bản khác TinyStories**? | Lợi thế có còn khi loại khác biệt row norm/higher moments/token morphology? |
| Lỗ hổng trực tiếp | L0017–L0020 đều cùng họ dữ liệu; khả năng chuyển miền chưa kiểm | Null giữ projection/covariance nhưng chưa triệt tiêu hoàn toàn yếu tố không ngữ nghĩa |
| Tái sử dụng | Có thể **dùng lại 12 checkpoint cuối**; **không cần train lại**, chỉ dự kiến scoring sau một approval mới | Có thể phải sinh null chặt hơn, thiết kế lại 4×3, cần GPU train nếu muốn hậu nghiệm NLL |
| Độ khó/chi phí tiếp theo | **Thấp hơn cho thiết kế nguồn**; inference chỉ khi xin quyết định science mới | **Cao hơn**, phụ thuộc kiểm định hình học và causal identification |
| Mức diễn giải | Kiểm tra **độ bền ngoài miền**, không chứng minh ngữ nghĩa | Tăng độ tin cậy cơ chế, nhưng khó chứng minh semantics hoàn toàn |

**Đề xuất ưu tiên A trước B:** kiểm tra khả năng khái quát (transport/robustness) là giới hạn khoa học lớn nhất còn trống trên một kết quả in-domain PASS. Một OOD evaluation âm hợp lệ vẫn rất có ích: cho biết giới hạn ứng dụng/kết luận, **không hồi tố làm L0020 thành FAIL**. Một OOD dương chưa chứng minh semantic isolation: đó là câu hỏi của B.

### A — Phạm vi bước tiếp theo duy nhất: thiết kế nguồn OOD, không chấm

1. Xác định **tối đa một tập OOD chính** thuộc thể loại *English factual/expository prose* ngoài TinyStories, nguồn được phép sử dụng, phiên bản dữ liệu và giấy phép đã pin. **Chưa chọn corpus** trong lượt này.
2. Thiết kế loại trừ theo SHA của TRAIN/VAL/TEST/H320/H512/H768 và kiểm tra near-duplicate trên dữ liệu được phép; kiểm tra miền, độ dài câu/từ, Unicode, BPE OOV/fragment, số token hợp lệ, story weighting và việc liệu độ khó ngôn ngữ quá khác có tạo ceiling/floor NLL. Không được mở lại holdout đã tiêu thụ để điều chỉnh thiết kế.
3. Khóa cùng tokenizer, context 256, một danh sách 12 checkpoint cuối, metric answer-only token-weighted NLL; lập contrast `tau_residual` và `gamma_real` theo cùng dấu, paired document bootstrap và tiêu chí stop/hold/pass/fail **trước khi scorer chấm**. Với dữ liệu miền khác, đơn vị bootstrap là tài liệu, phải khóa quy tắc độ dài/ngắt đoạn.
4. Xác minh nguồn, quyền, nhiễm bẩn donor pretraining ở mức có thể; nếu không thể chứng minh độc lập hoàn toàn thì ghi giới hạn. Kiểm nguồn bằng CPU không suy ra `OOD_SCIENCE_PASS` hoặc tự cấp GPU.
5. Chỉ sau hợp đồng tiền đăng ký riêng và phê duyệt của owner mới được chạy **inference-only** trên 12 checkpoint frozen; **không huấn luyện lại** hoặc chọn checkpoint theo OOD.

**OOD admission HOLD** nếu nguồn không có license/consent rõ ràng, không có đủ tài liệu không trùng, tokenizer quá kém tương thích, hoặc không thể bảo đảm đóng băng holdout mà không nhìn NLL. Không tự chọn lại sau khi biết kết quả; không thay L0020.

### B — Backlog nghiên cứu cơ chế, chưa mở thực thi

Đối chứng mới có thể cần (i) row-norm-matched donor null, (ii) token-neighborhood/morphology/frequency matched controls, (iii) nhiều seed/null realization hoặc donor khác, (iv) đánh giá overlap pretrain, và (v) thiết kế pretraining-level ablation nếu muốn trả lời đúng câu hỏi semantics. Tất cả yêu cầu **đăng ký trước** và quyền dữ liệu; không dùng kết quả S3 gần 0 để chọn seed hậu nghiệm.

## 5. Phán quyết quản trị cuối

`L0020=FROZEN` · `SCIENTIFIC_WORKSTREAM=CLOSED_PASS_SCOPED` · `GIT_BRANCH=PRESERVED` · `GIT_INTEGRATION=HOLD_DIVERGED_71AHEAD_160BEHIND` · `PR=NONE` · `NEXT_RESEARCH=OOD_SOURCE_AND_PREREG_DESIGN_ONLY` · `SEMANTIC_ISOLATION=SECOND_PRIORITY_BACKLOG` · `NO_GPU` · `NO_INFERENCE` · `NO_GGUF`.

**Bước thực hiện tiếp theo:** `TTM_GEMMA2_OOD_CORPUS_SOURCE_RIGHTS_TOKENIZER_FEASIBILITY_AND_PREREG_DESIGN_ONLY`. Chỉ chuyển sang một nhánh/lượt nghiên cứu mới sau khi chủ dự án phê duyệt phương án; không sửa hoặc chạy lại StudyID đã hoàn tất.

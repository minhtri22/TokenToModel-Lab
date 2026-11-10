# SEMANTIC4X3 — Bản sửa đổi kỹ thuật trước CLAIM: chạy khoa học 12 arm có resume

Ngày: 2026-11-10. Nguồn khoa học: hợp đồng SEMANTIC4X3 V2 đã tiền đăng ký, H768 đã niêm phong; `L0019` giữ nguyên. Chủ dự án đã đồng ý chạy **12 arm × 2048 bước = 24.576 optimizer steps** trên **Google Colab Free Tesla T4** trong cuộc trò chuyện ngày 2026-11-10 và yêu cầu cơ chế phục hồi.

**Phạm vi sửa đổi:** chỉ thay đổi checkpoint journal, tiếp tục cùng StudyID từ trạng thái đã xác minh, và cơ chế chấm H768 có biên bản từng arm. Không thay 4 arm, 3 model/null/permutation/schedule seeds, donor, checkpoint gốc, tokenizer, H768, train window schedule, optimizer, batch/micro, 2.048 bước/arm, FP32, thống kê bootstrap hay điều kiện PASS/FAIL. Không thêm nhánh; không thay thuật toán gradient hay xấp xỉ loss. Không claim science từ CPU fixture.

## Chuỗi thực thi / resume

1. Trước CLAIM: nguồn runner amended, null helper, reviewer, SHA-256 private 7+3, T4 free quota/VRAM, C2048 source parity và 3 schedules phải PASS. Bản `SOURCE_SHA256` mới thay source SHA của runner cho lượt science **trước** CLAIM. H768 không chấm trong preflight.
2. Execute tạo một `STUDY_CLAIM.json` độc quyền cho StudyID gốc `ttm_gemma2_semantic4x3_3seed_2048x4096_h768_20261110_v2`; 3 CLAIM seed là metadata của cùng thí nghiệm. Mỗi arm chạy **tuần tự trên cùng T4**, không chạy các arm trên hai Colab session song song.
3. Ghi checkpoint model + AdamW + CPU/CUDA RNG + lịch/sampler cursor + losses **sau mỗi 256 bước**; `READY.json` và `CHUNK_XXXX_DONE.json` gắn SHA-256. Mọi checkpoint READY trước đó chỉ được đọc, không ghi đè.
4. Nếu Colab ngắt giữa chunk chưa có READY, khi người dùng gọi `--mode resume --manual-resume-adjudicated` trong cùng StudyID, runner kiểm xác thực CLAIM, nguồn, GPU/runtime, 3 schedules, `READY` trước đó và checksum optimizer/model. Giữ nguyên START cũ và tạo biên bản `REPLAY_<n>_START`; chỉ chạy lại những update chưa có READY từ RNG/sampler **của READY cuối**. Đây là **tiếp tục cùng khoa học**, không mở một seed, run hay hypothesis mới; số update trong chuỗi hợp lệ vẫn là 2048/arm. Không xóa log START cũ.
5. Nếu checkpoint bytes đã viết nhưng READY chưa có, hoặc metadata/SHA không khớp: **HOLD_FOR_MANUAL_RECOVERY**, không tự xóa/quarantine binary hay tự tuyên bố PASS. Nếu nguồn/hardware library khác với CLAIM: HOLD, không tự đổi môi trường để resume.
6. Chỉ sau **12 READY bước 2048** hợp lệ, mới đọc và chấm H768. Mỗi arm sau khi chấm có `scoring/<seed>/<arm>_PER_STORY_PRIVATE.json` ràng SHA checkpoint. Khi score bị ngắt, các arm đã chấm có receipt được **tái sử dụng**, không chấm lại; arm bị ngắt trước receipt có `RETRY` log khi được chấm lại. Nếu receipt không khớp: HOLD. Xuất `PER_STORY_PRIVATE.json` và `RESULT.json` một lần; chờ independent adjudication trước L0020.
7. `--max-chunks-per-invocation=N` là tùy chọn **dừng tại READY sau N chunk bền vững**, không phải early stopping hay rút ngắn ngân sách. Mặc định `0` chạy liên tục; có thể dùng 2/4 cho phiên ngắn. Resume cùng CLAIM sau dấu `SEMANTIC4X3_PAUSED_AT_DURABLE_READY=YES`.

## Song song / đa luồng

Một Tesla T4 chỉ có một GPU. **Không chạy nhiều arm concurrently** (hai mô hình cùng T4 cạnh tranh VRAM và băng thông, tạo rủi ro OOM). Các phép nhân ma trận/cuDNN trên GPU đã chạy song song nội bộ; null SVD/QA giới hạn BLAS **2 CPU threads**, nhưng không thay thuật toán gradient. Không được dùng multi-GPU trả phí hoặc đổi mixed precision/gradient accumulation để tăng tốc mà không amendment mới.

## Nguồn và quyền

- Đầu vào private giữ nguyên trên Drive: ZIP CAUSAL6 20261109 và ZIP H768 20261110; public source bundle mới chỉ chứa mã và QA. Không đưa H768 story IDs, loss theo truyện, checkpoint TTM hay optimizer lên GitHub.
- `GGUF`, ứng dụng công nghiệp, L0017/18/19 và `main` không thay.
- Cổng khoa học nguyên gốc vẫn nguyên vẹn; nếu 12-arm result valid nhưng co-primary gate không đạt, ghi scientific scoped FAIL, không gán HOLD để né kiểm định.

## Giới hạn

- Colab Free không bảo đảm phiên chạy đủ 24.576 bước; một chunk bị ngắt có thể phải replay dưới 256 bước tính toán, **không cộng vào ngân sách optimizer updates hợp lệ**.
- Phiên Colab mới có thể cấp PyTorch/CUDA khác; chế độ resume phải HOLD để tránh mất khả năng tái lập thay vì tự đổi version.
- Google Drive mount không bảo đảm nguyên tử cho file binary đang ghi; nếu binary dở dang, cần thẩm định thủ công và giữ bằng chứng. Không bật tự động xóa.
- Score một arm đang dở có thể cần được chạy lại sau khi ghi biên bản retry; không chọn model theo kết quả H768.

**Trạng thái trước khi owner chạy notebook mới:** `OWNER_SCIENCE_AUTHORIZATION=GRANTED_FOR_ORIGINAL_4X3_V2` · `RESUME_SOURCE_QA=PASS_CPU_ONLY` · `CLAIM=NOT_CREATED` · `H768=SEALED_UNSCORED` · `SCIENCE=NOT_EXECUTED`.

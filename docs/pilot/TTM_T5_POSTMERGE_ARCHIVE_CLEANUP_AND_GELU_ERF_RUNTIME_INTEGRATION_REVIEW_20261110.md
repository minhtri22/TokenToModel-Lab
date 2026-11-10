# TTM T5 — hậu merge PR #16, bảo toàn archive và phương án runtime GELU_ERF

Ngày rà soát: 2026-11-10. Trạng thái: **SCIENCE=PASS_4/4 · PR16=MERGED · RUNTIME=NOT_PATCHED · LOCAL_CLEANUP=PREPARED_NOT_EXECUTED**.

## A. Kết quả rà soát nguồn và máy

- GitHub PR #16 đã merge vào `main` theo commit **`df126b2d4beaee865faa24d8a7e9720bb59693aa`**, khoa học C01–C04 `STRICT_PASS_4/4` trên GGUF F32 gốc, CPU `KV=F32` và `Flash=OFF`.
- Windows TTM root: `D:\WORK\RESEARCH\TokenToModel-Lab`. Worktree T5 `worktrees\ttm-t5-kvflash-preview-20261109` **còn tồn tại**; không biết Git porcelain `clean` vì RemoteMCP chỉ cung cấp `list_dir/read_file`, còn `run_command` bị chặn bởi managed mode. Do đó **chưa xóa worktree**.
- Các checkout llama.cpp isolate `_tmp\ttm_t5_exact_root_v1_20261110\trace_only` và `...\trace_gelu_erf` vẫn tồn tại, **phải giữ nguyên** vì là chứng cứ và nguồn ứng viên cho runtime. Không `git worktree prune` trên toàn bộ dự án.
- Toàn bộ các thư mục/tệp sau **không được xóa hoặc sửa**: `_tmp\ttm_t5_exact_root_discovery_run_v1_20261110`, `_tmp\ttm_t5_exact_root_discovery_recovery_v2_20261110`, `_tmp\ttm_t5_c01c04_gelu_erf_confirmatory_one_shot_20261110`, `_tmp\ttm_t5_c01c04_source_lock*`, `_tmp\TTM_T5*_REFERENCE_*.zip`, `_tmp\ttm_t5_trained_f32_v1`, `artifacts/qa/ttm-t5-parity`, `lineage.md`, và các checkout P01/SIX/T6, PR #13.
- Đã kiểm tra biên bản export: GGUF F32 **15.061.376 bytes**, **52 tensors**, tokenizer **2.048 tokens**, **1.791 merges**; checkpoint SHA256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`. Biên bản parity gốc có `tokenizer_mismatch_count=2` trên 9 fixture tokenizer: **vấn đề tokenizer riêng biệt** không được giải quyết bởi GELU.
- RemoteMCP `device_list` cho biết machine-1 ONLINE, nhưng API `run_command` trả `managed mode requires task_job_submit`. Danh mục maintenance chỉ có recipe `repo-targeted-pytest-v1`, **không có recipe dọn worktree**. Không dùng task science để thực hiện dọn dẹp kỹ thuật và không giả nhận đã xóa gì.

## B. Phần dọn dẹp an toàn đã chuẩn bị

Đã thêm script `tools/pilot_t5/postmerge/Invoke-TTM-T5-Merged-Worktree-Cleanup-PS51.ps1`. Script chỉ xóa **một worktree T5 đã merge và sạch**, khi chủ dự án chạy với `-ApplyCleanup`.

Các điều kiện bảo vệ gộp một lần:

1. Đường dẫn root/worktree chính xác bên trong TTM, `origin` khớp GitHub, Git worktree tồn tại/được đăng ký duy nhất.
2. `git fetch origin main` chỉ cập nhật `FETCH_HEAD`; remote main phải chứa merge commit PR16 và HEAD worktree phải là ancestor của merge. **Không checkout/reset/pull/sync local main**.
3. `git status --porcelain --untracked-files=all` của T5 worktree **rỗng**. Có bất kỳ sửa đổi hoặc tệp chưa theo dõi → HOLD, không xóa.
4. Sáu tệp bằng chứng hiện hữu phải đúng SHA256: GGUF, receipt discovery A, receipt discovery B, receipt xác nhận C, audit xác nhận C, ZIP P02. Phải có bản nguồn `trace_gelu_erf/src/models/gpt2.cpp` còn tồn tại.
5. `git worktree remove -- <exact-T5-worktree>` **không `--force`**, không `Remove-Item -Recurse`, không `git clean` hoặc `git reset`. Lưu receipt vào `_tmp/ttm_t5_postmerge_worktree_cleanup_v1_20261110` dưới chế độ không ghi đè.
6. **Giữ branch refs local và GitHub** cho truy vết. Dọn branch refs tách khỏi worktree removal và chỉ thực hiện sau khi xác minh các tác vụ liên quan không còn cần HEAD nghiên cứu. Không chạm `main`, PR13, chứng cứ hoặc isolated llama worktree.

Lưu ý: script đã được commit GitHub, **chưa chạy trên Windows**, nên đây là `CLEANUP_READY_OWNER_LOCAL_EXECUTION`, không phải `CLEANUP_PASS`.

## C. Tích hợp GELU_ERF vào runtime: phân tích thiết kế

### C1. Bằng chứng chính xác ở nguồn

- llama.cpp frozen commit: `372dc5ca157276beb6c67b2e92477e8d662e964a`.
- Trong `src/models/gpt2.cpp` upstream GPT-2 dùng đúng `LLM_FFN_GELU, LLM_FFN_SEQ, il` (Git blob `711a148a28bd1aa2c1dccf2e3b21803aac4a4185`). Kiểm tra lại GitHub `master` ngày 10/11/2026 vẫn thấy đúng blob/callsite này.
- T5 B candidate đã sửa tại đúng callsite thành `LLM_FFN_GELU_ERF, LLM_FFN_SEQ, il` và đạt C01–C04 strict PASS. Isolated B còn thêm callback chẩn đoán trong `llama-graph.cpp`: **không đưa nguyên trạng checkout B vào runtime production**.
- GELU mismatch chỉ ảnh hưởng phép tính inference, **không đổi trọng số** hoặc GGUF. GGUF gốc và tokenizer 2048 tokens vẫn phải được lưu SHA.

### C2. Khuyến nghị ba lựa chọn

**A — Ưu tiên, chi phí thấp:** một bản dựng **llama.cpp riêng cho TTM** trong `_tmp/ttm_t5_runtime_gelu_erf_v1/`, lấy nguồn từ đúng upstream pinned commit, chỉ thay **một callsite** trong `src/models/gpt2.cpp`, **không** copy callback trace tạm thời; build CPU x64 `llama-server` và/hoặc `llama-cli`. Cô lập binary/DLL và bind `127.0.0.1` trên cổng khác Ollama 11434 (ví dụ **18085**). Cấu hình parity thử ban đầu: `-ngl 0 -t 1 -c 256 -ctk f32 -ctv f32 -fa off`. Tùy binary pin cụ thể, xác minh `--help` trước; không chạy bất kỳ server nào khi chưa xác minh đúng SHA và cổng.

**B — Sau A, có lợi cho bảo trì:** dùng metadata/điều kiện nhận diện model TTM (ví dụ một GGUF metadata riêng, cần thiết kế lại converter/loader) để chọn GELU exact **chỉ** khi model yêu cầu. Tránh thay GELU mặc định cho toàn bộ GPT-2 mà có thể dùng tanh/approx từ lúc huấn luyện. Đây là **thiết kế mới**, không nằm trong PASS 4/4 hiện tại; cần kiểm tra từ đầu tính tương thích của GGUF/metadata và chú ý không làm thay đổi checkpoint đầu vào.

**C — Ollama tùy chỉnh, sau B hoặc A đã PASS:** Ollama hỗ trợ import GGUF bằng Modelfile `FROM <path.gguf>` nhưng **import thành công không tự sửa** toán tử bên trong binary. Bản Ollama hiện hành có cơ chế build-time `OLLAMA_LLAMA_CPP_SOURCE` để trỏ đến nguồn llama.cpp riêng; nguồn tùy chỉnh có thể bỏ qua compatibility patch của Ollama nên phải phân tích phiên bản/patch và build riêng ở `_tmp` trước. Không thay runtime Ollama cài sẵn, không cài package/khởi động server, không dùng cổng 11434. Phải kiểm tra trình phiên bản `LLAMA_CPP_VERSION` trong repo Ollama, source patch và phiên bản launcher.

### C3. Cổng kiểm tra ứng dụng tối thiểu (không phải lặp lại science)

1. Verify source patch diff chính xác **một callsite**, nguồn upstream commit SHA; file GGUF SHA nguyên bản. Build binary riêng với MSVC x64, chạy self-check loader và tệp source provenance.
2. Kiểm 4 fixture xác nhận **chỉ nếu mở một phép kiểm tích hợp runtime riêng mới** — không được gọi là tái chạy one-shot khoa học; hoặc dùng fixture kỹ thuật hoàn toàn mới nếu cần đo nhẹ. Kết quả science C01–C04 không đổi.
3. Kiểm bộ tokenizer 9 fixture đã có lỗi **2/9**: xác định chênh lệch encode/decode/UTF-8/special tokens, không đánh đồng với strict logits. Chưa PASS tokenizer thì không kết luận hoạt động văn bản tốt.
4. Smoke server HTTP qua localhost cổng riêng, 1–2 prompt phi-TEST, kiểm model load, tốc độ, bộ nhớ, đúng stop/EOS; không coi chất lượng ngôn ngữ của mô hình nhỏ 4M sau 1.024 bước là đã đạt production.
5. Chỉ sau loader/tokenizer/server PASS và source provenance PASS mới lập phương án tích hợp Ollama riêng. Intel Arc/XPU, F16 KV, Flash ON, quantized GGUF có cổng đánh giá khác; tuyệt đối không suy rộng từ C01–C04.

### C4. So sánh khả năng

| Lựa chọn | Cần code | Ảnh hưởng Ollama hiện tại | Phán quyết |
|---|---|---|---|
| llama.cpp TTM riêng (CPU) | Patch 1 callsite + build độc lập | Không | **Ưu tiên bước kế tiếp** |
| Metadata GELU theo model | Sửa converter/loader, đánh giá mới | Không ở giai đoạn thiết kế | Sau A |
| Ollama source tùy chỉnh | Build Ollama + nguồn llama.cpp pin tương thích | Không nếu cài song song | Sau A PASS |
| `ollama create FROM GGUF` trên stock Ollama | Không sửa code | Có thể nhập model nhưng GELU gốc còn khác | **Không đủ chứng minh parity** |

Nguồn tham khảo: `https://github.com/ggml-org/llama.cpp/blob/master/src/models/gpt2.cpp`, `https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md`, `https://github.com/ollama/ollama/blob/main/docs/import.mdx`, `https://github.com/ollama/ollama/blob/main/llama/server/CMakeLists.txt`, `https://github.com/ollama/ollama/blob/main/llama/compat/README.md`.

## D. Quyết định và hành động tiếp theo

- **Khoa học:** PASS có giới hạn `C01–C04 4/4` bất biến; L0013 cũ FAIL 32/32 và L0014 PASS đã lưu append-only.
- **Dọn dẹp:** giữ nguyên evidence và isolated source; chủ dự án chạy đúng script worktree-scoped một lần, chỉ xóa khi toàn bộ cổng PASS. Không tự nhận dọn xong khi RemoteMCP vẫn chặn.
- **Runtime:** chọn phương án A, **thiết kế/preflight-only** ở bước kế tiếp; chưa build/patch/serve, chưa sửa Ollama. Không công bố `PRODUCTION_PASS`.

**Bước thực hiện tiếp theo:** `TTM_T5_MERGED_WORKTREE_CLEANUP_GUARDED_OWNER_BATCH_AND_ISOLATED_LLAMA_GELU_ERF_RUNTIME_SOURCE_PLAN`.

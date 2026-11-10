# TTM Q1/Q2 — Phân xử native V1 HOLD trước khi sinh văn bản; V2 recovery

Ngày 2026-11-09. **V1 one-shot đã tiêu thụ và phải bất biến.** Không ghi đè kết quả, CLAIM, log hay model store của V1.

## Bằng chứng gốc
- PR #13 source HEAD: `fe5f2780786266362b19c24e91f63d2ee888de51`.
- Native evidence commit: `905023a85bf4a4d8aa5567bd026c9309d3de9be7`, `artifacts/qa/q1q2/TTM_Q1Q2_ONCE_V1/{CLAIM,RESULT,PUBLISHED_FILES_SHA256}.json`, readback 3/3 PASS.
- `RESULT.status=HOLD_PARTIAL_NO_AUTOMATIC_RERUN`, `complete_calls=0`, `completed_tokens=0`, `runs=[]`; `failure=MODEL_STORE_MODIFIED_BEFORE_BATCH`. Thời gian 15.469s. PID 22440 dừng `STOPPED_OWNED_TREE`, trạng thái socket `PASS_NO_ACTIVE_SOCKET_AFTER_SHUTDOWN`.
- Ollama 0.40.14 đã PASS /api/version và /api/tags; **không có POST /api/generate nào được chứng minh**.
- Đọc read-only model store V1 trên Windows: 4 blob gốc và `manifests-v2/.../latest` vẫn tồn tại, Ollama tạo thêm `metadata/sha256-5bdc904e6c51af04a4223219f36e6bc2e687f60fd6e17dc24508f3eb7489e4e5.json` cùng thư mục `manifests/` rỗng. Metadata mới chứa `ollama_version=0.40.14`, `general.architecture=gpt2`, 4 layers, d_model=256, ctx=256, 4 heads, BOS/EOS=256. Đây là **cache metadata quan sát được**, không chứng minh các blob bất biến cho đến khi mã kế nhiệm kiểm lại mọi SHA.

## Sửa mã nguồn (duy nhất nhánh PR #13)
- `tools/pilot_q1q2/single_batch_20261109/ttm_q1q2_single_batch.py`: thay hai so sánh `folder_snapshot == baseline` sau /api/tags và sau batch bằng `verify_runtime_store_delta()`.
- Hàm mới luôn so từng entry baseline (SHA256 + byte size) không thay đổi; từ chối mất/sửa file; từ chối **mọi** file bổ sung ngoại trừ đúng một `metadata/sha256-<GGUF_SHA>.json`. Sidecar (nếu hiện diện) phải đúng kích thước, SHA thực, Ollama 0.40.14 và thông số GPT2 khóa. Không cho phép đổi blob, manifest, version, architecture hoặc file lạ.
- `test_ttm_q1q2_offline.py`: bổ sung bốn ca kiểm chứng metadata hợp lệ, baseline blob bị sửa, file lạ, kiến trúc metadata sai. Tổng dự kiến **17 test**. Không thay Q1 48, Q2 24+2, BPE, GGUF, tiêu chí chấm hoặc dữ liệu.
- Runner kế nhiệm dùng `_tmp/ttm_q1q2_ollama_once_v2`, port loopback **12651**, evidence prefix `artifacts/qa/q1q2/TTM_Q1Q2_ONCE_V2`. V1 không bị dọn hay chạy lại. Wrapper giữ nguyên thuật toán tải sha-pinned, one-shot, publish và readback.

## Cổng tiếp theo
1. Đọc lại commit nguồn và kiểm thử **17/17 offline** trên source SHA đã ghim. Nguồn static PASS không thay thế native.
2. Tiền kiểm trên máy Windows Python 3.12, cần dừng nếu SHA MODEL/GGUF/source/BPE/tokenizer hoặc cổng thay đổi, không auto retry.
3. Khi người vận hành cho chạy V2: **một lần duy nhất** 48+2+24, lưu raw response và kết quả trên GitHub. Nếu V2 HOLD sau CLAIM, tuyệt đối không chạy lại.
4. Q1 quality GO/REVISE/STOP chỉ phán quyết khi có đủ output và chấm human rubric. `lineage.md` append-only, không ghi các lỗi kỹ thuật vào science lineage.

**Hiện trạng:** V1=`HOLD_CONSUMED_ZERO_GENERATIONS`; V2=`SOURCE_PATCH_PENDING_OFFLINE_QA`; `QUALITY=NOT_EXECUTED`; `MERGE_DECISION=HOLD`; `main` không đổi.

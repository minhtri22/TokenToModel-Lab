# TTM T5 — Preview đã hoàn tất: phân biệt SHA source và SHA executable; supplement chỉ đọc

**Ngày:** 2026-11-09. **Task:** `TTM_T5_OWNER_LOCAL_PREVIEW_RECEIPT_INDEPENDENT_READBACK_AND_SINGLE_INTEGRATED_RUN_DECISION`. **Trạng thái:** `PREVIEW=COMPLETED_HOLD` · `SOURCE_BINARY_ROLE_ERROR=CONFIRMED` · `SOURCE_KV_SEMANTICS=PENDING` · `NATIVE_2X2=0/32`.

## 1. Kết quả từ máy Windows

Đã đọc trực tiếp, nguyên dạng, hai tệp trong `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\ttm_t5_f32_kvflash_owner_gate_20261109`:

- `OWNER_LOCAL_PREVIEW_SINGLE_20261109.json`: SHA-256 do owner báo `80be696c6e834a6028e1e3c4325c1eb624af65e69566a871019e83b089232d63`.
- `TTM_T5_KVFLASH_Preview_20261109_154621_0013101.json`: SHA-256 trong receipt `cccf26c91f8e22c6f05b0edab2741b076ea04c45dc0aa24f5f0c8eb8bf5d5a71`.

Chế độ `Preview`, `status=HOLD_OWNER_RUN_GATE`, `native_execution=NOT_EXECUTED`. Đã PASS 9 kiểm tra: Branch, CleanTracked, P02GitBlob, PreregGitBlob, LlamaCommit, OldBuildRecord, OldFlashRuntimeLog, OldCMakeSourceDir, GGUFExact. 7 kiểm tra false: CallerSourceSHA, CallerSourceParams, CheckpointExact, ReferenceReady, CandidateExecutablePinned, CallerOwnerAttested, OwnerApproval.

Kết quả đúng là **Preview đã hoàn tất**, chứ không phải `Preview=NOT_EXECUTED`. Tuy nhiên HOLD không đồng nghĩa có quyền chạy.

## 2. Nguyên nhân `CALLER_SOURCE_SHA_MATCH=False`

| Artifact | SHA-256 | Nguồn chứng cứ |
|---|---|---|
| **`ttm_t5_layer_probe.cpp`** tại thư mục source do CMake ghi | `8a8324a10c67c6f868fe130d6ea7c535edb6364c8d04988600163e7b4a4b828e` | Inventory do chính owner Preview đo |
| **`ttm_t5_layer_probe.exe`** trong project `_tmp` | `62fda558309502fdef9c736243b9a6194262fe0b5667949a0872fbe5c33e4de2` | Preview và file GitHub `evidence/pilot/t5-trained/T5_F32_NUMERIC_LOCALIZATION_UNADJUDICATED.json` trường **`native_debug_probe_sha256`** |
| CMakeCache | `6575ad586870cff2e9b30b4551e6e8783d39e90ddb0eb74d5c300cbda3a412af` | Preview |
| Log FlashAttention | `b97345b8f43f76960371459ba97a4c90906ca7b0b31db961bebe81cdd901632d` | Preview |

Các script trước đây dùng cùng `62fda558...` ở trường “source caller expected”. Đây là **lỗi phân loại hiện vật (artifact type/provenance error)** trong công cụ chứng thực, không phải bằng chứng source C++ bị chỉnh sửa. Vì wrapper chỉ chuyển path caller vào preflight khi nó khớp SHA *sai loại*, preflight đã không đọc source và trả `type_k/type_v=UNKNOWN`.

Bản sửa mới phân biệt `OriginalCallerCppSHA256` với `OriginalProbeBinarySHA256`; SHA source mới là **SHA do owner Preview quan sát**, chưa phải independent source-to-binary build attestation. **Không thay dữ liệu gốc, không tự cập nhật hồ sơ cũ hoặc rerun Preview một lần đã dùng.**

## 3. Bước bổ sung chủ máy thực hiện *một lần*, không chạy model

Script đã ghi vào GitHub:

`tools/pilot_t5/kv_flash_precision_v1/Invoke-TTM-T5-Caller-Source-Binary-Supplement-PS51.ps1`.

Nó đọc (không sửa) SHA + một số dòng C++ trong thư mục Downloads đúng CMake source, executable lịch sử trong root TTM, SHA CMakeCache/log và receipt Preview đã khóa. Phải khớp SHA `OWNER_LOCAL_PREVIEW_SINGLE...` `80be696c...`; không khớp → HOLD/throw, không mở native. Không đọc checkpoint hay TEST, không gọi torch/llama, không tạo Git worktree mới. **Chỉ ghi** `_tmp\ttm_t5_f32_kvflash_owner_gate_20261109\OWNER_LOCAL_SOURCE_BINARY_SUPPLEMENT_V1_20261109.json`, không sửa biên bản Preview cũ. Marker chống ghi đè giúp tránh lặp.

Các dòng thu thập: `llama_context_default_params`, `type_k`, `type_v`, `flash_attn_type`, `llama_init_from_model`. Chương trình phân loại sự hiện diện của phép gán F16/F32 rõ ràng so với **default static** hoặc **dynamic/ambiguous**, không diễn giải thành runtime attestation. Cần xem source-to-binary build recipe và các nhánh điều kiện trước khi quy kết cấu hình chạy thật.

Gọi script tại commit SHA chính xác của nhánh T5 và kiểm Git blob đã ghim ở mục bàn giao của trợ lý. Lưu kết quả không có dữ liệu bí mật vào GitHub dưới dạng **receipt phụ lục**, không upload nguyên source trong Downloads mà chưa kiểm quyền.

## 4. Quyết định tích hợp tiếp theo

- **Source hash mismatch:** có thể sửa phân loại và kiểm tra lại bằng một receipt mới, không thay đổi Preview gốc.
- **Source static K/V:** cần có supplement mới và xem dòng mã; nếu `DEFAULT_...`, kết luận chỉ là **source static inference**, chưa đủ chứng nhận thực thi K/V nếu chưa có build linkage.
- **Old binary provenance:** SHA `62fda558...` phù hợp receipt cũ, nhưng source hiện ở Downloads ↔ executable đã build là quan hệ **chưa được chứng thực độc lập**.
- **New C++ candidate:** chưa biên dịch; **new PyTorch reference:** chưa tạo; **owner authorization:** chưa cấp. Vì thế `READY_2X2=NO`.
- **Kết quả strict trước:** `FAIL_7/8` tại `max_abs=0.001`, không được đổi nhãn. `main`, `lineage.md` và PR#13 không đổi.

**Bước thực hiện tiếp theo:** `TTM_T5_CALLER_SOURCE_BINARY_SUPPLEMENT_OWNER_READBACK_THEN_NATIVE_READINESS` — owner chạy đúng một lần script supplement, trả JSON và SHA; đối chiếu một gói source/body/classification/binary. Chưa chạy 32 native decodes.

# TTM T5 — Bản vá schema PowerShell V5, tiền kiểm chưa tiêu thụ lượt (2026-11-09)

Nguồn gốc lỗi: ZIP V5 SHA256 `0c27593dd01c5e652709c03b6a0019533aa602e178d1e4251052bc69bf01ef33` chứa manifest schema `ttm.t5.v5.timewait_guard.one_shot.source.manifest.v1` nhưng wrapper PowerShell so với schema V4 `ttm.t5.final.minimal.compat.one_shot.source.manifest.v1`. Kết quả trên máy người dùng `INVALID_MANIFEST_SCHEMA` và wrapper exit 1, xảy ra **trước claim**. Quan sát thư mục qua RemoteDesktop xác nhận không có thư mục `_tmp\ttm_t5_ollama_compat_only_single_v5final` tại thời điểm kiểm tra.

Bản vá `Repair-TTM-T5-V5-Manifest-PS51.ps1` SHA256 `ed4139967179b8ab1d10caa5a4aeeb08e875e85b2f3a0ae0616c1b4689efc6c5`: xác minh repo/ZIP/manifest/wrapper/source trước khi sửa; thay **một** chuỗi schema, giữ wrapper gốc bằng bản sao lưu `.original_sha856a61d3.bak`; wrapper sau sửa SHA256 `238570d7c98e228d351dbe9ebcd6992fb018ba482d9d0078008d4ab8a2c5c8ad`. Không sửa ZIP, manifest, Python runtime, GGUF, checkpoint, khoa học, hoặc các lượt V1–V4. Từ chối khi claim V5 tồn tại.

15/15 kiểm tra cấu trúc bản vá và SHA PASS trên môi trường assistant; kiểm thử V5 gốc 47/47 PASS giả lập. Chưa chạy bản vá bằng PowerShell 5.1 thực tế và chưa chạy Ollama V5. Khi người dùng chọn chế độ `PatchAndSmoke`, wrapper đã sửa sẽ chạy lại source QA, preview và chỉ khi PASS mới thực thi đúng một lần, không tự chạy lại sau CLAIM.

Quyết định: `V5_PRECLAIM_FAILURE=PACKAGING_SCHEMA_MISMATCH`; `V5_ONESHOT=NOT_CONSUMED_AS_OF_READONLY_CHECK`; `V1-V4=CONSUMED_NO_RERUN`; `T5_STRICT_PARITY=FAIL_7_OF_8_PRESERVED`. Bước tiếp theo: `TTM_T5_V5_MANIFEST_SCHEMA_ONE_LITERAL_PATCH_AND_SINGLE_NATIVE_SMOKE`. Không merge PR #12, không chỉnh `main`, `lineage.md`.

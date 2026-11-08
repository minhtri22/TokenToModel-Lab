# TTM T5 — Thiết kế sửa readiness gate V2 và kiểm định tĩnh độc lập (2026-11-08)

## 1. Phạm vi khóa
- V1 tại `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\ttm_t5_ollama_compat_only_single_v1` đã có `CLAIM.json` và `RESULT.json`: **one-shot đã tiêu thụ, không chạy lại, không dọn**.
- Lỗi V1 `ISOLATED_OLLAMA_SERVER_NOT_READY_20S` xảy ra **trước** import GGUF và inference. `serve.log` xác nhận Ollama 0.40.14 lắng nghe tại `127.0.0.1:12643` nhưng vòng kiểm tra không lưu PID/HTTP cụ thể.
- Không kết luận GGUF tương thích hay không tương thích. `T5_STRICT_LOGITS=FAIL_7_OF_8_PRESERVED` giữ nguyên; không TRAIN/TEST, không sửa checkpoint, GGUF, ngưỡng, `lineage.md` hoặc `main`.

## 2. Nguồn kế nhiệm V2 (chưa cấp quyền chạy)
- Bộ nguồn: `TTM_T5_OLLAMA_READINESS_V2_SOURCE_ONLY_20261108.zip`, SHA-256 `9da06fad41cd45a03f9221aade5de1fd6ef8446879276eebeebbebcbd9f71bbf`, 16872 bytes. Gói được phân phối dưới dạng tệp đính kèm của lượt trao đổi, **chưa tải full ZIP lên GitHub**; manifest và QA được ghim trong nhánh PR #12. Không xem tài liệu GitHub là bằng chứng rằng V2 đã được chạy.
- File Python V2 SHA-256 `de80194c4576ea8749fce0ec1367ee65a9d520f563ab70063006d5a6506def6f`; file checker độc lập SHA-256 `1d5da70808a9d63844b1a9ce66ba25864f27bee47b5c040d93795cebe4a7acae`.
- V2 dùng output root **khác hoàn toàn** `_tmp/ttm_t5_ollama_compat_only_single_v2`, cổng `127.0.0.1:12644`, tag `ttm-t5-f32-compat-only-v2:latest`. Giữ nguyên `num_ctx=256`, tối đa 32 token, nguồn GGUF F32 đã ghim SHA, model store trong project và khóa chống chạy lại.
- V2 ghi mỗi lần thử vào `READINESS_ATTEMPTS.jsonl` theo kiểu tạo mới độc quyền, `flush()` và `fsync()` trước quyết định, gồm timestamp, attempt, PID mong đợi, PID owner, các dòng netstat cục bộ, trạng thái HTTP, API version, loại/mã lỗi, quyết định.
- V2 không gọi HTTP khi PID khác, binding không phải loopback hoặc chứng cứ netstat không đáng tin cậy. HTTP chỉ tới `127.0.0.1:12644/api/version`, dùng `ProxyHandler({})` để bypass các proxy hệ thống; không ghi URL proxy/secret.
- Cảnh báo về thư mục DLL `_tmp/ttm_t2/build/bin/Release` được ghi vào `PATH_DLL_RISK.json` với nhãn `WARN_ENVIRONMENT_RISK_NOT_CAUSAL_PROOF` nếu thấy trong PATH. Không tự sửa PATH hoặc tải DLL. Chưa đủ bằng chứng kết luận cảnh báo DLL gây timeout V1.
- Số lần thử tối đa 40, nghỉ 0,5 giây giữa các lần; chi phí hệ thống khiến đây không phải cam kết chính xác 20 giây thời gian thực.

## 3. Kiểm định tĩnh độc lập
- Chạy checker trong gói bằng process/PID/netstat/HTTP **giả lập** (không tạo Ollama process, không mở socket thật, không import model). **23/23 PASS**, CPython 3.13 trên môi trường kiểm định nguồn; cú pháp phân tích theo Python 3.12.
- Các kiểm thử âm: sai PID -> HOLD không gửi HTTP; bind wildcard -> HOLD; netstat không nhất quán -> HOLD; process chết -> FAIL; version sai/HTTP lỗi/JSON lỗi -> ghi nguyên nhân; timeout -> vẫn lưu đầy đủ mẫu; file trace có sẵn -> không ghi đè; PATH cảnh báo không tự thay đổi; ID V2 không trùng V1.
- Trên Windows, checker được thiết kế đặt thư mục tạm bên trong `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp`. Kiểm định Windows native **chưa thực hiện**. Đây là QA riêng bằng dữ liệu giả lập, không phải kiểm định nhân sự thứ ba.

## 4. Phán quyết và bước kế
`READINESS_V2_DESIGN=COMPLETE` · `STATIC_QA=PASS_23_OF_23_SCOPED` · `NATIVE_WINDOWS_QA=NOT_EXECUTED` · `V1_ONE_SHOT=CONSUMED_NO_RERUN` · `V2_SMOKE=NOT_AUTHORIZED` · `T5_FULL_LOGITS=FAIL_PRESERVED`.

Bước tiếp theo: `TTM_T5_OLLAMA_READINESS_V2_WINDOWS_STATIC_PREVIEW_AND_NEW_SINGLE_SMOKE_AUTHORIZATION_DECISION`. Phải xác minh source SHA/đường dẫn Windows và quyết định phạm vi một lần chạy mới trước khi dùng V2. Không có cấp phép thực thi V2 trong biên bản này.

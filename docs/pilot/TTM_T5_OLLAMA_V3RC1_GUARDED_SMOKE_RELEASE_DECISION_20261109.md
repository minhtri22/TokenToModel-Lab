# TTM T5 — Phát hành ứng viên Ollama V3 RC1 và quyết định một lượt smoke (2026-11-09)

## Mục tiêu
Chỉ xác nhận GGUF F32 gốc TTM-Small-4M-T4 step1024 có thể **nhập và suy luận** bằng Ollama 0.40.14 trên Windows. Đây là kiểm tra tương thích kỹ thuật (compatibility-only), **không** chứng minh strict logits parity, chất lượng mô hình hay giá trị khoa học.

## Nguồn và danh tính được khóa
- V3 nguồn (không sửa, đang khóa): `tools/pilot_t5/ollama_tcp_owner_guard_v3_source_only_20261109/t5_ollama_smoke_v3_candidate.py`, SHA256 `9d7be21e5bc961a2fbcbe42c58790d8b2aac755e7d1e184eb7fd5d4c833f13cf`.
- RC1 tệp mới: `tools/pilot_t5/ollama_v3rc1_guarded_smoke_20261109/t5_ollama_v3rc1.py`, SHA256 `54a60678e72ebb829395edb2aa23e12d23da1388e3204b2e629138abc8ab493b`.
- ZIP đúng nguồn: `TTM_T5_OLLAMA_V3RC1_GUARDED_SMOKE_20261109.zip`, SHA256 `e96a876e5a08cdaa0da056570cc40da6807f8e59fe606c48e97b6108be3a5e9f`, 26099 bytes. ZIP phát hành kèm thông qua liên kết tệp hội thoại; 6 file văn bản trong ZIP đã được commit, hash Git blob đều khớp.
- Manifest: `tools/pilot_t5/ollama_v3rc1_guarded_smoke_20261109/SOURCE_SHA256_MANIFEST.json` (SHA256 `b9c500968ceb37c3c78b920c5cdd6917246ef5c8d840d172333be29adf187774`).
- Windows Python 3.12 (đường dẫn cố định), PowerShell 5.1, Ollama `0.40.14` executable SHA `14e0fff0449ce3c3a7fe9db8b8b32089274db5f835d4c99f5af7c32dcbf08981`.
- GGUF `TTM-Small4M-T4-step1024-F32.gguf` 15,061,376 bytes SHA256 `5bdc904e6c51af04a4223219f36e6bc2e687f60fd6e17dc24508f3eb7489e4e5`.
- Cổng `127.0.0.1:12645`, tag `ttm-t5-f32-compat-only-v3rc1:latest`, `num_ctx=256`, `num_predict=32`, prompt tổng hợp.

## Kiểm định độc lập và giới hạn
- V3 source-only trước đó đã QA Windows `PASS_60_OF_60`; **không** dùng bản V3 đó để chạy thực tế.
- RC1 mới kế thừa bộ 60 negative unit tests từ V3, cập nhật kiểm tra CLI/đường dẫn cho RC1 và bổ sung 24 trường hợp gồm mô phỏng end-to-end serve→create→manifest→generate, giữ FAIL khi API không đủ điều kiện, kho mô hình sai, >32 token, PID không tin cậy, ngăn overwrite. **84/84 PASS** trên môi trường kiểm thử ngoại tuyến Python 3.13.5, Linux, có mock tất cả các lệnh process/HTTP. `INDEPENDENT_OFFLINE_QA_RC1.json` là báo cáo gốc.
- **Chưa thực hiện** RC1 với Windows PowerShell 5.1, Windows native TCP table, hay Ollama runtime. Chưa nhập GGUF hoặc gọi generate bằng RC1. Không ghi PASS về runtime.
- Đường lưu mô hình, HOME, APPDATA, LOCALAPPDATA, TMP của tiến trình Ollama riêng nằm trong project TTM. Chỉ bỏ đường dẫn DLL TTM t2 có cảnh báo khỏi PATH của **tiến trình con**, không sửa PATH toàn hệ thống. Không sử dụng cổng 11434 hoặc cấu hình dịch vụ hiện có.
- RC1 dùng Windows TCP table + CIM để xác minh PID, executable/CreationDate, `State=Listen`, loopback; HTTP /api/version và đối chiếu PID trước/sau; fail-closed khi không chắc chắn. Ghi trace và báo cáo cả PASS/FAIL.

## Quyết định
**`V3_RC1_RELEASE_SOURCE_QA=PASS_SCOPED_MOCK_84_OF_84`.**
**`V3_RC1_ONE_SHOT_COMPATIBILITY_SMOKE=AUTHORIZED_CONDITIONALLY`** — chỉ chấp nhận một lượt khi trên **Windows đích**, wrapper xác minh ZIP exact SHA và manifest, PowerShell parse, QA 84/84, `--mode preview` PASS với đúng GGUF/executable/phiên bản/cổng trống và thư mục V3RC1 chưa tồn tại. Các điều kiện được gộp trong **một** lệnh PowerShell wrapper `-Mode Smoke`; không cấp phép từng kiểm thử nhỏ.

- Thư mục claim: `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\ttm_t5_ollama_compat_only_single_v3rc1`. Khi `CLAIM.json` đã có, **CONSUMED dù PASS, FAIL hay HOLD**; cấm dọn, đổi tên, chạy lại. V1/V2 đã tiêu thụ; không chạm các thư mục đó.
- Nếu wrapper QA/preclaim FAIL trước claim: `HOLD_PRECLAIM_NO_RUN`, báo cáo; không khởi động lại dịch vụ khác. Nếu runtime FAIL sau claim: giữ `RESULT.json`, `READINESS_ATTEMPTS.jsonl`, `serve.log`, model-store snapshots/logs; không chạy lại.
- Chỉ PASS `PASS_COMPATIBILITY_ONLY_OLLAMA_IMPORT_AND_INFERENCE` khi CLI create 0, kho mô hình project-local có manifest, local tags xác nhận đúng tag, API generate `done=true`, `1<=eval_count<=32`, đúng response model, kiểm PID và SHA trước/sau. Mọi kết quả khác là FAIL/HOLD đúng giai đoạn, **không tự kết luận không tương thích** nếu chưa đến import.
- V3 original source-only vẫn khóa; `main`, `lineage.md`, checkpoint và GGUF gốc không đổi. `T5_STRICT_LOGITS=FAIL_7_OF_8_PRESERVED`. Đây chưa phải kết quả khoa học.

## Bước thực hiện tiếp theo
`TTM_T5_OLLAMA_V3RC1_EXACT_ONCE_NATIVE_SMOKE_AND_EVIDENCE_READBACK`: người dùng thực thi đúng wrapper `-Mode Smoke` một lần tại Windows đích theo ZIP SHA pinned, trả về `RESULT.json` và `READINESS_ATTEMPTS.jsonl` cùng SHA. Chỉ sau đó phân xử `PASS_COMPATIBILITY_ONLY` hay `FAIL/HOLD`; không mở lại V1/V2 và không đổi strict parity.

### Chốt bản sửa wrapper sau QA
Đã sửa đọc trường tùy chọn `failure` trong PowerShell 5.1 bằng kiểm tra `PSObject.Properties` để PASS không bị lỗi giả; stdout/stderr của Python QA được redirect bằng `Start-Process` vào tệp trong project, tránh giả lỗi `NativeCommandError`. QA 84/84 vẫn PASS trên nguồn cuối. Mã RC1, wrapper và manifest chỉ được coi là đúng khi SHA phiên bản **cuối** khớp.

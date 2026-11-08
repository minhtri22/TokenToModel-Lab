# TTM T5 — Phân xử tiền kiểm Ollama Windows chỉ đọc

**Ngày:** 2026-11-08  
**Hạng mục:** `TTM_T5_OLLAMA_LOCAL_READONLY_PREFLIGHT_EVIDENCE_READBACK`  
**Phạm vi:** GGUF F32 T4 step1024 (đã khóa), Ollama Windows 0.40.14; tiền kiểm kỹ thuật (engineering QA), không phải kết quả thực nghiệm khoa học hay xác nhận tương đương số học (numeric parity).

## 1. Nguồn chứng cứ và kết quả

Nguồn trực tiếp là **console PowerShell Windows do người dùng cung cấp**, không phải một lượt thực thi native độc lập mới của reviewer. Bộ tiền kiểm V1 chỉ đọc từ `TTM_T5_OLLAMA_READONLY_PREFLIGHT_V1.zip`; SHA-256 đã công bố cho gói là `b2919a966f56d1cc954938078473df637d76661bf78d21e9ce51cc8cb942076c`.

| Kiểm tra | Giá trị được console báo cáo | Nhận định |
|---|---|---|
| Python | `C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe` | Đủ để thực hiện bộ đọc cấu trúc |
| GGUF SHA-256 | `5bdc904e6c51af04a4223219f36e6bc2e687f60fd6e17dc24508f3eb7489e4e5` | Khớp GGUF T5 gốc đã ghim |
| GGUF cấu trúc | v3 · GPT-2 · 15.061.376 byte · 18 metadata · 52 F32 tensor · context 256 | `GGUF_READONLY_STRUCTURE_PASS` |
| Tokenizer | 2.048 token, 1.791 merge | Khớp export đã ghim |
| Ollama CLI | `C:\Users\minht\AppData\Local\Programs\Ollama\ollama.exe` · `0.40.14` | Phát hiện được CLI |
| Process `ollama*` | 2 | Có process nhưng không chứng minh riêng runner đang được dùng |
| Port 11434 listener | `NO` từ `Get-NetTCPConnection` | Ảnh chụp chưa nhất quán với HTTP GET |
| HTTP `/api/version` | `0.40.14` từ `http://127.0.0.1:11434/api/version` | HTTP local API truy cập thành công tại thời điểm đo |
| `ollama create`, `run` | `NOT_EXECUTED_READONLY` | Chưa thử tương thích thực tế |
| T4 TRAIN/TEST | `NOT_ACCESSED` | Giữ nguyên |

### Phân xử khác biệt port/API

Bộ chạy nguồn dùng `Get-NetTCPConnection -LocalPort 11434 -State Listen -ErrorAction SilentlyContinue` để đo listener, sau đó `Invoke-RestMethod -Method Get -Uri http://127.0.0.1:11434/api/version -TimeoutSec 2`. Lệnh HTTP GET thành công và nhận phiên bản `0.40.14` có giá trị trực tiếp hơn đối với **khả năng truy cập API ở thời điểm đó**. Không suy ra `LISTENER=YES` từ hai phép đo mâu thuẫn và cũng không suy ra Ollama tắt. Có thể do hạn chế phép liệt kê, định tuyến/ủy quyền hoặc khác thời điểm chụp; **chưa xác định nguyên nhân cụ thể**. Không khởi động lại service để xử lý biểu hiện này.

## 2. Khả năng nhập GGUF và giới hạn còn lại

Theo tài liệu Ollama chính thức hiện hành (`https://docs.ollama.com/import`, `https://docs.ollama.com/modelfile`), cú pháp `FROM` trỏ GGUF và `ollama create` dùng để nhập mô hình. Đây là **khả năng được tài liệu hóa**, không phải bằng chứng phiên bản Ollama 0.40.14 đã chấp nhận GGUF TTM.

**Ràng buộc đặc biệt:** tài liệu Ollama Windows (`https://docs.ollama.com/windows`) cho biết mô hình mặc định nằm trong thư mục tài khoản (`~/.ollama`), trừ khi `OLLAMA_MODELS` đã được định cấu hình cho process server. `ollama create` ghi blobs/manifest vào model store của **Ollama server**. Đặt `OLLAMA_MODELS` chỉ trong cửa sổ terminal client không chứng minh được rằng một daemon Ollama đang chạy đã nhận thay đổi. Vì quy tắc TTM giới hạn ghi vào `D:\WORK\RESEARCH\TokenToModel-Lab`, **chưa thể chạy import trên server hiện tại khi model store đích còn chưa được xác minh**. Không chỉnh cấu hình hệ thống hoặc khởi động lại Ollama trong bước readback.

## 3. Phán quyết

- `TTM_T5_OLLAMA_LOCAL_READONLY_PREFLIGHT=PASS_SCOPED`.
- `GGUF_F32_SOURCE=PINNED_UNMODIFIED` · `OLLAMA_LOCAL_API=REACHABLE_AT_PROBE_TIME` · `CLI_VERSION=0.40.14`.
- `OLLAMA_PORT_LISTENER_SNAPSHOT=INCONSISTENT_NON_BLOCKING_FOR_READONLY`.
- `OLLAMA_EXACT_GGUF_IMPORT=NOT_TESTED` · `OLLAMA_INFERENCE=NOT_TESTED` · `OLLAMA_COMPATIBILITY=NOT_ESTABLISHED`.
- `COMPATIBILITY_ONLY_EXECUTION=HOLD_PROJECT_LOCAL_OLLAMA_MODEL_STORE_NOT_VERIFIED`.
- `T5_BACKEND_NUMERICAL_INCOMPATIBILITY=DOCUMENTED_CLOSED`; full logits FAIL 7/8 dưới ngưỡng `0.001` giữ nguyên; checkpoint/GGUF/TEST/TRAIN không bị sửa hoặc chạy lại.

## 4. Bước thực hiện tiếp theo, không thực thi trong readback

`TTM_T5_OLLAMA_COMPATIBILITY_ONLY_PROJECT_LOCAL_STORE_GUARD_AND_SINGLE_SMOKE`:

1. Gộp tiền kiểm storage/runtime và một lượt smoke thành **một quy trình kỹ thuật duy nhất**. Trước mọi ghi phải xác minh không trùng tên model tag, dung lượng, quyền thư mục, và **model store của daemon thực sự** nằm bên trong dự án. Không được đụng vào server/tray Ollama đang phục vụ công việc khác.
2. Chỉ khi điều kiện storage được chứng minh, tạo Modelfile trong `_tmp` trỏ tới **GGUF F32 gốc bằng đường dẫn tuyệt đối**; giới hạn context 256, không chat template ngoài ý muốn; dùng một prompt tổng hợp ngắn và giới hạn đầu ra. Đo import rồi inference đúng một lần. Ghi logs, manifest/tên model, SHA trước/sau, quyết định PASS/FAIL/HOLD vào `_tmp` trong project.
3. Nếu không chứng minh được storage confinement: `HOLD_NO_CREATE`; không thử `ollama create` vào default user store, không tự động thay đổi `OLLAMA_MODELS`, không tự cài Ollama mới, không chạy lại hoặc xóa chứng cứ lỗi. Kết quả smoke chỉ có nhãn `COMPATIBILITY_ONLY`, **không nâng T5 strict parity**.

Tài liệu là QA kỹ thuật, **không cập nhật `lineage.md`**. Nhánh PR #12 vẫn DRAFT; không hợp nhất vào `main`.

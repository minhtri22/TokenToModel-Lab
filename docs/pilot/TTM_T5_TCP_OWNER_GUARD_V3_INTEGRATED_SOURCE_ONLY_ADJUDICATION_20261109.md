# TTM T5 — Phán quyết sửa tích hợp TCP owner guard V3 (source-only, 2026-11-09)

## 1. Phạm vi và xuất xứ

Đây là sửa kỹ thuật **chỉ trên mã nguồn** sau khi cả hai lượt thử Ollama V1/V2 đã tiêu thụ. **Không** chạy `ollama serve`, `ollama create`, `ollama run` hay `/api/generate`; không đọc TEST/TRAIN; không sửa checkpoint/GGUF, `main` hay `lineage.md`. Bằng chứng gần nhất: trên cổng Ollama hiện có 11434, `netstat.exe -p TCP` và `-p TCPv6` đều không thấy listener, nhưng `Get-NetTCPConnection` thấy PID 14464 `ollama.exe`; TCP tới loopback PASS và `/api/version` 200 với 0.40.14. Nguyên nhân sâu xa của sự bất nhất này **chưa được cô lập**; không gán nó cho IPv6 hoặc DLL.

Microsoft Learn xác nhận `Get-NetTCPConnection` cung cấp `LocalAddress`, `LocalPort`, `State`, `OwningProcess`; trạng thái `Listen` được hỗ trợ: https://learn.microsoft.com/en-us/powershell/module/nettcpip/get-nettcpconnection

## 2. Thay đổi mã nguồn tích hợp

- Sao chép hợp đồng Ollama V2 vào một ứng viên riêng **V3**: tag `ttm-t5-f32-compat-only-v3:latest`, cổng `127.0.0.1:12645`, bằng chứng trong `_tmp/ttm_t5_ollama_compat_only_single_v3`. Không đụng V1 và V2. Đây là chuẩn bị kế nhiệm, không cấp quyền V3.
- Bỏ mọi chốt `netstat` trong mã ứng viên. Bộ quan sát dùng PowerShell 5.1 chạy `Get-NetTCPConnection -ErrorAction Stop`, lọc cổng đã ghim, trích xuất cả trạng thái kết nối; với listener, dùng `Get-CimInstance Win32_Process` để đọc PID, `Name`, `ExecutablePath`, `CreationDate`. Không viết dữ liệu hệ thống, không sửa dịch vụ.
- **Chỉ nhận** `State=Listen`, PID sở hữu đúng tiến trình con Ollama, `Name=ollama.exe`, executable path trùng đường dẫn Ollama đã ghim, `CreationDate` không rỗng. Từ chối PID lạ, nhiều PID, thiếu `State`, thiếu đường dẫn, CIM lỗi.
- **Chỉ nhận** `LocalAddress=127.0.0.1` hoặc `::1`; từ chối `::`, `0.0.0.0`, địa chỉ mạng khác và IPv4-mapped loopback khi chưa chứng minh tính an toàn. Không tự coi wildcard là loopback.
- Chỉ khi danh tính TCP đạt, mới gọi **HTTP GET trực tiếp** `/api/version` với `ProxyHandler({})`, yêu cầu status 200 và phiên bản chính xác `0.40.14`. Sau HTTP, đọc lại TCP table, đối chiếu PID, executable path, `CreationDate` và tập listener để chống thay đổi trong khoảng kiểm tra.
- Mọi lần thử ghi vào `READINESS_ATTEMPTS.jsonl` với `open('x')`, `flush()` và `fsync()`. Bộ guard nguồn cũng kiểm tra lại PID trước/sau các giai đoạn nhập và sinh token **chỉ như thiết kế, chưa chạy**.
- Vẫn giữ pin SHA GGUF `5bdc904e6c51af04a4223219f36e6bc2e687f60fd6e17dc24508f3eb7489e4e5`, `num_ctx=256`, `num_predict<=32`, dữ liệu prompt tổng hợp và kho mô hình riêng dưới gốc TTM. Cảnh báo `ggml-base.dll` được ghi quan sát, không kết luận là nguyên nhân.
- **Khóa thi hành cứng** trong `execute()`: `V3_SOURCE_ONLY_EXECUTION_LOCK_NO_RUNTIME_PERMIT`; CLI chỉ có `--mode contract`, từ chối `--mode execute`. Không có phép chạy Ollama nào trong bộ kiểm định.

## 3. Kiểm định độc lập (independent static QA)

**`PASS_SCOPED_INDEPENDENT_OFFLINE_60_OF_60`**. Kiểm tra Python AST, 60 bài unittest giả lập: IPv4/IPv6 loopback đúng PID; cả hai wildcard và địa chỉ mạng ngoài; PID khác/nhiều PID; trạng thái Bound, Established, rỗng; thiếu identity, đường dẫn, tên executable; `CreationDate` đổi; HTTP 503, JSON hỏng, sai version, lỗi không rò rỉ chi tiết; PID/sockets thay đổi sau HTTP; mảng trace ghi độc quyền, lỗi query TCP, không ghi đè; giả lập PowerShell `-EncodedCommand`, schema, port và khóa thi hành V3. Tất cả kiểm thử offline chạy thành công trong môi trường assistant trên Python stdlib, không gọi PowerShell hay Ollama thật. Không gọi lệnh mô hình và không tạo claim V3.

- Mã nguồn candidate SHA-256: `9d7be21e5bc961a2fbcbe42c58790d8b2aac755e7d1e184eb7fd5d4c833f13cf`.
- Bộ checker SHA-256: `c23e5513714c62f71c39d6287ae82afe4af3f111604c4ef7809a0b0170f01370`.
- ZIP bundle SHA-256: `ab4bcbe1d9e591f124b90fc5d342e93b6ae0a042b405053cbd7b437d8d691c71` (19.937 bytes). Bản blob nhị phân trên GitHub trùng chính xác SHA của ZIP đã tạo.

**Chưa được kiểm định:** Windows PowerShell 5.1 parse/runtime thật, hành vi `Get-NetTCPConnection` và `Get-CimInstance` trên máy đích trong đường gọi V3, khóa PID khi có kết nối thật, GGUF import, và sinh token. Cần fail-closed nếu TCP table không khả dụng hoặc không thấy `Listen`; không bù bằng bỏ qua kiểm tra PID.

## 4. Phán quyết

| Điều kiện | Phán quyết |
|---|---|
| V3 integrated source | `IMPLEMENTED_SOURCE_ONLY` |
| Independent offline QA | `PASS_60_OF_60` |
| Windows native PowerShell 5.1 QA | `NOT_EXECUTED` |
| V3 runtime execution | `LOCKED_NOT_AUTHORIZED` |
| V1/V2 | `CONSUMED_NO_RERUN` |
| Ollama GGUF import/inference | `NOT_ESTABLISHED` |
| GGUF/checkpoint | `UNCHANGED` |
| T5 strict full logits | `FAIL_7_OF_8_PRESERVED` |
| `main`, `lineage.md` | `UNCHANGED` |

## 5. Bước thực hiện tiếp theo

`TTM_T5_TCP_OWNER_GUARD_V3_WINDOWS_STATIC_QA_AND_TCP_TABLE_READONLY_READBACK`: thực hiện PS5.1 wrapper checker tĩnh trên Windows với SHA nguồn ghim, sau đó **chỉ đọc** danh sách TCP table dịch vụ Ollama đang có, xác nhận `State` là `Listen` trong JSON chuẩn hóa, không tạo tiến trình Ollama mới và không mở model store. Nếu PASS mới cân nhắc một quyết định cho một lượt smoke kế nhiệm mới; không tự động cấp phép V3 và không xóa V1/V2.

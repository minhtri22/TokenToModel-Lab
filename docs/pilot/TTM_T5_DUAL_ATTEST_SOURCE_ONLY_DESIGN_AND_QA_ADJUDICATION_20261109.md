# TTM T5 — Xác minh kép PID–HTTP: bản nguồn khóa thực thi và QA ngoại tuyến (2026-11-09)

## Quyết định
**PASS_SCOPED_OFFLINE_QA_114_OF_114** cho bản thiết kế nguồn Dual RC2. **RUNTIME_PERMIT=NOT_ISSUED**: chưa chạy native Windows 3.12 của bộ nguồn mới, chưa nhập GGUF hoặc suy luận. Gói ZIP chính xác và SHA-256 được lưu ở `tools/pilot_t5/dual_attestation_source_only_20261109/TTM_T5_DUAL_ATTEST_SOURCE_ONLY_20261109.zip`; mã nguồn, tester, README, manifest và biên bản thiết kế nằm nguyên trong ZIP. JSON SHA tương ứng nằm trong `evidence/pilot/t5-trained/`.

## Căn cứ
- V1/V2/V3 RC1 là **ba lượt Ollama đã tiêu thụ**. RC1 HOLD ở `State=""`, IP Helper kiểm tra dịch vụ 11434 trả `state_code=0` ở cả IPv4 và IPv6. `0` không phải TCP LISTEN (2), không được lén đổi hoặc bỏ qua kiểm tra chủ sở hữu.
- Ollama 0.40.14 thông thường trả HTTP 200 và GUI hoạt động với model chưa xác định; **không** chứng minh TTM-Small-4M tương thích.
- T5 strict full logits có kết quả khoa học gốc **FAIL 7/8**; bảo toàn checksum checkpoint/GGUF gốc và lineage.

## Bộ bảo vệ mới
1. Dùng `GetExtendedTcpTable` IPv4+IPv6 (bất kỳ family lỗi -> HOLD), duy trì raw `state_code`, `remote_address`, `remote_port`, `pid`, `local_address`, `local_port` và giới hạn buffer/count.
2. Đúng cổng riêng `12646`, chỉ loopback `127.0.0.1`/`::1`, đúng PID tiến trình con, đúng đường dẫn `ollama.exe` và CreationDate. Từ chối wildcard, địa chỉ LAN, nhiều PID, PID khác, state không hợp lệ. Với state **0**, chỉ là *socket ứng viên* khi remote address/cổng bằng không, không bao giờ gọi là LISTEN.
3. Cần HTTP trực tiếp (không proxy) GET `127.0.0.1:12646/api/version` trả 200 và phiên bản `0.40.14`; sau đó bắt buộc snapshot TCP/identity lần 2 không đổi. Kết quả riêng `READY_DUAL_ATTESTED_STATE_ZERO_UNKNOWN` không tuyên bố LISTEN.
4. Luồng create/generate theo mã kế thừa RC1: kho model tách trong project, Modelfile từ GGUF gốc SHA `5bdc904e6c51af04a4223219f36e6bc2e687f60fd6e17dc24508f3eb7489e4e5`, chỉ sinh tối đa 32 token với context 256; manifest/tag phải tồn tại trước khi generate. Chạy lại cùng thư mục CLAIM bị từ chối.
5. **Khóa thực thi:** `--mode contract` là tùy chọn CLI duy nhất; `--mode execute` bị từ chối; chốt `SOURCE_ONLY_EXECUTION_LOCK=True` đặt ở đầu `execute`. QA mô phỏng cả đường create/generate; không tạo model thực.

## QA và mức độ chứng minh
Đã chạy **114/114 PASS** trong assistant container: 21 bài parser; 36 ownership; 28 HTTP & trace; 21 lock & scope; 8 mô phỏng pipeline. QA này **không** chạy Windows native IP Helper/Powershell 5.1 thật và **không** chứng minh Ollama tải được GGUF. Mã wrapper để kiểm tra SHA và 114 bài được ghim trong ZIP; chỉ được dùng để kiểm định tĩnh Windows.

## Phán quyết
`SOURCE_DESIGN=COMPLETE` · `OFFLINE_QA=PASS_114/114` · `WINDOWS_STATIC_QA=PENDING` · `NEW_OLLAMA_SINGLE_SMOKE=NOT_AUTHORIZED` · `V1_V2_RC1=CONSUMED_PRESERVED` · `TTM_GGUF_COMPATIBILITY=NOT_ESTABLISHED` · `T5_STRICT_PARITY=FAIL_7_OF_8_PRESERVED`.

**Bước thực hiện tiếp theo:** `TTM_T5_DUAL_ATTEST_WINDOWS_STATIC_QA_READBACK_AND_ONE_GUARDED_RELEASE_DECISION`. Một lần xác thực ZIP SHA/nguồn và chạy kiểm định tĩnh Python 3.12/PowerShell 5.1, rồi quyết định tích hợp về bản runtime mới có định danh/SHA riêng. Không mở thêm micro-gate. Không sửa `main`/`lineage.md`.

Nguồn API Windows: https://learn.microsoft.com/en-us/windows/win32/api/tcpmib/ns-tcpmib-mib_tcprow_owner_pid và https://learn.microsoft.com/en-us/windows/win32/api/tcpmib/ns-tcpmib-mib_tcp6row_owner_pid .

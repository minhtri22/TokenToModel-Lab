# TTM T2 V5 — Đọc lại độc lập lỗi C1083 và phạm vi phục hồi V5B (08/11/2026)

> Đây là bản tiếng Việt của [hồ sơ kỹ thuật V5 gốc](../../pilot/TTM_T2_V5_CMAKE_C1083_AND_V5B_RECOVERY_20261108.md), giữ nguyên trạng thái lúc đó. Các kết quả kiểm tra V5B/V5 tiếp theo có biên bản riêng; không sửa hồi tố lỗi đã xảy ra.

**Nguồn bằng chứng:** nhật ký cửa sổ lệnh (Console) Windows của chủ dự án; tệp `TTM_T2_V5_UTF8_AND_F16_MIXED_DIAGNOSTIC.json` đã được đối chiếu SHA; và tệp `cmake_1.log` đọc trực tiếp từ máy Windows bằng kết nối chỉ đọc (Read-only).

## Bằng chứng tại thời điểm V5

- Kiểm tra trước (Preview) V5 PASS; bộ chạy Python gọi `--mode preview` PASS. Lượt thực thi (Execute) V5 chỉ tạo thư mục `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\ttm_t2\v5_technical` và kết thúc bằng `STOP_RUNTIME_OR_BUILD`.
- SHA-256 báo cáo V5: `59763e6a153c9f917bb494247ba207b1394fc4c775932b5aba036d09cd6cb147`. Trạng thái `STOP_RUNTIME_OR_BUILD`, `runs=[]`, lỗi `V5_CMAKE_STEP_1_EXIT_1; see cmake_1.log`, `science_executed=false`, `gpu_used=false`. Tệp đính kèm được đối chiếu với SHA trong console.
- Nhật ký `v5_technical\cmake_1.log` hiển thị `llama.h(4,10): error C1083: Cannot open include file: 'ggml.h': No such file or directory`. Lỗi phát sinh ở bước biên dịch (Build) sau khi cấu hình (Configure) hoàn tất, **không phải** kết quả số học hoặc bộ tách token của V5.
- `CMakeLists.txt` V5 có đường dẫn tệp đầu (Include Path) `${LLAMA_SOURCE}/include` nhưng thiếu `${LLAMA_SOURCE}/ggml/include`, là nơi mã `ggml.h` nằm trong dự án nguồn. **Không có kết quả suy luận CPU, logits hoặc tokenizer hợp lệ mới từ V5.** Kết quả V4 vẫn được giữ nguyên: logits F32 PASS **8/8**, sai lệch tối đa **0.0008664 < 0.001**; tokenizer FAIL **4/9**, F16 gốc dừng do kiểu số hỗn hợp.

## Phương án V5B đã chuẩn bị ở thời điểm đó (chưa thực thi Windows)

- **Không chạy lại V5** hay ghi đè biên bản và hiện vật. Gói kế tiếp `TTM_SMALL4M_T2_V5B_CMAKE_HEADER_RECOVERY_20261108.zip`, SHA-256 `3C2284253D703FB7EFC7F1D53F7F97348BC811DBD63E5FB7E417D4FAEFF688EE`.
- `CMakeLists.txt` SHA-256 `2D1C2A0ABA4ABFBE265D9279D286E2618B7659DD791A93008EB267D49E58382C`: bổ sung `${LLAMA_SOURCE}/ggml/include`, kiểm `ggml.h` tồn tại, liên kết với `llama.lib` đã biên dịch. Không sử dụng `FetchContent`, `ExternalProject` hoặc biên dịch lại dự án nguồn (Upstream).
- Bộ thăm dò C++ (Native Probe) giữ byte và SHA của V5: `A9ADA1032A070FC8AB8198257A9BA41B034A05E1FE15DD97E3FCBDD51C6B4455`.
- Mã Python V5B có SHA-256 `1CA2E65DED24BD926CBD271003993F36BFDAD853F0709BDD8B44C76C09C1EEC4`: giữ nguyên **8** ca logits, **9** ca tokenizer và ngưỡng F32 `1e-3`, F16 hỗn hợp `2e-2`; thêm kiểm SHA báo cáo V5 và nhận dạng lỗi C1083. Kết quả chỉ được phép ghi vào `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\ttm_t2\v5b_technical`, không ghi đè (No-overwrite).
- Bộ chạy PowerShell có SHA-256 `1217553E8A7680434431DDA54CC059855C444DA1333949BD1D40F7BBBB73CEF4`: chuyển tham số `Preview/Execute` thành `preview/execute` khi gọi bộ phân tích đối số (Argparse), giữ khóa SHA và môi trường Python riêng (Virtual Environment) trên ổ D:.
- Kiểm thử tĩnh ngoại tuyến (Offline Static QA): **8/8 PASS**; biên dịch mã byte Python (Bytecode Compilation) PASS; kiểm tra ZIP, tính toàn vẹn và đọc lại PASS. **Lúc đó chưa thử động trên Windows PowerShell 5.1 hay chạy V5B native.**

## Phán quyết cổng (Gate)

`T2_V5_EXECUTION=CONSUMED_STOP_C1083` · `T2_V5_LOGITS=NOT_EXECUTED` · `T2_V5B_SOURCE_STATIC_QA=PASS` · `T2_V5B_WINDOWS=NOT_EXECUTED` · `T2_FULL=HOLD` · `SCIENCE_LOCK=NOT_GRANTED`.

**Bước tiếp theo ở thời điểm ghi:** xác minh SHA và cú pháp PS5.1, chạy V5B Preview chỉ đọc rồi Execute đúng một lượt trong thư mục mới, không tự chạy lại khi có tệp dở. Đọc báo cáo V5B để phân loại lỗi tokenizer, UTF-8 và F16, **kể cả khi kết quả là FAIL kỹ thuật**; chưa huấn luyện trên Colab.

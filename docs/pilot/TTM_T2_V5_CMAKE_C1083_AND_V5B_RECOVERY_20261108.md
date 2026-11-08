# TTM T2 V5 — C1083 independent readback and V5B scoped successor (2026-11-08)

**Nguồn:** console Windows của chủ dự án, file `TTM_T2_V5_UTF8_AND_F16_MIXED_DIAGNOSTIC.json` được đính kèm và đối chiếu SHA, cùng đọc trực tiếp `cmake_1.log` từ máy Windows qua kết nối chỉ đọc.

## Bằng chứng hiện tại

- V5 Preview đã PASS, direct driver Python `--mode preview` PASS; V5 execute tạo **duy nhất** thư mục `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\ttm_t2\v5_technical` và kết thúc `STOP_RUNTIME_OR_BUILD`.
- Báo cáo V5 SHA256 exact **`59763e6a153c9f917bb494247ba207b1394fc4c775932b5aba036d09cd6cb147`**, trạng thái `STOP_RUNTIME_OR_BUILD`, `runs=[]`, message `V5_CMAKE_STEP_1_EXIT_1; see cmake_1.log`; `science_executed=false`, `gpu_used=false`. Bộ đính kèm người dùng đã được so sánh với SHA console.
- Đọc trực tiếp `v5_technical\cmake_1.log` thấy `llama.h(4,10): error C1083: Cannot open include file: 'ggml.h': No such file or directory`. Đây là bước **CMake build** sau khi configure đã xong, không phải lỗi số học hay tokenizer V5.
- V5 `CMakeLists.txt` có include `${LLAMA_SOURCE}/include` nhưng thiếu `${LLAMA_SOURCE}/ggml/include`, nơi upstream `ggml.h` tồn tại. Không có T2 V5 logits/tokenizer/CPU inference outcome; V4 scientific state vẫn như cũ: F32 logits PASS 8/8 (max 0.0008664 < 0.001), tokenizer FAIL 4/9, F16 original STOP runtime mixed types.

## Phương án kỹ thuật V5B đã chuẩn bị (chưa chạy trên Windows)

- **Không chạy lại V5** hoặc ghi đè V5 receipt/artifact. Gói successor mới: `TTM_SMALL4M_T2_V5B_CMAKE_HEADER_RECOVERY_20261108.zip` SHA256 `3C2284253D703FB7EFC7F1D53F7F97348BC811DBD63E5FB7E417D4FAEFF688EE`.
- `CMakeLists.txt` SHA256 `2D1C2A0ABA4ABFBE265D9279D286E2618B7659DD791A93008EB267D49E58382C` — thêm include `${LLAMA_SOURCE}/ggml/include`, kiểm tra `ggml.h` tồn tại, liên kết đúng `llama.lib` đã biên dịch. Không `FetchContent`, `ExternalProject`, hay biên dịch lại upstream.
- C++ probe giữ byte/SHA từ V5: `A9ADA1032A070FC8AB8198257A9BA41B034A05E1FE15DD97E3FCBDD51C6B4455`.
- Python V5B SHA256 `1CA2E65DED24BD926CBD271003993F36BFDAD853F0709BDD8B44C76C09C1EEC4` — giữ 8 logits/9 tokenizer fixtures và ngưỡng F32 1e-3, mixed F16 2e-2; thêm khóa SHA V5 receipt và check log C1083; ghi kết quả **chỉ** `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\ttm_t2\v5b_technical` với no-overwrite.
- PowerShell runner SHA256 `1217553E8A7680434431DDA54CC059855C444DA1333949BD1D40F7BBBB73CEF4` — chuyển `Preview/Execute` thành `preview/execute` khi gọi argparse, khóa SHA nguồn, pin Python trong venv trên D:.
- Offline static tests **8/8 PASS**, Python bytecode compilation PASS, ZIP integrity/readback PASS. **Chưa kiểm thử PowerShell 5.1 động hoặc probe Windows V5B**.

## Gate

`T2_V5_EXECUTION=CONSUMED_STOP_C1083` · `T2_V5_LOGITS=NOT_EXECUTED` · `T2_V5B_SOURCE_STATIC_QA=PASS` · `T2_V5B_WINDOWS=NOT_EXECUTED` · `T2_FULL=HOLD` · `SCIENCE_LOCK=NOT_GRANTED`.

**Bước tiếp theo:** kiểm tra SHA và PS5.1 Parser trên Windows, chạy V5B Preview read-only, rồi đúng một Execute vào thư mục mới; không rerun sau partial artifacts. Đọc report V5B và tiếp tục phân loại tokenizer, UTF-8, F16 **kể cả nếu V5B có kết quả FAIL kỹ thuật**, không huấn luyện Colab.
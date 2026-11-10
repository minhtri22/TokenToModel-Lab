# TTM T5 — Kiểm tra tương thích nguồn Ollama tùy chỉnh

Ngày 2026-11-11 (UTC+7). Phạm vi Windows x64, CPU, GGUF F32 gốc. Kết luận `SOURCE_COMPATIBILITY=PASS` · `WINDOWS_TOOLCHAIN=NOT_RECHECKED` · `CUSTOM_BUILD=NOT_EXECUTED` · `OLLAMA_RUNTIME=NOT_EXECUTED`.

## Khóa nguồn và bằng chứng

| Thành phần | Giá trị |
| --- | --- |
| Ollama từng chạy T5 trên Windows | `0.40.14` theo `_tmp/ttm_t5_v5_imported_model_inference_only_v1/serve.log` ngày 2026-11-09 |
| Ollama source | `v0.40.14` / `9a3e8177767245acc62b735eba7d5d8a553606d0` |
| llama.cpp do Ollama pin | `b11963` / `39febd2adb947b70da35e95f9351b3bf58ad170a`, khớp tiền tố build `39febd2ad` trong log Windows |
| Blob GPT-2 trước vá | `d6ca64744f492733612d3854e869e42ce1d52774` |
| Blob GPT-2 sau vá | `430eed46a557f5004fb8a72e86f3152b06d95b6a` |
| Bản vá GELU SHA-256 | `47ef4854094d6b9db648cde7067a3d243b10ce632f0b58397e986110a7f62de2` |
| GGUF SHA-256 | `5bdc904e6c51af04a4223219f36e6bc2e687f60fd6e17dc24508f3eb7489e4e5` |
| Biên bản CPU tham chiếu SHA-256 | `af35a3e6a086d5c542d6c5751a54716dab2d2c56475335c09b370fe1e742bed1` |

[Khóa llama.cpp của Ollama](https://github.com/ollama/ollama/blob/9a3e8177767245acc62b735eba7d5d8a553606d0/LLAMA_CPP_VERSION) · [Biên bản CPU tham chiếu](https://github.com/minhtri22/TokenToModel-Lab/blob/d9625c87adb3ede28ad647905b004bbd9c0dbef9/artifacts/qa/ttm-t5-parity/TTM_T5_ISOLATED_CPU_QA_V2_RECEIPT_20261110.json) · [Bản vá GELU đã khóa](https://github.com/minhtri22/TokenToModel-Lab/blob/09652a13c9ae98f586acc3b58b3e8141205746c4/tools/pilot_t5/postmerge/ttm_gpt2_gelu_erf_ollama_b11963.patch)

## Đường biên dịch và nạp mô hình

1. Bộ dựng GPT-2 của `b11963` gọi `LLM_FFN_GELU` ở đúng một vị trí. Đổi sang `LLM_FFN_GELU_ERF` dẫn tới `ggml_gelu_erf` ở nhánh FFN tuần tự. Bản vá ảnh hưởng các mô hình GPT-2 chạy bằng binary tùy chỉnh, do đó phạm vi sử dụng là phiên bản thử nghiệm riêng với GGUF T5. [GPT-2 builder](https://github.com/ggml-org/llama.cpp/blob/39febd2adb947b70da35e95f9351b3bf58ad170a/src/models/gpt2.cpp#L118-L124) · [Graph operator](https://github.com/ggml-org/llama.cpp/blob/39febd2adb947b70da35e95f9351b3bf58ad170a/src/llama-graph.cpp#L2047-L2072)
2. Kiểm tra `git apply --check --index`, áp dụng và kiểm tra đảo cả bản vá tương thích đi kèm Ollama và bản vá GELU trên các tệp nguồn đã xác minh blob. Hook tương thích sửa model loader và CLIP. Bản vá T5 sửa duy nhất `src/models/gpt2.cpp`. Kết quả PASS trong bản sao scratch, phạm vi kiểm tra cú pháp bản vá và blob.
3. Với build gốc của Ollama, chuẩn bị cây llama.cpp đã áp dụng cả hai bản vá rồi truyền `-DFETCHCONTENT_SOURCE_DIR_LLAMA_CPP=<cây đã khóa>`. CMake gốc chuyển cây này xuống build con và đặt `OLLAMA_LLAMA_CPP_SKIP_COMPAT_PATCH=ON`. Tùy chọn đó giữ liên kết mã tương thích nhưng yêu cầu các hook đã có trên đĩa. Đường cấu hình CMake con qua biến môi trường `OLLAMA_LLAMA_CPP_SOURCE` đơn lẻ đi vào nhánh khác, có thể bỏ cả phần áp dụng và liên kết shim. [CMake gốc](https://github.com/ollama/ollama/blob/9a3e8177767245acc62b735eba7d5d8a553606d0/cmake/local.cmake#L133-L159) · [Cấu hình build con](https://github.com/ollama/ollama/blob/9a3e8177767245acc62b735eba7d5d8a553606d0/cmake/local.cmake#L452-L478) · [Liên kết shim](https://github.com/ollama/ollama/blob/9a3e8177767245acc62b735eba7d5d8a553606d0/llama/server/CMakeLists.txt#L125-L162)
4. Đặt `ollama.exe` và payload `lib/ollama/llama-server.exe` cùng các DLL bên trong gói riêng. Dùng đường dẫn tuyệt đối và xác nhận đường dẫn tiến trình runner thực tế trong log. Go module yêu cầu `1.26.10`, đường build CLI đặt `CGO_ENABLED=1`, CMake tối thiểu `3.24`. Trước khi build trên Windows cần xác minh Go, compiler hỗ trợ CGO và trình dựng native. [Tìm runner](https://github.com/ollama/ollama/blob/9a3e8177767245acc62b735eba7d5d8a553606d0/llm/llama_binary.go) · [Go module](https://github.com/ollama/ollama/blob/9a3e8177767245acc62b735eba7d5d8a553606d0/go.mod) · [Build Go CLI](https://github.com/ollama/ollama/blob/9a3e8177767245acc62b735eba7d5d8a553606d0/cmake/local.cmake#L711-L721)

## Điều kiện kiểm thử sau build

- Dùng thư mục build, payload, bộ lưu model và tệp tạm riêng trong TTM. Dùng cổng API loopback riêng được kiểm tra trước khi chạy. Khóa SHA-256 binary, payload và blob GGUF mà runner thực sự nạp.
- Đặt `OLLAMA_KV_CACHE_TYPE=f32`, `OLLAMA_FLASH_ATTENTION=false`, `OLLAMA_NUM_PARALLEL=1` và tùy chọn `num_gpu=0`, `num_thread=1`, `num_ctx=256`. Log tiến trình con cần ghi `--cache-type-k f32 --cache-type-v f32 --flash-attn off -ngl 0 -t 1 -c 256 -np 1`. Kiểm log context xác nhận kiểu K/V F32 và Flash Attention tắt sau khi nạp. [Truyền KV cache](https://github.com/ollama/ollama/blob/9a3e8177767245acc62b735eba7d5d8a553606d0/llm/server.go#L104-L117) · [Cờ runner](https://github.com/ollama/ollama/blob/9a3e8177767245acc62b735eba7d5d8a553606d0/llm/llama_server.go#L395-L450) · [Flash Attention](https://github.com/ollama/ollama/blob/9a3e8177767245acc62b735eba7d5d8a553606d0/llm/llama_server.go#L636-L662)
- Đối chiếu 9 mẫu mã hóa và giải mã qua runner. Sau đó chạy API Ollama ở chế độ `raw` với `Xin chào`, nhiệt độ 0, seed 42 và tối đa 8 token. Mốc CPU ghi nội dung `.`, token `[46, 256]` và EOS. Lưu riêng kết quả API công khai và dữ liệu runner để phân biệt đường nạp, tokenizer và hành vi sinh. Cặp revision llama.cpp khác lượt CPU đã PASS nên phép thử này phải dùng bằng chứng mới. Chứng cứ logits C01–C04 giữ nguyên phạm vi cũ.

**Bước thực hiện tiếp theo** `TTM_T5_CUSTOM_OLLAMA_CPU_BUILD_AND_ISOLATED_SMOKE`.

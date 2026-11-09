# TTM Q1/Q2 — Bổ sung giới hạn ngữ cảnh và cleanup sau readback

**Ngày:** 2026-11-09 · PR #13 · Không huấn luyện, không chạy TEST hay Ollama trong bước sửa nguồn này.

- Nguồn Python runner SHA256 cuối: `80a5fae1155e3680207318af0d218ce4050ad2e8f554db107cac31a0af4cd450`. Lời dẫn Q1 <=192 BPE tokens khi `num_ctx=256` và sinh tối đa 64; lời dẫn Q2 <=96 BPE tokens khi `num_ctx=128` và sinh tối đa 32. Kiểm tra trên tokenizer BPE2048 đã khóa, trước CLAIM; tránh so sánh context 128/256 mà prompt bị cắt.
- PowerShell SHA256 cuối: `361d4f6452e59d446ecc661f3520191956b61d0c407cf6b07c700f5665b93473`. Sau khi commit bằng chứng và **fresh clone GitHub đọc lại tất cả raw+manifest**, chỉ dọn `github_publish_checkout`, `github_readback_checkout` và bootstrap do batch tạo trong `_tmp`. Nếu cleanup thất bại thì ghi HOLD riêng, không xóa nguồn T5/V5 hay dữ liệu private.
- Test module giữ SHA256 `e24ea51b34008b21f188e01c30cda16fe50beb9008dc2a4fd1831906aad0db57`. Python compile PASS, unittest 10/10 PASS (Linux 3.13.5). **Windows PowerShell parse/preview và native 74 calls chưa thực thi**.
- Nguyên tắc: Main `b57b44e7287f842e81050c1faee337f636333dd0` không đổi; branch PR13 duy nhất; source GH trước runtime; không tạo model, không retry một-shot; `T5_STRICT_LOGITS=FAIL_7_OF_8_PRESERVED`.

**Bước tiếp theo:** dùng nguồn tại exact HEAD PR #13 sau khi đọc lại, chạy QA+Preview rồi **một** Execute; GitHub evidence readback và phân xử GO/REVISE/STOP bằng rubric khóa.

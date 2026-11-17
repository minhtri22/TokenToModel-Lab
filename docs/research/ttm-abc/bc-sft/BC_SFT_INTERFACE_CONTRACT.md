# BC — giao diện synthetic SFT B↔C (engineering-only)

**Operation:** TTM_PM_BC_SYNTHETIC_SFT_INTERFACE_QUALIFICATION_SINGLE_GATE  
**Trạng thái:** IMPLEMENTATION_CANDIDATE · AUTHOR_QA_PENDING · DISTINCT_QA_PENDING · NO_SCIENCE  
**B source:** 43896bcd034c82e8433bc6a2b53eefbd936616fb, Draft PR #34 (không sửa).  
**C source:** 185d465c31f5f4bef6220be95e39dac1ae81c5b8, Draft PR #35 (không sửa).  
**C independent review:** 9fac5a675955d8b91d6855d27907f239cbfb745f — PASS_DESIGN_SCOPED, 35/35, không đồng nghĩa B integration PASS.  
**PM handoff thực có trên GitHub:** b4cd629f624f53e24c9eb05120ffe649b664b05d, blob d75965a6787a1839f05bc01cf3f1071e0b8ba935. SHA được cung cấp trong URL của yêu cầu là b4cd629f624f53e24a9f4e2c62bb78b2b05d không tồn tại (GitHub 404); URL chính xác được xác nhận từ PM Issue #32.
**Nhánh riêng:** integration/ttm-bc-synthetic-sft-interface-20261116, base=exact B commit. Draft PR #36 base B branch, không chỉnh PR #34/#35/main/lineage.

## 1. Source boundary

- C oracle: tests/ttm_track_bc/c_m4_source_pinned.py là bản sao byte-identical của tests/ttm_track_c/synthetic_contract.py @185d465c, Git blob SHA-1 83c6d5abe0948c24c9e49375ffc2a17e3143a793, SHA-256 522618430f32fd0cc74da945a7bf208aad3a146c1f113a320a13e9490f9e2b88. Chỉ test, không ghi đè nhánh C.
- B adapter: src/ttm_track_b/bc_sft_interface.py là biến thể B-owned của role/mask parser C đã được review, thay namespace và byte-domain, bổ sung hash/schema/CPU QA. Code QA dùng chính P02 GPT và Track B cross_entropy_valid.
- P02.forward mặc định không hỗ trợ ignored labels: không sử dụng đường loss mặc định; truyền logits vào masked CE reduction=sum / tổng nhãn hợp lệ.

## 2. Noncolliding codec + template

| Token | ID | Semantics |
|---|---:|---|
| Byte content | 0..255 | Mỗi byte nguyên gốc là một ID; KHÔNG phải real BPE |
| EOS | 256 | Một lần cuối dialogue |
| PAD | 257 | Chỉ right-pad, target ignore |
| BOS | 258 | Dialogue begin |
| SYS | 259 | Header system tùy chọn, chỉ ở đầu |
| USER | 260 | Header user |
| ASSIST | 261 | Header assistant |
| EOT | 262 | Turn end, assistant EOT là target hợp lệ |

Vocab P02 không đổi 2048. Không tráo T4/P01 tokenizer. CODEC_SHA256 và TEMPLATE_SHA256 là hash canonical JSON được versioned. Byte values 0..6 phải được diễn giải như content B, tuyệt đối không phải delimiter của C toy.

Grammar: BOS [SYS byte+ EOT]? (USER byte+ EOT ASSIST byte+ EOT)+ EOS. Một conversation/row; không packing, không left padding, không silent truncation; bounded wire tối đa 33 token, P02 context 32. Không chấp nhận caller-supplied flags như provenance: bản thấp hơn reparses toàn bộ grammar và so mọi bit; API B-facing tự sinh mask từ role-bearing messages. Đây là kiểm tra cấu trúc, KHÔNG bảo đảm người tạo dữ liệu khai đúng role hoặc có quyền source.

## 3. Shift/loss/gradient

Shift +1: input IDs = padded[:-1], target_i = padded[i+1] nếu assistant-content, assistant EOT hoặc final EOS; còn lại = ignore_index -100. Không có nhãn BOS/SYS/USER/ASSIST/PAD. Assistant loss được chia tổng số valid supervised targets, không chia tổng window/pad. So sánh oracle độc lập bằng log-softmax full 2048 logits. Cấm all-IGNORE.

Với system/user/header, direct CE logit gradient bằng 0, **không** yêu cầu gradient qua embedding prompt bằng 0; P02 causal attention cho phép assistant loss backprop qua context prompt. Dùng finite synthetic CPU P02 forward/backward không optimizer.step, không checkpoint weights. Causal future-token isolation và right-padding isolation được kiểm chứng riêng; left-padding, concatenated packing bị từ chối.

## 4. Synthetic pack, resume and source hashes

Schema mới: ttm.bc.synthetic.sft.pack.v1. Records có ID, TRAIN/VAL, messages toy byte, SHA256 source, shifted x/y, số target valid. Xác minh source hashes, group uniqueness, no cross-split same-source, exact reconstruction, pack/hash/config/codec/template pins. Legacy B byte pack schema ttm.track_b.synthetic.byte_windows.v1 REJECT.

Metadata-only resume schema ttm.bc.synthetic.sft.resume.v1: kiểm tra codec/template/model/pack exact hashes; mismatch phải FAIL_CLOSED. P04, T4 science và checkpoint B0/B1 cũ KHÔNG tương thích; không load/convert hoặc lưu weights, optimizer state. No actual SFT training, no GPU, no TEST64/FRESH16/FINAL24, no TinyStories, no real data.

## 5. B-G5 V3 incident preservation — NOT an SFT gate PASS

Owner V3 báo HOLD_NATIVE_QA tại job_memory_negative_EXIT_1; receipt SHA256 063bb5770c92881ab8fd0ae485f007026594495109c0c0b0359a0ba686c22188. Bản gốc phải bất biến. Script V3 gọi memory negative với 400MiB bytearray nhưng Job Object 256MiB; -ExpectNonZero true. Trong hàm Invoke-Guarded, exit=1 **được kỳ vọng**; chuỗi EXIT_1 trong exception chỉ là hậu tố, không xác định nguyên nhân. Các điều kiện khác gồm JobApplied, JobCapBytes đúng, TimedOut đúng, PeakJobCommitBytes không vượt cap, stdout/stderr không quá 64MiB. Script mới kiểm MemoryError stderr *sau* predicate thành công.

Thiếu nguyên bản PM_B_NATIVE_QA_RECEIPT.json, row phases[name=job_memory_negative], stdout/stderr và SHA readback của lượt V3 trong nguồn hiện truy cập. Không suy đoán vì sao predicate false, không sửa/khởi chạy lại native harness. B-G5 và B-G6 vẫn HOLD.

## 6. Acceptance

BC-0 source pins, review = PENDING_DISTINCT; BC-1 codec/mask = AUTHOR_QA_PENDING; BC-2 shifted/masked CE = AUTHOR_QA_PENDING; BC-3 CPU/causal = AUTHOR_QA_PENDING; BC-4 schema/resume negatives = AUTHOR_QA_PENDING; BC-5 owner native & distinct exact HEAD = HOLD_B_G5_G6.

Test matrix chạy CPU Py3.12 Linux/Windows CI, PyTorch CPU-only; 1 layer ×32 width ×32 context, batch 1, max 2 threads, 1 forward/backward, zero optimizer steps. CI timeout 15 phút không thay thế hard memory limit chủ máy. Không nâng C-G1/C-G2/C-G8 hoặc B-G5/B-G6.

**Bước tiếp theo duy nhất:** TTM_BC_EXACT_INTEGRATION_HEAD_DISTINCT_NEGATIVE_QA_AND_B_G5_V3_LOG_ADJUDICATION_ONEPACK.

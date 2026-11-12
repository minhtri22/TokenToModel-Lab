# TTM-Small-4M — EXPLORATORY DEV32: quyết định owner GO độc lập D1 confirmatory

**Ngày:** 12/11/2026  
**Operation:** `TTM_SMALL4M_D1_POST_FINGERPRINT_ONE_OWNER_EXPLORATORY_DEV_RUN_DECISION`  
**Quyết định:** **`GO_EXPLORATORY_DEV32_CPU_ONLY_ONE_SHOT`**.  
**Loại:** `EXPLORATORY_SCOPED` — độc lập về quyết định thực thi và diễn giải, không hạ chuẩn D1 confirmatory.

## 1. Nguồn và lựa chọn đóng băng trước chạy

- D1 V2 raw SHA-256 `f381ae8ab9c67c8590092f85445ab2fbe95a3b1c6a646ec18ee26b6b13ac92b8` — chỉ dùng 16 family × 2 fact, tại `length=short`, `distance=near`, tương ứng **32 prompt**. Theo thứ tự `family_id` tăng dần rồi `condition=A/B`. Không biên tập văn bản hoặc tạo prompt mới.
- Chọn 1 neutral prompt tương ứng `short/near` cho mỗi family, tổng 16 neutral, từ **chính V2**.
- Checkpoint chỉ **step1024**, SHA-256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`; model P02 blob `9762343e06cf800b50574c2871ae1ed58537fb18`, 3.749.376 tham số; T1 BPE manifest file SHA-256 `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc`. P02 2048 vocab, context 256. Không update weight/config, không dùng GPU.
- Fingerprint DEV192×historical152 đã chạy: private index SHA-256 `66a987550fdeb5b6ff3711d49ab673578be68418a1978b33126f6127deed763c`, summary SHA-256 `7f27c8f9226ff333b61e1fd08dc140424c76aef2ea5ab1f0baaf9a751739ada7`. So sánh exact 0/29184 và 0 cờ lexical, **chỉ PASS_SCOPED**.

## 2. Phép đo trong **một** lượt thực nghiệm

**Teacher-forced:** 16 family × (xA/yA, xA/yB, xB/yA, xB/yB, x0/yA, x0/yB) = **96 candidate scores**. Lấy trung bình log probability theo token của answer, không sinh token trong phép này. Với `ell(y|x)` là mean log-probability:

- `mA = ell(yA|xA) - ell(yB|xA)`
- `mB = ell(yB|xB) - ell(yA|xB)`
- `d0 = ell(yA|x0) - ell(yB|x0)`
- `mA_adj=mA-d0`, `mB_adj=mB+d0`.
- Báo `S` = số family cả `mA>0` và `mB>0` (trên 16), `S_adj` tương tự, mean positive/negative margins theo bốn category. **Không áp ngưỡng D1 confirmatory hoặc tuyên bố thống kê nhân quả.**

**Free running:** với 32 prompt trên:
- 32 greedy argmax, dừng EOS ID256, tối đa **32 token mới mỗi bản**.
- 32 nucleus top-p=0.9, temperature=0.8, chỉ dùng **seed nucleus đầu tiên trong manifest V2** (không sinh lại/tìm seed thuận lợi). Rút mẫu theo thứ tự prompt đã khóa bằng cùng một torch CPU generator; cap 32 token, EOS ID256.
- Tổng **64 văn bản**, tối đa 2.048 token mới. Đầu ra sinh lưu private; số token, tỉ lệ EOS/repetition và hash được tổng hợp an toàn. **Không tự chấm bằng mapping**.
- Tạo gói **BLIND64**: chỉ `opaque_id`, `prompt_text`, `generated_text_only`; không chứa family, condition, decoder, seed, expected continuation hay danh tính mô hình. Giao cho một phiên ChatGPT khác chấm theo rubric 0–3 của handoff (mở rộng 64 bản), khóa score SHA-256 trước nối lại nhãn để phân tích.

**Phạm vi diễn giải:** chỉ là tín hiệu DEV32 short/near 1 seed; không được suy rộng về long/far, ba seed, 512 outputs, confirmatory success, hay decoder rescue bền vững. Điểm teacher-forced không thay thế điểm rollout blind.

## 3. Điều kiện thực thi một lần

- CPU FP32 Windows + Python 3.12, packages `torch` và `regex`; RAM available ≥8 GiB, checkpoint/BPE hash exact, Python/P02 source pinned.
- Thực thi one-shot local dưới `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\TTM_D1_EXPLORATORY_DEV32_ONE_SHOT_20261112`, **không ghi đè**. Nếu thiếu điều kiện, dừng an toàn (HOLD infrastructure); không sửa một phần rồi tự tái chạy. Tạo outputs sau preflight source, không dùng train/TEST/Q1Q2, không optimizer, không paid API/GPU.
- Private raw/mapping, blind text và các câu trả lời đều giữ local, GitHub chỉ nhận source code, aggregate số liệu và SHA receipts. Không công khai prompt text, generated texts, per-record score, seed hoặc mapping.

## 4. Phân định GO

`GO_EXPLORATORY_DEV32_CPU_ONLY_ONE_SHOT` được owner phê duyệt trong chat; **không phải** `GO_D1_512_CONFIRMATORY`. Do đó các HOLD đã công bố về nonoverlap với nguồn niêm phong TEST/Q1Q2 vẫn đúng cho D1 confirmatory. Quyết định này không sửa phạm vi/threshold của thiết kế đã khóa mà mở một hoạt động exploratory riêng. Không cần chữ ký hoặc micro-permit.

**Kết luận hiện hành:** `DEV32_SCOPE_GO=YES` · `D1_CONFIRMATORY_512=HOLD` · `D1_DEV_FINGERPRINT=PASS_SCOPED` · `TEST_Q1Q2=SEALED` · `INFERENCE=NOT_YET_EXECUTED` · `TRAINING=NO`. `lineage.md` giữ nguyên; chỉ đánh giá ghi nhận lineage sau science thực và phân xử scoped.

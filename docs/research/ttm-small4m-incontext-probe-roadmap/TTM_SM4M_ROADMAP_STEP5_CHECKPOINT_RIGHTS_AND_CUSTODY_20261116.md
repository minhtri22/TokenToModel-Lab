# Bước 5 — Xác minh quyền và custody checkpoint (AD-01C/E6)

**Trạng thái:** `DESIGN_PROPOSAL_NOT_AUTHORIZED · SOURCE_ONLY · NO_MODEL_RUN · NO_TRAINING · LINEAGE_UNCHANGED`  
**Ngày:** 2026-11-16 · **Repository:** `minhtri22/TokenToModel-Lab` · **Main được đối chiếu:** `f7a0a5874e8fd895c8ea8d17ceff393a4d4917a3` (PR #27).  
**Tác giả:** Claude (AI), soạn theo yêu cầu của chủ repo trong một phiên trò chuyện. **Review độc lập: `NOT_PERFORMED`.** Mọi ngưỡng, cỡ mẫu và ngân sách dưới đây là **đề xuất của tác giả bản nháp**, chưa dựa trên dữ liệu đo và chưa được đóng băng.  
**Quan hệ với quản trị hiện hành:** `docs/governance/ACTIVE_RESEARCH_GATE.md` ghi `NO_NEW_BRANCH_AUTHORIZED` và `TTM-SM4M-DIAG-Q001` ở `Q1_REGISTERED_SOURCE_ONLY`. Nhánh chứa tài liệu này được tạo theo yêu cầu trực tiếp của chủ repo; việc nó có trở thành Question Gate, amendment của DIAG-Q001 hay bị bỏ là **quyết định của owner**, không được suy ra từ sự tồn tại của nhánh. Tài liệu này không cấp quyền truy cập checkpoint, không cấp quyền chạy mô hình và không thêm mục vào `lineage.md`.

**Lộ trình 5 bước (mỗi bước một tài liệu):**
1. Probe teacher-forced trên checkpoint nguyên bản (tài liệu STEP1)
2. Đối chứng random-init và hai checkpoint 1024/1280 (STEP2)
3. Sửa thang đo trước khi train thêm (STEP3)
4. Tách data / objective / capacity (STEP4)
5. Xác minh quyền và custody checkpoint, chạy song song (STEP5)

---

## 1. Vì sao là bước đầu tiên về mặt phụ thuộc

Cả STEP1 lẫn STEP2 đều cần mở checkpoint. `docs/governance/ACTIVE_RESEARCH_GATE.md` ghi `checkpoint_model_rights = AD00_AD01C_E6_NOT_VERIFIED` và `execution_permit = NO`. Không có bước này thì mọi bước dùng checkpoint đều bị chặn. Bước này **không đòi chạy mô hình** và có thể thực hiện song song.

## 2. Những gì repo đã biết (đã đọc) và những gì chưa

**Đã ghi trong repo:**
- Dữ liệu nguồn: TinyStories (`roneneldan/TinyStories`) tại revision `f54c09fd23315a6f9c86f9dc80f725de7d8f9c64`, giấy phép công bố **CDLA-Sharing-1.0** (xác minh bởi QA tác giả trên nhánh `docs/ttm-small4m-model-card-dataset-rights-20261109`, `PASS_24_OF_24` ở mức kiểm tra tài liệu).
- Trọng số M1024 và M1280: ma trận quyền ghi là "trọng số TTM tự train từ đầu, không dùng pretrained checkpoint", trạng thái phát hành công khai **HOLD**, điều kiện mở: owner chọn license cho weights, kiểm toán ghi nhớ/privacy, phân loại Results-vs-Data.
- Chính QA đó ghi: `legal_reviewer = NOT_PERFORMED`, `PII_or_memorization_audit = NOT_PERFORMED`, `model_product_readiness = NO`, `code_license = UNDECLARED_MAIN_ROOT`.
- Hash đã ghi: M1024 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b` (45.074.891 byte, lineage L0011); M1280 `ee723407b2c25a18be20e26387a3dd8e4a18e2942d469279b6f0748ff86af0dc` (manifest tái lập trên cùng nhánh). Các SHA này "không chứng minh quyền công bố".

**Chưa có / chưa xác minh trong phạm vi đã đọc:** byte của hai checkpoint trên máy sẽ chạy; vị trí lưu trữ và quyền truy cập hiện hành; kết luận pháp lý của người có thẩm quyền; kiểm toán ghi nhớ; chứng nhận của owner cho đúng phạm vi mới.

## 3. Hai câu hỏi cần tách

Tài liệu quyền của repo chủ yếu nói về **công bố** (release): dữ liệu thô, truyện đã chọn, merges, weights, GGUF đều `HOLD` cho việc đưa lên công khai. Việc **chạy suy luận cục bộ trên trọng số riêng của owner, không phân phối lại** là một câu hỏi khác. Theo diễn giải thận trọng ngay trong ma trận quyền, giấy phép cho phép dùng dữ liệu theo điều khoản và nghĩa vụ ở mục 3 của CDLA áp dụng khi **phân phối** Data/Enhanced Data. Vì vậy có khả năng AD-01C chỉ cần được chứng nhận cho phạm vi "suy luận cục bộ, không công bố trọng số, không đưa dữ liệu hay logits thô ra ngoài".

Đây là **diễn giải của tác giả bản nháp dựa trên tài liệu repo, không phải tư vấn pháp lý**. Người có thẩm quyền (owner, và luật sư nếu owner muốn) phải xác nhận.

## 4. Danh mục kiểm tra (không cần chạy mô hình)

### 4.1. Chain of custody của byte
- [ ] Vị trí lưu trữ riêng tư hiện tại của từng checkpoint (M1024, M1280; tùy chọn M256/M512/M768) và người có quyền truy cập.
- [ ] SHA-256 và độ dài tệp tính lại trên **đúng bản sao** sẽ dùng, bằng lệnh chỉ đọc (repo đã có ví dụ `Get-FileHash` trong manifest tái lập).
- [ ] So với hash đã ghi. Sai khác thì `HOLD_CUSTODY`, không chọn tệp khác.
- [ ] Sao chép sang máy chạy là bản sao có kiểm hash; ghi ngày, người thực hiện.

### 4.2. Cấu trúc và nguồn gốc bên trong tệp
- [ ] Mở bằng `torch.load(weights_only=True, map_location='cpu')`; không tắt chế độ an toàn.
- [ ] Kiểm các trường nhúng: `p02_git_blob` (kỳ vọng `9762343e06cf800b50574c2871ae1ed58537fb18`), cấu hình (2048/256/256/4/4), số bước (1024 hoặc 1280), và nạp `strict=True`.
- [ ] Đối chiếu chuỗi nguồn: trainer `tools/pilot_t4/a2_continuous1024/t4_train_science_a2.py` (blob `76c4d0155cd0736919f41682f240b47ad3d7c428`), hash JSON cuối, khóa science và dữ liệu riêng tư đã ghi ở lineage L0011.

### 4.3. Quyền (AD-01C) theo phạm vi cụ thể
- [ ] Owner xác nhận bằng văn bản: phạm vi sử dụng (suy luận forward cục bộ, probe teacher-forced, không phân phối, không công bố logits thô).
- [ ] Ghi rõ **cả hai** SHA (M1024 và M1280) và các mốc tùy chọn đưa vào phạm vi; DIAG-Q001 hiện chỉ ghim M1024.
- [ ] Nêu giả định về giấy phép dữ liệu nguồn (CDLA-Sharing-1.0, revision đã ghim) và việc không có phân phối lại.
- [ ] Nêu rõ nội dung nào vẫn `HOLD` (công bố weights, GGUF, merges).
- [ ] Ghi `legal_reviewer` là có hay không, và ai chịu trách nhiệm quyết định.

### 4.4. Custody của runner và đầu ra (E6)
- [ ] Hash của runner, fixture và tokenizer được ghim trước khi chạy.
- [ ] Đầu ra riêng tư (logits thô, fixture) ở máy riêng; chỉ bản tóm tắt không nhạy cảm lên GitHub.
- [ ] Không đưa checkpoint, dữ liệu nguồn hay token pack lên GitHub (đúng ma trận quyền).
- [ ] Không dùng TEST64, FINAL24 và các tập đã tiêu thụ.

### 4.5. Dữ liệu mới cho STEP4
- [ ] Quyền chọn tập con TinyStories mới, huấn luyện cục bộ từ nó, và xử lý trọng số dẫn xuất mới: quyết định riêng; không suy ra từ chứng nhận cho M1024/M1280.
- [ ] Phân loại Data/Enhanced Data/Results nếu có kế hoạch công bố sau này (mục R1–R4 của ma trận quyền).

## 5. Mẫu chứng nhận của owner (khung, không phải văn bản pháp lý)

```
CheckpointAttestation
- Ngày, người chứng nhận, vai trò
- Hiện vật: tên, SHA-256 (tính lại), độ dài, vị trí lưu trữ
- Phạm vi được phép: suy luận cục bộ forward-only trên máy [ghi rõ]
- Điều bị loại trừ: phân phối lại, công bố, GGUF, logits thô
- Giả định nguồn dữ liệu: TinyStories revision f54c09fd..., CDLA-Sharing-1.0
- Người có thẩm quyền xác nhận: [owner / legal / chưa có]
- Trạng thái: AD-01C = VERIFIED_FOR_LOCAL_INFERENCE_ONLY | HOLD
- Hạn hiệu lực và điều kiện thu hồi
```

## 6. Đầu ra và tiêu chí quyết định

| Kết quả | Hệ quả |
|---|---|
| Hash khớp, cấu trúc khớp, owner chứng nhận phạm vi cục bộ | `AD-01C = VERIFIED_FOR_LOCAL_INFERENCE_ONLY` cho đúng các SHA đã nêu; STEP1–STEP2 có thể được xem xét (vẫn cần owner GO riêng) |
| Hash lệch hoặc tệp thiếu | `HOLD_CUSTODY`; không thay checkpoint |
| Owner không thể chứng nhận phạm vi | `HOLD_RUN`; STEP1–2 chỉ chạy được phần không cần checkpoint (random-init) |
| Cấu trúc nhúng không khớp | `HOLD_SOURCE_MISMATCH` |

Chứng nhận này **không** là bằng chứng khoa học và không mở quyền chạy tự động.

## 7. Điểm yếu và giới hạn

- Tác giả bản nháp không phải người có thẩm quyền pháp lý; mục 3 là diễn giải.
- Không đọc được byte checkpoint nên mọi hash ở đây là hash đã ghi, không phải hash đã tính lại.
- Tài liệu quyền của repo là QA tác giả (không có thẩm định pháp lý) và có từ 09/11/2026; phải kiểm trạng thái hiện hành trước khi dựa vào.
- Chứng nhận cho suy luận cục bộ không giải quyết câu hỏi công bố sau này.

## 8. Việc cần làm ngay (không cần quyền chạy mô hình)

1. Owner xác định vị trí và người giữ các checkpoint.
2. Tính lại hash trên bản sao sẽ dùng và đối chiếu.
3. Quyết định có cần ý kiến pháp lý cho phạm vi "suy luận cục bộ" hay owner tự chứng nhận.
4. Điền khung chứng nhận ở mục 5 và đưa vào gói quyết định GO/HOLD của DIAG-Q001 hoặc của câu hỏi riêng.

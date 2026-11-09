# HANDOFF — Codex reviewer độc lập cho TTM-Small-4M FRESH12

**Nhiệm vụ:** `TTM_SMALL4M_FRESH12_INDEPENDENT_REVIEWER_ATTESTATION_THEN_SINGLE_BATCH_INFERENCE`  
**Ngày lập:** 2026-11-09  
**Trạng thái tại handoff:** `FRESH12_PREREG=FROZEN` · `INFERENCE=0/48` · `REVIEWER=NOT_IDENTIFIED` · `PR13=DRAFT_HOLD`. Không suy đoán rằng đã có dữ liệu chấm.

## 1. Kho và các nguồn chuẩn

- GitHub: https://github.com/minhtri22/TokenToModel-Lab
- Main đã được xác minh lúc lập handoff: `b57b44e7287f842e81050c1faee337f636333dd0`.
- Nhánh canonical đánh giá: `research/ttm-small4m-q1q2-quality-single-batch-20261109`; HEAD lúc lập handoff sẽ thay đổi khi tài liệu này được commit. Không lấy SHA lịch sử làm HEAD hiện tại; **đọc lại HEAD/refs trước mọi ghi**.
- PR #13: https://github.com/minhtri22/TokenToModel-Lab/pull/13 (draft, merge HOLD).
- Thư mục local Windows dự án duy nhất: `D:\WORK\RESEARCH\TokenToModel-Lab`. Python 3.12 có tại `C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe`; PowerShell 5.1.
- GitHub Source of Truth: [sổ mục lục](README.md), [FRESH12 protocol/rubric](../../../artifacts/qa/ttm-original1280/fresh12/TTM_SMALL4M_FRESH12_PUBLIC_PREREG_GITHUB_CANONICAL_20261109.json), [readiness QA](../../../artifacts/qa/ttm-original1280/fresh12/TTM_SMALL4M_FRESH12_READINESS_SCOPED_QA_20261109.json), [CSV reviewer template](../../../artifacts/qa/ttm-original1280/fresh12/REVIEWER_SCORE_TEMPLATE_20261109.csv) và [mẫu attestation chưa ký](TTM_SMALL4M_FRESH12_INDEPENDENT_REVIEWER_ATTESTATION_TEMPLATE_20261109.md).
- Tránh đọc các báo cáo A/B đã giải mù ở các lượt trước khi ở **vai trò chấm**; chúng chứa thông tin có thể thiên lệch đánh giá. Nhiệm vụ chấm chỉ nhận packet vô danh chuyên biệt, mô tả dưới đây.

## 2. Phân vai bắt buộc; không tự nhận độc lập

**A — Executor / custodian (không phải reviewer):**
1. Kiểm tra lại chính xác GitHub HEAD, manifest, checkpoint 1024 SHA256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`; checkpoint 1280 SHA256 `ee723407b2c25a18be20e26387a3dd8e4a18e2942d469279b6f0748ff86af0dc`; mã P02 Git blob `9762343e06cf800b50574c2871ae1ed58537fb18`; BPE2048 merges SHA `aea0e2a1a1bc1943f20b767ba2f879e3a47f0cb43b8b66026b1a34a038e014af`.
2. Chỉ khi có **người chấm độc lập cam kết nhận việc**, chạy **một** lượt 48 phần tiếp nối: 12 prompt F01–F12 × 2 checkpoint × 2 dạng prompt, decoder `greedy`/argmax, tối đa 64 token, EOS=256, seed ghi như prereg. Hai điều kiện chỉ khác một ký tự dấu cách U+0020 cuối prompt. Không huấn luyện, không TEST, không Q1/Q2, không sửa checkpoint/dữ liệu.
3. Kiểm tra văn bản/token IDs và SHA trước khi chuẩn bị reviewer packet. 24 cặp A/B cân bằng 12/12 tổng, 6/6 riêng từng checkpoint. Trong packet gửi reviewer, chỉ gồm `pair_id, prompt_clean, output_A, output_B` với **biểu diễn whitespace đầu thống nhất**; *không* kèm nhãn checkpoint, điều kiện, token IDs, phân bố xác suất, khóa giải mù, kết quả thí nghiệm cũ.
4. Giữ mapping plaintext và khóa giải mã **riêng tư**, không commit vào repository GitHub **public**. GitHub có encrypted escrow metadata, không có AES decryption key; kiểm toán bởi SHA/hợp đồng. Giữ chứng cứ raw riêng tư nguyên byte theo chính sách dự án.

**B — Codex reviewer độc lập (chính là nhiệm vụ handoff này):**
1. Xác nhận bằng văn bản trước khi xem packet: không tham gia tạo prompt, chọn model, chạy sinh/gom dữ liệu hoặc có mapping A/B. Nếu đã thấy key/condition labels, **STOP / `REVIEWER_BLINDING_FAIL`**, bàn giao cho người chấm khác.
2. Không chạy inference, không sửa model, không mở TSV/JSON checkpoint, không đọc legacy Q1/Q2/TEST, không cố giải mã escrow. Reviewer **không tự sinh packet**, không gọi công cụ xử lý mapping.
3. Nhận **chỉ** packet mới đã ẩn nhãn và rubric đã khóa; chấm riêng A và B theo 3 trục 0–3, số nguyên: bám prompt, mạch lạc, nhất quán. Không cộng điểm vì không có newline đầu, không đoán thứ tự A/B từ khoảng trắng; chấm phần văn bản *được sinh*, không chấm prompt.
4. Hoàn thành **144 điểm thành phần** = 24 cặp × 2 output × 3 trục, kèm nhận xét cụ thể để người khác có thể tái kiểm. Không tự tạo cột `trimmed`, `baseline`, `step1024` trong phiếu chấm.
5. Khóa SHA-256 của CSV A/B và biên bản `AI_REVIEWER_ATTESTATION` (ghi rõ **Codex AI reviewer, không phải con người**). Nếu dùng subagent, bắt đầu phiên **không thừa hưởng ngữ cảnh giải mù**; không khẳng định subagent là phản biện bên thứ ba tuyệt đối. Sau khi commit SHA + chứng cứ chấm lên nhánh được chủ dự án duyệt, **STOP**. Không giải mù trong phiên chấm.

**C — Post-score unblinder (tách khỏi reviewer):**
Sau khi có receipt SHA **bất biến trên GitHub**, chủ dự án/custodian mới sử dụng khóa cá nhân để giải mã AES-256-GCM, đối chiếu seed SHA, tái dựng mapping SHA và tính `trimmed−baseline` theo các ngưỡng được khóa trước. Không thay đổi số điểm sau unblind. Không sửa `lineage.md` nếu chưa có khoa học PASS/FAIL được thẩm định đúng phạm vi.

## 3. Tiêu chí FRESH12 đã đóng băng (không sửa hậu nghiệm)

- 12 prompt mới, 2 checkpoint T4 gốc, greedy thống nhất, 24 cặp; băm dữ liệu/biên bản nguyên gốc theo JSON prereg GitHub.
- Primary: Δ trung bình **prompt adherence** trên 24 cặp. Candidate improvement cần đồng thời: Δ ≥ **+0.5/3**, trimmed thắng rõ ≥**16/24** cặp; Δ adherence riêng từng checkpoint không âm; Δ coherence và consistency ≥ **−0.25/3** từng trục; bootstrap theo **12 cụm prompt** có CI95 lower >0; A/B 12/12 và **reviewer nhận việc độc lập / chấm trước giải mù**.
- Nếu reviewer không sẵn sàng, packet không đủ 24 cặp hoặc bị lộ nhãn: `HOLD`. QA tính toán đạt không tương đương `SCIENCE_PASS` hay chứng minh người chấm là con người.
- Reviewer không có quyền đơn phương sửa ngưỡng hoặc mở TRAIN/TEST.

## 4. Bảo toàn dự án và vùng ghi

- Không merge PR #13, không sửa `main` hoặc `lineage.md` trong bước reviewer; không force-push, không xóa worktree/nhánh/lịch sử.
- Mọi thao tác ở máy Windows và worktree phụ chỉ trong `D:\WORK\RESEARCH\TokenToModel-Lab`; từ chối symlink/junction vượt ranh giới. Thu thập script/receipt trong project root; tránh ghi `C:\` root, không cài lại môi trường ngoài phạm vi.
- Không làm lại 32 đầu ra ablation cũ, Q1/Q2 đã tiêu thụ hoặc T4 training. Không biến kiểm toán kỹ thuật nhỏ thành nhiều yêu cầu cấp phép; chỉ một lần xác nhận người chấm + một batch đã khóa theo đúng phạm vi.
- Repo GitHub hiện công khai. **Không gửi khóa riêng** `OWNER_PRIVATE_DECRYPTION_KEY_DO_NOT_GITHUB.json` (SHA256 `36ee3b169f507dabe85fa902c6c0a1963bee0973cd334cc79c57d5d8fe929ca7`) cho reviewer hoặc lên GitHub. SHA đủ dùng để xác định bản sao của owner.

## 5. Kết thúc hữu hạn và điều kiện chờ

- Nếu nhận handoff **trước khi có 48 đầu ra/packet**: chỉ kiểm tra tư cách reviewer và protocol. Ghi `HOLD_PACKET_NOT_YET_AVAILABLE`, không tự claim đã chấm.
- Nếu đã có packet nhưng người chấm từng xem key/nhãn: `HOLD_BLINDING_COMPROMISED`.
- Nếu reviewer hoàn thành: phát hành `REVIEWER_SCORE_FROZEN_SHA256`, `REVIEWER_AI_ATTESTATION`, `REVIEW_COMPLETE_BEFORE_UNBLIND`; bàn giao lại chủ dự án để giải mù bằng khóa cá nhân.
- Luôn báo cáo **trạng thái thực** (PASS/HOLD/FAIL kỹ thuật) với GitHub HEAD, SHA256 files, phạm vi quyền và các mục chưa thực hiện. Không tự nhận kết quả trong tương lai.

**Bước thực hiện tiếp theo khi agent rảnh:** tạo phiên Codex riêng, chấp nhận vai trò `REVIEWER_ONLY`, xác nhận chưa xem mapping, rồi nhận packet A/B sau khi executor hoàn tất 48 đầu ra. Nếu chưa có packet, trả `HOLD_PACKET_NOT_YET_AVAILABLE` chứ không mở science.

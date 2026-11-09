# TTM × SIX — Nhánh nghiên cứu chuyển giao biểu diễn liên mô hình

**Ngày thiết lập:** 2026-11-09  
**Trạng thái:** `DESIGN_ONLY / UPSTREAM_PINS_RECORDED / NO_SCIENCE_RUN`  
**Kho đích:** https://github.com/minhtri22/TokenToModel-Lab  
**Nhánh:** `research/ttm-six-cross-model-representation-transfer-20261109`  
**Commit gốc (exact main snapshot):** `1a9d8cba56564d6d36257fe95c34f2fd52c4f48a`  
**Kho nguồn SIX:** https://github.com/minhtri22/CLDP (các nghiên cứu SIX được quản lý trong kho CLDP; không tồn tại kho `minhtri22/SIX` đã xác minh).

## 1. Quyết định phân tách nghiên cứu

- Tuyến `main` của TTM và nhánh pilot `research/ttm-small-4m-colab-pilot-prereg-20261108` tiếp tục TTM-Small-4M theo ADR-0001. PR #12 vẫn là bản nháp tại thời điểm xác minh; **không merge, đổi base hay can thiệp**.
- Nhánh mới chỉ nghiên cứu giả thuyết: liệu thông tin trong biểu diễn nội bộ (internal representations) của mô hình nguồn mở có thể chuyển sang TTM nhỏ, tạo lợi ích đo được **sau khi bỏ mô hình nguồn khỏi đường suy luận**?
- Chưa thay kiến trúc hoặc mã huấn luyện TTM, không mở thêm P09/P10; giữ nguyên P00–P12, P07 PAUSED, bằng chứng lịch sử và các kết quả FAIL.
- Không thay đổi kho SIX và không sao chép trọng số, dữ liệu thô, checkpoint hoặc tài liệu chứng cứ sang TTM khi chưa kiểm tra quyền, dung lượng và nguồn gốc. Ghép nối các dự án chỉ bằng tham chiếu **commit bất biến**, không theo đầu nhánh di động.
- `lineage.md` (TTM và SIX) được giữ nguyên. Chỉ bổ sung kết luận khoa học sau khi có thực nghiệm và thẩm định; lỗi hạ tầng/QA đi vào biên bản kỹ thuật riêng.

## 2. Các kết quả SIX ghim theo đúng nguồn

| ID | Tham chiếu SHA cố định trong `minhtri22/CLDP` | Kết quả đã ghi trong nguồn | Ranh giới cần bảo toàn |
|---|---|---|---|
| SIX-R0-PARENT | `32c528104c4d16eddb0d8ba094e5d117234ba524` | `FORMALLY_CLOSED`; đóng băng R0 dựa trên kết quả `BASIS15` và commit nguồn bên dưới | Đây là mốc hội tụ tài liệu, **không phải** bằng chứng chuyển giao giữa LLM |
| SIX-REP-INFO | `2fc30fba568fd3782d32fd9cb3caa172d26f7853` — `research/lineage.md` | `PHI8_ORACLE`, `FULL_RESPONSE576`, `BASIS15` đều PASS 5/5 seed ở bài toán đã khóa; BASIS15 held-out median NRMSE = 0.141100; independent QA PASS | `IDENTITY16` cũng PASS; không chứng minh BASIS15 cần thiết, duy nhất, hay đủ với Qwen/TTM |
| SIX-ORACLE-COMPETENCE | `a9d9ceb33fbbc7ad2ed3fd495cb1e7b0917a7f02` | `CLOSED_PASS_ADJUDICATED`, oracle composition learner qualified (seeds 91–95) | Chỉ đánh giá họ learner và bài toán đã đóng băng; không tái chạy seed |
| SIX-COMPOSITION-NEGATIVE | `9ef06b141bdd0fb42255f361e426b2359bb0a84e` — `research/lineage.md` | Learned functional basis PASS nhưng held-out composition FAIL 0/5, kết luận tổng thể `INCONCLUSIVE` | Không được diễn dịch thành giả thuyết mọi biểu diễn chung bị bác bỏ |
| SIX-BASIS-QUALIFICATION | `1d9f91b6562410c4c62f90010f8cf5cb144cc15f` — `research/lineage.md` | Exact basis reconstruction tốt nhưng hai learner competence FAIL; `INCONCLUSIVE` | Đây là giai đoạn trước positive-control learner đủ năng lực; không coi là chứng minh BASIS15 thiếu thông tin |
| SIX-OW1-SHIFT | `9720ef5671990479db86fee7af8668d389f3bd30` | `FORMALLY_CLOSED_FAIL_ADJUDICATED`; trực tiếp chuyển không gian con SVD nguồn qua ba kiểu dịch chuyển phân phối đều FAIL | Bác bỏ hợp đồng Euclidean source-subspace đã thử, **không** bác bỏ mọi phép căn chỉnh phi tuyến/bất biến |

**Nguồn gốc (provenance) cho SIX-REP-INFO:** frozen raw evidence SHA-256 `81a1ad556160b935651bc9cfc2db28533c3d4efa647d191acc828e65e82c208d`; raw evidence Git blob `7ed20fcf606b7c2a21aab2016f03c2db686f5cf3`; independent QA Git blob `ff8018391025f7dc3b4526814c51ce1074097f05`. Các định danh này được đọc từ bản ghi `research/lineage.md` tại commit nguồn. **Chưa tải và tính lại SHA-256 của tệp raw/QA**, do đó trạng thái là `SOURCE_RECORDED_NOT_INDEPENDENTLY_REHASHED`.

Đường dẫn tham khảo cố định:
- [SIX R0 parent freeze](https://github.com/minhtri22/CLDP/commit/32c528104c4d16eddb0d8ba094e5d117234ba524)
- [SIX representation-information verdict](https://github.com/minhtri22/CLDP/blob/2fc30fba568fd3782d32fd9cb3caa172d26f7853/research/lineage.md)
- [SIX composition negative / inconclusive](https://github.com/minhtri22/CLDP/blob/9ef06b141bdd0fb42255f361e426b2359bb0a84e/research/lineage.md)
- [SIX OW1 shift closure](https://github.com/minhtri22/CLDP/commit/9720ef5671990479db86fee7af8668d389f3bd30)

## 3. Câu hỏi, đối chứng, điều kiện hội nhập TTM

**H0:** Chưng cất biểu diễn của mô hình nguồn không cải thiện TTM so với các đối chứng công bằng cùng tài nguyên.  
**H1 (ứng viên, chưa tiền đăng ký khóa):** một phép chuyển biểu diễn đã kiểm định có thể cải thiện đánh giá độc lập của TTM so với huấn luyện gốc và chưng cất đầu ra thông thường, khi chi phí và dữ liệu được kiểm soát.

Bài thử tiền đề và hướng thực hiện:
1. **G0 — Hồ sơ thiết kế và quyền:** xác minh mô hình nguồn có thể truy cập hidden states, revision trọng số/tokenizer và giấy phép; ứng viên ban đầu Qwen3-0.6B, nguồn thứ hai Qwen3-1.7B. GPT-3/ChatGPT dạng dịch vụ không được coi là nguồn trọng số mở. Muse chỉ được xem xét sau đánh giá tài nguyên và điều kiện cấp phép.
2. **G1 — Đo tính chuyển được:** cùng các tiền tố văn bản; xuất trạng thái ẩn theo layer, so sánh CKA, ánh xạ tuyến tính, kiểm tra giữ thông tin theo nhiệm vụ, đối chứng tráo cặp và ngẫu nhiên. Tokenizer khác nhau nên **không ghép vector theo chỉ số token**.
3. **G2 — Thử nghiệm chức năng nhỏ:** thử can thiệp/đánh giá held-out trên các nội dung độc lập; không được gọi độ tương tự vector là chuyển giao tri thức.
4. **G3 — TTM khi baseline ổn định:** chạy A = TTM chuẩn, B = output distillation, C = SIX-aligned representation distillation, D = shuffled representation. Kiểm soát tổng dữ liệu, số bước/tokens, optimizer, seed, FLOPs hoặc lượng tính toán và tham số adapter. Báo cáo NLL/độ lệch, chất lượng held-out, hiệu quả học; đánh giá TTM **không có teacher khi suy luận**.

**Điều kiện quyết định:** đề xuất tiêu chí PASS/FAIL, kiểm soát rò rỉ, cách tính ngân sách, quyền dữ liệu/model và tập TEST niêm phong trong tài liệu tiền đăng ký riêng **trước** chạy khoa học. G3 chỉ có thể thử trên checkpoint và baseline TTM được xác minh độc lập; không được sử dụng kết quả TTM pilot chưa chốt làm bằng chứng.

## 4. Điều kiện quản trị và phạm vi thao tác

- Trạng thái nhánh hiện tại: `BRANCH_CREATED / DOC_ONLY`. Không tự mở thí nghiệm, tải mô hình, train, thuê GPU, gọi Colab, đổi Ollama, đổi runtime, sửa `main` hoặc PR #12.
- Mọi thao tác local tương lai, bao gồm `git worktree` và dọn dẹp, phải nằm **bên trong** `D:\WORK\RESEARCH\TokenToModel-Lab`, kiểm tra `origin`, SHA/đường dẫn và symlink/junction; dọn dẹp cần cấp quyền riêng.
- Chỉ merge sau kiểm thử và thẩm định qua PR riêng; việc mở nhánh và ghi tài liệu **không** phải QA khoa học hoặc giấy phép tích hợp.
- Giữ mọi FAIL/INCONCLUSIVE nguồn, không tẩy lỗi lịch sử. Nếu mốc nguồn bị thay đổi ở nhánh khác, **pin vẫn giữ SHA đã khóa** và thay đổi chỉ thông qua phiên bản manifest mới có diễn giải lý do.

**Bước kế tiếp:** `TTM_SIX_XMODEL_G0_PIN_AUDIT_AND_PREREG_DRAFT` — kiểm toán lại từng tham chiếu nguồn, xác minh điều kiện model/revision/license/hidden states và soạn tiền đăng ký thí nghiệm nhỏ. **Không chạy khoa học ở G0.**

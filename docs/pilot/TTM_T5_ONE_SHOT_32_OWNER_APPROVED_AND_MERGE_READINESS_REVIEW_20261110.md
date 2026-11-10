# TTM T5 — Owner phê duyệt batch 32 và rà soát merge

**Ngày:** 2026-11-10. **Source of truth:** nhánh `research/ttm-t5-f32-strict-logit-parity-diagnostic-20261109` của `minhtri22/TokenToModel-Lab`.

## 1. Quyết định owner đã nhận

> “đồng ý chạy 32, xem xét việc merge”

Quyền thực thi: **GRANTED — một batch native mới duy nhất**, 8 fixture SYN01..SYN08 × S0/S1/S2/S3, threshold strict `max |Δlogit|≤0.001`, không tái chạy 8 fixture gốc, không sửa trọng số/dữ liệu/TEST, không train. Không suy diễn “xem xét merge” là “đồng ý merge”.

`READY_TECHNICAL=PASS` từ receipt Windows `2648b84558a503de66a2e2a0e09094561123d64578eefa82b26bf85fcfdc1be2`, old EXE SHA `0da91785a0882dd1b5a04cce4dc050886b54e0fe0f17e66f66802638b3760537`, reference SHA `d6f367269df610a4e1c93edbff9a4dcffb7f0e0b6bd5f77247c5c90394de176c`.

**Cổng RemoteMCP hiện tại**: `project_register` báo `paired execution devices require project_register_on_device`, nhưng `project_register_on_device` bị từ chối `remote project kind changed`. Không nhận proxy job, chưa có lệnh native thực thi qua connector. Cổng thực thi local được thay bằng đúng một script Python one-shot, source Git blob **`61c1cf9c31bc3514f4982509655990110aaf56ed`** (không cần build/QA lại). Chủ máy tải script đó vào thư mục `_tmp` của dự án, xác minh Git blob bằng `git hash-object`, kiểm parser Python 3.12, rồi gọi với `--approve-one-frozen-batch I_APPROVE_ONE_TTM_T5_FROZEN_NEW_32_NATIVE_BATCH`. Việc truyền literal này là thực thi quyền owner đã phê duyệt trong cuộc trò chuyện, **không yêu cầu thêm cấp phép**.

Khi hoàn tất, thư mục biên bản mới duy nhất:
`D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\ttm_t5_kvflash_frozen_new_32_native_one_shot_v1_20261110`, trong đó có `RUN_RECEIPT.json`, `01_native_one_shot.log`, 32 dòng logits, `02_independent_native_32_audit.log`, `AUDIT_FROZEN_NEW_32.json`. Runner không cho tự retry nếu thư mục đã tồn tại. Nếu lỗi/partial, giữ nguyên để phân xử.

## 2. Khảo sát nhánh Git

| Tiêu chí | Trạng thái khi kiểm |
|---|---|
| `main` | `b57b44e7287f842e81050c1faee337f636333dd0` |
| T5 so với `main` | Ahead 63 / Behind 0 |
| Diff files | 41 tệp **added**, không thay đổi tệp đã có của `main` |
| Thay đổi `lineage.md` | Không |
| PR #13 | Draft, **nhánh khác** `research/ttm-small4m-q1q2-quality-single-batch-20261109` |
| Git ancestry | Nhánh T5 là fast-forward descendant của `main` hiện tại |
| Independent native 32 | Chưa thực thi tại thời điểm viết |
| Merge verdict | **HOLD_PENDING_EXPERIMENT_AND_INDEPENDENT_QA** |

Phân biệt hai loại cổng: `GIT_INTEGRATION_FEASIBLE` vì lịch sử tuyến tính, chỉ thêm 41 tệp; nhưng `SCIENCE/QUALITY_MERGE_READY` còn HOLD vì chưa có kết quả 2×2, chưa độc lập phân xử nguyên nhân 7/8 FAIL.

## 3. Phương án merge sau khi có 32 output

1. Đọc SHA `RUN_RECEIPT`, audit chính xác 32/32 fixture × arm, mỗi dòng đủ 2.048 logits và Flash graph counter phù hợp, tính contrast S0..S3 theo hợp đồng đóng băng.
2. Ghi **adjudication PASS/FAIL khoa học** và SHA evidence lên nhánh T5; chỉ khi đạt điều kiện science mới append-only `lineage.md` theo quy tắc nghiên cứu. Trường hợp `HOLD` hoặc đo thất bại: giữ nguyên nguyên nhân và evidence; không thay result gốc `FAIL_7/8`.
3. Trước merge: QA tĩnh/PS51/parsing cho source mới, tách hoặc đánh dấu rõ script từng bị lỗi và bị thay thế (preview, supplement, old stage), rà nội dung 41 tệp added tránh đưa mã chẩn đoán cũ gây hiểu nhầm vào đường production. Không ép merge nếu còn lỗi hoặc dữ liệu chưa đủ.
4. **Đề xuất một PR riêng cho nhánh T5** (không dùng PR #13), review phạm vi và checks, rồi merge theo SHA đúng lúc đã QA. Vì đang ở HOLD, chưa tạo PR mới/merge/update `main`.

Bước tiếp: owner thực thi một batch 32 bằng runner SHA ghim và chuyển biên bản `RUN_RECEIPT.json`; sau đó độc lập phân xử + quyết định merge cụ thể. Không chạy lại công việc đã PASS và không thay threshold.

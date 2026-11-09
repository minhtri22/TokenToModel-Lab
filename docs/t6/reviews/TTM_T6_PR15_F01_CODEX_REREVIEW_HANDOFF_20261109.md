# HANDOFF — Codex re-review bản sửa F-01 của TTM-T6 PR #15

**Ngày:** 2026-11-09  
**Nhiệm vụ:** `TTM_T6_PR15_F01_PATH_CONTAINMENT_AUTHOR_FIX_AND_DISTINCT_REREVIEW`  
**Quyền:** REVIEW_ONLY; không tự sửa mã, không merge, không xóa/rerun benchmark Windows lịch sử.

## A. Nguồn xác nhận từ GitHub

- Repo: https://github.com/minhtri22/TokenToModel-Lab
- PR: https://github.com/minhtri22/TokenToModel-Lab/pull/15
- Branch: `feature/ttm-t6-dense-paged-ab-benchmark-fixture-20261109`.
- `main` tại thời điểm tác giả sửa: `b57b44e7287f842e81050c1faee337f636333dd0`.
- Báo cáo reviewer gốc: [`TTM_T6_PR15_CODEX_DISTINCT_REVIEW_20261109.md`](TTM_T6_PR15_CODEX_DISTINCT_REVIEW_20261109.md). Review trước ở HEAD `1b98dde3b40f78edd7c599a12ff8c71ebe6b346f` với `HOLD_REQUIRED_FIX_OR_EVIDENCE`, `MERGE_HOLD`.
- Biên bản tác giả: [`TTM_T6_PR15_F01_AUTHOR_STATIC_QA_AND_HOLD_20261109.json`](../../../artifacts/qa/t6/reviews/TTM_T6_PR15_F01_AUTHOR_STATIC_QA_AND_HOLD_20261109.json).
- HEAD mới phải **được reviewer tự lấy lại** từ GitHub trước khi review. Không mặc định SHA ở đây là HEAD cuối sau khi handoff được commit.
- Source thực thi benchmark Windows đã khóa `ff4d30ea294f148d5d060f1331cfbf6f4f6d44aa`. Không cần chạy lại lượt này hoặc thay bản raw.

## B. Thay đổi F-01 cần kiểm chứng lại

1. `tools/t6/path_containment.py`: guard chung; kiểm tra lexical path (không absolute/drive/UNC/traversal/ADS), `Path.is_symlink()`, `Path.is_junction()` Python 3.12, `FILE_ATTRIBUTE_REPARSE_POINT`, và `Path.resolve()` nằm trong subtree `artifacts/qa/t6`. Input phải tồn tại và là file; output phải có parent tồn tại, chưa được ghi, dùng `open('x')`.
2. `tools/t6/cache_ab_benchmark_fixture.py`: `_ensure_safe_output()` phải dùng guard trên trước mọi ghi/chạy benchmark.
3. `tools/t6/independent_scoped_qa.py`: **cả ba** path `--report`, `--unittest-log`, `--output` dùng guard; không tự `mkdir` trước xác minh.
4. `tests/t6/test_f01_path_containment.py`: **9 test mới**, gồm một negative test junction Windows thật qua `cmd /c mklink /J`; kiểm tra không làm thay đổi target và cleanup chỉ tháo junction.
5. `tools/t6/run_f01_windows_qa.ps1`: QA tĩnh/âm tính trên worktree mới bên trong project root, 16 bài gốc + 9 bài F-01; tuyệt đối **không** gọi benchmark, TEST/Q1Q2, TRAIN, GPU hoặc P07/P08. Không cho re-run nếu đã có worktree/evidence.
6. `tools/t6/run_windows_exact_head.ps1`: giữ pattern đúng **16 bài legacy** để không diễn giải sai receipts cũ. Không chạy lại script benchmark này.
7. `tools/t6/README.md`: F-03 đánh dấu rõ hướng dẫn replay trước đây là **lịch sử**; F-02 được giữ `DESCRIPTIVE_ONLY` về so sánh TTFT.

## C. Review thực chất, không chỉ đọc nhãn PASS

- Thử các đường dẫn gây lỗi: symlink/dangling symlink, Windows junction, reparse point, `..`, absolute paths, drive/UNC, alternate data stream, output tồn tại, QA input bị redirect, symlink ancestor và nested parent. Đặc biệt kiểm tra `Path.resolve()` không escape repo.
- Kiểm tra `_reparse` có bắt junction trên đúng Python 3.12/Windows; `Path.is_symlink() == False` không được là lý do chấp nhận junction.
- Nếu `mklink /J` bị SKIP, phải ghi `HOLD_REAL_JUNCTION_PROBE_NOT_EXECUTED`, không tự nâng thành PASS.
- Chứng minh đường gọi trực tiếp `python tools/t6/cache_ab_benchmark_fixture.py` và `python tools/t6/independent_scoped_qa.py` đều bị chặn **trước khi** ghi hiện vật ngoài vùng cho phép. Không cần gọi cả benchmark để kiểm chứng guard.
- Xem xét giới hạn TOCTOU: bản sửa phòng ngừa cấu hình workspace tĩnh/đơn người, **không** khẳng định race-free trước attacker có thể đổi ancestor ngay sau validation. Nếu threat model yêu cầu chống race, ghi rủi ro hoặc HOLD với căn cứ cụ thể; không suy diễn PASS vô điều kiện.
- Dùng `git diff` HEAD trước/sau review để khẳng định không sửa hàm `run_once`, `measure_workload`, KV implementations, model hoặc nguồn P02/P05/P06. Git blob P02 `9762343e06cf800b50574c2871ae1ed58537fb18`; P05 `d835e5d7bb07fea447c5a869b13c70327ab05a53`; P06 `4d52188adaf55674b6965513ea1beb38ec9a8e9b`.
- Kiểm lại mọi bằng chứng Windows cũ, SHA không đổi; không chạy lại 6-token benchmark historical hay tự cập nhật `lineage.md`.

## D. Cổng QA/merge đã khóa

Trước khi ra `PASS_REVIEWED_SCOPED`, reviewer phải có **bằng chứng dynamic Windows F-01** trên HEAD đã sửa: 16/16 legacy tests + **9/9 F-01 negative tests**, trong đó junction thật **không SKIP**, log và receipt SHA256 trên GitHub, cùng đối chiếu source. Tác giả mới có `AUTHOR_STATIC_QA=PASS_19/19` — **KHÔNG thay thế Windows tests**.

Nếu chưa có log Windows mới: `HOLD_REQUIRED_FIX_OR_EVIDENCE` / `MERGE_HOLD`. Nếu test phát hiện lỗ hổng: ghi CRITICAL/HIGH với path/line/probe; tác giả sửa riêng và review HEAD mới. Nếu tất cả qua: đề xuất `PASS_REVIEWED_SCOPED` và `MERGE_CANDIDATE`, nhưng **chỉ chủ dự án** quyết định merge. F-02 vẫn chỉ non-blocking cho benchmark mô tả; tuyệt đối không kết luận tăng tốc. F-03 chỉ sửa nhãn lịch sử.

## E. Bàn giao

Biên bản re-review phải ghi reviewer identity, mode, exact HEAD/source blobs, các lệnh thực sự chạy, outcome của từng gate, findings mới hoặc đã đóng, SHA-256 logs trên GitHub, và quyết định riêng `MERGE_CANDIDATE`/`MERGE_HOLD`/`MERGE_DENY`. Nếu reviewer chưa chạy Windows, ghi rõ chỉ `STATIC_REVIEW`.

Đề xuất đường dẫn: `docs/t6/reviews/TTM_T6_PR15_F01_CODEX_DISTINCT_REREVIEW_YYYYMMDD.md` và receipt `artifacts/qa/t6/reviews/` trên nhánh PR #15. Không tự merge PR.

**Bước thực hiện tiếp theo:** `TTM_T6_PR15_F01_WINDOWS_NEGATIVE_QA_THEN_CODEX_DISTINCT_REREVIEW`.

`PR15=HOLD` · `MAIN=UNCHANGED` · `LINEAGE=UNCHANGED` · `P07=PAUSED_PRESERVE` · `P08=NOT_OPENED`.

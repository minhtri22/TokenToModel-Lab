# Track A Q001 M0 v3 — Tái kiểm toán F01/F02

**Phán quyết duy nhất `I1_PASS_SCOPED_MEASUREMENT`** · 2026-11-17.

Reviewer độc lập Hypatia (`01a1e558-969b-7e43-85c2-6aaa8d4df3e5`) tự viết và chạy checker F01/F02 rồi phân xử. Phiên chính (`01a1e4ff-9475-7401-939d-a7ba70985fce`) đọc lại custody trên Windows và công bố qua tài khoản GitHub của repository.

- PR #33, exact source HEAD `ec197b5f00d3a037420390edd11ee55047e1d37f`, base PR #28 `ebdc54575eed1ff60c402eecf60289f408bb38ca`. Receipt ghi SHA-256 blob Git LF, CRLF suy ra và bytes checkout của toàn bộ 10 file thay đổi kể từ review trước. Review gốc tại `05041501bfe84822feffd39290c6800b2152055a` và `lineage.md` có diff rỗng. HEAD của main, PR #28 và các nhánh Track B/C chính khớp trước và sau phiên đọc. [Draft PR #33](https://github.com/minhtri22/TokenToModel-Lab/pull/33)
- CI tác giả ở `8cc069095724e96fd051561a3037f579d01d9222` khớp toàn bộ mã và workflow của HEAD review. Receipt bàn giao cuối dẫn run 43903520071, với 48 negative checks. [CI Windows cuối](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43903520071)

## Negative controls độc lập

| Kiểm tra | Kết quả ở HEAD review |
|---|---|
| F01, 2.048 logits đồng đều tại float32 khoảng `+1e20`, `-1e20` và float32 max, 80 case mock mỗi mức | Cả 240 lần cho NLL `7.6246189861593985` và abstain ở cả hai top-1. Scorer trước sửa cho NLL `0.0`. |
| F01, logits không đồng đều và dịch `0`, `+2^46`, `-2^46` | Cả ba lần đạt `1.4131451562150485`, khớp oracle Decimal. Scorer trước sửa cho `1.40625` và `1.4140625` ở hai mức dịch lớn. Gold rank 2, full-vocab top-1 sai và four-choice đúng. |
| F01, đầu vào sai | Từ chối 2.047 hoặc 2.049 logits, NaN và infinity. |
| F02, cache timestamp/size hợp lệ dưới Python `-I -B` | Loader cũ và loader chuẩn chạy sentinel. Runner mới bỏ qua sentinel ở cả LF và CRLF, đọc source một lần và chạy buffer đã xác minh kể cả khi file bị đổi sau lần đọc. |
| F02, sai source | Từ chối khi thiếu file source dù cache còn tồn tại, sửa bytes, mixed EOL, lone CR, BOM và symlink trỏ sang bytes sai. Symlink trỏ sang bytes đúng vẫn được loader xác thực bằng SHA. |
| Runner, manifest lịch sử mô phỏng | Chấp nhận đúng cặp records/manifest đã pin, từ chối digest sai, sai scorer lịch sử, sửa bytes dù JSON tương đương, thay đổi nội dung ngoài scorer SHA và symlink của records/manifest. |

Checker riêng đạt **35/35**, không skip. Output nằm trong [receipt tổng hợp](receipt.json). [Checker F01/F02](check_f01_f02.py) · [Scorer ghim](https://github.com/minhtri22/TokenToModel-Lab/blob/ec197b5f00d3a037420390edd11ee55047e1d37f/tools/pilot_t4/direct_failure_diag_q001/track_a_m0_v3/q001_m0_goldblind.py#L219-L224) · [Loader ghim](https://github.com/minhtri22/TokenToModel-Lab/blob/ec197b5f00d3a037420390edd11ee55047e1d37f/tools/pilot_t4/direct_failure_diag_q001/preexec_candidate_20261116/ttm_sm4m_diag_q001.py#L135-L162)

## Native Windows readback

- Windows PowerShell `5.1.26100.9818`, Python `3.12.10`. OnePack được lưu trực tiếp từ blob Git LF bằng chế độ tạo file mới, giữ LF cuối. SHA-256 của script chạy là `6506ddf1e5b98793a4b2a3ba3b7aaf089f8692b64f4e0f6b53899b3c28d1a76d`. Chạy `-ReadbackOnly` với exact HEAD và runner CRLF SHA của handoff. Worktree Windows thực tế dùng LF, khớp pin. Native OnePack report `POSTFIX_PRIVATE_READBACK=PASS_SCOPED`, với SHA-256 của receipt tại máy `4897bbf3400f4179cbb692a40bd70c4b814f2ececa552aaab5cde802704436cf`. Phạm vi của wrapper là SHA của các file được pin và metadata manifest.
- Checker custody tính lại **80/80 case digest** và **5/5 group digest** từ các rows đã đóng băng. Kết quả khớp cả manifest trên máy và receipt review gốc. Split RECOMBINED/ABSENT có 0 TRAIN binding leak, NOVEL_IDS có 0 ID overlap và 16 cặp counterfactual đều khớp parent. Manifest hiện tại tính từ rows đã lưu chỉ khác manifest đóng băng ở scorer SHA. Runner xác thực các rows này trực tiếp. `read_frozen_fixture` được chạy riêng trên mock, vì hàm đó tái sinh reference rows trong bộ nhớ.
- Snapshot SHA-256, kích thước và mtime trước/sau khớp cho BPE, records v3, manifest, freeze receipt, records lịch sử và receipt custody cũ. Checker kiểm tra cả file lẫn các thư mục cha trong project đều không có reparse point. Fixture thật được mở chỉ đọc, số lần freeze hoặc tái sinh fixture thật trong phiên bằng 0.

| Custody | SHA-256 |
|---|---|
| BPE TRAIN-only | `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc` |
| Records v3 | `823a08dd4be0da7748cb258b9bf5b2841dd1fdbac84956eb204be7ba57f8c55d` |
| Manifest đóng băng v3 | `0b80368a6747994df5f5b8d0e7b35137266ac82f6c9b83d26af5b61f79b3cb04` |
| Freeze receipt | `b82a7ebc29930563db581f7724d0847a725d893860b776b7cc682ec875af4c3a` |
| Records lịch sử | `5f1234f583ccf719ca9f0e68de4f47d8b653af777271b8115c5f02307f764e5a` |

Native suite đạt **31/31** unittest, **18/18** runner source QA, **10/10** mock source checks và **48/48** negative QA. Mock forged-GO đi qua CLI với dữ liệu giả, trả exit `86` và lý do thực tế `HOLD_WINJOB_LIMIT_READBACK_MISMATCH`, không tạo output. Release preflight gọi riêng trên host trả exit `2` với `HOLD_OWNER_INTERNAL_I1_NOT_PASS` từ verdict lịch sử.

## Giới hạn OnePack và phạm vi quyết định

OnePack đếm metadata, SHA của freeze receipt được ghi ra nhưng chưa pin trong script, và wrapper chưa tự kiểm reparse point. Thao tác kiểm đích rồi ghi receipt gồm hai bước, nên kiểm tra no-overwrite ở đây áp dụng cho lần chạy thực tế với snapshot ổn định. Checker custody bổ sung kiểm chứng riêng cho digest và đường dẫn của lần chạy này. Bootstrap mẫu trong handoff có thể bỏ LF cuối, nên phiên review đã dùng trực tiếp byte blob. Harness exit 86 nhận diện chuỗi lý do bằng substring, còn trace native ghi nhận đúng mã lý do. [OnePack ghim](https://github.com/minhtri22/TokenToModel-Lab/blob/ec197b5f00d3a037420390edd11ee55047e1d37f/tools/pilot_t4/direct_failure_diag_q001/track_a_m0_v3/Invoke-TrackA-M0V3-RealTokenizer-Freeze-PS51.ps1#L97-L148)

Kết luận áp dụng cho phép đo M0 tại commit ghim và fixture đã xác minh. Release preflight chi phối quyền chạy vẫn đang HOLD. **I2 `NOT_EXECUTED`**, model forward 0, optimizer steps 0, checkpoint access 0 và nonce claim 0.

## Tái lập evidence

```powershell
python.exe -I -B .\check_f01_f02.py <git-checkout> <new-mock-scratch>
python.exe -I -B .\check_native_custody.py --root <root> --tree <exact-checkout> --fixture <existing-fixture> --bpe <original-bpe> --historical <old-records> --onepack-receipt <native-receipt>
```

[Checker custody](check_native_custody.py) · [Receipt tổng hợp đã loại dữ liệu riêng tư](receipt.json)

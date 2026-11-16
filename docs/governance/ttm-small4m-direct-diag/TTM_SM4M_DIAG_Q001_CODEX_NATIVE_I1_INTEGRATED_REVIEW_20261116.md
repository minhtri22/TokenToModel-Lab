# TTM-SM4M-DIAG-Q001 · Native I1 trên Windows

Ngày 16/11/2026 · Operation **TTM_SM4M_DIAG_Q001_CODEX_NATIVE_I1_NEGATIVE_QA_RIGHTS_CUSTODY_AND_SINGLE_ADJUDICATION_ONEPACK**.

**I1_VERDICT = HOLD_I1.** F06 thiếu trust anchor được xác thực cho ba vai trò, quyền AD-00/AD-01C/E6 và custody của checkpoint, tokenizer, fixture thật. Watchdog hiện đo RSS theo mẫu. Trần RAM 12 GiB của cây tiến trình chưa được cưỡng chế. QA kỹ thuật do Codex thực hiện trên bản Codex sửa, chưa có xác nhận độc lập trên commit này. Python đã ghim còn thiếu psutil cần cho I2.

| Kết quả | Phạm vi |
|---|---|
| SOURCE_QA | PASS trong phạm vi source/mock. Oracle 18/18, bộ V3 của tác giả 44/44, đối kháng Codex 22/22, prefix launcher 9/9. |
| WINDOWS_NATIVE_QA | PASS trong phạm vi no-model. Parser 6/6, watchdog trực tiếp 5/5 và qua OnePack 5/5. |
| EXTERNAL_RIGHTS_CUSTODY | NOT_VERIFIED. Trust store production rỗng và fail closed. |
| I2_NOT_EXECUTED | Không gọi launcher I2, chạy mô hình, đọc checkpoint hoặc tokenizer riêng, hay freeze fixture thật. |

[PR #28](https://github.com/minhtri22/TokenToModel-Lab/pull/28) · [Issue #29 và ủy quyền của owner](https://github.com/minhtri22/TokenToModel-Lab/issues/29#issuecomment-6915190196) · [Biên nhận JSON](../../../artifacts/governance/ttm-small4m-direct-diag/TTM_SM4M_DIAG_Q001_CODEX_NATIVE_I1_RECEIPT_20261116.json) · [Evidence native](../../../artifacts/governance/ttm-small4m-direct-diag/TTM_SM4M_DIAG_Q001_CODEX_NATIVE_I1_EVIDENCE_20261116).

## Mã nguồn và môi trường

- GitHub main đúng baseline Q1 `f7a0a5874e8fd895c8ea8d17ceff393a4d4917a3`. HEAD draft đầu lượt là `2e875f18490e3cb7f6e967e5a91d2c6af04d16f0`. So với `4f5e6533854818845d3ccdfad661ccc25f0e2812` chỉ thêm handoff. Cả 14 mục V4 khớp blob Git, SHA-256 và số byte giữa manifest, ba commit được đối chiếu và checkout native. [Biên nhận preflight](../../../artifacts/governance/ttm-small4m-direct-diag/TTM_SM4M_DIAG_Q001_CODEX_NATIVE_I1_EVIDENCE_20261116/preflight.json).
- Commit retest là `77f6e946975a8b5cd5859297f6d0f161bb13f629`. Sáu tệp nguồn đổi trong thư mục candidate. Biên nhận JSON ghim SHA-256, Git blob và số byte của cả 14 tệp theo commit này. [Diff nguồn chính xác](https://github.com/minhtri22/TokenToModel-Lab/compare/2e875f18490e3cb7f6e967e5a91d2c6af04d16f0...77f6e946975a8b5cd5859297f6d0f161bb13f629).
- Máy `DESKTOP-4PSD0G2`, OS 10.0.26300.0, AMD64, PowerShell 5.1.26100.9818, Python 3.12.10 x64 tại `C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe`. Chạy trực tiếp trong worktree riêng dưới project trên D:. Lượt đầu thừa hưởng module path của PS 7 nên không tìm được Get-FileHash. Các lượt sau đặt PSModulePath về module hệ thống Windows PowerShell trong tiến trình QA và chạy với -NoProfile.
- OnePack gốc gọi lệnh tách dòng sai cú pháp PS 5.1. Watchdog gốc đạt 4/5 khi dùng module đúng. Ca thành công trả `HOLD_RUN_EXIT_` vì Start-Process -PassThru chưa giữ process handle trước khi tiến trình thoát. Probe tái hiện exit code rỗng ở đường gốc và bằng 0 khi giữ handle. Đã sửa bằng splatting, giữ handle, fail closed nếu thiếu exit code và ghi PID, exit code, số byte, thời gian và RSS đo mẫu. Log trung gian giữ lỗi dấu nháy do lần sửa đầu và kết quả retest.
- Launcher ghim hash runner và watchdog, từ chối hash do caller tự tính cho module bị thay và nạp chính buffer đã xác minh. QA tách riêng prefix bằng AST và dùng fixture có marker. Guard yêu cầu trường `expires_utc` nằm trong payload ký và dùng nonce từ payload đã xác thực. Kiểm thử hết hạn gọi validator riêng vì production chưa có key để đi qua nhánh Ed25519.
- QA từ chối root khác, tên host sai, thoát scope qua junction và symlink thật, replay nonce từ hai bản sao mã runner và qua alias của cùng root. Thử nonce dùng ledger tạm với pin root thay trong bộ nhớ. Với root/host thật, production empty trust từ chối unsigned, forged và expired trước thao tác mở input sentinel.

## Watchdog Windows

Bảng lấy từ lượt chạy trực tiếp cuối. OnePack chạy cùng năm ca với PID khác. RSS là đỉnh qua polling nên ca nhanh có thể kết thúc trước lần đo đầu. Các bài test dùng ngưỡng nhỏ và đối chiếu riêng các hằng số production.

| Ca | Kết quả quan sát | Exit code cha | Đỉnh RSS đo mẫu | Cleanup quan sát được |
|---|---|---:|---:|---|
| Thoát bình thường | PASS, 4 byte stdout | 0 | 0 byte | PID 19464 đã thoát |
| Stdout vượt 4.096 byte khi thoát | HOLD, thu 65.536 byte | 0 | 21.422.080 byte | PID 16952 đã thoát |
| Hết hạn ở ngưỡng thử 1 giây | HOLD tại khoảng 1,43 giây | 1 | 25.071.616 byte | PID 25516 đã dừng |
| RSS cả cây vượt ngưỡng thử 48 MiB | HOLD | 1 | 133.689.344 byte | PID con 32452 đã dừng trước cleanup fixture |
| Tiến trình con còn sống khi cha thoát | HOLD | 0 | 133.443.584 byte | PID con 32920 đã dừng trước cleanup fixture |

[Watchdog trực tiếp](../../../artifacts/governance/ttm-small4m-direct-diag/TTM_SM4M_DIAG_Q001_CODEX_NATIVE_I1_EVIDENCE_20261116/native-watchdog-standalone.json) · [Watchdog qua OnePack](../../../artifacts/governance/ttm-small4m-direct-diag/TTM_SM4M_DIAG_Q001_CODEX_NATIVE_I1_EVIDENCE_20261116/native-watchdog-onepack.json) · [Stdout/stderr nguyên byte, exit code và fixture giả](../../../artifacts/governance/ttm-small4m-direct-diag/TTM_SM4M_DIAG_Q001_CODEX_NATIVE_I1_EVIDENCE_20261116/native-transcripts.zip).

## Findings và điều kiện còn thiếu

| Finding | Kết quả và phạm vi |
|---|---|
| F01 | Empty trust fail closed và replay mock bị từ chối. Ba signer thật và bảo vệ ledger trước sửa/xóa trên host chưa được chứng minh. |
| F02 | Negative QA cho digest và taxonomy inventory giả đạt. Còn thiếu nguồn và provenance tokenizer riêng. |
| F03 | Mock 80/80 và tamper case/group đạt. Thiếu freeze và readback độc lập của 80 ca thật. |
| F04 | Parser, môi trường, pin launcher/module và escape tĩnh qua Win32 reparse đạt trong các bài đã chạy. Cần custody chống thay đổi đồng thời và qualification production trước khi cấp quyền cho private paths. |
| F05 | Source/mock và watchdog đã chạy trực tiếp. Thiếu xác nhận của reviewer độc lập trên exact commit. |
| F06 | **Hard veto.** Issue #29, PR #28 và evidence V4 ghi GO có điều kiện, thiếu trust anchor và attestation AD-00/AD-01C/E6 có thể xác minh. Checkpoint riêng step 1024 có SHA-256 kỳ vọng `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b` và 45.074.891 byte theo hồ sơ, chưa có custody/readback hợp lệ. Metadata Python ghi torch 2.11.0, cryptography 46.0.6, psutil vắng mặt. Chưa import Torch hoặc xác nhận runtime I2. |
| F07 | Source có gate delta hữu hạn và dương cùng fingerprint tham số. Chưa có kết quả thực nghiệm về gradient hoặc weight update. |
| F08 | Timeout, RSS tổng lấy mẫu, output và dừng cây có bằng chứng ở ngưỡng thử. Contract giữ 900 giây, 12 GiB RSS và 1 GiB tổng output. Polling có thể bỏ lỡ đỉnh RSS hoặc overshoot giữa hai lần đo. `HOLD_I1_RESOURCE_GUARD`. |
| F09 | Closed ở source. Số lịch sử đã sửa ở README, receipt cũ giữ nguyên. |
| F10 | Closed ở source. Giữ caveat gold ở vị trí 0 và distractor giới hạn cùng thiết kế frozen cũ. |
| N05 | Closed trong QA native. Launcher parse, lỗi parser riêng của OnePack đã sửa và retest. |
| N06 | Closed trong prefix QA. Pin runner/watchdog đúng định dạng và khớp mã, từ chối bytes thay hoặc caller rehash. |
| N07 | Closed trong prefix QA. Nạp buffer hash-verified trước spawn, không xuất hiện marker của module thay thế. |
| N08 | Open. Chưa chứng minh được giới hạn bộ nhớ cấp OS cho toàn bộ cây. |

Owner GO có điều kiện được bảo toàn. Checkpoint, seed, TEST/FINAL24, P02, `lineage.md` và Q1 không thay đổi. Không tạo micro-permit. Evidence mới được nối tiếp lịch sử trên nhánh draft của PR #28.

# TTM × SIX G1 — Windows real QA, distinct reviewer adjudication

**Task:** TTM_SIX_G1_WINDOWS_REAL_QA_EVIDENCE_READBACK_AND_INTEGRATED_HARD_GATE_DISTINCT_ADJUDICATION

**Ngày:** 2026-11-10 (Asia/Ho_Chi_Minh)

**Reviewer ID:** codex-native2-g1-windows-distinct-20261110

**Vai trò:** Reviewer độc lập với tác giả bộ kiểm thử. Lượt này tự truy xuất Git, tự tính hash file Windows, đối chiếu byte bundle với Git blob, đọc mã và phân xử. Đây là độc lập về thao tác kiểm định, không phải phép chứng thực danh tính bằng hệ thống IAM độc lập.

**Môi trường:** Windows 11 build 26300, máy chạy bằng chứng Windows có PowerShell 5.1.26100.9818 theo log QA; shell reviewer thực tế PowerShell 7.6.9; Python tại máy 3.12.10. Tên máy, tài khoản, SID và DACL giữ trong bằng chứng private.

## 1. Provenance và tính toàn vẹn

Origin kiểm chứng trực tiếp bằng Git là https://github.com/minhtri22/TokenToModel-Lab.git. Lệnh git ls-remote xác minh các ref và SHA sau, khớp handoff:

| Ref | Commit kiểm chứng |
| --- | --- |
| main | b57b44e7287f842e81050c1faee337f636333dd0 |
| implementation/ttm-six-g1-trusted-runtime-witness-20261109 | 81795e794550d6f8ff3515ce3332b7c053197b46 |
| research/ttm-six-cross-model-representation-transfer-20261109 | d5d0c5346a595557a76349f900d09be50bce289c |
| review/ttm-six-g1-v1c-codex-distinct-20261109 | d478282e16a4728f064892564b949e671e13cdd2 |
| Controller/watchdog source ancestor of implementation | cdaf13b4ac131b0117aadb836fd42810c63978db |

Đã fetch đúng nhánh implementation để đọc Git objects tại local, không checkout sang implementation ở main. Lệnh git rev-parse COMMIT:path và git hash-object --no-filters trên từng file bundle cho kết quả **PASS_BLOB_IDENTICAL**:

| Mã nguồn đã ghim | Git blob SHA-1 |
| --- | --- |
| g1_trusted_runtime_witness_candidate.py | f7db10a711c9f83d5e9c414ab2b183eed3313421 |
| test_g1_trusted_runtime_witness_candidate.py | 1849fa8c1f799018b7b4dc55d7c37a5ac61b91ff |
| g1_win32_job_object_watchdog_candidate.py | afd182da02cdc86b7b55063fafd8c5ab9e6a138c |
| Run-G1-TrustedRuntime-WindowsReadOnly-PS51.ps1 | 5dc3720eeee17503912da0919cfed65acd53ea16 |
| G1_OWNER_SCOPE_AND_METHODS_V1D_REVIEW_CANDIDATE_20261109.md | a470394aab9dd404fa885bd0190dac82ef40a694 |

Owner Windows QA packet tại commit 81795e7 có blob 7c525e374ebafd924695e9ebfd3413c32a7b9886. File SHA256SUMS.txt trong bundle đã được đối chiếu từng entry: **9/9 PASS**. SHA ZIP tìm thấy trên máy và được tính lại: 5584dfb61d293f2946b66ef9f5e4bb4a0703c415ced0946ff2bacc302e95013c.

Đã đọc file thực và tự chạy Get-FileHash -Algorithm SHA256, không dùng văn bản checksum làm bằng chứng thay thế. Đường dẫn private chứa bằng chứng gốc, tính từ project root, là _tmp/G1_TRUST_BOUNDARY_WINDOWS_QA_20261110_003825_4116bd1e. Tất cả file nhận kiểm tra đều là file thường, không phải reparse point.

| File private (chỉ ghi hash lên Git) | SHA-256 tự tính từ raw bytes | Kết quả |
| --- | --- | --- |
| G1_WINDOWS_QA_PRIVATE_RECEIPT.json | ecbca346db8dff459ca8659101e60391a3edd54df585d11dbede69cc93ec177e | PASS |
| LOCAL_SHA256_RECEIPT.txt | edddceb3af93b0717744b7acc57c1bc235a3b319e2f255fecca96177c24f7832 | PASS |
| logs/windows_readonly_inventory.log | 9fb7e63e550e7cb15fbcabf91d20a160319b27f5803f6e35b5f087104e1c29f1 | PASS |
| logs/synthetic_45.log | c3b3d40af2e04679f3721cde2ea31eb76d767e338364f53d262d07a2037bc52b | PASS |
| logs/controller_status.log | 627fca1dcd299caa37be51443abd43a20c014235850535812d9a7468b13c3b3a | PASS |
| logs/win32_watchdog_status.log | 30fda00e8bbed991570e91dbcae835a1e2bcfcea84a28994517fc7f59f2fb530 | PASS |
| logs/win32_job_forced_kill.log | b8d5db6116cef3eb4139fa1cd92ca0759ee0028d974f25d7af64fa811f0cc723 | PASS |
| logs/win32_job_normal_exit.log | 2b432f756cd8c54b0e956f8881cdd027be6094a2eed7aae1d2ba106f2255b330 | PASS |

Receipt có sáu mục command. Mỗi mục chứa log hash phù hợp, exit_code=0, không ghi lỗi. Giá trị last_line khớp log. Hash xác thực sự nhất quán nội bộ của các file hiện có, không chứng minh độc lập lịch sử tạo log hoặc quyền production.

## 2. Kết quả kiểm định độc lập và giới hạn

| Kiểm tra | Quan sát reviewer | Phân loại |
| --- | --- | --- |
| Git origin, bốn ref, commit ancestor và năm blob | Truy vấn Git/so byte bundle độc lập | PASS |
| Raw receipt và sáu log | Tự tính lại toàn bộ SHA-256, khớp handoff và receipt | PASS |
| Bundle manifest và ZIP | Hash 9/9 entry đúng; ZIP SHA đúng | PASS |
| Sáu command của owner runner | Receipt exit 0, log tương ứng và status đồng nhất | PASS_READBACK, không phải độc lập rerun |
| Synthetic 45 case | Log ghi 45 kiểm thử PASS và science=false | PASS_AUTHOR_SYNTHETIC_45/45; không nâng lên independent QA |
| Win32 Job Object forced kill | Log ghi timeout, TerminateJobObject và WaitForSingleObject child success theo mã QA; child_exited=true | PASS_HARMLESS_CHILD_LOG_READBACK |
| Win32 normal exit | Log ghi child_exited=true, exit_code=0 | PASS_HARMLESS_CHILD_LOG_READBACK |
| Orphan/suspended child và child-tree toàn bộ sau sự kiện | Log không có PID/process-tree trước và sau, chỉ xác nhận child handle được wait | NOT_TESTED_END_TO_END |
| Negative AccessDenied bằng worker SID thật | Chưa có principal riêng, chưa cấp ACL/root, không chạy negative token test | NOT_TESTED |
| Production pack writer, witness, T4 peak VRAM và GPU watchdog | Chưa có chứng cứ production | NOT_TESTED |
| G1 science, TEST thật, key/permit | Receipt ghi chưa thực hiện/cấp | NOT_TESTED, LOCK=HOLD |

Log Win32 thực thi **bản QA safety patch** có SHA-256 a033e881d42e59c18aa9af96390fe808eb2b9858ee2653ae88c5b238256393e5. Bản này khác Git blob production afd182da02cdc86b7b55063fafd8c5ab9e6a138c. Bản QA bổ sung TerminateProcess cho child sở hữu khi CreateProcess thành công nhưng AssignProcessToJobObject hoặc ResumeThread lỗi. Bản production đóng Job handle mà không tự kết thúc suspended child chưa được assign trong nhánh lỗi đó. Đây là **khoảng trống source code đã thấy khi kiểm tĩnh**, chưa có thử nghiệm lỗi Win32 đó trên production. Kết quả kill đúng cho harmless child trong thành công-path và không chứng thực kill toàn bộ GPU group hay không còn orphan trong mọi failure-path.

Inventory xác nhận D: là NTFS. Bốn root dự kiến controller, worker, broker, witness đều có provisioned=false, owner distinction=false. Sentinel hiện hữu được đọc thành công dưới account hiện tại, inherited_rule_count=4 và separate_worker_test=NOT_TESTED. Không có negative test bằng worker SID khác hoặc đường truy cập alias, junction, hardlink trong production. Không đăng raw SID/DACL, machine/account name hoặc receipt gốc.

## 3. Một lượt phân xử sáu hard gate

Các nhãn PASS local chỉ giới hạn cho log và synthetic evidence đã xem. Cột production cần chứng cứ từ quyền/hạ tầng thật.

| Hard gate | Local / simulation | Production | Severity | Blocker cần đóng |
| --- | --- | --- | --- | --- |
| 1. Owner authority / launcher / exact source+run+rights signature | PASS_SCOPED synthetic signature checks, science fail-closed | NOT_TESTED | HIGH | Owner key/credential quản lý độc lập, hợp đồng ký thực ràng buộc code blobs, run_id, data rights, quyền hạn và trusted launcher; owner permit chưa phát hành |
| 2. Trusted split broker / TEST denied to worker SID | PASS_SCOPED synthetic alias/path tests; inventory NTFS | NOT_TESTED | CRITICAL | Provision principal riêng, ACL có hiệu lực, worker-token AccessDenied âm tính với TEST qua cả path/hardlink/junction trước freeze |
| 3. Trusted writer / authenticated crash-consistent pack ledger | PASS_SCOPED staged-file và hash simulation | NOT_TESTED | CRITICAL | Writer có quyền riêng, ký xác thực bytes đã parse, durable transactional recovery cho pack/receipt/ACK với crash injection |
| 4. External monotonic witness / one-shot rollback | PASS_SCOPED hai bản lưu synthetic, rollback một phía fail-closed | NOT_TESTED | CRITICAL | Witness monotonic authenticated ngoài miền rollback của controller/worker; kiểm crash trước/sau ACK, rollback hai phía và concurrent replay |
| 5. OS-level watchdog và cumulative GPU budgets | PASS_HARMLESS_CHILD trên safety-patched QA runner | NOT_TESTED | HIGH | Fix failure-path production candidate, chứng cứ kill process tree và budget 3600s/teacher, 7200s tổng, GPU peak/resource guard trên target được phép |
| 6. Preregistered scientific methods v1a-v1d | PASS_SYNTHETIC_SUBSET đối với v1c CKA/bootstrap, v1d mới là candidate | NOT_TESTED / REVIEW_HOLD | HIGH | Khóa độc lập giả định null, nhóm near-duplicate, bootstrap estimand, CKA tie, power/inconclusive và giới hạn tuyên bố trước TEST |

### Witness, pack và failure modes

Mã prototype viết SQLite commit rồi append witness file (source candidate L200-L223). Witness class là **SyntheticFileWitness**, chạy trên filesystem và không có chứng thực, signer hoặc miền rollback khác. Khi cả DB và witness cùng rollback, tip có thể đồng thuận giả. Commit pack tạo staging, hardlink publish, re-read byte, rồi mới advance ledger (L255-L291). Crash ở các khoảng trước/sau publish hoặc giữa ledger và witness cần independent recovery proof, cụ thể trạng thái orphan pack, thiếu receipt, consumed ACK, crash trước/sau TEST byte read. Prototype hiện có kiểm các ca simulation, nhưng không thay cho durable authenticated service. Hàm authorize_real_science chủ động STOP vì release production chưa triển khai (L298-L304).

### Phán quyết phương pháp v1d (trước TEST)

- **v1a:** First occurrence và exact normalized dedup cần pin normalization, ordering và nguồn lineage trước phân tập. Nếu near-duplicate cùng gia đình qua TRAIN/DEV/TEST, các p-value dựa trên độc lập cặp sẽ thiếu hiệu lực. Quy tắc group split và phân tích overlap phải khóa mà không dùng outcome TEST để chọn.
- **v1b:** Mã guard v1c L314-L336 áp dụng paired bootstrap 2.000 lần với SST toàn bộ TEST cố định và paired resampling 64 hàng. Estimand là improvement so với TRAIN mean có denominator cố định, CI phải gắn đúng diễn giải có điều kiện đó. Giả định 64 hàng có thể bootstrap trao đổi được phải được đánh giá theo nhóm near-duplicate; đây là CI, không thay shuffle-null threshold. Trường hợp SST degenerate trả INCONCLUSIVE.
- **v1c:** Mã core v1c L179-L211 chuẩn hóa Gram một lần và tính null bằng hoán vị, dùng tolerance 64 × epsilon_float64 × max(1, abs(observed)) cho tie. Independent v1c synthetic review từng ghi nhận xử lý invariant p=1 và informative p≈0.000999. Quy tắc có tính bảo thủ số học nhưng chưa có chứng minh type-I/power cho dữ liệu thật, null exchangeability và near-degenerate geometry.
- **v1d:** Cấu hình 128/64/64, 8 continuation pairs, ridge grid [1,10,100], 1.000 shuffle fits, 1.000 CKA null, 2.000 bootstrap, layer 28 và các đối chứng cần được cố định trước TEST. TEST=64 chưa chứng minh công suất 80%; kết luận âm/INCONCLUSIVE không được suy diễn thành vô hiệu biểu diễn. G1 chỉ đánh giá scoped cross-model feasibility với B-direct, target-oracle, TRAIN-mean, shuffle, CKA được báo cùng nhau; không khẳng định cơ chế nhân quả độc quyền SIX hoặc lợi ích đối với huấn luyện TTM.

**Methods adjudication:** REVIEW_HOLD. Reviewer chưa phê chuẩn amendment v1d làm giao thức science cuối cùng vì các điều kiện khoa học kể trên chưa được khóa và qualification chưa độc lập hoàn tất.

## 4. Phán quyết duy nhất

**HOLD**

Các hash/origin/source pins đạt PASS độc lập. Windows harmless-child kill và 45 synthetic cases có bằng chứng đúng phạm vi. Sáu gate production chưa đạt qualification, phương pháp v1d chưa được phê chuẩn độc lập. Không xác lập FAIL tamper hoặc phản ví dụ production mới trong lượt readback này. Các khiếm khuyết v1b trong review 2026-11-09 vẫn là historical synthetic defect, đã có sửa v1c ở phạm vi được kiểm.

G1_SCIENCE_LOCK=HOLD

OWNER_SCIENCE_PERMIT=NOT_ISSUED

G1_PRIVATE_TEST_OPENED=NO

SCIENCE_EXECUTED=NO

## 5. Một gói khắc phục tích hợp hữu hạn

**TTM_SIX_G1_INTEGRATED_PREEXECUTION_PRODUCTION_GATES_AND_METHODS_CLOSURE** gồm đồng thời sáu thành phần: (1) owner-bound signed authority và exact-version launcher; (2) broker với worker principal/SID riêng và AccessDenied thật trước freeze; (3) signed trusted pack writer với crash-consistent ledger; (4) external monotonic authenticated witness chống rollback cả hai miền và replay; (5) watchdog production có failure-path cleanup và kiểm cumulative/time/peak-GPU bằng workload kỹ thuật được phép; (6) amendment v1a–v1d đã preregister và được reviewer độc lập phê chuẩn, bao gồm group dependence, null validity, CI estimand, power và INCONCLUSIVE. Chạy một lượt QA âm tính/tích hợp đã ghim trên môi trường tin cậy sau khi các thành phần tồn tại; reviewer sau đó adjudicate chung đúng một lần. Việc cấp owner science permit là quyết định riêng sau PASS gates.

**Phạm vi thực thi reviewer:** chỉ đọc file, tính hash, truy vấn Git và phân tích tĩnh. Không rerun 45 tests, không chạy GPU/Qwen/science, không mở TEST, không thay đổi ACL, owner key, v1c, PR #12, main, lineage.md hoặc checkpoints. Báo cáo và JSON receipt đã khử thông tin nhạy cảm được lưu trên nhánh reviewer riêng.

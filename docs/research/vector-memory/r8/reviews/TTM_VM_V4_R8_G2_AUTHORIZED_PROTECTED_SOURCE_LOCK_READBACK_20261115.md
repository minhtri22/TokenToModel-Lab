# TTM Vector Memory V4 R8 — G2 Authorized Protected Source-Lock Readback

**Operation** `TTM_VM_V4_R8_G2_AUTHORIZED_PROTECTED_SOURCE_LOCK_READBACK`
**Ngày kiểm tra** 2026-11-15 (Asia/Bangkok)
**UTC readback window** `2026-11-15T05:10:31Z`–`2026-11-15T05:10:56Z`
**Vai trò** Codex Windows execution and private custody verification
**Chế độ** `READ_ONLY_PREFLIGHT · G2_CUSTODY_ONLY · NO_SCIENCE_EXECUTION`
**Kết luận G2** `G2_HOLD_SOURCE_LOCK_REBIND_NOT_VERIFIED`
**Lý do trực tiếp** `G2_HOLD_PROTECTED_STORE_NOT_IDENTIFIED`
**Quyết định tích hợp** `FINAL_DECISION=HOLD_INTEGRATED`

## 1. Source of truth và các commit đã khóa

Repository `minhtri22/TokenToModel-Lab`. Exact implementation source là `84d9d5c95e9962ccfe294852570e261b145fe403`. Frozen V4 scientific contract là `b8410d9c1f77a733036e980b567de73c316f8725`. Independent G0/G2 adjudication là `12d66bcff86a6cf435998a98a14afd254924fa5d` trên nhánh `evidence/ttm-vm-v4-r8-g0-f01-f03-single-closure-20261114`.

Đã đọc adjudication đúng commit bằng `git show`, lấy Git objects của scientific source qua Git remote và tính SHA-256 trực tiếp trên byte của từng Git blob bằng Python 3.12. Đồng thời đọc các byte trong **checkout Git thông thường** trên Windows bằng `Get-FileHash`. Hai nguồn công khai cùng khớp 5/5 với pin trong handoff. Các commit báo cáo evidence sau implementation commit chỉ cung cấp chứng cứ, không thay thế scientific source pin.

Các quyết định `B03-A=PASS_SCOPED`, `B03-B=PASS_SCOPED`, `B03-C=PASS_SCOPED_INDEPENDENT`, `G0-VERSION-01=PASS_SCOPED_INDEPENDENT_SOURCE_REVIEW` và `PRODUCTION_GATEWAY=PASS_SCOPED_SOURCE` được kế thừa nguyên phạm vi từ adjudication đã khóa. Không thực hiện lại G0.

## 2. Local executor và working tree

| Thuộc tính | Readback tại Windows |
| --- | --- |
| Host | `DESKTOP-4PSD0G2` |
| OS | Windows NT 10.0.26300.0 (Windows 11 host) |
| PowerShell cho lượt này | `7.6.9` |
| Process security context | Interactive user, medium integrity, administrator group deny-only |
| Token privileges | Đọc bằng `whoami /user`, `whoami /groups`, `whoami /priv`; không elevation |
| Repository chính | `D:\WORK\RESEARCH\TokenToModel-Lab`, `main` tại `1edb95cc3925ff18f0c644e94888139af854fae5` khi discovery |
| Evidence worktree hiện hữu | Nhánh evidence đúng tên, clean trước khi cập nhật fast-forward từ `2eecf748...` tới `12d66bcff86a6cf435998a98a14afd254924fa5d` |
| Protected-runtime authorization | `NOT_VERIFIED` |

Thông tin SID, tên tài khoản, membership chi tiết và ACL entries đã được kiểm tra trong phiên local và được giữ ngoài báo cáo public. Không tạo biên nhận private chứa các định danh này vì chưa có approved persistent private receipt root. Checkout chính có các mục untracked từ trước, không được chỉnh sửa.

## 3. Authorized custodian và protected storage discovery

Đã kiểm tra đúng phạm vi hồ sơ hiện hữu trong dự án, bao gồm `docs/research/vector-memory/r8/`, quyết định G1, các G2 reviews, và record `integrated_closure/OWNER_RIGHTS_CUSTODY_DECISION_PACKET_PENDING.json`. Đã đối chiếu thư mục chứng cứ `_evidence/vector-memory` trong repository chính theo tên và các record R8 liên quan. Không mở rộng tìm kiếm ngoài phạm vi này.

Record custody ở exact implementation source ghi `custodian_private_storage_readback_plan.status=NOT_VERIFIED`, `private_storage_uri=REDACTED_NOT_SUPPLIED`, `private_material_read=NOT_EXECUTED`, `gold_access=NO`. Independent adjudication tại `12d66bc...` cũng xác nhận chưa có protected source path hay custodian permission đã xác thực. G1 standing decision có phạm vi nghiên cứu nhưng không chỉ định account và protected root hợp lệ cho G2.

| Yêu cầu G2 | Kết quả hiện tại |
| --- | --- |
| Canonical approved R8 protected source root | `NOT_IDENTIFIED_IN_REVIEWED_AUTHORIZED_RECORDS` |
| Authorized custodian account / right to use this store | `NOT_VERIFIED` |
| Persistent protected storage identity | `NOT_VERIFIED` |
| Provenance giữa protected checkout, execution identity và source pin | `NOT_VERIFIED` |
| Private receipt storage scope | `NOT_IDENTIFIED` |

**Đánh giá cổng** `G2_HOLD_PROTECTED_STORE_NOT_IDENTIFIED`. Việc xác minh protected-path, custody ACL và protected-runtime SHA dừng ở điều kiện tiên quyết. Không suy đoán đường dẫn từ research root hoặc public Git worktree. Không kết luận kho private không tồn tại ở nơi khác.

## 4. SHA-256 exact-source readback

Thư mục source tương đối `docs/research/vector-memory/r8/integrated_closure/`.

| File | Expected SHA-256 = actual Git-blob SHA-256 = actual public-worktree SHA-256 | Git byte match | Public Windows checkout match | Protected runtime |
| --- | --- | --- | --- | --- |
| `folds_raters.py` | `02626f9f0def5af90b57c2930898e96dbc8f6206c441bb4aaa4c4278ce0dddae` | PASS | PASS | NOT_EXECUTED |
| `r8_production_caller.py` | `3a9b249bced1b4ceaa5746d63367c017410ef82ded21ef386c3be2b1ee76b206` | PASS | PASS | NOT_EXECUTED |
| `test_g0_algorithm_version_binding.py` | `2ce86fe549e1625790fcab72c076df2f12d648b048a350570d5c97a026431ae2` | PASS | PASS | NOT_EXECUTED |
| `gold_contract.py` | `8e8b81ce2d0bc47cc60c29abc7156fe9d97613e67983e43b7f587615d68015a5` | PASS | PASS | NOT_EXECUTED |
| `restricted_oracles.py` | `34ab74d36b822703e4d8cbdf281e142273d55d181243d904b55fd31a0e6382a1` | PASS | PASS | NOT_EXECUTED |

Windows `Get-Item` không phát hiện reparse-point flag tại năm public file. Các path này thuộc checkout Git thông thường, chưa có attestation chứng minh đây là protected private runtime. Không tính SHA trên tệp hay root private chưa được xác lập.

**Phân loại chứng cứ SHA** `G2_PUBLIC_SOURCE_SHA_MATCH_ONLY` (`5/5`). **Protected source SHA matches** `0/5 VERIFIED`, `5/5 NOT_EXECUTED`.

## 5. ACL/DACL và tính bền vững của storage

`Get-Acl` trên worktree Git công khai cho thấy ACL thừa kế, có quyền cho nhóm người dùng thông thường. Kết quả này xác định checkout đang đọc là môi trường Git công khai. Không suy diễn từ ACL này về kho protected R8.

| Khía cạnh | Kết quả |
| --- | --- |
| Public Git worktree ACL | `OBSERVED_PUBLIC_CHECKOUT_ONLY` |
| Approved R8 protected-root owner/ACL/DACL | `NOT_EXECUTED_NO_VERIFIED_ROOT` |
| Effective access under authorized private custodian | `NOT_VERIFIED` |
| Private store persistence across sessions | `NOT_VERIFIED` |
| Historical 54-byte non-R8 sentinel | `PASS_SCOPED_STORAGE_PREFLIGHT_REPORTED`, preserved, not rerun |

Sandbox của sentinel lịch sử đã xóa theo record `62542b6db216a021f84aa8495f40794fb82097d4`. Không sử dụng nó làm protected persistent store.

## 6. HMAC custody và pre-G3 commitment readiness

Historical G2 report mô tả thủ tục **dự kiến** dùng Windows CSPRNG, DPAPI CurrentUser và ACL giới hạn cho HMAC key. Hiện chưa có approved R8 store/custodian scope và chưa có bằng chứng xác nhận key policy áp dụng cho một kho bền vững cụ thể. Quy trình khóa source/runtime và nơi ghi immutable timestamped G_pre commitment trước G3 chưa được kiểm chứng trên protected storage.

| Yêu cầu | Trạng thái |
| --- | --- |
| Prospective HMAC procedure documented | `YES_HISTORICAL_DESIGN` |
| `HMAC_KEY_CUSTODY_POLICY_VERIFIED` | `NO` |
| `ACTUAL_HMAC_KEY_GENERATED` | `NO` |
| Durable, immutable pre-G3 commitment mechanism | `NOT_VERIFIED` |
| Actual G_pre commitment | `NOT_CREATED` |

## 7. Giới hạn và phân xử cuối

Lượt này có bằng chứng thực thi tại local Windows và hash readback của **public checkout**. Không thu được approved protected source root, chứng cứ ủy quyền custodian, protected ACL, durable private receipt hoặc protected runtime hash. Do đó không đủ điều kiện `G2_PROTECTED_SOURCE_LOCK_PASS_SCOPED`. Nguyên nhân cụ thể của readback HOLD là `G2_HOLD_PROTECTED_STORE_NOT_IDENTIFIED`, đồng thời quyền custodian chưa xác thực (`G2_HOLD_CUSTODIAN_AUTHORIZATION_NOT_VERIFIED`).

**G2** `G2_HOLD_SOURCE_LOCK_REBIND_NOT_VERIFIED`
**G0** `G0_VERSION_BINDING_PASS_SCOPED_INDEPENDENT_SOURCE_REVIEW` — giữ nguyên báo cáo tại `12d66bc...`
**G1** `OWNER_STANDING_RESEARCH_DIRECTION_RECORDED` — giữ nguyên
**Final** `FINAL_DECISION=HOLD_INTEGRATED`
**Candidate authoring** `GO_R8_D_CANDIDATE_AUTHORING_ONLY=NOT_AUTHORIZED`

Giữ nguyên scientific invariants `R7=FROZEN_FAIL`, `R8=NOT_GENERATED`, `G3/G4=NOT_EXECUTED`, `G5/G6=SEALED`, `READER=0`, `GPU=NO`, `PROBE256=SEALED`. Không chạy QA lịch sử, khoa học, model, blind rating, TEST hoặc GPU. Không sinh candidate/gold/fold/key; không thay đổi G0 implementation, protected ACL, chính sách hoặc main. Báo cáo này là biên nhận G2 public-safe cho lượt xác minh hiện tại, không đóng vai trò attestation private custodian.

**Bước thực hiện tiếp theo** — trong cổng G2 hiện hữu, authorized custodian liên kết approved protected source root và execution identity với exact commit `84d9d5c...`, cung cấp receipt riêng tư cho effective ACL, persistence, 5 protected-runtime SHA-256 và readiness của HMAC/immutable pre-G3 commitment. Chỉ sau khi chứng cứ đó tồn tại mới phân xử tích hợp trên các gate đã khóa.

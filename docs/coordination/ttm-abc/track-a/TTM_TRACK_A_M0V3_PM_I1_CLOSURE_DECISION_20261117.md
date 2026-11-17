# PM DECISION — Track A M0 v3 · Đóng I1 về mặt đo lường

**Ngày:** 2026-11-17  
**Nguồn quyết định:** PM/owner trao quyết định trong cuộc hội thoại, được Agent A ghi nhận trên GitHub; đây là bản ghi nhận quyết định, **không phải chữ ký mật mã (cryptographic sign-off)**.  
**Repository:** `minhtri22/TokenToModel-Lab` · **Branch:** `research/ttm-track-a-small4m-diagnosis-20261116` · **Draft PR:** [#33](https://github.com/minhtri22/TokenToModel-Lab/pull/33).

## 1. Quyết định đã khóa

**PM ACCEPTS: `I1_PASS_SCOPED_MEASUREMENT`.**  
**`I1_MEASUREMENT_CLOSED · I2_RELEASE_HOLD · I2_NOT_EXECUTED · NO_MERGE`.**

Phán quyết I1 áp dụng **duy nhất cho phép đo M0 v3** tại exact source SHA:

`ec197b5f00d3a037420390edd11ee55047e1d37f`.

Sau exact source commit trên, commit độc lập `e3e1c802815f4db1534e92d9848d6015eb9203cc` chỉ thêm bốn file evidence; commit ghi trạng thái/PM handoff `771314c07ba061ebeb1baa87018248ed73181079` không sửa source đã được review. Kết quả QA của tác giả không thay thế kiểm toán độc lập.

### Bằng chứng chấp nhận

- [Independent re-review](https://github.com/minhtri22/TokenToModel-Lab/blob/e3e1c802815f4db1534e92d9848d6015eb9203cc/artifacts/ttm-abc/track-a/M0_V3_POST_HOLD_DISTINCT_I1_20261117/REVIEW.md): **F01/F02 35/35 PASS** (NLL ổn định ở 2.048 logits float32 lớn; thực thi từ source buffer đã hash, không tin `.pyc`).
- [Sanitized receipt](https://github.com/minhtri22/TokenToModel-Lab/blob/e3e1c802815f4db1534e92d9848d6015eb9203cc/artifacts/ttm-abc/track-a/M0_V3_POST_HOLD_DISTINCT_I1_20261117/receipt.json): **native custody 38/38 PASS; case digest 80/80, group digest 5/5 PASS**; readback-only trên Windows PowerShell 5.1 / Python 3.12.
- Real T1 BPE TRAIN-only SHA-256: `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc`.
- Frozen private fixture SHA-256: `823a08dd4be0da7748cb258b9bf5b2841dd1fdbac84956eb204be7ba57f8c55d`. Frozen manifest SHA-256: `0b80368a6747994df5f5b8d0e7b35137266ac82f6c9b83d26af5b61f79b3cb04`.
- Independent historical `HOLD_I1` (commit `05041501bfe84822feffd39290c6800b2152055a`) **giữ nguyên trong lịch sử**. PASS mới không sửa hồ sơ thất bại cũ.

## 2. Hai blocker phát hành — KHÔNG đảo ngược I1

**BR-I2-01: stale owner-internal I1 decision pointer.** `release-preflight` vẫn kết thúc mã **2**, lý do `HOLD_OWNER_INTERNAL_I1_NOT_PASS` vì tham chiếu phán quyết I1 lịch sử. Đó là ranh giới quyền phát hành; **không sửa release guard, không đổi trust anchor, không gán I2 GO chỉ để preflight PASS**. Một tham chiếu I1 mới chỉ được thiết kế và chấp nhận theo hợp đồng owner/release riêng và có bằng chứng byte-exact.

**BR-I2-02: OnePack receipt TOCTOU.** Trình tự kiểm tra đích rồi ghi receipt chưa nguyên tử; wrapper ghi SHA freeze receipt nhưng chưa tự khóa toàn bộ dữ liệu custody và kiểm reparse point, một phần do checker độc lập bù trong lượt I1. Cần thiết kế và kiểm chứng tính nguyên tử của sản phẩm mới trước khi coi là sẵn sàng phát hành; **không tái đóng băng fixture**, không thay đổi các byte đã kiểm toán.

Các blocker này là **release readiness**; không phải lỗi mới của phép đo I1 và không yêu cầu chạy lại M0 v3.

## 3. Phạm vi không được suy diễn

`I1_PASS_SCOPED_MEASUREMENT` không phải `I2_GO`, không chứng minh năng lực khoa học của mô hình, không chứng nhận kết quả TEST hay FINAL24, không cho phép checkpoint access, model forward, optimizer, nonce claim, merge PR #33, merge PR #28 hoặc sửa `main`/`lineage.md`.

**Tính đến closure:** I2 = `NOT_EXECUTED`; model forward = 0; optimizer steps = 0; checkpoint accesses = 0; nonce claims = 0. PR #33 vẫn Draft.

## 4. Bước thực hiện tiếp theo — duy nhất

`TTM_TRACK_A_I2_RELEASE_BARRIER_TOCTOU_ATOMICITY_AND_OWNER_AUTHORITY_DESIGN_SINGLE_GATE`

Một lượt **DESIGN/SOURCE-ONLY**, không khoa học: lập hợp đồng cho (a) chuyển nguồn phán quyết I1 đã được PM chấp nhận vào release authority theo quy trình owner hợp lệ, **không bypass**, và (b) ghi receipt nguyên tử, từ chối symlink/reparse, ghim snapshot SHA và idempotence/no-overwrite. Dự kiến điều kiện QA độc lập và tiêu chí STOP/HOLD, không cấp quyền chạy I2 hay sửa release guard trong lượt đóng I1 này.

**Final:** `I1_MEASUREMENT_CLOSED · INDEPENDENT_QA_PASS · RELEASE_PREFLIGHT_HOLD · I2_NOT_EXECUTED · PR33_DRAFT · NO_MERGE`.

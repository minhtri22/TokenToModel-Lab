# A0E — Sửa đổi tiền đăng ký hai bên, chuẩn hóa P/N và kiểm soát projector

**Operation:** `TTM_GEMMA2_A0E_TWO_PARTY_PROCEDURAL_BLINDING_AND_CAUSAL_CONTROL_SINGLE_AMENDMENT`  
**Ngày:** 2026-11-11  
**Nhánh:** `research/ttm-gemma2-token-alignment-pretraining-causality-20261111`  
**Loại:** **AMENDMENT V1, PROSPECTIVE, SOURCE-ONLY — NO SCIENCE OUTCOMES READ**  
**Nguồn hợp đồng gốc bất biến:** `docs/pilot/TTM_GEMMA2_A0E_FRESH_LEXICAL_HUMAN_RATED_4ARM_PROSPECTIVE_PREREG_FREEZE_DESIGN_ONLY_20261111.md`, Git blob `d6e5d82709b2bc31458f73e7720cdae1e5f5e54e`.  
**Phán quyết hiện tại:** `AMENDMENT_DESIGN_ACCEPTED_SCOPED` / `T4_2X2=NO_GO_HOLD`.

## 0. Vấn đề nghiên cứu và mức độ khẳng định

Mục tiêu trước mắt là thăm dò xem sự liên kết token–residual **gắn với nguồn pretraining (pretraining-associated)** có giúp TTM hay không. Không đặt tiêu chuẩn xác nhận “pure semantic causality” cho pilot ba seed. SimVerb-3500 có human judgments nhưng công khai từ 2016: không thể loại trừ dữ liệu benchmark trong pretraining donor. Người chủ và trợ lý không phải người giữ nhãn độc lập với nhau.

Giữ nguyên bốn nhánh `P-A/P-C/N-A/N-C`; TRAIN seeds `41031/41032/41033`, N init `61031/61032/61033`, null `51031/51032/51033`; `4×3×512×4096=25,165,824` target-token presentations; frozen TRAIN/VAL và (D_origin=[NLL(P-C)-NLL(P-A)]-[NLL(N-C)-NLL(N-A)]). Không lấy kết quả TEST/H768/OOD256 hoặc SimLex/WordSim đã tiêu thụ. Không đổi các ngưỡng đã công bố (`D_origin>0` cả ba seed; mean `>=0.02` nats/token; `D_align>0` cả ba), chúng là ngưỡng thăm dò, không phải p-value hoặc kiểm định alpha 0,05.

## 1. Thay thế người giữ nhãn thứ ba — phạm vi PILOT ONLY

**Bỏ điều kiện bắt buộc `EXTERNAL_GOLD_CUSTODIAN_SIGNATURE` khỏi pilot A0E.** Thay bằng `TWO_PARTY_PROCEDURAL_BLINDING` với các điều kiện một lần:

1. Khóa hợp đồng A0E gốc và amendment này theo Git SHA; khóa roster private 138 cặp / core 37 cặp theo SHA, và nguồn gold Cambridge SHA `b58f68454cf9354b94ecd8bfd778ff2cc784a25fc7dca02bc695319ad2b4157e`. Gold **không được đọc** trong quá trình chọn nguồn, chỉnh P/N hoặc chốt training code.
2. Khóa mã scorer lexical và NLL, source/optimizer/VAL roster, tất cả thay đổi chuẩn hóa và projector trước khi chạy. Người chủ ghi tuyên bố không sử dụng gold/NLL để lựa chọn phương án.
3. Sau **đúng một vòng** pilot, lưu **12 tệp kết quả** cố định `seed41031__P-A.json` ... `seed41033__N-C.json`; ghi SHA256, kích thước, source/manifest hash vào receipt chỉ đọc, không ghi đè. Chứng thực receipt bằng một **Git commit xác minh được trước khi mở gold**. Việc nhập một chuỗi commit SHA không đủ để chứng minh commit đã tồn tại; phải độc lập đọc lại commit và receipt.
4. **Chỉ khi đủ 12 kết quả đã khóa**, mở gold bằng scorer cố định, ghi thời điểm, nhánh/commit và người thực hiện. Không được thay subset/seed, scorer, mô hình hay thresholds sau khi xem nhãn hoặc NLL.
5. Giữ lại receipt gốc, trường `EXTERNAL_CUSTODIAN=NONE`, và log mọi truy cập. Không gọi đây là third-party blind audit. Vì gold công khai, thủ tục này kiểm toán thứ tự thao tác trong dự án, **không thể chứng minh chưa ai từng xem gold ngoài dự án**.

**Quan trọng:** Không cần 12 output khi *đang xin phép pilot*, vì output chỉ sinh ra sau thực thi; trước GPU cần mã khóa, scorer, chính sách và QA fail-closed PASS, rồi thực tế khóa sau khi chạy. Không tự đánh đồng `gold_custody=HOLD` của hợp đồng cũ với “thiếu người thứ ba là lỗi khoa học”: gate đó đã được **amended** và chỉ còn là thủ tục kiểm soát thứ tự.

## 2. Chuẩn hóa scalar P/N — phương án trước outcome

Nguồn private đã được kiểm 3/3 N→T1 và 6/6 P-C/N-C null trước amendment (không chạy lại). P và N có median row-norm ratio `2.210338–2.212920`; covariance trace ratio `4.774143–4.780100`. Đề xuất một thay đổi **được khóa trước NLL**:

Đối với từng seed `s`, chỉ tính từ **1.917 T1 mapping hợp lệ** và TRAIN-source frozen, không đọc nhãn:
```
alpha_s = median(||N-A_s[token]||_2)/median(||P-A[token]||_2)
P-A'_s = alpha_s * P-A
P-C'_s = alpha_s * P-C
N-A'_s = N-A_s
N-C'_s = N-C_s
```

Áp dụng **một hệ số giống nhau** cho P-A/P-C trong block seed; cùng projector `P0` ban đầu cho cả P/N, và 131 fallback/special IDs giữ đúng quy tắc cũ, không tự ý chuẩn hóa. Không biến đổi theo token, không fit nhãn, không thay tokenizer và không dùng `VAL` để fit.

Từ **các thống kê gốc của ba seed, chưa đo tensor mới**:  
- `alpha_s` từ `0.4518916284` đến `0.4524194705`;  
- median mapped-row norm P/N sau scalar = 1 **theo định nghĩa**;  
- tỷ lệ covariance *trace* sau scalar nằm trong `0.9749089215–0.9773489490`, tương ứng sai khác 2,3–2,5% của trace;  
- pairwise cosine của P không thay đổi dưới `alpha>0`; covariance-relative A/C không thay đổi đại số nếu nhân cùng `alpha`.

**CHƯA ĐẠT:** scalar không đối sánh covariance **ma trận**, effective rank/eigen-spectrum, phân phối từng row norm, TRAIN-only frequency/morphology/length SMD, gradient với projector đang train, hay tất cả T1 fallback. Phải chạy **một lượt QA nguồn private mới cho biến đổi đã sửa**, xuất SHA của 6 ma trận scaled P (P-A'/P-C' theo ba seed) và các đại lượng trước pilot. Không tuyên bố trước rằng `P/N_MATCHED=PASS`.

## 3. Projector: thay đổi phạm vi kết luận, không thêm GPU mù quáng

A0B constrained null thỏa `X_A P0^T = X_C P0^T` tại bước 0. Nếu **P0 frozen** thì toàn bộ luồng vào mạng bằng nhau, và mọi chênh lệch A/C do residual là bằng 0 theo cấu trúc, với các điều kiện khởi tạo và train deterministic khác giữ cố định. Nếu **P0 trainable**, chênh lệch `dL/dP` có thể xuất hiện dù giữ nguyên gram của nguồn; phép kiểm toán CPU trước đó đã cho gradient relative difference `1.5336064` trong một negative control không phá pairwise Gram.

Vì vậy, phép thử bốn nhánh đo **pretrained-origin-specific learnability through trainable projection**, không nhận diện “pure semantics”. Giữ `P0` **trainable** như hợp đồng chính, không tự biến frozen-projector thành thêm 4 arm GPU ngoài ngân sách. Thêm kiểm soát toán học preexec `FROZEN_PROJECTOR_ZERO_EFFECT` (không GPU); nếu owner muốn kiểm định cơ chế sâu hơn sau pilot, tiền đăng ký một thí nghiệm kế nhiệm trên dữ liệu chưa tiêu thụ.

## 4. Đánh giá mã runner/scorer

- Scorer NLL bốn nhánh nguồn đã khóa: `tools/embeddinggemma2_swap/semantics_origin_a0/ttm_a0e_fourarm_independent_scorer_v1.py`, Git blob `88ea6af212b2ebaab60e4c208390113882611f34`. Synthetic QA PASS tại Actions `43046304992`; **chưa có scorer lexical hoàn chỉnh được QA trên dữ liệu mù**, và chưa chạy VAL/NLL.
- Runner v1 `ttm_a0e_fourarm_preexec_runner_contract_v1.py` là guard chưa có đường training, còn hardcode yêu cầu external custodian. Không sửa/xóa file này; bổ sung **v2** hỗ trợ two-party procedural gate, chỉ yêu cầu chứng thực SHA tệp thực tồn tại, nguồn đúng và quyền owner.
- Bộ khóa đầu ra 12 arm×seed phải PASS negative QA: thiếu/sửa output, thay manifest, ghi đè lock, mở gold quá sớm đều HOLD.
- **Pilot trainer đầy đủ**, optimizer, sampler, resume, checkpoint baseline, fresh VAL IDs, raw TinyStories rights/near-duplicate và official pretrained weight extraction **chưa đóng**. Không được dùng runner six-arm CAUSAL6 thay cho A0E.

## 5. Cổng T4 duy nhất, KHÔNG cấp quyền trong amendment

GO chỉ có thể được cân nhắc khi, trong một packet: (a) source P/N sau scalar và spectral/shape/frequency/morphology QA PASS, hashes mới pin; (b) blind lock và independent scorer source QA PASS; (c) official P/N provenance, TRAIN/VAL raw rights + no-near-duplicate PASS; (d) source code huấn luyện **thực sự chạy được**, source checkpoint, optimizer/sampler/seed/VAL SHA fixed; (e) preflight T4 resource & owner-specific approval, không có model outcomes bị peek. Chỉ dùng một lần phán quyết, không tạo micro-permits.

**Phán quyết amendment:** `EXTERNAL_CUSTODIAN_REQUIRED=NO_FOR_PILOT` · `PROCEDURAL_BLINDING_DESIGN=FROZEN_SOURCE_QA` · `SCALAR_NORMALIZATION_DESIGN=FROZEN_AGGREGATE_FEASIBLE` · `P_N_FULL_SOURCE_MATCH=HOLD` · `FULL_RUNNER_AND_RIGHTS=HOLD` · `SCIENCE_ADMISSION=NO_GO_HOLD` · `T4_2X2=HOLD_NO_GPU`.

**Bước thực hiện tiếp theo:** `TTM_GEMMA2_A0E_TWO_PARTY_SOURCE_NORMALIZED_PN_AND_REAL_RUNNER_FINAL_ONE_PACKET_PREEXEC`. Không tái kiểm A0D/20/20/16/16/3/3/6/6 đã PASS; chỉ thực hiện normalized-source QA mới và hoàn thiện trainer/rights cần thiết. Không đổi `main`, không viết `lineage.md` hay tạo L0022 khi chưa có kết quả khoa học.

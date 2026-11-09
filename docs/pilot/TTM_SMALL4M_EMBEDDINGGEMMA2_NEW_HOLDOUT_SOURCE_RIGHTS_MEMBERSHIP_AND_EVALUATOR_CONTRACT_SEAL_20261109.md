# TTM-Small-4M × EmbeddingGemma 2 — Cổng nguồn, quyền, danh sách truyện và bộ chấm độc lập

**Ngày:** 09/11/2026. **Mã công việc:** `TTM_SMALL4M_EMBEDDINGGEMMA2_NEW_HOLDOUT_SOURCE_RIGHTS_MEMBERSHIP_AND_EVALUATOR_CONTRACT_SEAL`.

**Kết luận thực tế:** `PASS_SCOPED_SYNTHETIC_SOURCE_CONTRACT` · `HOLD_REAL_MEMBERSHIP_SEAL` · `MODEL_BINDING=NOT_CONNECTED`. Chưa chạy suy luận trên 320 truyện mới, chưa chạy GPU/huấn luyện, chưa ghi khoa học vào `lineage.md`.

## 1. Bằng chứng nguồn trên máy Windows và GitHub

Đã đọc GitHub nhánh `research/ttm-small4m-embeddinggemma2-token-swap-minimal-proof-20261109` tại commit `fcb71a2c5bcfe81e98ad10692273251577644b0f`; đã kiểm tra qua kết nối RemoteDesktop chế độ liệt kê/đọc tệp. Những đường dẫn sau **tồn tại** dưới `D:\WORK\RESEARCH\TokenToModel-Lab`:

- `datasets/tinystories_v1_original_pinned/TinyStories-train.txt` và `TinyStories-valid.txt`.
- `_tmp/ttm_t1_real_source_v1/T1_STORY_SPLIT_IDS_NO_RAW_TEXT.json`; `T1_BPE2048_REAL_TRAIN_MANIFEST.json`.
- `_tmp/ttm_t4_data_pack_v1/T4_PRIVATE_PACK_MANIFEST.json`.

Bằng chứng lịch sử T1 đã ký: TRAIN quét 2.119.489 truyện; VALID gốc 21.990; va chạm SHA nguyên bản giữa VALID và toàn TRAIN 6.601; tập pilot 2.048 TRAIN / 256 VALIDATION / 64 TEST. T1 đã độc lập PASS trong phạm vi nguồn/T1; kiểm tra trùng gần đúng trước đó **chỉ bao phủ nhóm pilot đã chọn**, không phải toàn bộ TRAIN đối với một tập VALIDATION mới.

Tập dữ liệu ghim `roneneldan/TinyStories@f54c09fd23315a6f9c86f9dc80f725de7d8f9c64`; SHA-256 tệp TRAIN `c5cf5e22ff13614e830afbe61a99fbcbe8bcb7dd72252b989fa1117a368d401f`, tệp VALID `94e431816c4cce81ff71e4408ff8d3bda9a42e8d2663986697c3954288cb38b4`. Manifest T1 split SHA-256 `9f2ebaca821bddf0a9d7ae30ccfcef34561b968b21159aa913794298235a2fa9`; BPE chỉ huấn luyện trên TRAIN SHA-256 `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc`.

**Ranh giới xác minh:** lượt rà soát hiện tại chỉ xác nhận sự tồn tại của tệp Windows. Lệnh thực thi từ xa trả `managed mode requires task_job_submit`, nên **chưa băm lại byte của các tệp lớn**, chưa quét/dedup 320 truyện. Không tuyên bố đã niêm phong một tập thực tế.

## 2. Cổng quyền sử dụng dữ liệu

[Thẻ dữ liệu TinyStories](https://huggingface.co/datasets/roneneldan/TinyStories) ghi `cdla-sharing-1.0`. [CDLA-Sharing-1.0](https://cdla.dev/sharing-1-0/) cho phép sử dụng, phân tích và dùng tính toán (computational use) theo các điều kiện của thỏa thuận. Khi công bố dữ liệu hoặc dữ liệu bổ sung phải xét yêu cầu giữ giấy phép, thông báo thay đổi và ghi nguồn. Không công bố dữ liệu truyện gốc, cửa sổ token đảo ngược, danh sách riêng tư của TEST, checkpoint hoặc loss theo truyện trên GitHub. Không xem việc có giấy phép nguồn là một bảo đảm pháp lý về mọi nội dung truyện hoặc sản phẩm thương mại.

**Trạng thái:** `LICENSE_CARD_AND_TEXT=PASS_FOR_INTERNAL_COMPUTATIONAL_USE_WITH_CONDITIONS`; `FINAL_SOURCE_SCOPE_AND_PUBLICATION_RIGHTS=HOLD` trước khi công bố hoặc dùng cho sản phẩm.

## 3. Quy tắc chọn nguồn và chống trùng — sửa đổi thiết kế trước khi đánh giá

So với **thiết kế chưa thực thi** ngay trước bước này, khóa rõ quy trình lấy **640 ứng viên đầu** để sau khi loại trùng gần đúng vẫn có thể chọn đủ **320 truyện** theo cùng thứ tự cố định. Đây là **sửa đổi hợp đồng kỹ thuật trước niêm phong**, không phải thay kết quả khoa học.

- Dùng đúng bộ phân tách truyện (story parser) T1, đọc nguồn VALID gốc và băm SHA-256 raw story trước khi giải mã. Loại mọi truyện khớp SHA với toàn bộ TRAIN hoặc có ID thuộc 2.048 TRAIN / 256 VAL / 64 TEST cũ. Không giải mã truyện thuộc danh sách TEST cũ để tạo ứng viên.
- Loại cả nhóm được quy hoạch vào bucket TEST lịch sử bằng `SHA256(TTM_SMALL4M_20261108_STORY_HASH_V1|story_sha) mod 5 == 0`. Điều này chặt hơn loại 64 thành viên TEST đã chọn.
- Xếp hạng các truyện đủ điều kiện theo `SHA256(TTM_GEMMA2_2048_NEW_HOLDOUT_V1|story_sha)`, tăng dần; chỉ giữ 640 ứng viên đầu, không dựa trên kết quả dự đoán.
- Đối với 640 ứng viên: đối chiếu **toàn bộ 2.119.489 truyện TRAIN**, không lấy mẫu, bằng các tập 5 từ `text.casefold().split()`, ngưỡng Jaccard **≥0,85**. Bộ chỉ mục đảo (inverted index) chứa đầy đủ 5-gram của ứng viên; so khớp chính xác, không dùng bộ tìm xấp xỉ (LSH) có nguy cơ bỏ sót.
- Từ danh sách đã xếp hạng, bỏ mọi ứng viên gần trùng TRAIN, rồi bỏ ứng viên gần trùng các truyện mới đã chọn; giữ 320 truyện đầu. Không đổi thứ tự, seed, số truyện hay ngưỡng nếu không đủ. Thiếu → `HOLD_INSUFFICIENT_NEW_STORIES`.
- Dùng chính BPE 2.048 ID đã khóa trên TRAIN để tính số nhãn; mô phỏng quy tắc T4 `input_ids=BPE(text)+EOS`, số nhãn hợp lệ `len(BPE(text))`. Yêu cầu tối thiểu **50.000 nhãn**. Không chấm bằng bất kỳ mô hình nào ở bước niêm phong.
- Chỉ khi tất cả PASS mới ghi `MEMBERSHIP_PRIVATE.json` dưới `_tmp/ttm_gemma2_new_holdout_membership_v1_20261109` chứa ID/mã băm và số nhãn riêng tư; ghi `SOURCE_SEAL_PUBLIC.json` chỉ chứa thống kê và SHA-256 private manifest. Từ chối ghi đè output đã tồn tại, không tiết lộ ID trong báo cáo công khai.

**Lưu ý hiệu năng:** quét hai lần tệp TRAIN gần 1,92 GB, lưu danh sách SHA và bộ chỉ mục 5-gram của ứng viên; đây là kiểm toán trên CPU toàn bộ nguồn, không phải thử nghiệm siêu nhỏ hay GPU. Cần quan sát RAM và tình trạng đĩa Windows khi chủ dự án chạy. Nếu vượt tài nguyên, ghi HOLD và lập phương án tương đương trước khi kiểm tra NLL.

## 4. Mã nguồn khóa và QA tổng hợp

| Hạng mục | SHA-256 nguồn | Kiểm thử |
|---|---|---|
| [Bộ chọn truyện/chống trùng](tools/embeddinggemma2_swap/ttm_gemma2_holdout_seal.py) | `0f494cc4efbfdb6aa6e8f04825ec1dda929c836a1ac981463f24eb2bd8d9c8e4` | **14/14 PASS** |
| [Bộ chấm NLL CPU độc lập](tools/embeddinggemma2_swap/ttm_gemma2_independent_cpu_scorer.py) | `de6ab9652bb690a6e967e752b9367f5755674a23a6c4b2fcb45941274612dfe1` | **12/12 PASS** |

Đã thực thi `--mode fixture-qa` bằng CPU Linux Python 3.13.5; phần chấm dùng PyTorch 2.10.0+cpu, không nạp checkpoint thực, không đọc dữ liệu riêng tư và không chạy GPU. Bộ chấm bảo đảm nhãn `NEW_HOLDOUT` mới, chặn VALIDATION/TEST cũ, xử lý mặt nạ nhãn `-100`, tính tổng NLL theo truyện bằng độ chính xác float64 và từ chối đầu vào/logits không hữu hạn.

**Giới hạn:** bộ chấm là hợp đồng chấm điểm và tính NLL có kiểm thử tổng hợp; **chưa liên kết bộ dựng model A/B/C/D thật**, chưa kiểm tra sự tương đồng với phép chấm GPU thực tế. Windows Python 3.12 QA và cả bốn checkpoint nạp CPU còn phải kiểm tra trước thí nghiệm xác nhận.

## 5. Kết luận và cổng kế tiếp

| Hạng mục | Trạng thái |
|---|---|
| GitHub source pin, chứng cứ lịch sử T1 | PASS lịch sử |
| Sự hiện diện nguồn Windows | PASS_PRESENCE_ONLY |
| SHA tệp nguồn hiện tại | HOLD_CURRENT_READBACK |
| Quyền dùng tính toán nội bộ | PASS_WITH_CONDITIONS |
| Chống trùng 320 truyện thật | NOT_EXECUTED |
| Danh sách thành viên thực đã niêm phong | NOT_SEALED |
| Kiểm thử tổng hợp bộ nguồn + bộ chấm | PASS_26_OF_26 |
| Kết nối bộ chấm với mô hình thật | NOT_CONNECTED |
| TRAIN hoặc đánh giá tập mới | NOT_EXECUTED |
| GPU | NOT_USED |
| `lineage.md` | UNCHANGED |

**Công việc sau bước này:** `TTM_SMALL4M_EMBEDDINGGEMMA2_NEW_HOLDOUT_WINDOWS_SOURCE_SEAL_READBACK_AND_INDEPENDENT_CPU_MODEL_BINDING_QA`. Chỉ kiểm tra nguồn/niêm phong manifest và kỹ thuật bộ chấm; chưa tính NLL trên tập mới. Mọi kết quả khoa học PASS/FAIL sau này mới được nối thêm vào `lineage.md`.

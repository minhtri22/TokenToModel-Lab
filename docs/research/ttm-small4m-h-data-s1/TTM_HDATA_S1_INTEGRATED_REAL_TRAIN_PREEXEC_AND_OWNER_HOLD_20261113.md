# TTM-Small-4M H-DATA-S1 — tiền kiểm tích hợp trên metadata TRAIN gốc và một quyết định owner GO/HOLD

**Operation:** `TTM_HDATA_S1_ONEPACKET_SAMPLER_SOURCE_REAL_METADATA_QA_RIGHTS_T4_RESUME_AND_OWNER_GO_HOLD_PREEXEC_NO_TRAIN`  
**Ngày:** 2026-11-13 (Asia/Bangkok).  
**Nhánh:** `research/ttm-small4m-h-data-s1-matched-budget-prereg-20261113`.  
**Prereg đã khóa trước lượt này:** `docs/research/ttm-small4m-h-data-s1/TTM_HDATA_S1_MATCHED_BUDGET_PREREG_DESIGN_20261113.md`.  
**Phán quyết một cổng:** **`HOLD_NO_GO_TRAINING_PENDING_NEW_RIGHTS_T4_RUNNER_RESUME_AND_NEW_BLIND_ESCROW`**.  
**Phân loại:** `SOURCE_ONLY_REAL_TRAIN_METADATA_AND_CPU_PREEXEC`, **không phải kết quả thí nghiệm huấn luyện/inference**.

## 1. Nguồn nguyên gốc: byte custody PASS

Tải trực tiếp tệp trong Google Drive private đã có từ thí nghiệm T4, không tái tạo/reseed dữ liệu và không dùng TEST:

| Nguồn | SHA-256 đã xác minh |
|---|---|
| `T4_PRIVATE_TRAIN_VAL_WINDOWS.npz` | `184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913` |
| `T4_PRIVATE_PACK_MANIFEST.json` | `ef2e6e67d49b1d5a921b1051df329f15574f1c10cece0ce49468acb53322d650` |
| `checkpoint.pt` tại P02 `step_1024` | `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b` |
| `T4_SCIENCE_LOCK_A2_1024.json` | `fd183ade2a696d40313aae19b63429d4ef3edd8abf25c899c8cc496836d36817` |
| `T1_BPE2048_REAL_TRAIN_MANIFEST.json` | `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc` |
| `DEV12` public source | `60e514a2329abe6b6df673058ee7656bb57287758c6ee4cc861a396a1788ba3d` |

Nguồn NPZ là pack có **2.048 TRAIN stories, 2.691 TRAIN windows, 498.287 nhãn đích TRAIN**; manifest gốc xác nhận không chứa TEST. Mã chỉ giải nén hai mảng metadata **`train_count.npy`, `train_story_index.npy`**; không giải nén/đọc `train_x`, `train_y` hay bất cứ mảng VAL nào. Đọc byte toàn pack chỉ để hash toàn vẹn, không diễn giải nội dung token. `torch.load(..., weights_only=True, map_location='cpu')` được dùng để đọc *trạng thái* checkpoint/sampler, không khởi tạo GPT, không model-forward hoặc optimizer step.

Các kiểm tra khi cố ý sửa một byte của ba nguồn (pack, checkpoint, manifest) đều bị từ chối. Checkpoint P02-1024 chứa nguyên bản optimizer, scheduler, scaler, RNG và sampler state. Chữ ký quyền nghiên cứu trước: `RIGHTS_OWNER_SIGNED.json` có **`internal_A_C_only=true`**; xác nhận đó **không chuyển tiếp** sang H-DATA-S1.

## 2. Real TRAIN metadata sampler — PASS đúng hợp đồng matched budget

Cùng một **checkpoint P02 bước 1.024**, `H0` khôi phục `torch.Generator` từ `sampler_state`; **128/128** số cửa sổ mỗi bước giống biên nhận metadata A/C trước (`REAL_METADATA_MATCHED_DRAWS_READONLY_20261110.json`, Git blob `39fcf5810a81877d19abeabc9dae7434d63827b9`). Không lấy kết quả FINAL làm input quyết định.

Chính sách H1 theo **đúng thứ tự khóa từ tiền đăng ký**: chọn từ cửa sổ TRAIN đủ `count >= scored_count` của lượt H0; ưu tiên số lần xuất hiện truyện ít nhất, tiếp đó cửa sổ đầu truyện, sau đó hạn chế thay cửa sổ gốc; phá hòa với `SHA256(run_id|step|draw|candidate_window|seed)` và seed `20261113`. Giữ nguyên số nhãn đích của từng lượt, cắt/mask phần nhãn dư bằng `-100` khi chạy trainer thật (chưa chạy). Không thay loss/VAL/model.

| Chỉ số | H0 — original sampler | H1 — story coverage + early context |
|---|---:|---:|
| Số bước dự kiến | 128 | 128 |
| Nhãn hợp lệ mỗi bước | 4.096 | 4.096 |
| Tổng lượt nhãn | **524.288** | **524.288** |
| Cửa sổ forward | **2.928** | **2.928** |
| Tensor slots (256 vị trí/cửa sổ) | **749.568** | **749.568** |
| Số truyện TRAIN độc nhất | 1.493 | **2.048** |
| Tỷ lệ cửa sổ đầu truyện | 75,9904% | **100%** |

- Độ phủ truyện tương đối H1 so với H0: **+37,1735%**, lớn hơn ngưỡng **+5%**.
- Tỷ lệ cửa sổ đầu truyện: **+24,0096 điểm phần trăm**, lớn hơn ngưỡng **+10 pp**.
- Số lượt cửa sổ thay đổi: **1.567/2.928**. Cả 128 bước có đúng target count và số forward slots cặp tương ứng.
- Resume lịch sampler theo **64 bước + 64 bước** khớp SHA và trạng thái RNG/stored story-exposure với chạy liên tục. Đây là **metadata-schedule resume**, **không phải train resume parity**.
- Bộ kiểm toán triển khai khác của cùng trợ lý đạt **3.205/3.205 PASS**, gồm **128/128** kiểm tra số draw của H0 theo biên nhận lịch sử, **128/128** ngân sách từng bước, **2.928** cặp cửa sổ đúng số nhãn và **5** negative fixtures. Đây không phải human/external independent scientific reviewer.

**Giới hạn quan trọng:** H1 hiện chọn **100% cửa sổ đầu truyện**, tạo một **dịch chuyển phân bố (distribution shift) lớn**, có thể làm giảm việc tiếp xúc phần giữa/cuối truyện. Hai điều kiện thao tác đạt PASS nhưng không chứng minh tăng bám prompt. Nếu H1 có lợi về sau, chỉ quy cho **chính sách lấy mẫu tổng hợp**, không kết luận riêng về story coverage hay early-context. Cấm tinh chỉnh policy dựa trên bộ FINAL đã khóa.

## 3. BPE/context và checkpoint/resume: PASS từng phần

- BPE manifest source sha PASS, internal manifest digest, 1.791 merges/vocab 2.048 và token merges SHA PASS; triển khai shadow độc lập thực hiện roundtrip **12/12 DEV**. Độ dài `DEV` **36–52 token BPE**; cộng 64 token sinh đều nhỏ hơn context 256. **Không đọc 24 FINAL rõ chữ trong lượt này.**
- Checkpoint parent `step=1024`, 53 nhóm tham số mô hình, `optimizer.state.step=1024`, scheduler `last_epoch=1024`, grad scaler, RNG đầy đủ; **CPU readonly copy state không alias optimizer-step storage: PASS**. Không xây dựng model đối tượng, không train, không kiểm VAL NLL mới.
- Đã chuẩn bị cell runner Colab **NO TRAIN / NO FORWARD**, yêu cầu Tesla T4 + Torch `2.14.1+cu130` và đối chiếu source SHA/lịch sampler mới. Test trên CPU không có CUDA: **đã HOLD đúng và không tạo receipt giả**. **Chưa thực thi cell trên Colab T4**, nên `T4_RUNTIME_SOURCE_PIN=NOT_EXECUTED`.
- **Chưa có runner huấn luyện H0/H1 tích hợp** và **chưa có parity interrupted/resume của AdamW/scheduler/FP16 scaler + model** trên T4. Không được nâng một QA của metadata thành PASS toàn bộ trainer.

## 4. Quyền, chấm mù và dữ liệu FINAL

- Quyền owner: phiếu cũ chỉ được cấp cho **A/C**, H-DATA mới chưa có xác nhận riêng `OWNER_HDATA_S1_NEW_TRAIN_GO=YES` và không được suy diễn từ yêu cầu làm tiền kiểm. **HOLD.**
- `HF01–HF24` mới đã được cam kết SHA từ lượt DESIGN_ONLY, file owner-private SHA `b129a5c52520a25f1c40de950471622320abfa6b5414d0b16e0111ed96adc680`; lượt này **không mở nội dung FINAL**. Không dùng FINAL24 A/C, H-DEC NEXT24, Q1/Q2/TEST/OOD để tuning.
- Escrow AES H0/H1 12/12, chia đều 3/3 trên 4 nhóm, **chưa được lập**; bắt buộc freeze trước bất cứ model-forward nào. Người chấm AI có thể nhận gói và chấm **sau sinh**, không cần trước khi train; phải đóng băng **240 điểm nguyên +24 note** rồi owner mới giải mù.
- BPE/context của 24 FINAL và QA model-forward trên runtime thật vẫn là **điều kiện sau**, chưa được khẳng định PASS trong lượt này.

## 5. Formal owner GO/HOLD duy nhất

**`SOURCE_QA=PASS_SCOPED_REAL_TRAIN_METADATA`** · **`MATCHED_BUDGET=PASS`** · **`MANIPULATION=PASS`** · **`BPE_DEV=PASS`** · **`CHECKPOINT_CPU=PASS`** · **`SAMPLER_METADATA_RESUME=PASS`**.

**`TRAINING_RELEASE=HOLD_NO_GO`**, vì **quyền H-DATA mới**, **actual T4 runner + full interrupted/resume parity**, **runtime source pin**, **escrow mới trước forward** còn thiếu. Kết luận GO/HOLD không chia thành các micro-permit; không được gọi sampler metadata QA là science evidence.

Quy tắc kế tiếp: sau khi owner xác nhận quyền và hoàn thành source-only/native runtime QA trên **cùng một gói** (không inference), phát hành đúng **một quyết định science GO/HOLD**, rồi nếu GO mới phát lệnh one-shot train riêng. Không mở lại FINAL để đổi sampler. **Không tự train, infer, merge `main`, hay sửa kết quả quá khứ** trong lượt này.

## Bước thực hiện tiếp theo

`TTM_HDATA_S1_OWNER_RIGHTS_NATIVE_T4_TRAINER_RESUME_AES_ESCROW_SINGLE_PACKET_FINAL_RELEASE_NO_AUTO_TRAIN`

Đóng một gói gồm chữ ký owner H-DATA riêng, runner H0/H1 nguồn ghim, negative QA thật của trainer/resume, Colab T4 source pin, AES mapping 12/12 cho NEW FINAL; phán quyết cuối duy nhất, không auto train. Khi hoàn tất, giữ nguyên các SHA và chỉ có owner mới khởi chạy science one-shot.

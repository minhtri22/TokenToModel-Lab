# A0E — Phán quyết độc lập về nguồn, lưu giữ nhãn và tiền kiểm bốn nhánh

**Ngày:** 2026-11-11  
**Operation:** `TTM_GEMMA2_A0E_INDEPENDENT_SOURCE_LABEL_CUSTODY_AND_PREEXEC_FROZEN_GATE_DECISION`  
**Nhánh:** `research/ttm-gemma2-token-alignment-pretraining-causality-20261111`  
**Phạm vi:** chỉ đọc + kiểm byte nguồn + thiết kế; **không forward, không train, không inference, không GPU, không TEST/H768/OOD256**  
**Quyết định duy nhất:** `NO_GO_HOLD` — không cấp phép chạy T4.

## 1. Cái gì đã thực sự đạt PASS

- **A0D owner-local giữ PASS:** Python 3.12.10, Transformers 5.19.0; official EmbeddingGemma2TextModel; 271.002.624 tham số, 413 tensor; 1.917 T1 mapped, 50 multi-ID, 0 invalid. Receipt SHA `f4c4c0b44d588a876fdc8cf02f9b333820ac244f9c048cf9ee62bcf4d312e81a`. A0D không tải pretrained weights và không forward.
- **Nguồn lexical chính thức PASS:** Cambridge Apollo DOI [10.17863/CAM.9391](https://www.repository.cam.ac.uk/items/8a568201-0fa4-4e54-81b1-f920102492ea) quy định CC BY 4.0. Phép kiểm độc lập trên [GitHub Actions 43014627056](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43014627056) đã tải `simverb-3500-data.zip` từ website Cambridge, và so sánh `SimVerb-3500.txt` với Git mirror đã khóa. Kết luận **PASS chính xác từng byte**.
  - Cambridge ZIP SHA256 `dcd3d5a43724d4e763b9c7f7f28f3785c5cc73e79144346c3b5904c667719530`.
  - Tệp chính thức `SimVerb-3500.txt` SHA256 `b58f68454cf9354b94ecd8bfd778ff2cc784a25fc7dca02bc695319ad2b4157e`, Git blob `769fcdee0ebfae8e37b8ca69241f626a080a75c8`, giống mirror 100%.
  - CI artifact ID `13851922366`, metadata-only receipt SHA256 `31607af478b010f3c9e2a3d1b52d4b1e82c2562153155f80afedbb9d26dec777`. Không công bố nhãn hay dữ liệu mới. Lần chạy đầu `43014563519` thất bại do escaping trong mã kiểm hash Git; mã sửa, chạy lại `43014627056` SUCCESS, không tiêu thụ khoa học.
- **Danh sách lexical vẫn khóa:** ZIP private SHA256 `5680a2e8b39b04eba85629a0851c50f3da18387305221bdfa4a2aa2ab3b7c710`, 138 cặp thuộc 78 từ; tập lõi 37 cặp không trùng từ. SHA roster `8ba5b07bea73cfc6784de940378d5726be9cc8dab2ecc32daa4a5a3555bf91b1`; core `b280478feb9f7359c261944e5c54c7808c96e05bd14558657044fe6f35a2ee2c`. Independent hash/graph `PASS_12_GATES`. Không dùng nhãn vàng để lựa chọn cặp, không đọc kết quả mô hình.
- **Đối chiếu lại gói riêng từ nghiên cứu trước (SHA only):** `TTM_GEMMA2_CAUSAL6_INPUT_PRIVATE_V1_20261109.zip` SHA `2c6cb72f35eba72d6014f15914d6e9792cbf0bf6774d93e3ff5c53e5c6b9ba9a`; `candidate_initialization.pt` SHA `c9fc798d8880c7e76636258052e9885dbb086d7b462a5b6bee5cff8b582973c3`; `T4_PRIVATE_TRAIN_VAL_WINDOWS.npz` SHA `184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913`; `checkpoint.pt` SHA `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`. Đây chỉ là nguồn hiện hữu có SHA đúng, **không có nghĩa tất cả đã được khóa để dùng cho pilot A0E**.
- **Giấy phép các nguồn hiện có:** SimVerb-3500 CC BY 4.0 yêu cầu ghi nguồn; Google EmbeddingGemma 2 Apache 2.0 theo [model card](https://ai.google.dev/gemma/docs/embeddinggemma/model_card_2); TinyStories ghi CDLA-Sharing-1.0 trên [dataset card](https://huggingface.co/datasets/roneneldan/TinyStories), kèm điều kiện [CDLA](https://cdla.dev/sharing-1-0/). Quyền sử dụng để tính toán khác với quyền công bố raw/derived data; không đưa raw TRAIN/VAL hay donor weights lên GitHub.

## 2. Ma trận phán quyết tích hợp (13 cổng)

| Gate | Nội dung | Kết quả |
|---|---|---|
| G01 | A0D official source, class và T1 owner-local | **PASS** |
| G02 | Provenance & CC BY 4.0 của SimVerb | **PASS** |
| G03 | Parity Cambridge official ZIP ↔ mirror GitHub | **PASS** |
| G04 | 138/37 cặp, hash & graph QA không dùng nhãn | **PASS** |
| G05 | TinyStories raw SHA owner và phạm vi quyền phát hành | **HOLD** |
| G06 | Người giữ nhãn độc lập; gold file SHA + log/niêm phong | **HOLD** |
| G07 | Loại trừ SimVerb khỏi dữ liệu pretraining donor | **HOLD** cho tuyên bố ngữ nghĩa nhân quả mạnh |
| G08 | Truy xuất nguồn chính xác của pretrained donor weights và chain-of-custody đầu vào P | **HOLD** |
| G09 | Đóng băng 3 seeded official nonpretrained N tensors, projection và row-pin | **HOLD** |
| G10 | A0B constrained null **đạt ở P-only phạm vi toán học cũ**, nhưng N-C/4-arm matching + selective lexical disruption chưa QA | **HOLD** |
| G11 | Source TRAIN/VAL + checkpoint/optimizer/sampler/scorer 4-arm hoàn chỉnh, không rò rỉ | **HOLD** |
| G12 | Thiết kế, seed, ngân sách, ngưỡng cố định và không peek | **PASS_DESIGN_ONLY** |
| G13 | Phán quyết khoa học một lần trước Colab T4 | **HOLD — NO GO** |

**Tổng:** `5 PASS / 8 HOLD / 0 SCIENCE FAIL`. G07 là giới hạn diễn giải vĩnh viễn của benchmark 2016 nếu không có bộ nhãn mới sau pretraining; không được coi chính SimVerb là dữ liệu "mới được đánh giá độc lập" chỉ vì lần này TTM chưa dùng điểm nhãn.

## 3. Phạm vi của independent label custody

Hiện chỉ khóa **cặp từ** chứ không có receipt được người giữ nhãn độc lập ký chứng thực. Nhãn SimVerb công khai, và việc băm gold file không tạo được điều kiện blind độc lập nếu người chạy mô hình vẫn có quyền mở nhãn.

Hồ sơ niêm phong cần ghi: nguồn Cambridge chính thức và SHA; tên vai trò/đơn vị chấm độc lập; thời điểm niêm phong; gold SHA; kiểm exact pair roster 138/37; khóa nguồn mã scorer, phiên bản thống kê và 10.000 resamples; quy tắc không tiết lộ điểm trước khi khóa đủ P-A/P-C/N-A/N-C; log ai có quyền đọc và khi nào; biên bản QA độc lập. Không công bố điểm nhãn hay tên người nếu chưa cần.

Do benchmark tồn tại từ 2016 và pretraining web có thể đã thấy nó, nhãn công khai chỉ hỗ trợ một phép kiểm **exploratory semantic association**. Muốn khẳng định contamination-free mạnh hơn, cần bộ nhãn mới, được con người đánh giá sau khi đóng băng thí nghiệm, với quyền sử dụng và giữ blind độc lập.

## 4. Hợp đồng 4-arm không được thay đổi sau kết quả

Giữ nguyên `P-A / P-C / N-A / N-C`, ba training seed `41031/41032/41033`, N init `61031/61032/61033`, null `51031/51032/51033`, 512 steps, 4.096 target tokens/bước, tổng 25.165.824 presentations; `D_origin` và `D_align` như hợp đồng A0E.

Không tái sử dụng 44 SimLex, 21 WordSim hay TEST/H768/OOD256; không chọn lại ngưỡng sau khi xem cosine/NLL. 3 seed chỉ sàng lọc, không đủ kiểm định xác nhận với alpha 0,05. `PASS_SOURCE` không thể thay cho `PASS_SCIENCE`.

**Điểm chưa đạt quan trọng:** A0B từng kiểm toán một biến đổi P residual có covariance rất tốt, nhưng đó là kiểm toán tính khả thi trước khi có đủ 4-arm matched provenance; không suy diễn thành `P-C/N-C_FULL_PASS`. A0D official class CPU PASS chỉ xác nhận lớp và mapping, chưa chứng minh một tensor nonpretrained 262.144×512 cụ thể đã được đóng băng đúng seed và dùng trong pilot.

## 5. Quyết định và hành động hữu hạn

**Final:** `A0D=PASS` · `A0E_OFFICIAL_PUBLISHER_BYTES=PASS` · `A0E_SOURCE_MASK=PASS` · `A0E_PREREG_DESIGN=FROZEN` · `GOLD_CUSTODY=HOLD` · `4ARM_NULL_PROVENANCE=HOLD` · `SCIENCE_ADMISSION=NO_GO_HOLD` · `T4_2X2=HOLD`.

**Bước thực hiện tiếp theo:** `TTM_GEMMA2_A0E_OWNER_GOLD_CUSTODIAN_SEAL_AND_FOUR_ARM_FROZEN_INPUT_NULL_QA_FINAL_ADMISSION`.

Chỉ một hồ sơ bổ sung tích hợp: (1) người giữ gold độc lập có receipt + nguồn Cambridge pinned; (2) kiểm nguyên gốc source rights/TinyStories SHA; (3) xác nhận pretrained donor actual weights/candidate chain; (4) frozen official nonpretrained N-source/seed; (5) kiểm 4-arm null và projected/source geometry trên TRAIN-only; (6) manifest chính xác checkpoint/optimizer/VAL code/QA. Nếu bất kỳ cổng bắt buộc nào vẫn HOLD thì **không chạy GPU**. Không sửa `main`, `lineage.md`, L0020/L0021 hay thêm L0022 trong đợt source-only này.

**Biên bản máy đọc:** [TTM_GEMMA2_A0E_INDEPENDENT_SOURCE_LABEL_CUSTODY_PREEXEC_SINGLE_GATE_ADJUDICATION_20261111.json](../../artifacts/qa/ttm-embeddinggemma2/TTM_GEMMA2_A0E_INDEPENDENT_SOURCE_LABEL_CUSTODY_PREEXEC_SINGLE_GATE_ADJUDICATION_20261111.json).

# FC01 — Phân xử BPE thất bại V1 và đóng băng sửa đổi tiền thực thi V2

**Operation:** `TTM_FC01_V1_REAL_T1_BPE_FAIL_AND_V2_SOURCE_ONLY_AMENDMENT_ONE_PACKET`  
**Ngày:** 13/11/2026  
**Loại:** PREEXEC DATA/SOURCE AMENDMENT, không thay đổi D1, không training, không GPU, không TEST/Q1Q2  
**Quyết định V1:** `HOLD_EXACT_BPE_CANDIDATE_LENGTH_MISMATCH`  
**Quyết định V2:** `GO_SOURCE_ONLY_AMENDMENT_FOR_ONE_OWNER_READBACK`; science release vẫn **HOLD_PREEXEC**.

## Bằng chứng owner Windows, không diễn giải lại

Owner chạy launcher sửa CRLF và nhận các mốc:

- `FC01_SEVEN_FILES_PREFLIGHT=PASS_KNOWN_LF_OR_EXACT_CRLF`; nguồn chuẩn LF `PASS 7/7`.
- `FC01_PINNED_ORIGINAL_TINYSTORIES_T1_CHECKPOINT_T4_PACK=PASS`.
- `FC01_PRIVATE_CORPUS_SHA256=7214213c79002943cbb9f7d0c6c25a81ba7f522c7218dcd4297a2c8465084bd6`; 384 family, TRAIN 256 / VAL 64 / EVAL 64, B và C giống nhau.
- QA chính xác bằng tokenizer T1 đã khóa thất bại tại `('CANDIDATE_BPE_LENGTH_DIFFERS', 'entity_location', [13, 12])`.
- Không chạy code phía sau QA, không audit runner, không training hoặc test. Corpus V1 lưu nguyên làm chứng cứ thất bại; không sửa/ghi đè V1.

Từ `pair_ids` của manifest T1 gốc đã pin, bộ tính toán **đọc-only độc lập trong phiên nghiên cứu** thu được:

| Category | V1 candidate yA/yB, BPE tokens | Kết luận V1 |
|---|---|---|
| `entity_location` | **13/12** | lệch + vượt 12 |
| `causal_reasoning` | **11/11** | đạt |
| `rule_constraint` | **12/12** | đạt |
| `goal_persistence` | **14/14** | vượt 12 |

Owner run thực tế dừng ở category đầu tiên, nên **14/14 chỉ là kết quả tính lại từ pair_ids**, chưa phải kết quả của QA Windows lần đầu. Điều này tránh sửa một lỗi rồi thất bại lại vì lỗi thứ hai.

## Sửa đổi đã tiền đăng ký cho V2 — không tìm kiếm theo loss/output

**Thay đổi có phạm vi giới hạn, không thay đổi seed hoặc hyperparameter:**  

1. `entity_location`: đổi cue `upper/lower` thành `upstairs/downstairs` và hai continuation thành “The keeper used the upstairs bin.” / “The keeper used the downstairs bin.” Độ dài trên pinned T1: **12/12**.
2. `goal_persistence`: đổi mục tiêu đặt ceramic token ở north/south **counter** thành north/south **table**; hai continuation “The keeper put it on the north table.” / “The keeper put it on the south table.” Độ dài trên pinned T1: **12/12**, thể hiện rõ hành động đặt vật tại đích.
3. `causal_reasoning`, `rule_constraint`: giữ nguyên cặp candidate, độ dài **11/11**, **12/12**.
4. Gỡ đường tắt `ITEM→LABEL` của singleton D0. V1 sử dụng `index % 2` trong khi `ITEM=index % 8`, khiến một item luôn gắn với một fact trong corpus A. V2 dùng parity `(index // 8 + index % 8) % 2`; với mỗi item và mỗi adjective thuộc TRAIN, **4 family A / 4 family B**, giữ corpus A tổng 256/256.
5. Giữ nguyên số family, split, arms, episode 512/arm, checkpoint, T1, core TinyStories, 256 updates/arm, budget/seed/optimizer, objective, CI, threshold và định nghĩa primary. **B/C vẫn giống byte**.
6. Tăng QA tĩnh độc lập từ 15 thành **16 test** với test âm tái dựng confound ITEM→LABEL của V1; thêm bất biến không rò nhãn qua item/adjective vào checker.

**Không tuyên bố** semantic templates độc lập: V2 vẫn chỉ có bốn template semantics chung. Chuyển `upper/lower` thành `upstairs/downstairs` và counter thành table là thay đổi câu hỏi đo trong **nghiên cứu FC01 preexec**, không bao giờ gộp V1/V2 hay so các kết quả này như một can thiệp khoa học.

## SHA pin V2 đã tính bằng generator tĩnh, chưa có owner dynamic readback

- **V1 private corpus:** `7214213c79002943cbb9f7d0c6c25a81ba7f522c7218dcd4297a2c8465084bd6` — **immutable archive**.
- **V2 private corpus deterministic candidate:** `becc0408880aaed8bd5eb6fdf3997e62d5131c187a48331a03ae37d41aaa1aa3`.
- **V2 source SHA-256** (UTF-8 LF):
  - `fc01_build_private_corpus.py`: `a9978a1961a2d062e5229ad91593eddb01f7fcfab00c4dfb55cc3df316053c98`.
  - `fc01_integrated_static_qa.py`: `f4f205ed4be0021faf99b3e73f4c0fb80ef4d1ce095ee5985507ca3f1e33cc3e`.
  - `fc01_independent_contract_tests.py`: `316b6d8a26881abbcc333aedbf14ef0342f65731b56690f8a09dbd24e34f8f6e`.
  - `fc01_train_eval_once.py`: `b786a4468ba104786df7683da9b1cf19d2334d9cc203dd19c3e7d6f10e2e93be`.
  - `Invoke-TTM-FC01-Integrated-Readiness-PS51.ps1`: `cf8ad6aa83d83319201bb90e7d89cfa1adda18bb2e6dea8d5f6e88cc38c4678b`.
  - `fc01_pinned_bpe.py`: `d90ddbcdbea8450d7605cf7e65936efd032344b8d7793c2272d4d0870cfbff01` (không thay).
  - `README_FC01_ONEPACKET_VI.md`: `f0aa8bf7e31f627802aa8469ad67bd197c208c98991a82c840119f13d90b6231` (historical V1 README, không dùng như hướng dẫn chạy V2).

V2 được dựng **source-only** trong container: structural QA PASS; independent self-authored negative/source QA **16/16 PASS**. Bộ tính BPE độc lập (bảng merges T1 gốc, tái lập thuật toán pretoken cho text ASCII) ghi nhận cặp candidates: `12/12,11/11,12/12,12/12`; tổng **0 prefix mismatch, 0 overflow** trên 384 families, max context+answer 58 BPE tokens. Đây **không thay** cho lần QA chính xác sử dụng `fc01_pinned_bpe.py` và manifest gốc trên Windows.

**Lưu trữ V2 mới, không thay đổi đường dẫn V1:**
`D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\fc01_onepacket_20261113_v2\` (source);
`D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\TTM_FC01_OWNER_CORPUS_20261113_v2\` (private data);
`D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\TTM_FC01_SOURCE_BUNDLE_20261113_v2\` (bundle).

## Giới hạn / phán quyết

- `V1_EXACT_BPE=FAIL_CONFIRMED` · `V1_SOURCE=IMMUTABLE`.
- `V2_SCOPED_SOURCE_CONSTRUCTION=PASS` · `V2_INDEPENDENT_STATIC_QA=PASS_16_OF_16` · `V2_OWNER_REAL_T1_BPE=NOT_EXECUTED` · `V2_RUNNER_AUDIT=NOT_EXECUTED`.
- `FC01_SCIENCE=HOLD_PREEXEC` · `GPU=NO` · `TRAINING=NO` · `D1_CONFIRMATORY=HOLD` · `TEST_Q1Q2=SEALED` · `DEV32=CLOSED_UNCHANGED` · `LINEAGE=UNCHANGED`.
- Chỉ tiếp tục *một* lượt Windows owner **V2 source-only integrated QA**. Không tự cấp GO huấn luyện kể cả khi readback V2 đạt PASS; quyền dữ liệu và runtime/resume Colab vẫn phải xác minh trước science.

**Kết luận:** sửa lỗi thiết kế **trước training** có chứng cứ và versioning; không nới tiêu chí, không đổi model, không tối ưu theo kết quả huấn luyện. Kết quả V1 và V2 không được trộn lẫn.

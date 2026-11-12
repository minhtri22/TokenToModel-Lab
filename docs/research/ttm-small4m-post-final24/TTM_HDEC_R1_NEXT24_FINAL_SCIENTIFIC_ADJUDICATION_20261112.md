# TTM-Small-4M H-DEC-R1 NEXT24 — hậu giải mù, QA khoa học và phán quyết cuối cùng

**Operation:** `TTM_HDEC_R1_NEXT24_INDEPENDENT_IMPL_QA_POST_FREEZE_UNBLIND_AND_FINAL_ADJUDICATION`  
**Ngày:** 2026-11-12  
**Run ID:** `TTM_SMALL4M_POST_FINAL24_DECODING_REPETITION_DIAGNOSTIC_V1`  
**Loại kết luận:** `EXPLORATORY_SCOPED_AI_REVIEW` / kiểm toán độc lập cách triển khai (`INDEPENDENT_IMPLEMENTATION_QA`), **không phải** peer review con người/nhóm bên ngoài.  
**Phán quyết kỹ thuật:** `PASS_SCOPED_INDEPENDENT_IMPLEMENTATION_QA` + `H_DEC_R1_EXPLORATORY_CANDIDATE_PASS`.  
**Phán quyết ngữ nghĩa:** `PROMPT_ADHERENCE_NEAR_ZERO_NO_SEMANTIC_GAIN_DEMONSTRATED`.

## Chuỗi nguồn và trật tự một lần

1. FINAL24 A/C trước đó đã đóng; H-DEC dùng đúng checkpoint A-1152, **không training lại**. Một lượt Colab T4 đã sinh **72** đầu ra: 24 DEV, 48 BLIND_FINAL; 4.040 `model.forward`, 0 optimizer updates.
2. Owner-private raw-72 SHA-256: `e09572c29993af8379a57cfc26c905912525e6238510f2803af5c9a81cc2f208`; generation receipt SHA-256: `bdd1a513fef9de45fc66873795b6a04551ebde9b08f9b1b7a37d4d028d51735a`.
3. Rater ZIP neutral SHA-256: `9ec48639974575e1cdebb28fcf9b2a0393a3318fb954dc9c5824e2f8bace927a`. Packet JSON SHA-256: `e28049bf770ddab879fdd10ac5805b9b5bf2e60fa0f8f9264ba641abab82dd22`.
4. GPT-6 trong phiên khác chấm đủ 24 cặp / 48 đoạn / **144 điểm nguyên** và **24 ghi chú**, khai báo chưa giải mù. Điểm JSON gốc byte SHA-256: `6ba3420b8863c435ef1fc71d9706826221455d5254c87ea4e789b852b908a682`. SHA-256 mảng điểm canonical: `891225c539ffc46522e06a711fc1e8d60038d7dfba0195ac64c5d7754289543a`. Biên nhận gốc SHA-256 `27b759413e4aae07d90ddd84aa7f84b6253be93547ed1cbf03e5a198f46d16cc`.
5. Thiếu tệp `.sha256` do rater phát hành cùng lượt; owner **không tuyên bố đã nhận** tệp đó. Vì byte của scores và SHA lưu trong receipt khớp chính xác, owner tạo **sidecar tái dựng ghi rõ nguồn**, không sửa JSON điểm, và chấp nhận score freeze. Kiểm toán này đạt **35/35 PASS**.
6. Chỉ **sau** bước 5, owner xác minh giải mã AES-256-GCM escrow nguyên thủy: ciphertext SHA `812e7e23cdc3eba4735bfb0b8ff43b2a7420fbaac4fa0edfc2fe4a944cb8c3b7`, plaintext mapping SHA **chỉ digest** `603bccaf0060f8a8a577302353ea6cac831281ad17596603ffa7eb6630ce20a3`. Ánh xạ 12/12, mỗi stratum 3/3. Không bốc thăm lại hoặc in khóa/ánh xạ ra công khai.
7. Owner postfreeze checker dùng frozen metric source SHA `1c5cecf97cc86da1d833c9c4959d4532c989d5c0e604a1490e88c684870828f1`, NumPy `2.3.5`, seed `20261112`, 20.000 bootstrap; **343/343 PASS**. Bộ kiểm toán triển khai độc lập lần thứ hai, tự tính trigram và bootstrap, **360/360 PASS**. Không model-forward mới, không chấm lại, không mở TEST/Q1/Q2/OOD.

## Chỉ tiêu đã tiền đăng ký (không sửa ngưỡng sau kết quả)

Source contract: `docs/research/ttm-small4m-post-final24/TTM_SMALL4M_POST_FINAL24_ROOT_CAUSE_AND_NEW_HYPOTHESIS_PREREG_20261112.md`, Git blob `46953a5911afea92252403f2c6ed809fab547df5`. Word tokenizer regex `r"[A-Za-z]+(?:'[A-Za-z]+)?"`; tỷ lệ lặp = `1 - ngram_unique/total_word_trigrams`, 0 khi dưới 3 từ. Primary endpoint là `mean(D1 - D0)` trên 24 prompt mới; giảm có dấu âm. D1 áp penalty 1,15 lên mỗi token đã sinh riêng biệt, không phạt prompt, cùng A-1152, greedy, tối đa 64 BPE token.

| Chỉ tiêu / guardrail | Ngưỡng khóa | Đã đo | Quyết định |
|---|---|---|---|
| Mean word-trigram repetition D1 − D0 | ≤ −0,10 | **−0,248158122681317** | PASS |
| D1 strict thắng giảm lặp | ≥16/24 | **23/24**, D0 1, hòa 0 | PASS |
| Upper CI95 paired-bootstrap | <0 | **−0,18957060771446313** (CI95 [−0,31026832687906614; −0,18957060771446313]) | PASS |
| Mean prompt adherence D1 − D0 | ≥−0,25 | **0,000000** | PASS guardrail |
| Mean coherence D1 − D0 | ≥−0,25 | **+0,0416667** | PASS guardrail |
| Mean consistency D1 − D0 | ≥−0,25 | **0,000000** | PASS guardrail |
| D1 đoạn dưới 8 từ không vượt D0 | D1 ≤ D0 | **0 vs 0** | PASS |

Tỷ lệ lặp D0 = **0,2860416650** (28,60%); D1 = **0,0378835423** (3,79%), giảm khoảng **24,82 điểm phần trăm** theo trung bình ghép cặp. Cả D0, D1 đều có **8 EOS** và **16 cap-64** trên 24 đoạn FINAL mỗi arm. Mean số BPE token mới: D0 **55,5417**, D1 **53,7917**.

Chất lượng do GPT-6 tự khai chấm trên thang 0–3: adherence D0 **0,0417**, D1 **0,0417**; coherence **0,9583 vs 1,0000**; consistency **1,0000 vs 1,0000**. Bám prompt hoàn toàn không cải thiện, và điểm gốc gần 0: đây là **floor effect** khiến `no quality drop` không bảo đảm đầu ra hữu ích. Không được diễn giải PASS về lặp là mô hình hiểu prompt, suy luận hay tạo văn bản tốt.

## Quyết định hai tầng và giới hạn

- **`INDEPENDENT_IMPLEMENTATION_QA=PASS_SCOPED`**: hai cách triển khai số học độc lập (cùng byte nguồn, cùng escrow nguyên thủy) cho kết quả thống nhất, 35 + 343 + 360 checks; không có reviewer độc lập thứ hai / chứng nhận bên ngoài.
- **`CANDIDATE_GATE=PASS_EXPLORATORY`**: theo đúng bảy guardrail tính toán đã khóa, can thiệp penalty 1,15 làm giảm mạnh mức lặp 3-gram trên 24 prompt mới. Các phép bootstrap là CI mô tả, không phải kiểm định nhân quả multi-seed hoặc proof of production utility.
- **`SEMANTIC_PROMPT_ADHERENCE_GAIN=NOT_DEMONSTRATED`**: cả hai decoder gần 0/3; không tuyên bố cải thiện bám prompt, khả năng tổng quát, tính đúng ngữ nghĩa, hay equivalence.
- Không nghiên cứu chọn penalty khác trên NEXT24 sau khi đã biết outcome; đánh dấu 24 FINAL mới `CONSUMED_CLOSED`, không tái dùng cho phép thử xác nhận khác. Khóa/ánh xạ/điểm từng cặp chỉ lưu owner-private. Duy trì quyền / nguồn và governance cho mọi nghiên cứu kế nhiệm.

## Bằng chứng

- Owner score acceptance: `TTM_NEXT24_OWNER_SCORE_FREEZE_ACCEPTANCE_20261112.json` (public safe, không có điểm cá thể).
- Owner private postfreeze mapping/score readback: `TTM_HDEC_R1_NEXT24_OWNER_PRIVATE_POSTFREEZE_UNBLIND_20261112.json` (**không lên GitHub**).
- Owner public aggregate: `TTM_HDEC_R1_NEXT24_PUBLIC_SAFE_UNBLIND_AGGREGATE_20261112.json`.
- Independent implementation scientific QA: `TTM_HDEC_R1_NEXT24_INDEPENDENT_POSTUNBLIND_QA_20261112.json`.
- Read-only checker sources: `ttm_next24_owner_acceptance_qa_v1.py`, `ttm_hdec_r1_next24_owner_postfreeze_unblind_v1.py`, `ttm_hdec_r1_next24_independent_postunblind_qa_v1.py`.
- Rater original JSON byte preserved; reconstructed sidecar distinct and explicitly labeled.

**Next:** archive immutable H-DEC-R1 NEXT24; if new question is semantic prompt-following, design **H-DATA matched-budget** with completely new blinded FINAL, before any training or inference. No automatic new GPU job, no rerun of this one-shot. Merge into main remains separate gate.

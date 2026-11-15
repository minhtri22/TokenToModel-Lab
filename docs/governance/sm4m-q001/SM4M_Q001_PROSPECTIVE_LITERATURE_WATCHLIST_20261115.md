# SM4M-Q001 — Danh mục tài liệu tham khảo mở rộng (Prospective Literature Watchlist)

**Loại:** tài liệu nghiên cứu tham khảo, **không phải** bằng chứng kết quả thực nghiệm TTM / phán quyết Q3 / quyết định owner Q4.  
**QuestionID:** `SM4M-Q001` · **Entry:** `SM4M-REF-PROSPECTIVE-001` · **Ngày bổ sung:** 2026-11-15.  
**Nguồn đề xuất:** Owner cung cấp arXiv `2601.06002` và yêu cầu đưa vào nhóm tài liệu cần tham khảo.  
**Repo PR:** [Draft #21](https://github.com/minhtri22/TokenToModel-Lab/pull/21).  
**Q3 reviewed exact design HEAD:** `c37ac0b3901eb6fd9c658d818c02e85f66b7936e`; entry này xuất hiện **sau** Q3 review, không nằm trong 13 nguồn frozen Q2, không làm thay đổi conclusion hoặc prior audit.  
**Status:** `REFERENCE_ONLY · FUTURE_HYPOTHESIS_SUPPORT · NOT_ADMITTED_AS_SMALL4M_CAUSAL_EVIDENCE · NO_SCIENCE_PERMIT`.

## 1. Hồ sơ thư mục chính thức

- **Tựa:** *The Molecular Structure of Thought: Mapping the Topology of Long Chain-of-Thought Reasoning*.
- **Tác giả:** Qiguang Chen, Yantao Du, Ziniu Li, Jinhao Liu, Songyao Duan, Jiarui Guo, Minghao Liu, Jiaheng Liu, Tong Yang, Ge Zhang, Libo Qin, Wanxiang Che, Wenhao Huang.
- **Năm:** 2026; **arXiv:** `2601.06002v2`. Submitted `2026-01-09`, v2 revised `2026-01-13` (the PDF first page says “Date: Jan 15, 2026”; arXiv's version history is the canonical version timestamp).
- **Permanent metadata:** https://arxiv.org/abs/2601.06002
- **Exact source-version PDF:** https://arxiv.org/pdf/2601.06002v2
- **DOI issued for the preprint:** https://doi.org/10.48550/arXiv.2601.06002
- **Status of publication:** arXiv **preprint**; no peer-review acceptance status asserted.
- **URL cleanup:** tracking query parameter `fbclid` removed from owner-provided link; retained canonical arXiv identifier.
- **Original Q2 literature:** 13 papers P01…P13 remain immutable and unchanged. This is **a prospective reference**, not retroactively numbered P14 in Q2's frozen literature QA receipt.

## 2. Các kết quả do bài báo thực sự trình bày

1. Authors describe long chain-of-thought (Long CoT) trajectories with a **behavior-directed graph**: Deep Reasoning, Self-Reflection and Self-Exploration. The covalent/hydrogen/van-der-Waals language is a **molecular analogy** to represent the organization of reasoning steps, not a demonstrated physical neural mechanism. [Abstract and §§1,3](https://arxiv.org/pdf/2601.06002v2).
2. They argue the distribution and **transitions between reasoning behaviors** can matter more for transferring stable Long CoT than superficial reasoning keywords; introduce **effective semantic isomers**, where superficially/semantically similar solutions can have different transfer behaviors. [§§4–5](https://arxiv.org/pdf/2601.06002v2).
3. **Mole-Syn** uses a behavior-distribution/transfer graph from capable reasoning teachers to guide synthetic Long CoT traces. Authors report outcomes on **six mathematics/reasoning benchmarks** and training/RL stability in much larger instruction-tuned student models, not Small-4M. [§6, Tables 2, 6–8](https://arxiv.org/pdf/2601.06002v2).
4. **Source limitations explicitly admitted:** limited teacher/backbone models, offline SFT/distillation emphasis, imperfect semantic topology visualization, automatically labeled behavior data with inevitable noise/bias. [§Limitations](https://arxiv.org/pdf/2601.06002v2).

## 3. Ý nghĩa với lộ trình TokenToModel-Lab

| Nhóm / câu hỏi | Mức liên quan | Ý nghĩa hợp lý; không được suy diễn |
|---|---|---|
| `TTM future reasoning / CoT / structured training` | `CONCEPTUAL_RELEVANCE_HIGH` | Cân nhắc nghiên cứu tương lai về **chất lượng và cấu trúc reasoning traces**, bao gồm chuyển tiếp deep-reasoning / reflection / exploration; đánh giá có đối chứng trước khi chọn training recipe |
| `TTM Small-4M H-OBJECTIVE / H-DATA` | `HYPOTHESIS_INSPIRATION_ONLY` | Gợi ý data/objective alignment không đơn giản là thêm từ khóa suy luận hoặc kéo dài output; bài báo **không chứng minh** nguyên nhân T4 |
| `TTM Small-4M H-CAPACITY` | `DIRECT_EVIDENCE_NONE` | Llama/Qwen 8B–70B và các teacher reasoning LLM **không suy ra** 3,749,376-parameter T4 có thể/hay không thể học Long CoT |
| `TTM Small-4M attention/FFN patch` | `DIRECT_EVIDENCE_NONE` | Không có kiểm chứng rằng causal attention hiện tại hỏng hoặc cần đổi architecture; graph/bond model **không phải** đơn đặt hàng thay Transformer |
| `Current Q001 gold/rater / Q2 admission` | `DIRECT_EVIDENCE_NONE` | Sơ đồ reasoning label trong paper có giới hạn automatic annotation; **không thể thay thế** AD-02/03/04/05/06/07 hiện chưa đạt |

**Vị trí phù hợp:** danh mục tham khảo cho **future reasoning-training directions** của TTM; có thể dẫn trong **ma trận lựa chọn hướng nghiên cứu sau Q4** nhưng **không nâng cấp** thành căn cứ sửa Small-4M hiện tại.

## 4. Các câu hỏi tham khảo có thể dùng về sau — CHƯA mở experiment

- Liệu hiệu quả nằm ở **trình tự chuyển tiếp giữa các hành vi suy luận**, thay vì chỉ tăng số token hoặc đặt nhãn “think/reflect” trên surface?
- Có thể phân biệt **reasoning structure** với lexical shortcut, sample leakage, answer-format/verbosity bias và rater-induced artifact bằng gold độc lập và matched controls không?
- Một model rất nhỏ với context256 có đủ phạm vi biểu diễn để dùng protocol như bài báo, hay chỉ nên dùng nó để đặt câu hỏi tương lai? Cần nghiên cứu riêng **sau** khi có question gate, source/rights/custody và tiền đăng ký.
- Nếu một hướng mới được đề xuất, phải tách ba cấp: **quan sát từ paper ngoài** → **giả thuyết áp dụng TTM** → **kiểm tra do owner cấp quyền**, không nhảy cóc thành `ROOT_CAUSE_IDENTIFIED`.

## 5. Ràng buộc và bất biến (hard boundaries)

- `Q3=PASS_Q3_SOURCE_AND_EVIDENCE_SCOPE_SCOPED` chỉ gắn exact reviewed HEAD `c37ac0b3901eb6fd9c658d818c02e85f66b7936e`; entry reference mới **không tự coi là được reviewer Q3 xét duyệt**.
- `Q4=OWNER_NOT_DECIDED`; `PR21=DRAFT_UNMERGED`; `main` không được coi là đã cập nhật trước merge được phép.
- `ROOT_CAUSE_NOT_IDENTIFIED`; `HOLD_BASELINE_ADMISSION_FOR_NEW_SCIENCE`; `KEEP_HISTORICAL_REFERENCE_ONLY`; `F0_F2_PAUSED`.
- **Không** sửa Q2 original 13 references, bảy Q2 blobs, ten original study verdicts, AD-00…AD-08 statuses, `ACTIVE_RESEARCH_GATE.md`, `lineage.md` hoặc source code vì entry này.
- **Không** tạo dataset/gold/scorer, không train/inference/GPU, không mở research branch mới, không cấp science permit.
- **Owner Q4 merge GO/HOLD chưa được đưa ra.** Việc bổ sung tài liệu tham khảo không là chấp thuận Q4.

**Bước tiếp theo của hồ sơ quản trị hiện hành (không mở gate mới):** `SM4M_Q001_Q4_OWNER_CLOSURE_AND_PR21_GOVERNANCE_ONLY_MERGE_GO_HOLD_SINGLE_GATE`.

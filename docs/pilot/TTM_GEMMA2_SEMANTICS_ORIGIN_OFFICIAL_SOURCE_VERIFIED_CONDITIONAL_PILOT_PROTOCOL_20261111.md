# TTM-Small-4M × EmbeddingGemma 2 — A0D official-source readback, kế hoạch bốn nhánh có điều kiện

**Ngày:** 2026-11-11
**Operation:** TTM_GEMMA2_A0D_OWNER_LOCAL_PINNED_DONOR_TOKENIZER_AND_OFFICIAL_TRANSFORMERS_CLASS_ONE_INTEGRATED_READBACK
**Trạng thái:** CONDITIONAL_PROTOCOL_LOCK_SOURCE_ONLY — không phải science prereg có thể thực thi; chưa cấp T4.
**Branch:** research/ttm-gemma2-token-alignment-pretraining-causality-20261111

## 1. Phân biệt CI PASS và owner-local chưa chạy

GitHub Actions [run 42968236741](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/42968236741), commit 931dc78101d845dd55e4f161829708003c87a005, chạy Python 3.12.16, PyTorch 2.10.0+cpu, Transformers 5.19.0. Chỉ lấy ba file từ google/embeddinggemma-2 revision f9972ac22e696a105c482202646979e33e4b5a1e, không tải trọng số pretrained:
- config.json: 4.455 bytes, SHA256 b8f1e9931b57fbc054acdb445c41765d55b0074c58d145fa82839941ad1b5bb3.
- tokenizer.json: 32.170.510 bytes, SHA256 4d777ef5bdc1aa36227abdfb77c3e49e7b9c892d16e1b6bda41c393504828be4.
- tokenizer_config.json: 1.599 bytes, SHA256 17bd5d6e9364ca49a534e1502076593317c298d4a663623091ed45388f004874.
- Chính lớp official EmbeddingGemma2TextModel đã khởi tạo CPU từ exact config: 271.002.624 parameters, 413 state tensors, text source tokenizer class GemmaTokenizer, no forward/training/checkpoint; named-state-shape-dtype SHA256 9e36b43011641e65bbdbdc2938d8c12a368810d9e59e2107024683288d2fecc1.

**CI PASS không phải OWNER_WINDOWS_PASS.** Drive scoped search/folder browsing chưa tìm được ba file donor gốc. Cache Hugging Face trên Drive thuộc snapshot khác. RemoteDesktop trả internal error, do đó chưa đọc file Windows. CI không nhận T1 private manifest, nên chưa chạy lại mapping 1.917 valid / 50 multi donor IDs.

**Owner-local gate:** chạy canonical source-only runner tools/embeddinggemma2_swap/semantics_origin_a0/ttm_a0d_pinned_official_source_readback.py cùng ba donor files đúng SHA, manifest T1 SHA cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc và --cpu-init trên Python 3.12. Yêu cầu mapping mapped=1917, multi_id_mapped=50, incomplete_utf8=130, empty_or_special=1, unmapped_or_invalid_donor_ids=0. Độc lập đọc lại SHA receipt. Nếu thiếu tệp, phiên bản thư viện hoặc không khớp map, HOLD; không tự tải weights hay cài lại môi trường.

## 2. Khóa thiết kế H-A/H-B, chỉ design-only

Bốn arm với cùng TTM checkpoint ban đầu, T1, TRAIN-only corpus, optimizer, target-token budget, seeds và schedule:

| Arm | Donor input rows | Phép can thiệp |
|---|---|---|
| P-A | Official pretrained EmbeddingGemma 2 pinned source | Đúng token |
| P-C | Cùng nguồn pretrained | Constrained residual null control A0B |
| N-A | Official EmbeddingGemma2TextModel khởi tạo ngẫu nhiên chỉ lấy input embedding, ánh xạ với cùng tokenizer | Đúng token |
| N-C | Cùng nguồn nonpretrained | Constrained residual null control A0B |

H-A: D_align = NLL(P-C) − NLL(P-A). Kết luận tối đa là tác dụng token-specific residual association dưới các kiểm soát hình học, không phải tác dụng nhân quả ngữ nghĩa tiền huấn luyện.

H-B: D_origin = [NLL(P-C)−NLL(P-A)] − [NLL(N-C)−NLL(N-A)]. Cần kiểm mean/covariance/per-token norm, frequency, hình thái, projected input, pairwise topology và source distribution theo ngân sách ngang nhau; sự khác biệt giữa nguồn pretrained và untrained không thuần là ngữ nghĩa. Dương tính H-B chỉ có thể diễn giải pretraining-associated token-identity transfer, trước khi có độc lập lexical evidence.

Pilot feasibility, nếu các gate admission đạt: 4 arms × 3 seeds × 512 optimizer steps × 4096 target-token presentations = 25.165.824 presentations, Colab T4 + Drive checkpoint. Kế hoạch không tự cấp permit science. Không chỉnh sửa/tiêu thụ lại H768 và OOD256, không dùng TEST để điều chỉnh hyperparameters hoặc chọn null controls. Mốc H768/OOD256 chỉ là prior evidence.

## 3. Bộ lexical mới, độc lập — chưa được chấp nhận

44 cặp SimLex A0D (22 high/22 low) đã chấm là exploratory consumed; 76 cặp SimLex và 21 cặp WordSim được xem để đo coverage không thể tái dán nhãn như confirmatory TEST. Đối chứng sau:
- Lấy mẫu whole-word lexical anchors đã được T1–donor exact source readback, tách word identity giữa các mẫu, tránh shared-word dependence.
- Dữ liệu nhãn human relatedness hoặc similarity mới có provenance, rights và annotator blind to donor cosine/LM NLL; không pha trộn hai construct vào một thang điểm.
- Đối sánh và báo cáo TRAIN-only frequency, length, case, prefix, orthographic similarity, morphology, stratum representation.
- Prespecify nhóm high/low, ngưỡng tối thiểu số cặp, CI/bootstrap unit theo word clusters, nhãn ngẫu nhiên và nguồn chấm độc lập trước khi đo donor cosine hoặc LM NLL.
- Đối chứng phải giữ cùng ngân sách để tránh kết quả do source row scale/covariance. Nếu không tuyển đủ anchor không trùng, HOLD_LEXICAL_SAMPLE_INSUFFICIENT; không hạ ngưỡng dựa trên outcome.

Không được dùng p=0.0052 trước đó để kết luận significance. New science pre-registration còn thiếu fresh dataset và decision thresholds; chỉ đóng băng **cấu trúc nghiên cứu**, không khóa khoa học như đã đủ dữ liệu.

## 4. Phán quyết tích hợp

- HF exact donor SHA256: PASS_CI_3_OF_3
- Official Transformers EmbeddingGemma2TextModel CPU: PASS_CI_OFFICIAL
- Windows/owner local verified files: HOLD_REMOTE_UNAVAILABLE
- Owner-local T1 tokenizer mapping: NOT_EXECUTED
- Fresh independent lexical evaluation: NOT_ADMITTED
- Four-arm protocol: CONDITIONALLY_LOCKED_DESIGN_ONLY
- **T4 2×2: HOLD**
- L0020, L0021 và lineage.md giữ nguyên. No new science claim/lineage L0022; main và checkpoint không bị tác động. No training/inference/optimizer/GPU.

**Bước thực hiện tiếp theo:** TTM_GEMMA2_A0D_OWNER_WINDOWS_PINNED_SOURCE_T1_MAPPING_SINGLE_READBACK_AND_PILOT_PREREG_GATE. Một lượt PowerShell 5.1 owner-local kiểm ba file đúng SHA và T1 1917/50 bằng official class; độc lập xác minh receipt rồi mới chốt pilot prereg và một quyết định T4. Không thêm model mirror hoặc lặp lại các benchmark đã tiêu thụ.

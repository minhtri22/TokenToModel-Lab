# TTM-Small-4M × EmbeddingGemma 2 — Semantic mechanism 4×3 V2

**Trạng thái:** SOURCE-ONLY / PRE-CLAIM · H768 chưa niêm phong trên dữ liệu thật · chưa có quyết định chạy science.

- `ttm_semantic4x3_balanced_null_cpu_qa.py`: sinh đối chứng null bảo toàn Z=XPᵀ và covariance, chỉ QA CPU; không save ma trận donor riêng tư, không forward mô hình.
- `ttm_semantic4x3_h768_one_shot_source_seal.py`: khóa và niêm phong H768 bằng pinned TinyStories-valid, chính xác một lựa chọn, chỉ ghi private trong `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp`. Không giải mã nội dung TEST/H320/H512 đã tiêu thụ; loại bằng SHA. Chỉ chạy `--mode seal` khi thực hiện bước seal đã chốt, không phải để chấm khoa học.
- Cả hai có chế độ `--mode fixture`. Với `--mode real`, null QA yêu cầu chính hai file private `candidate_initialization.pt` và `checkpoint.pt` có SHA256 pinned. Không được đưa các file đó lên GitHub.
- H768 selector tải helper H512 đúng SHA Git blob từ repo source hoặc staged trusted `_tmp\ttm_causal6_source_h512_stage_20261109\code` để không buộc sync local repo, và dùng T1 parser/BPE checksum nguồn.
- File manifest cùng commit ghi SHA256 và Git blob cho cả hai script.

Hợp đồng tiền đăng ký bản khóa: `docs/pilot/TTM_GEMMA2_SEMANTIC4X3_INTEGRATED_PREREG_SOURCE_RESOURCE_DECISION_20261110.md`.

**Không có model training runner 4×3 trong commit này**: phương án chạy khoa học chưa được cấp quyền, tài nguyên hiện HOLD. Đừng coi SOURCE_QA=PASS như đủ điều kiện mở CLAIM. Giữ `lineage.md` L0019 và không đổi main.

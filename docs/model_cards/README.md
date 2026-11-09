# TTM-Small-4M — Thông tin mô hình, nguồn và quyền công bố

**Source of truth:** branch docs/ttm-small4m-model-card-dataset-rights-20261109 từ main ghim b57b44e7287f842e81050c1faee337f636333dd0. Tài liệu này là phạm vi hỗ trợ P11/P12, **không mở P11/P12** và không phải giấy phép release.

## Tài liệu chuẩn

- [Model card T4 original](TTM_SMALL4M_T4_MODEL_CARD_20261109.md): cấu hình 3,749,376 tham số, checkpoint, run H1/TEST/thăm dò, hạn chế chất lượng và cách sử dụng.
- [Dataset card TTM TinyStories pilot](../data_governance/TTM_SMALL4M_TINYSTORIES_DATASET_CARD_20261109.md): nguồn revision, split 2048/256/64, BPE TRAIN-only và leakage scope.
- [Ma trận quyền nguồn và giới hạn công bố](../data_governance/TTM_SOURCE_RIGHTS_AND_RELEASE_MATRIX_20261109.md): CDLA-Sharing-1.0 và rights/release gate R1–R8.
- [Manifest tái lập T4](../reproducibility/TTM_SMALL4M_T4_REPRODUCIBILITY_MANIFEST_20261109.md): Git pin, SHA256, PowerShell kiểm tra chỉ đọc, giới hạn reproduce.
- [Checklist quyết định công bố](../data_governance/TTM_SMALL4M_RELEASE_READINESS_CHECKLIST_20261109.md): mẫu phân xử riêng Data/BPE/weights/GGUF/code và owner signoff.
- [Biên bản QA nguồn/tài liệu](../../artifacts/qa/docs_rights/TTM_SMALL4M_MODEL_DATA_RIGHTS_DOCS_SCOPED_QA_20261109.json): chỉ QA tài liệu, **không** phải rà soát pháp lý độc lập.

## Kết luận hiện tại

**Đã ghi hồ sơ khoa học:** H1 VAL PASS scoped; TEST one-shot descriptive; step1280 exploratory NLL; strict T5 llama.cpp trained logits FAIL7/8; prompt adherence chưa được chứng minh dù có Ollama compatibility.

**Được phép public trong lượt này:** tài liệu/metadata/biên bản/checksum và các tuyên bố giới hạn có bằng chứng. **HOLD** quyền phân phối raw TinyStories, private TRAIN/VAL/TEST, BPE merge thực, checkpoint PyTorch, GGUF F32 và license chung cho source code TTM (chưa có LICENSE ở main). Quyết định HOLD là chủ trương an toàn hiện tại, **không phải** cấm vĩnh viễn do giấy phép.

**Bước thực hiện tiếp theo:** reviewer tài liệu/owner giải quyết tập hợp R1–R8 một lượt và cấp quyết định riêng cho từng loại tài sản. Không TRAIN, không TEST và không sửa lineage.md trong scope này.

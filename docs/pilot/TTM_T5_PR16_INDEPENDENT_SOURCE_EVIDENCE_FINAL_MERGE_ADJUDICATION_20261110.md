# TTM T5 PR #16 — Rà soát độc lập nguồn, bằng chứng và phán quyết merge cuối cùng

**Ngày:** 2026-11-10  
**Task:** `TTM_T5_PR16_INDEPENDENT_SOURCE_EVIDENCE_REVIEW_AND_FINAL_MERGE_ADJUDICATION`  
**Phán quyết:** **`MERGE` cho hồ sơ nghiên cứu âm tính có phạm vi khóa**. Đây là kết luận **đủ điều kiện về khoa học và mã nguồn để hợp nhất kết quả**; **chưa thực thi merge lên `main`**, vì yêu cầu của owner là `xem xét việc merge` và `ra phán quyết`, không phải lệnh merge vô điều kiện.

## 1. Kiểm tra nhánh và source

PR #16 từ `research/ttm-t5-f32-strict-logit-parity-diagnostic-20261109` vào `main`. Tại lúc bắt đầu review, HEAD `0194b81ddff679a9c6eb6c7e15526234b21d0371`, main `b57b44e7287f842e81050c1faee337f636333dd0`: **ahead 69, behind 0, Git mergeable true**, tổng 46 tệp (45 tệp mới, một tệp hiện hữu `lineage.md` được nối thêm đúng L0013). Không sửa mã P02, checkpoint, TEST, Q1/Q2 hoặc các nhánh PR13/14/15.

**QA nguồn lượt hai: PASS 20/20 kiểm tra có phạm vi**, bao gồm:

- Source C++ Git blob `bb0e1726e77c92696ffbbb92aa6e6b9aa49ee490`: đối chiếu 8 fixture-ID, toàn bộ token ID và bốn arm chính xác với prereg `3b12cc1883ab20e2d9e3a92e6907586c1b4cad36`. Mỗi phép đo tạo context mới, dùng CPU, gán rõ type_k/type_v/flash, dùng callback đếm `FLASH_ATTN_EXT`, lưu đủ 2048 logits.
- Python auditor Git blob `18dc82d845f228ea4e5b349ac5cabf9f1110a252`: khóa 8 reference và 32 native, kiểm số chiều và finite, cặp fixture/arm duy nhất, actual Flash counters, metric `max(abs(native-ref))` và strict threshold `0.001`.
- Runner Git blob `61c1cf9c31bc3514f4982509655990110aaf56ed`: chỉ một lần one-shot sau owner approval, pin EXE/GGUF/DLL/reference/SHA, từ chối chạy lại, không dùng TEST hay huấn luyện.
- Reference producer Git blob `5e7c5eb2a9f7caf31577b6a1454fc7163918813b`: pin checkpoint 1024, nạp CPU với `weights_only=True` và `strict=True`.
- Lịch sử script lỗi và đã bị thay thế **không bị xóa hoặc đổi SHA**; README_VI.md hiện có lời cảnh báo ngay đầu để phân biệt trạng thái mới với snapshot `DESIGN_ONLY` lịch sử. Không có lý do khoa học để tái chạy những script đó.
- Unit test tổng hợp 13/13 đã PASS trên Windows từ stage trước. Đây **không phải** lần biên dịch/chạy model mới trong lượt review.

## 2. Kiểm tra bằng chứng không chạy lại khoa học

**QA lượt hai: PASS 16/16** dựa trên receipt, audit thật, prereg và báo cáo đã khóa. Xác minh 32 cặp duy nhất (8×4), ngưỡng 0,001, mỗi cặp đúng Flash counter 4 hoặc 0, top1 32/32 và strict FAIL 32/32.

| Arm | Context K/V đã nhìn thấy trong log Windows | Flash thực thi | Strict PASS/8 | Max-abs lớn nhất |
|---|---|---|---:|---:|
| S0 | F16/F16 | ON | 0/8 | 0,0044434023 |
| S1 | F32/F32 | OFF | 0/8 | 0,0030384065 |
| S2 | F32/F32 | ON | 0/8 | 0,0044434023 |
| S3 | F16/F16 | OFF | 0/8 | 0,0026888890 |

Đã quan sát trực tiếp log runtime cho mỗi tổ hợp K/V và Flash, không chỉ dựa vào nhãn lưu ở JSON. Kết quả **S1 vẫn FAIL 8/8** bác bỏ khả năng *chỉ* đổi KV precision hoặc tắt Flash là **đủ** khôi phục strict parity trong 8 fixture mới. Không chứng minh chính xác nguồn sai số, không kết luận Flash hoặc F16 vô tác dụng. `descriptive_contrasts` chỉ là phép trừ max-abs error giữa các arm; không phải hiệu logits từng chiều hay bằng chứng nhân quả trực tiếp.

### Chuỗi SHA đối chiếu

| Hiện vật | SHA-256 |
|---|---|
| `RUN_RECEIPT.json` | `fcaea7a629bd6dda7a4f35b60da686b73b02bc0e9e56ebe7c380d9b9e4c7db09` |
| `AUDIT_FROZEN_NEW_32.json` | `8aca17561d6beca200fbc746854ab0186e5f3d75930737077111a86c475acc6c` |
| Native raw 32×2048 JSONL (do frozen auditor đọc và SHA trên Windows) | `544df628802591bcdda7ca9d6de4779d5e2872ee8b409c6710ede5bbf8ac19b8` |
| Reference raw 8×2048 JSONL (đã băm lại độc lập) | `d6f367269df610a4e1c93edbff9a4dcffb7f0e0b6bd5f77247c5c90394de176c` |
| Reference ZIP sao lưu (đã test ZIP và băm lại) | `6f260c7f52f906a693245f75a51b02fa9641ce34502eb9f2a0aff3c949315ce4` |

Hai receipt/báo cáo được kiểm lại SHA sau khôi phục newline CRLF Windows. **Giới hạn kiểm định độc lập:** RemoteDesktop cắt các dòng raw native dài 2048 logits khoảng 20 nghìn ký tự, nên lượt kiểm tra thứ hai **không tính lại toàn bộ raw native từ đầu**; việc đọc đủ 32×2048 và tính hash gốc thuộc chương trình auditor đã chạy trên Windows. Không nhận là một bên thứ ba đã kiểm tra trực tiếp toàn bộ raw độc lập.

## 3. Giới hạn được chấp nhận khi quyết định merge

- **CI/check-runs trên GitHub: 0**, và **review bên thứ ba: 0** tại HEAD được rà. QA 20/20 + 16/16 là second-pass scoped review của trợ lý, **không phải** chứng nhận độc lập của con người hay CI toàn hệ thống.
- Native raw 32×2048 và log gốc hiện lưu bên trong `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp` của owner, **chưa có bằng chứng bản sao raw ngoài máy Windows**. Khuyến nghị sao lưu vào lưu trữ lâu dài kèm SHA **trước mọi dọn dẹp**; không xóa raw khi merge.
- Bằng chứng về strict parity của 8 fixture lịch sử vẫn **`FAIL_7/8`**, không đánh đồng với `FAIL_32/32` của phép đo mới. `L0013` ghi **FAIL khoa học**, đúng quy tắc append-only.
- Các script Preview, Supplement, Stage đã lỗi được lưu trong lịch sử, không phải entrypoint để chạy lại; thông báo top-level README đã ghi trạng thái này. Đường code nghiên cứu này **không phải** bản vá parity cho production.

Những giới hạn trên không làm vô hiệu quan sát và đủ điều kiện giữ **một kết quả nghiên cứu âm tính** trong `main`; tuy nhiên cần giữ nguyên các lưu ý đó khi dùng lại kết quả.

## 4. Phán quyết cuối

**`FINAL_VERDICT=MERGE` — trong phạm vi bảo toàn khoa học âm tính và mã chẩn đoán.** Các cổng bắt buộc về một lượt khoa học, QA giao thức, provenance source SHA, lineage append-only và không sửa TEST/training đều đạt theo chứng cứ hiện có.

**Không merge ngay trong lượt này**, do chủ dự án chỉ yêu cầu review và phán quyết; `main` vẫn không đổi. PR #16 có thể chuyển trạng thái từ Draft thành Ready for Review sau khi báo cáo được lưu, nhưng thao tác hợp nhất thật cần chủ dự án ra lệnh rõ. Không tự động đồng bộ hoặc xóa worktree local.

**Bước thực hiện tiếp theo:** `TTM_T5_PR16_EXACT_HEAD_OWNER_MERGE_AND_POSTMERGE_READBACK`, chỉ khi owner yêu cầu: đọc lại main/head, merge đúng HEAD đã chốt theo GitHub và xác minh postmerge. Bảo toàn raw science, không chạy lại 32, không train, không sửa các PR #13–#15.

**Biên bản machine-readable:** `artifacts/qa/ttm-t5-parity/TTM_T5_PR16_INDEPENDENT_SOURCE_EVIDENCE_FINAL_MERGE_ADJUDICATION_20261110.json`.

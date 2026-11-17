# Q001 Track A M0 v3 — Phán quyết I1 độc lập

**Phán quyết `HOLD_I1`** · 2026-11-16 · PR #33 · phạm vi fixture và phép đo M0.

## Nguồn và danh tính

- Phiên reviewer Codex `01a1e4ff-9475-7401-939d-a7ba70985fce` tự viết và chạy checker trong phiên này. GitHub dùng tài khoản repository `minhtri22`, cũng là tài khoản đứng tên PR. Tính độc lập ở đây dựa trên phiên thực thi và checker mới. Handoff không cung cấp ID phiên của Agent A để đối chiếu qua GitHub.
- HEAD được review `6ccd00ec3faef0e87b095662fdb099ac01f4709a`. PR #33 là draft, base và HEAD PR #28 đều ở `ebdc54575eed1ff60c402eecf60289f408bb38ca`. Revision CI `639a662ef52d028d0b3f07234bdc6d0a5ed5be62` khớp HEAD ở toàn bộ `tools/` và `.github/`. Phạm vi 16 file và SHA-256 từng file có trong receipt. Diff của PR #33 giới hạn trong Track A và runner được kế thừa từ PR #28. [Handoff ghim](https://github.com/minhtri22/TokenToModel-Lab/blob/6ccd00ec3faef0e87b095662fdb099ac01f4709a/docs/coordination/ttm-abc/track-a/TTM_TRACK_A_M0V3_DISTINCT_I1_REVIEW_HANDOFF_20261116.md) · [CI Windows](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43895224590)

| Byte thực thi | SHA-256 Windows CRLF | SHA-256 blob Git LF |
|---|---|---|
| Runner | `ccc4f496edbda23517c8efa6110b447eeab807d84a087b0284277670e78cc73d` | `de21d93bd81b098daf805e3f9300856411a6810e51c3d3a5641adedd7f7dbbe5` |
| Scorer | `98101e871410e7255cd25f611e5eb9d7068ab264ac162e0af89ef1f1863f6587` | `c00c043fc6e4f0f04fa33c91b79d38691d46bb72c60b3452d26df6281b3f367d` |

## Đóng băng và đọc lại

Đã xác minh tokenizer BPE gốc TRAIN-only trên Windows tại chỗ, sau đó gọi đúng một lần `python.exe -I <runner> fixture-freeze --owner-internal --root <root> --tokenizer-source <tokenizer> --out <new-private-dir>` từ PowerShell 5.1.26100.9818 với Python 3.12.10. Các lần thử trước dừng ở kiểm tra phiên bản, nạp cmdlet hoặc đối chiếu SHA, trước khi gọi runner. Các lần thử đều được kiểm tra đường dẫn đích trống trước khi tiếp tục.

OnePack tại HEAD có ba lỗi PS5.1. Native argument parsing làm hỏng câu lệnh Python có dấu nháy, truy cập trực tiếp `PSObject.Properties.Count` thất bại dưới strict mode, và chuỗi `"\n"` sinh ký tự thừa ở cuối JSON. Checkout LF mặc định tại máy review cũng trượt SHA CRLF của handoff. Bản OnePack cục bộ sửa ba điểm trên, đồng thời cho phép đúng hai thay đổi EOL chưa stage tại worktree riêng sau khi đối chiếu blob LF, đích CRLF byte-for-byte và SHA đã ghim. Các companion file pin theo Git blob giữ dạng LF. Tiến trình PS5.1 tự khởi tạo `PSModulePath` để tải cmdlet hệ thống. Các bản local và log vẫn ở máy Windows.

| Bằng chứng | SHA-256 |
|---|---|
| BPE gốc TRAIN-only | `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc` |
| Records v3 thật | `823a08dd4be0da7748cb258b9bf5b2841dd1fdbac84956eb204be7ba57f8c55d` |
| Manifest v3 | `0b80368a6747994df5f5b8d0e7b35137266ac82f6c9b83d26af5b61f79b3cb04` |
| Receipt freeze riêng | `b82a7ebc29930563db581f7724d0847a725d893860b776b7cc682ec875af4c3a` |
| Receipt OnePack tại máy | `33ace4e05cbffce0fed965a86ac2b272a04ec9aba01e79d489afdab8f05f7eb5` |
| Records lịch sử, khớp trước và sau | `5f1234f583ccf719ca9f0e68de4f47d8b653af777271b8115c5f02307f764e5a` |
| OnePack từ blob Git | `73411526140279a88c55cf950565bd1cba408468ed27e126f1ec1b0c713074d3` |
| OnePack cục bộ đã thực thi | `46deed99cc2835a52e829c506a212086f9e30ec3dffd2194ae8c20105a797af5` |

Taxonomy khớp pin 2.048 token, EOS bị loại khỏi tập ID được phép. Fixture gồm context tổng hợp từ tập ID này. Checker tính lại SHA của records, 80 case và 5 nhóm, rồi đối chiếu cùng kết quả đọc lại và tái sinh của runner. Có 24 TRAIN và 56 probe. Trong 24 case RECOMBINED/ABSENT, không có binding TRAIN xuất hiện ở hai vị trí context. Trong 16 NOVEL_IDS, không có key/value/query ID trùng TRAIN. Cả 16 COUNTERFACTUAL có parent TRAIN riêng và hoán đổi đúng hai giá trị của parent.

## Negative controls

| Control trên fixture thật, logits tổng hợp | Full-vocab top-1 | Four-choice phụ | Cả hai phía đúng trong 16 cặp |
|---|---:|---:|---:|
| Uniform 0, tie-abstain 80/80 mỗi chế độ | 0/80 | 0/80 | 0/16 |
| Xếp hạng theo ID tăng / giảm | 0/80 mỗi chiều | 21/80 mỗi chiều | 0/16 mỗi chiều |
| Xếp hạng ngẫu nhiên cố định theo seed | 0/80 | 20/80 | 0/16 |
| Luôn `NO_ANSWER` (trong đó ABSENT đúng 8/8) | 16/80 | 16/80 | 0/16 |
| Luôn chọn giá trị đầu / cuối, bỏ qua query | 33/80 · 31/80 | 33/80 · 31/80 | 8/16 mỗi cách |
| Oracle độc lập theo query | 80/80 | 80/80 | 16/16 |

640 hoán vị thứ tự khi xếp hạng cho cùng kết quả. Thay gold giữ nguyên candidates ở 80/80 case và đổi kết quả đo theo label mới. Runner từ chối 80/80 record bị sửa thứ tự đã đóng băng. Đổi riêng query trên 64/64 case bound làm đáp án cũ sai, đáp án theo query mới đúng. Trên 16/16 NOVEL_IDS, một token ngoài candidate đứng đầu làm full-vocab top-1 sai dù four-choice đúng, rank của gold là 2. Control chọn theo vị trí đạt 8/16 cặp parent/swap vì query vẫn trỏ vào cùng vị trí. Đổi query khi giữ bindings cố định là kiểm tra riêng cho phụ thuộc vào query. Không gán mốc chance 25%.

Runner source QA đạt 18/18, unittest đạt 27/27 trên máy review. Suite của Agent A đạt 44/45 trên host này so với 45/45 trong CI. Dòng kiểm tra forged-GO nhận exit 86 `HOLD_WINJOB_LIMIT_READBACK_MISMATCH` với đường dẫn giả, trong khi harness đòi exit 2. Kết quả fail closed tại Job Object guard. `release-preflight` thực tế trả exit 2 `HOLD_OWNER_INTERNAL_I1_NOT_PASS` từ verdict lịch sử trên GitHub. Checker mới cũng xác minh từ chối trust anchor thiếu, đường dẫn ngoài root, junction, ghi đè đích mock, sửa bytes của fixture, sửa manifest và sửa scorer text.

## Hai lỗi chặn I1

1. **Full-vocabulary NLL mất tính bất biến khi cộng hằng số.** Với cả 2.048 logits cùng bằng giá trị float32 hữu hạn gần `1e20`, scorer trả NLL `0.0` cho cả 80 case. Giá trị đúng bằng `log(2048) ≈ 7.624618986`, dù top-1 vẫn abstain. Biểu thức cộng log-sum-exp vào peak trước rồi mới trừ gold làm mất số hạng log vì làm tròn. Tính `(peak - gold_logit) + log(sum(exp(logit - peak)))` và kiểm tra lại invariance ở điểm vào tích hợp. [Scorer tại HEAD review](https://github.com/minhtri22/TokenToModel-Lab/blob/6ccd00ec3faef0e87b095662fdb099ac01f4709a/tools/pilot_t4/direct_failure_diag_q001/track_a_m0_v3/q001_m0_goldblind.py#L219)
2. **SHA của source chưa khóa bytecode thực thi.** Trong thư mục mock riêng, checker tạo cache Python chứa cờ vô hại với mtime/size hợp lệ, rồi khôi phục nguyên bytes scorer CRLF. SHA của scorer vẫn đúng và loader thực thi cache. Việc gọi Python với `-B` chỉ ngăn ghi cache trong lần gọi đó. Runner cần đọc source một lần, xác minh SHA rồi compile đúng buffer đã kiểm tra, sau đó chạy lại negative này. [Loader tại HEAD review](https://github.com/minhtri22/TokenToModel-Lab/blob/6ccd00ec3faef0e87b095662fdb099ac01f4709a/tools/pilot_t4/direct_failure_diag_q001/preexec_candidate_20261116/ttm_sm4m_diag_q001.py#L130-L139)

Bước tiếp theo là sửa scorer, loader và OnePack trong cùng revision, ghim lại bytes LF/CRLF theo hợp đồng checkout rõ ràng, rồi review lại đúng pin với fixture v3 đã lưu và các control trên. Giữ bản freeze này làm record custody, đồng thời quyết định rõ cách ràng buộc manifest với scorer SHA mới. I2 `NOT_EXECUTED`, model forward 0, optimizer steps 0, checkpoint access 0 và nonce claim 0.

## Evidence có thể kiểm tra

Checker và receipt chỉ chứa code QA, kết quả tổng hợp, metadata và digest. Fixture, vocabulary, token ID theo case, context, logits thô, đường dẫn dữ liệu cụ thể và log native giữ riêng. Dùng Python 3.12 dưới Windows PowerShell 5.1 với source materialization như bảng SHA ở trên.

```powershell
python.exe -I -B .\check_m0v3_i1.py --root <root> --tree <review-worktree> --fixture <private-new-dir> --tokenizer <private-t1-manifest> --historical <private-old-records>
```

- [Checker tự viết trong phiên review](check_m0v3_i1.py) · SHA-256 `49c76456099200fbb827d2d764906cf151b02ac085f14fbad96d0d00fedcadd3`
- [Receipt công khai, gồm 80 case SHA và 5 group SHA](receipt.json) · SHA-256 `6afb85fb34b4895ce540e586224a683400fe50760c70fb1f079a630afb5a6240`

SHA-256 receipt stdout tại Windows trước khi chuẩn hóa LF để commit là `09f28ed62d49d4539486f3629d521ed2977df159f14845df327e79743078313f`.

# TTM CAUSAL6 — Google Drive chỉ đọc, phân loại lưu trữ và GitHub source of truth

**Ngày:** 2026-11-09. **Thao tác:** READONLY_DRIVE_INVENTORY + GITHUB_PUBLIC_SOURCE_PUBLICATION. **Không xóa/di chuyển/cập nhật Google Drive; không chạy lại H512; không tạo CLAIM khoa học.**

## 1. Kiểm kê có phân cấp các thư mục TTM

| Khu vực | Dung lượng đo metadata (GB thập phân) |
|---|---:|
| `MyDrive/TTM/ttm-small-pilot/` và con | 0.514087695 |
| `TTM_Small4M_EmbeddingSwap/` và `_Input/` | 1.709985027 |
| `TTM_EmbeddingGemma2_D1_*` và con | 0.999733372 |
| **Tổng các khu vực TTM trên** | **3.223806094** |

Nhánh direct-swap1024 có 16 checkpoint ở 4 arms/4 milestones, tổng **809682516 bytes**; direct-swap2048 tương tự **809832672 bytes**. Riêng **12 intermediate checkpoints ở mỗi nhánh** (không tính 4 final) lần lượt **607247964** và **607360680 bytes**. Đây chỉ là **ứng viên có thể giảm dung lượng** sau audit exact-ready-SHA và kiểm tra mọi phụ thuộc resume, không phải danh sách được phép xóa.

Qwen2.5-0.5B-Instruct có `model.safetensors` **988097824 bytes**: owner yêu cầu ưu tiên giữ mô hình để tiết kiệm thời gian tải lại. D1 tokenizer và nguồn khác cũng có thể cần cho nghiên cứu. T4 base step1024 và direct-swap A/B/C/D final checkpoint, candidate donor, CAUSAL6 private ZIP H512, cùng READY cần cho exact-resume phải được bảo toàn khi còn phụ thuộc.

Danh sách Drive này **không phải toàn bộ quota tài khoản Google**; không suy luận phần còn lại do Drive hay Gmail/Google Photos/Trash khi chưa có Google One storage breakdown. Folder shared-with-me không mặc nhiên tính vào quota owner. Google Drive connector không có thông tin quota chính xác qua các hành động hiện có.

## 2. Cổng dung lượng

Ảnh owner trước đó ghi **13.46/15 GB đã dùng**, tương ứng ~1.54 GB trống = ~1.434 GiB. Giao thức CAUSAL6 yêu cầu `>=4 GiB` trống trước CLAIM, thiếu khoảng **2.754967296 GB** thập phân so với ảnh.

Nếu *giữ nguyên riêng Qwen model* 988097824 bytes, ngay cả loại bỏ **toàn bộ các tệp TTM còn lại** trong ba nhóm trên chỉ thu tối đa **2.235708270 GB**, thấp hơn thiếu hụt khoảng **0.519259026 GB**. Việc xóa sạch thực tế không được đề nghị vì còn nhiều mô hình/đầu vào quan trọng. Chuyển script/JSON nhỏ lên GitHub không làm tăng đáng kể free Drive.

**Kết luận:** `HOLD_UNEXECUTED_RESOURCE_DRIVE_CAPACITY` cho Colab; không fake free-space value, không giảm điều kiện 4 GiB khi chưa có amendment riêng dựa trên phép đo thực.

## 3. Quy tắc lưu trữ owner

- **GitHub public**: mã nguồn Python/Notebook/PowerShell đã làm sạch đường dẫn nhận diện cá nhân, hợp đồng, thiết kế, test source, QA và public scientific receipts/lineage, SHA/provenance. Giữ nguồn đúng phiên bản đã freeze, kiểm readback. GitHub không lưu secrets, raw model weights/private data dù kích thước có thể chấp nhận.
- **Private Google Drive**: model/cache ưu tiên giữ; final checkpoint và `READY` cần lưu đầy đủ cho nghiên cứu, checkpoint resume phải chứa **model + AdamW optimizer + RNG + sampler cursor** chứ không chỉ model weights. CAUSAL6 private input ZIP khoảng **61 MB** chứa H512 / model cần cho hiện hành; **không commit GitHub public**.
- **Máy cá nhân**: không yêu cầu làm kho lưu trữ dài hạn ngoài kho khóa bí mật an toàn; workspace cục bộ chỉ staging tạm khi không thể làm hoàn toàn trên Colab/Drive. Không tự xóa dữ liệu nghiên cứu cũ; làm sạch phải có căn cứ SHA, kế hoạch phục hồi và owner scope.
- Dữ liệu TinyStories raw, BPE train pack/private holdout, token IDs, per-story losses, user Drive file IDs, keys và credentials **không** chuyển lên repo công khai. Riêng `H512_PUBLIC_SEAL.json` đã thiết kế công khai, không chứa text/IDs, có thể commit.
- GitHub đã chứa phần lớn docs/QA nghiên cứu, nhưng mã nguồn CAUSAL6 sáu nhánh thực tế trước đây chưa được commit. Commit này bổ sung **6 tệp nguồn** bằng đúng Git blob SHA frozen và public H512 receipt. File `RUN_WINDOWS_H512_SEAL_AND_STAGE.ps1` không công khai trong commit này vì bản gốc có đường dẫn local cá nhân; đã ghim SHA256 `544a48032438bbba9e3f00796a05fc4f473917fd2fdcb2baa983bd5378d20d75`. Notebook SHA-filled cá nhân cũng không xuất bản. README frozen nói pre-H512 theo thời điểm tạo source; receipt H512 mới trong commit phản ánh seal đã đạt.

## 4. H512 và quyền khoa học

Receipt public từ Windows: **H512_SEALED_NOT_SCORED**, 512 stories, 651 windows, 119856 next-token targets, 0 model forwards, không đọc TEST lịch sử. Owner-reported receipt SHA256 `d9ce40f37da7acf2b4b12fd657cdedb366754b2bb29b4b86de144230240f1b03`, membership private SHA256 `544c30b470f5e8718ba35fe016b0f52cac95e559020eae2806e1ff7291a03661`, private window pack SHA256 `d70b23ad862f29f8adc39bb7690688960b67409b5e3f1706abd00c3fc2a72d86`. Đã có CPU parity with C2048 `PASS_EXACT` theo stdout owner, **chưa kiểm tra Tesla T4 runtime**, `CLAIM=NOT_CONSUMED`, `TRAINING=NOT_EXECUTED`.

**Bước tiếp theo:** kiểm tra Google One quota breakdown (Drive/Gmail/Photos), rồi đề xuất **tệp checkpoint trung gian cụ thể** có thể loại sau SHA/READY/dependency check và quyết định riêng. Tiếp tục Colab PRE-CLAIM chỉ khi thực tế >=4 GiB và T4 Free đã được xác minh. Không lặp H512 hoặc mở science nếu cổng HOLD.

# P01 D1 — Kiểm tra tài nguyên Windows chỉ đọc và giới hạn cấp quyền

**Mã:** `TTM_P01_D1_WINDOWS_RESOURCE_PREAUTH_READONLY`  
**Ngày:** 05/11/2026  
**Máy đích:** `DESKTOP-4PSD0G2` / RemoteMCP `machine-1`  
**Workspace hợp lệ:** `D:\WORK\RESEARCH\TokenToModel-Lab`  
**Quyết định:** `H05_HOST_RESOURCES_NOT_MEASURED=HOLD`.

## 1. Quan sát qua thiết bị được quản lý (RemoteMCP)

Đọc trực tiếp trạng thái thiết bị và thông tin năng lực từ nhịp báo có chữ ký (Signed Node Heartbeat):

| Chỉ số | Quan sát | Ý nghĩa |
|---|---|---|
| Trạng thái thiết bị | `ONLINE` | Có thể liên lạc với thiết bị |
| Cơ chế xác thực tình trạng | `AUTHORITATIVE_NODE_HEARTBEAT_RECONCILED_DURABLE_STATE` | Dữ liệu định danh tác vụ RemoteMCP đã đối chiếu với trạng thái node |
| Công việc RemoteMCP đang thực thi | `0` | Không có job RemoteMCP đang chạy theo trạng thái node |
| Công việc chưa phân giải trên node | `0` | Không còn job node chưa có kết luận |
| Trạng thái xử lý node | `FRESH_SIGNED_PROCESS_SNAPSHOT`; không có blocker node được khai báo | Không chứng minh toàn hệ thống không có ứng dụng tiêu thụ tài nguyên |
| RAM khả dụng hiện thời | **Không có trong dữ liệu trả về** | `NOT_MEASURED` |
| D: còn trống hiện thời | **Không có trong dữ liệu trả về** | `NOT_MEASURED` |
| Bộ giới hạn RAM/thời gian của P01 | Chưa triển khai hay kiểm thử | `NOT_VERIFIED` |

Các trường `active_node_jobs=0` và `physical_process_blocker_count=0` **không thể thay thế** chỉ số Windows `FreePhysicalMemory` hay `Win32_LogicalDisk.FreeSpace`. Các số đo RAM/đĩa trong hội thoại cũ không được tái sử dụng để cấp phép.

## 2. Ngưỡng đề xuất, chưa phải giấy phép chạy

| Chỉ số | Ngưỡng ứng viên từ đặc tả H05 | Dữ liệu Windows hiện có |
|---|---:|---|
| RAM khả dụng tại thời điểm xét | Ít nhất **8 GiB** | Chưa đo |
| Ổ D: trống tại thời điểm xét | Ít nhất **16 GiB** | Chưa đo |
| D: trống sau dự phòng đề xuất | Ít nhất **12 GiB** | Chưa đo |
| RAM đỉnh khi chạy BPE | Không vượt **4 GiB** | Chưa có phép đo |
| Dữ liệu nguồn được phê duyệt | Tối đa **64 MiB** | Không có nguồn nào được cấp quyền |
| Số tài liệu | Tối đa **2.000** | Chưa có |
| Thời gian thực thi | Tối đa **1.800 giây** | Chưa chạy |

Các ngưỡng này là **ứng viên thiết kế**, chưa được kiểm định khả năng bảo vệ tài nguyên của tiến trình thực.

## 3. Đường đo Windows chỉ đọc được chuẩn bị

- Tên chương trình: `TTM_P01_D1_RESOURCE_READONLY_PREFLIGHT.ps1`.
- SHA-256 chính xác: `e48e6a101e640a483f727786e50032f04e1b39bdbc6c6b97b75d9c437c606606`.
- Chương trình kiểm tra đúng kho `minhtri22/TokenToModel-Lab`, ranh giới đường dẫn, danh sách worktree, `main` và đọc thông số RAM/đĩa bằng `Get-CimInstance`.
- Chương trình chỉ hiển thị số liệu trên màn hình, **không tạo/đổi/xóa tệp, không fetch/pull/merge Git, không chạy Python, không tải corpus và không huấn luyện**.
- Phải kiểm SHA-256 trước khi thực hiện trên Windows PowerShell 5.1. Vì là khảo sát chỉ đọc, kết quả vượt ngưỡng ứng viên chỉ là `CANDIDATE_RESOURCE_SNAPSHOT`, **không phải** `P01_EXECUTION_PERMIT`.
- Đường dẫn gợi ý nếu cần lưu script: `D:\WORK\RESEARCH\TokenToModel-Lab\tmp\TTM_P01_D1_RESOURCE_READONLY_PREFLIGHT.ps1`; việc người dùng lưu script ở đó không tạo worktree mới. Có thể chép nội dung vào PowerShell để không tạo file.
- Trong bước này, chương trình mới được kiểm tra tĩnh nguồn. **Chưa có xác nhận chạy trên Windows**, nên không ghi RAM/D: PASS.

## 4. Điều kiện sau số đo

- Nếu thiếu thông số RAM/đĩa, báo `RESOURCE_METRIC_UNAVAILABLE` và dừng quyết định H05.
- Nếu RAM dưới 8 GiB hoặc D: dưới 16 GiB, báo `CANDIDATE_THRESHOLD_NOT_MET`; không giảm ngưỡng trong cùng hồ sơ.
- Nếu số đo trên ngưỡng nhưng chưa có trình giới hạn RAM/thời gian được QA, tiếp tục `H05_RUNTIME_GUARD_PENDING`.
- Bất kỳ lúc nào nguồn dữ liệu chưa được cấp quyền thì H02 vẫn HOLD, dù tài nguyên đủ.

## 5. Quyết định

`H05_SIGNED_NODE_CAPACITY_OBSERVED=PASS_READ_ONLY`  
`H05_WINDOWS_FREE_RAM=NOT_MEASURED`  
`H05_WINDOWS_D_FREE=NOT_MEASURED`  
`H05_RESOURCE_GUARD_QA=NOT_PERFORMED`  
`H05_D1_LOCK=HOLD`  
`P01_WORKTREE_CREATION_AUTHORIZED=false`  
`P01_DATA_DOWNLOAD_AUTHORIZED=false`  
`P01_TRAINING_AUTHORIZED=false`

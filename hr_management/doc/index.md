# Module HR Management - Tài liệu Chức năng

## 1. Tổng quan

**HR Management** là một module tùy chỉnh cho Odoo 17, được xây dựng để cung cấp một giải pháp quản lý nhân sự tập trung và hiệu quả. Module cho phép quản lý thông tin nhân viên, cơ cấu tổ chức (phòng ban, vị trí công việc), và kiểm soát quyền truy cập một cách linh hoạt.

## 2. Các Chức năng Chính

### 2.1. Quản lý Nhân viên (`hr.employee`)

Đây là model cốt lõi, lưu trữ toàn bộ thông tin về nhân viên.

#### 2.1.1. Thông tin chi tiết

- **Thông tin công việc:**
  - Email, điện thoại công việc (cố định và di động).
  - Liên kết chặt chẽ với **Phòng ban** (`hr.department`) và **Vị trí công việc** (`hr.job`).
  - Xác định **Quản lý trực tiếp** (`manager_id`) và **Người hướng dẫn** (`coach_id`).
  - Ngày bắt đầu/kết thúc làm việc, lịch làm việc (`resource_calendar_id`), và múi giờ (`tz`).
  - Trạng thái làm việc (`work_status`): Active, Left.

- **Thông tin cá nhân:**
  - Địa chỉ, email, điện thoại cá nhân.
  - Thông tin nhân khẩu học: Ngày sinh, giới tính, quốc tịch.
  - Giấy tờ tùy thân: Số CCCD/CMND, số hộ chiếu.
  - Trình độ học vấn: Bằng cấp, lĩnh vực học, trường học.

- **Đồng bộ hóa với Người dùng (`res.users`):**
  - Mỗi nhân viên có thể được liên kết với một tài khoản người dùng duy nhất.
  - Thông tin cơ bản (tên, email, ảnh đại diện, ngôn ngữ, múi giờ) được **đồng bộ hai chiều** giữa nhân viên và người dùng. Thay đổi ở một nơi sẽ tự động cập nhật ở nơi còn lại.

#### 2.1.2. Tự động hóa và Ràng buộc
- **Tự động tạo User:** Có thể cấu hình trong *Settings* để tự động tạo một tài khoản người dùng mới khi một nhân viên được tạo với email công việc.
- **Ràng buộc dữ liệu:**
  - Ngày sinh không được ở tương lai.
  - Ngày kết thúc công việc không được trước ngày bắt đầu.
  - Nhân viên không thể là quản lý/người hướng dẫn của chính mình.
  - Email công việc và liên kết tới User là duy nhất.

#### 2.1.3. Tương tác
- **Nút "Related User":** Trên form nhân viên, cho phép truy cập nhanh đến form người dùng liên quan.
- **Trang "My Profile":** Nhân viên có thể tự xem và chỉnh sửa thông tin cá nhân của mình (nếu được cho phép).

### 2.2. Quản lý Cơ cấu Tổ chức

#### 2.2.1. Phòng ban (`hr.department`)
- Quản lý phòng ban theo **cấu trúc cây (cha-con)**, cho phép xây dựng sơ đồ tổ chức đa cấp.
- Mỗi phòng ban có một **Quản lý** (`manager_id`).
- **Smart button "Employees":** Hiển thị và truy cập nhanh danh sách tất cả nhân viên thuộc phòng ban đó.
- Tự động đếm số lượng nhân viên trong phòng ban.

#### 2.2.2. Vị trí Công việc (`hr.job`)
- Định nghĩa các chức danh, vị trí công việc trong công ty.
- Mỗi vị trí có thể được gán cho một phòng ban cụ thể.
- **Smart button "Employees":** Hiển thị và truy cập nhanh danh sách nhân viên đang giữ vị trí đó.

### 2.3. Quản lý Phân quyền và Truy cập

Module xây dựng một hệ thống phân quyền chi tiết với 2 cấp độ chính.

#### 2.3.1. Các Nhóm quyền
- **HR Management / User (`group_hr_management_user`):**
  - Có quyền xem danh sách nhân viên, phòng ban, vị trí công việc.
  - Có thể xem và tự chỉnh sửa thông tin cá nhân của mình.
  - Không thể tạo/xóa nhân viên, phòng ban, vị trí.
  - Có thể tạo yêu cầu nâng cấp quyền.
- **HR Management / Manager (`group_hr_management_manager`):**
  - Có **toàn quyền** (CRUD) trên các model Nhân viên, Phòng ban, Vị trí công việc.
  - Có thể duyệt/từ chối các yêu cầu nâng cấp quyền.
  - Có quyền truy cập menu *Configuration*.

#### 2.3.2. Yêu cầu Nâng cấp Quyền (`hr.access.request`)
- Một cơ chế cho phép nhân viên (User) gửi yêu cầu để trở thành Manager.
- **Luồng hoạt động:**
  1. User tạo một yêu cầu mới từ menu "Access Requests".
  2. Yêu cầu ở trạng thái "To Approve".
  3. Manager vào danh sách yêu cầu, có thể **Approve** (Duyệt) hoặc **Refuse** (Từ chối).
  4. Nếu **Approve**: Hệ thống tự động gán người dùng vào nhóm `group_hr_management_manager`.
  5. Nếu **Refuse**: Yêu cầu chuyển sang trạng thái "Refused".
- **Ràng buộc:**
  - Không thể tạo yêu cầu cho nhân viên không có tài khoản user.
  - Không thể tạo yêu cầu trùng lặp khi đã có yêu cầu đang chờ xử lý.
  - Không thể hạ quyền của Manager cuối cùng trong hệ thống.

### 2.4. Cấu hình và Tùy chỉnh

- **Menu Cấu hình (`Configuration`):**
  - Quản lý Vị trí công việc (`Job Positions`).
  - Quản lý Lịch làm việc (`Working Schedules`).
- **Menu Settings (dành cho System Admin):**
  - **Auto-Create User:** Bật/tắt tính năng tự động tạo user khi tạo nhân viên mới.

### 2.5. Cải tiến Giao diện Người dùng (UI/UX)

- **Menu "My Profile":** Thay thế menu "Preferences" mặc định của Odoo, điều hướng người dùng đến một trang hồ sơ cá nhân thân thiện và đầy đủ thông tin hơn.
- **Search Panel:** Cung cấp bộ lọc theo Phòng ban trên giao diện danh sách nhân viên, giúp tìm kiếm và phân loại dễ dàng.
- **Smart Buttons:** Các nút bấm thông minh được thêm vào form Nhân viên và Phòng ban để điều hướng nhanh đến các bản ghi liên quan.

## 3. Dữ liệu Demo

Module đi kèm một bộ dữ liệu demo (`hr_management_demo.xml`) đơn giản, giúp người dùng mới nhanh chóng hiểu được cách hoạt động của hệ thống:
- Tạo sẵn một cơ cấu phòng ban đa cấp.
- Tạo sẵn các vị trí công việc tương ứng.
- Tạo một danh sách nhân viên với các vai trò và mối quan hệ quản lý rõ ràng.
- Tự động gán quyền Manager cho các nhân viên quản lý trong dữ liệu demo.
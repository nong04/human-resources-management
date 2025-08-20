# Chức năng Chi tiết - HR Management

Tài liệu này mô tả sâu về các tính năng, logic nghiệp vụ, và các quy tắc tự động hóa được xây dựng trong module **HR Management**.

## 1. Quản lý Nhân viên (`hr.employee`)

Đây là đối tượng trung tâm của module, được thiết kế để lưu trữ một hồ sơ nhân sự 360 độ.

### 1.1. Đồng bộ hóa với Người dùng (`res.users`)

Tính năng này tạo ra một liên kết chặt chẽ giữa hồ sơ nhân viên và tài khoản đăng nhập hệ thống.

- **Cơ chế:**
  - Sử dụng các trường `related` trên model `res.users` để ánh xạ đến các trường trên `hr.employee`.
  - Ghi đè phương thức `create` và `write` trên cả hai model để đảm bảo dữ liệu luôn nhất quán.
- **Luồng dữ liệu:**
  - **Từ Nhân viên -> Người dùng:** Khi HR Manager cập nhật tên, email công việc, ảnh đại diện của nhân viên, thông tin tương ứng trên tài khoản người dùng sẽ tự động được cập nhật.
  - **Từ Người dùng -> Nhân viên (My Profile):** Khi người dùng tự cập nhật thông tin cá nhân qua menu "My Profile", các trường tương ứng trong hồ sơ `hr.employee` của họ cũng được cập nhật. Điều này trao quyền cho nhân viên tự quản lý thông tin của mình.
- **Lợi ích:** Giảm thiểu việc nhập liệu trùng lặp và đảm bảo tính nhất quán dữ liệu trên toàn hệ thống.

### 1.2. Tự động hóa & Ràng buộc

Để đảm bảo tính toàn vẹn và chính xác của dữ liệu, module đã tích hợp nhiều quy tắc tự động.

- **Tự động tạo User:**
  - **Kích hoạt:** Tại `HR Management > Configuration > Settings > Auto-Create User`.
  - **Logic:** Khi một bản ghi `hr.employee` mới được tạo và có điền `Work Email`, hệ thống sẽ kiểm tra xem đã có `user_id` hay chưa. Nếu chưa, một tài khoản `res.users` mới sẽ được tự động tạo với `login` là `work_email` và được gán vào nhóm quyền `User` mặc định.
  - **Mục đích:** Đơn giản hóa quy trình onboarding, giúp nhân viên mới nhanh chóng có tài khoản để truy cập hệ thống.

- **Các Ràng buộc Dữ liệu (`@api.constrains`):**
  - `_check_birthday`: Ngày sinh không được nằm trong tương lai.
  - `_check_manager_coach`: Một nhân viên không thể tự làm quản lý hoặc người hướng dẫn của chính mình.
  - `_check_work_dates`: Ngày kết thúc công việc phải sau hoặc bằng ngày bắt đầu.
  - `_sql_constraints`: Đảm bảo `work_email` và `user_id` là duy nhất trên toàn bộ bảng `hr_employee`.

## 2. Quản lý Cơ cấu Tổ chức

Module cho phép mô hình hóa cấu trúc doanh nghiệp một cách linh hoạt.

- **Phòng ban (`hr.department`):**
  - **Cấu trúc cây:** Sử dụng `parent_id` và `child_ids` để tạo ra mối quan hệ cha-con, cho phép xây dựng sơ đồ tổ chức đa cấp không giới hạn.
  - **Ràng buộc đệ quy:** Ngăn chặn người dùng tạo vòng lặp (ví dụ: Phòng A là con của Phòng B, và Phòng B lại là con của Phòng A).
- **Vị trí Công việc (`hr.job`):**
  - **Tính duy nhất:** Tên vị trí công việc phải là duy nhất trong cùng một phòng ban để tránh nhầm lẫn.
- **Smart Buttons:**
  - Model `hr.department` có các nút bấm thông minh (smart buttons) hiển thị số lượng nhân viên liên quan. Khi nhấn vào, hệ thống sẽ tự động điều hướng đến danh sách các nhân viên đó, giúp người dùng truy cập dữ liệu liên quan một cách nhanh chóng.

## 3. Hệ thống Phân quyền

Hệ thống phân quyền được thiết kế rõ ràng để kiểm soát quyền truy cập và bảo mật thông tin.

### 3.1. Các Nhóm quyền

- **User (`group_hr_management_user`):**
  - **Quyền hạn:** Là nhóm quyền cơ bản nhất. Người dùng thuộc nhóm này có thể xem thông tin công khai của các nhân viên khác và tự chỉnh sửa thông tin của chính mình. Họ không có quyền tạo mới hay xóa nhân viên.
  - **Mục đích:** Dành cho tất cả nhân viên trong công ty.
- **Manager (`group_hr_management_manager`):**
  - **Quyền hạn:** Kế thừa tất cả quyền của nhóm User và có thêm toàn quyền (Tạo, Đọc, Sửa, Xóa) trên các model `hr.employee`, `hr.department`, và `hr.job`.
  - **Mục đích:** Dành cho bộ phận Nhân sự hoặc các cấp quản lý có trách nhiệm quản lý dữ liệu nhân sự.

### 3.2. Quy trình Yêu cầu Cấp quyền (`hr.access.request`)

Đây là một quy trình nghiệp vụ được xây dựng để quản lý việc nâng cấp quyền một cách minh bạch.

- **Logic:**
  1.  Một nhân viên (đã có user) tạo một bản ghi `hr.access.request`.
  2.  Hệ thống kiểm tra để đảm bảo không có yêu cầu nào khác đang chờ xử lý cho nhân viên này.
  3.  Yêu cầu được chuyển sang trạng thái `confirm`.
  4.  Một Manager nhận được thông báo và vào duyệt.
  5.  Khi **Approve**, hệ thống sẽ tự động thực hiện thao tác ghi vào `res.groups` để thêm user của nhân viên vào nhóm `group_hr_management_manager`.
- **Ràng buộc an toàn:**
  - Hệ thống sẽ ngăn chặn việc hạ quyền của người quản lý cuối cùng trong hệ thống để tránh trường hợp không còn ai có quyền quản trị.

## 4. Cải tiến Giao diện và Trải nghiệm Người dùng (UI/UX)

- **Menu "My Profile":**
  - **Cơ chế:** Ghi đè (`override`) `user_menuitems` mặc định của Odoo bằng JavaScript.
  - **Hành động:** Thay đổi `description` của menu "Preferences" thành "My Profile" và điều hướng người dùng đến một form view tùy chỉnh của `res.users` đã được thiết kế lại để thân thiện hơn.
- **Form View Nhân viên:**
  - **Trường `is_manager` và `is_self`:** Đây là các trường `compute` không lưu trữ, được tính toán dựa trên quyền và ID của người dùng hiện tại. Chúng được dùng để điều khiển thuộc tính `readonly` và `invisible` trên giao diện XML, giúp ẩn/hiện hoặc cho/không cho phép sửa các trường tùy theo ngữ cảnh. Ví dụ, một nhân viên chỉ có thể sửa các trường thông tin cá nhân của chính mình.
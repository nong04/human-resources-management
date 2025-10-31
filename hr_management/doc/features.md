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

---

# Detailed Features - HR Management

This document describes in depth the features, business logic, and automation rules built into the **HR Management** module.

## 1. Employee Management (`hr.employee`)

This is the central object of the module, designed to store a 360-degree HR profile.

### 1.1. Synchronization with User (`res.users`)

This feature creates a strong link between the employee profile and the system login account.

- **Mechanism:**
  - Uses `related` fields on the `res.users` model to map to fields on `hr.employee`.
  - Overrides the `create` and `write` methods on both models to ensure data consistency.
- **Data Flow:**
  - **From Employee -> User:** When an HR Manager updates an employee's name, work email, or profile picture, the corresponding information on the user account is automatically updated.
  - **From User -> Employee (My Profile):** When a user updates their personal information via the "My Profile" menu, the corresponding fields in their `hr.employee` profile are also updated. This empowers employees to manage their own information.
- **Benefits:** Minimizes duplicate data entry and ensures data consistency across the system.

### 1.2. Automation & Constraints

To ensure data integrity and accuracy, the module integrates several automatic rules.

- **Auto-Create User:**
  - **Activation:** At `HR Management > Configuration > Settings > Auto-Create User`.
  - **Logic:** When a new `hr.employee` record is created with a `Work Email`, the system checks if a `user_id` already exists. If not, a new `res.users` account is automatically created with the `login` as the `work_email` and assigned to the default `User` group.
  - **Purpose:** Simplifies the onboarding process, helping new employees quickly get an account to access the system.

- **Data Constraints (`@api.constrains`):**
  - `_check_birthday`: The date of birth cannot be in the future.
  - `_check_manager_coach`: An employee cannot be their own manager or coach.
  - `_check_work_dates`: The employment end date must be on or after the start date.
  - `_sql_constraints`: Ensures `work_email` and `user_id` are unique across the entire `hr_employee` table.

## 2. Organizational Structure Management

The module allows for flexible modeling of the company structure.

- **Department (`hr.department`):**
  - **Tree Structure:** Uses `parent_id` and `child_ids` to create a parent-child relationship, allowing for the construction of a multi-level organizational chart.
  - **Recursion Constraint:** Prevents users from creating loops (e.g., Department A is a child of Department B, and Department B is a child of Department A).
- **Job Position (`hr.job`):**
  - **Uniqueness:** The job position name must be unique within the same department to avoid confusion.
- **Smart Buttons:**
  - The `hr.department` model has smart buttons that display the number of related employees. Clicking them automatically navigates to the list of those employees, helping users quickly access related data.

## 3. Permission and Access System

The permission system is clearly designed to control access and secure information.

### 3.1. User Groups

- **User (`group_hr_management_user`):**
  - **Permissions:** The most basic permission group. Users in this group can view public information of other employees and edit their own personal information. They cannot create or delete employees.
  - **Purpose:** Intended for all employees in the company.
- **Manager (`group_hr_management_manager`):**
  - **Permissions:** Inherits all permissions from the User group and has full CRUD (Create, Read, Update, Delete) rights on the `hr.employee`, `hr.department`, and `hr.job` models.
  - **Purpose:** Intended for the HR department or managers responsible for managing HR data.

### 3.2. Access Request Workflow (`hr.access.request`)

This is a business process built to manage permission upgrades transparently.

- **Logic:**
  1.  An employee (who already has a user account) creates a new `hr.access.request` record.
  2.  The system checks to ensure there are no other pending requests for this employee.
  3.  The request is moved to the `confirm` state.
  4.  A Manager is notified and reviews the request.
  5.  Upon **Approve**, the system automatically writes to `res.groups` to add the employee's user to the `group_hr_management_manager` group.
- **Security Constraint:**
  - The system prevents the demotion of the last manager in the system to avoid a situation where no one has administrative rights.

## 4. UI/UX Enhancements

- **"My Profile" Menu:**
  - **Mechanism:** Overrides Odoo's default `user_menuitems` using JavaScript.
  - **Action:** Changes the `description` of the "Preferences" menu to "My Profile" and directs the user to a custom `res.users` form view redesigned to be more user-friendly.
- **Employee Form View:**
  - **`is_manager` and `is_self` fields:** These are non-stored `compute` fields, calculated based on the current user's permissions and ID. They are used to control `readonly` and `invisible` attributes in the XML view, hiding/showing or allowing/disallowing edits to fields based on the context. For example, an employee can only edit their own personal information fields.
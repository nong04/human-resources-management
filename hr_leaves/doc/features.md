# Chức năng Chi tiết - Leave Management

Tài liệu này mô tả sâu về các tính năng, logic nghiệp vụ, và các quy tắc tự động hóa được xây dựng trong module **Leave Management**.

## 1. Logic Tính toán Thời gian nghỉ Thông minh

Đây là một trong những tính năng cốt lõi của module, đảm bảo số ngày nghỉ được tính toán chính xác và công bằng.

### 1.1. Tự động loại trừ Ngày nghỉ

- **Cơ chế:**
  - Khi một nhân viên chọn "Start Date" và "End Date" trong một yêu cầu nghỉ phép, trường `duration` sẽ được tính toán lại tự động.
- **Logic hoạt động (`_compute_duration`):**
  1.  **Lấy Lịch làm việc:** Hệ thống truy xuất `resource_calendar_id` và múi giờ `tz` từ hồ sơ của nhân viên. Lịch làm việc này định nghĩa các ngày và giờ làm việc trong tuần.
  2.  **Lấy Ngày nghỉ Lễ:** Hệ thống gọi phương thức `get_public_leave_dates()` từ model `hr.public.leaves` để lấy danh sách tất cả các ngày nghỉ lễ chung của công ty.
  3.  **Tính toán:** Hệ thống duyệt qua từng ngày trong khoảng thời gian xin nghỉ, và chỉ đếm những ngày thỏa mãn cả hai điều kiện:
      - Là một ngày làm việc theo lịch của nhân viên (`_work_intervals_batch`).
      - **Không** phải là ngày nghỉ lễ chung.
- **Kết quả:** `duration` chỉ phản ánh số ngày làm việc thực tế mà nhân viên sẽ nghỉ, loại bỏ hoàn toàn các ngày nghỉ cuối tuần và lễ tết.

### 1.2. Kiểm tra Số dư Phép

Module đảm bảo nhân viên không thể xin nghỉ quá số ngày phép được cấp.

- **Cơ chế:**
  - Logic này được kích hoạt khi nhân viên nhấn nút "Submit" (`action_confirm`) trên một yêu cầu nghỉ phép có loại phép `requires_allocation` = 'yes'.
- **Logic hoạt động (`_get_remaining_days`):**
  1.  **Tính tổng Cấp phát:** Hệ thống tìm tất cả các bản ghi `hr.leaves.allocation` đã được `approved` cho nhân viên đó, thuộc cùng loại phép và còn hiệu lực, sau đó tính tổng `duration`.
  2.  **Tính tổng đã nghỉ:** Hệ thống tìm tất cả các bản ghi `hr.leaves.request` đã được `approved` cho nhân viên đó, thuộc cùng loại phép (không tính yêu cầu hiện tại), và tính tổng `duration`.
  3.  **So sánh:** Hệ thống so sánh số ngày đang yêu cầu với `(Tổng Cấp phát - Tổng đã nghỉ)`. Nếu số ngày yêu cầu lớn hơn, một lỗi sẽ được hiển thị và yêu cầu không thể được gửi đi.

## 2. Quy trình Phê duyệt & Phân quyền

Module xây dựng một quy trình phê duyệt rõ ràng và hệ thống phân quyền linh hoạt.

### 2.1. Luồng Phê duyệt (Workflow)

- **Bước 1: Gửi yêu cầu (`action_confirm`):**
  - Khi nhân viên nhấn "Submit", trạng thái của yêu cầu chuyển từ `draft` sang `confirm`.
  - Hệ thống tự động tạo một "Activity" (Hoạt động) (`activity_schedule`) và gán nó cho người quản lý duyệt phép (`leaves_manager_id`) của nhân viên đó. Người quản lý sẽ nhận được thông báo trong Odoo.
- **Bước 2: Phê duyệt/Từ chối (`action_approve` / `action_refuse`):**
  - Người quản lý mở yêu cầu và nhấn "Approve" hoặc "Refuse".
  - Trạng thái của yêu cầu được cập nhật tương ứng, đồng thời `approver_id` và `response` được ghi lại.
  - Hệ thống tự động gửi một tin nhắn vào chatter của yêu cầu (`message_post`), ghi lại ai đã duyệt/từ chối và vào thời điểm nào.
  - "Activity" đã tạo trước đó sẽ được đánh dấu là hoàn thành (`activity_feedback`).

### 2.2. Hệ thống Phân quyền

- **Người duyệt phép (`leaves_manager_id`):**
  - Mặc định, người duyệt phép của một nhân viên là user của trưởng phòng của nhân viên đó (`manager_id.user_id`).
  - Tuy nhiên, trường này có thể được HR Manager tùy chỉnh riêng trên hồ sơ nhân viên, cho phép một người khác (ví dụ: trưởng phòng nhân sự) duyệt phép cho một nhân viên cụ thể.
- **Record Rules (Quy tắc Truy cập Dữ liệu):**
  - **User (`group_hr_leaves_user`):** Chỉ có thể thấy các yêu cầu/cấp phát có `domain_force` là `['|', ('employee_id.user_id', '=', user.id), ('employee_id.leaves_manager_id', '=', user.id)]`. Điều này cho phép quản lý cấp trung xem yêu cầu của team mình mà không cần quyền Manager toàn hệ thống.
  - **Manager (`group_hr_leaves_manager`):** Có thể thấy tất cả yêu cầu/cấp phát trong toàn bộ công ty.
- **Ràng buộc an toàn:**
  - Hệ thống sẽ ngăn chặn việc hạ quyền của người quản lý cuối cùng trong hệ thống để tránh trường hợp không còn ai có quyền quản trị.

### 2.3. Chống Trùng lặp

- **Cơ chế:**
  - Logic `_check_overlapping_leaves` được kích hoạt mỗi khi một yêu cầu được tạo hoặc chuyển sang trạng thái `approved`.
- **Logic hoạt động:**
  - Hệ thống tìm kiếm các yêu cầu nghỉ phép khác của cùng một nhân viên, đã ở trạng thái `approved`, có khoảng thời gian bị trùng lặp (`date_to >= date_from` và `date_from <= date_to`) với yêu cầu hiện tại.
  - Nếu tìm thấy bất kỳ sự trùng lặp nào, hệ thống sẽ báo lỗi và ngăn chặn hành động.
- **Mục đích:** Đảm bảo dữ liệu nghỉ phép luôn chính xác và không có xung đột về lịch trình.

## 3. Tích hợp và Trải nghiệm Người dùng

- **Smart Button trên Form Nhân viên:**
  - Module thêm một nút bấm thông minh "Leaves" trực tiếp trên form `hr.employee`.
  - Nút này hiển thị số ngày phép còn lại (`remaining_leaves`), được tính toán real-time.
  - Cho phép người dùng và quản lý truy cập nhanh vào lịch sử nghỉ phép của nhân viên đó chỉ bằng một cú nhấp chuột.
- **Lịch nghỉ Tổng quan (`hr.leaves.calendar`):**
  - Cung cấp một giao diện lịch (`Calendar View`) tại menu **Overview**.
  - Hiển thị đồng thời cả các yêu cầu nghỉ phép đã được duyệt (màu theo nhân viên) và các ngày nghỉ lễ chung của công ty.
  - Giúp quản lý có cái nhìn tổng thể về sự vắng mặt trong team và lên kế hoạch công việc hiệu quả.
- **Bộ lọc Tìm kiếm:**
  - Giao diện danh sách yêu cầu nghỉ phép được trang bị các bộ lọc mặc định tiện lợi như "My Requests", "My Team's Requests", và "To Approve", giúp người dùng nhanh chóng tìm thấy thông tin cần thiết.

---

# Detailed Features - Leave Management

This document describes in depth the features, business logic, and automation rules built into the **Leave Management** module.

## 1. Intelligent Leave Duration Calculation Logic

This is one of the core features of the module, ensuring leave days are calculated accurately and fairly.

### 1.1. Automatic Exclusion of Non-Working Days

- **Mechanism:**
  - When an employee selects a "Start Date" and "End Date" in a leave request, the `duration` field is recalculated automatically.
- **How it works (`_compute_duration`):**
  1.  **Get Working Schedule:** The system retrieves the `resource_calendar_id` and `tz` (timezone) from the employee's profile. This schedule defines the working days and hours of the week.
  2.  **Get Public Holidays:** The system calls the `get_public_leave_dates()` method from the `hr.public.leaves` model to get a list of all company-wide public holidays.
  3.  **Calculation:** The system iterates through each day in the requested leave period and only counts the days that meet both conditions:
      - It is a working day according to the employee's schedule (`_work_intervals_batch`).
      - It is **not** a public holiday.
- **Result:** The `duration` only reflects the actual number of working days the employee will be absent, completely excluding weekends and public holidays.

### 1.2. Leave Balance Check

The module ensures that employees cannot request more leave days than they have been allocated.

- **Mechanism:**
  - This logic is triggered when an employee clicks the "Submit" button (`action_confirm`) on a leave request for a leave type where `requires_allocation` = 'yes'.
- **How it works (`_get_remaining_days`):**
  1.  **Calculate Total Allocation:** The system finds all `approved` `hr.leaves.allocation` records for that employee, of the same leave type, and within the validity period, then sums their `duration`.
  2.  **Calculate Total Taken:** The system finds all `approved` `hr.leaves.request` records for that employee, of the same leave type (excluding the current request), and sums their `duration`.
  3.  **Comparison:** The system compares the currently requested days with `(Total Allocation - Total Taken)`. If the requested amount is greater, an error is displayed, and the request cannot be submitted.

## 2. Approval Workflow & Permissions

The module establishes a clear approval process and a flexible permission system.

### 2.1. Approval Workflow

- **Step 1: Submit Request (`action_confirm`):**
  - When an employee clicks "Submit", the request's state changes from `draft` to `confirm`.
  - The system automatically creates an "Activity" (`activity_schedule`) and assigns it to the employee's leave approver (`leaves_manager_id`). The approver will receive a notification in Odoo.
- **Step 2: Approve/Refuse (`action_approve` / `action_refuse`):**
  - The manager opens the request and clicks "Approve" or "Refuse".
  - The request's state is updated accordingly, and the `approver_id` and `response` are recorded.
  - The system automatically posts a message in the request's chatter (`message_post`), logging who approved/refused and when.
  - The previously created "Activity" is marked as done (`activity_feedback`).

### 2.2. Permission System

- **Leave Approver (`leaves_manager_id`):**
  - By default, an employee's leave approver is the user of their direct manager (`manager_id.user_id`).
  - However, this field can be manually customized on the employee profile by an HR Manager, allowing another person (e.g., the head of HR) to approve leaves for a specific employee.
- **Record Rules:**
  - **User (`group_hr_leaves_user`):** Can only see requests/allocations where the `domain_force` is `['|', ('employee_id.user_id', '=', user.id), ('employee_id.leaves_manager_id', '=', user.id)]`. This allows mid-level managers to see their team's requests without needing system-wide Manager rights.
  - **Manager (`group_hr_leaves_manager`):** Can see all requests/allocations across the entire company.
- **Security Constraint:**
  - The system prevents the demotion of the last manager in the system to avoid a situation where no one has administrative rights.

### 2.3. Overlap Prevention

- **Mechanism:**
  - The `_check_overlapping_leaves` logic is triggered whenever a request is created or its state is changed to `approved`.
- **How it works:**
  - The system searches for other leave requests from the same employee that are already in the `approved` state and have an overlapping time period (`date_to >= date_from` and `date_from <= date_to`).
  - If any overlap is found, the system raises an error and prevents the action.
- **Purpose:** To ensure leave data is always accurate and there are no scheduling conflicts.

## 3. Integration and User Experience

- **Smart Button on Employee Form:**
  - The module adds a "Leaves" smart button directly to the `hr.employee` form.
  - This button displays the remaining leave days (`remaining_leaves`), calculated in real-time.
  - It allows users and managers to quickly access an employee's leave history with a single click.
- **Leave Overview Calendar (`hr.leaves.calendar`):**
  - Provides a `Calendar View` accessible from the **Overview** menu.
  - It displays both approved leave requests (colored by employee) and company-wide public holidays simultaneously.
  - This helps managers get a holistic view of team absences and plan work effectively.
- **Search Filters:**
  - The leave request list view is equipped with convenient default filters like "My Requests", "My Team's Requests", and "To Approve", helping users quickly find the information they need.
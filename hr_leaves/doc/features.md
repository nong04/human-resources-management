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
# Chức năng Chi tiết - Payroll & Attendance

Tài liệu này giải thích sâu về các tính năng, logic nghiệp vụ, và các quy tắc tự động hóa được xây dựng trong module **Payroll & Attendance**.

## 1. Logic Tính lương Toàn diện (`action_compute_sheet`)

Đây là chức năng cốt lõi, tự động hóa việc tính toán lương chi tiết cho từng nhân viên.

- **Cơ chế:**
  - Khi nút "Compute Sheet" được nhấn, hệ thống thực hiện một chuỗi các bước tính toán phức tạp.
- **Logic hoạt động:**
  1.  **Thu thập Dữ liệu:**
      - Lấy thông tin cơ bản: `base_salary`, `allowance`, lịch làm việc (`resource_calendar_id`), múi giờ (`tz`) từ hồ sơ nhân viên.
      - Lấy toàn bộ bản ghi chấm công (`payroll.attendance.record`) trong kỳ lương.
      - Lấy toàn bộ yêu cầu nghỉ phép đã duyệt (`hr.leaves.request`) trong kỳ.
      - Lấy toàn bộ ngày nghỉ lễ (`hr.public.leaves`) và hệ số nhân lương (`public_leaves_rate`) trong kỳ.
      - Đọc các tham số cấu hình hệ thống (tỷ lệ OT, dung sai, chính sách nghỉ phép) từ `ir.config_parameter`.
  2.  **Tính toán Giờ làm:**
      - **Giờ tiêu chuẩn (`standard_work_hours`):** Tính tổng số giờ làm việc theo lịch trong kỳ, trừ ngày lễ.
      - **Lương giờ (`hourly_wage`):** Tính bằng `base_salary / standard_work_hours`.
      - **Phân loại giờ làm thực tế:** Duyệt qua từng bản ghi chấm công, phân loại giờ làm vào các nhóm:
          - `actual_worked_hours`: Giờ làm trong ngày làm việc bình thường.
          - `overtime_hours`: Giờ làm vượt quá giờ tiêu chuẩn trong ngày (sau khi trừ đi `overtime_tolerance`).
          - `public_leaves_worked_hours`: Giờ làm vào ngày nghỉ lễ.
  3.  **Xử lý Ngày nghỉ (không đi làm):**
      - Duyệt qua các ngày nghỉ phép đã duyệt nhưng không có chấm công.
      - Phân loại giờ nghỉ vào các nhóm:
          - `paid_leaves_hours`: Giờ nghỉ có lương.
          - `unpaid_leaves_hours`: Giờ nghỉ không lương.
  4.  **Xử lý Chính sách Đặc biệt:**
      - Áp dụng các chính sách (`policy_*`) từ Settings để xử lý các trường hợp phức tạp như "làm việc trong ngày nghỉ phép" (có tính là OT không, có trừ ngày phép không).
  5.  **Tính toán Lương gộp (trước thưởng/phạt):**
      - `base_pay`: `(actual_worked_hours + paid_leaves_hours)` * `hourly_wage`.
      - `overtime_pay`: `overtime_hours` * `hourly_wage` * `payroll_overtime_rate`.
      - `public_leaves_pay`: `public_leaves_worked_hours` * `hourly_wage` * `public_leaves_rate`.
      - `gross_salary_before_adjustments`: Tổng của `base_pay`, `overtime_pay`, `public_leaves_pay`, và `allowance`.
  6.  **Tính toán Thưởng và Khấu trừ:**
      - Duyệt qua các dòng `payroll.payslip.line` theo `sequence`.
      - Tính giá trị của mỗi dòng (`_calculate_amount`). Quy tắc theo `%` sẽ được tính trên lương gộp hiện tại (đã cộng các khoản thưởng trước đó).
      - Cộng dồn vào `total_bonus` và `total_deduction`.
  7.  **Tính Lương thực nhận (`net_salary`):**
      - `net_salary` = `gross_salary_before_adjustments` + `total_bonus` + `total_deduction`.

## 2. Quản lý Bảng lương (`payroll.payroll`)

Tính năng này giúp tối ưu hóa quy trình tính lương hàng tháng cho nhiều nhân viên.

- **Tạo và Chọn lọc:** Cho phép tạo một Bảng lương mới, chọn nhân viên theo danh sách (`employee`) hoặc theo phòng ban (`department`).
- **Dòng Mẫu (`payroll.payroll.line`):** Có thể thêm các quy tắc thưởng/khấu trừ chung cho cả Bảng lương (ví dụ: thưởng thâm niên). Khi tạo phiếu lương, các dòng này sẽ được tự động thêm vào từng phiếu lương cá nhân.
- **Hành động Hàng loạt:** Cung cấp các nút để thực hiện hành động cho tất cả phiếu lương trong Bảng lương:
  - `Generate Payslips`: Tạo các phiếu lương ở trạng thái `draft`.
  - `Compute All`: Chạy `action_compute_sheet` cho tất cả.
  - `Confirm All`: Chuyển tất cả sang trạng thái `done`.
  - `Export Excel`: Xuất báo cáo Excel cho các phiếu lương đã `done`.

## 3. Tích hợp Chấm công qua Systray

Cung cấp một tiện ích chấm công nhanh chóng và tiện lợi cho nhân viên.

- **Cơ chế:**
  - Một widget được thêm vào thanh hệ thống (systray) bằng JavaScript.
  - Trạng thái (`checked_in`/`checked_out`) được lấy từ backend thông qua phương thức `get_systray_info` của `hr.employee`.
- **Hành động:**
  - Khi nhân viên nhấn "Check In" / "Check Out", nó sẽ gọi phương thức `action_manual_attendance` trên `hr.employee`.
  - Backend sẽ tạo hoặc cập nhật bản ghi `payroll.attendance.record` tương ứng và trả về trạng thái mới để cập nhật giao diện.

## 4. Xử lý Đa tiền tệ và Xuất Excel

- **Đa tiền tệ:**
  - **Lưu trữ:** Mọi tính toán và lưu trữ giá trị tiền tệ trong backend (các trường `Monetary`) đều được thực hiện bằng một đơn vị tiền tệ cơ sở (mặc định là USD) để đảm bảo tính nhất quán.
  - **Hiển thị:** Giao diện người dùng hiển thị giá trị tiền tệ theo một loại tiền tệ có thể cấu hình trong Settings (`payroll_currency_id`). Hệ thống tự động chuyển đổi qua lại bằng phương thức `_convert` của Odoo.
- **Xuất Excel:**
  - Sử dụng một `Controller` (`/payroll/export/payslips`) để xử lý yêu cầu HTTP.
  - Dùng thư viện `xlsxwriter` để tạo file Excel trong bộ nhớ, định dạng header, và điền dữ liệu từ các phiếu lương đã được xác nhận.
  - Trả về file Excel cho người dùng tải xuống với tên file được tạo động.

## 5. Hệ thống Phân quyền

- **Hai cấp độ:** `User` (`group_payroll_user`) và `Manager` (`group_payroll_manager`).
- **Record Rules:**
  - **User:**
      - `payroll.attendance.record`: Chỉ có thể xem và quản lý (`create`/`write`) các bản ghi chấm công của chính mình.
      - `payroll.payslip`: Chỉ có thể xem phiếu lương của chính mình.
  - **Manager:** Có toàn quyền trên tất cả các model của module.
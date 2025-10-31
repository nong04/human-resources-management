# Hướng dẫn Sử dụng - Payroll & Attendance

Tài liệu này cung cấp hướng dẫn chi tiết về các quy trình nghiệp vụ chính trong module **Payroll & Attendance**, từ cấu hình, chấm công hàng ngày đến chạy lương hàng tháng.

## 1. Dành cho Quản trị viên & Quản lý Nhân sự (Cấu hình ban đầu)

Các bước này cần được thực hiện trước khi chạy kỳ lương đầu tiên.

### 1.1. Cấu hình Hệ thống
1.  **Truy cập:** Vào menu **Payroll -> Configuration -> Settings**.
2.  **Thiết lập các tham số:**
    - **Payroll Currency:** Chọn loại tiền tệ chính sẽ hiển thị trên tất cả giao diện.
    - **Overtime Tolerance:** Đặt số phút dung sai trước khi giờ làm được tính là làm thêm (OT).
    - **Overtime Rate:** Đặt hệ số nhân lương cho giờ làm thêm (ví dụ: 1.5 cho 150%).
    - **Leave Policies:** Cấu hình các chính sách xử lý khi nhân viên đi làm trong ngày nghỉ phép.
3.  **Lưu lại.**

![Giao diện Cấu hình Payroll](images/payroll_settings.png)

### 1.2. Định nghĩa Quy tắc Thưởng/Khấu trừ
1.  **Truy cập:** Vào menu **Payroll -> Configuration -> Bonus/Deduction Rules**.
2.  **Tạo mới:** Giao diện cho phép tạo và sửa trực tiếp trên danh sách.
3.  **Điền thông tin:**
    - **Name & Code:** Tên và mã quy tắc (ví dụ: "Thưởng KPI", "KPI_BONUS").
    - **Type:** Chọn `Bonus` (cộng vào lương) hoặc `Deduction` (trừ khỏi lương).
    - **Computation Method:** Chọn `Fixed Amount` hoặc `Percentage of Gross Salary`.
    - **Amount:** Điền số tiền hoặc tỷ lệ phần trăm tương ứng.
4.  **Lưu lại.**

![Danh sách Quy tắc Thưởng/Khấu trừ](images/payroll_bonus_deduction_rules.png)

### 1.3. Cập nhật Lương cho Nhân viên
1.  **Truy cập:** Vào menu **HR Management -> Employees**, mở hồ sơ nhân viên.
2.  **Vào tab Payroll:**
    - **Base Salary:** Nhập mức lương cơ bản hàng tháng.
    - **Allowance:** Nhập các khoản phụ cấp cố định hàng tháng.
3.  **Lưu lại.**

![Form Hồ sơ Nhân viên - Tab Payroll](images/hr_employee_payroll.png)

## 2. Dành cho tất cả Nhân viên (Hàng ngày)

### 2.1. Chấm công (Check-in / Check-out)
1.  **Sử dụng Systray:** Trên thanh công cụ trên cùng của Odoo, tìm biểu tượng chấm công (hình tròn).
    - **Màu đỏ:** Bạn đã `checked out`.
    - **Màu xanh:** Bạn đã `checked in`.
2.  **Thực hiện:**
    - Nhấn vào biểu tượng, sau đó chọn **Check In** khi bắt đầu làm việc.
    - Nhấn vào biểu tượng, sau đó chọn **Check Out** khi kết thúc làm việc.

![Widget Chấm công trên Systray](images/payroll_systray.png)

### 2.2. Xem Lịch sử Chấm công và Phiếu lương
- **Xem Chấm công:**
  1.  **Truy cập:** Vào menu **Payroll -> Attendances**.
  2.  Sử dụng bộ lọc **My Attendances** để xem các bản ghi chấm công của bạn.

![Danh sách Chấm công của Nhân viên](images/payroll_attendance_record.png)

- **Xem Phiếu lương:**
  1.  **Truy cập:** Vào menu **Payroll -> All Payslips**.
  2.  Sử dụng bộ lọc **My Payslips** để xem các phiếu lương của bạn đã được phòng nhân sự xác nhận.

![Danh sách Phiếu lương của Nhân viên](images/payroll_payslip.png)

## 3. Dành cho Quản lý Nhân sự (Hàng tháng)

Đây là quy trình chính để tính và trả lương cho nhân viên.

### 3.1. Tạo Bảng lương (`payroll.payroll`)
1.  **Truy cập:** Vào menu **Payroll -> Payrolls**.
2.  **Tạo mới:** Nhấn **New**.
3.  **Điền thông tin cơ bản:**
    - **Name:** Tên của Bảng lương (ví dụ: "Lương tháng 08/2025").
    - **Period:** Chọn ngày bắt đầu và kết thúc của kỳ lương.
4.  **Chọn Nhân viên:**
    - **Selection Mode:** Chọn `By Department` (để chọn cả phòng ban) hoặc `By Employee` (để chọn từng nhân viên).
    - Chọn các phòng ban hoặc nhân viên tương ứng.
5.  **(Tùy chọn) Thêm Thưởng/Phạt chung:** Vào tab **Bonuses & Deductions** để thêm các quy tắc sẽ áp dụng cho tất cả mọi người trong Bảng lương này.
6.  **Lưu lại.**

![Form tạo Bảng lương](images/payroll_payroll_form.png)

### 3.2. Xử lý và Hoàn tất Bảng lương
1.  **Tạo Phiếu lương:** Mở Bảng lương vừa tạo và nhấn nút **Generate Payslips**. Hệ thống sẽ tạo các phiếu lương con ở trạng thái `draft`.
2.  **(Tùy chọn) Điều chỉnh cá nhân:** Nhấn vào smart button **Payslips** để xem danh sách. Mở từng phiếu lương để thêm các khoản thưởng/phạt riêng cho từng người nếu cần.
3.  **Tính toán:** Quay lại form Bảng lương, nhấn **Compute All**. Hệ thống sẽ chạy logic tính lương cho tất cả các phiếu lương.
4.  **Xác nhận:** Sau khi đã kiểm tra, nhấn **Confirm All**. Tất cả phiếu lương sẽ chuyển sang trạng thái `done` và khóa lại.
5.  **Xuất Báo cáo:** Nhấn **Export Excel** để tải về file báo cáo lương của cả Bảng lương.

![Quy trình các nút trên Bảng lương](images/payroll_payroll_form2.png)

---

# User Guide - Payroll & Attendance

This document provides detailed instructions for the main business processes in the **Payroll & Attendance** module, from configuration and daily attendance to running monthly payroll.

## 1. For Administrators & HR Managers (Initial Setup)

These steps should be completed before running the first payroll period.

### 1.1. System Configuration
1.  **Navigate:** Go to the **Payroll -> Configuration -> Settings** menu.
2.  **Set Parameters:**
    - **Payroll Currency:** Choose the main currency that will be displayed on all payroll interfaces.
    - **Overtime Tolerance:** Set the grace period in minutes before work time is considered overtime (OT).
    - **Overtime Rate:** Set the salary multiplier for overtime hours (e.g., 1.5 for 150%).
    - **Leave Policies:** Configure policies for handling cases where an employee works on a leave day.
3.  **Save.**

![Payroll Configuration Interface](images/payroll_settings.png)

### 1.2. Define Bonus/Deduction Rules
1.  **Navigate:** Go to the **Payroll -> Configuration -> Bonus/Deduction Rules** menu.
2.  **Create New:** The interface allows for direct creation and editing in the list view.
3.  **Enter Information:**
    - **Name & Code:** Rule name and code (e.g., "KPI Bonus", "KPI_BONUS").
    - **Type:** Choose `Bonus` (adds to salary) or `Deduction` (subtracts from salary).
    - **Computation Method:** Choose `Fixed Amount` or `Percentage of Gross Salary`.
    - **Amount:** Enter the corresponding amount or percentage rate.
4.  **Save.**

![Bonus/Deduction Rules List](images/payroll_bonus_deduction_rules.png)

### 1.3. Update Employee Salary
1.  **Navigate:** Go to **HR Management -> Employees**, and open an employee's profile.
2.  **Go to the Payroll tab:**
    - **Base Salary:** Enter the basic monthly salary.
    - **Allowance:** Enter any fixed monthly allowances.
3.  **Save.**

![Employee Profile Form - Payroll Tab](images/hr_employee_payroll.png)

## 2. For All Employees (Daily)

### 2.1. Attendance (Check-in / Check-out)
1.  **Use the Systray:** On Odoo's top toolbar, find the attendance icon (a circle).
    - **Red:** You are `checked out`.
    - **Green:** You are `checked in`.
2.  **Perform Action:**
    - Click the icon, then select **Check In** when you start working.
    - Click the icon, then select **Check Out** when you finish working.

![Attendance Widget on Systray](images/payroll_systray.png)

### 2.2. View Attendance History and Payslips
- **View Attendance:**
  1.  **Navigate:** Go to the **Payroll -> Attendances** menu.
  2.  Use the **My Attendances** filter to see your attendance records.

![Employee's Attendance List](images/payroll_attendance_record.png)

- **View Payslips:**
  1.  **Navigate:** Go to the **Payroll -> All Payslips** menu.
  2.  Use the **My Payslips** filter to see your payslips that have been confirmed by the HR department.

![Employee's Payslip List](images/payroll_payslip.png)

## 3. For HR Managers (Monthly)

This is the main process for calculating and issuing employee salaries.

### 3.1. Create a Payroll (`payroll.payroll`)
1.  **Navigate:** Go to the **Payroll -> Payrolls** menu.
2.  **Create New:** Click **New**.
3.  **Enter Basic Information:**
    - **Name:** Name of the payroll run (e.g., "Salary for August 2025").
    - **Period:** Select the start and end dates of the pay period.
4.  **Select Employees:**
    - **Selection Mode:** Choose `By Department` (to select entire departments) or `By Employee` (to select individual employees).
    - Select the corresponding departments or employees.
5.  **(Optional) Add General Bonuses/Deductions:** Go to the **Bonuses & Deductions** tab to add rules that will apply to everyone in this payroll.
6.  **Save.**

![Create Payroll Form](images/payroll_payroll_form.png)

### 3.2. Process and Finalize the Payroll
1.  **Generate Payslips:** Open the newly created Payroll and click the **Generate Payslips** button. The system will create the child payslips in the `draft` state.
2.  **(Optional) Individual Adjustments:** Click the **Payslips** smart button to see the list. Open individual payslips to add specific bonuses or deductions for each person if needed.
3.  **Calculate:** Return to the Payroll form and click **Compute All**. The system will run the salary calculation logic for all payslips.
4.  **Confirm:** After reviewing, click **Confirm All**. All payslips will be moved to the `done` state and locked.
5.  **Export Report:** Click **Export Excel** to download the salary report file for the entire Payroll.

![Button Workflow on Payroll Form](images/payroll_payroll_form2.png)
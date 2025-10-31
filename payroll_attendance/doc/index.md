# Tài liệu Module Payroll & Attendance

## 1. Giới thiệu

**Payroll & Attendance** là một module toàn diện cho Odoo 17, được xây dựng để tích hợp liền mạch quy trình chấm công và tính lương cơ bản. Module này mở rộng các chức năng của **HR Management** và **Leave Management**, cho phép doanh nghiệp theo dõi giờ làm việc thực tế của nhân viên và tự động hóa việc tính toán lương hàng tháng.

### Mục tiêu chính:
- **Tích hợp Chấm công:** Cung cấp hệ thống ghi nhận thời gian vào-ra (`check-in`/`check-out`) và tự động tính toán giờ làm việc.
- **Tự động hóa Tính lương:** Xây dựng một quy trình tính lương mạnh mẽ, tự động tổng hợp giờ làm, giờ tăng ca, nghỉ phép, và các khoản thưởng/phạt để ra phiếu lương cuối cùng.
- **Quản lý theo Lô:** Cho phép tạo và xử lý phiếu lương cho hàng loạt nhân viên một cách hiệu quả thông qua các "Bảng lương".
- **Linh hoạt và Tùy chỉnh:** Cung cấp khả năng định nghĩa các quy tắc thưởng và khấu trừ (cố định hoặc theo phần trăm), cùng nhiều chính sách tính lương có thể cấu hình.
- **Báo cáo và Xuất dữ liệu:** Hỗ trợ xuất báo cáo lương ra file Excel theo định dạng chuyên nghiệp.
- **Hỗ trợ Đa tiền tệ:** Cho phép tính toán và lưu trữ bằng một loại tiền tệ cơ sở (USD) và hiển thị bằng một loại tiền tệ khác do người dùng lựa chọn.

### Tích hợp:
- Module này yêu cầu cài đặt và phụ thuộc vào **HR Management** và **HR Leaves** để sử dụng dữ liệu nhân viên, lịch làm việc, và thông tin nghỉ phép.

---

## 2. Cấu trúc Tài liệu

Để hiểu rõ hơn về module, vui lòng tham khảo các tài liệu chi tiết dưới đây:

- ### **[Mô hình Dữ liệu](./data_model.md)**
  > *Dành cho nhà phát triển và người quản trị hệ thống.*
  > 
  > Phân tích cấu trúc kỹ thuật của module, bao gồm sơ đồ lớp UML, mô tả các model (`payroll.payslip`, `payroll.attendance.record`, v.v.), hệ thống tiền tệ, mối quan hệ, và các ràng buộc logic.

- ### **[Hướng dẫn Sử dụng](./user_guide.md)**
  > *Dành cho người dùng cuối (Nhân viên, Kế toán lương, Quản lý).*
  > 
  > Hướng dẫn từng bước các quy trình nghiệp vụ chính:
  > - **Quy trình 1:** Cấu hình hệ thống (lương, quy tắc, chính sách).
  > - **Quy trình 2:** Nhân viên chấm công hàng ngày.
  > - **Quy trình 3:** Chạy lương hàng tháng.
  > - **Quy trình 4:** Xem và xuất phiếu lương.

- ### **[Chức năng Chi tiết](./features.md)**
  > *Dành cho người muốn hiểu sâu về logic hoạt động của module.*
  > 
  > Giải thích chi tiết về "cách thức hoạt động" của các tính năng cốt lõi:
  > - Logic tính toán lương chi tiết (`action_compute_sheet`).
  > - Cơ chế xử lý đa tiền tệ.
  > - Quy trình xử lý và tạo phiếu lương hàng loạt.
  > - Tích hợp widget chấm công trên thanh hệ thống (Systray).

---

## 3. Cài đặt và Phụ thuộc

- **Phiên bản Odoo:** 17.0
- **Các module phụ thuộc:**
  - `hr_management`: Cung cấp dữ liệu nhân viên và cơ cấu tổ chức.
  - `hr_leaves`: Cung cấp dữ liệu nghỉ phép để tính toán lương.
  - `mail`: Cung cấp tính năng chatter, activity và thông báo.

---

# Payroll & Attendance Module Documentation

## 1. Introduction

**Payroll & Attendance** is a comprehensive module for Odoo 17, built to seamlessly integrate attendance tracking and basic salary calculation processes. This module extends the functionalities of **HR Management** and **Leave Management**, enabling businesses to track employees' actual working hours and automate the monthly payroll calculation.

### Main Objectives:
- **Attendance Integration:** Provide a system for recording check-in/check-out times and automatically calculating worked hours.
- **Payroll Automation:** Build a robust payroll calculation process that automatically aggregates working hours, overtime, leaves, and bonuses/deductions to generate the final payslip.
- **Batch Management:** Allow for the efficient creation and processing of payslips for multiple employees through "Payrolls".
- **Flexibility and Customization:** Provide the ability to define bonus and deduction rules (fixed or percentage-based), along with various configurable payroll policies.
- **Reporting and Data Export:** Support exporting payroll reports to professionally formatted Excel files.
- **Multi-Currency Support:** Allow calculations and storage in a base currency (USD) while displaying in a different user-selected currency.

### Integration:
- This module requires the installation of and depends on **HR Management** and **HR Leaves** to use employee data, work schedules, and leave information.

---

## 2. Documentation Structure

To better understand the module, please refer to the detailed documents below:

- ### **[Data Model](./data_model.md)**
  > *For developers and system administrators.*
  > 
  > Analyzes the technical structure of the module, including a UML class diagram, descriptions of models (`payroll.payslip`, `payroll.attendance.record`, etc.), the currency system, relationships, and logical constraints.

- ### **[User Guide](./user_guide.md)**
  > *For end-users (Employees, Payroll Accountants, Managers).*
  > 
  > Provides step-by-step instructions for key business processes:
  > - **Process 1:** System configuration (salary, rules, policies).
  > - **Process 2:** Daily employee attendance.
  > - **Process 3:** Running monthly payroll.
  > - **Process 4:** Viewing and exporting payslips.

- ### **[Detailed Features](./features.md)**
  > *For those who want to understand the module's operational logic in depth.*
  > 
  > Explains in detail "how" the core features work:
  > - The detailed salary calculation logic (`action_compute_sheet`).
  > - The multi-currency handling mechanism.
  > - The batch processing and bulk payslip generation workflow.
  - Integration of the attendance widget in the system tray (Systray).

---

## 3. Installation and Dependencies

- **Odoo Version:** 17.0
- **Dependent Modules:**
  - `hr_management`: Provides employee data and organizational structure.
  - `hr_leaves`: Provides leave data for salary calculations.
  - `mail`: Provides chatter, activity, and notification features.
# Tài liệu Module Leave Management

## 1. Giới thiệu

**Leave Management** là một module mở rộng cho Odoo 17, được thiết kế để quản lý toàn diện quy trình nghỉ phép trong doanh nghiệp. Module hoạt động dựa trên nền tảng của module **HR Management**, cho phép nhân viên gửi yêu cầu nghỉ phép, quản lý cấp phép và phê duyệt các yêu cầu một cách có hệ thống.

### Mục tiêu chính:
- **Tự động hóa quy trình:** Cung cấp một luồng công việc (workflow) rõ ràng từ lúc tạo yêu cầu, gửi duyệt, đến khi phê duyệt hoặc từ chối, tích hợp với hệ thống thông báo (Activity) của Odoo.
- **Quản lý Số dư Phép:** Tự động tính toán và theo dõi số ngày phép còn lại của nhân viên đối với các loại phép yêu cầu cấp phát.
- **Tính toán Thông minh:** Tự động loại trừ ngày cuối tuần và ngày nghỉ lễ chung của công ty khi tính toán thời gian nghỉ, dựa trên lịch làm việc cá nhân của từng nhân viên.
- **Phân quyền Rõ ràng:** Đảm bảo nhân viên chỉ có thể xem và quản lý yêu cầu của mình, trong khi quản lý có thể xem xét yêu cầu của team.
- **Trực quan hóa Dữ liệu:** Cung cấp một lịch nghỉ tổng quan, hiển thị cả ngày nghỉ của nhân viên và ngày lễ chung của công ty.

### Tích hợp:
- Module này yêu cầu cài đặt và phụ thuộc hoàn toàn vào module **HR Management** để có thể hoạt động, sử dụng chung dữ liệu về nhân viên và cơ cấu tổ chức.

---

## 2. Cấu trúc Tài liệu

Để hiểu rõ hơn về module, vui lòng tham khảo các tài liệu chi tiết dưới đây:

- ### **[Mô hình Dữ liệu](./data_model.md)**
  > *Dành cho nhà phát triển và người quản trị hệ thống.*
  > 
  > Phân tích cấu trúc kỹ thuật của module, bao gồm các model (`hr.leaves.request`, `hr.leaves.allocation`, `hr.leaves.calendar` SQL View, v.v.), các trường dữ liệu, mối quan hệ, và các ràng buộc logic quan trọng.

- ### **[Hướng dẫn Sử dụng](./user_guide.md)**
  > *Dành cho người dùng cuối (Nhân viên, Quản lý).*
  > 
  > Hướng dẫn từng bước các quy trình nghiệp vụ chính:
  > - **Quy trình 1:** Cấu hình các loại nghỉ phép và ngày nghỉ lễ.
  > - **Quy trình 2:** Cấp phát (phân bổ) ngày nghỉ cho nhân viên.
  > - **Quy trình 3:** Nhân viên tạo và gửi yêu cầu nghỉ phép.
  > - **Quy trình 4:** Quản lý phê duyệt hoặc từ chối yêu cầu.
  > - **Quy trình 5:** Xem lịch nghỉ tổng quan của công ty và team.

- ### **[Chức năng Chi tiết](./features.md)**
  > *Dành cho người muốn hiểu sâu về logic hoạt động của module.*
  > 
  > Giải thích chi tiết về "cách thức hoạt động" của các tính năng cốt lõi:
  > - Hệ thống phân quyền và quy tắc truy cập dữ liệu (`Record Rules`).
  > - Logic tính toán thời gian nghỉ (loại trừ ngày nghỉ theo lịch làm việc).
  > - Cơ chế kiểm tra số dư phép và chống nghỉ trùng lặp.
  > - Tích hợp với hệ thống thông báo và hoạt động (Activity) của Odoo.

---

## 3. Cài đặt và Phụ thuộc

- **Phiên bản Odoo:** 17.0
- **Các module phụ thuộc:**
  - `hr_management`: Cung cấp dữ liệu nhân viên và cơ cấu tổ chức.
  - `mail`: Cung cấp tính năng chatter, activity và thông báo.

---

# Leave Management Module Documentation

## 1. Introduction

**Leave Management** is an extension module for Odoo 17, designed to comprehensively manage the leave process within a company. The module operates on the foundation of the **HR Management** module, allowing employees to submit leave requests, and managers to allocate and approve these requests systematically.

### Main Objectives:
- **Process Automation:** Provide a clear workflow from request creation, submission, to approval or refusal, integrated with Odoo's notification system (Activity).
- **Leave Balance Management:** Automatically calculate and track the remaining leave days for employees for leave types that require allocation.
- **Intelligent Calculation:** Automatically exclude weekends and company-wide public holidays when calculating leave duration, based on each employee's individual work schedule.
- **Clear Permissions:** Ensure employees can only view and manage their own requests, while managers can review their team's requests.
- **Data Visualization:** Provide an overview calendar that displays both employee leaves and company-wide public holidays.

### Integration:
- This module requires the **HR Management** module to be installed and is fully dependent on it for employee data and organizational structure.

---

## 2. Documentation Structure

To better understand the module, please refer to the detailed documents below:

- ### **[Data Model](./data_model.md)**
  > *For developers and system administrators.*
  > 
  > Analyzes the technical structure of the module, including models (`hr.leaves.request`, `hr.leaves.allocation`, `hr.leaves.calendar` SQL View, etc.), data fields, relationships, and important logical constraints.

- ### **[User Guide](./user_guide.md)**
  > *For end-users (Employees, Managers).*
  > 
  > Provides step-by-step instructions for key business processes:
  > - **Process 1:** Configuring leave types and public holidays.
  > - **Process 2:** Allocating leave days to employees.
  > - **Process 3:** Employee creates and submits a leave request.
  > - **Process 4:** Manager approves or refuses a request.
  > - **Process 5:** Viewing the company and team leave overview calendar.

- ### **[Detailed Features](./features.md)**
  > *For those who want to understand the module's operational logic in depth.*
  > 
  > Explains in detail "how" the core features work:
  > - The permission system and data access rules (`Record Rules`).
  > - The logic for calculating leave duration (excluding non-working days based on work schedules).
  > - The mechanism for checking leave balances and preventing overlapping leaves.
  > - Integration with Odoo's notification and activity system.

---

## 3. Installation and Dependencies

- **Odoo Version:** 17.0
- **Dependent Modules:**
  - `hr_management`: Provides employee data and organizational structure.
  - `mail`: Provides chatter, activity, and notification features.
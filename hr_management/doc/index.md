# Tài liệu Module HR Management

## 1. Giới thiệu

**HR Management** là một module nền tảng cho Odoo 17, được xây dựng với mục tiêu cung cấp một hệ thống quản lý nhân sự tập trung, linh hoạt và dễ mở rộng. Module này đóng vai trò là "trái tim" cho các hoạt động nhân sự, quản lý thông tin cốt lõi về nhân viên và cơ cấu tổ chức của doanh nghiệp.

### Mục tiêu chính:
- **Tập trung hóa Dữ liệu:** Lưu trữ toàn bộ hồ sơ nhân viên, từ thông tin liên lạc, vị trí công việc đến các thông tin cá nhân, tại một nơi duy nhất.
- **Xây dựng Sơ đồ Tổ chức:** Cho phép định nghĩa cấu trúc công ty một cách trực quan thông qua các Phòng ban (Departments) và Vị trí Công việc (Job Positions).
- **Phân quyền Linh hoạt:** Cung cấp một hệ thống phân quyền 2 cấp (User và Manager) rõ ràng, cùng với quy trình yêu cầu và phê duyệt quyền minh bạch.
- **Nền tảng Mở rộng:** Thiết kế để dễ dàng tích hợp và làm cơ sở cho các module nhân sự chuyên sâu khác như Quản lý Nghỉ phép, Chấm công, Bảng lương, Tuyển dụng.

### Đối tượng sử dụng:
- **Quản lý Nhân sự (HR Manager):** Quản lý toàn bộ thông tin, cấu hình hệ thống và phê duyệt các yêu cầu.
- **Nhân viên (Employee):** Tự xem và cập nhật thông tin cá nhân, xem thông tin công khai của đồng nghiệp.
- **Quản lý Trực tiếp (Line Manager):** Xem thông tin nhân viên trong team của mình.

---

## 2. Tài liệu Chi tiết

Để hiểu rõ hơn về module, vui lòng tham khảo các tài liệu chi tiết dưới đây:

- ### **[Mô hình Dữ liệu](./data_model.md)**
  > *Dành cho nhà phát triển và người quản trị hệ thống.*
  > 
  > Tài liệu này phân tích sâu về cấu trúc kỹ thuật của module. Nó mô tả chi tiết các model (`hr.employee`, `hr.department`, v.v.), các trường dữ liệu quan trọng, các mối quan hệ (Many2one, One2many), và các ràng buộc SQL. Đây là tài liệu cần thiết nếu bạn muốn tùy chỉnh hoặc phát triển các tính năng mở rộng dựa trên module này.

- ### **[Hướng dẫn Sử dụng](./user_guide.md)**
  > *Dành cho người dùng cuối (Nhân viên, Quản lý).*
  > 
  > Hướng dẫn từng bước các quy trình nghiệp vụ phổ biến nhất, bao gồm:
  > - **Quy trình 1:** Thêm mới và quản lý hồ sơ nhân viên.
  > - **Quy trình 2:** Thiết lập và điều chỉnh cơ cấu phòng ban, vị trí công việc.
  > - **Quy trình 3:** Gửi yêu cầu và phê duyệt nâng cấp quyền hạn.
  > 
  > Tài liệu này được trình bày dưới dạng các bước thực hiện cụ thể, giúp người dùng nhanh chóng làm quen và sử dụng thành thạo module.

- ### **[Chức năng Chi tiết](./features.md)**
  > *Dành cho người muốn hiểu sâu về logic hoạt động của module.*
  > 
  > Tài liệu này đi sâu vào "cách thức hoạt động" của các tính năng, giải thích các logic nghiệp vụ ẩn sau giao diện người dùng. Các chủ đề bao gồm:
  > - Hệ thống phân quyền chi tiết cho User và Manager.
  > - Cơ chế đồng bộ hóa dữ liệu tự động giữa Nhân viên và Người dùng (User).
  > - Các tính năng tự động hóa như tự tạo user.
  > - Danh sách các quy tắc và ràng buộc dữ liệu để đảm bảo tính toàn vẹn của hệ thống.

---

## 3. Cài đặt và Phụ thuộc

- **Phiên bản Odoo:** 17.0
- **Các module phụ thuộc:**
  - `base`: Module lõi của Odoo.
  - `mail`: Cung cấp tính năng chatter, activity và thông báo.
  - `resource`: Cung cấp model `resource.resource` để quản lý lịch làm việc.

---

# HR Management Module Documentation

## 1. Introduction

**HR Management** is a foundational module for Odoo 17, built to provide a centralized, flexible, and extensible human resources management system. This module acts as the "heart" of HR operations, managing core information about employees and the company's organizational structure.

### Main Objectives:
- **Data Centralization:** Store complete employee profiles, from contact information and job positions to personal details, in a single place.
- **Organizational Chart Building:** Allow for the intuitive definition of the company structure through Departments and Job Positions.
- **Flexible Permissions:** Provide a clear two-tier permission system (User and Manager), along with a transparent process for requesting and approving rights.
- **Extensible Foundation:** Designed for easy integration and to serve as a base for more specialized HR modules such as Leave Management, Attendance, Payroll, and Recruitment.

### Target Audience:
- **HR Manager:** Manages all information, configures the system, and approves requests.
- **Employee:** Views and updates their own personal information, and views public information of colleagues.
- **Line Manager:** Views information of employees in their team.

---

## 2. Detailed Documentation

To better understand the module, please refer to the detailed documents below:

- ### **[Data Model](./data_model.md)**
  > *For developers and system administrators.*
  > 
  > This document provides a deep dive into the technical structure of the module. It details the models (`hr.employee`, `hr.department`, etc.), important data fields, relationships (Many2one, One2many), and SQL constraints. This is essential documentation if you intend to customize or develop extensions based on this module.

- ### **[User Guide](./user_guide.md)**
  > *For end-users (Employees, Managers).*
  > 
  > Provides step-by-step instructions for the most common business processes, including:
  > - **Process 1:** Adding and managing employee profiles.
  > - **Process 2:** Setting up and adjusting the structure of departments and job positions.
  > - **Process 3:** Submitting and approving requests for permission upgrades.
  > 
  > This document is presented as a series of concrete steps to help users quickly familiarize themselves with and master the module.

- ### **[Detailed Features](./features.md)**
  > *For those who want to understand the module's operational logic in depth.*
  > 
  > This document delves into "how" the features work, explaining the business logic hidden behind the user interface. Topics include:
  > - The detailed permission system for Users and Managers.
  > - The automatic data synchronization mechanism between Employees and Users.
  > - Automation features like automatic user creation.
  > - A list of rules and data constraints to ensure system integrity.

---

## 3. Installation and Dependencies

- **Odoo Version:** 17.0
- **Dependent Modules:**
  - `base`: Odoo's core module.
  - `mail`: Provides chatter, activity, and notification features.
  - `resource`: Provides the `resource.resource` model for managing working schedules.
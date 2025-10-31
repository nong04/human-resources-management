# Hướng dẫn Sử dụng - HR Management

Tài liệu này cung cấp hướng dẫn chi tiết về các quy trình nghiệp vụ chính trong module **HR Management**. Các hướng dẫn được chia theo vai trò và chức năng để người dùng có thể dễ dàng tìm thấy thông tin cần thiết.

## 1. Dành cho tất cả Nhân viên

### 1.1. Xem Danh bạ Công ty

Tất cả nhân viên đều có thể xem thông tin cơ bản của đồng nghiệp để tiện liên lạc và phối hợp công việc.

1.  **Truy cập:** Vào menu **HR Management -> Employees**.
2.  **Tìm kiếm:** Sử dụng thanh tìm kiếm để tìm nhân viên theo tên, hoặc sử dụng bộ lọc bên trái để lọc theo Phòng ban.
3.  **Xem thông tin:** Nhấn vào một nhân viên để xem các thông tin công khai như Tên, Vị trí, Phòng ban, Email và Điện thoại công việc.

![Giao diện danh bạ nhân viên](images/employee_directory.png)

### 1.2. Cập nhật Hồ sơ Cá nhân ("My Profile")

Mỗi nhân viên có thể tự cập nhật các thông tin cá nhân của mình.

1.  **Truy cập:** Nhấn vào avatar của bạn ở góc trên bên phải màn hình, sau đó chọn **My Profile**.
2.  **Cập nhật:** Bạn có thể thay đổi các thông tin như:
    - Ảnh đại diện.
    - Thông tin liên lạc cá nhân (Địa chỉ, Email, Điện thoại).
    - Thông tin nhân khẩu học (Ngày sinh, Giới tính, Quốc tịch).
    - Thông tin học vấn.
3.  **Lưu lại:** Nhấn **Save** để hoàn tất.

![Giao diện My Profile](images/my_profile.png)

## 2. Dành cho Quản lý Nhân sự (HR Manager)

Quản lý Nhân sự có toàn quyền trên module để thực hiện các nghiệp vụ quản trị.

### 2.1. Quản lý Hồ sơ Nhân viên

#### a. Thêm một Nhân viên mới
1.  **Truy cập:** Vào menu **HR Management -> Employees**.
2.  **Tạo mới:** Nhấn nút **New**.
3.  **Nhập thông tin:**
    - **Thông tin bắt buộc:** *Employee Name*, *Work Email*, *Department*, *Job Position*.
    - **Thông tin quan trọng khác:** *Manager* (Quản lý trực tiếp), *Start Date*.
4.  **Liên kết User (Tab HR Settings):**
    - **Trường hợp 1 (Tự động):** Nếu tính năng "Auto-Create User" được bật trong Settings, chỉ cần điền *Work Email* và lưu lại, một tài khoản sẽ được tự động tạo và liên kết.
    - **Trường hợp 2 (Thủ công):** Nếu nhân viên đã có tài khoản Odoo, chọn tài khoản đó ở trường *User*.
5.  **Lưu lại:** Nhấn **Save**.

![Giao diện New](images/new_employee.png)

#### b. Chuyển trạng thái Nhân viên Nghỉ việc
1.  Mở hồ sơ của nhân viên cần cập nhật.
2.  Nhấn **Edit**.
3.  Tại tab **HR Settings**, thay đổi trường **Work Status** từ `Active` thành `Left`.
4.  Điền ngày nghỉ việc vào trường **End Date** (tab Work Information).
5.  Nhấn **Save**. Nhân viên sẽ được tự động archived (lưu trữ).

### 2.2. Quản lý Cơ cấu Tổ chức

#### a. Tạo và Cấu trúc Phòng ban
1.  **Truy cập:** Vào menu **HR Management -> Departments**.
2.  **Tạo mới:** Nhấn **New**.
3.  **Nhập thông tin:** Điền *Department Name*.
    - Để chuyển phòng sang dạng phòng ban con, hãy chọn phòng ban cha ở trường *Parent Department*.
4.  **Gán Trưởng phòng:** Chọn nhân viên tương ứng ở trường *Manager*.
5.  **Lưu lại.**
6.  **Xem nhân viên:** Từ form Phòng ban, nhấn vào smart button **Employees** để xem danh sách nhân viên thuộc phòng ban đó.

![Form quản lý phòng ban](images/department_form.png)

#### b. Tạo Vị trí Công việc
1.  **Truy cập:** Vào menu **HR Management -> Configuration -> Job Positions**.
2.  **Tạo mới:** Nhấn **New**.
3.  Điền **Job Position Name** và (tùy chọn) **Department**.
4.  **Lưu lại.**

### 2.3. Quy trình Phê duyệt Quyền Manager

Khi một nhân viên yêu cầu quyền Manager, Quản lý Nhân sự sẽ là người phê duyệt.

1.  **Nhận thông báo:** Hệ thống sẽ tạo một "Activity" (Hoạt động) trên biểu tượng đồng hồ, thông báo có yêu cầu mới.
2.  **Truy cập:** Vào menu **HR Management -> Access Requests**.
3.  **Xem xét:** Danh sách các yêu cầu đang ở trạng thái "To Approve" sẽ hiện ra.
4.  **Ra quyết định:**
    - Mở yêu cầu để xem chi tiết.
    - Nhấn **Approve** để đồng ý. Quyền Manager sẽ được tự động cấp cho người dùng.
    - Nhấn **Refuse** để từ chối.
    
![Giao diện duyệt yêu cầu cấp quyền](images/access_request.png)

## 3. Dành cho Quản trị viên Hệ thống (System Admin)

### 3.1. Cấu hình Module

Quản trị viên có thể tùy chỉnh một số hành vi mặc định của module.

1.  **Truy cập:** Vào menu **HR Management -> Configuration -> Settings**.
2.  **Tùy chọn:**
    - **Auto-Create User:** Tích vào ô này để kích hoạt tính năng tự động tạo tài khoản người dùng khi tạo nhân viên mới có email.
3.  **Lưu lại:** Nhấn **Save** để áp dụng cấu hình.

![Giao diện cấu hình module](images/hr_settings.png)

---

# User Guide - HR Management

This document provides detailed instructions for the main business processes in the **HR Management** module. The instructions are divided by role and function so users can easily find the information they need.

## 1. For All Employees

### 1.1. View Company Directory

All employees can view basic information of their colleagues for easy communication and collaboration.

1.  **Navigate:** Go to the **HR Management -> Employees** menu.
2.  **Search:** Use the search bar to find an employee by name, or use the filters on the left to filter by Department.
3.  **View Information:** Click on an employee to see public information such as Name, Job Position, Department, Work Email, and Work Phone.

![Employee directory interface](images/employee_directory.png)

### 1.2. Update Personal Profile ("My Profile")

Each employee can update their own personal information.

1.  **Navigate:** Click on your avatar in the top right corner of the screen, then select **My Profile**.
2.  **Update:** You can change information such as:
    - Profile picture.
    - Personal contact information (Address, Email, Phone).
    - Demographic information (Date of Birth, Gender, Nationality).
    - Education information.
3.  **Save:** Click **Save** to finish.

![My Profile interface](images/my_profile.png)

## 2. For HR Managers

HR Managers have full permissions on the module to perform administrative tasks.

### 2.1. Manage Employee Profiles

#### a. Add a New Employee
1.  **Navigate:** Go to the **HR Management -> Employees** menu.
2.  **Create:** Click the **New** button.
3.  **Enter Information:**
    - **Required Information:** *Employee Name*, *Work Email*, *Department*, *Job Position*.
    - **Other Important Information:** *Manager*, *Start Date*.
4.  **Link User (HR Settings Tab):**
    - **Case 1 (Automatic):** If the "Auto-Create User" feature is enabled in Settings, simply fill in the *Work Email* and save. A user account will be automatically created and linked.
    - **Case 2 (Manual):** If the employee already has an Odoo account, select it in the *User* field.
5.  **Save:** Click **Save**.

![New Employee Interface](images/new_employee.png)

#### b. Change Employee Status to "Left"
1.  Open the profile of the employee you need to update.
2.  Click **Edit**.
3.  In the **HR Settings** tab, change the **Work Status** field from `Active` to `Left`.
4.  Enter the departure date in the **End Date** field (Work Information tab).
5.  Click **Save**. The employee will be automatically archived.

### 2.2. Manage Organizational Structure

#### a. Create and Structure Departments
1.  **Navigate:** Go to the **HR Management -> Departments** menu.
2.  **Create:** Click **New**.
3.  **Enter Information:** Fill in the *Department Name*.
    - To make it a sub-department, select the parent department in the *Parent Department* field.
4.  **Assign Manager:** Select the corresponding employee in the *Manager* field.
5.  **Save.**
6.  **View Employees:** From the Department form, click the **Employees** smart button to see the list of employees in that department.

![Department management form](images/department_form.png)

#### b. Create Job Positions
1.  **Navigate:** Go to the **HR Management -> Configuration -> Job Positions** menu.
2.  **Create:** Click **New**.
3.  Fill in the **Job Position Name** and optionally the **Department**.
4.  **Save.**

### 2.3. Manager Rights Approval Process

When an employee requests Manager rights, the HR Manager is responsible for approval.

1.  **Get Notified:** The system will create an "Activity" on the clock icon, notifying you of a new request.
2.  **Navigate:** Go to the **HR Management -> Access Requests** menu.
3.  **Review:** A list of requests in the "To Approve" state will be displayed.
4.  **Make a Decision:**
    - Open the request to see the details.
    - Click **Approve** to agree. Manager rights will be automatically granted to the user.
    - Click **Refuse** to deny.
    
![Access request approval interface](images/access_request.png)

## 3. For System Administrators

### 3.1. Configure the Module

Administrators can customize some of the module's default behaviors.

1.  **Navigate:** Go to the **HR Management -> Configuration -> Settings** menu.
2.  **Option:**
    - **Auto-Create User:** Check this box to enable the feature that automatically creates a user account when a new employee with an email is created.
3.  **Save:** Click **Save** to apply the configuration.

![Module configuration interface](images/hr_settings.png)
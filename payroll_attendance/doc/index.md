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
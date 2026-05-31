# PHẦN MỀM QUẢN LÝ CỬA HÀNG BÁN THIẾT BỊ DI ĐỘNG

## Giới thiệu
Đây là đồ án môn Lập trình ứng dụng với Python, xây dựng phần mềm quản lý cửa hàng bán thiết bị di động bằng Python, PyQt6 và SQLite.

## Công nghệ sử dụng
- Python 3.13
- PyQt6
- SQLite3
- Pandas
- Matplotlib
- OpenCV (cv2)
- Pyzbar
- Google GenAI

## Chức năng chính

### Quản lý hệ thống
- Đăng nhập, đăng ký
- Phân quyền người dùng
- Quản lý hồ sơ cá nhân

### Quản lý sản phẩm
- Thêm sản phẩm
- Sửa sản phẩm
- Xóa sản phẩm
- Quản lý biến thể
- Quản lý IMEI

### Bán hàng
- Tìm kiếm khách hàng
- Quét IMEI
- Thêm vào giỏ hàng
- Thanh toán
- Xuất hóa đơn

### Khách hàng
- Quản lý thông tin khách hàng
- Lịch sử mua hàng
- Phân loại khách hàng VIP

### Bảo hành
- Tra cứu IMEI
- Tạo phiếu bảo hành
- Cập nhật trạng thái bảo hành

### Báo cáo
- Thống kê doanh thu
- Thống kê lợi nhuận
- Top sản phẩm bán chạy
- Top khách hàng

### AI hỗ trợ khách hàng
- Tư vấn sản phẩm
- Hỗ trợ tra cứu thông tin

## Kiến trúc hệ thống

Mô hình MVC (Model - View - Controller)

```text
View
 ↓
Controller
 ↓
Model
 ↓
SQLite Database
```

## Cấu trúc dự án

```text
LV_SHOP
│
├── app/
├── assets/
├── main.py
├── lvshop.db
└── requirements.txt
```

## Thành viên thực hiện

- Lương Văn Ngọc – 20231511
- Khuất Thị Biên Thùy – 20231564

## Giảng viên hướng dẫn

Ngô Thị Hoa

## Môn học

Lập trình ứng dụng với Python
Trường Đại học Công nghệ Đông Á

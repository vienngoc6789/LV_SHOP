import re
from PyQt6.QtWidgets import QMessageBox, QLineEdit

from app.models.user_model import UserModel


class AuthController:
    def __init__(self, main_window):
        self.main_window = main_window

        self.login_page = main_window.login_page
        self.register_page = main_window.register_page

        self.connect_events()

    def connect_events(self):
        self.login_page.btnLogin.clicked.connect(self.login)
        self.login_page.btnGoRegister.clicked.connect(self.show_register)
        self.login_page.btnForgotPassword.clicked.connect(self.show_contact_admin)
        self.register_page.btnRegister.clicked.connect(self.register)
        self.register_page.btnBackLogin.clicked.connect(self.show_login)

        if hasattr(self.login_page, "btnShowPassword"):
            self.login_page.btnShowPassword.clicked.connect(
                lambda: self.toggle_password(
                    self.login_page.txtPassword,
                    self.login_page.btnShowPassword
                )
            )

        if hasattr(self.register_page, "btnShowPassword"):
            self.register_page.btnShowPassword.clicked.connect(
                lambda: self.toggle_password(
                    self.register_page.txtPassword,
                    self.register_page.btnShowPassword
                )
            )

        if hasattr(self.register_page, "btnShowConfirmPassword"):
            self.register_page.btnShowConfirmPassword.clicked.connect(
                lambda: self.toggle_password(
                    self.register_page.txtConfirmPassword,
                    self.register_page.btnShowConfirmPassword
                )
            )

    def show_login(self):
        self.main_window.stack.setCurrentWidget(self.main_window.login_page)

    def show_contact_admin(self):
        QMessageBox.information(
            self.main_window,
            "Quên mật khẩu",
            "Vui lòng liên hệ admin để được cấp lại mật khẩu.\n\n"
            "Hotline: 0123 456 789\n"
            "Email: admin@lvshop.com"
        )
    def show_register(self):
        self.main_window.stack.setCurrentWidget(self.main_window.register_page)

    def toggle_password(self, line_edit, button):
        if line_edit.echoMode() == QLineEdit.EchoMode.Password:
            line_edit.setEchoMode(QLineEdit.EchoMode.Normal)
            button.setText("🙈")
        else:
            line_edit.setEchoMode(QLineEdit.EchoMode.Password)
            button.setText("👁")

    def login(self):
        try:
            username = self.login_page.txtUsername.text().strip()
            password = self.login_page.txtPassword.text().strip()

            if not username:
                QMessageBox.warning(self.main_window, "Lỗi", "Vui lòng nhập tài khoản")
                return

            if not password:
                QMessageBox.warning(self.main_window, "Lỗi", "Vui lòng nhập mật khẩu")
                return

            user = UserModel.check_login(username, password)

            if user:
                self.main_window.current_user = user

                role = str(user[4] or "").strip().lower()
                if role in ["customer", "khách hàng", "khach hang"]:
                    UserModel.ensure_customer_profile(user)

                if hasattr(self.main_window, "dashboard_controller"):
                    self.main_window.dashboard_controller.load_user_info(user)

                QMessageBox.information(self.main_window, "Thành công", "Đăng nhập thành công")
                self.main_window.stack.setCurrentWidget(self.main_window.dashboard_page)
            else:
                QMessageBox.warning(self.main_window, "Lỗi", "Sai tài khoản hoặc mật khẩu")

        except Exception as e:
            QMessageBox.critical(
                self.main_window,
                "Lỗi hệ thống",
                f"Lỗi khi đăng nhập:\n{e}"
            )

    def register(self):
        try:
            self._register()
        except Exception as e:
            QMessageBox.critical(
                self.main_window,
                "Lỗi hệ thống",
                f"Lỗi khi đăng ký:\n{e}"
            )

    def _register(self):
        full_name = self.register_page.txtFullName.text().strip()
        birth_date = self.register_page.dateBirth.date().toString("yyyy-MM-dd")
        phone = self.register_page.txtPhone.text().strip()
        email = self.register_page.txtEmail.text().strip()
        address = self.register_page.txtAddress.text().strip()
        username = self.register_page.txtUsername.text().strip()
        password = self.register_page.txtPassword.text().strip()
        confirm_password = self.register_page.txtConfirmPassword.text().strip()

        # Public registration must never decide staff/admin permissions.
        # Employee accounts are created from the Human Resources screen.
        role = "Khách hàng"

        gender = "Nam"
        if self.register_page.radioFemale.isChecked():
            gender = "Nữ"

        if not full_name:
            QMessageBox.warning(self.main_window, "Lỗi", "Vui lòng nhập họ và tên")
            return

        if not phone:
            QMessageBox.warning(self.main_window, "Lỗi", "Vui lòng nhập số điện thoại")
            return

        if not email:
            QMessageBox.warning(self.main_window, "Lỗi", "Vui lòng nhập Gmail")
            return

        if not self.is_valid_email(email):
            QMessageBox.warning(
                self.main_window,
                "Lỗi",
                "Gmail không hợp lệ. Email phải có dạng ví dụ: example@gmail.com"
            )
            return

        if not address:
            QMessageBox.warning(self.main_window, "Lỗi", "Vui lòng nhập địa chỉ")
            return

        if not username:
            QMessageBox.warning(self.main_window, "Lỗi", "Vui lòng nhập tài khoản")
            return

        password_error = self.validate_password(password)
        if password_error:
            QMessageBox.warning(self.main_window, "Lỗi mật khẩu", password_error)
            return

        if password != confirm_password:
            QMessageBox.warning(self.main_window, "Lỗi", "Mật khẩu xác nhận không khớp")
            return

        is_customer = role.strip().lower() in ["customer", "khách hàng", "khach hang"]
        employee_code = UserModel.generate_customer_code() if is_customer else UserModel.generate_employee_code()

        if hasattr(self.register_page, "txtEmployeeCode"):
            self.register_page.txtEmployeeCode.setText(employee_code)

        data = {
            "full_name": full_name,
            "birth_date": birth_date,
            "gender": gender,
            "role": role,
            "phone": phone,
            "email": email,
            "address": address,
            "username": username,
            "employee_code": employee_code,
            "password": password
        }

        UserModel.create_user(data)

        if is_customer:
            created_user = UserModel.check_login(username, password)
            UserModel.ensure_customer_profile(created_user)

        code_label = "Mã khách hàng" if is_customer else "Mã nhân viên"
        QMessageBox.information(
            self.main_window,
            "Thành công",
            f"Tạo tài khoản thành công!\n{code_label} của bạn là: {employee_code}"
        )

        self.clear_register_form()
        self.show_login()

    def is_valid_email(self, email):
        pattern = r"^[A-Za-z0-9._%+-]+@gmail\.com$"
        return re.match(pattern, email) is not None

    def validate_password(self, password):
        if not password:
            return "Vui lòng nhập mật khẩu"

        if len(password) < 8:
            return "Mật khẩu phải có ít nhất 8 ký tự"

        if not re.search(r"[A-Z]", password):
            return "Mật khẩu phải có ít nhất 1 chữ cái in hoa"

        if not re.search(r"[0-9]", password):
            return "Mật khẩu phải có ít nhất 1 chữ số"

        return None

    def clear_register_form(self):
        self.register_page.txtFullName.clear()
        self.register_page.txtPhone.clear()
        self.register_page.txtEmail.clear()
        self.register_page.txtAddress.clear()
        self.register_page.txtUsername.clear()
        self.register_page.txtPassword.clear()
        self.register_page.txtConfirmPassword.clear()

        if hasattr(self.register_page, "txtEmployeeCode"):
            self.register_page.txtEmployeeCode.setText("Tự động sau khi đăng ký")

        self.register_page.radioMale.setChecked(True)
        if hasattr(self.register_page, "cboRole"):
            self.register_page.cboRole.setCurrentText("Khách hàng")

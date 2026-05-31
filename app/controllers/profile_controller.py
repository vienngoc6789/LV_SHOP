import csv
from datetime import datetime

from PyQt6.QtWidgets import (
    QMessageBox,
    QTableWidgetItem,
    QAbstractItemView,
    QFileDialog,
    QApplication
)

from app.models.profile_model import ProfileModel


class ProfileController:
    def __init__(self, page, main_window=None, current_user=None):
        self.page = page
        self.main_window = main_window
        self.current_user = current_user
        self.current_user_id = None

        ProfileModel.ensure_schema()
        self.setup_ui()
        self.connect_events()
        self.refresh()

    def sync_current_user(self):
        if self.main_window and hasattr(self.main_window, "current_user"):
            self.current_user = self.main_window.current_user

        self.current_user_id = self.resolve_current_user_id()

    def resolve_current_user_id(self):
        user = self.current_user

        if isinstance(user, dict):
            return user.get("id") or user.get("user_id")

        if isinstance(user, int):
            return user

        if isinstance(user, (list, tuple)) and len(user) > 0:
            return user[0]

        return None

    def setup_ui(self):
        self.page.tableMyInvoices.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.page.tableMyInvoices.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )

        self.page.tableMyInvoices.setColumnWidth(0, 70)
        self.page.tableMyInvoices.setColumnWidth(1, 145)
        self.page.tableMyInvoices.setColumnWidth(2, 160)
        self.page.tableMyInvoices.setColumnWidth(3, 75)
        self.page.tableMyInvoices.setColumnWidth(4, 120)
        self.page.tableMyInvoices.horizontalHeader().setStretchLastSection(True)

    def connect_events(self):
        self.page.btnUpdateProfile.clicked.connect(self.update_profile)
        self.page.btnRefreshProfile.clicked.connect(self.refresh)

        self.page.btnChangePassword.clicked.connect(self.change_password)
        self.page.btnClearPassword.clicked.connect(self.clear_password_fields)

        self.page.btnExportMyInvoices.clicked.connect(self.export_my_invoices)
        self.page.btnLogoutProfile.clicked.connect(self.logout)

    def money(self, value):
        return f"{float(value or 0):,.0f} đ"

    def format_date_vn(self, value):
        if not value:
            return ""
        try:
            return datetime.strptime(str(value)[:19], "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M")
        except Exception:
            try:
                return datetime.strptime(str(value)[:10], "%Y-%m-%d").strftime("%d/%m/%Y")
            except Exception:
                return str(value)

    def clear_ui(self):
        self.page.lblProfileName.setText("---")
        self.page.lblProfileRole.setText("---")

        self.page.txtFullName.clear()
        self.page.txtUsername.clear()
        self.page.txtPhone.clear()
        self.page.txtEmail.clear()
        if hasattr(self.page, "txtAddress"):
            self.page.txtAddress.clear()
        self.page.txtRole.clear()

        self.page.lblAccountStatus.setText("---")

        self.page.lblMyInvoices.setText("0")
        self.page.lblMyRevenue.setText("0 đ")
        self.page.lblMyAov.setText("0 đ")
        self.page.lblTodayRevenueValue.setText("0 đ")
        self.page.lblMonthRevenueValue.setText("0 đ")
        self.page.lblTodayOrderValue.setText("0")
        self.page.lblMonthOrderValue.setText("0")

        self.page.tableMyInvoices.setRowCount(0)

    def refresh(self):
        self.sync_current_user()

        if not self.current_user_id:
            self.clear_ui()
            return

        self.load_profile()
        self.load_summary()
        self.load_my_invoices()

    def load_profile(self):
        user = ProfileModel.get_user_by_id(self.current_user_id)

        if not user:
            self.clear_ui()
            QMessageBox.warning(None, "Không tìm thấy", "Không tìm thấy thông tin tài khoản đang đăng nhập")
            return

        (
            user_id,
            full_name,
            username,
            phone,
            email,
            address,
            role,
            status,
            created_at
        ) = user

        self.page.lblProfileName.setText(full_name or username or "---")
        self.page.lblProfileRole.setText(role or "---")

        self.page.txtFullName.setText(full_name)
        self.page.txtUsername.setText(username)
        self.page.txtPhone.setText(phone)
        self.page.txtEmail.setText(email)
        if hasattr(self.page, "txtAddress"):
            self.page.txtAddress.setText(address)
        self.page.txtRole.setText(role)

        self.page.lblAccountStatus.setText(status)
        self.apply_role_layout(role)

    def apply_role_layout(self, role):
        role_text = (role or "").lower()
        is_customer = role_text in ["customer", "khách hàng", "khach hang"]

        for widget_name in ["summaryCard1", "summaryCard2", "summaryCard3", "salesPanel", "invoicePanel"]:
            if hasattr(self.page, widget_name):
                getattr(self.page, widget_name).setVisible(not is_customer)

        if hasattr(self.page, "summaryCard4"):
            self.page.summaryCard4.setVisible(not is_customer)

        if hasattr(self.page, "infoPanel"):
            if is_customer:
                self.page.infoPanel.setMinimumWidth(430)
                self.page.infoPanel.setMaximumWidth(620)
            else:
                self.page.infoPanel.setMinimumWidth(360)
                self.page.infoPanel.setMaximumWidth(400)

        if hasattr(self.page, "passwordPanel"):
            self.page.passwordPanel.setMaximumHeight(190 if is_customer else 160)

        if hasattr(self.page, "contentLayout"):
            self.page.contentLayout.setStretch(0, 1)
            self.page.contentLayout.setStretch(1, 1 if is_customer else 2)

    def load_summary(self):
        summary = ProfileModel.get_my_summary(self.current_user_id)

        self.page.lblMyInvoices.setText(str(summary["total_invoice"]))
        self.page.lblMyRevenue.setText(self.money(summary["total_revenue"]))
        self.page.lblMyAov.setText(self.money(summary["aov"]))

        self.page.lblTodayRevenueValue.setText(self.money(summary["today_revenue"]))
        self.page.lblMonthRevenueValue.setText(self.money(summary["month_revenue"]))
        self.page.lblTodayOrderValue.setText(str(summary["today_order"]))
        self.page.lblMonthOrderValue.setText(str(summary["month_order"]))

    def load_my_invoices(self):
        data = ProfileModel.get_my_recent_invoices(self.current_user_id, 30)

        self.page.tableMyInvoices.setRowCount(0)

        for row_data in data:
            row = self.page.tableMyInvoices.rowCount()
            self.page.tableMyInvoices.insertRow(row)

            for col, value in enumerate(row_data):
                display = value

                if col == 1:
                    display = self.format_date_vn(value)

                if col == 4:
                    display = self.money(value)

                if col == 5:
                    display = "Tiền mặt" if value == "cash" else "QR"

                self.page.tableMyInvoices.setItem(row, col, QTableWidgetItem(str(display)))

    def update_profile(self):
        self.sync_current_user()

        if not self.current_user_id:
            QMessageBox.warning(None, "Lỗi", "Chưa xác định được tài khoản đang đăng nhập")
            return

        full_name = self.page.txtFullName.text().strip()
        phone = self.page.txtPhone.text().strip()
        email = self.page.txtEmail.text().strip()
        address = self.page.txtAddress.text().strip() if hasattr(self.page, "txtAddress") else ""

        if not full_name:
            QMessageBox.warning(None, "Thiếu họ tên", "Vui lòng nhập họ tên")
            return

        ProfileModel.update_profile(
            self.current_user_id,
            full_name,
            phone,
            email,
            address
        )

        self.sync_updated_user(full_name, phone, email, address)

        QMessageBox.information(None, "Thành công", "Đã cập nhật thông tin cá nhân")
        self.refresh()

    def sync_updated_user(self, full_name, phone, email, address):
        if not self.main_window or not getattr(self.main_window, "current_user", None):
            return

        user = self.main_window.current_user
        if not isinstance(user, (list, tuple)) or len(user) < 11:
            return

        updated_user = list(user)
        updated_user[1] = full_name
        updated_user[5] = phone
        updated_user[6] = email
        updated_user[7] = address
        self.main_window.current_user = tuple(updated_user)

        if hasattr(self.main_window, "dashboard_page"):
            self.main_window.dashboard_page.lblUserName.setText(full_name)

    def change_password(self):
        self.sync_current_user()

        if not self.current_user_id:
            QMessageBox.warning(None, "Lỗi", "Chưa xác định được tài khoản đang đăng nhập")
            return

        old_password = self.page.txtOldPassword.text()
        new_password = self.page.txtNewPassword.text()
        confirm = self.page.txtConfirmPassword.text()

        if not old_password:
            QMessageBox.warning(None, "Thiếu mật khẩu cũ", "Vui lòng nhập mật khẩu hiện tại")
            return

        if not new_password:
            QMessageBox.warning(None, "Thiếu mật khẩu mới", "Vui lòng nhập mật khẩu mới")
            return

        if len(new_password) < 4:
            QMessageBox.warning(None, "Mật khẩu yếu", "Mật khẩu nên có ít nhất 4 ký tự")
            return

        if new_password != confirm:
            QMessageBox.warning(None, "Sai xác nhận", "Mật khẩu nhập lại không khớp")
            return

        if not ProfileModel.check_password(self.current_user_id, old_password):
            QMessageBox.warning(None, "Sai mật khẩu", "Mật khẩu hiện tại không đúng")
            return

        ProfileModel.change_password(self.current_user_id, new_password)

        QMessageBox.information(None, "Thành công", "Đã đổi mật khẩu")
        self.clear_password_fields()

    def clear_password_fields(self):
        self.page.txtOldPassword.clear()
        self.page.txtNewPassword.clear()
        self.page.txtConfirmPassword.clear()

    def export_my_invoices(self):
        self.sync_current_user()

        if not self.current_user_id:
            QMessageBox.warning(None, "Lỗi", "Chưa xác định được tài khoản đang đăng nhập")
            return

        data = ProfileModel.get_my_recent_invoices(self.current_user_id, 9999)

        if not data:
            QMessageBox.warning(None, "Không có dữ liệu", "Không có hóa đơn để xuất")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            None,
            "Xuất hóa đơn cá nhân",
            "hoa_don_cua_toi.csv",
            "CSV Files (*.csv)"
        )

        if not file_path:
            return

        if not file_path.lower().endswith(".csv"):
            file_path += ".csv"

        headers = [
            "Mã đơn",
            "Ngày bán",
            "Khách hàng",
            "Số máy",
            "Tổng tiền",
            "Thanh toán"
        ]

        with open(file_path, "w", newline="", encoding="utf-8-sig") as file:
            writer = csv.writer(file)
            writer.writerow(headers)

            for row in data:
                row = list(row)
                row[1] = self.format_date_vn(row[1])
                row[4] = self.money(row[4])
                row[5] = "Tiền mặt" if row[5] == "cash" else "QR"
                writer.writerow(row)

        QMessageBox.information(None, "Thành công", f"Đã xuất danh sách:\n{file_path}")

    def logout(self):
        confirm = QMessageBox.question(
            None,
            "Đăng xuất",
            "Bạn có chắc chắn muốn đăng xuất?"
        )

        if confirm != QMessageBox.StandardButton.Yes:
            return

        if self.main_window:
            self.main_window.current_user = None

        QApplication.quit()

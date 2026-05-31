import csv
from datetime import datetime

from PyQt6.QtWidgets import (
    QMessageBox,
    QTableWidgetItem,
    QAbstractItemView,
    QFileDialog
)
from PyQt6.QtGui import QColor

from app.models.human_model import HumanModel


class HumanController:
    def __init__(self, page):
        self.page = page
        self.selected_user_id = None
        self.users_cache = []

        HumanModel.ensure_schema()
        self.setup_ui()
        self.connect_events()
        self.refresh()

    def setup_ui(self):
        for table in [self.page.tableUsers, self.page.tablePerformance]:
            table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
            table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        self.page.tableUsers.setColumnWidth(0, 45)
        self.page.tableUsers.setColumnWidth(1, 145)
        self.page.tableUsers.setColumnWidth(2, 115)
        self.page.tableUsers.setColumnWidth(3, 105)
        self.page.tableUsers.setColumnWidth(4, 150)
        self.page.tableUsers.setColumnWidth(5, 85)
        self.page.tableUsers.setColumnWidth(6, 85)
        self.page.tableUsers.setColumnWidth(7, 65)
        self.page.tableUsers.setColumnWidth(8, 105)
        self.page.tableUsers.horizontalHeader().setStretchLastSection(True)

        self.page.tablePerformance.setColumnWidth(0, 45)
        self.page.tablePerformance.setColumnWidth(1, 170)
        self.page.tablePerformance.setColumnWidth(2, 75)
        self.page.tablePerformance.setColumnWidth(3, 120)
        self.page.tablePerformance.horizontalHeader().setStretchLastSection(True)

    def connect_events(self):
        self.page.btnAddUser.clicked.connect(self.add_user)
        self.page.btnUpdateUser.clicked.connect(self.update_user)
        self.page.btnDeleteUser.clicked.connect(self.delete_user)
        self.page.btnClearForm.clicked.connect(self.clear_form)

        self.page.btnResetPassword.clicked.connect(self.reset_password)
        self.page.btnToggleStatus.clicked.connect(self.toggle_status)
        self.page.btnGrantManager.clicked.connect(self.grant_manager)

        self.page.btnSearch.clicked.connect(self.apply_filters)
        self.page.btnClearFilter.clicked.connect(self.clear_filter)
        self.page.btnRefresh.clicked.connect(self.refresh)

        self.page.btnViewPerformance.clicked.connect(self.load_performance)
        self.page.btnExportHuman.clicked.connect(self.export_csv)

        self.page.txtSearch.textChanged.connect(self.apply_filters)
        self.page.cboFilterRole.currentIndexChanged.connect(self.apply_filters)
        self.page.cboFilterStatus.currentIndexChanged.connect(self.apply_filters)

        self.page.tableUsers.cellClicked.connect(self.select_user_row)

    def money(self, value):
        return f"{float(value or 0):,.0f} đ"

    def format_date_vn(self, value):
        if not value:
            return ""
        try:
            return datetime.strptime(str(value)[:10], "%Y-%m-%d").strftime("%d/%m/%Y")
        except Exception:
            return str(value)

    def refresh(self):
        self.users_cache = HumanModel.get_all_users()
        self.apply_filters()
        self.load_summary()
        self.load_performance()

    def load_summary(self):
        total, active, sale_users, selected_revenue = HumanModel.get_summary(self.selected_user_id)

        self.page.lblTotalUsers.setText(str(total))
        self.page.lblActiveUsers.setText(str(active))
        self.page.lblSaleUsers.setText(str(sale_users))
        self.page.lblSelectedRevenue.setText(self.money(selected_revenue))

    def apply_filters(self):
        keyword = self.page.txtSearch.text().strip().lower()
        role_filter = self.page.cboFilterRole.currentText()
        status_filter = self.page.cboFilterStatus.currentText()

        data = []

        for row in self.users_cache:
            text = " ".join(str(x).lower() for x in row)
            role = row[5]
            status = row[6]

            match_keyword = keyword in text
            match_role = role_filter == "Tất cả vai trò" or role == role_filter
            match_status = status_filter == "Tất cả trạng thái" or status == status_filter

            if match_keyword and match_role and match_status:
                data.append(row)

        self.render_users(data)

    def render_users(self, data):
        self.page.tableUsers.setRowCount(0)

        for row_data in data:
            row = self.page.tableUsers.rowCount()
            self.page.tableUsers.insertRow(row)

            for col, value in enumerate(row_data):
                display = value

                if col == 8:
                    display = self.money(value)

                if col == 9:
                    display = self.format_date_vn(value)

                item = QTableWidgetItem(str(display))

                if col == 5:
                    role = str(value).lower()
                    if role == "admin":
                        item.setForeground(QColor("#dc2626"))
                    elif role == "quản lý":
                        item.setForeground(QColor("#7c3aed"))
                    elif role == "sale":
                        item.setForeground(QColor("#2563eb"))

                if col == 6:
                    if value == "active":
                        item.setForeground(QColor("#16a34a"))
                    elif value == "inactive":
                        item.setForeground(QColor("#64748b"))
                    elif value == "locked":
                        item.setForeground(QColor("#dc2626"))

                self.page.tableUsers.setItem(row, col, item)

    def get_form_data(self):
        full_name = self.page.txtFullName.text().strip()
        username = self.page.txtUsername.text().strip()
        phone = self.page.txtPhone.text().strip()
        email = self.page.txtEmail.text().strip()
        role = self.page.cboRole.currentText()
        status = self.page.cboStatus.currentText()

        return full_name, username, phone, email, role, status

    def validate_form(self, require_password=False):
        full_name, username, phone, email, role, status = self.get_form_data()

        if not full_name:
            QMessageBox.warning(None, "Thiếu họ tên", "Vui lòng nhập họ tên nhân viên")
            return False

        if not username:
            QMessageBox.warning(None, "Thiếu username", "Vui lòng nhập tên đăng nhập")
            return False

        if require_password:
            password = self.page.txtPassword.text()
            confirm = self.page.txtConfirmPassword.text()

            if not password:
                QMessageBox.warning(None, "Thiếu mật khẩu", "Vui lòng nhập mật khẩu")
                return False

            if len(password) < 4:
                QMessageBox.warning(None, "Mật khẩu yếu", "Mật khẩu nên có ít nhất 4 ký tự")
                return False

            if password != confirm:
                QMessageBox.warning(None, "Sai xác nhận", "Mật khẩu nhập lại không khớp")
                return False

        return True

    def add_user(self):
        if not self.validate_form(require_password=True):
            return

        full_name, username, phone, email, role, status = self.get_form_data()
        password = self.page.txtPassword.text()

        try:
            HumanModel.add_user(full_name, username, password, phone, email, role, status)
            QMessageBox.information(None, "Thành công", "Đã thêm nhân sự")
            self.clear_form()
            self.refresh()
        except Exception as e:
            QMessageBox.warning(None, "Lỗi", f"Không thể thêm nhân sự:\n{e}")

    def update_user(self):
        if not self.selected_user_id:
            QMessageBox.warning(None, "Chưa chọn", "Vui lòng chọn nhân sự cần sửa")
            return

        if not self.validate_form(require_password=False):
            return

        full_name, username, phone, email, role, status = self.get_form_data()

        try:
            HumanModel.update_user(
                self.selected_user_id,
                full_name,
                username,
                phone,
                email,
                role,
                status
            )
            QMessageBox.information(None, "Thành công", "Đã cập nhật nhân sự")
            self.refresh()
        except Exception as e:
            QMessageBox.warning(None, "Lỗi", f"Không thể sửa nhân sự:\n{e}")

    def delete_user(self):
        if not self.selected_user_id:
            QMessageBox.warning(None, "Chưa chọn", "Vui lòng chọn nhân sự cần xóa")
            return

        confirm = QMessageBox.question(
            None,
            "Xác nhận xóa",
            "Bạn chắc chắn muốn xóa nhân sự này?"
        )

        if confirm != QMessageBox.StandardButton.Yes:
            return

        ok, msg = HumanModel.delete_user(self.selected_user_id)

        if ok:
            QMessageBox.information(None, "Thành công", msg)
            self.clear_form()
            self.refresh()
        else:
            QMessageBox.warning(None, "Không thể xóa", msg)

    def reset_password(self):
        if not self.selected_user_id:
            QMessageBox.warning(None, "Chưa chọn", "Vui lòng chọn nhân sự cần đổi mật khẩu")
            return

        password = self.page.txtPassword.text()
        confirm = self.page.txtConfirmPassword.text()

        if not password:
            QMessageBox.warning(None, "Thiếu mật khẩu", "Vui lòng nhập mật khẩu mới")
            return

        if len(password) < 4:
            QMessageBox.warning(None, "Mật khẩu yếu", "Mật khẩu nên có ít nhất 4 ký tự")
            return

        if password != confirm:
            QMessageBox.warning(None, "Sai xác nhận", "Mật khẩu nhập lại không khớp")
            return

        HumanModel.reset_password(self.selected_user_id, password)
        QMessageBox.information(None, "Thành công", "Đã đổi mật khẩu")
        self.page.txtPassword.clear()
        self.page.txtConfirmPassword.clear()

    def toggle_status(self):
        if not self.selected_user_id:
            QMessageBox.warning(None, "Chưa chọn", "Vui lòng chọn nhân sự cần bật/tắt")
            return

        HumanModel.toggle_status(self.selected_user_id)
        QMessageBox.information(None, "Thành công", "Đã đổi trạng thái tài khoản")
        self.refresh()

    def grant_manager(self):
        if not self.selected_user_id:
            QMessageBox.warning(None, "Chưa chọn", "Vui lòng chọn nhân sự cần gán quyền")
            return

        HumanModel.grant_manager(self.selected_user_id)
        QMessageBox.information(None, "Thành công", "Đã gán quyền quản lý")
        self.page.cboRole.setCurrentText("quản lý")
        self.refresh()

    def select_user_row(self, row, column):
        self.selected_user_id = int(self.page.tableUsers.item(row, 0).text())

        raw = None
        for item in self.users_cache:
            if item[0] == self.selected_user_id:
                raw = item
                break

        if not raw:
            return

        (
            user_id,
            full_name,
            username,
            phone,
            email,
            role,
            status,
            order_count,
            revenue,
            created_at
        ) = raw

        self.page.txtFullName.setText(full_name)
        self.page.txtUsername.setText(username)
        self.page.txtPhone.setText(phone)
        self.page.txtEmail.setText(email)
        self.page.cboRole.setCurrentText(role)
        self.page.cboStatus.setCurrentText(status)

        self.page.txtPassword.clear()
        self.page.txtConfirmPassword.clear()

        self.load_summary()

    def clear_form(self):
        self.selected_user_id = None

        self.page.txtFullName.clear()
        self.page.txtUsername.clear()
        self.page.txtPhone.clear()
        self.page.txtEmail.clear()
        self.page.txtPassword.clear()
        self.page.txtConfirmPassword.clear()

        self.page.cboRole.setCurrentText("nhân viên")
        self.page.cboStatus.setCurrentText("active")

        self.page.tableUsers.clearSelection()
        self.load_summary()

    def clear_filter(self):
        self.page.txtSearch.clear()
        self.page.cboFilterRole.setCurrentIndex(0)
        self.page.cboFilterStatus.setCurrentIndex(0)
        self.apply_filters()

    def load_performance(self):
        data = HumanModel.get_performance(10)
        self.page.tablePerformance.setRowCount(0)

        for index, row_data in enumerate(data, start=1):
            full_name, order_count, revenue, aov = row_data

            row = self.page.tablePerformance.rowCount()
            self.page.tablePerformance.insertRow(row)

            values = [
                index,
                full_name,
                order_count,
                self.money(revenue),
                self.money(aov)
            ]

            for col, value in enumerate(values):
                self.page.tablePerformance.setItem(row, col, QTableWidgetItem(str(value)))

    def export_csv(self):
        if not self.users_cache:
            QMessageBox.warning(None, "Không có dữ liệu", "Không có dữ liệu nhân sự để xuất")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            None,
            "Xuất danh sách nhân sự",
            "danh_sach_nhan_su.csv",
            "CSV Files (*.csv)"
        )

        if not file_path:
            return

        if not file_path.lower().endswith(".csv"):
            file_path += ".csv"

        headers = [
            "ID",
            "Họ tên",
            "Username",
            "SĐT",
            "Email",
            "Vai trò",
            "Trạng thái",
            "Số đơn",
            "Doanh số",
            "Ngày tạo"
        ]

        with open(file_path, "w", newline="", encoding="utf-8-sig") as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            for row in self.users_cache:
                writer.writerow(row)

        QMessageBox.information(None, "Thành công", f"Đã xuất danh sách:\n{file_path}")
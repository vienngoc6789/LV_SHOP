from PyQt6.QtWidgets import QTableWidgetItem, QMessageBox, QAbstractItemView
from PyQt6.QtGui import QColor

from app.models.customer_model import CustomerModel


class CustomerController:
    def __init__(self, page):
        self.page = page
        self.selected_customer_id = None
        self.customers_cache = []

        CustomerModel.ensure_schema()
        self.setup_tables()
        self.connect_events()
        self.refresh()

    def setup_tables(self):
        for table in [
            self.page.tableCustomers,
            self.page.tableInvoices,
            self.page.tableBoughtImeis
        ]:
            table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
            table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        self.page.tableCustomers.setColumnWidth(0, 50)
        self.page.tableCustomers.setColumnWidth(1, 150)
        self.page.tableCustomers.setColumnWidth(2, 110)
        self.page.tableCustomers.setColumnWidth(3, 150)
        self.page.tableCustomers.setColumnWidth(4, 180)
        self.page.tableCustomers.setColumnWidth(5, 80)
        self.page.tableCustomers.setColumnWidth(6, 70)
        self.page.tableCustomers.setColumnWidth(7, 120)
        self.page.tableCustomers.horizontalHeader().setStretchLastSection(True)

        self.page.tableInvoices.setColumnWidth(0, 70)
        self.page.tableInvoices.setColumnWidth(1, 140)
        self.page.tableInvoices.setColumnWidth(2, 110)
        self.page.tableInvoices.setColumnWidth(3, 90)
        self.page.tableInvoices.horizontalHeader().setStretchLastSection(True)

        self.page.tableBoughtImeis.setColumnWidth(0, 140)
        self.page.tableBoughtImeis.setColumnWidth(1, 160)
        self.page.tableBoughtImeis.setColumnWidth(2, 130)
        self.page.tableBoughtImeis.setColumnWidth(3, 90)
        self.page.tableBoughtImeis.horizontalHeader().setStretchLastSection(True)

    def connect_events(self):
        self.page.btnAddCustomer.clicked.connect(self.add_customer)
        self.page.btnUpdateCustomer.clicked.connect(self.update_customer)
        self.page.btnDeleteCustomer.clicked.connect(self.delete_customer)
        self.page.btnClearForm.clicked.connect(self.clear_form)
        self.page.btnRefresh.clicked.connect(self.refresh)
        self.page.btnSearchCustomer.clicked.connect(self.search_by_phone)
        self.page.btnVipCustomer.clicked.connect(self.mark_vip)

        self.page.txtSearch.textChanged.connect(self.apply_filters)
        self.page.cboFilterGroup.currentIndexChanged.connect(self.apply_filters)
        self.page.tableCustomers.cellClicked.connect(self.select_customer_row)

        self.page.btnViewInvoice.clicked.connect(self.view_invoice_notice)
        self.page.btnViewWarranty.clicked.connect(self.view_warranty_notice)
        self.page.btnExportCustomer.clicked.connect(self.export_notice)

    def money(self, value):
        return f"{float(value):,.0f} đ"

    def refresh(self):
        self.customers_cache = CustomerModel.get_all_customers()
        self.apply_filters()
        self.update_summary()

        if self.selected_customer_id:
            self.load_customer_details(self.selected_customer_id)

    def apply_filters(self):
        keyword = self.page.txtSearch.text().lower().strip()
        group_filter = self.page.cboFilterGroup.currentText()

        data = []

        for row in self.customers_cache:
            text = " ".join(str(x).lower() for x in row)
            group = row[5]

            match_keyword = keyword in text
            match_group = group_filter == "Tất cả" or group == group_filter

            if match_keyword and match_group:
                data.append(row)

        self.render_customers(data)

    def render_customers(self, data):
        self.page.tableCustomers.setRowCount(0)

        for row_data in data:
            row = self.page.tableCustomers.rowCount()
            self.page.tableCustomers.insertRow(row)

            for col, value in enumerate(row_data):
                display_value = value

                if col == 7:
                    display_value = self.money(value)

                item = QTableWidgetItem(str(display_value))

                if col == 5:
                    if value == "VIP":
                        item.setForeground(QColor("#7c3aed"))
                    elif value == "Blacklist":
                        item.setForeground(QColor("#dc2626"))
                    elif value == "Đại lý":
                        item.setForeground(QColor("#2563eb"))

                self.page.tableCustomers.setItem(row, col, item)

    def get_form_data(self):
        return (
            self.page.txtName.text().strip(),
            self.page.txtPhone.text().strip(),
            self.page.txtEmail.text().strip(),
            self.page.txtAddress.text().strip(),
            self.page.cboCustomerGroup.currentText(),
            self.page.txtNote.toPlainText().strip()
        )

    def validate_form(self):
        name, phone, email, address, group, note = self.get_form_data()

        if not phone:
            QMessageBox.warning(None, "Thiếu SĐT", "Vui lòng nhập số điện thoại khách hàng")
            return False

        if not name:
            QMessageBox.warning(None, "Thiếu tên", "Vui lòng nhập họ tên khách hàng")
            return False

        return True

    def add_customer(self):
        if not self.validate_form():
            return

        name, phone, email, address, group, note = self.get_form_data()

        try:
            CustomerModel.add_customer(name, phone, email, address, group, note)
            QMessageBox.information(None, "Thành công", "Đã thêm khách hàng")
            self.clear_form()
            self.refresh()
        except Exception as e:
            QMessageBox.warning(None, "Lỗi", f"Không thể thêm khách hàng:\n{e}")

    def update_customer(self):
        if not self.selected_customer_id:
            QMessageBox.warning(None, "Chưa chọn", "Vui lòng chọn khách hàng cần sửa")
            return

        if not self.validate_form():
            return

        name, phone, email, address, group, note = self.get_form_data()

        try:
            CustomerModel.update_customer(
                self.selected_customer_id,
                name,
                phone,
                email,
                address,
                group,
                note
            )
            QMessageBox.information(None, "Thành công", "Đã cập nhật khách hàng")
            self.refresh()
        except Exception as e:
            QMessageBox.warning(None, "Lỗi", f"Không thể sửa khách hàng:\n{e}")

    def delete_customer(self):
        if not self.selected_customer_id:
            QMessageBox.warning(None, "Chưa chọn", "Vui lòng chọn khách hàng cần xóa")
            return

        confirm = QMessageBox.question(
            None,
            "Xác nhận",
            "Chỉ xóa được khách chưa có hóa đơn. Bạn muốn xóa?"
        )

        if confirm != QMessageBox.StandardButton.Yes:
            return

        ok = CustomerModel.delete_customer(self.selected_customer_id)

        if not ok:
            QMessageBox.warning(
                None,
                "Không thể xóa",
                "Khách hàng đã có hóa đơn, không nên xóa. Có thể chuyển nhóm Blacklist nếu cần."
            )
            return

        QMessageBox.information(None, "Thành công", "Đã xóa khách hàng")
        self.clear_form()
        self.refresh()

    def search_by_phone(self):
        phone = self.page.txtPhone.text().strip()

        if not phone:
            QMessageBox.warning(None, "Thiếu SĐT", "Vui lòng nhập số điện thoại cần tìm")
            return

        customer = CustomerModel.get_customer_by_phone(phone)

        if not customer:
            QMessageBox.information(None, "Không tìm thấy", "Không tìm thấy khách hàng")
            return

        self.fill_form_from_customer(customer)
        self.selected_customer_id = customer[0]
        self.load_customer_details(self.selected_customer_id)
        self.update_summary()

    def select_customer_row(self, row, column):
        customer_id = int(self.page.tableCustomers.item(row, 0).text())
        phone = self.page.tableCustomers.item(row, 2).text()

        customer = CustomerModel.get_customer_by_phone(phone)

        if customer:
            self.selected_customer_id = customer_id
            self.fill_form_from_customer(customer)
            self.load_customer_details(customer_id)
            self.update_summary()

    def fill_form_from_customer(self, customer):
        customer_id, name, phone, email, address, group, note, created_at = customer

        self.page.txtName.setText(name or "")
        self.page.txtPhone.setText(phone or "")
        self.page.txtEmail.setText(email or "")
        self.page.txtAddress.setText(address or "")
        self.page.cboCustomerGroup.setCurrentText(group or "Thường")
        self.page.txtNote.setPlainText(note or "")

    def load_customer_details(self, customer_id):
        self.load_invoices(customer_id)
        self.load_bought_imeis(customer_id)

    def load_invoices(self, customer_id):
        data = CustomerModel.get_customer_invoices(customer_id)

        self.page.tableInvoices.setRowCount(0)

        for row_data in data:
            row = self.page.tableInvoices.rowCount()
            self.page.tableInvoices.insertRow(row)

            for col, value in enumerate(row_data):
                display_value = value

                if col == 2:
                    display_value = self.money(value)

                if col == 3:
                    display_value = "Tiền mặt" if value == "cash" else "QR"

                self.page.tableInvoices.setItem(row, col, QTableWidgetItem(str(display_value)))

    def load_bought_imeis(self, customer_id):
        data = CustomerModel.get_customer_bought_imeis(customer_id)

        self.page.tableBoughtImeis.setRowCount(0)

        for row_data in data:
            row = self.page.tableBoughtImeis.rowCount()
            self.page.tableBoughtImeis.insertRow(row)

            for col, value in enumerate(row_data):
                self.page.tableBoughtImeis.setItem(row, col, QTableWidgetItem(str(value)))

    def update_summary(self):
        customer_id = self.selected_customer_id or 0
        total_customers, vip_customers, selected_spent = CustomerModel.get_customer_summary(customer_id)

        self.page.lblTotalCustomers.setText(str(total_customers))
        self.page.lblVipCustomers.setText(str(vip_customers))
        self.page.lblSelectedCustomerSpent.setText(self.money(selected_spent))

    def mark_vip(self):
        if not self.selected_customer_id:
            QMessageBox.warning(None, "Chưa chọn", "Vui lòng chọn khách hàng")
            return

        CustomerModel.mark_vip(self.selected_customer_id)
        self.page.cboCustomerGroup.setCurrentText("VIP")
        QMessageBox.information(None, "Thành công", "Đã đánh dấu khách VIP")
        self.refresh()

    def clear_form(self):
        self.selected_customer_id = None

        self.page.txtName.clear()
        self.page.txtPhone.clear()
        self.page.txtEmail.clear()
        self.page.txtAddress.clear()
        self.page.txtNote.clear()
        self.page.cboCustomerGroup.setCurrentIndex(0)

        self.page.tableInvoices.setRowCount(0)
        self.page.tableBoughtImeis.setRowCount(0)
        self.page.tableCustomers.clearSelection()

        self.update_summary()

    def view_invoice_notice(self):
        QMessageBox.information(
            None,
            "Thông báo",
            "Chức năng mở chi tiết hóa đơn sẽ gắn với màn Invoice ở bước sau."
        )

    def view_warranty_notice(self):
        QMessageBox.information(
            None,
            "Thông báo",
            "Chức năng xem bảo hành sẽ gắn với màn Warranty ở bước sau."
        )

    def export_notice(self):
        QMessageBox.information(
            None,
            "Thông báo",
            "Chức năng xuất Excel/PDF danh sách khách hàng sẽ làm sau."
        )
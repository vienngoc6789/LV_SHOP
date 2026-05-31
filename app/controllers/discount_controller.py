import csv
from datetime import datetime

from PyQt6.QtWidgets import (
    QMessageBox,
    QTableWidgetItem,
    QAbstractItemView,
    QFileDialog
)
from PyQt6.QtCore import QDate
from PyQt6.QtGui import QColor

from app.models.discount_model import DiscountModel


class DiscountController:
    def __init__(self, page):
        self.page = page
        self.selected_id = None
        self.discounts_cache = []

        DiscountModel.ensure_schema()
        self.setup_ui()
        self.connect_events()
        self.refresh()

    def setup_ui(self):
        for table in [self.page.tableDiscount, self.page.tableUsageStats]:
            table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
            table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        self.page.tableDiscount.setColumnWidth(0, 45)
        self.page.tableDiscount.setColumnWidth(1, 95)
        self.page.tableDiscount.setColumnWidth(2, 75)
        self.page.tableDiscount.setColumnWidth(3, 80)
        self.page.tableDiscount.setColumnWidth(4, 105)
        self.page.tableDiscount.setColumnWidth(5, 105)
        self.page.tableDiscount.setColumnWidth(6, 75)
        self.page.tableDiscount.setColumnWidth(7, 90)
        self.page.tableDiscount.setColumnWidth(8, 80)
        self.page.tableDiscount.setColumnWidth(9, 90)
        self.page.tableDiscount.setColumnWidth(10, 90)
        self.page.tableDiscount.setColumnWidth(11, 85)
        self.page.tableDiscount.horizontalHeader().setStretchLastSection(True)

        self.page.tableUsageStats.setColumnWidth(0, 55)
        self.page.tableUsageStats.setColumnWidth(1, 120)
        self.page.tableUsageStats.setColumnWidth(2, 100)
        self.page.tableUsageStats.setColumnWidth(3, 120)
        self.page.tableUsageStats.horizontalHeader().setStretchLastSection(True)

        today = QDate.currentDate()
        self.page.dateStart.setDate(today)
        self.page.dateEnd.setDate(today.addMonths(1))

    def connect_events(self):
        self.page.btnAddDiscount.clicked.connect(self.add_discount)
        self.page.btnUpdateDiscount.clicked.connect(self.update_discount)
        self.page.btnDeleteDiscount.clicked.connect(self.delete_discount)
        self.page.btnClearForm.clicked.connect(self.clear_form)

        self.page.btnSearch.clicked.connect(self.apply_filters)
        self.page.btnClearFilter.clicked.connect(self.clear_filter)
        self.page.btnRefresh.clicked.connect(self.refresh)

        self.page.btnToggleStatus.clicked.connect(self.toggle_status)
        self.page.btnDuplicateDiscount.clicked.connect(self.duplicate_discount)
        self.page.btnViewUsage.clicked.connect(self.load_usage_stats)
        self.page.btnExportDiscount.clicked.connect(self.export_csv)

        self.page.btnCheckCode.clicked.connect(self.check_code)

        self.page.tableDiscount.cellClicked.connect(self.select_row)

        self.page.txtSearch.textChanged.connect(self.apply_filters)
        self.page.cboFilterStatus.currentIndexChanged.connect(self.apply_filters)
        self.page.cboFilterType.currentIndexChanged.connect(self.apply_filters)

        self.page.txtCode.textChanged.connect(self.update_preview)
        self.page.cboDiscountType.currentIndexChanged.connect(self.update_preview)
        self.page.spinDiscountValue.valueChanged.connect(self.update_preview)
        self.page.spinMaxDiscount.valueChanged.connect(self.update_preview)
        self.page.spinMinOrder.valueChanged.connect(self.update_preview)
        self.page.spinUsageLimit.valueChanged.connect(self.update_preview)
        self.page.spinPerCustomerLimit.valueChanged.connect(self.update_preview)
        self.page.dateStart.dateChanged.connect(self.update_preview)
        self.page.dateEnd.dateChanged.connect(self.update_preview)
        self.page.cboStatus.currentIndexChanged.connect(self.update_preview)

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
        self.discounts_cache = DiscountModel.get_all()
        self.apply_filters()
        self.load_summary()
        self.load_usage_stats()
        self.update_preview()

    def load_usage_stats(self):
        data = DiscountModel.get_usage_stats(10)

        self.page.tableUsageStats.setRowCount(0)

        if not data:
            QMessageBox.information(None, "Thống kê sử dụng", "Chưa có mã giảm giá nào được sử dụng.")
            return

        message = "TOP MÃ GIẢM GIÁ DÙNG NHIỀU\n\n"

        for index, row_data in enumerate(data, start=1):
            row = self.page.tableUsageStats.rowCount()
            self.page.tableUsageStats.insertRow(row)

            code, used_count, total_discount_amount, revenue_applied = row_data
            values = [
                index,
                code,
                used_count,
                self.money(total_discount_amount),
                self.money(revenue_applied)
            ]

            message += (
                f"{index}. {code} - {used_count} lượt | "
                f"Đã giảm {self.money(total_discount_amount)} | "
                f"Doanh thu {self.money(revenue_applied)}\n"
            )

            for col, value in enumerate(values):
                self.page.tableUsageStats.setItem(row, col, QTableWidgetItem(str(value)))

        QMessageBox.information(None, "Thống kê sử dụng", message)

    def load_summary(self):
        total, active, expired, used = DiscountModel.get_summary()

        self.page.lblTotalDiscount.setText(str(total))
        self.page.lblActiveDiscount.setText(str(active))
        self.page.lblExpiredDiscount.setText(str(expired))
        self.page.lblTotalDiscountUsed.setText(str(used))

    def apply_filters(self):
        keyword = self.page.txtSearch.text().strip().lower()
        status_filter = self.page.cboFilterStatus.currentText()
        type_filter = self.page.cboFilterType.currentText()

        data = []

        for row in self.discounts_cache:
            text = " ".join(str(x).lower() for x in row)
            dtype = row[2]
            status = row[11]

            match_keyword = keyword in text
            match_status = status_filter == "Tất cả" or status == status_filter
            match_type = type_filter == "Tất cả loại" or dtype == type_filter

            if match_keyword and match_status and match_type:
                data.append(row)

        self.render_table(data)

    def render_table(self, data):
        self.page.tableDiscount.setRowCount(0)

        for row_data in data:
            row = self.page.tableDiscount.rowCount()
            self.page.tableDiscount.insertRow(row)

            for col, value in enumerate(row_data):
                display = value

                if col in [4, 5, 12]:
                    display = self.money(value)
                elif col in [9, 10]:
                    display = self.format_date_vn(value)
                elif col == 3:
                    if row_data[2] == "percent":
                        display = f"{float(value):.0f}%"
                    else:
                        display = self.money(value)

                item = QTableWidgetItem(str(display))

                if col == 11:
                    if value == "active":
                        item.setForeground(QColor("#16a34a"))
                    elif value == "inactive":
                        item.setForeground(QColor("#64748b"))
                    elif value == "expired":
                        item.setForeground(QColor("#dc2626"))

                self.page.tableDiscount.setItem(row, col, item)

    def get_form_data(self):
        code = self.page.txtCode.text().strip().upper()
        dtype = self.page.cboDiscountType.currentText()
        value = self.page.spinDiscountValue.value()
        max_discount = self.page.spinMaxDiscount.value()
        min_order = self.page.spinMinOrder.value()
        usage_limit = self.page.spinUsageLimit.value()
        per_customer_limit = self.page.spinPerCustomerLimit.value()
        start_date = self.page.dateStart.date().toString("yyyy-MM-dd")
        end_date = self.page.dateEnd.date().toString("yyyy-MM-dd")
        status = self.page.cboStatus.currentText()

        return (
            code,
            dtype,
            value,
            max_discount,
            min_order,
            usage_limit,
            per_customer_limit,
            start_date,
            end_date,
            status
        )

    def validate_form(self):
        code, dtype, value, max_discount, min_order, usage_limit, per_customer_limit, start_date, end_date, status = self.get_form_data()

        if not code:
            QMessageBox.warning(None, "Thiếu mã", "Vui lòng nhập mã giảm giá")
            return False

        if value <= 0:
            QMessageBox.warning(None, "Sai giá trị", "Giá trị giảm phải lớn hơn 0")
            return False

        if dtype == "percent" and value > 100:
            QMessageBox.warning(None, "Sai phần trăm", "Mã giảm theo % không được vượt quá 100%")
            return False

        if self.page.dateEnd.date() < self.page.dateStart.date():
            QMessageBox.warning(None, "Sai ngày", "Ngày kết thúc không được nhỏ hơn ngày bắt đầu")
            return False

        return True

    def add_discount(self):
        if not self.validate_form():
            return

        try:
            DiscountModel.add(self.get_form_data())
            QMessageBox.information(None, "Thành công", "Đã thêm mã giảm giá")
            self.clear_form()
            self.refresh()
        except Exception as e:
            QMessageBox.warning(None, "Lỗi", f"Không thể thêm mã:\n{e}")

    def update_discount(self):
        if not self.selected_id:
            QMessageBox.warning(None, "Chưa chọn", "Vui lòng chọn mã cần sửa")
            return

        if not self.validate_form():
            return

        try:
            DiscountModel.update(self.selected_id, self.get_form_data())
            QMessageBox.information(None, "Thành công", "Đã cập nhật mã giảm giá")
            self.refresh()
        except Exception as e:
            QMessageBox.warning(None, "Lỗi", f"Không thể sửa mã:\n{e}")

    def delete_discount(self):
        if not self.selected_id:
            QMessageBox.warning(None, "Chưa chọn", "Vui lòng chọn mã cần xóa")
            return

        confirm = QMessageBox.question(
            None,
            "Xác nhận xóa",
            "Bạn chắc chắn muốn xóa mã giảm giá này?"
        )

        if confirm != QMessageBox.StandardButton.Yes:
            return

        DiscountModel.delete(self.selected_id)
        QMessageBox.information(None, "Thành công", "Đã xóa mã giảm giá")
        self.clear_form()
        self.refresh()

    def select_row(self, row, column):
        table = self.page.tableDiscount
        self.selected_id = int(table.item(row, 0).text())

        raw = None
        for item in self.discounts_cache:
            if item[0] == self.selected_id:
                raw = item
                break

        if not raw:
            return

        (
            discount_id,
            code,
            dtype,
            value,
            max_discount,
            min_order,
            used_count,
            usage_limit,
            per_customer_limit,
            start_date,
            end_date,
            status,
            revenue_applied
        ) = raw

        self.page.txtCode.setText(code or "")
        self.page.cboDiscountType.setCurrentText(dtype or "percent")
        self.page.spinDiscountValue.setValue(float(value or 0))
        self.page.spinMaxDiscount.setValue(float(max_discount or 0))
        self.page.spinMinOrder.setValue(float(min_order or 0))
        self.page.spinUsageLimit.setValue(int(usage_limit or 0))
        self.page.spinPerCustomerLimit.setValue(int(per_customer_limit or 1))
        self.page.cboStatus.setCurrentText(status or "active")

        if start_date:
            self.page.dateStart.setDate(QDate.fromString(start_date[:10], "yyyy-MM-dd"))

        if end_date:
            self.page.dateEnd.setDate(QDate.fromString(end_date[:10], "yyyy-MM-dd"))

        self.update_preview()

    def clear_form(self):
        self.selected_id = None
        self.page.txtCode.clear()
        self.page.cboDiscountType.setCurrentText("percent")
        self.page.spinDiscountValue.setValue(0)
        self.page.spinMaxDiscount.setValue(0)
        self.page.spinMinOrder.setValue(0)
        self.page.spinUsageLimit.setValue(100)
        self.page.spinPerCustomerLimit.setValue(1)
        self.page.dateStart.setDate(QDate.currentDate())
        self.page.dateEnd.setDate(QDate.currentDate().addMonths(1))
        self.page.cboStatus.setCurrentText("active")
        self.page.tableDiscount.clearSelection()
        self.update_preview()

    def clear_filter(self):
        self.page.txtSearch.clear()
        self.page.cboFilterStatus.setCurrentIndex(0)
        self.page.cboFilterType.setCurrentIndex(0)
        self.apply_filters()

    def toggle_status(self):
        if not self.selected_id:
            QMessageBox.warning(None, "Chưa chọn", "Vui lòng chọn mã cần bật/tắt")
            return

        DiscountModel.toggle_status(self.selected_id)
        QMessageBox.information(None, "Thành công", "Đã đổi trạng thái mã")
        self.refresh()

    def duplicate_discount(self):
        if not self.selected_id:
            QMessageBox.warning(None, "Chưa chọn", "Vui lòng chọn mã cần nhân bản")
            return

        try:
            DiscountModel.duplicate(self.selected_id)
            QMessageBox.information(None, "Thành công", "Đã nhân bản mã giảm giá")
            self.refresh()
        except Exception as e:
            QMessageBox.warning(None, "Lỗi", f"Không thể nhân bản mã:\n{e}")

    def check_code(self):
        code = self.page.txtTestCode.text().strip()
        order_total = self.page.spinTestOrderAmount.value()

        if not code:
            QMessageBox.warning(None, "Thiếu mã", "Vui lòng nhập mã cần kiểm tra")
            return

        ok, msg, discount_amount = DiscountModel.validate_code(code, order_total)

        if ok:
            self.page.lblTestResult.setText(f"Hợp lệ: giảm {self.money(discount_amount)}")
            self.page.lblTestResult.setStyleSheet("color: #16a34a; font-size: 14px; font-weight: bold;")
        else:
            self.page.lblTestResult.setText(f"Không hợp lệ: {msg}")
            self.page.lblTestResult.setStyleSheet("color: #dc2626; font-size: 14px; font-weight: bold;")

    def update_preview(self):
        code = self.page.txtCode.text().strip().upper() or "MÃ"
        dtype = self.page.cboDiscountType.currentText()
        value = self.page.spinDiscountValue.value()
        max_discount = self.page.spinMaxDiscount.value()
        min_order = self.page.spinMinOrder.value()
        usage_limit = self.page.spinUsageLimit.value()
        start = self.page.dateStart.date().toString("dd/MM/yyyy")
        end = self.page.dateEnd.date().toString("dd/MM/yyyy")
        status = self.page.cboStatus.currentText()

        if dtype == "percent":
            desc = f"{code}: giảm {value:.0f}%"
            if max_discount > 0:
                desc += f", tối đa {self.money(max_discount)}"
        else:
            desc = f"{code}: giảm cố định {self.money(value)}"

        if min_order > 0:
            desc += f", đơn từ {self.money(min_order)}"

        desc += f". Lượt dùng: {usage_limit}. Hạn: {start} - {end}. Trạng thái: {status}"

        self.page.lblPreview.setText(desc)

    def load_usage_stats(self):
        data = DiscountModel.get_usage_stats(5)

        self.page.tableUsageStats.setRowCount(0)

        for index, row_data in enumerate(data, start=1):
            row = self.page.tableUsageStats.rowCount()
            self.page.tableUsageStats.insertRow(row)

            code, used_count, total_discount_amount, revenue_applied = row_data
            values = [
                index,
                code,
                used_count,
                self.money(total_discount_amount),
                self.money(revenue_applied)
            ]

            for col, value in enumerate(values):
                self.page.tableUsageStats.setItem(row, col, QTableWidgetItem(str(value)))

    def export_csv(self):
        if not self.discounts_cache:
            QMessageBox.warning(None, "Không có dữ liệu", "Không có dữ liệu để xuất")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            None,
            "Xuất danh sách mã giảm giá",
            "danh_sach_ma_giam_gia.csv",
            "CSV Files (*.csv)"
        )

        if not file_path:
            return

        if not file_path.lower().endswith(".csv"):
            file_path += ".csv"

        headers = [
            "ID",
            "Mã",
            "Loại",
            "Giá trị",
            "Giảm tối đa",
            "Đơn tối thiểu",
            "Đã dùng",
            "Lượt tối đa",
            "Mỗi khách",
            "Bắt đầu",
            "Kết thúc",
            "Trạng thái",
            "Doanh thu áp mã"
        ]

        with open(file_path, "w", newline="", encoding="utf-8-sig") as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            for row in self.discounts_cache:
                writer.writerow(row)

        QMessageBox.information(None, "Thành công", f"Đã xuất danh sách:\n{file_path}")
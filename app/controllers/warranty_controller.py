import csv
import traceback
from datetime import datetime

from PyQt6.QtWidgets import (
    QMessageBox,
    QTableWidgetItem,
    QAbstractItemView,
    QFileDialog
)
from PyQt6.QtGui import QColor, QTextDocument, QPageSize
from PyQt6.QtCore import QDate, QSizeF
from PyQt6.QtPrintSupport import QPrinter

from app.models.warranty_model import WarrantyModel


class WarrantyController:
    def __init__(self, page):
        self.page = page
        self.current_device = None
        self.selected_warranty_id = None

        WarrantyModel.ensure_schema()
        self.setup_ui()
        self.connect_events()
        self.refresh()

    def setup_ui(self):
        self.page.tableWarrantyHistory.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.page.tableWarrantyHistory.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )

        self.page.tableWarrantyHistory.setColumnWidth(0, 55)
        self.page.tableWarrantyHistory.setColumnWidth(1, 140)
        self.page.tableWarrantyHistory.setColumnWidth(2, 160)
        self.page.tableWarrantyHistory.setColumnWidth(3, 130)
        self.page.tableWarrantyHistory.setColumnWidth(4, 95)
        self.page.tableWarrantyHistory.setColumnWidth(5, 95)
        self.page.tableWarrantyHistory.setColumnWidth(6, 95)
        self.page.tableWarrantyHistory.setColumnWidth(7, 160)
        self.page.tableWarrantyHistory.horizontalHeader().setStretchLastSection(True)

        today = QDate.currentDate()
        self.page.dateReceive.setDate(today)
        self.page.dateReturn.setDate(today)

    def connect_events(self):
        self.page.btnSearchImei.clicked.connect(self.search_imei)
        self.page.txtSearchImei.returnPressed.connect(self.search_imei)

        self.page.btnCreateWarranty.clicked.connect(self.create_warranty)
        self.page.btnUpdateWarranty.clicked.connect(self.update_warranty)
        self.page.btnReturnDevice.clicked.connect(self.return_device)
        self.page.btnCancelWarranty.clicked.connect(self.cancel_warranty)

        self.page.btnClearForm.clicked.connect(self.clear_form)
        self.page.btnRefresh.clicked.connect(self.refresh)
        self.page.cboHistoryFilter.currentIndexChanged.connect(self.load_history)

        self.page.tableWarrantyHistory.cellClicked.connect(self.select_history_row)

        self.page.btnPrintWarranty.clicked.connect(self.print_warranty_pdf)
        self.page.btnExportWarranty.clicked.connect(self.export_warranty_csv)

    def refresh(self):
        self.load_summary()
        self.load_history()

    def load_summary(self):
        total, pending, done, expired = WarrantyModel.get_summary()

        self.page.lblTotalWarranty.setText(str(total))
        self.page.lblPendingWarranty.setText(str(pending))
        self.page.lblDoneWarranty.setText(str(done))
        self.page.lblExpiredWarranty.setText(str(expired))

    def format_date_for_db(self, qdate):
        return qdate.toString("yyyy-MM-dd")

    def format_date_vn(self, date_text):
        if not date_text:
            return "---"

        try:
            return datetime.strptime(date_text[:10], "%Y-%m-%d").strftime("%d/%m/%Y")
        except Exception:
            return date_text

    def calculate_warranty_status(self, end_date):
        if not end_date:
            return "Không có dữ liệu", "---", "#64748b"

        try:
            end = datetime.strptime(end_date[:10], "%Y-%m-%d").date()
            today = datetime.now().date()
            days = (end - today).days

            if days < 0:
                return "Hết bảo hành", f"Quá hạn {abs(days)} ngày", "#dc2626"

            if days == 0:
                return "Hết hạn hôm nay", "Còn 0 ngày", "#f59e0b"

            return "Còn bảo hành", f"Còn {days} ngày", "#16a34a"

        except Exception:
            return "Không xác định", "---", "#64748b"

    def search_imei(self):
        imei = self.page.txtSearchImei.text().strip()

        if not imei:
            QMessageBox.warning(None, "Thiếu IMEI", "Vui lòng nhập IMEI cần tra cứu")
            return

        device = WarrantyModel.search_device_by_imei(imei)

        if not device:
            self.current_device = None
            self.clear_device_info()
            QMessageBox.warning(None, "Không tìm thấy", "Không tìm thấy IMEI trong hệ thống")
            return

        (
            imei_id,
            imei,
            imei_status,
            invoice_item_id,
            product_name,
            storage,
            color,
            warranty_month,
            invoice_id,
            sold_date,
            customer_id,
            customer_name,
            customer_phone,
            end_date
        ) = device

        if not invoice_item_id:
            self.current_device = None
            self.clear_device_info()
            QMessageBox.warning(
                None,
                "Chưa bán",
                "IMEI này chưa có hóa đơn bán hàng nên chưa thể tạo phiếu bảo hành"
            )
            return

        self.current_device = {
            "imei_id": imei_id,
            "imei": imei,
            "imei_status": imei_status,
            "invoice_item_id": invoice_item_id,
            "product_name": product_name,
            "storage": storage,
            "color": color,
            "warranty_month": warranty_month,
            "invoice_id": invoice_id,
            "sold_date": sold_date,
            "customer_id": customer_id,
            "customer_name": customer_name,
            "customer_phone": customer_phone,
            "end_date": end_date,
        }

        self.page.lblImeiValue.setText(imei)
        self.page.lblProductValue.setText(product_name or "---")
        self.page.lblVariantValue.setText(f"{storage or ''} / {color or ''}")
        self.page.lblSoldDateValue.setText(self.format_date_vn(sold_date))
        self.page.lblWarrantyEndValue.setText(self.format_date_vn(end_date))

        self.page.lblCustomerNameValue.setText(customer_name or "---")
        self.page.lblPhoneValue.setText(customer_phone or "---")
        self.page.lblInvoiceValue.setText(f"#{invoice_id}" if invoice_id else "---")

        status_text, remain_text, color_code = self.calculate_warranty_status(end_date)
        self.page.lblWarrantyStatusValue.setText(status_text)
        self.page.lblWarrantyStatusValue.setStyleSheet(
            f"color: {color_code}; font-size: 22px; font-weight: bold;"
        )
        self.page.lblWarrantyRemainValue.setText(remain_text)

        self.load_history()

    def clear_device_info(self):
        self.page.lblImeiValue.setText("---")
        self.page.lblProductValue.setText("---")
        self.page.lblVariantValue.setText("---")
        self.page.lblSoldDateValue.setText("---")
        self.page.lblWarrantyEndValue.setText("---")

        self.page.lblCustomerNameValue.setText("---")
        self.page.lblPhoneValue.setText("---")
        self.page.lblInvoiceValue.setText("---")

        self.page.lblWarrantyStatusValue.setText("Chưa tra cứu")
        self.page.lblWarrantyStatusValue.setStyleSheet(
            "color: #dc2626; font-size: 22px; font-weight: bold;"
        )
        self.page.lblWarrantyRemainValue.setText("---")

    def load_history(self):
        status_filter = self.page.cboHistoryFilter.currentText()

        # Nếu vừa tra cứu IMEI thì chỉ hiện lịch sử của IMEI đó
        imei = None
        if self.current_device:
            imei = self.current_device["imei"]

        data = WarrantyModel.get_history(status_filter, imei)

        self.page.tableWarrantyHistory.setRowCount(0)

        for row_data in data:
            row = self.page.tableWarrantyHistory.rowCount()
            self.page.tableWarrantyHistory.insertRow(row)

            for col, value in enumerate(row_data):
                display_value = value

                if col in [4, 5]:
                    display_value = self.format_date_vn(value)

                item = QTableWidgetItem(str(display_value))

                if col == 6:
                    if value in ["pending", "checking", "repairing"]:
                        item.setForeground(QColor("#f59e0b"))
                    elif value in ["done", "returned", "active"]:
                        item.setForeground(QColor("#16a34a"))
                    elif value == "cancelled":
                        item.setForeground(QColor("#dc2626"))

                self.page.tableWarrantyHistory.setItem(row, col, item)
    def select_history_row(self, row, column):
        self.selected_warranty_id = int(self.page.tableWarrantyHistory.item(row, 0).text())

        warranty = WarrantyModel.get_warranty_by_id(self.selected_warranty_id)
        if not warranty:
            return

        (
            warranty_id,
            invoice_item_id,
            customer_id,
            imei_id,
            imei,
            product_name,
            start_date,
            end_date,
            status,
            note,
            receive_date,
            return_date,
            issue,
            device_condition,
            tech_note
        ) = warranty

        self.page.cboWarrantyStatus.setCurrentText(status or "pending")

        if receive_date:
            self.page.dateReceive.setDate(QDate.fromString(receive_date[:10], "yyyy-MM-dd"))

        if return_date:
            self.page.dateReturn.setDate(QDate.fromString(return_date[:10], "yyyy-MM-dd"))

        self.page.txtIssue.setPlainText(issue or "")
        self.page.txtDeviceCondition.setPlainText(device_condition or "")
        self.page.txtTechNote.setPlainText(tech_note or note or "")

        if imei:
            self.page.txtSearchImei.setText(imei)
            self.search_imei()

    def validate_current_device(self):
        if not self.current_device:
            QMessageBox.warning(None, "Chưa chọn IMEI", "Vui lòng tra cứu IMEI trước")
            return False

        status_text = self.page.lblWarrantyStatusValue.text()
        if status_text == "Hết bảo hành":
            confirm = QMessageBox.question(
                None,
                "Máy đã hết bảo hành",
                "Máy này đã hết hạn bảo hành. Vẫn tạo phiếu xử lý?"
            )

            if confirm != QMessageBox.StandardButton.Yes:
                return False

        return True

    def create_warranty(self):
        if not self.validate_current_device():
            return

        issue = self.page.txtIssue.toPlainText().strip()
        device_condition = self.page.txtDeviceCondition.toPlainText().strip()
        tech_note = self.page.txtTechNote.toPlainText().strip()

        if not issue:
            QMessageBox.warning(None, "Thiếu thông tin", "Vui lòng nhập lỗi khách báo")
            return

        data = {
            "invoice_item_id": self.current_device["invoice_item_id"],
            "customer_id": self.current_device["customer_id"],
            "imei_id": self.current_device["imei_id"],
            "imei": self.current_device["imei"],
            "product_name": self.current_device["product_name"],
            "start_date": self.current_device["sold_date"][:10] if self.current_device["sold_date"] else "",
            "end_date": self.current_device["end_date"],
            "status": self.page.cboWarrantyStatus.currentText(),
            "note": tech_note,
            "receive_date": self.format_date_for_db(self.page.dateReceive.date()),
            "return_date": "",
            "issue": issue,
            "device_condition": device_condition,
            "tech_note": tech_note,
        }

        WarrantyModel.create_warranty_claim(data)
        QMessageBox.information(None, "Thành công", "Đã tạo phiếu bảo hành")
        self.clear_form()
        self.refresh()

    def update_warranty(self):
        if not self.selected_warranty_id:
            QMessageBox.warning(None, "Chưa chọn", "Vui lòng chọn phiếu bảo hành cần cập nhật")
            return

        WarrantyModel.update_warranty_claim(
            self.selected_warranty_id,
            self.page.cboWarrantyStatus.currentText(),
            self.format_date_for_db(self.page.dateReceive.date()),
            self.format_date_for_db(self.page.dateReturn.date()),
            self.page.txtIssue.toPlainText().strip(),
            self.page.txtDeviceCondition.toPlainText().strip(),
            self.page.txtTechNote.toPlainText().strip(),
        )

        QMessageBox.information(None, "Thành công", "Đã cập nhật phiếu bảo hành")
        self.refresh()

    def refresh(self):
        # Làm mới = reset IMEI đang tra cứu, hiển thị lại tất cả phiếu bảo hành
        self.current_device = None
        self.selected_warranty_id = None

        self.page.txtSearchImei.clear()
        self.clear_device_info()
        self.clear_form()

        self.load_summary()

        status_filter = self.page.cboHistoryFilter.currentText()
        data = WarrantyModel.get_history(status_filter, imei=None)

        self.page.tableWarrantyHistory.setRowCount(0)

        for row_data in data:
            row = self.page.tableWarrantyHistory.rowCount()
            self.page.tableWarrantyHistory.insertRow(row)

            for col, value in enumerate(row_data):
                display_value = value

                if col in [4, 5]:
                    display_value = self.format_date_vn(value)

                item = QTableWidgetItem(str(display_value))

                if col == 6:
                    if value in ["pending", "checking", "repairing"]:
                        item.setForeground(QColor("#f59e0b"))
                    elif value in ["done", "returned", "active"]:
                        item.setForeground(QColor("#16a34a"))
                    elif value == "cancelled":
                        item.setForeground(QColor("#dc2626"))

                self.page.tableWarrantyHistory.setItem(row, col, item)

    def return_device(self):
        if not self.selected_warranty_id:
            QMessageBox.warning(None, "Chưa chọn", "Vui lòng chọn phiếu bảo hành cần trả máy")
            return

        confirm = QMessageBox.question(
            None,
            "Xác nhận trả máy",
            "Xác nhận đã trả máy cho khách?"
        )

        if confirm != QMessageBox.StandardButton.Yes:
            return

        WarrantyModel.return_device(
            self.selected_warranty_id,
            self.format_date_for_db(self.page.dateReturn.date())
        )

        QMessageBox.information(None, "Thành công", "Đã cập nhật trạng thái trả máy")
        self.refresh()

    def cancel_warranty(self):
        if not self.selected_warranty_id:
            QMessageBox.warning(None, "Chưa chọn", "Vui lòng chọn phiếu bảo hành cần hủy")
            return

        confirm = QMessageBox.question(
            None,
            "Xác nhận hủy",
            "Bạn chắc chắn muốn hủy phiếu bảo hành này?"
        )

        if confirm != QMessageBox.StandardButton.Yes:
            return

        WarrantyModel.cancel_warranty(self.selected_warranty_id)
        QMessageBox.information(None, "Thành công", "Đã hủy phiếu bảo hành")
        self.refresh()

    def clear_form(self):
        self.selected_warranty_id = None
        self.page.cboWarrantyStatus.setCurrentText("pending")
        self.page.dateReceive.setDate(QDate.currentDate())
        self.page.dateReturn.setDate(QDate.currentDate())
        self.page.txtIssue.clear()
        self.page.txtDeviceCondition.clear()
        self.page.txtTechNote.clear()
        self.page.tableWarrantyHistory.clearSelection()

    def print_warranty_pdf(self):
        try:
            if not self.selected_warranty_id:
                QMessageBox.warning(None, "Chưa chọn", "Vui lòng chọn phiếu bảo hành cần in")
                return

            warranty = WarrantyModel.get_warranty_by_id(self.selected_warranty_id)
            if not warranty:
                QMessageBox.warning(None, "Lỗi", "Không tìm thấy phiếu bảo hành")
                return

            file_path, _ = QFileDialog.getSaveFileName(
                None,
                "Xuất phiếu bảo hành PDF",
                f"phieu_bao_hanh_{self.selected_warranty_id}.pdf",
                "PDF Files (*.pdf)"
            )

            if not file_path:
                return

            if not file_path.lower().endswith(".pdf"):
                file_path += ".pdf"

            html = self.build_warranty_html(warranty)

            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
            printer.setOutputFileName(file_path)
            printer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))

            document = QTextDocument()
            document.setHtml(html)
            document.setPageSize(QSizeF(printer.pageRect(QPrinter.Unit.Point).size()))
            document.print(printer)

            QMessageBox.information(None, "Thành công", f"Đã xuất phiếu bảo hành PDF:\n{file_path}")

        except Exception as e:
            print(traceback.format_exc())
            QMessageBox.critical(None, "Lỗi xuất PDF", f"Không thể xuất phiếu bảo hành:\n{e}")

    def build_warranty_html(self, warranty):
        (
            warranty_id,
            invoice_item_id,
            customer_id,
            imei_id,
            imei,
            product_name,
            start_date,
            end_date,
            status,
            note,
            receive_date,
            return_date,
            issue,
            device_condition,
            tech_note
        ) = warranty

        customer_name = self.page.lblCustomerNameValue.text()
        customer_phone = self.page.lblPhoneValue.text()
        invoice_text = self.page.lblInvoiceValue.text()
        variant_text = self.page.lblVariantValue.text()
        sold_date = self.page.lblSoldDateValue.text()

        status_text, remain_text, color_code = self.calculate_warranty_status(end_date)

        return f"""
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    color: #0f172a;
                    font-size: 12px;
                }}

                .header {{
                    text-align: center;
                    margin-bottom: 20px;
                }}

                .shop {{
                    font-size: 28px;
                    font-weight: bold;
                    color: #1e3a8a;
                    letter-spacing: 1px;
                }}

                .subtitle {{
                    color: #64748b;
                    margin-top: 4px;
                }}

                .title {{
                    margin-top: 12px;
                    font-size: 22px;
                    font-weight: bold;
                    color: #dc2626;
                }}

                .box {{
                    border: 1px solid #dbeafe;
                    border-radius: 10px;
                    padding: 12px;
                    margin-bottom: 12px;
                }}

                table {{
                    width: 100%;
                    border-collapse: collapse;
                }}

                td {{
                    padding: 6px;
                    vertical-align: top;
                }}

                .label {{
                    font-weight: bold;
                    color: #475569;
                    width: 130px;
                }}

                .status {{
                    font-size: 18px;
                    font-weight: bold;
                    color: {color_code};
                }}

                .section {{
                    font-size: 15px;
                    font-weight: bold;
                    color: #1e3a8a;
                    margin-bottom: 8px;
                }}

                .note-box {{
                    border: 1px solid #dbeafe;
                    background-color: #f8fbff;
                    border-radius: 8px;
                    padding: 10px;
                    min-height: 55px;
                }}

                .sign {{
                    margin-top: 45px;
                    text-align: center;
                    font-weight: bold;
                }}

                .footer {{
                    margin-top: 30px;
                    text-align: center;
                    color: #64748b;
                    font-style: italic;
                }}
            </style>
        </head>

        <body>
            <div class="header">
                <div class="shop">LV SHOP</div>
                <div class="subtitle">Phiếu tiếp nhận và xử lý bảo hành theo IMEI</div>
                <div class="title">PHIẾU BẢO HÀNH</div>
            </div>

            <div class="box">
                <table>
                    <tr>
                        <td class="label">Mã phiếu:</td>
                        <td>#{warranty_id}</td>
                        <td class="label">Trạng thái:</td>
                        <td class="status">{status}</td>
                    </tr>
                    <tr>
                        <td class="label">Ngày nhận:</td>
                        <td>{self.format_date_vn(receive_date)}</td>
                        <td class="label">Ngày trả:</td>
                        <td>{self.format_date_vn(return_date)}</td>
                    </tr>
                    <tr>
                        <td class="label">Tình trạng BH:</td>
                        <td>{status_text}</td>
                        <td class="label">Thời hạn:</td>
                        <td>{remain_text}</td>
                    </tr>
                </table>
            </div>

            <div class="box">
                <div class="section">Thông tin máy</div>
                <table>
                    <tr>
                        <td class="label">IMEI:</td>
                        <td>{imei}</td>
                        <td class="label">Hóa đơn:</td>
                        <td>{invoice_text}</td>
                    </tr>
                    <tr>
                        <td class="label">Sản phẩm:</td>
                        <td>{product_name}</td>
                        <td class="label">Biến thể:</td>
                        <td>{variant_text}</td>
                    </tr>
                    <tr>
                        <td class="label">Ngày bán:</td>
                        <td>{sold_date}</td>
                        <td class="label">Hạn bảo hành:</td>
                        <td>{self.format_date_vn(end_date)}</td>
                    </tr>
                </table>
            </div>

            <div class="box">
                <div class="section">Thông tin khách hàng</div>
                <table>
                    <tr>
                        <td class="label">Khách hàng:</td>
                        <td>{customer_name}</td>
                        <td class="label">SĐT:</td>
                        <td>{customer_phone}</td>
                    </tr>
                </table>
            </div>

            <div class="box">
                <div class="section">Thông tin lỗi và xử lý</div>
                <table>
                    <tr>
                        <td class="label">Lỗi khách báo:</td>
                        <td><div class="note-box">{issue or ""}</div></td>
                    </tr>
                    <tr>
                        <td class="label">Tình trạng máy:</td>
                        <td><div class="note-box">{device_condition or ""}</div></td>
                    </tr>
                    <tr>
                        <td class="label">Ghi chú kỹ thuật:</td>
                        <td><div class="note-box">{tech_note or note or ""}</div></td>
                    </tr>
                </table>
            </div>

            <table class="sign">
                <tr>
                    <td>Khách hàng</td>
                    <td>Nhân viên tiếp nhận</td>
                    <td>Kỹ thuật</td>
                </tr>
                <tr>
                    <td><br><br><br>{customer_name}</td>
                    <td><br><br><br>LV SHOP</td>
                    <td><br><br><br>........................</td>
                </tr>
            </table>

            <div class="footer">
                Vui lòng giữ phiếu này để đối chiếu khi nhận máy.
            </div>
        </body>
        </html>
        """

    def export_warranty_csv(self):
        try:
            status_filter = self.page.cboHistoryFilter.currentText()
            imei = None

            if self.current_device:
                imei = self.current_device["imei"]

            data = WarrantyModel.get_history(status_filter, imei)

            if not data:
                QMessageBox.warning(None, "Không có dữ liệu", "Không có dữ liệu bảo hành để xuất")
                return

            file_path, _ = QFileDialog.getSaveFileName(
                None,
                "Xuất danh sách bảo hành",
                "danh_sach_bao_hanh.csv",
                "CSV Files (*.csv)"
            )

            if not file_path:
                return

            if not file_path.lower().endswith(".csv"):
                file_path += ".csv"

            headers = [
                "ID",
                "IMEI",
                "Sản phẩm",
                "Khách hàng",
                "Ngày nhận",
                "Ngày trả",
                "Trạng thái",
                "Lỗi báo",
                "Ghi chú kỹ thuật",
            ]

            with open(file_path, "w", newline="", encoding="utf-8-sig") as file:
                writer = csv.writer(file)
                writer.writerow(headers)

                for row in data:
                    row = list(row)
                    row[4] = self.format_date_vn(row[4])
                    row[5] = self.format_date_vn(row[5])
                    writer.writerow(row)

            QMessageBox.information(None, "Thành công", f"Đã xuất danh sách bảo hành:\n{file_path}")

        except Exception as e:
            print(traceback.format_exc())
            QMessageBox.critical(None, "Lỗi xuất file", f"Không thể xuất danh sách bảo hành:\n{e}")
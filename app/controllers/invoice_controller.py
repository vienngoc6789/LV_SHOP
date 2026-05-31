import traceback
from datetime import datetime, date

from PyQt6.QtWidgets import (
    QTableWidgetItem,
    QMessageBox,
    QAbstractItemView,
    QFileDialog
)
from PyQt6.QtGui import QColor, QTextDocument, QPageSize
from PyQt6.QtCore import QSizeF, QDate
from PyQt6.QtPrintSupport import QPrinter

from app.models.invoice_model import InvoiceModel


class InvoiceController:
    def __init__(self, page):
        self.page = page
        self.selected_invoice_id = None
        self.invoices_cache = []

        self.setup_tables()
        self.connect_events()
        self.clear_invoice_table()
        self.clear_invoice_detail()
        self.load_summary()

    def money(self, value):
        return f"{float(value):,.0f} đ"

    def setup_tables(self):
        for table in [self.page.tableInvoices, self.page.tableInvoiceItems]:
            table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
            table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        self.page.tableInvoices.setColumnWidth(0, 70)
        self.page.tableInvoices.setColumnWidth(1, 145)
        self.page.tableInvoices.setColumnWidth(2, 150)
        self.page.tableInvoices.setColumnWidth(3, 105)
        self.page.tableInvoices.setColumnWidth(4, 70)
        self.page.tableInvoices.setColumnWidth(5, 105)
        self.page.tableInvoices.setColumnWidth(6, 90)
        self.page.tableInvoices.setColumnWidth(7, 110)
        self.page.tableInvoices.setColumnWidth(8, 95)
        self.page.tableInvoices.horizontalHeader().setStretchLastSection(True)

        self.page.tableInvoiceItems.setColumnWidth(0, 135)
        self.page.tableInvoiceItems.setColumnWidth(1, 150)
        self.page.tableInvoiceItems.setColumnWidth(2, 70)
        self.page.tableInvoiceItems.setColumnWidth(3, 70)
        self.page.tableInvoiceItems.horizontalHeader().setStretchLastSection(True)

    def connect_events(self):
        if hasattr(self.page, "btnRefresh"):
            self.page.btnRefresh.clicked.connect(self.new_page)

        if hasattr(self.page, "btnSearch"):
            self.page.btnSearch.clicked.connect(self.search_invoices)

        if hasattr(self.page, "btnClearFilter"):
            self.page.btnClearFilter.clicked.connect(self.clear_filter)

        self.page.tableInvoices.cellClicked.connect(self.select_invoice_row)

        self.page.btnViewDetail.clicked.connect(self.view_selected_invoice)
        self.page.btnCancelInvoice.clicked.connect(self.cancel_invoice)

        self.page.btnExportPdf.clicked.connect(self.export_pdf)
        self.page.btnReprintInvoice.clicked.connect(self.export_pdf)
        self.page.btnReturnItem.clicked.connect(self.notice_return)

    def clear_invoice_table(self):
        self.page.tableInvoices.setRowCount(0)

    def clear_invoice_items(self):
        self.page.tableInvoiceItems.setRowCount(0)

    def clear_invoice_detail(self):
        self.selected_invoice_id = None

        labels = [
            "lblInvoiceIdValue",
            "lblCreatedAtValue",
            "lblCustomerValue",
            "lblPhoneValue",
            "lblStaffValue",
            "lblPaymentValue",
            "lblSubtotalValue",
            "lblDiscountValue",
            "lblTotalValue",
        ]

        for name in labels:
            if hasattr(self.page, name):
                getattr(self.page, name).setText("")

        self.clear_invoice_items()

    def new_page(self):
        self.invoices_cache = []
        self.selected_invoice_id = None
        self.clear_invoice_table()
        self.clear_invoice_detail()
        self.load_summary()

    def refresh(self):
        self.new_page()

    def load_summary(self):
        total, today, month, cancelled = InvoiceModel.get_summary()

        self.page.lblTotalInvoices.setText(str(total))
        self.page.lblTodayRevenue.setText(self.money(today))
        self.page.lblMonthRevenue.setText(self.money(month))
        self.page.lblCancelledInvoices.setText(str(cancelled))

    def get_date_value(self, widget_names):
        for name in widget_names:
            if not hasattr(self.page, name):
                continue

            widget = getattr(self.page, name)

            try:
                if hasattr(widget, "date"):
                    qdate = widget.date()

                    if isinstance(qdate, QDate) and qdate.isValid():
                        return date(qdate.year(), qdate.month(), qdate.day())

                if hasattr(widget, "text"):
                    text = widget.text().strip()

                    if not text:
                        return None

                    for fmt in [
                        "%d/%m/%Y",
                        "%d-%m-%Y",
                        "%Y-%m-%d",
                        "%d/%m/%y",
                        "%d-%m-%y"
                    ]:
                        try:
                            return datetime.strptime(text, fmt).date()
                        except ValueError:
                            pass

            except Exception:
                pass

        return None

    def get_from_date(self):
        return self.get_date_value([
            "dateFrom",
            "dateFromInvoice",
            "dateStart",
            "dateStartInvoice",
            "dtFrom",
            "dtStart",
            "txtFromDate",
            "txtStartDate",
            "txtDateFrom",
        ])

    def get_to_date(self):
        return self.get_date_value([
            "dateTo",
            "dateToInvoice",
            "dateEnd",
            "dateEndInvoice",
            "dtTo",
            "dtEnd",
            "txtToDate",
            "txtEndDate",
            "txtDateTo",
        ])

    def parse_invoice_date(self, value):
        if not value:
            return None

        text = str(value).strip()

        for fmt in [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%Y-%m-%d",
            "%d/%m/%Y %H:%M:%S",
            "%d/%m/%Y %H:%M",
            "%d/%m/%Y",
            "%d-%m-%Y %H:%M:%S",
            "%d-%m-%Y %H:%M",
            "%d-%m-%Y",
        ]:
            try:
                return datetime.strptime(text, fmt).date()
            except ValueError:
                pass

        try:
            return datetime.fromisoformat(text).date()
        except Exception:
            return None

    def has_filter_condition(self):
        keyword = self.page.txtSearchInvoice.text().lower().strip()
        payment_filter = self.page.cboPaymentFilter.currentText()
        status_filter = self.page.cboStatusFilter.currentText()
        from_date = self.get_from_date()
        to_date = self.get_to_date()

        has_keyword = bool(keyword)

        has_payment = payment_filter not in [
            "",
            "Tất cả",
            "Tất cả thanh toán",
            "Tất cả phương thức",
        ]

        has_status = status_filter not in [
            "",
            "Tất cả",
            "Tất cả trạng thái",
        ]

        has_date = from_date is not None or to_date is not None

        return has_keyword or has_payment or has_status or has_date

    def search_invoices(self):
        if not self.has_filter_condition():
            QMessageBox.warning(
                None,
                "Thiếu điều kiện tìm kiếm",
                "Vui lòng nhập từ khóa, chọn ngày, trạng thái hoặc phương thức thanh toán để tìm."
            )
            return

        self.invoices_cache = InvoiceModel.get_all_invoices()
        self.apply_filters()
        self.load_summary()

    def apply_filters(self):
        keyword = self.page.txtSearchInvoice.text().lower().strip()
        payment_filter = self.page.cboPaymentFilter.currentText()
        status_filter = self.page.cboStatusFilter.currentText()
        from_date = self.get_from_date()
        to_date = self.get_to_date()

        data = []

        for row in self.invoices_cache:
            text = " ".join(str(x).lower() for x in row)

            created_at = row[1]
            payment = row[8]
            status = row[9]

            invoice_date = self.parse_invoice_date(created_at)

            if payment_filter == "Tiền mặt":
                match_payment = payment == "cash"
            elif payment_filter == "QR chuyển khoản" or payment_filter == "QR":
                match_payment = payment == "qr"
            else:
                match_payment = True

            if status_filter in ["Tất cả trạng thái", "Tất cả", ""]:
                match_status = True
            else:
                match_status = status == status_filter

            if keyword:
                match_keyword = keyword in text
            else:
                match_keyword = True

            match_date = True

            if from_date and invoice_date:
                match_date = match_date and invoice_date >= from_date

            if to_date and invoice_date:
                match_date = match_date and invoice_date <= to_date

            if (from_date or to_date) and not invoice_date:
                match_date = False

            if match_keyword and match_payment and match_status and match_date:
                data.append(row)

        self.render_invoices(data)

    def render_invoices(self, data):
        self.page.tableInvoices.setRowCount(0)

        for row_data in data:
            row = self.page.tableInvoices.rowCount()
            self.page.tableInvoices.insertRow(row)

            for col, value in enumerate(row_data):
                display_value = value

                if col in [5, 6, 7]:
                    display_value = self.money(value)

                if col == 8:
                    display_value = "Tiền mặt" if value == "cash" else "QR"

                item = QTableWidgetItem(str(display_value))

                if col == 9:
                    if value == "paid":
                        item.setForeground(QColor("#16a34a"))
                    elif value == "cancelled":
                        item.setForeground(QColor("#dc2626"))
                    elif value == "returned":
                        item.setForeground(QColor("#f59e0b"))

                self.page.tableInvoices.setItem(row, col, item)

    def select_invoice_row(self, row, column):
        item = self.page.tableInvoices.item(row, 0)

        if not item:
            return

        self.selected_invoice_id = int(item.text())
        self.load_invoice_detail(self.selected_invoice_id)

    def view_selected_invoice(self):
        if not self.selected_invoice_id:
            QMessageBox.warning(None, "Chưa chọn", "Vui lòng chọn hóa đơn")
            return

        self.load_invoice_detail(self.selected_invoice_id)

    def load_invoice_detail(self, invoice_id):
        detail = InvoiceModel.get_invoice_detail(invoice_id)

        if not detail:
            return

        (
            invoice_id,
            created_at,
            customer_name,
            customer_phone,
            staff_name,
            payment_method,
            subtotal,
            discount,
            total,
            status
        ) = detail

        self.page.lblInvoiceIdValue.setText(f"#{invoice_id}")
        self.page.lblCreatedAtValue.setText(str(created_at))
        self.page.lblCustomerValue.setText(customer_name)
        self.page.lblPhoneValue.setText(customer_phone)
        self.page.lblStaffValue.setText(staff_name)
        self.page.lblPaymentValue.setText("Tiền mặt" if payment_method == "cash" else "QR")

        self.page.lblSubtotalValue.setText(self.money(subtotal))
        self.page.lblDiscountValue.setText(self.money(discount))
        self.page.lblTotalValue.setText(self.money(total))

        self.load_invoice_items(invoice_id)

    def load_invoice_items(self, invoice_id):
        data = InvoiceModel.get_invoice_items(invoice_id)

        self.page.tableInvoiceItems.setRowCount(0)

        for row_data in data:
            row = self.page.tableInvoiceItems.rowCount()
            self.page.tableInvoiceItems.insertRow(row)

            for col, value in enumerate(row_data):
                display_value = self.money(value) if col == 4 else value
                self.page.tableInvoiceItems.setItem(row, col, QTableWidgetItem(str(display_value)))

    def clear_date_widgets(self):
        today = QDate.currentDate()

        for name in [
            "dateFrom",
            "dateFromInvoice",
            "dateStart",
            "dateStartInvoice",
            "dtFrom",
            "dtStart",
        ]:
            if hasattr(self.page, name):
                widget = getattr(self.page, name)
                try:
                    if hasattr(widget, "setDate"):
                        widget.setDate(today)
                    elif hasattr(widget, "clear"):
                        widget.clear()
                except Exception:
                    pass

        for name in [
            "dateTo",
            "dateToInvoice",
            "dateEnd",
            "dateEndInvoice",
            "dtTo",
            "dtEnd",
        ]:
            if hasattr(self.page, name):
                widget = getattr(self.page, name)
                try:
                    if hasattr(widget, "setDate"):
                        widget.setDate(today)
                    elif hasattr(widget, "clear"):
                        widget.clear()
                except Exception:
                    pass

        for name in [
            "txtFromDate",
            "txtStartDate",
            "txtDateFrom",
            "txtToDate",
            "txtEndDate",
            "txtDateTo",
        ]:
            if hasattr(self.page, name):
                widget = getattr(self.page, name)
                try:
                    widget.clear()
                except Exception:
                    pass

    def clear_filter(self):
        self.page.txtSearchInvoice.clear()
        self.page.cboPaymentFilter.setCurrentIndex(0)
        self.page.cboStatusFilter.setCurrentIndex(0)

        self.clear_date_widgets()

        self.invoices_cache = []
        self.selected_invoice_id = None
        self.clear_invoice_table()
        self.clear_invoice_detail()
        self.load_summary()

    def cancel_invoice(self):
        if not self.selected_invoice_id:
            QMessageBox.warning(None, "Chưa chọn", "Vui lòng chọn hóa đơn cần hủy")
            return

        confirm = QMessageBox.question(
            None,
            "Xác nhận hủy đơn",
            "Hủy đơn sẽ trả IMEI về kho và đổi trạng thái hóa đơn thành cancelled. Tiếp tục?"
        )

        if confirm != QMessageBox.StandardButton.Yes:
            return

        InvoiceModel.cancel_invoice(self.selected_invoice_id)
        QMessageBox.information(None, "Thành công", "Đã hủy hóa đơn và trả IMEI về kho")

        self.search_invoices()

        if self.selected_invoice_id:
            self.load_invoice_detail(self.selected_invoice_id)

    def export_pdf(self):
        try:
            if not self.selected_invoice_id:
                QMessageBox.warning(None, "Chưa chọn", "Vui lòng chọn hóa đơn cần xuất PDF")
                return

            detail = InvoiceModel.get_invoice_detail(self.selected_invoice_id)
            items = InvoiceModel.get_invoice_items(self.selected_invoice_id)

            if not detail:
                QMessageBox.warning(None, "Lỗi", "Không tìm thấy hóa đơn")
                return

            file_path, _ = QFileDialog.getSaveFileName(
                None,
                "Xuất hóa đơn PDF",
                f"hoa_don_{self.selected_invoice_id}.pdf",
                "PDF Files (*.pdf)"
            )

            if not file_path:
                return

            if not file_path.lower().endswith(".pdf"):
                file_path += ".pdf"

            html = self.build_invoice_html(detail, items)

            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
            printer.setOutputFileName(file_path)
            printer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))

            document = QTextDocument()
            document.setHtml(html)
            document.setPageSize(QSizeF(printer.pageRect(QPrinter.Unit.Point).size()))
            document.print(printer)

            QMessageBox.information(None, "Thành công", f"Đã xuất hóa đơn PDF:\n{file_path}")

        except Exception as e:
            print(traceback.format_exc())
            QMessageBox.critical(None, "Lỗi xuất PDF", f"Không thể xuất hóa đơn PDF:\n{e}")

    def build_invoice_html(self, detail, items):
        (
            invoice_id,
            created_at,
            customer_name,
            customer_phone,
            staff_name,
            payment_method,
            subtotal,
            discount,
            total,
            status
        ) = detail

        payment_text = "Tiền mặt" if payment_method == "cash" else "QR chuyển khoản"

        rows = ""
        for index, item in enumerate(items, start=1):
            imei, product_name, storage, color, price = item

            rows += f"""
            <tr>
                <td>{index}</td>
                <td>
                    <b>{product_name}</b><br>
                    <span>{storage} - {color}</span>
                </td>
                <td>{imei}</td>
                <td class="right">{self.money(price)}</td>
            </tr>
            """

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
                    padding: 5px;
                    vertical-align: top;
                }}

                .label {{
                    font-weight: bold;
                    color: #475569;
                    width: 120px;
                }}

                .items th {{
                    background: #1e3a8a;
                    color: white;
                    padding: 8px;
                    border: 1px solid #1e3a8a;
                }}

                .items td {{
                    border: 1px solid #dbeafe;
                    padding: 8px;
                }}

                .items span {{
                    color: #64748b;
                    font-size: 11px;
                }}

                .right {{
                    text-align: right;
                }}

                .total {{
                    margin-top: 14px;
                }}

                .total td {{
                    padding: 6px;
                }}

                .grand {{
                    color: #dc2626;
                    font-size: 20px;
                    font-weight: bold;
                }}

                .sign {{
                    margin-top: 40px;
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
                <div class="subtitle">Chuyên điện thoại chính hãng - Bảo hành theo IMEI</div>
                <div class="title">HÓA ĐƠN BÁN HÀNG</div>
            </div>

            <div class="box">
                <table>
                    <tr>
                        <td class="label">Mã hóa đơn:</td>
                        <td>#{invoice_id}</td>
                        <td class="label">Ngày bán:</td>
                        <td>{created_at}</td>
                    </tr>
                    <tr>
                        <td class="label">Khách hàng:</td>
                        <td>{customer_name}</td>
                        <td class="label">SĐT:</td>
                        <td>{customer_phone}</td>
                    </tr>
                    <tr>
                        <td class="label">Nhân viên:</td>
                        <td>{staff_name}</td>
                        <td class="label">Thanh toán:</td>
                        <td>{payment_text}</td>
                    </tr>
                    <tr>
                        <td class="label">Trạng thái:</td>
                        <td>{status}</td>
                        <td></td>
                        <td></td>
                    </tr>
                </table>
            </div>

            <table class="items">
                <tr>
                    <th>STT</th>
                    <th>Sản phẩm</th>
                    <th>IMEI</th>
                    <th>Thành tiền</th>
                </tr>
                {rows}
            </table>

            <table class="total">
                <tr>
                    <td class="right"><b>Tạm tính:</b></td>
                    <td class="right">{self.money(subtotal)}</td>
                </tr>
                <tr>
                    <td class="right"><b>Giảm giá:</b></td>
                    <td class="right">{self.money(discount)}</td>
                </tr>
                <tr>
                    <td class="right grand">Tổng thanh toán:</td>
                    <td class="right grand">{self.money(total)}</td>
                </tr>
            </table>

            <table class="sign">
                <tr>
                    <td>Khách hàng</td>
                    <td>Nhân viên bán hàng</td>
                </tr>
                <tr>
                    <td><br><br><br>{customer_name}</td>
                    <td><br><br><br>{staff_name}</td>
                </tr>
            </table>

            <div class="footer">
                Cảm ơn quý khách đã mua hàng tại LV SHOP!
            </div>
        </body>
        </html>
        """

    def notice_return(self):
        QMessageBox.information(
            None,
            "Thông báo",
            "Hoàn từng sản phẩm sẽ làm sau. Hiện tại có thể hủy cả hóa đơn."
        )
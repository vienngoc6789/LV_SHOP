from datetime import datetime

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QAbstractItemView,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.models.customer_portal_model import CustomerPortalModel


class CustomerPortalController:
    def __init__(self, page, main_window=None):
        self.page = page
        self.main_window = main_window
        self.customer_id = None

        self.setup_ui()
        self.connect_events()

    def setup_ui(self):
        for table in [self.page.tableProducts, self.page.tableHistory, self.page.tableWarranty]:
            table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
            table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            table.horizontalHeader().setStretchLastSection(True)

        self.page.tableProducts.setColumnWidth(0, 210)
        self.page.tableProducts.setColumnWidth(1, 110)
        self.page.tableProducts.setColumnWidth(2, 140)
        self.page.tableProducts.setColumnWidth(3, 120)
        self.page.tableProducts.setColumnWidth(4, 120)

        self.page.tableHistory.setColumnWidth(0, 75)
        self.page.tableHistory.setColumnWidth(1, 130)
        self.page.tableHistory.setColumnWidth(2, 170)
        self.page.tableHistory.setColumnWidth(5, 145)

        self.page.tableWarranty.setColumnWidth(0, 145)
        self.page.tableWarranty.setColumnWidth(1, 70)
        self.page.tableWarranty.setColumnWidth(2, 145)
        self.page.tableWarranty.setColumnWidth(3, 180)
        self.page.tableWarranty.setColumnWidth(6, 110)

    def connect_events(self):
        self.page.btnSearchProducts.clicked.connect(self.load_products)
        self.page.btnRefreshProducts.clicked.connect(self.refresh_products)
        self.page.txtProductSearch.returnPressed.connect(self.load_products)

        self.page.btnRefreshHistory.clicked.connect(self.load_history)

        self.page.btnSearchWarranty.clicked.connect(self.load_warranty)
        self.page.btnRefreshWarranty.clicked.connect(self.refresh_warranty)
        self.page.txtWarrantySearch.returnPressed.connect(self.load_warranty)

        self.page.btnSendChat.clicked.connect(self.send_chat)
        self.page.txtChatInput.returnPressed.connect(self.send_chat)
        self.page.btnClearChat.clicked.connect(self.clear_chat)

    def refresh(self):
        user = getattr(self.main_window, "current_user", None) if self.main_window else None
        self.customer_id = CustomerPortalModel.resolve_customer(user)

        if not self.customer_id:
            self.clear_tables()
            self.page.lblCustomerSummary.setText("Chưa xác định được hồ sơ khách hàng.")
            return

        name = user[1] if user and len(user) > 1 else "Khách hàng"
        self.page.lblCustomerSummary.setText(f"Xin chào {name}. Bạn có thể xem sản phẩm, đơn mua, bảo hành và hỏi AI tại đây.")
        self.load_products()
        self.load_history()
        self.load_warranty()

    def clear_tables(self):
        self.page.tableProducts.setRowCount(0)
        self.page.tableHistory.setRowCount(0)
        self.page.tableWarranty.setRowCount(0)

    def money(self, value):
        return f"{float(value or 0):,.0f} đ"

    def format_date(self, value):
        if not value:
            return ""
        value = str(value)
        for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]:
            try:
                return datetime.strptime(value[:19 if "H" in fmt else 10], fmt).strftime("%d/%m/%Y")
            except Exception:
                pass
        return value

    def refresh_products(self):
        self.page.txtProductSearch.clear()
        self.load_products()

    def load_products(self):
        data = CustomerPortalModel.get_available_products(self.page.txtProductSearch.text())
        self.page.tableProducts.setRowCount(0)

        for row_data in data:
            row = self.page.tableProducts.rowCount()
            self.page.tableProducts.insertRow(row)

            variant_id, name, brand, storage, color, price, description, stock_count = row_data
            stock_text = "Còn hàng"

            note = "Có thể đặt mua tại cửa hàng"
            if description:
                clean_description = " ".join(str(description).split())
                note = clean_description[:80] + ("..." if len(clean_description) > 80 else "")

            values = [
                name,
                brand,
                f"{storage} / {color}",
                self.money(price),
                stock_text,
                note,
            ]

            for col, value in enumerate(values):
                self.page.tableProducts.setItem(row, col, QTableWidgetItem(str(value)))

    def load_history(self):
        if not self.customer_id:
            return

        data = CustomerPortalModel.get_purchase_history(self.customer_id)
        self.page.tableHistory.setRowCount(0)

        for row_data in data:
            row = self.page.tableHistory.rowCount()
            self.page.tableHistory.insertRow(row)

            values = list(row_data)
            values[1] = self.format_date(values[1])
            values[6] = self.money(values[6])
            values[7] = f"{values[7]} tháng"
            values[8] = "Tiền mặt" if values[8] == "cash" else "QR" if values[8] == "qr" else values[8]

            for col, value in enumerate(values):
                self.page.tableHistory.setItem(row, col, QTableWidgetItem(str(value)))

    def refresh_warranty(self):
        self.page.txtWarrantySearch.clear()
        self.load_warranty()

    def load_warranty(self):
        if not self.customer_id:
            return

        data = CustomerPortalModel.get_warranty_status(
            self.customer_id,
            self.page.txtWarrantySearch.text()
        )
        self.page.tableWarranty.setRowCount(0)
        claim_counts = {}

        for row_data in data:
            row = self.page.tableWarranty.rowCount()
            self.page.tableWarranty.insertRow(row)

            warranty_id, invoice_item_id, imei, product_name, start_date, end_date, status, receive_date, return_date, issue, tech_note = row_data
            claim_counts[invoice_item_id] = claim_counts.get(invoice_item_id, 0) + 1
            claim_number = claim_counts[invoice_item_id]
            claim_label = "Gốc" if claim_number == 1 and not receive_date and status == "active" else f"Lần {claim_number}"

            values = [
                f"#{warranty_id}",
                claim_label,
                imei,
                product_name,
                start_date,
                end_date,
                CustomerPortalModel.warranty_remaining_text(end_date),
                status,
                receive_date,
                return_date,
                issue,
                tech_note,
            ]
            for col in [4, 5, 8, 9]:
                values[col] = self.format_date(values[col])

            for col, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                if col == 6:
                    text = str(value)
                    if text.startswith("Còn"):
                        item.setForeground(Qt.GlobalColor.darkGreen)
                    elif text.startswith("Hết"):
                        item.setForeground(Qt.GlobalColor.red)
                self.page.tableWarranty.setItem(row, col, item)

    def append_chat(self, sender, text, side="left"):
        is_user = side == "right"
        bubble_bg = "#2563eb" if is_user else "#ffffff"
        text_color = "#ffffff" if is_user else "#0f172a"
        border = "1px solid #2563eb" if is_user else "1px solid #dbeafe"
        label_color = "#dbeafe" if is_user else "#2563eb"

        row = QWidget(parent=self.page.chatMessagesWidget)
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(8)

        bubble = QFrame(parent=row)
        bubble.setMaximumWidth(560)
        bubble.setStyleSheet(f"""
QFrame {{
    background-color: {bubble_bg};
    border: {border};
    border-radius: 14px;
}}
        """)

        bubble_layout = QVBoxLayout(bubble)
        bubble_layout.setContentsMargins(12, 8, 12, 10)
        bubble_layout.setSpacing(4)

        sender_label = QLabel(sender, parent=bubble)
        sender_label.setStyleSheet(
            f"QLabel {{ color: {label_color}; font-size: 11px; font-weight: bold; "
            "background: transparent; border: none; padding: 0; margin: 0; }}"
        )

        message_label = QLabel(str(text), parent=bubble)
        message_label.setWordWrap(True)
        message_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        message_label.setStyleSheet(
            f"QLabel {{ color: {text_color}; font-size: 13px; background: transparent; "
            "border: none; padding: 0; margin: 0; }}"
        )

        bubble_layout.addWidget(sender_label)
        bubble_layout.addWidget(message_label)

        if is_user:
            row_layout.addStretch(1)
            row_layout.addWidget(bubble)
        else:
            row_layout.addWidget(bubble)
            row_layout.addStretch(1)

        self.page.chatMessagesLayout.addWidget(row)
        QApplication.processEvents()
        self.page.chatScrollArea.verticalScrollBar().setValue(
            self.page.chatScrollArea.verticalScrollBar().maximum()
        )

    def clear_chat(self):
        while self.page.chatMessagesLayout.count():
            item = self.page.chatMessagesLayout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def send_chat(self):
        if not self.customer_id:
            QMessageBox.warning(None, "Chưa có hồ sơ", "Không xác định được hồ sơ khách hàng.")
            return

        question = self.page.txtChatInput.text().strip()
        if not question:
            return

        self.append_chat("Bạn", question, "right")
        self.page.txtChatInput.clear()

        old_text = self.page.btnSendChat.text()
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        self.page.btnSendChat.setEnabled(False)
        self.page.btnSendChat.setText("Đang hỏi...")
        QApplication.processEvents()

        ok, answer = CustomerPortalModel.ask_gemini(self.customer_id, question)

        self.page.btnSendChat.setEnabled(True)
        self.page.btnSendChat.setText(old_text)
        QApplication.restoreOverrideCursor()

        if not ok:
            self.append_chat("Hệ thống", answer, "left")
            return

        self.append_chat("AI", answer, "left")

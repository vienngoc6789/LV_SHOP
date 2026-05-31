from PyQt6 import QtCore, QtWidgets


class Ui_CustomerPortalPage(object):
    def setupUi(self, CustomerPortalPage):
        CustomerPortalPage.setObjectName("CustomerPortalPage")
        CustomerPortalPage.resize(1050, 560)
        CustomerPortalPage.setStyleSheet("""
QWidget#CustomerPortalPage {
    background-color: #f8fafc;
}
QTabWidget::pane {
    border: 1px solid #dbeafe;
    border-radius: 12px;
    background-color: white;
}
QTabBar::tab {
    background-color: #e2e8f0;
    color: #0f172a;
    padding: 9px 16px;
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
    font-weight: bold;
}
QTabBar::tab:selected {
    background-color: #2563eb;
    color: white;
}
QLineEdit {
    background-color: white;
    border: 1px solid #cbd5e1;
    border-radius: 10px;
    padding: 8px;
    color: #0f172a;
    font-size: 13px;
}
QPushButton {
    background-color: #2563eb;
    color: white;
    border: none;
    border-radius: 10px;
    padding: 9px 12px;
    font-weight: bold;
}
QPushButton#btnClearChat {
    background-color: #e2e8f0;
    color: #0f172a;
}
QTableWidget {
    background-color: white;
    border: 1px solid #dbeafe;
    border-radius: 10px;
    gridline-color: #e2e8f0;
    color: #0f172a;
    font-size: 12px;
}
QHeaderView::section {
    background-color: #1e3a8a;
    color: white;
    padding: 7px;
    border: none;
    font-weight: bold;
}
QLabel#lblCustomerSummary {
    color: #1e3a8a;
    font-size: 18px;
    font-weight: bold;
}
        """)

        self.mainLayout = QtWidgets.QVBoxLayout(CustomerPortalPage)
        self.mainLayout.setContentsMargins(14, 12, 14, 12)
        self.mainLayout.setSpacing(10)

        self.lblCustomerSummary = QtWidgets.QLabel(parent=CustomerPortalPage)
        self.lblCustomerSummary.setObjectName("lblCustomerSummary")
        self.mainLayout.addWidget(self.lblCustomerSummary)

        self.tabs = QtWidgets.QTabWidget(parent=CustomerPortalPage)
        self.tabs.setObjectName("tabs")

        self.productTab = QtWidgets.QWidget()
        self.productLayout = QtWidgets.QVBoxLayout(self.productTab)
        self.productTopLayout = QtWidgets.QHBoxLayout()
        self.txtProductSearch = QtWidgets.QLineEdit(parent=self.productTab)
        self.txtProductSearch.setPlaceholderText("Tìm theo tên máy, hãng, màu, dung lượng")
        self.btnSearchProducts = QtWidgets.QPushButton("Tìm sản phẩm", parent=self.productTab)
        self.btnRefreshProducts = QtWidgets.QPushButton("Làm mới", parent=self.productTab)
        self.productTopLayout.addWidget(self.txtProductSearch)
        self.productTopLayout.addWidget(self.btnSearchProducts)
        self.productTopLayout.addWidget(self.btnRefreshProducts)
        self.productLayout.addLayout(self.productTopLayout)

        self.tableProducts = QtWidgets.QTableWidget(parent=self.productTab)
        self.tableProducts.setColumnCount(6)
        self.tableProducts.setHorizontalHeaderLabels([
            "Sản phẩm", "Hãng", "Phiên bản", "Giá bán", "Tình trạng", "Gợi ý"
        ])
        self.productLayout.addWidget(self.tableProducts)
        self.tabs.addTab(self.productTab, "Sản phẩm đang bán")

        self.historyTab = QtWidgets.QWidget()
        self.historyLayout = QtWidgets.QVBoxLayout(self.historyTab)
        self.btnRefreshHistory = QtWidgets.QPushButton("Làm mới lịch sử", parent=self.historyTab)
        self.historyLayout.addWidget(self.btnRefreshHistory, 0, QtCore.Qt.AlignmentFlag.AlignRight)
        self.tableHistory = QtWidgets.QTableWidget(parent=self.historyTab)
        self.tableHistory.setColumnCount(10)
        self.tableHistory.setHorizontalHeaderLabels([
            "Hóa đơn", "Ngày mua", "Sản phẩm", "Dung lượng", "Màu", "IMEI", "Giá", "BH", "Thanh toán", "Trạng thái"
        ])
        self.historyLayout.addWidget(self.tableHistory)
        self.tabs.addTab(self.historyTab, "Lịch sử mua")

        self.warrantyTab = QtWidgets.QWidget()
        self.warrantyLayout = QtWidgets.QVBoxLayout(self.warrantyTab)
        self.warrantyTopLayout = QtWidgets.QHBoxLayout()
        self.txtWarrantySearch = QtWidgets.QLineEdit(parent=self.warrantyTab)
        self.txtWarrantySearch.setPlaceholderText("Nhập IMEI để lọc bảo hành")
        self.btnSearchWarranty = QtWidgets.QPushButton("Tra cứu", parent=self.warrantyTab)
        self.btnRefreshWarranty = QtWidgets.QPushButton("Làm mới", parent=self.warrantyTab)
        self.warrantyTopLayout.addWidget(self.txtWarrantySearch)
        self.warrantyTopLayout.addWidget(self.btnSearchWarranty)
        self.warrantyTopLayout.addWidget(self.btnRefreshWarranty)
        self.warrantyLayout.addLayout(self.warrantyTopLayout)
        self.tableWarranty = QtWidgets.QTableWidget(parent=self.warrantyTab)
        self.tableWarranty.setColumnCount(12)
        self.tableWarranty.setHorizontalHeaderLabels([
            "Mã phiếu", "Lần", "IMEI", "Sản phẩm", "Ngày mua", "Hạn BH", "Còn lại", "Trạng thái", "Ngày nhận", "Ngày trả", "Lỗi", "Ghi chú"
        ])
        self.warrantyLayout.addWidget(self.tableWarranty)
        self.tabs.addTab(self.warrantyTab, "Bảo hành")

        self.chatTab = QtWidgets.QWidget()
        self.chatLayout = QtWidgets.QVBoxLayout(self.chatTab)
        self.chatScrollArea = QtWidgets.QScrollArea(parent=self.chatTab)
        self.chatScrollArea.setWidgetResizable(True)
        self.chatScrollArea.setObjectName("chatScrollArea")
        self.chatScrollArea.setStyleSheet("""
QScrollArea#chatScrollArea {
    background-color: #f8fafc;
    border: 1px solid #dbeafe;
    border-radius: 12px;
}
QScrollArea#chatScrollArea QWidget {
    background-color: #f8fafc;
}
        """)

        self.chatMessagesWidget = QtWidgets.QWidget(parent=self.chatScrollArea)
        self.chatMessagesLayout = QtWidgets.QVBoxLayout(self.chatMessagesWidget)
        self.chatMessagesLayout.setContentsMargins(14, 12, 14, 12)
        self.chatMessagesLayout.setSpacing(10)
        self.chatMessagesLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.chatScrollArea.setWidget(self.chatMessagesWidget)
        self.chatLayout.addWidget(self.chatScrollArea)
        self.chatInputLayout = QtWidgets.QHBoxLayout()
        self.txtChatInput = QtWidgets.QLineEdit(parent=self.chatTab)
        self.txtChatInput.setPlaceholderText("Hỏi AI về sản phẩm, đơn mua hoặc bảo hành")
        self.btnSendChat = QtWidgets.QPushButton("Gửi AI", parent=self.chatTab)
        self.btnClearChat = QtWidgets.QPushButton("Xóa chat", parent=self.chatTab)
        self.btnClearChat.setObjectName("btnClearChat")
        self.chatInputLayout.addWidget(self.txtChatInput)
        self.chatInputLayout.addWidget(self.btnSendChat)
        self.chatInputLayout.addWidget(self.btnClearChat)
        self.chatLayout.addLayout(self.chatInputLayout)
        self.tabs.addTab(self.chatTab, "AI chat")

        self.mainLayout.addWidget(self.tabs)

        self.lblCustomerSummary.setText("Customer portal")
        QtCore.QMetaObject.connectSlotsByName(CustomerPortalPage)

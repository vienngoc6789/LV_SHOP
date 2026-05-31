from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_DashboardPage(object):
    def setupUi(self, DashboardPage):
        DashboardPage.setObjectName("DashboardPage")
        DashboardPage.resize(1200, 720)
        DashboardPage.setStyleSheet("""
QWidget#DashboardPage {
    background-color: #eff6ff;
}

QFrame#sidebarFrame {
    background-color: #1e3a8a;
}

QLabel#logoLabel {
    color: white;
    font-size: 24px;
    font-weight: bold;
}

QPushButton#btnToggleSidebar {
    background-color: #2563eb;
    color: white;
    border: none;
    border-radius: 10px;
    font-size: 18px;
}

QPushButton#btnToggleSidebar:hover {
    background-color: #3b82f6;
}

QPushButton#btnDashboard,
QPushButton#btnSales,
QPushButton#btnProduct,
QPushButton#btnDiscount,
QPushButton#btnCustomer,
QPushButton#btnInvoice,
QPushButton#btnWarranty,
QPushButton#btnHuman,
QPushButton#btnReport,
QPushButton#btnProfile {
    background-color: transparent;
    color: #dbeafe;
    border: none;
    border-radius: 12px;
    padding: 12px;
    text-align: left;
    font-size: 14px;
    font-weight: bold;
}

QPushButton#btnDashboard:hover,
QPushButton#btnSales:hover,
QPushButton#btnProduct:hover,
QPushButton#btnDiscount:hover,
QPushButton#btnCustomer:hover,
QPushButton#btnInvoice:hover,
QPushButton#btnWarranty:hover,
QPushButton#btnHuman:hover,
QPushButton#btnReport:hover,
QPushButton#btnProfile:hover {
    background-color: #2563eb;
    color: white;
}

QPushButton#btnDashboard:checked,
QPushButton#btnSales:checked,
QPushButton#btnProduct:checked,
QPushButton#btnDiscount:checked,
QPushButton#btnCustomer:checked,
QPushButton#btnInvoice:checked,
QPushButton#btnWarranty:checked,
QPushButton#btnHuman:checked,
QPushButton#btnReport:checked,
QPushButton#btnProfile:checked {
    background-color: #60a5fa;
    color: #0f172a;
}

QPushButton#btnLogout {
    background-color: #ef4444;
    color: white;
    border: none;
    border-radius: 12px;
    padding: 12px;
    text-align: left;
    font-size: 14px;
    font-weight: bold;
}

QPushButton#btnLogout:hover {
    background-color: #dc2626;
}

QFrame#contentFrame {
    background-color: #eff6ff;
}

QFrame#topHeaderFrame {
    background-color: white;
    border-radius: 18px;
    border: 1px solid #dbeafe;
}

QLabel#lblPageTitle {
    color: #1e3a8a;
    font-size: 26px;
    font-weight: bold;
}

QLabel#lblUserName {
    color: #0f172a;
    font-size: 15px;
    font-weight: bold;
}

QLabel#lblUserRole {
    color: #2563eb;
    font-size: 13px;
    font-weight: bold;
}

QStackedWidget#contentStackedWidget {
    background-color: white;
    border-radius: 20px;
    border: 1px solid #dbeafe;
}

QLabel#welcomeTitleLabel {
    color: #1e3a8a;
    font-size: 30px;
    font-weight: bold;
}

QLabel#welcomeSubtitleLabel {
    color: #64748b;
    font-size: 16px;
}
        """)

        self.mainLayout = QtWidgets.QHBoxLayout(DashboardPage)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(0)

        self.sidebarFrame = QtWidgets.QFrame(parent=DashboardPage)
        self.sidebarFrame.setMinimumSize(QtCore.QSize(260, 0))
        self.sidebarFrame.setMaximumSize(QtCore.QSize(260, 16777215))
        self.sidebarFrame.setObjectName("sidebarFrame")

        self.sidebarLayout = QtWidgets.QVBoxLayout(self.sidebarFrame)
        self.sidebarLayout.setContentsMargins(18, 20, 18, 20)
        self.sidebarLayout.setSpacing(12)

        self.sidebarHeaderLayout = QtWidgets.QHBoxLayout()
        self.sidebarHeaderLayout.setSpacing(8)

        self.logoLabel = QtWidgets.QLabel(parent=self.sidebarFrame)
        self.logoLabel.setMinimumSize(QtCore.QSize(0, 54))
        self.logoLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.logoLabel.setObjectName("logoLabel")
        self.sidebarHeaderLayout.addWidget(self.logoLabel)

        spacerItem = QtWidgets.QSpacerItem(
            40, 20,
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Minimum
        )
        self.sidebarHeaderLayout.addItem(spacerItem)

        self.btnToggleSidebar = QtWidgets.QPushButton(parent=self.sidebarFrame)
        self.btnToggleSidebar.setMinimumSize(QtCore.QSize(38, 38))
        self.btnToggleSidebar.setMaximumSize(QtCore.QSize(38, 38))
        self.btnToggleSidebar.setObjectName("btnToggleSidebar")
        self.sidebarHeaderLayout.addWidget(self.btnToggleSidebar)

        self.sidebarLayout.addLayout(self.sidebarHeaderLayout)

        self.menuLayout = QtWidgets.QVBoxLayout()
        self.menuLayout.setSpacing(8)

        self.btnDashboard = QtWidgets.QPushButton(parent=self.sidebarFrame)
        self.btnDashboard.setCheckable(True)
        self.btnDashboard.setObjectName("btnDashboard")
        self.menuLayout.addWidget(self.btnDashboard)

        self.btnSales = QtWidgets.QPushButton(parent=self.sidebarFrame)
        self.btnSales.setCheckable(True)
        self.btnSales.setObjectName("btnSales")
        self.menuLayout.addWidget(self.btnSales)

        self.btnProduct = QtWidgets.QPushButton(parent=self.sidebarFrame)
        self.btnProduct.setCheckable(True)
        self.btnProduct.setObjectName("btnProduct")
        self.menuLayout.addWidget(self.btnProduct)

        self.btnDiscount = QtWidgets.QPushButton(parent=self.sidebarFrame)
        self.btnDiscount.setCheckable(True)
        self.btnDiscount.setObjectName("btnDiscount")
        self.menuLayout.addWidget(self.btnDiscount)

        self.btnCustomer = QtWidgets.QPushButton(parent=self.sidebarFrame)
        self.btnCustomer.setCheckable(True)
        self.btnCustomer.setObjectName("btnCustomer")
        self.menuLayout.addWidget(self.btnCustomer)

        self.btnInvoice = QtWidgets.QPushButton(parent=self.sidebarFrame)
        self.btnInvoice.setCheckable(True)
        self.btnInvoice.setObjectName("btnInvoice")
        self.menuLayout.addWidget(self.btnInvoice)

        self.btnWarranty = QtWidgets.QPushButton(parent=self.sidebarFrame)
        self.btnWarranty.setCheckable(True)
        self.btnWarranty.setObjectName("btnWarranty")
        self.menuLayout.addWidget(self.btnWarranty)

        self.btnHuman = QtWidgets.QPushButton(parent=self.sidebarFrame)
        self.btnHuman.setCheckable(True)
        self.btnHuman.setObjectName("btnHuman")
        self.menuLayout.addWidget(self.btnHuman)

        self.btnReport = QtWidgets.QPushButton(parent=self.sidebarFrame)
        self.btnReport.setCheckable(True)
        self.btnReport.setObjectName("btnReport")
        self.menuLayout.addWidget(self.btnReport)

        self.btnProfile = QtWidgets.QPushButton(parent=self.sidebarFrame)
        self.btnProfile.setCheckable(True)
        self.btnProfile.setObjectName("btnProfile")
        self.menuLayout.addWidget(self.btnProfile)

        self.sidebarLayout.addLayout(self.menuLayout)

        spacerItem1 = QtWidgets.QSpacerItem(
            20, 40,
            QtWidgets.QSizePolicy.Policy.Minimum,
            QtWidgets.QSizePolicy.Policy.Expanding
        )
        self.sidebarLayout.addItem(spacerItem1)

        self.btnLogout = QtWidgets.QPushButton(parent=self.sidebarFrame)
        self.btnLogout.setMinimumSize(QtCore.QSize(0, 46))
        self.btnLogout.setObjectName("btnLogout")
        self.sidebarLayout.addWidget(self.btnLogout)

        self.mainLayout.addWidget(self.sidebarFrame)

        self.contentFrame = QtWidgets.QFrame(parent=DashboardPage)
        self.contentFrame.setObjectName("contentFrame")

        self.contentLayout = QtWidgets.QVBoxLayout(self.contentFrame)
        self.contentLayout.setContentsMargins(24, 24, 24, 24)
        self.contentLayout.setSpacing(18)

        self.topHeaderFrame = QtWidgets.QFrame(parent=self.contentFrame)
        self.topHeaderFrame.setMinimumSize(QtCore.QSize(0, 78))
        self.topHeaderFrame.setMaximumSize(QtCore.QSize(16777215, 90))
        self.topHeaderFrame.setObjectName("topHeaderFrame")

        self.topHeaderLayout = QtWidgets.QHBoxLayout(self.topHeaderFrame)
        self.topHeaderLayout.setContentsMargins(24, 12, 24, 12)

        self.lblPageTitle = QtWidgets.QLabel(parent=self.topHeaderFrame)
        self.lblPageTitle.setObjectName("lblPageTitle")
        self.topHeaderLayout.addWidget(self.lblPageTitle)

        spacerItem2 = QtWidgets.QSpacerItem(
            40, 20,
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Minimum
        )
        self.topHeaderLayout.addItem(spacerItem2)

        self.userInfoLayout = QtWidgets.QVBoxLayout()
        self.userInfoLayout.setSpacing(2)

        self.lblUserName = QtWidgets.QLabel(parent=self.topHeaderFrame)
        self.lblUserName.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignRight |
            QtCore.Qt.AlignmentFlag.AlignTrailing |
            QtCore.Qt.AlignmentFlag.AlignVCenter
        )
        self.lblUserName.setObjectName("lblUserName")
        self.userInfoLayout.addWidget(self.lblUserName)

        self.lblUserRole = QtWidgets.QLabel(parent=self.topHeaderFrame)
        self.lblUserRole.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignRight |
            QtCore.Qt.AlignmentFlag.AlignTrailing |
            QtCore.Qt.AlignmentFlag.AlignVCenter
        )
        self.lblUserRole.setObjectName("lblUserRole")
        self.userInfoLayout.addWidget(self.lblUserRole)

        self.topHeaderLayout.addLayout(self.userInfoLayout)
        self.contentLayout.addWidget(self.topHeaderFrame)

        self.contentStackedWidget = QtWidgets.QStackedWidget(parent=self.contentFrame)
        self.contentStackedWidget.setObjectName("contentStackedWidget")

        self.pageWelcome = QtWidgets.QWidget()
        self.pageWelcome.setObjectName("pageWelcome")

        self.welcomeLayout = QtWidgets.QVBoxLayout(self.pageWelcome)

        spacerItem3 = QtWidgets.QSpacerItem(
            20, 40,
            QtWidgets.QSizePolicy.Policy.Minimum,
            QtWidgets.QSizePolicy.Policy.Expanding
        )
        self.welcomeLayout.addItem(spacerItem3)

        self.welcomeTitleLabel = QtWidgets.QLabel(parent=self.pageWelcome)
        self.welcomeTitleLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.welcomeTitleLabel.setObjectName("welcomeTitleLabel")
        self.welcomeLayout.addWidget(self.welcomeTitleLabel)

        self.welcomeSubtitleLabel = QtWidgets.QLabel(parent=self.pageWelcome)
        self.welcomeSubtitleLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.welcomeSubtitleLabel.setObjectName("welcomeSubtitleLabel")
        self.welcomeLayout.addWidget(self.welcomeSubtitleLabel)

        spacerItem4 = QtWidgets.QSpacerItem(
            20, 40,
            QtWidgets.QSizePolicy.Policy.Minimum,
            QtWidgets.QSizePolicy.Policy.Expanding
        )
        self.welcomeLayout.addItem(spacerItem4)

        self.contentStackedWidget.addWidget(self.pageWelcome)
        self.contentLayout.addWidget(self.contentStackedWidget)

        self.mainLayout.addWidget(self.contentFrame)

        self.retranslateUi(DashboardPage)
        self.contentStackedWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(DashboardPage)

    def retranslateUi(self, DashboardPage):
        _translate = QtCore.QCoreApplication.translate
        self.logoLabel.setText(_translate("DashboardPage", "LV SHOP"))
        self.btnToggleSidebar.setText(_translate("DashboardPage", "‹"))
        self.btnDashboard.setText(_translate("DashboardPage", "📊  Trang chủ"))
        self.btnSales.setText(_translate("DashboardPage", "🛒  Bán hàng"))
        self.btnProduct.setText(_translate("DashboardPage", "📦  Sản phẩm & Kho"))
        self.btnDiscount.setText(_translate("DashboardPage", "🎁  Mã giảm giá"))
        self.btnCustomer.setText(_translate("DashboardPage", "👥  Khách hàng"))
        self.btnInvoice.setText(_translate("DashboardPage", "🧾  Hóa đơn"))
        self.btnWarranty.setText(_translate("DashboardPage", "🛠  Bảo hành"))
        self.btnHuman.setText(_translate("DashboardPage", "👨‍💼  Nhân sự"))
        self.btnReport.setText(_translate("DashboardPage", "📈  Báo cáo"))
        self.btnProfile.setText(_translate("DashboardPage", "👤  Tài khoản"))
        self.btnLogout.setText(_translate("DashboardPage", "🚪  Đăng xuất"))
        self.lblPageTitle.setText(_translate("DashboardPage", "Trang chủ"))
        self.lblUserName.setText(_translate("DashboardPage", "Nguyễn Văn A"))
        self.lblUserRole.setText(_translate("DashboardPage", "Admin"))
        self.welcomeTitleLabel.setText(
            _translate("DashboardPage", "Chào mừng đến với hệ thống quản lý")
        )
        self.welcomeSubtitleLabel.setText(
            _translate("DashboardPage", "Vui lòng chọn chức năng ở menu bên trái")
        )
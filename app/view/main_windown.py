from PyQt6 import QtCore, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1000, 650)

        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.centralwidget.setStyleSheet("""
QWidget#centralwidget {
    background-color: #eff6ff;
}

QFrame#heroCard {
    background-color: white;
    border-radius: 26px;
    border: 1px solid #dbeafe;
}

QLabel#lblLogo {
    color: #2563eb;
    font-size: 46px;
    font-weight: bold;
}

QLabel#lblTitle {
    color: #1e3a8a;
    font-size: 34px;
    font-weight: bold;
}

QLabel#lblSubtitle {
    color: #475569;
    font-size: 16px;
}

QLabel#lblDescription {
    color: #64748b;
    font-size: 14px;
}

QPushButton#btnOpenLogin {
    background-color: #2563eb;
    color: white;
    border: none;
    border-radius: 14px;
    padding: 13px;
    font-size: 15px;
    font-weight: bold;
}

QPushButton#btnOpenLogin:hover {
    background-color: #1d4ed8;
}

QPushButton#btnOpenRegister {
    background-color: white;
    color: #2563eb;
    border: 2px solid #2563eb;
    border-radius: 14px;
    padding: 13px;
    font-size: 15px;
    font-weight: bold;
}

QPushButton#btnOpenRegister:hover {
    background-color: #dbeafe;
}
        """)

        self.mainLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.mainLayout.setObjectName("mainLayout")

        self.mainLayout.addItem(
            QtWidgets.QSpacerItem(
                20, 40,
                QtWidgets.QSizePolicy.Policy.Minimum,
                QtWidgets.QSizePolicy.Policy.Expanding
            )
        )

        self.centerLayout = QtWidgets.QHBoxLayout()
        self.centerLayout.setObjectName("centerLayout")

        self.centerLayout.addItem(
            QtWidgets.QSpacerItem(
                40, 20,
                QtWidgets.QSizePolicy.Policy.Expanding,
                QtWidgets.QSizePolicy.Policy.Minimum
            )
        )

        self.heroCard = QtWidgets.QFrame(parent=self.centralwidget)
        self.heroCard.setObjectName("heroCard")
        self.heroCard.setMinimumSize(QtCore.QSize(760, 460))
        self.heroCard.setMaximumSize(QtCore.QSize(820, 500))

        self.heroLayout = QtWidgets.QVBoxLayout(self.heroCard)
        self.heroLayout.setObjectName("heroLayout")
        self.heroLayout.setContentsMargins(50, 42, 50, 42)
        self.heroLayout.setSpacing(18)

        self.lblLogo = QtWidgets.QLabel(parent=self.heroCard)
        self.lblLogo.setObjectName("lblLogo")
        self.lblLogo.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.lblTitle = QtWidgets.QLabel(parent=self.heroCard)
        self.lblTitle.setObjectName("lblTitle")
        self.lblTitle.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.lblTitle.setWordWrap(True)

        self.lblSubtitle = QtWidgets.QLabel(parent=self.heroCard)
        self.lblSubtitle.setObjectName("lblSubtitle")
        self.lblSubtitle.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.lblSubtitle.setWordWrap(True)

        self.lblDescription = QtWidgets.QLabel(parent=self.heroCard)
        self.lblDescription.setObjectName("lblDescription")
        self.lblDescription.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.lblDescription.setWordWrap(True)

        self.heroLayout.addWidget(self.lblLogo)
        self.heroLayout.addWidget(self.lblTitle)
        self.heroLayout.addWidget(self.lblSubtitle)
        self.heroLayout.addWidget(self.lblDescription)

        self.heroLayout.addItem(
            QtWidgets.QSpacerItem(
                20, 40,
                QtWidgets.QSizePolicy.Policy.Minimum,
                QtWidgets.QSizePolicy.Policy.Expanding
            )
        )

        self.buttonLayout = QtWidgets.QHBoxLayout()
        self.buttonLayout.setObjectName("buttonLayout")

        self.buttonLayout.addItem(
            QtWidgets.QSpacerItem(
                40, 20,
                QtWidgets.QSizePolicy.Policy.Expanding,
                QtWidgets.QSizePolicy.Policy.Minimum
            )
        )

        self.btnOpenLogin = QtWidgets.QPushButton(parent=self.heroCard)
        self.btnOpenLogin.setObjectName("btnOpenLogin")
        self.btnOpenLogin.setMinimumSize(QtCore.QSize(180, 48))

        self.btnOpenRegister = QtWidgets.QPushButton(parent=self.heroCard)
        self.btnOpenRegister.setObjectName("btnOpenRegister")
        self.btnOpenRegister.setMinimumSize(QtCore.QSize(180, 48))

        self.buttonLayout.addWidget(self.btnOpenLogin)
        self.buttonLayout.addWidget(self.btnOpenRegister)

        self.buttonLayout.addItem(
            QtWidgets.QSpacerItem(
                40, 20,
                QtWidgets.QSizePolicy.Policy.Expanding,
                QtWidgets.QSizePolicy.Policy.Minimum
            )
        )

        self.heroLayout.addLayout(self.buttonLayout)

        self.centerLayout.addWidget(self.heroCard)

        self.centerLayout.addItem(
            QtWidgets.QSpacerItem(
                40, 20,
                QtWidgets.QSizePolicy.Policy.Expanding,
                QtWidgets.QSizePolicy.Policy.Minimum
            )
        )

        self.mainLayout.addLayout(self.centerLayout)

        self.mainLayout.addItem(
            QtWidgets.QSpacerItem(
                20, 40,
                QtWidgets.QSizePolicy.Policy.Minimum,
                QtWidgets.QSizePolicy.Policy.Expanding
            )
        )

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate

        MainWindow.setWindowTitle(_translate("MainWindow", "LV SHOP"))
        self.lblLogo.setText(_translate("MainWindow", "LV SHOP"))
        self.lblTitle.setText(_translate("MainWindow", "Hệ thống quản lý cửa hàng điện thoại"))
        self.lblSubtitle.setText(_translate("MainWindow", "Quản lý sản phẩm, nhân viên, khách hàng và đơn hàng dễ dàng hơn"))
        self.lblDescription.setText(_translate("MainWindow", "LV SHOP hỗ trợ quản lý thông tin điện thoại, tồn kho, tài khoản nhân viên, lịch sử bán hàng và thống kê doanh thu trong một giao diện desktop hiện đại."))
        self.btnOpenLogin.setText(_translate("MainWindow", "Đăng nhập"))
        self.btnOpenRegister.setText(_translate("MainWindow", "Đăng ký"))
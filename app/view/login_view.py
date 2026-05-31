from PyQt6 import QtCore, QtWidgets


class Ui_LoginPage(object):
    def setupUi(self, LoginPage):
        LoginPage.setObjectName("LoginPage")
        LoginPage.resize(900, 600)

        LoginPage.setStyleSheet("""
QWidget#LoginPage {
    background-color: #eff6ff;
}

QFrame#loginCard {
    background-color: white;
    border-radius: 24px;
    border: 1px solid #bfdbfe;
}

QLabel#lblTitle {
    color: #1e3a8a;
    font-size: 34px;
    font-weight: bold;
}

QLabel#lblSubtitle {
    color: #64748b;
    font-size: 16px;
}

QLabel.formLabel {
    color: #334155;
    font-size: 14px;
    font-weight: bold;
}

QFrame.inputBox {
    background-color: #f8fafc;
    border: 1px solid #cbd5e1;
    border-radius: 14px;
}

QFrame.inputBox:focus-within {
    border: 2px solid #2563eb;
    background-color: white;
}

QLabel.inputIcon {
    color: #2563eb;
    font-size: 18px;
}

QLineEdit {
    background-color: transparent;
    border: none;
    color: #0f172a;
    font-size: 15px;
    padding: 8px;
    selection-background-color: #2563eb;
    selection-color: white;
}

QLineEdit::placeholder {
    color: #94a3b8;
}

QCheckBox {
    color: #334155;
    font-size: 14px;
}

QPushButton#btnLogin {
    background-color: #2563eb;
    color: white;
    border: none;
    border-radius: 14px;
    padding: 13px;
    font-size: 16px;
    font-weight: bold;
}

QPushButton#btnLogin:hover {
    background-color: #1d4ed8;
}

QPushButton#btnLogin:pressed {
    background-color: #1e40af;
}

QPushButton#btnShowPassword {
    background-color: transparent;
    border: none;
    color: #2563eb;
    font-size: 18px;
}

QPushButton#btnForgotPassword,
QPushButton#btnGoRegister {
    background-color: transparent;
    border: none;
    color: #2563eb;
    font-size: 14px;
    font-weight: bold;
}

QPushButton#btnForgotPassword:hover,
QPushButton#btnGoRegister:hover {
    color: #1d4ed8;
    text-decoration: underline;
}
        """)

        self.mainLayout = QtWidgets.QVBoxLayout(LoginPage)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)

        self.mainLayout.addItem(
            QtWidgets.QSpacerItem(
                20, 40,
                QtWidgets.QSizePolicy.Policy.Minimum,
                QtWidgets.QSizePolicy.Policy.Expanding
            )
        )

        self.centerLayout = QtWidgets.QHBoxLayout()

        self.centerLayout.addItem(
            QtWidgets.QSpacerItem(
                40, 20,
                QtWidgets.QSizePolicy.Policy.Expanding,
                QtWidgets.QSizePolicy.Policy.Minimum
            )
        )

        self.loginCard = QtWidgets.QFrame(parent=LoginPage)
        self.loginCard.setObjectName("loginCard")
        self.loginCard.setMinimumSize(QtCore.QSize(520, 580))
        self.loginCard.setMaximumSize(QtCore.QSize(560, 620))

        self.cardLayout = QtWidgets.QVBoxLayout(self.loginCard)
        self.cardLayout.setContentsMargins(48, 42, 48, 42)
        self.cardLayout.setSpacing(14)

        self.lblTitle = QtWidgets.QLabel(parent=self.loginCard)
        self.lblTitle.setObjectName("lblTitle")
        self.lblTitle.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.cardLayout.addWidget(self.lblTitle)

        self.lblSubtitle = QtWidgets.QLabel(parent=self.loginCard)
        self.lblSubtitle.setObjectName("lblSubtitle")
        self.lblSubtitle.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.cardLayout.addWidget(self.lblSubtitle)

        self.cardLayout.addItem(
            QtWidgets.QSpacerItem(
                20, 28,
                QtWidgets.QSizePolicy.Policy.Minimum,
                QtWidgets.QSizePolicy.Policy.Fixed
            )
        )

        self.lblUsername = QtWidgets.QLabel(parent=self.loginCard)
        self.lblUsername.setText("Tài khoản")
        self.lblUsername.setProperty("class", "formLabel")
        self.cardLayout.addWidget(self.lblUsername)

        self.usernameBox = QtWidgets.QFrame(parent=self.loginCard)
        self.usernameBox.setProperty("class", "inputBox")
        self.usernameBox.setMinimumHeight(54)

        self.usernameLayout = QtWidgets.QHBoxLayout(self.usernameBox)
        self.usernameLayout.setContentsMargins(16, 4, 12, 4)
        self.usernameLayout.setSpacing(8)

        self.iconUser = QtWidgets.QLabel(parent=self.usernameBox)
        self.iconUser.setText("👤")
        self.iconUser.setProperty("class", "inputIcon")
        self.usernameLayout.addWidget(self.iconUser)

        self.txtUsername = QtWidgets.QLineEdit(parent=self.usernameBox)
        self.txtUsername.setObjectName("txtUsername")
        self.txtUsername.setPlaceholderText("Nhập tài khoản hoặc email")
        self.txtUsername.setClearButtonEnabled(True)
        self.usernameLayout.addWidget(self.txtUsername)

        self.cardLayout.addWidget(self.usernameBox)

        self.lblPassword = QtWidgets.QLabel(parent=self.loginCard)
        self.lblPassword.setText("Mật khẩu")
        self.lblPassword.setProperty("class", "formLabel")
        self.cardLayout.addWidget(self.lblPassword)

        self.passwordBox = QtWidgets.QFrame(parent=self.loginCard)
        self.passwordBox.setProperty("class", "inputBox")
        self.passwordBox.setMinimumHeight(54)

        self.passwordLayout = QtWidgets.QHBoxLayout(self.passwordBox)
        self.passwordLayout.setContentsMargins(16, 4, 8, 4)
        self.passwordLayout.setSpacing(8)

        self.iconLock = QtWidgets.QLabel(parent=self.passwordBox)
        self.iconLock.setText("🔒")
        self.iconLock.setProperty("class", "inputIcon")
        self.passwordLayout.addWidget(self.iconLock)

        self.txtPassword = QtWidgets.QLineEdit(parent=self.passwordBox)
        self.txtPassword.setObjectName("txtPassword")
        self.txtPassword.setPlaceholderText("Nhập mật khẩu")
        self.txtPassword.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.txtPassword.setClearButtonEnabled(True)
        self.passwordLayout.addWidget(self.txtPassword)

        self.btnShowPassword = QtWidgets.QPushButton(parent=self.passwordBox)
        self.btnShowPassword.setObjectName("btnShowPassword")
        self.btnShowPassword.setText("👁")
        self.btnShowPassword.setMinimumSize(QtCore.QSize(42, 42))
        self.btnShowPassword.setMaximumSize(QtCore.QSize(42, 42))
        self.passwordLayout.addWidget(self.btnShowPassword)

        self.cardLayout.addWidget(self.passwordBox)

        self.optionLayout = QtWidgets.QHBoxLayout()

        self.chkRemember = QtWidgets.QCheckBox(parent=self.loginCard)
        self.chkRemember.setObjectName("chkRemember")
        self.optionLayout.addWidget(self.chkRemember)

        self.optionLayout.addItem(
            QtWidgets.QSpacerItem(
                40, 20,
                QtWidgets.QSizePolicy.Policy.Expanding,
                QtWidgets.QSizePolicy.Policy.Minimum
            )
        )

        self.btnForgotPassword = QtWidgets.QPushButton(parent=self.loginCard)
        self.btnForgotPassword.setObjectName("btnForgotPassword")
        self.optionLayout.addWidget(self.btnForgotPassword)

        self.cardLayout.addLayout(self.optionLayout)

        self.btnLogin = QtWidgets.QPushButton(parent=self.loginCard)
        self.btnLogin.setObjectName("btnLogin")
        self.btnLogin.setMinimumHeight(54)
        self.cardLayout.addWidget(self.btnLogin)

        self.cardLayout.addItem(
            QtWidgets.QSpacerItem(
                20, 24,
                QtWidgets.QSizePolicy.Policy.Minimum,
                QtWidgets.QSizePolicy.Policy.Expanding
            )
        )

        self.btnGoRegister = QtWidgets.QPushButton(parent=self.loginCard)
        self.btnGoRegister.setObjectName("btnGoRegister")
        self.cardLayout.addWidget(self.btnGoRegister)

        self.centerLayout.addWidget(self.loginCard)

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

        self.retranslateUi(LoginPage)
        QtCore.QMetaObject.connectSlotsByName(LoginPage)

    def retranslateUi(self, LoginPage):
        _translate = QtCore.QCoreApplication.translate

        self.lblTitle.setText(_translate("LoginPage", "Đăng nhập"))
        self.lblSubtitle.setText(_translate("LoginPage", "Chào mừng bạn quay trở lại"))
        self.chkRemember.setText(_translate("LoginPage", "Ghi nhớ đăng nhập"))
        self.btnForgotPassword.setText(_translate("LoginPage", "Quên mật khẩu?"))
        self.btnLogin.setText(_translate("LoginPage", "Đăng nhập"))
        self.btnGoRegister.setText(_translate("LoginPage", "Chưa có tài khoản? Đăng ký ngay"))
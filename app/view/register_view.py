from PyQt6 import QtCore, QtWidgets


class Ui_RegisterPage(object):
    def setupUi(self, RegisterPage):
        RegisterPage.setObjectName("RegisterPage")
        RegisterPage.resize(980, 720)

        RegisterPage.setStyleSheet("""
QWidget#RegisterPage {
    background-color: #eff6ff;
}

QFrame#registerCard {
    background-color: white;
    border-radius: 24px;
    border: 1px solid #bfdbfe;
}

QLabel#lblTitle {
    color: #1e3a8a;
    font-size: 30px;
    font-weight: bold;
}

QLabel#lblSubtitle {
    color: #64748b;
    font-size: 14px;
}

QLabel.formLabel {
    color: #334155;
    font-size: 13px;
    font-weight: bold;
}

QFrame.inputBox {
    background-color: #f8fafc;
    border: 1px solid #cbd5e1;
    border-radius: 12px;
}

QLabel.inputIcon {
    color: #2563eb;
    font-size: 17px;
}

QLineEdit, QDateEdit, QComboBox {
    background-color: transparent;
    border: none;
    color: #0f172a;
    font-size: 14px;
    padding: 8px;
}

QLineEdit:read-only {
    color: #64748b;
}

QLineEdit::placeholder {
    color: #94a3b8;
}

QRadioButton {
    color: #334155;
    font-size: 14px;
}

QPushButton#btnRegister {
    background-color: #2563eb;
    color: white;
    border: none;
    border-radius: 14px;
    padding: 13px;
    font-size: 15px;
    font-weight: bold;
}

QPushButton#btnRegister:hover {
    background-color: #1d4ed8;
}

QPushButton#btnBackLogin {
    background-color: transparent;
    color: #2563eb;
    border: none;
    font-size: 14px;
    font-weight: bold;
}

QPushButton#btnShowPassword,
QPushButton#btnShowConfirmPassword {
    background-color: transparent;
    border: none;
    color: #2563eb;
    font-size: 18px;
}
        """)

        self.mainLayout = QtWidgets.QVBoxLayout(RegisterPage)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)

        self.mainLayout.addItem(
            QtWidgets.QSpacerItem(
                20, 20,
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

        self.registerCard = QtWidgets.QFrame(parent=RegisterPage)
        self.registerCard.setObjectName("registerCard")
        self.registerCard.setMinimumSize(QtCore.QSize(780, 660))
        self.registerCard.setMaximumSize(QtCore.QSize(860, 700))

        self.cardLayout = QtWidgets.QVBoxLayout(self.registerCard)
        self.cardLayout.setContentsMargins(36, 28, 36, 28)
        self.cardLayout.setSpacing(12)

        self.lblTitle = QtWidgets.QLabel(parent=self.registerCard)
        self.lblTitle.setObjectName("lblTitle")
        self.lblTitle.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.cardLayout.addWidget(self.lblTitle)

        self.lblSubtitle = QtWidgets.QLabel(parent=self.registerCard)
        self.lblSubtitle.setObjectName("lblSubtitle")
        self.lblSubtitle.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.cardLayout.addWidget(self.lblSubtitle)

        self.formGrid = QtWidgets.QGridLayout()
        self.formGrid.setHorizontalSpacing(18)
        self.formGrid.setVerticalSpacing(8)

        self.lblFullName = self.create_label("Họ và tên")
        self.fullNameBox = self.create_input("👤", "txtFullName", "Nhập họ và tên")
        self.formGrid.addWidget(self.lblFullName, 0, 0)
        self.formGrid.addWidget(self.fullNameBox, 1, 0)

        self.lblBirth = self.create_label("Ngày tháng năm sinh")
        self.dateBirthBox = QtWidgets.QFrame(parent=self.registerCard)
        self.dateBirthBox.setProperty("class", "inputBox")
        self.dateBirthBox.setMinimumHeight(46)

        dateLayout = QtWidgets.QHBoxLayout(self.dateBirthBox)
        dateLayout.setContentsMargins(14, 3, 10, 3)
        dateLayout.setSpacing(8)

        self.iconBirth = QtWidgets.QLabel("📅", parent=self.dateBirthBox)
        self.iconBirth.setProperty("class", "inputIcon")
        dateLayout.addWidget(self.iconBirth)

        self.dateBirth = QtWidgets.QDateEdit(parent=self.dateBirthBox)
        self.dateBirth.setObjectName("dateBirth")
        self.dateBirth.setCalendarPopup(True)
        self.dateBirth.setDisplayFormat("dd/MM/yyyy")
        self.dateBirth.setDate(QtCore.QDate.currentDate())
        dateLayout.addWidget(self.dateBirth)

        self.formGrid.addWidget(self.lblBirth, 0, 1)
        self.formGrid.addWidget(self.dateBirthBox, 1, 1)

        self.lblGender = self.create_label("Giới tính")
        self.genderBox = QtWidgets.QFrame(parent=self.registerCard)
        self.genderBox.setProperty("class", "inputBox")
        self.genderBox.setMinimumHeight(46)

        genderLayout = QtWidgets.QHBoxLayout(self.genderBox)
        genderLayout.setContentsMargins(14, 3, 10, 3)
        genderLayout.setSpacing(18)

        self.radioMale = QtWidgets.QRadioButton("Nam", parent=self.genderBox)
        self.radioMale.setObjectName("radioMale")
        self.radioMale.setChecked(True)

        self.radioFemale = QtWidgets.QRadioButton("Nữ", parent=self.genderBox)
        self.radioFemale.setObjectName("radioFemale")

        genderLayout.addWidget(self.radioMale)
        genderLayout.addWidget(self.radioFemale)
        genderLayout.addStretch()

        self.formGrid.addWidget(self.lblGender, 2, 0)
        self.formGrid.addWidget(self.genderBox, 3, 0)

        self.lblRole = self.create_label("Vai trò")
        self.roleBox = QtWidgets.QFrame(parent=self.registerCard)
        self.roleBox.setProperty("class", "inputBox")
        self.roleBox.setMinimumHeight(46)

        roleLayout = QtWidgets.QHBoxLayout(self.roleBox)
        roleLayout.setContentsMargins(14, 3, 10, 3)
        roleLayout.setSpacing(8)

        self.iconRole = QtWidgets.QLabel("💼", parent=self.roleBox)
        self.iconRole.setProperty("class", "inputIcon")
        roleLayout.addWidget(self.iconRole)

        self.cboRole = QtWidgets.QComboBox(parent=self.roleBox)
        self.cboRole.setObjectName("cboRole")
        self.cboRole.addItems(["Khách hàng"])
        self.cboRole.setEnabled(False)
        roleLayout.addWidget(self.cboRole)

        self.formGrid.addWidget(self.lblRole, 2, 1)
        self.formGrid.addWidget(self.roleBox, 3, 1)

        self.lblPhone = self.create_label("Số điện thoại")
        self.phoneBox = self.create_input("📞", "txtPhone", "Nhập số điện thoại")
        self.formGrid.addWidget(self.lblPhone, 4, 0)
        self.formGrid.addWidget(self.phoneBox, 5, 0)

        self.lblEmail = self.create_label("Gmail")
        self.emailBox = self.create_input("✉", "txtEmail", "example@gmail.com")
        self.formGrid.addWidget(self.lblEmail, 4, 1)
        self.formGrid.addWidget(self.emailBox, 5, 1)

        self.lblAddress = self.create_label("Địa chỉ")
        self.addressBox = self.create_input("📍", "txtAddress", "Nhập địa chỉ hiện tại")
        self.formGrid.addWidget(self.lblAddress, 6, 0, 1, 2)
        self.formGrid.addWidget(self.addressBox, 7, 0, 1, 2)

        self.lblUsername = self.create_label("Tài khoản")
        self.usernameBox = self.create_input("👤", "txtUsername", "Tên đăng nhập")
        self.formGrid.addWidget(self.lblUsername, 8, 0)
        self.formGrid.addWidget(self.usernameBox, 9, 0)

        self.lblEmployeeCode = self.create_label("Mã khách hàng")
        self.employeeCodeBox = self.create_input("🆔", "txtEmployeeCode", "Hệ thống tự động tạo")
        self.txtEmployeeCode.setReadOnly(True)
        self.txtEmployeeCode.setText("Tự động sau khi đăng ký")
        self.formGrid.addWidget(self.lblEmployeeCode, 8, 1)
        self.formGrid.addWidget(self.employeeCodeBox, 9, 1)

        self.lblPassword = self.create_label("Mật khẩu")
        self.passwordBox = self.create_password_box(
            "txtPassword",
            "Ít nhất 8 ký tự, có chữ hoa và số",
            "btnShowPassword"
        )
        self.formGrid.addWidget(self.lblPassword, 10, 0)
        self.formGrid.addWidget(self.passwordBox, 11, 0)

        self.lblConfirmPassword = self.create_label("Xác nhận mật khẩu")
        self.confirmPasswordBox = self.create_password_box(
            "txtConfirmPassword",
            "Nhập lại mật khẩu",
            "btnShowConfirmPassword"
        )
        self.formGrid.addWidget(self.lblConfirmPassword, 10, 1)
        self.formGrid.addWidget(self.confirmPasswordBox, 11, 1)

        self.cardLayout.addLayout(self.formGrid)

        self.btnRegister = QtWidgets.QPushButton(parent=self.registerCard)
        self.btnRegister.setObjectName("btnRegister")
        self.btnRegister.setMinimumHeight(48)
        self.cardLayout.addWidget(self.btnRegister)

        self.btnBackLogin = QtWidgets.QPushButton(parent=self.registerCard)
        self.btnBackLogin.setObjectName("btnBackLogin")
        self.cardLayout.addWidget(self.btnBackLogin)

        self.centerLayout.addWidget(self.registerCard)
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
                20, 20,
                QtWidgets.QSizePolicy.Policy.Minimum,
                QtWidgets.QSizePolicy.Policy.Expanding
            )
        )

        self.retranslateUi(RegisterPage)
        QtCore.QMetaObject.connectSlotsByName(RegisterPage)

    def create_label(self, text):
        label = QtWidgets.QLabel(parent=self.registerCard)
        label.setText(text)
        label.setProperty("class", "formLabel")
        return label

    def create_input(self, icon, object_name, placeholder):
        box = QtWidgets.QFrame(parent=self.registerCard)
        box.setProperty("class", "inputBox")
        box.setMinimumHeight(46)

        layout = QtWidgets.QHBoxLayout(box)
        layout.setContentsMargins(14, 3, 10, 3)
        layout.setSpacing(8)

        iconLabel = QtWidgets.QLabel(icon, parent=box)
        iconLabel.setProperty("class", "inputIcon")
        layout.addWidget(iconLabel)

        lineEdit = QtWidgets.QLineEdit(parent=box)
        lineEdit.setObjectName(object_name)
        lineEdit.setPlaceholderText(placeholder)
        lineEdit.setClearButtonEnabled(True)

        layout.addWidget(lineEdit)

        setattr(self, object_name, lineEdit)

        return box

    def create_password_box(self, object_name, placeholder, button_name):
        box = QtWidgets.QFrame(parent=self.registerCard)
        box.setProperty("class", "inputBox")
        box.setMinimumHeight(46)

        layout = QtWidgets.QHBoxLayout(box)
        layout.setContentsMargins(14, 3, 6, 3)
        layout.setSpacing(8)

        iconLabel = QtWidgets.QLabel("🔒", parent=box)
        iconLabel.setProperty("class", "inputIcon")
        layout.addWidget(iconLabel)

        lineEdit = QtWidgets.QLineEdit(parent=box)
        lineEdit.setObjectName(object_name)
        lineEdit.setPlaceholderText(placeholder)
        lineEdit.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        lineEdit.setClearButtonEnabled(True)
        layout.addWidget(lineEdit)

        button = QtWidgets.QPushButton(parent=box)
        button.setObjectName(button_name)
        button.setText("👁")
        button.setMinimumSize(QtCore.QSize(38, 38))
        button.setMaximumSize(QtCore.QSize(38, 38))
        layout.addWidget(button)

        setattr(self, object_name, lineEdit)
        setattr(self, button_name, button)

        return box

    def retranslateUi(self, RegisterPage):
        _translate = QtCore.QCoreApplication.translate

        self.lblTitle.setText(_translate("RegisterPage", "Tạo tài khoản khách hàng"))
        self.lblSubtitle.setText(_translate("RegisterPage", "Nhập đầy đủ thông tin để tạo hồ sơ khách hàng"))
        self.btnRegister.setText(_translate("RegisterPage", "Tạo tài khoản khách hàng"))
        self.btnBackLogin.setText(_translate("RegisterPage", "Đã có tài khoản? Quay lại đăng nhập"))

from PyQt6.QtWidgets import QMainWindow, QWidget, QStackedWidget

from app.view.main_windown import Ui_MainWindow
from app.view.login_view import Ui_LoginPage
from app.view.register_view import Ui_RegisterPage
from app.view.dashboard_view import Ui_DashboardPage


class AppWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("LV SHOP")
        self.resize(1200, 720)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.home_page = QMainWindow()
        self.home_ui = Ui_MainWindow()
        self.home_ui.setupUi(self.home_page)

        self.login_page = QWidget()
        self.login_ui = Ui_LoginPage()
        self.login_ui.setupUi(self.login_page)

        self.register_page = QWidget()
        self.register_ui = Ui_RegisterPage()
        self.register_ui.setupUi(self.register_page)

        self.dashboard_page = QWidget()
        self.dashboard_ui = Ui_DashboardPage()
        self.dashboard_ui.setupUi(self.dashboard_page)

        self.stack.addWidget(self.home_page)
        self.stack.addWidget(self.login_page)
        self.stack.addWidget(self.register_page)
        self.stack.addWidget(self.dashboard_page)

        self.stack.setCurrentWidget(self.home_page)

        self._bind_ui()

    def _bind_ui(self):
        for name in dir(self.home_ui):
            if not name.startswith("_"):
                setattr(self.home_page, name, getattr(self.home_ui, name))

        for name in dir(self.login_ui):
            if not name.startswith("_"):
                setattr(self.login_page, name, getattr(self.login_ui, name))

        for name in dir(self.register_ui):
            if not name.startswith("_"):
                setattr(self.register_page, name, getattr(self.register_ui, name))

        for name in dir(self.dashboard_ui):
            if not name.startswith("_"):
                setattr(self.dashboard_page, name, getattr(self.dashboard_ui, name))
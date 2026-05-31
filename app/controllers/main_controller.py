class MainController:
    def __init__(self, main_window):
        self.main_window = main_window
        self.connect_events()

    def connect_events(self):
        self.main_window.home_page.btnOpenLogin.clicked.connect(self.show_login)
        self.main_window.home_page.btnOpenRegister.clicked.connect(self.show_register)

    def show_login(self):
        self.main_window.stack.setCurrentWidget(self.main_window.login_page)

    def show_register(self):
        self.main_window.stack.setCurrentWidget(self.main_window.register_page)
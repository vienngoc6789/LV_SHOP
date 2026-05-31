from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QWidget

from app.view.dashboard_home_view import Ui_DashboardHomePage
from app.controllers.dashboard_home_controller import DashboardHomeController

from app.view.product_stock_view import Ui_ProductStockPage
from app.controllers.product_stock_controller import ProductStockController

from app.view.sales_view import Ui_SalesPage
from app.controllers.sales_controller import SalesController

from app.view.customer_view import Ui_CustomerPage
from app.controllers.customer_controller import CustomerController

from app.view.invoice_view import Ui_InvoicePage
from app.controllers.invoice_controller import InvoiceController

from app.view.warranty_view import Ui_WarrantyPage
from app.controllers.warranty_controller import WarrantyController

from app.view.discount_view import Ui_DiscountPage
from app.controllers.discount_controller import DiscountController

from app.view.report_view import Ui_ReportPage
from app.controllers.report_controller import ReportController

from app.view.human_view import Ui_HumanPage
from app.controllers.human_controller import HumanController

from app.view.profile_view import Ui_ProfilePage
from app.controllers.profile_controller import ProfileController
from app.view.customer_portal_view import Ui_CustomerPortalPage
from app.controllers.customer_portal_controller import CustomerPortalController

class DashboardController:
    def __init__(self, main_window):
        self.main_window = main_window
        self.dashboard_page = main_window.dashboard_page

        self.home_widget = QWidget()
        self.home_ui = Ui_DashboardHomePage()
        self.home_ui.setupUi(self.home_widget)
        self.dashboard_page.contentStackedWidget.addWidget(self.home_widget)
        self.home_controller = DashboardHomeController(
            self.home_ui,
            self
        )

        self.product_widget = QWidget()
        self.product_ui = Ui_ProductStockPage()
        self.product_ui.setupUi(self.product_widget)
        self.dashboard_page.contentStackedWidget.addWidget(self.product_widget)
        self.product_controller = ProductStockController(self.product_ui)

        self.sales_widget = QWidget()
        self.sales_ui = Ui_SalesPage()
        self.sales_ui.setupUi(self.sales_widget)
        self.dashboard_page.contentStackedWidget.addWidget(self.sales_widget)
        self.sales_controller = SalesController(self.sales_ui, self.main_window)

        self.customer_widget = QWidget()
        self.customer_ui = Ui_CustomerPage()
        self.customer_ui.setupUi(self.customer_widget)
        self.dashboard_page.contentStackedWidget.addWidget(self.customer_widget)
        self.customer_controller = CustomerController(self.customer_ui)

        self.invoice_widget = QWidget()
        self.invoice_ui = Ui_InvoicePage()
        self.invoice_ui.setupUi(self.invoice_widget)
        self.dashboard_page.contentStackedWidget.addWidget(self.invoice_widget)
        self.invoice_controller = InvoiceController(self.invoice_ui)

        self.warranty_widget = QWidget()
        self.warranty_ui = Ui_WarrantyPage()
        self.warranty_ui.setupUi(self.warranty_widget)
        self.dashboard_page.contentStackedWidget.addWidget(self.warranty_widget)
        self.warranty_controller = WarrantyController(self.warranty_ui)

        self.discount_widget = QWidget()
        self.discount_ui = Ui_DiscountPage()
        self.discount_ui.setupUi(self.discount_widget)
        self.dashboard_page.contentStackedWidget.addWidget(self.discount_widget)
        self.discount_controller = DiscountController(self.discount_ui)

        self.report_widget = QWidget()
        self.report_ui = Ui_ReportPage()
        self.report_ui.setupUi(self.report_widget)
        self.dashboard_page.contentStackedWidget.addWidget(self.report_widget)
        self.report_controller = ReportController(self.report_ui)

        self.human_widget = QWidget()
        self.human_ui = Ui_HumanPage()
        self.human_ui.setupUi(self.human_widget)
        self.dashboard_page.contentStackedWidget.addWidget(self.human_widget)
        self.human_controller = HumanController(self.human_ui)

        self.profile_widget = QWidget()
        self.profile_ui = Ui_ProfilePage()
        self.profile_ui.setupUi(self.profile_widget)
        self.dashboard_page.contentStackedWidget.addWidget(self.profile_widget)

        self.profile_controller = ProfileController(
            self.profile_ui,
            self.main_window,
            getattr(self.main_window, "current_user", None)
        )

        self.customer_portal_widget = QWidget()
        self.customer_portal_ui = Ui_CustomerPortalPage()
        self.customer_portal_ui.setupUi(self.customer_portal_widget)
        self.dashboard_page.contentStackedWidget.addWidget(self.customer_portal_widget)
        self.customer_portal_controller = CustomerPortalController(
            self.customer_portal_ui,
            self.main_window
        )

        self.current_role = ""

        self.is_sidebar_expanded = True
        self.sidebar_expanded_width = 260
        self.sidebar_collapsed_width = 82
        self.sidebar_animation = None

        self.logo_in_path = "assets/images/logoout.png"
        self.logo_out_path = "assets/images/logoin.png"

        self.menu_buttons = [
            self.dashboard_page.btnDashboard,
            self.dashboard_page.btnSales,
            self.dashboard_page.btnProduct,
            self.dashboard_page.btnDiscount,
            self.dashboard_page.btnCustomer,
            self.dashboard_page.btnInvoice,
            self.dashboard_page.btnWarranty,
            self.dashboard_page.btnHuman,
            self.dashboard_page.btnReport,
            self.dashboard_page.btnProfile,
        ]

        self.expanded_texts = {
            self.dashboard_page.btnDashboard: "📊  Trang chủ",
            self.dashboard_page.btnSales: "🛒  Bán hàng",
            self.dashboard_page.btnProduct: "📦  Sản phẩm & Kho",
            self.dashboard_page.btnDiscount: "🎁  Mã giảm giá",
            self.dashboard_page.btnCustomer: "👥  Khách hàng",
            self.dashboard_page.btnInvoice: "🧾  Hóa đơn",
            self.dashboard_page.btnWarranty: "🛠  Bảo hành",
            self.dashboard_page.btnHuman: "👨‍💼  Nhân sự",
            self.dashboard_page.btnReport: "📈  Báo cáo",
            self.dashboard_page.btnProfile: "👤  Tài khoản",
        }

        self.collapsed_texts = {
            self.dashboard_page.btnDashboard: "📊",
            self.dashboard_page.btnSales: "🛒",
            self.dashboard_page.btnProduct: "📦",
            self.dashboard_page.btnDiscount: "🎁",
            self.dashboard_page.btnCustomer: "👥",
            self.dashboard_page.btnInvoice: "🧾",
            self.dashboard_page.btnWarranty: "🛠",
            self.dashboard_page.btnHuman: "👨",
            self.dashboard_page.btnReport: "📈",
            self.dashboard_page.btnProfile: "👤",
        }

        self.page_titles = {
            self.dashboard_page.btnDashboard: "Trang chủ",
            self.dashboard_page.btnSales: "Bán hàng",
            self.dashboard_page.btnProduct: "Sản phẩm & Kho",
            self.dashboard_page.btnDiscount: "Mã giảm giá",
            self.dashboard_page.btnCustomer: "Khách hàng",
            self.dashboard_page.btnInvoice: "Hóa đơn",
            self.dashboard_page.btnWarranty: "Bảo hành",
            self.dashboard_page.btnHuman: "Nhân sự",
            self.dashboard_page.btnReport: "Báo cáo",
            self.dashboard_page.btnProfile: "Tài khoản",
        }

        self.setup_sidebar_style()
        self.connect_events()
        self.select_menu(self.dashboard_page.btnDashboard)

    def setup_sidebar_style(self):
        self.dashboard_page.sidebarFrame.setFixedWidth(self.sidebar_expanded_width)

        self.dashboard_page.logoLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.dashboard_page.logoLabel.setFixedHeight(54)
        self.set_logo_expanded()

        self.dashboard_page.btnToggleSidebar.setFixedSize(38, 38)
        self.dashboard_page.btnToggleSidebar.setText("‹")

        for btn in self.menu_buttons:
            btn.setCheckable(True)
            btn.setMinimumHeight(46)

        self.dashboard_page.btnLogout.setMinimumHeight(46)

    def connect_events(self):
        self.dashboard_page.btnToggleSidebar.clicked.connect(self.toggle_sidebar)
        self.dashboard_page.btnLogout.clicked.connect(self.logout)

        for button in self.menu_buttons:
            button.clicked.connect(
                lambda checked=False, btn=button: self.select_menu(btn)
            )

    def set_logo_expanded(self):
        pixmap = QPixmap(self.logo_in_path)
        self.dashboard_page.logoLabel.setText("")
        self.dashboard_page.logoLabel.setPixmap(
            pixmap.scaled(
                150,
                48,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        )

    def set_logo_collapsed(self):
        pixmap = QPixmap(self.logo_out_path)
        self.dashboard_page.logoLabel.setText("")
        self.dashboard_page.logoLabel.setPixmap(
            pixmap.scaled(
                42,
                42,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        )

    def load_user_info(self, user):
        full_name = user[1]
        role = user[4]

        self.dashboard_page.lblUserName.setText(full_name)
        self.dashboard_page.lblUserRole.setText(role)

        self.apply_permission(role)

    def apply_permission(self, role):
        role = role.lower()

        if role in ["admin", "quản lý"]:
            for btn in self.menu_buttons:
                btn.show()

        elif role in ["nhân viên", "sale"]:
            for btn in self.menu_buttons:
                btn.show()

            self.dashboard_page.btnHuman.hide()
            self.dashboard_page.btnReport.hide()

        else:
            for btn in self.menu_buttons:
                btn.show()

    def select_menu(self, selected_button):
        for button in self.menu_buttons:
            button.setChecked(False)

        selected_button.setChecked(True)

        title = self.page_titles.get(selected_button, "Trang chủ")
        self.dashboard_page.lblPageTitle.setText(title)

        if selected_button == self.dashboard_page.btnDashboard:
            self.dashboard_page.contentStackedWidget.setCurrentWidget(self.home_widget)

        elif selected_button == self.dashboard_page.btnSales:
            self.dashboard_page.contentStackedWidget.setCurrentWidget(self.sales_widget)

        elif selected_button == self.dashboard_page.btnProduct:
            self.dashboard_page.contentStackedWidget.setCurrentWidget(self.product_widget)

        elif selected_button == self.dashboard_page.btnCustomer:
            self.dashboard_page.contentStackedWidget.setCurrentWidget(self.customer_widget)

        elif selected_button == self.dashboard_page.btnInvoice:
            self.dashboard_page.contentStackedWidget.setCurrentWidget(self.invoice_widget)

        elif selected_button == self.dashboard_page.btnWarranty:
            self.dashboard_page.contentStackedWidget.setCurrentWidget(self.warranty_widget)
        elif selected_button == self.dashboard_page.btnDiscount:
            self.dashboard_page.contentStackedWidget.setCurrentWidget(self.discount_widget)

        elif selected_button == self.dashboard_page.btnReport:
            self.dashboard_page.contentStackedWidget.setCurrentWidget(self.report_widget)
        elif selected_button == self.dashboard_page.btnHuman:
            self.dashboard_page.contentStackedWidget.setCurrentWidget(self.human_widget)
        elif selected_button == self.dashboard_page.btnProfile:
            self.profile_controller.refresh()
            self.dashboard_page.contentStackedWidget.setCurrentWidget(self.profile_widget)
        else:
            self.dashboard_page.contentStackedWidget.setCurrentWidget(
                self.dashboard_page.pageWelcome
            )

            if hasattr(self.dashboard_page, "welcomeTitleLabel"):
                self.dashboard_page.welcomeTitleLabel.setText(title)

            if hasattr(self.dashboard_page, "welcomeSubtitleLabel"):
                self.dashboard_page.welcomeSubtitleLabel.setText(
                    "Chức năng sẽ được load UI riêng vào đây."
                )

    def toggle_sidebar(self):
        if self.is_sidebar_expanded:
            self.collapse_sidebar()
        else:
            self.expand_sidebar()

    def animate_sidebar(self, start_width, end_width):
        if self.sidebar_animation:
            self.sidebar_animation.stop()

        self.sidebar_animation = QPropertyAnimation(
            self.dashboard_page.sidebarFrame,
            b"minimumWidth"
        )
        self.sidebar_animation.setDuration(320)
        self.sidebar_animation.setStartValue(start_width)
        self.sidebar_animation.setEndValue(end_width)
        self.sidebar_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.sidebar_animation.valueChanged.connect(
            lambda value: self.dashboard_page.sidebarFrame.setMaximumWidth(value)
        )

        self.sidebar_animation.finished.connect(
            lambda: self.dashboard_page.sidebarFrame.setFixedWidth(end_width)
        )

        self.sidebar_animation.start()

    def collapse_sidebar(self):
        self.dashboard_page.sidebarFrame.setFixedWidth(self.sidebar_expanded_width)
        self.dashboard_page.sidebarLayout.setContentsMargins(8, 14, 8, 14)
        self.dashboard_page.sidebarLayout.setSpacing(9)

        self.dashboard_page.logoLabel.setFixedHeight(48)
        self.set_logo_collapsed()

        self.dashboard_page.btnToggleSidebar.setText("›")
        self.dashboard_page.btnToggleSidebar.setFixedSize(48, 42)

        for btn in self.menu_buttons:
            btn.setText(self.collapsed_texts[btn])
            btn.setToolTip(self.expanded_texts[btn])
            btn.setFixedSize(54, 46)

        self.dashboard_page.btnLogout.setText("🚪")
        self.dashboard_page.btnLogout.setToolTip("Đăng xuất")
        self.dashboard_page.btnLogout.setFixedSize(54, 46)

        self.animate_sidebar(
            self.sidebar_expanded_width,
            self.sidebar_collapsed_width
        )

        self.is_sidebar_expanded = False

    def expand_sidebar(self):
        self.dashboard_page.sidebarFrame.setFixedWidth(self.sidebar_collapsed_width)
        self.dashboard_page.sidebarLayout.setContentsMargins(18, 20, 18, 20)
        self.dashboard_page.sidebarLayout.setSpacing(12)

        self.dashboard_page.logoLabel.setFixedHeight(54)
        self.set_logo_expanded()

        self.dashboard_page.btnToggleSidebar.setText("‹")
        self.dashboard_page.btnToggleSidebar.setFixedSize(38, 38)

        for btn in self.menu_buttons:
            btn.setText(self.expanded_texts[btn])
            btn.setToolTip("")
            btn.setMinimumHeight(46)
            btn.setMaximumHeight(16777215)
            btn.setMinimumWidth(0)
            btn.setMaximumWidth(16777215)

        self.dashboard_page.btnLogout.setText("🚪  Đăng xuất")
        self.dashboard_page.btnLogout.setToolTip("")
        self.dashboard_page.btnLogout.setMinimumHeight(46)
        self.dashboard_page.btnLogout.setMaximumHeight(16777215)
        self.dashboard_page.btnLogout.setMinimumWidth(0)
        self.dashboard_page.btnLogout.setMaximumWidth(16777215)

        self.animate_sidebar(
            self.sidebar_collapsed_width,
            self.sidebar_expanded_width
        )

        self.is_sidebar_expanded = True

    def logout(self):
        self.main_window.current_user = None

        for button in self.menu_buttons:
            button.setChecked(False)

        self.dashboard_page.lblPageTitle.setText("Trang chủ")
        self.dashboard_page.lblUserName.setText("")
        self.dashboard_page.lblUserRole.setText("")

        self.main_window.stack.setCurrentWidget(self.main_window.login_page)

    def show_home(self):
        self.main_window.stack.setCurrentWidget(self.main_window.home_page)

    def load_user_info(self, user):
        full_name = user[1]
        role = user[4]
        self.current_role = role or ""

        self.dashboard_page.lblUserName.setText(full_name)
        self.dashboard_page.lblUserRole.setText(role)

        self.apply_permission(role)
        self.select_menu(self.dashboard_page.btnDashboard)

    def apply_permission(self, role):
        role = (role or "").lower()

        if role in ["admin", "quản lý", "quáº£n lÃ½"]:
            self.restore_staff_dashboard_text()
            for btn in self.menu_buttons:
                btn.show()

        elif role in ["nhân viên", "nhÃ¢n viÃªn", "sale"]:
            self.restore_staff_dashboard_text()
            for btn in self.menu_buttons:
                btn.show()

            self.dashboard_page.btnHuman.hide()
            self.dashboard_page.btnReport.hide()

        elif role in ["customer", "khách hàng", "khach hang"]:
            for btn in self.menu_buttons:
                btn.hide()

            self.dashboard_page.btnDashboard.show()
            self.dashboard_page.btnProfile.show()
            self.expanded_texts[self.dashboard_page.btnDashboard] = "🛍  Cửa hàng"
            self.collapsed_texts[self.dashboard_page.btnDashboard] = "🛍"
            self.page_titles[self.dashboard_page.btnDashboard] = "Cửa hàng của tôi"
            self.refresh_sidebar_button_texts()

        else:
            self.restore_staff_dashboard_text()
            for btn in self.menu_buttons:
                btn.hide()

            self.dashboard_page.btnDashboard.show()
            self.dashboard_page.btnProfile.show()

    def select_menu(self, selected_button):
        if selected_button and not selected_button.isVisible():
            selected_button = self.dashboard_page.btnDashboard

        for button in self.menu_buttons:
            button.setChecked(False)

        selected_button.setChecked(True)

        title = self.page_titles.get(selected_button, "Trang chủ")
        self.dashboard_page.lblPageTitle.setText(title)

        if selected_button == self.dashboard_page.btnDashboard:
            if self.is_customer_role():
                self.customer_portal_controller.refresh()
                self.dashboard_page.contentStackedWidget.setCurrentWidget(self.customer_portal_widget)
            else:
                self.dashboard_page.contentStackedWidget.setCurrentWidget(self.home_widget)

        elif selected_button == self.dashboard_page.btnSales:
            self.dashboard_page.contentStackedWidget.setCurrentWidget(self.sales_widget)

        elif selected_button == self.dashboard_page.btnProduct:
            self.dashboard_page.contentStackedWidget.setCurrentWidget(self.product_widget)

        elif selected_button == self.dashboard_page.btnCustomer:
            self.dashboard_page.contentStackedWidget.setCurrentWidget(self.customer_widget)

        elif selected_button == self.dashboard_page.btnInvoice:
            self.dashboard_page.contentStackedWidget.setCurrentWidget(self.invoice_widget)

        elif selected_button == self.dashboard_page.btnWarranty:
            self.dashboard_page.contentStackedWidget.setCurrentWidget(self.warranty_widget)

        elif selected_button == self.dashboard_page.btnDiscount:
            self.dashboard_page.contentStackedWidget.setCurrentWidget(self.discount_widget)

        elif selected_button == self.dashboard_page.btnReport:
            self.dashboard_page.contentStackedWidget.setCurrentWidget(self.report_widget)

        elif selected_button == self.dashboard_page.btnHuman:
            self.dashboard_page.contentStackedWidget.setCurrentWidget(self.human_widget)

        elif selected_button == self.dashboard_page.btnProfile:
            self.profile_controller.refresh()
            self.dashboard_page.contentStackedWidget.setCurrentWidget(self.profile_widget)

    def logout(self):
        self.main_window.current_user = None
        self.current_role = ""
        self.restore_staff_dashboard_text()

        for button in self.menu_buttons:
            button.setChecked(False)

        self.dashboard_page.lblPageTitle.setText("Trang chủ")
        self.dashboard_page.lblUserName.setText("")
        self.dashboard_page.lblUserRole.setText("")

        self.main_window.stack.setCurrentWidget(self.main_window.login_page)

    def is_customer_role(self):
        role = (self.current_role or "").lower()
        return role in ["customer", "khách hàng", "khach hang"]

    def restore_staff_dashboard_text(self):
        self.expanded_texts[self.dashboard_page.btnDashboard] = "📊  Trang chủ"
        self.collapsed_texts[self.dashboard_page.btnDashboard] = "📊"
        self.page_titles[self.dashboard_page.btnDashboard] = "Trang chủ"
        self.refresh_sidebar_button_texts()

    def refresh_sidebar_button_texts(self):
        if self.is_sidebar_expanded:
            for btn in self.menu_buttons:
                btn.setText(self.expanded_texts[btn])
        else:
            for btn in self.menu_buttons:
                btn.setText(self.collapsed_texts[btn])

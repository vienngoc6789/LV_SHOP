import sqlite3
from datetime import datetime

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QListWidgetItem, QVBoxLayout, QMessageBox
from PyQt6.QtGui import QColor

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

try:
    from app.models.database import get_connection
except Exception:
    get_connection = None


class DashboardHomeController:
    def __init__(self, dashboard_page, dashboard_controller=None):
        self.page = dashboard_page
        self.dashboard_controller = dashboard_controller
        self.chart_canvas = None

        self.setup_ui()
        self.connect_events()
        self.load_all()

        self.timer = QTimer()
        self.timer.timeout.connect(self.load_all)
        self.timer.start(30000)

    def setup_ui(self):
        self.page.chartFrame.setFixedHeight(230)

        if self.page.chartFrame.layout() is None:
            self.page.chartFrame.setLayout(QVBoxLayout())

        if hasattr(self.page, "lblChartPlaceholder"):
            self.page.lblChartPlaceholder.hide()

        self.page.listRecentActivity.setMinimumHeight(150)
        self.page.listWarning.setMinimumHeight(150)

    def connect_events(self):
        self.page.btnCreateOrder.clicked.connect(self.create_order)
        self.page.btnAddProduct.clicked.connect(self.add_product)
        self.page.btnAddCustomer.clicked.connect(self.add_customer)

    def get_db(self):
        if get_connection:
            return get_connection()
        return sqlite3.connect("lvshop.db")

    def safe_one(self, sql, params=(), default=0):
        try:
            conn = self.get_db()
            cursor = conn.cursor()
            cursor.execute(sql, params)
            row = cursor.fetchone()
            conn.close()
            return row[0] if row and row[0] is not None else default
        except Exception:
            return default

    def safe_all(self, sql, params=()):
        try:
            conn = self.get_db()
            cursor = conn.cursor()
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            conn.close()
            return rows
        except Exception:
            return []

    def money(self, value):
        return f"{float(value or 0):,.0f} ₫"

    def format_date(self, value):
        if not value:
            return ""
        try:
            return datetime.strptime(str(value)[:19], "%Y-%m-%d %H:%M:%S").strftime("%d/%m %H:%M")
        except Exception:
            return str(value)

    def load_all(self):
        self.load_statistics()
        self.draw_revenue_chart()
        self.load_recent_activity()
        self.load_warnings()

    def load_statistics(self):
        revenue = self.safe_one("""
            SELECT IFNULL(SUM(total_price), 0)
            FROM invoices
            WHERE status = 'paid'
              AND DATE(created_at) = DATE('now', 'localtime')
        """)

        orders = self.safe_one("""
            SELECT COUNT(*)
            FROM invoices
            WHERE status = 'paid'
              AND DATE(created_at) = DATE('now', 'localtime')
        """)

        products = self.safe_one("""
            SELECT COUNT(*)
            FROM product_imeis
            WHERE status = 'in_stock'
        """)

        customers = self.safe_one("SELECT COUNT(*) FROM customers")

        self.page.lblRevenueToday.setText(self.money(revenue))
        self.page.lblOrderToday.setText(str(orders))
        self.page.lblProductCount.setText(str(products))
        self.page.lblCustomerCount.setText(str(customers))

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()

    def draw_revenue_chart(self):
        data = self.safe_all("""
            SELECT DATE(created_at), IFNULL(SUM(total_price), 0)
            FROM invoices
            WHERE status = 'paid'
              AND DATE(created_at) >= DATE('now', '-6 day', 'localtime')
            GROUP BY DATE(created_at)
            ORDER BY DATE(created_at)
        """)

        layout = self.page.chartFrame.layout()
        self.clear_layout(layout)

        fig = Figure(figsize=(7.0, 2.8), dpi=100)
        canvas = FigureCanvas(fig)
        canvas.setFixedHeight(220)

        ax = fig.add_subplot(111)

        if not data:
            ax.text(0.5, 0.5, "Chưa có doanh thu 7 ngày gần nhất", ha="center", va="center")
            ax.axis("off")
        else:
            labels = [str(row[0])[5:] for row in data]
            values = [float(row[1] or 0) for row in data]

            ax.bar(labels, values)
            ax.set_ylabel("VNĐ")
            ax.tick_params(axis="x", rotation=25)
            ax.grid(axis="y", linestyle="--", alpha=0.3)

            for index, value in enumerate(values):
                label = f"{value / 1_000_000:.1f}M" if value >= 1_000_000 else f"{value:,.0f}"
                ax.text(index, value, label, ha="center", va="bottom", fontsize=8)

        fig.tight_layout()
        layout.addWidget(canvas)
        self.chart_canvas = canvas

    def load_recent_activity(self):
        self.page.listRecentActivity.setUpdatesEnabled(False)
        self.page.listRecentActivity.clear()

        invoices = self.safe_all("""
            SELECT
                i.id,
                i.created_at,
                IFNULL(c.name, 'Khách lẻ'),
                IFNULL(i.total_price, 0)
            FROM invoices i
            LEFT JOIN customers c ON i.customer_id = c.id
            ORDER BY i.id DESC
            LIMIT 6
        """)

        if invoices:
            for invoice_id, created_at, customer_name, total_price in invoices:
                text = (
                    f"🧾 Hóa đơn #{invoice_id} - {customer_name} - "
                    f"{self.money(total_price)} ({self.format_date(created_at)})"
                )
                self.page.listRecentActivity.addItem(QListWidgetItem(text))
        else:
            self.page.listRecentActivity.addItem(QListWidgetItem("Chưa có hoạt động bán hàng."))

        self.page.listRecentActivity.setUpdatesEnabled(True)

    def load_warnings(self):
        self.page.listWarning.setUpdatesEnabled(False)
        self.page.listWarning.clear()

        warnings = []

        low_stock = self.safe_all("""
                                  SELECT IFNULL(p.name, 'Sản phẩm') AS product_name,
                                         IFNULL(s.name, '')         AS storage,
                                         IFNULL(c.name, '')         AS color,
                                         COUNT(pi.id)               AS stock
                                  FROM product_variants v
                                           LEFT JOIN products p ON v.product_id = p.id
                                           LEFT JOIN storages s ON v.storage_id = s.id
                                           LEFT JOIN colors c ON v.color_id = c.id
                                           LEFT JOIN product_imeis pi
                                                     ON pi.variant_id = v.id
                                                         AND pi.status = 'in_stock'
                                  GROUP BY v.id
                                  HAVING stock < 2
                                  ORDER BY stock ASC LIMIT 8
                                  """)
        for product_name, storage, color, stock in low_stock:
            warnings.append(
                f"⚠️ Sắp hết hàng: {product_name} {storage} {color} chỉ còn {stock} IMEI"
            )

        pending_warranty = self.safe_one("""
            SELECT COUNT(*)
            FROM warranties
            WHERE status IN ('pending', 'checking', 'repairing')
        """)

        if pending_warranty > 0:
            warnings.append(f"🛠 Có {pending_warranty} phiếu bảo hành đang xử lý")

        if not warnings:
            warnings.append("✅ Không có cảnh báo quan trọng.")

        for text in warnings:
            item = QListWidgetItem(text)

            if text.startswith("⚠️"):
                item.setForeground(QColor("#dc2626"))
            elif text.startswith("🛠"):
                item.setForeground(QColor("#f59e0b"))
            else:
                item.setForeground(QColor("#16a34a"))

            self.page.listWarning.addItem(item)

        self.page.listWarning.setUpdatesEnabled(True)

    def switch_to_menu(self, button_name):
        if not self.dashboard_controller:
            QMessageBox.information(
                None,
                "Thông báo",
                "Chưa truyền DashboardController vào DashboardHomeController."
            )
            return

        dashboard_page = getattr(self.dashboard_controller, "dashboard_page", None)

        if not dashboard_page or not hasattr(dashboard_page, button_name):
            QMessageBox.warning(None, "Lỗi", f"Không tìm thấy nút menu {button_name}")
            return

        button = getattr(dashboard_page, button_name)
        button.click()

    def create_order(self):
        self.switch_to_menu("btnSales")

    def add_product(self):
        self.switch_to_menu("btnProduct")

    def add_customer(self):
        self.switch_to_menu("btnCustomer")
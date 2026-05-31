import csv
import traceback

from PyQt6.QtWidgets import (
    QTableWidgetItem,
    QAbstractItemView,
    QFileDialog,
    QMessageBox,
    QVBoxLayout,
)
from PyQt6.QtCore import QDate

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from app.models.report_model import ReportModel


class ReportController:
    def __init__(self, page):
        self.page = page
        self.chart_group_type = "Theo ngày"
        self.revenue_canvas = None
        self.brand_canvas = None

        self.setup_ui()
        self.connect_events()
        self.set_default_dates()
        self.view_by_day()

    def setup_ui(self):
        tables = [
            self.page.tableTopProducts,
            self.page.tableTopCustomers,
            self.page.tableTopDiscounts,
        ]

        for table in tables:
            table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
            table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        self.page.tableTopProducts.setColumnWidth(0, 45)
        self.page.tableTopProducts.setColumnWidth(1, 170)
        self.page.tableTopProducts.setColumnWidth(2, 75)
        self.page.tableTopProducts.horizontalHeader().setStretchLastSection(True)

        self.page.tableTopCustomers.setColumnWidth(0, 45)
        self.page.tableTopCustomers.setColumnWidth(1, 160)
        self.page.tableTopCustomers.setColumnWidth(2, 75)
        self.page.tableTopCustomers.horizontalHeader().setStretchLastSection(True)

        self.page.tableTopDiscounts.setColumnWidth(0, 45)
        self.page.tableTopDiscounts.setColumnWidth(1, 110)
        self.page.tableTopDiscounts.setColumnWidth(2, 90)
        self.page.tableTopDiscounts.horizontalHeader().setStretchLastSection(True)

        self.ensure_chart_layouts()

    def ensure_chart_layouts(self):
        if self.page.chartRevenueFrame.layout() is None:
            self.page.chartRevenueFrame.setLayout(QVBoxLayout())

        if self.page.chartBrandFrame.layout() is None:
            self.page.chartBrandFrame.setLayout(QVBoxLayout())

        if hasattr(self.page, "lblRevenueChartPlaceholder"):
            self.page.lblRevenueChartPlaceholder.hide()

        if hasattr(self.page, "lblBrandChartPlaceholder"):
            self.page.lblBrandChartPlaceholder.hide()

    def connect_events(self):
        self.page.btnViewDay.clicked.connect(self.view_by_day)
        self.page.btnViewMonth.clicked.connect(self.view_by_month)
        self.page.btnViewYear.clicked.connect(self.view_by_year)

        self.page.btnRefreshReport.clicked.connect(self.load_report)
        self.page.btnExportCsv.clicked.connect(self.export_csv)
        self.page.btnExportExcel.clicked.connect(self.export_csv)

    def set_default_dates(self):
        today = QDate.currentDate()
        first_day = QDate(today.year(), today.month(), 1)
        self.page.dateFrom.setDate(first_day)
        self.page.dateTo.setDate(today)

    def money(self, value):
        return f"{float(value or 0):,.0f} đ"

    def get_dates(self):
        return (
            self.page.dateFrom.date().toString("yyyy-MM-dd"),
            self.page.dateTo.date().toString("yyyy-MM-dd"),
        )

    def view_by_day(self):
        self.chart_group_type = "Theo ngày"
        self.highlight_button(self.page.btnViewDay)
        self.load_report()

    def view_by_month(self):
        self.chart_group_type = "Theo tháng"
        self.highlight_button(self.page.btnViewMonth)
        self.load_report()

    def view_by_year(self):
        self.chart_group_type = "Theo năm"
        self.highlight_button(self.page.btnViewYear)
        self.load_report()

    def highlight_button(self, active_button):
        buttons = [
            self.page.btnViewDay,
            self.page.btnViewMonth,
            self.page.btnViewYear,
        ]

        for button in buttons:
            if button == active_button:
                button.setStyleSheet("background-color: #1d4ed8; color: white;")
            else:
                button.setStyleSheet("background-color: #2563eb; color: white;")

    def load_report(self):
        try:
            date_from, date_to = self.get_dates()

            if self.page.dateTo.date() < self.page.dateFrom.date():
                QMessageBox.warning(None, "Sai ngày", "Ngày kết thúc không được nhỏ hơn ngày bắt đầu")
                return

            order_count, revenue, profit, aov = ReportModel.get_kpi(date_from, date_to)

            self.page.lblRevenueValue.setText(self.money(revenue))
            self.page.lblProfitValue.setText(self.money(profit))
            self.page.lblOrderValue.setText(str(order_count))
            self.page.lblAovValue.setText(self.money(aov))

            self.draw_revenue_bar_chart(date_from, date_to, self.chart_group_type)
            self.draw_brand_bar_chart(date_from, date_to)

            self.load_top_products(date_from, date_to)
            self.load_top_customers(date_from, date_to)
            self.load_top_discounts()

        except Exception as e:
            print(traceback.format_exc())
            QMessageBox.critical(None, "Lỗi báo cáo", f"Không thể tải báo cáo:\n{e}")

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def draw_revenue_bar_chart(self, date_from, date_to, group_type):
        self.page.lblRevenueChartTitle.setText(f"📊 Doanh thu {group_type.lower()}")

        data = ReportModel.get_revenue_grouped(date_from, date_to, group_type)

        layout = self.page.chartRevenueFrame.layout()
        self.clear_layout(layout)

        fig = Figure(figsize=(6.4, 3.0), dpi=100)
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)

        if not data:
            ax.text(
                0.5,
                0.5,
                f"Chưa có dữ liệu doanh thu {group_type.lower()}",
                ha="center",
                va="center",
                fontsize=11,
            )
            ax.axis("off")
        else:
            labels = [str(row[0]) for row in data]
            values = [float(row[1] or 0) for row in data]

            if group_type == "Theo tháng":
                labels = [
                    label[5:7] + "/" + label[0:4] if "-" in label else label
                    for label in labels
                ]

            ax.bar(labels, values)
            ax.set_title(f"Doanh thu {group_type.lower()}")
            ax.set_ylabel("VNĐ")
            ax.tick_params(axis="x", rotation=35)
            ax.grid(axis="y", linestyle="--", alpha=0.3)

            for index, value in enumerate(values):
                label = f"{value / 1_000_000:.1f}M" if value >= 1_000_000 else f"{value:,.0f}"
                ax.text(index, value, label, ha="center", va="bottom", fontsize=8)

        fig.tight_layout()
        layout.addWidget(canvas)
        self.revenue_canvas = canvas

    def draw_brand_bar_chart(self, date_from, date_to):
        self.page.lblBrandChartTitle.setText("🏷 Top hãng bán chạy")

        data = ReportModel.get_top_brands(date_from, date_to, 5)

        layout = self.page.chartBrandFrame.layout()
        self.clear_layout(layout)

        fig = Figure(figsize=(3.6, 3.0), dpi=100)
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)

        if not data:
            ax.text(
                0.5,
                0.5,
                "Chưa có dữ liệu hãng bán chạy",
                ha="center",
                va="center",
                fontsize=11,
            )
            ax.axis("off")
        else:
            brands = [str(row[0]) for row in data]
            qty_values = [int(row[1] or 0) for row in data]

            ax.barh(brands, qty_values)
            ax.set_title("Top hãng bán chạy")
            ax.set_xlabel("Số máy bán")
            ax.invert_yaxis()
            ax.grid(axis="x", linestyle="--", alpha=0.3)

            for index, value in enumerate(qty_values):
                ax.text(value, index, f" {value}", va="center", fontsize=8)

        fig.tight_layout()
        layout.addWidget(canvas)
        self.brand_canvas = canvas

    def load_top_products(self, date_from, date_to):
        data = ReportModel.get_top_products(date_from, date_to, 5)
        self.page.tableTopProducts.setRowCount(0)

        for index, row_data in enumerate(data, start=1):
            product_name, qty, revenue = row_data
            row = self.page.tableTopProducts.rowCount()
            self.page.tableTopProducts.insertRow(row)

            values = [index, product_name, qty, self.money(revenue)]

            for col, value in enumerate(values):
                self.page.tableTopProducts.setItem(row, col, QTableWidgetItem(str(value)))

    def load_top_customers(self, date_from, date_to):
        data = ReportModel.get_top_customers(date_from, date_to, 5)
        self.page.tableTopCustomers.setRowCount(0)

        for index, row_data in enumerate(data, start=1):
            customer_name, order_count, total_spent = row_data
            row = self.page.tableTopCustomers.rowCount()
            self.page.tableTopCustomers.insertRow(row)

            values = [index, customer_name, order_count, self.money(total_spent)]

            for col, value in enumerate(values):
                self.page.tableTopCustomers.setItem(row, col, QTableWidgetItem(str(value)))

    def load_top_discounts(self):
        data = ReportModel.get_top_discounts(5)
        self.page.tableTopDiscounts.setRowCount(0)

        for index, row_data in enumerate(data, start=1):
            code, used_count, total_discount = row_data
            row = self.page.tableTopDiscounts.rowCount()
            self.page.tableTopDiscounts.insertRow(row)

            values = [index, code, used_count, self.money(total_discount)]

            for col, value in enumerate(values):
                self.page.tableTopDiscounts.setItem(row, col, QTableWidgetItem(str(value)))

    def export_csv(self):
        date_from, date_to = self.get_dates()

        file_path, _ = QFileDialog.getSaveFileName(
            None,
            "Xuất báo cáo",
            f"bao_cao_{date_from}_to_{date_to}.csv",
            "CSV Files (*.csv)",
        )

        if not file_path:
            return

        if not file_path.lower().endswith(".csv"):
            file_path += ".csv"

        order_count, revenue, profit, aov = ReportModel.get_kpi(date_from, date_to)
        revenue_grouped = ReportModel.get_revenue_grouped(date_from, date_to, self.chart_group_type)
        top_brands = ReportModel.get_top_brands(date_from, date_to, 10)
        top_products = ReportModel.get_top_products(date_from, date_to, 10)
        top_customers = ReportModel.get_top_customers(date_from, date_to, 10)
        top_discounts = ReportModel.get_top_discounts(10)

        with open(file_path, "w", newline="", encoding="utf-8-sig") as file:
            writer = csv.writer(file)

            writer.writerow(["BÁO CÁO LV SHOP"])
            writer.writerow(["Từ ngày", date_from, "Đến ngày", date_to])
            writer.writerow(["Kiểu biểu đồ", self.chart_group_type])
            writer.writerow([])

            writer.writerow(["KPI"])
            writer.writerow(["Số đơn", order_count])
            writer.writerow(["Doanh thu", revenue])
            writer.writerow(["Lợi nhuận ước tính", profit])
            writer.writerow(["Trung bình / đơn", aov])
            writer.writerow([])

            writer.writerow(["DOANH THU"])
            writer.writerow(["Kỳ", "Doanh thu"])
            for row in revenue_grouped:
                writer.writerow(row)
            writer.writerow([])

            writer.writerow(["TOP HÃNG BÁN CHẠY"])
            writer.writerow(["Hãng", "Số lượng", "Doanh thu"])
            for row in top_brands:
                writer.writerow(row)
            writer.writerow([])

            writer.writerow(["TOP SẢN PHẨM"])
            writer.writerow(["Sản phẩm", "Số lượng", "Doanh thu"])
            for row in top_products:
                writer.writerow(row)
            writer.writerow([])

            writer.writerow(["TOP KHÁCH HÀNG"])
            writer.writerow(["Khách hàng", "Số đơn", "Tổng chi"])
            for row in top_customers:
                writer.writerow(row)
            writer.writerow([])

            writer.writerow(["TOP MÃ GIẢM GIÁ"])
            writer.writerow(["Mã", "Lượt dùng", "Tổng giảm"])
            for row in top_discounts:
                writer.writerow(row)

        QMessageBox.information(None, "Thành công", f"Đã xuất báo cáo:\n{file_path}")
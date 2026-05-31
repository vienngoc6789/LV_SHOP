from PyQt6.QtWidgets import (
    QTableWidgetItem,
    QMessageBox,
    QListWidgetItem,
    QAbstractItemView,
    QCompleter
)
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt

from app.models.product_model import ProductModel


class ProductStockController:
    def __init__(self, page):
        self.page = page
        self.selected_variant_id = None
        self.selected_imei_id = None
        self.products_cache = []

        self.setup_tables()
        self.setup_product_name_input()
        self.connect_events()
        self.refresh()

    # ======================
    # SETUP
    # ======================
    def setup_tables(self):
        self.page.tableProducts.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.page.tableProducts.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )

        self.page.tableImeis.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.page.tableImeis.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )

        self.page.tableProducts.setColumnCount(9)
        self.page.tableProducts.setHorizontalHeaderLabels([
            "ID",
            "Tên sản phẩm",
            "Hãng",
            "Dung lượng",
            "Màu",
            "Giá bán",
            "Giá nhập TB",
            "Tồn IMEI",
            "Mô tả"
        ])

        self.page.tableProducts.setColumnWidth(0, 55)
        self.page.tableProducts.setColumnWidth(1, 180)
        self.page.tableProducts.setColumnWidth(2, 95)
        self.page.tableProducts.setColumnWidth(3, 90)
        self.page.tableProducts.setColumnWidth(4, 90)
        self.page.tableProducts.setColumnWidth(5, 120)
        self.page.tableProducts.setColumnWidth(6, 120)
        self.page.tableProducts.setColumnWidth(7, 90)
        self.page.tableProducts.horizontalHeader().setStretchLastSection(True)

        self.page.tableImeis.setColumnCount(5)
        self.page.tableImeis.setHorizontalHeaderLabels([
            "ID",
            "IMEI",
            "Trạng thái",
            "Giá nhập",
            "Ngày nhập"
        ])

        self.page.tableImeis.setColumnWidth(0, 50)
        self.page.tableImeis.setColumnWidth(1, 190)
        self.page.tableImeis.setColumnWidth(2, 100)
        self.page.tableImeis.setColumnWidth(3, 120)
        self.page.tableImeis.horizontalHeader().setStretchLastSection(True)

    def setup_product_name_input(self):
        names = ProductModel.get_product_names()

        self.page.cboProductName.blockSignals(True)
        self.page.cboProductName.clear()
        self.page.cboProductName.addItems(names)
        self.page.cboProductName.setEditable(True)
        self.page.cboProductName.setInsertPolicy(
            self.page.cboProductName.InsertPolicy.NoInsert
        )
        self.page.cboProductName.blockSignals(False)

        completer = QCompleter(names)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.page.cboProductName.setCompleter(completer)

    def connect_events(self):
        self.page.btnAdd.clicked.connect(self.add_variant_with_imeis)
        self.page.btnUpdate.clicked.connect(self.update_product)
        self.page.btnDelete.clicked.connect(self.delete_product)
        self.page.btnClear.clicked.connect(self.clear_form)
        self.page.btnRefresh.clicked.connect(self.refresh)

        self.page.btnShowVariants.clicked.connect(self.refresh)
        self.page.btnMarkImeiSold.clicked.connect(self.mark_imei_sold)
        self.page.btnDeleteImei.clicked.connect(self.delete_imei)

        self.page.searchBox.textChanged.connect(self.apply_filters)
        self.page.cboFilterStock.currentIndexChanged.connect(self.apply_filters)
        self.page.tableProducts.cellClicked.connect(self.select_product_row)
        self.page.tableImeis.cellClicked.connect(self.select_imei_row)
        self.page.cboProductName.currentTextChanged.connect(self.on_product_selected)

    # ======================
    # LOAD DATA
    # ======================
    def refresh(self):
        current_name = self.get_product_name()

        self.setup_product_name_input()

        if current_name:
            self.set_product_name(current_name)

        self.products_cache = ProductModel.get_all_products()
        self.apply_filters()
        self.load_low_stock()

        if self.selected_variant_id:
            self.load_imeis(self.selected_variant_id)

    def apply_filters(self):
        keyword = self.page.searchBox.text().lower().strip()
        stock_filter = self.page.cboFilterStock.currentText()

        data = []

        for item in self.products_cache:
            text = " ".join(str(x).lower() for x in item)
            stock = int(item[7])

            if stock_filter == "Sắp hết hàng":
                match_stock = 0 < stock <= 3
            elif stock_filter == "Còn hàng":
                match_stock = stock > 3
            elif stock_filter == "Hết hàng":
                match_stock = stock == 0
            else:
                match_stock = True

            if keyword in text and match_stock:
                data.append(item)

        self.render_product_table(data)

    def render_product_table(self, data):
        self.page.tableProducts.setRowCount(0)

        for row_data in data:
            row = self.page.tableProducts.rowCount()
            self.page.tableProducts.insertRow(row)

            # row_data:
            # 0 id, 1 name, 2 brand, 3 storage, 4 color,
            # 5 sell_price, 6 avg_import_price, 7 stock, 8 description,
            # 9 imei_search_text hidden
            for col, value in enumerate(row_data[:9]):
                display_value = value

                if col in [5, 6]:
                    display_value = f"{float(value):,.0f} đ"

                item = QTableWidgetItem(str(display_value))

                if col == 7:
                    stock = int(value)

                    if stock == 0:
                        item.setForeground(QColor("#b91c1c"))
                    elif stock <= 3:
                        item.setForeground(QColor("#dc2626"))
                    elif stock <= 6:
                        item.setForeground(QColor("#f59e0b"))
                    else:
                        item.setForeground(QColor("#16a34a"))

                self.page.tableProducts.setItem(row, col, item)

    def load_low_stock(self):
        self.page.listLowStock.clear()
        data = ProductModel.get_low_stock(3)

        if not data:
            self.page.listLowStock.addItem("✅ Không có sản phẩm sắp hết hàng")
            return

        for variant_id, name, storage, color, stock in data:
            item = QListWidgetItem(
                f"⚠️ #{variant_id} - {name} / {storage} / {color} còn {stock} máy"
            )
            item.setForeground(QColor("#dc2626"))
            self.page.listLowStock.addItem(item)

    def load_imeis(self, variant_id):
        self.page.tableImeis.setRowCount(0)
        data = ProductModel.get_imeis_by_variant(variant_id)

        for row_data in data:
            row = self.page.tableImeis.rowCount()
            self.page.tableImeis.insertRow(row)

            for col, value in enumerate(row_data):
                display_value = value

                if col == 3:
                    display_value = f"{float(value):,.0f} đ"

                item = QTableWidgetItem(str(display_value))

                if col == 2:
                    if value == "in_stock":
                        item.setForeground(QColor("#16a34a"))
                    elif value == "sold":
                        item.setForeground(QColor("#dc2626"))
                    else:
                        item.setForeground(QColor("#f59e0b"))

                self.page.tableImeis.setItem(row, col, item)

    # ======================
    # FORM HELPERS
    # ======================
    def get_product_name(self):
        return self.page.cboProductName.currentText().strip()

    def set_product_name(self, value):
        self.page.cboProductName.setCurrentText(value)

    def get_form_data(self):
        return (
            self.get_product_name(),
            self.page.txtBrand.text().strip(),
            self.page.cboStorage.currentText().strip(),
            self.page.cboColor.currentText().strip(),
            self.page.spinPrice.value(),
            self.page.spinImportPrice.value(),
            self.page.txtDescription.text().strip()
        )

    def get_imei_list_from_form(self):
        text = self.page.txtBulkImei.toPlainText().strip()

        if not text:
            return []

        imeis = []
        duplicate_input = []

        for line in text.splitlines():
            imei = line.strip()

            if not imei:
                continue

            if imei in imeis:
                duplicate_input.append(imei)
            else:
                imeis.append(imei)

        if duplicate_input:
            QMessageBox.warning(
                None,
                "Trùng IMEI",
                "Danh sách IMEI đang có dòng bị trùng. Vui lòng kiểm tra lại."
            )
            return None

        return imeis

    def validate_form(self, require_imei=False):
        name, brand, storage, color, price, import_price, description = self.get_form_data()

        if not name:
            QMessageBox.warning(None, "Thiếu thông tin", "Vui lòng nhập tên sản phẩm")
            return False

        if not brand:
            QMessageBox.warning(None, "Thiếu thông tin", "Vui lòng nhập hãng")
            return False

        if not storage:
            QMessageBox.warning(None, "Thiếu thông tin", "Vui lòng nhập dung lượng")
            return False

        if not color:
            QMessageBox.warning(None, "Thiếu thông tin", "Vui lòng nhập màu sắc")
            return False

        if price <= 0:
            QMessageBox.warning(None, "Lỗi giá", "Giá bán phải lớn hơn 0")
            return False

        if import_price < 0:
            QMessageBox.warning(None, "Lỗi giá nhập", "Giá nhập không hợp lệ")
            return False

        if require_imei:
            imeis = self.get_imei_list_from_form()

            if imeis is None:
                return False

            if not imeis:
                QMessageBox.warning(
                    None,
                    "Thiếu IMEI",
                    "Thêm biến thể bắt buộc phải nhập IMEI.\n"
                    "Mỗi máy điện thoại phải có 1 IMEI."
                )
                return False

        return True

    def clear_form(self):
        self.selected_variant_id = None
        self.selected_imei_id = None

        self.set_product_name("")
        self.page.txtBrand.clear()
        self.page.txtDescription.clear()
        self.page.txtBulkImei.clear()

        self.page.spinImportPrice.setValue(0)
        self.page.spinPrice.setValue(10000000)

        self.page.tableProducts.clearSelection()
        self.page.tableImeis.setRowCount(0)

    # ======================
    # SELECTION EVENTS
    # ======================
    def on_product_selected(self):
        name = self.get_product_name()

        if not name:
            return

        info = ProductModel.get_product_info_by_name(name)

        if info:
            brand, description, base_price = info
            self.page.txtBrand.setText(brand or "")
            self.page.txtDescription.setText(description or "")

            if base_price:
                self.page.spinPrice.setValue(float(base_price))

    def select_product_row(self, row, column):
        self.selected_variant_id = int(self.page.tableProducts.item(row, 0).text())
        self.selected_imei_id = None

        self.set_product_name(self.page.tableProducts.item(row, 1).text())
        self.page.txtBrand.setText(self.page.tableProducts.item(row, 2).text())
        self.page.cboStorage.setCurrentText(self.page.tableProducts.item(row, 3).text())
        self.page.cboColor.setCurrentText(self.page.tableProducts.item(row, 4).text())

        price_text = self.page.tableProducts.item(row, 5).text()
        price_text = price_text.replace("đ", "").replace(",", "").strip()

        import_price_text = self.page.tableProducts.item(row, 6).text()
        import_price_text = import_price_text.replace("đ", "").replace(",", "").strip()

        self.page.spinPrice.setValue(float(price_text))
        self.page.spinImportPrice.setValue(float(import_price_text))
        self.page.txtDescription.setText(self.page.tableProducts.item(row, 8).text())

        self.load_imeis(self.selected_variant_id)

    def select_imei_row(self, row, column):
        self.selected_imei_id = int(self.page.tableImeis.item(row, 0).text())

    # ======================
    # CRUD VARIANT + IMEI
    # ======================
    def add_variant_with_imeis(self):
        if not self.validate_form(require_imei=True):
            return

        imeis = self.get_imei_list_from_form()

        if imeis is None:
            return

        name, brand, storage, color, price, import_price, description = self.get_form_data()

        action, variant_id = ProductModel.upsert_variant(
            name,
            brand,
            storage,
            color,
            price,
            description
        )

        success, errors = ProductModel.add_imeis_bulk(
            variant_id,
            imeis,
            import_price
        )

        self.selected_variant_id = variant_id

        if errors:
            QMessageBox.warning(
                None,
                "Kết quả nhập kho",
                f"Đã thêm {success}/{len(imeis)} IMEI.\n\n"
                f"Một số IMEI lỗi hoặc đã tồn tại:\n" + "\n".join(errors[:8])
            )
        else:
            QMessageBox.information(
                None,
                "Thành công",
                f"Đã thêm/cập nhật biến thể và nhập kho {success} IMEI.\n"
                f"Tồn kho tự động tăng theo số IMEI."
            )
            self.page.txtBulkImei.clear()

        self.refresh()

    def update_product(self):
        if not self.selected_variant_id:
            QMessageBox.warning(None, "Chưa chọn", "Vui lòng chọn biến thể cần sửa")
            return

        if not self.validate_form(require_imei=False):
            return

        name, brand, storage, color, price, import_price, description = self.get_form_data()

        ProductModel.update_full_variant(
            self.selected_variant_id,
            name,
            brand,
            storage,
            color,
            price,
            description
        )

        imeis = self.get_imei_list_from_form()

        if imeis is None:
            return

        if imeis:
            success, errors = ProductModel.add_imeis_bulk(
                self.selected_variant_id,
                imeis,
                import_price
            )

            if errors:
                QMessageBox.warning(
                    None,
                    "Cập nhật biến thể",
                    f"Đã cập nhật biến thể và thêm {success}/{len(imeis)} IMEI.\n"
                    f"Lỗi:\n" + "\n".join(errors[:8])
                )
            else:
                QMessageBox.information(
                    None,
                    "Thành công",
                    f"Đã cập nhật biến thể và thêm {success} IMEI mới"
                )
                self.page.txtBulkImei.clear()
        else:
            QMessageBox.information(None, "Thành công", "Đã cập nhật thông tin biến thể")

        self.refresh()

    def delete_product(self):
        if not self.selected_variant_id:
            QMessageBox.warning(None, "Chưa chọn", "Vui lòng chọn biến thể cần xóa")
            return

        confirm = QMessageBox.question(
            None,
            "Xác nhận",
            "Chỉ xóa được biến thể khi chưa có IMEI và chưa nằm trong hóa đơn. Bạn muốn xóa?"
        )

        if confirm != QMessageBox.StandardButton.Yes:
            return

        deleted = ProductModel.delete_variant(self.selected_variant_id)

        if not deleted:
            QMessageBox.warning(
                None,
                "Không thể xóa",
                "Biến thể đã có IMEI hoặc hóa đơn. Hãy xóa IMEI chưa bán trước."
            )
            return

        QMessageBox.information(None, "Thành công", "Đã xóa biến thể")
        self.clear_form()
        self.refresh()

    # ======================
    # IMEI ACTIONS
    # ======================
    def mark_imei_sold(self):
        if not self.selected_imei_id:
            QMessageBox.warning(None, "Chưa chọn", "Vui lòng chọn IMEI cần đổi trạng thái")
            return

        confirm = QMessageBox.question(
            None,
            "Xác nhận",
            "Đánh dấu IMEI này là đã bán?"
        )

        if confirm != QMessageBox.StandardButton.Yes:
            return

        ProductModel.update_imei_status(self.selected_imei_id, "sold")
        QMessageBox.information(None, "Thành công", "Đã đánh dấu IMEI là đã bán")
        self.refresh()

    def delete_imei(self):
        if not self.selected_imei_id:
            QMessageBox.warning(None, "Chưa chọn", "Vui lòng chọn IMEI cần xóa")
            return

        confirm = QMessageBox.question(
            None,
            "Xác nhận",
            "Bạn có chắc muốn xóa IMEI này?"
        )

        if confirm != QMessageBox.StandardButton.Yes:
            return

        ok, msg = ProductModel.delete_imei(self.selected_imei_id)

        if ok:
            QMessageBox.information(None, "Thành công", msg)
        else:
            QMessageBox.warning(None, "Không thể xóa", msg)

        self.refresh()
from pathlib import Path
import re
import json
import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass
from PyQt6.QtWidgets import (
    QMessageBox,
    QTableWidgetItem,
    QAbstractItemView,
    QFileDialog,
    QDialog,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QCompleter,
    QApplication,
)
from PyQt6.QtGui import QPixmap, QTextDocument, QPageSize
from PyQt6.QtCore import Qt, QSizeF, QStringListModel
from PyQt6.QtPrintSupport import QPrinter
import traceback
from app.models.sales_model import SalesModel
from app.models.discount_model import DiscountModel


class SalesController:
    def __init__(self, page, main_window=None):
        self.page = page
        self.main_window = main_window

        self.cart = []
        self.selected_imei_data = None
        self.selected_cart_row = None
        self.current_invoice_id = None
        self.discount_amount = 0
        self.discount_code = ""

        SalesModel.ensure_schema()
        DiscountModel.ensure_schema()
        self.setup_tables()
        self.connect_events()
        self.setup_discount_code_completer()
        self.setup_imei_completer()
        self.update_totals()

    def setup_tables(self):
        self.page.tableCart.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.page.tableCart.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )

        self.page.tableCart.setColumnWidth(0, 70)
        self.page.tableCart.setColumnWidth(1, 145)
        self.page.tableCart.setColumnWidth(2, 180)
        self.page.tableCart.setColumnWidth(3, 90)
        self.page.tableCart.setColumnWidth(4, 80)
        self.page.tableCart.setColumnWidth(5, 115)
        self.page.tableCart.setColumnWidth(6, 85)
        self.page.tableCart.horizontalHeader().setStretchLastSection(True)

    def connect_events(self):
        self.page.btnFindCustomer.clicked.connect(self.find_customer)
        self.page.btnImportCustomer.clicked.connect(self.import_customer)
        self.page.btnNewCustomer.clicked.connect(self.clear_customer)

        self.page.btnFindImei.clicked.connect(self.find_imei)
        self.page.txtImeiSearch.returnPressed.connect(self.find_imei)

        if hasattr(self.page, "btnScanImei"):
            self.page.btnScanImei.clicked.connect(self.scan_imei_from_camera)

        if hasattr(self.page, "btnAiSuggest"):
            self.page.btnAiSuggest.clicked.connect(self.ai_suggest_products)

        self.page.btnAddToCart.clicked.connect(self.add_to_cart)

        self.page.tableCart.cellClicked.connect(self.select_cart_row)
        self.page.btnRemoveCartItem.clicked.connect(self.remove_cart_item)
        self.page.btnClearCart.clicked.connect(self.clear_cart)

        self.page.btnApplyDiscount.clicked.connect(self.apply_discount)
        self.page.spinCustomerPaid.valueChanged.connect(self.update_totals)
        self.page.radioCash.toggled.connect(self.update_payment_mode)
        self.page.radioQR.toggled.connect(self.update_payment_mode)

        self.page.btnConfirmPayment.clicked.connect(self.confirm_payment)
        self.page.btnExportInvoice.clicked.connect(self.export_invoice)

        if hasattr(self.page, "btnShowQr"):
            self.page.btnShowQr.clicked.connect(self.show_qr_popup)

    def setup_discount_code_completer(self):
        try:
            import sqlite3

            conn = sqlite3.connect("lvshop.db")
            cursor = conn.cursor()

            cursor.execute("""
                SELECT code
                FROM discounts
                WHERE IFNULL(status, 'active') = 'active'
                ORDER BY code ASC
            """)

            codes = [str(row[0]) for row in cursor.fetchall() if row and row[0]]

            conn.close()

            model = QStringListModel(codes)

            completer = QCompleter()
            completer.setModel(model)
            completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            completer.setFilterMode(Qt.MatchFlag.MatchContains)
            completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)

            self.page.txtDiscountCode.setCompleter(completer)

        except Exception as e:
            print("Discount completer error:", e)

    def setup_imei_completer(self):
        try:
            data = SalesModel.search_available_imeis("")
            imeis = []

            for row in data:
                imei = row[1]
                if imei:
                    imeis.append(str(imei))

            model = QStringListModel(imeis)

            completer = QCompleter()
            completer.setModel(model)
            completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            completer.setFilterMode(Qt.MatchFlag.MatchContains)
            completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)

            self.page.txtImeiSearch.setCompleter(completer)

        except Exception as e:
            print("IMEI completer error:", e)

    def money(self, value):
        return f"{float(value):,.0f} đ"

    def get_qr_path(self):
        return Path("assets/images/qr.jpg")

    def show_qr_popup(self):
        qr_path = self.get_qr_path()

        if not qr_path.exists():
            QMessageBox.warning(
                None,
                "Không tìm thấy QR",
                "Không tìm thấy file: assets/images/qr.jpg"
            )
            return

        total = max(self.get_subtotal() - self.discount_amount, 0)

        dialog = QDialog()
        dialog.setWindowTitle("QR thanh toán")
        dialog.setMinimumSize(430, 560)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #f8fafc;
            }
            QLabel#title {
                color: #1e3a8a;
                font-size: 20px;
                font-weight: bold;
            }
            QLabel#amount {
                color: #dc2626;
                font-size: 24px;
                font-weight: bold;
            }
            QLabel#qr {
                background-color: white;
                border: 1px solid #dbeafe;
                border-radius: 18px;
                padding: 12px;
            }
            QPushButton {
                background-color: #2563eb;
                color: white;
                border: none;
                border-radius: 12px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }
        """)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(14)

        title = QLabel("🏦 Quét QR để thanh toán")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        amount = QLabel(self.money(total))
        amount.setObjectName("amount")
        amount.setAlignment(Qt.AlignmentFlag.AlignCenter)

        qr_label = QLabel()
        qr_label.setObjectName("qr")
        qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        pixmap = QPixmap(str(qr_path))
        qr_label.setPixmap(
            pixmap.scaled(
                350,
                390,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        )

        note = QLabel("Sau khi khách chuyển khoản, nhân viên bấm xác nhận thanh toán.")
        note.setAlignment(Qt.AlignmentFlag.AlignCenter)
        note.setWordWrap(True)
        note.setStyleSheet("color: #475569; font-size: 13px;")

        close_btn = QPushButton("Đóng")
        close_btn.clicked.connect(dialog.close)

        layout.addWidget(title)
        layout.addWidget(amount)
        layout.addWidget(qr_label)
        layout.addWidget(note)
        layout.addWidget(close_btn)

        dialog.exec()

    def scan_imei_from_camera(self):
        import cv2
        from pyzbar.pyzbar import decode

        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            QMessageBox.warning(
                None,
                "Lỗi camera",
                "Không mở được webcam."
            )
            return

        imei_found = None

        while True:
            ret, frame = cap.read()

            if not ret:
                break

            results = decode(frame)

            for result in results:
                raw_text = result.data.decode("utf-8", errors="ignore")
                imei = self.extract_imei(raw_text)

                if imei:
                    imei_found = imei
                    break

            cv2.imshow("Quet IMEI - Nhan Q de thoat", frame)

            if imei_found:
                break

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cap.release()
        cv2.destroyAllWindows()

        if imei_found:
            self.page.txtImeiSearch.setText(imei_found)
            self.find_imei()
        else:
            QMessageBox.information(
                None,
                "Không tìm thấy",
                "Không đọc được IMEI."
            )

    def read_imei_from_image(self, file_path):
        try:
            from PIL import Image
            from pyzbar.pyzbar import decode

            image = Image.open(file_path)
            results = decode(image)

            for result in results:
                raw_text = result.data.decode("utf-8", errors="ignore")
                imei = self.extract_imei(raw_text)

                if imei:
                    return imei

        except Exception as e:
            print("Scan IMEI error:", e)

        return None

    def extract_imei(self, text):
        if not text:
            return None

        text = str(text)
        matches = re.findall(r"\d{15}", text)

        if matches:
            return matches[0]

        only_number = re.sub(r"\D", "", text)

        if len(only_number) >= 15:
            return only_number[:15]

        return None

    def ai_suggest_products(self):
        request = self.page.txtAiRequest.text().strip()

        if not request:
            QMessageBox.warning(
                None,
                "Thiếu yêu cầu",
                "Vui lòng nhập nhu cầu khách hàng."
            )
            return

        products = SalesModel.get_available_products_for_ai()

        if not products:
            QMessageBox.information(
                None,
                "Không có hàng",
                "Hiện không có máy còn hàng."
            )
            return

        old_button_text = self.page.btnAiSuggest.text()

        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        self.page.btnAiSuggest.setEnabled(False)
        self.page.btnAiSuggest.setText("⏳ Đang AI...")
        QApplication.processEvents()

        try:
            # Ưu tiên gọi Gemini trước
            gemini_results = self.gemini_ai_filter(request, products)

        except Exception as e:
            print("AI suggest error:", e)
            gemini_results = []

        finally:
            self.page.btnAiSuggest.setEnabled(True)
            self.page.btnAiSuggest.setText(old_button_text or "🤖 Gợi ý")
            QApplication.restoreOverrideCursor()
            QApplication.processEvents()

        if gemini_results:
            self.show_ai_suggestions(
                gemini_results,
                "🤖 Gợi ý từ Gemini AI"
            )
            return

        # Nếu Gemini lỗi / không trả kết quả thì fallback local
        local_results = self.local_ai_filter(request, products)

        if local_results:
            self.show_ai_suggestions(
                local_results,
                "⚙️ Gợi ý từ bộ lọc local"
            )
            return

        # Fallback cuối cùng, không để AI bó tay
        fallback_results = self.fallback_smart_suggestions(request, products)

        if fallback_results:
            self.show_ai_suggestions(
                fallback_results,
                "🔍 Gợi ý gần phù hợp nhất"
            )
            return

        QMessageBox.information(
            None,
            "Không tìm thấy",
            "Không tìm được máy phù hợp với yêu cầu này."
        )

    def should_use_local_filter(self, request):
        text = request.lower()

        fuzzy_keywords = [
            "nữ văn phòng", "nu van phong", "máy sang", "may sang", "sang",
            "da đẹp", "da dep", "mượt", "muot", "ổn định", "on dinh",
            "ít lỗi", "it loi", "lâu dài", "lau dai", "cho mẹ", "cho me",
            "người lớn tuổi", "nguoi lon tuoi", "tiktok", "quay video",
            "edit video", "đáng tiền", "dang tien", "nâng cấp", "nang cap",
            "pin đủ 1 ngày", "pin du 1 ngay", "dùng mượt", "dung muot",
            "dùng 3 năm", "dung 3 nam", "ngân sách linh động", "ngan sach linh dong"
        ]

        if any(keyword in text for keyword in fuzzy_keywords):
            return False

        clear_keywords = [
            "iphone", "apple", "ios", "samsung", "xiaomi", "oppo", "vivo", "realme",
            "dưới", "duoi", "trên", "tren", "tầm", "tam", "khoảng", "khoang",
            "tr", "triệu", "trieu", "gb", "g",
            "tím", "tim", "trắng", "trang", "đen", "den", "xanh", "đỏ", "do",
            "vàng", "vang", "hồng", "hong", "xám", "xam", "purple", "white",
            "black", "blue", "red", "gold", "pink", "gray", "grey"
        ]

        has_clear_keyword = any(keyword in text for keyword in clear_keywords)
        has_number_price = bool(re.search(r"\d+\s*(tr|triệu|trieu)", text))
        has_storage = bool(re.search(r"\d+\s*(gb|g)", text))

        return has_clear_keyword or has_number_price or has_storage

    def local_ai_filter(self, request, products):
        text = request.lower()
        results = []

        price_max = self.extract_price_max(text)

        brand_keywords = {
            "iphone": "apple",
            "ios": "apple",
            "apple": "apple",
            "samsung": "samsung",
            "xiaomi": "xiaomi",
            "oppo": "oppo",
            "vivo": "vivo",
            "realme": "realme",
        }

        wanted_brand = None
        for keyword, brand in brand_keywords.items():
            if keyword in text:
                wanted_brand = brand
                break

        wanted_storage = None
        storage_matches = re.findall(r"(\d+)\s*(gb|g)", text)
        if storage_matches:
            wanted_storage = storage_matches[0][0]

        color_keywords = {
            "tím": "tím", "tim": "tím", "purple": "tím",
            "trắng": "trắng", "trang": "trắng", "white": "trắng",
            "đen": "đen", "den": "đen", "black": "đen",
            "xanh": "xanh", "blue": "xanh",
            "đỏ": "đỏ", "do": "đỏ", "red": "đỏ",
            "vàng": "vàng", "vang": "vàng", "gold": "vàng",
            "hồng": "hồng", "hong": "hồng", "pink": "hồng",
            "xám": "xám", "xam": "xám", "gray": "xám", "grey": "xám",
        }

        wanted_color = None
        for keyword, mapped_color in color_keywords.items():
            if keyword in text:
                wanted_color = mapped_color
                break

        for row in products:
            imei_id, imei, variant_id, product_name, brand, storage, color, price, import_price, status = row

            score = 0
            reasons = []

            brand_text = str(brand).lower()
            storage_text = str(storage).lower()
            color_text = str(color).lower()
            product_text = f"{product_name} {brand} {storage} {color}".lower()

            if wanted_brand:
                if wanted_brand in brand_text or wanted_brand in product_text:
                    score += 40
                    reasons.append(f"Đúng hãng {brand}")
                else:
                    continue

            if price_max:
                if float(price) <= price_max:
                    score += 35
                    reasons.append(f"Giá dưới {self.money(price_max)}")
                else:
                    continue

            if wanted_storage:
                if wanted_storage in storage_text:
                    score += 20
                    reasons.append(f"Dung lượng {storage}")
                else:
                    continue

            if wanted_color:
                if wanted_color in color_text:
                    score += 20
                    reasons.append(f"Màu {color}")
                else:
                    continue

            if "pin" in text or "trâu" in text or "trau" in text:
                score += 5
                reasons.append("Ưu tiên pin tốt")

            if "chụp" in text or "chup" in text or "camera" in text or "ảnh" in text or "anh" in text:
                score += 5
                reasons.append("Ưu tiên camera đẹp")

            if "game" in text or "liên quân" in text or "lien quan" in text or "pubg" in text:
                score += 5
                reasons.append("Ưu tiên chơi game")

            if score > 0:
                results.append({
                    "imei_id": imei_id,
                    "imei": imei,
                    "variant_id": variant_id,
                    "product_name": product_name,
                    "brand": brand,
                    "storage": storage,
                    "color": color,
                    "price": price,
                    "import_price": import_price,
                    "status": status,
                    "score": score,
                    "reason": ", ".join(reasons) if reasons else "Phù hợp với yêu cầu"
                })

        results.sort(key=lambda x: (-x["score"], x["price"]))
        return results[:5]

    def extract_price_max(self, text):
        text = text.lower()
        text = text.replace(",", ".")
        text = text.replace("triệu", "tr")
        text = text.replace("trieu", "tr")

        match = re.search(r"(dưới|duoi|tầm|tam|khoảng|khoang|<=|<)\s*(\d+(\.\d+)?)\s*tr", text)
        if match:
            return float(match.group(2)) * 1_000_000

        match = re.search(r"(\d+(\.\d+)?)\s*tr", text)
        if match:
            return float(match.group(1)) * 1_000_000

        match = re.search(r"(\d{7,9})", text)
        if match:
            return float(match.group(1))

        return None

    def fallback_smart_suggestions(self, request, products):
        text = request.lower()
        results = []

        for row in products:
            imei_id, imei, variant_id, product_name, brand, storage, color, price, import_price, status = row

            score = 10
            reasons = ["Gợi ý gần phù hợp nhất từ hàng còn trong kho"]
            product_text = f"{product_name} {brand} {storage} {color}".lower()

            if "iphone" in text or "sang" in text or "mượt" in text or "muot" in text or "ổn định" in text or "on dinh" in text:
                if "iphone" in product_text or "apple" in product_text:
                    score += 40
                    reasons.append("Phù hợp nhu cầu máy sang, ổn định, dễ dùng")

            if "samsung" in text and "samsung" in product_text:
                score += 40
                reasons.append("Đúng nhu cầu Samsung")

            if "chụp" in text or "chup" in text or "camera" in text or "tiktok" in text or "ảnh" in text or "anh" in text:
                score += 15
                reasons.append("Phù hợp nhu cầu chụp ảnh / quay video")

            if "pin" in text or "1 ngày" in text or "1 ngay" in text or "lâu" in text or "lau" in text:
                score += 10
                reasons.append("Ưu tiên máy dùng ổn trong ngày")

            if "mẹ" in text or "me" in text or "người lớn" in text or "nguoi lon" in text:
                score += 10
                reasons.append("Phù hợp nhu cầu dễ dùng")

            results.append({
                "imei_id": imei_id,
                "imei": imei,
                "variant_id": variant_id,
                "product_name": product_name,
                "brand": brand,
                "storage": storage,
                "color": color,
                "price": price,
                "import_price": import_price,
                "status": status,
                "score": score,
                "reason": ", ".join(reasons)
            })

        results.sort(key=lambda x: (-x["score"], x["price"]))
        return results[:5]

    def gemini_ai_filter(self, request, products):
        try:
            from google import genai

            api_key = os.getenv("GEMINI_API_KEY")

            if not api_key:
                print("Gemini error: chưa có GEMINI_API_KEY")
                return []

            product_lines = []

            for row in products[:100]:
                imei_id, imei, variant_id, product_name, brand, storage, color, price, import_price, status = row
                product_lines.append({
                    "imei_id": imei_id,
                    "imei": imei,
                    "variant_id": variant_id,
                    "product_name": product_name,
                    "brand": brand,
                    "storage": storage,
                    "color": color,
                    "price": price,
                    "status": status
                })

            prompt = f"""
Bạn là AI tư vấn bán điện thoại cho cửa hàng LV SHOP.
Khách hàng yêu cầu:
{request}

Danh sách máy còn hàng dạng JSON:
{json.dumps(product_lines, ensure_ascii=False)}

Nhiệm vụ:
- Bắt buộc phải chọn tối đa 5 máy gần phù hợp nhất từ danh sách, kể cả khi yêu cầu mơ hồ.
- Chỉ được chọn IMEI có trong danh sách.
- Ưu tiên đúng nhu cầu khách: ngân sách, hãng, màu, dung lượng, camera, pin, độ ổn định, đối tượng sử dụng.
- Nếu không có máy khớp hoàn toàn, chọn máy gần phù hợp nhất và ghi rõ lý do.

Chỉ trả về JSON array hợp lệ, không thêm chữ ngoài JSON.
Mỗi item gồm đúng các khóa: imei, reason, score

Ví dụ:
[
  {{"imei": "352761234567890", "reason": "Đúng nhu cầu iPhone dưới 10 triệu", "score": 95}}
]
"""

            client = genai.Client(api_key=api_key)

            print(">>> CALLING GEMINI API...")

            try:
                response = client.models.generate_content(
                    model=os.getenv("GEMINI_MODEL", "gemini-2.5-pro"),
                    contents=prompt
                )
            except Exception as pro_error:
                print("Gemini Pro error, fallback Flash:", pro_error)
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )

            print("RAW GEMINI:", response.text)

            raw = response.text.strip()
            raw = raw.replace("```json", "").replace("```", "").strip()

            json_match = re.search(r"\[.*\]", raw, re.DOTALL)
            if json_match:
                raw = json_match.group(0)

            ai_items = json.loads(raw)

            product_map = {str(row[1]): row for row in products}
            results = []

            for item in ai_items:
                imei = str(item.get("imei", "")).strip()

                if imei not in product_map:
                    continue

                row = product_map[imei]
                imei_id, imei, variant_id, product_name, brand, storage, color, price, import_price, status = row

                results.append({
                    "imei_id": imei_id,
                    "imei": imei,
                    "variant_id": variant_id,
                    "product_name": product_name,
                    "brand": brand,
                    "storage": storage,
                    "color": color,
                    "price": price,
                    "import_price": import_price,
                    "status": status,
                    "score": item.get("score", 0),
                    "reason": item.get("reason", "Gemini gợi ý phù hợp")
                })

            return results[:5]

        except Exception as e:
            print("Gemini AI error:", e)
            print(traceback.format_exc())
            return []

    def show_ai_suggestions(self, results, title):
        from PyQt6.QtWidgets import QInputDialog

        lines = []

        for index, item in enumerate(results, start=1):
            lines.append(
                f"{index}. {item['product_name']} - {item['storage']} - {item['color']}\n"
                f"   IMEI: {item['imei']}\n"
                f"   Giá: {self.money(item['price'])}\n"
                f"   Lý do: {item['reason']}\n"
            )

        message = "\n".join(lines)
        message += "\nNhập số thứ tự máy muốn chọn:"

        number, ok = QInputDialog.getInt(
            None,
            title,
            message,
            1,
            1,
            len(results),
            1
        )

        if not ok:
            return

        selected = results[number - 1]
        self.page.txtImeiSearch.setText(str(selected["imei"]))
        self.find_imei()


    def update_payment_mode(self):
        if self.page.radioQR.isChecked():
            self.page.spinCustomerPaid.setEnabled(False)
            self.page.lblChangeValue.setText("0 đ")
            self.show_qr_popup()
        else:
            self.page.spinCustomerPaid.setEnabled(True)

        self.update_totals()

    def find_customer(self):
        phone = self.page.txtCustomerPhone.text().strip()

        if not phone:
            QMessageBox.warning(None, "Thiếu SĐT", "Vui lòng nhập số điện thoại khách hàng")
            return

        customer = SalesModel.find_customer_by_phone(phone)

        if not customer:
            QMessageBox.information(
                None,
                "Khách mới",
                "Không tìm thấy khách hàng. Bạn có thể nhập thông tin mới."
            )
            return

        customer_id, name, phone, email, address = customer

        self.page.txtCustomerName.setText(name or "")
        self.page.txtCustomerPhone.setText(phone or "")
        self.page.txtCustomerEmail.setText(email or "")
        self.page.txtCustomerAddress.setText(address or "")

        QMessageBox.information(None, "Tìm thấy", "Đã tải thông tin khách hàng cũ")

    def import_customer(self):
        name = self.page.txtCustomerName.text().strip()
        phone = self.page.txtCustomerPhone.text().strip()
        email = self.page.txtCustomerEmail.text().strip()
        address = self.page.txtCustomerAddress.text().strip()

        if not phone:
            QMessageBox.warning(None, "Thiếu SĐT", "Vui lòng nhập số điện thoại")
            return

        if not name:
            QMessageBox.warning(None, "Thiếu tên", "Vui lòng nhập tên khách hàng")
            return

        SalesModel.upsert_customer(name, phone, email, address)
        QMessageBox.information(None, "Thành công", "Đã lưu/import khách hàng vào hệ thống")

    def clear_customer(self):
        self.page.txtCustomerName.clear()
        self.page.txtCustomerPhone.clear()
        self.page.txtCustomerEmail.clear()
        self.page.txtCustomerAddress.clear()

    def find_imei(self):
        imei = self.page.txtImeiSearch.text().strip()

        if not imei:
            QMessageBox.warning(None, "Thiếu IMEI", "Vui lòng nhập IMEI cần bán")
            return

        imei_data = SalesModel.find_imei_for_sale(imei)

        if not imei_data:
            self.selected_imei_data = None
            self.clear_selected_product()
            QMessageBox.warning(None, "Không tìm thấy", "Không tìm thấy IMEI trong kho")
            return

        status = imei_data[9]

        if status != "in_stock":
            self.selected_imei_data = None
            self.clear_selected_product()
            QMessageBox.warning(None, "Không thể bán", f"IMEI này đang có trạng thái: {status}")
            return

        self.selected_imei_data = imei_data
        self.fill_product_from_imei(imei_data)

    def fill_product_from_imei(self, data):
        imei_id, imei, variant_id, product_name, brand, storage, color, price, import_price, status = data

        self.page.txtProductName.setText(product_name)
        self.page.txtSelectedImei.setText(imei)
        self.page.txtBrand.setText(brand)
        self.page.txtVariantInfo.setText(f"{storage} / {color}")
        self.page.spinSalePrice.setValue(float(price))

    def clear_selected_product(self):
        self.selected_imei_data = None
        self.page.txtProductName.clear()
        self.page.txtSelectedImei.clear()
        self.page.txtBrand.clear()
        self.page.txtVariantInfo.clear()
        self.page.spinSalePrice.setValue(0)

    def add_to_cart(self):
        if not self.selected_imei_data:
            QMessageBox.warning(None, "Chưa chọn IMEI", "Vui lòng tìm IMEI cần bán")
            return

        imei_id, imei, variant_id, product_name, brand, storage, color, price, import_price, status = self.selected_imei_data

        for item in self.cart:
            if item["imei_id"] == imei_id:
                QMessageBox.warning(None, "Trùng IMEI", "IMEI này đã có trong giỏ hàng")
                return

        sale_price = self.page.spinSalePrice.value()
        warranty_month = self.page.spinWarrantyMonth.value()

        if sale_price <= 0:
            QMessageBox.warning(None, "Lỗi giá", "Giá bán phải lớn hơn 0")
            return

        self.cart.append({
            "imei_id": imei_id,
            "imei": imei,
            "variant_id": variant_id,
            "product_name": product_name,
            "brand": brand,
            "storage": storage,
            "color": color,
            "price": sale_price,
            "warranty_month": warranty_month
        })

        self.render_cart()
        self.clear_selected_product()
        self.page.txtImeiSearch.clear()
        self.update_totals()

    def render_cart(self):
        self.page.tableCart.setRowCount(0)

        for item in self.cart:
            row = self.page.tableCart.rowCount()
            self.page.tableCart.insertRow(row)

            values = [
                item["imei_id"],
                item["imei"],
                item["product_name"],
                item["storage"],
                item["color"],
                self.money(item["price"]),
                f"{item['warranty_month']} tháng",
                self.money(item["price"])
            ]

            for col, value in enumerate(values):
                self.page.tableCart.setItem(row, col, QTableWidgetItem(str(value)))

    def select_cart_row(self, row, column):
        self.selected_cart_row = row

    def remove_cart_item(self):
        if self.selected_cart_row is None:
            QMessageBox.warning(None, "Chưa chọn", "Vui lòng chọn dòng cần xóa")
            return

        if 0 <= self.selected_cart_row < len(self.cart):
            self.cart.pop(self.selected_cart_row)

        self.selected_cart_row = None
        self.render_cart()
        self.update_totals()

    def clear_cart(self):
        self.cart.clear()
        self.selected_cart_row = None
        self.render_cart()
        self.update_totals()

    def get_subtotal(self):
        return sum(item["price"] for item in self.cart)

    def apply_discount(self):
        code = self.page.txtDiscountCode.text().strip()
        subtotal = self.get_subtotal()

        if not code:
            self.discount_code = ""
            self.discount_amount = 0
            self.update_totals()
            QMessageBox.information(None, "Mã giảm giá", "Đã bỏ mã giảm giá")
            return

        if subtotal <= 0:
            QMessageBox.warning(None, "Chưa có hàng", "Vui lòng thêm sản phẩm vào giỏ trước")
            return

        ok, msg, discount_amount = DiscountModel.validate_code(code, subtotal)

        if not ok:
            self.discount_code = ""
            self.discount_amount = 0
            self.update_totals()
            QMessageBox.warning(None, "Mã không hợp lệ", msg)
            return

        self.discount_code = code.upper()
        self.discount_amount = discount_amount
        self.update_totals()

        QMessageBox.information(
            None,
            "Áp mã thành công",
            f"{msg}\nGiảm: {self.money(discount_amount)}"
        )

    def update_totals(self):
        subtotal = self.get_subtotal()
        total = max(subtotal - self.discount_amount, 0)

        self.page.lblSubtotalValue.setText(self.money(subtotal))
        self.page.lblDiscountValue.setText(self.money(self.discount_amount))
        self.page.lblTotalValue.setText(self.money(total))

        if self.page.radioCash.isChecked():
            paid = self.page.spinCustomerPaid.value()
            change = max(paid - total, 0)
            self.page.lblChangeValue.setText(self.money(change))
        else:
            self.page.lblChangeValue.setText("0 đ")

    def validate_before_payment(self):
        if not self.cart:
            QMessageBox.warning(None, "Giỏ hàng trống", "Vui lòng thêm sản phẩm vào giỏ hàng")
            return False

        name = self.page.txtCustomerName.text().strip()
        phone = self.page.txtCustomerPhone.text().strip()

        if not name:
            QMessageBox.warning(None, "Thiếu khách hàng", "Vui lòng nhập tên khách hàng")
            return False

        if not phone:
            QMessageBox.warning(None, "Thiếu SĐT", "Vui lòng nhập số điện thoại khách hàng")
            return False

        total = max(self.get_subtotal() - self.discount_amount, 0)

        if self.page.radioCash.isChecked():
            paid = self.page.spinCustomerPaid.value()

            if paid < total:
                QMessageBox.warning(None, "Chưa đủ tiền", "Số tiền khách đưa chưa đủ")
                return False

        return True

    def confirm_payment(self):
        if not self.validate_before_payment():
            return

        subtotal = self.get_subtotal()
        total = max(subtotal - self.discount_amount, 0)

        if self.page.radioCash.isChecked():
            payment_method = "cash"
            paid_amount = self.page.spinCustomerPaid.value()
            change_amount = max(paid_amount - total, 0)
            confirm_text = "Xác nhận đã nhận đủ tiền mặt?"
        else:
            payment_method = "qr"
            paid_amount = total
            change_amount = 0
            confirm_text = "Xác nhận khách đã chuyển khoản QR thành công?"

        confirm = QMessageBox.question(None, "Xác nhận thanh toán", confirm_text)

        if confirm != QMessageBox.StandardButton.Yes:
            return

        customer_data = {
            "name": self.page.txtCustomerName.text().strip(),
            "phone": self.page.txtCustomerPhone.text().strip(),
            "email": self.page.txtCustomerEmail.text().strip(),
            "address": self.page.txtCustomerAddress.text().strip()
        }

        user_id = None
        if self.main_window and getattr(self.main_window, "current_user", None):
            user_id = self.main_window.current_user[0]

        payment_data = {
            "subtotal": subtotal,
            "discount_code": self.discount_code,
            "discount_amount": self.discount_amount,
            "total_price": total,
            "payment_method": payment_method,
            "paid_amount": paid_amount,
            "change_amount": change_amount
        }

        ok, invoice_id, msg = SalesModel.create_invoice(
            customer_data,
            self.cart,
            payment_data,
            user_id
        )

        if not ok:
            QMessageBox.critical(None, "Lỗi tạo hóa đơn", msg)
            return

        self.current_invoice_id = invoice_id
        if self.discount_code and self.discount_amount > 0:
            DiscountModel.record_usage(
                self.discount_code,
                subtotal,
                self.discount_amount
            )

        QMessageBox.information(
            None,
            "Thanh toán thành công",
            f"Đã tạo hóa đơn #{invoice_id}\n"
            f"IMEI đã được chuyển sang trạng thái sold.\n"
            f"Phiếu bảo hành đã được tạo tự động."
        )

        self.clear_cart()
        self.clear_selected_product()
        self.page.txtDiscountCode.clear()
        self.discount_amount = 0
        self.discount_code = ""
        self.page.spinCustomerPaid.setValue(0)
        self.update_totals()

    def export_invoice(self):
        try:
            if not self.current_invoice_id:
                QMessageBox.warning(
                    None,
                    "Chưa có hóa đơn",
                    "Vui lòng thanh toán thành công trước khi xuất hóa đơn"
                )
                return

            invoice, items = SalesModel.get_invoice_detail(self.current_invoice_id)

            if not invoice:
                QMessageBox.warning(None, "Lỗi", "Không tìm thấy hóa đơn")
                return

            default_name = f"hoa_don_{self.current_invoice_id}.pdf"

            file_path, _ = QFileDialog.getSaveFileName(
                None,
                "Xuất hóa đơn PDF",
                default_name,
                "PDF Files (*.pdf)"
            )

            if not file_path:
                return

            if not file_path.lower().endswith(".pdf"):
                file_path += ".pdf"

            html = self.build_invoice_html(invoice, items)

            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
            printer.setOutputFileName(file_path)
            printer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))

            document = QTextDocument()
            document.setHtml(html)
            document.setPageSize(QSizeF(printer.pageRect(QPrinter.Unit.Point).size()))

            document.print(printer)

            QMessageBox.information(
                None,
                "Thành công",
                f"Đã xuất hóa đơn PDF:\n{file_path}"
            )

        except Exception as e:
            error_detail = traceback.format_exc()
            print(error_detail)

            QMessageBox.critical(
                None,
                "Lỗi xuất hóa đơn",
                f"Không thể xuất hóa đơn PDF:\n{e}"
            )

    def build_invoice_html(self, invoice, items):
        (
            invoice_id,
            created_at,
            customer_name,
            customer_phone,
            customer_email,
            customer_address,
            subtotal,
            discount_code,
            discount_amount,
            total_price,
            payment_method,
            paid_amount,
            change_amount,
            staff_name
        ) = invoice

        rows = ""

        for idx, item in enumerate(items, start=1):
            product_name, storage, color, imei, price, warranty_month = item

            rows += f"""
            <tr>
                <td>{idx}</td>
                <td>
                    <b>{product_name}</b><br>
                    <span class="muted">{storage} - {color}</span>
                </td>
                <td>{imei}</td>
                <td>{warranty_month} tháng</td>
                <td class="right">{self.money(price)}</td>
            </tr>
            """

        payment_text = "Tiền mặt" if payment_method == "cash" else "QR chuyển khoản"

        return f"""
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    color: #0f172a;
                    font-size: 12px;
                }}

                .header {{
                    text-align: center;
                    margin-bottom: 18px;
                }}

                .shop-name {{
                    font-size: 28px;
                    font-weight: bold;
                    color: #1e3a8a;
                    letter-spacing: 1px;
                }}

                .subtitle {{
                    color: #64748b;
                    margin-top: 4px;
                    font-size: 12px;
                }}

                .invoice-title {{
                    margin-top: 18px;
                    font-size: 22px;
                    font-weight: bold;
                    color: #dc2626;
                }}

                .box {{
                    border: 1px solid #dbeafe;
                    border-radius: 10px;
                    padding: 12px;
                    margin-bottom: 12px;
                }}

                .grid {{
                    width: 100%;
                }}

                .grid td {{
                    padding: 4px 6px;
                    vertical-align: top;
                }}

                .label {{
                    color: #475569;
                    font-weight: bold;
                    width: 120px;
                }}

                table.items {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 10px;
                }}

                table.items th {{
                    background-color: #1e3a8a;
                    color: white;
                    padding: 8px;
                    border: 1px solid #1e3a8a;
                }}

                table.items td {{
                    padding: 8px;
                    border: 1px solid #dbeafe;
                }}

                .right {{
                    text-align: right;
                }}

                .muted {{
                    color: #64748b;
                    font-size: 11px;
                }}

                .total-box {{
                    margin-top: 14px;
                    width: 100%;
                }}

                .total-box td {{
                    padding: 5px 8px;
                }}

                .total-label {{
                    text-align: right;
                    font-weight: bold;
                    color: #334155;
                }}

                .total-value {{
                    text-align: right;
                    width: 170px;
                }}

                .grand-total {{
                    color: #dc2626;
                    font-size: 20px;
                    font-weight: bold;
                }}

                .signatures {{
                    margin-top: 35px;
                    width: 100%;
                    text-align: center;
                }}

                .signatures td {{
                    width: 50%;
                    padding-top: 10px;
                    font-weight: bold;
                }}

                .footer {{
                    margin-top: 28px;
                    text-align: center;
                    color: #475569;
                    font-style: italic;
                }}
            </style>
        </head>

        <body>
            <div class="header">
                <div class="shop-name">LV SHOP</div>
                <div class="subtitle">Chuyên điện thoại chính hãng - Bảo hành theo IMEI</div>
                <div class="invoice-title">HÓA ĐƠN BÁN HÀNG</div>
            </div>

            <div class="box">
                <table class="grid">
                    <tr>
                        <td class="label">Mã hóa đơn:</td>
                        <td>#{invoice_id}</td>
                        <td class="label">Ngày bán:</td>
                        <td>{created_at}</td>
                    </tr>
                    <tr>
                        <td class="label">Nhân viên:</td>
                        <td>{staff_name}</td>
                        <td class="label">Thanh toán:</td>
                        <td>{payment_text}</td>
                    </tr>
                </table>
            </div>

            <div class="box">
                <table class="grid">
                    <tr>
                        <td class="label">Khách hàng:</td>
                        <td>{customer_name}</td>
                        <td class="label">SĐT:</td>
                        <td>{customer_phone}</td>
                    </tr>
                    <tr>
                        <td class="label">Email:</td>
                        <td>{customer_email or ""}</td>
                        <td class="label">Địa chỉ:</td>
                        <td>{customer_address or ""}</td>
                    </tr>
                </table>
            </div>

            <table class="items">
                <thead>
                    <tr>
                        <th>STT</th>
                        <th>Sản phẩm</th>
                        <th>IMEI</th>
                        <th>Bảo hành</th>
                        <th>Thành tiền</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>

            <table class="total-box">
                <tr>
                    <td class="total-label">Tạm tính:</td>
                    <td class="total-value">{self.money(subtotal)}</td>
                </tr>
                <tr>
                    <td class="total-label">Mã giảm giá:</td>
                    <td class="total-value">{discount_code or "Không"}</td>
                </tr>
                <tr>
                    <td class="total-label">Giảm giá:</td>
                    <td class="total-value">{self.money(discount_amount)}</td>
                </tr>
                <tr>
                    <td class="total-label">Khách đã trả:</td>
                    <td class="total-value">{self.money(paid_amount)}</td>
                </tr>
                <tr>
                    <td class="total-label">Trả lại:</td>
                    <td class="total-value">{self.money(change_amount)}</td>
                </tr>
                <tr>
                    <td class="total-label grand-total">Tổng thanh toán:</td>
                    <td class="total-value grand-total">{self.money(total_price)}</td>
                </tr>
            </table>

            <table class="signatures">
                <tr>
                    <td>Khách hàng</td>
                    <td>Nhân viên bán hàng</td>
                </tr>
                <tr>
                    <td><br><br><br>{customer_name}</td>
                    <td><br><br><br>{staff_name}</td>
                </tr>
            </table>

            <div class="footer">
                Cảm ơn quý khách đã mua hàng tại LV SHOP!
            </div>
        </body>
        </html>
        """

    def build_invoice_text(self, invoice, items):
        (
            invoice_id,
            created_at,
            customer_name,
            customer_phone,
            customer_email,
            customer_address,
            subtotal,
            discount_code,
            discount_amount,
            total_price,
            payment_method,
            paid_amount,
            change_amount,
            staff_name
        ) = invoice

        lines = []
        lines.append("LV SHOP - HÓA ĐƠN BÁN HÀNG")
        lines.append("=" * 45)
        lines.append(f"Mã hóa đơn: #{invoice_id}")
        lines.append(f"Ngày tạo: {created_at}")
        lines.append(f"Nhân viên bán hàng: {staff_name}")
        lines.append("")
        lines.append("THÔNG TIN KHÁCH HÀNG")
        lines.append(f"Họ tên: {customer_name}")
        lines.append(f"SĐT: {customer_phone}")
        lines.append(f"Email: {customer_email or ''}")
        lines.append(f"Địa chỉ: {customer_address or ''}")
        lines.append("")
        lines.append("SẢN PHẨM")
        lines.append("-" * 45)

        for idx, item in enumerate(items, start=1):
            product_name, storage, color, imei, price, warranty_month = item
            lines.append(f"{idx}. {product_name} - {storage} - {color}")
            lines.append(f"   IMEI: {imei}")
            lines.append(f"   Giá: {self.money(price)}")
            lines.append(f"   Bảo hành: {warranty_month} tháng")

        lines.append("")
        lines.append("-" * 45)
        lines.append(f"Tạm tính: {self.money(subtotal)}")
        lines.append(f"Mã giảm giá: {discount_code or 'Không'}")
        lines.append(f"Giảm giá: {self.money(discount_amount)}")
        lines.append(f"Tổng thanh toán: {self.money(total_price)}")
        lines.append(f"Phương thức: {'Tiền mặt' if payment_method == 'cash' else 'QR chuyển khoản'}")
        lines.append(f"Khách đã trả: {self.money(paid_amount)}")
        lines.append(f"Trả lại: {self.money(change_amount)}")
        lines.append("=" * 45)
        lines.append("Cảm ơn quý khách!")

        return "\n".join(lines)

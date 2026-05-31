import json
import os
import re
import traceback
from datetime import datetime

from app.models.database import get_connection
from app.models.user_model import UserModel

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass


class CustomerPortalModel:
    @staticmethod
    def resolve_customer(user):
        return UserModel.ensure_customer_profile(user)

    @staticmethod
    def get_available_products(keyword=""):
        conn = get_connection()
        cursor = conn.cursor()

        keyword = f"%{keyword.strip()}%"

        cursor.execute("""
            SELECT
                pv.id,
                p.name,
                IFNULL(p.brand, ''),
                IFNULL(s.name, ''),
                IFNULL(c.name, ''),
                IFNULL(pv.price, 0),
                IFNULL(p.description, ''),
                (
                    SELECT COUNT(*)
                    FROM product_imeis pi
                    WHERE pi.variant_id = pv.id
                      AND pi.status = 'in_stock'
                ) AS stock_count
            FROM product_variants pv
            JOIN products p ON pv.product_id = p.id
            JOIN storages s ON pv.storage_id = s.id
            JOIN colors c ON pv.color_id = c.id
            WHERE stock_count > 0
              AND (
                    p.name LIKE ?
                    OR p.brand LIKE ?
                    OR s.name LIKE ?
                    OR c.name LIKE ?
                    OR p.description LIKE ?
              )
            ORDER BY p.name ASC, pv.price ASC
        """, (keyword, keyword, keyword, keyword, keyword))

        data = cursor.fetchall()
        conn.close()
        return data

    @staticmethod
    def get_purchase_history(customer_id):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                i.id,
                i.created_at,
                IFNULL(ii.product_name, ''),
                IFNULL(ii.storage, ''),
                IFNULL(ii.color, ''),
                IFNULL(ii.imei, ''),
                IFNULL(ii.price, 0),
                IFNULL(ii.warranty_month, 12),
                IFNULL(i.payment_method, ''),
                IFNULL(i.status, '')
            FROM invoices i
            JOIN invoice_items ii ON ii.invoice_id = i.id
            WHERE i.customer_id = ?
            ORDER BY i.id DESC, ii.id DESC
        """, (customer_id,))

        data = cursor.fetchall()
        conn.close()
        return data

    @staticmethod
    def get_warranty_status(customer_id, imei_keyword=""):
        conn = get_connection()
        cursor = conn.cursor()

        keyword = f"%{imei_keyword.strip()}%"

        cursor.execute("""
            SELECT
                w.id,
                IFNULL(w.invoice_item_id, 0),
                IFNULL(w.imei, ''),
                IFNULL(w.product_name, ''),
                IFNULL(w.start_date, ''),
                IFNULL(w.end_date, ''),
                IFNULL(w.status, ''),
                IFNULL(w.receive_date, ''),
                IFNULL(w.return_date, ''),
                IFNULL(w.issue, ''),
                IFNULL(w.tech_note, '')
            FROM warranties w
            WHERE w.customer_id = ?
              AND IFNULL(w.imei, '') LIKE ?
            ORDER BY w.invoice_item_id DESC, w.id ASC
        """, (customer_id, keyword))

        data = cursor.fetchall()
        conn.close()
        return data

    @staticmethod
    def get_context_for_ai(customer_id):
        products = CustomerPortalModel.get_available_products("")[:50]
        purchases = CustomerPortalModel.get_purchase_history(customer_id)[:30]
        warranties = CustomerPortalModel.get_warranty_status(customer_id, "")[:30]
        return products, purchases, warranties

    @staticmethod
    def ask_gemini(customer_id, question):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return False, "Chưa cấu hình GEMINI_API_KEY trong file .env."

        try:
            from google import genai

            products, purchases, warranties = CustomerPortalModel.get_context_for_ai(customer_id)

            product_rows = [
                {
                    "name": row[1],
                    "brand": row[2],
                    "storage": row[3],
                    "color": row[4],
                    "price": row[5],
                    "availability": "Còn hàng",
                }
                for row in products
            ]

            purchase_rows = [
                {
                    "invoice_id": row[0],
                    "date": row[1],
                    "product": row[2],
                    "storage": row[3],
                    "color": row[4],
                    "imei": row[5],
                    "price": row[6],
                    "warranty_month": row[7],
                    "status": row[9],
                }
                for row in purchases
            ]

            warranty_rows = [
                {
                    "imei": row[0],
                    "product": row[1],
                    "start_date": row[2],
                    "end_date": row[3],
                    "status": row[4],
                    "receive_date": row[5],
                    "return_date": row[6],
                    "issue": row[7],
                    "tech_note": row[8],
                }
                for row in warranties
            ]

            prompt = f"""
Bạn là trợ lý AI của LV SHOP. Trả lời bằng tiếng Việt, ngắn gọn, đúng dữ liệu cửa hàng.

Câu hỏi của khách:
{question}

Sản phẩm đang bán:
{json.dumps(product_rows, ensure_ascii=False)}

Lịch sử mua của khách:
{json.dumps(purchase_rows, ensure_ascii=False)}

Bảo hành của khách:
{json.dumps(warranty_rows, ensure_ascii=False)}

Quy tắc:
- Không bịa sản phẩm, IMEI, hóa đơn hoặc trạng thái bảo hành ngoài dữ liệu trên.
- Nếu thiếu dữ liệu, nói rõ cần liên hệ cửa hàng để kiểm tra thêm.
- Khi tư vấn mua hàng, ưu tiên sản phẩm còn hàng trong danh sách.
- Tuyệt đối không nói số lượng tồn kho, không dùng các cụm như "còn 1", "còn 2", "còn X máy".
- Với sản phẩm trong danh sách, chỉ được nói trạng thái chung là "còn hàng".
- Không tiết lộ dữ liệu nội bộ như số lượng tồn, giá nhập, hoặc danh sách IMEI hàng chưa bán.
"""

            client = genai.Client(api_key=api_key)
            try:
                response = client.models.generate_content(
                    model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
                    contents=prompt
                )
            except Exception:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )

            text = (response.text or "").strip()
            return True, text or "AI chưa trả về nội dung."

        except Exception as e:
            print("Customer Gemini error:", e)
            print(traceback.format_exc())
            return False, f"Lỗi khi gọi Gemini: {e}"

    @staticmethod
    def warranty_remaining_text(end_date):
        if not end_date:
            return "Chưa có hạn bảo hành"

        try:
            end = datetime.strptime(str(end_date)[:10], "%Y-%m-%d").date()
            days = (end - datetime.now().date()).days
            if days < 0:
                return f"Hết bảo hành {abs(days)} ngày"
            if days == 0:
                return "Hết hạn hôm nay"
            return f"Còn {days} ngày"
        except Exception:
            return "Không xác định"

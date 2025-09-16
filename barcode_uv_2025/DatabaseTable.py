import pandas as pd
import datetime
from fpdf import FPDF
import sqlite3
import base64
import eel
import json


class PDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 8)
        self.cell(0, 7, 'Datentabelle', 0, 1, 'C')

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 7, f'Seite {self.page_no()}', 0, 0, 'C')


eel.init('web')

DB_PATH = "barcode_data.db"


def get_db_connection():
    return sqlite3.connect(DB_PATH)


@eel.expose
def get_items():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT i.item_id, b.box_name, p.barcode, p.product_name,
                i.quantity, i.expiration_date, i.count, i.image
        FROM items i
        JOIN boxes b ON i.box_id = b.box_id
        JOIN products p ON i.product_id = p.product_id
    ''')
    items = cursor.fetchall()
    conn.close()

    items_list = []
    for row in items:
        items_list.append({
            "item_id": row[0],
            "box_name": row[1],
            "barcode": row[2],
            "product_name": row[3],
            "quantity": row[4],
            "expiration_date": row[5],
            "count": row[6],
            "image": base64.b64encode(row[7]).decode('utf-8') if row[7] else None
        })
    return json.dumps(items_list)


@eel.expose
def update_item(item_id, field, value):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"UPDATE items SET {field} = ? WHERE item_id = ?", (value, item_id))
    conn.commit()
    conn.close()
    return json.dumps({"message": "Updated successfully"})


@eel.expose
def turn_camera_on():
    from ArticleScanner import cam
    c = cam()
    print("An")


@eel.expose
def start_scanner(box_name: str, cam_index_or_url: str):
    from ArticleScanner import cam
    cam(box_name=box_name, cam=cam_index_or_url)


@eel.expose
def delete_item(item_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM items WHERE item_id = ?", (item_id,))
    conn.commit()
    conn.close()
    return json.dumps({"message": "Deleted successfully"})


@eel.expose
def save_pdf(data):
    """data kommt als Liste von Dicts aus JS"""
    if isinstance(data, str):
        data = json.loads(data)

    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=8)

    headers = ["ID", "BARCODE", "BOX", "NAME", "QUANTITY", "EXPIRY_DATE", "COUNT"]
    column_widths = [20, 40, 30, 40, 25, 35, 20]

    # Header schreiben
    for header, width in zip(headers, column_widths):
        pdf.cell(width, 10, header, border=1)
    pdf.ln()

    # Daten schreiben
    for row in data:
        values = [
            row["item_id"],
            row["barcode"],
            row["box_name"],
            row["product_name"],
            row["quantity"],
            row["expiration_date"],
            row["count"],
        ]
        for val, width in zip(values, column_widths):
            pdf.cell(width, 10, str(val), border=1)
        pdf.ln()

    file_name = datetime.datetime.now().strftime("DATA_%Y-%m-%d_%H-%M-%S") + ".pdf"
    pdf.output(file_name)
    return json.dumps({"message": f"PDF gespeichert: {file_name}"})


@eel.expose
def save_excel(data):
    """data kommt als Liste von Dicts aus JS"""
    if isinstance(data, str):
        data = json.loads(data)

    df = pd.DataFrame(data)
    file_name = datetime.datetime.now().strftime("DATA_%Y-%m-%d_%H-%M-%S") + ".xlsx"
    df.to_excel(file_name, index=False)
    return json.dumps({"message": f"Excel gespeichert: {file_name}"})


if __name__ == "__main__":
    eel.start('index.html', host='0.0.0.0', port=8001, size=(1000, 600), block=True, mode='none')

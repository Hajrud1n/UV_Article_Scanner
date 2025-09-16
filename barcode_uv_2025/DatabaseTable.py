import sqlite3
import base64
import eel
import json

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

    # Konvert BLOBs into Base64 for the database
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
    from KellerScanner2025 import cam
    c = cam()
    print("An")

@eel.expose
def start_scanner(box_name: str, cam_index_or_url: str):
    """
    Startet den Barcode Scanner.
    Kann von JS/GUI aufgerufen werden.
    """
    cam(box_name=box_name, cam=cam_index_or_url)

@eel.expose
def delete_item(item_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM items WHERE item_id = ?", (item_id,))
    conn.commit()
    conn.close()
    return json.dumps({"message": "Deleted successfully"})

if __name__ == "__main__":
    eel.start('index.html', host='0.0.0.0', port=8001, size=(1000, 600), block=True, mode='none')

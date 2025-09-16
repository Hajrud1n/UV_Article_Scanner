import os
import urllib.request
import sqlite3
import requests
import cv2
from pyzbar import pyzbar
import time
import sys




def cam(box_name=None, cam=None):
    # In Case didnt put Parameter  Input in Terminal
    if box_name is None:
        box_name = input("Enter the box name: ")
    if cam is None:
        cam = input("Enter cam index or url: ")


    # -------------------------------
    # Setup
    # -------------------------------
    last_saved = {}
    SAVE_INTERVAL = 10  # Seconds
    saved_data = []
    image_folder = 'images'
    os.makedirs(image_folder, exist_ok=True)
    db_filename = 'barcode_data.db'

    # -------------------------------
    # DB-Verbindung & Tabellen erstellen
    # -------------------------------
    def get_db_connection():
        return sqlite3.connect(db_filename)

    def create_tables():
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS boxes (
                box_id INTEGER PRIMARY KEY AUTOINCREMENT,
                box_name TEXT UNIQUE NOT NULL,
                store TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                barcode TEXT UNIQUE NOT NULL,
                product_name TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS items (
                item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                box_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity TEXT,
                expiration_date TEXT,
                image BLOB,
                count INTEGER DEFAULT 1,
                FOREIGN KEY (box_id) REFERENCES boxes (box_id),
                FOREIGN KEY (product_id) REFERENCES products (product_id)
            )
        ''')

        conn.commit()
        conn.close()
        print("Database created.")

    # -------------------------------
    # User ask for Box-Name
    # -------------------------------
    #box_name = input("Enter the box name: ")
    #cam = input("Enter cam index or url (http://192.168.188.117:9998/video) here: ")
    saved_data = []
    # -------------------------------
    # Produktdetails von API abrufen
    # -------------------------------
    def get_product_details(barcode):
        product_details = {}
        try:
            url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data and 'product' in data:
                product = data['product']
                product_details['name'] = product.get('product_name')
                product_details['weight'] = product.get('quantity')
                product_details['expirationdate'] = product.get('expiration_date')

                # Bild herunterladen
                url_image = product.get('image_front_url')
                if url_image:
                    image_filename = os.path.join(image_folder, f"{barcode}_image.jpg")
                    urllib.request.urlretrieve(url_image, image_filename)
                    with open(image_filename, 'rb') as img_file:
                        product_details['image'] = img_file.read()
                else:
                    product_details['image'] = None
            else:
                print(f"No product details found for barcode {barcode}.")
        except Exception as e:
            print(f"Error retrieving product details: {e}")

        return product_details

    # -------------------------------
    # Product into Database Save
    # -------------------------------
    def store_in_db(product_details):
        conn = get_db_connection()
        cursor = conn.cursor()

        barcode = product_details.get('barcode')
        box = product_details.get('box')

        # 1) Produkt einfügen oder holen
        cursor.execute("""
            INSERT OR IGNORE INTO products (barcode, product_name)
            VALUES (?, ?)
        """, (
            barcode,
            product_details.get('name')
        ))
        cursor.execute("SELECT product_id FROM products WHERE barcode = ?", (barcode,))
        product_id = cursor.fetchone()[0]

        # 2) Box einfügen oder holen
        cursor.execute("""
            INSERT OR IGNORE INTO boxes (box_name)
            VALUES (?)
        """, (box,))
        cursor.execute("SELECT box_id FROM boxes WHERE box_name = ?", (box,))
        box_id = cursor.fetchone()[0]

        # 3) Item prüfen und aktualisieren oder einfügen
        cursor.execute("""
            SELECT count FROM items
            WHERE product_id = ? AND box_id = ?
        """, (product_id, box_id))
        row = cursor.fetchone()

        if row:
            new_count = row[0] + 1
            cursor.execute("""
                UPDATE items
                SET count = ?, quantity = ?, expiration_date = ?, image = ?
                WHERE product_id = ? AND box_id = ?
            """, (
                new_count,
                product_details.get('weight'),
                product_details.get('expirationdate'),
                product_details.get('image'),
                product_id,
                box_id
            ))
        else:
            cursor.execute("""
                INSERT INTO items (box_id, product_id, quantity, expiration_date, image, count)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                box_id,
                product_id,
                product_details.get('weight'),
                product_details.get('expirationdate'),
                product_details.get('image'),
                1
            ))

        conn.commit()
        conn.close()

    # -------------------------------
    # Barcode adjustments
    # -------------------------------
    def process_barcode(barcode):
        barcode = barcode.strip()

        for item in saved_data:
            if item['barcode'] == barcode and item['box'] == box_name:
                item['quantity'] += 1
                print(f"Barcode {barcode} already processed in box '{box_name}'. Quantity: {item['quantity']}")
                store_in_db(item)
                return

        product_details = get_product_details(barcode)
        if product_details:
            product_details['box'] = box_name
            product_details['barcode'] = barcode
            product_details['quantity'] = 1
            saved_data.append(product_details)
            print(f"Processed new barcode: {barcode} for box '{box_name}'")
            store_in_db(product_details)
        else:
            product_details = {
                'box': box_name,
                'barcode': barcode,
                'name': None,
                'weight': None,
                'expirationdate': None,
                'image': None,
                'quantity': 1
            }
            saved_data.append(product_details)
            print(f"No product details found for barcode {barcode}. Saving placeholder entry.")
            store_in_db(product_details)
    # -------------------------------
    # Get product name for overlay
    # -------------------------------
    def get_product_name(barcode):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT product_name FROM products WHERE barcode = ?", (barcode,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else "Unknown Product"
    # -------------------------------
    # DB-Check-Funktion
    # -------------------------------
    def db_checks():
        conn = get_db_connection()
        cursor = conn.cursor()

        queries = {
            "Alle Boxes": "SELECT * FROM boxes;",
            "Alle Produkte": "SELECT * FROM products;",
            "Alle Items": "SELECT * FROM items;",
            "Items mit Box und Produkt": """
                SELECT 
                    i.item_id,
                    b.box_name,
                    p.barcode,
                    p.product_name,
                    i.quantity,
                    i.expiration_date,
                    i.count
                FROM items i
                JOIN boxes b ON i.box_id = b.box_id
                JOIN products p ON i.product_id = p.product_id;
            """,
            "Suche nach Produktname 'Apples'": """
                SELECT 
                    b.box_name,
                    p.product_name,
                    p.barcode,
                    i.quantity,
                    i.count
                FROM products p
                JOIN items i ON p.product_id = i.product_id
                JOIN boxes b ON i.box_id = b.box_id
                WHERE p.product_name = 'Apples';
            """,
            "Ablaufende Produkte in 6 Monaten": """
                SELECT 
                    p.product_name,
                    i.expiration_date,
                    i.count
                FROM items i
                JOIN products p ON p.product_id = i.product_id
                JOIN boxes b ON b.box_id = i.box_id
                WHERE DATE(i.expiration_date) <= DATE('now', '+6 months')
                ORDER BY i.expiration_date;
            """,
            "Konsistenz-Check": """
                SELECT 
                    i.item_id,
                    i.box_id,
                    b.box_id AS box_exists,
                    i.product_id,
                    p.product_id AS product_exists
                FROM items i
                LEFT JOIN boxes b ON i.box_id = b.box_id
                LEFT JOIN products p ON i.product_id = p.product_id
                WHERE b.box_id IS NULL OR p.product_id IS NULL;
            """,
            "Anzahl pro Produkt": """
                SELECT 
                    p.product_name,
                    SUM(i.count) AS total_count
                FROM products p
                JOIN items i ON p.product_id = i.product_id
                GROUP BY p.product_name
                ORDER BY total_count DESC;
            """
        }

        for desc, q in queries.items():
            print(f"\n--- {desc} ---")
            cursor.execute(q)
            rows = cursor.fetchall()
            for row in rows:
                print(row)

        conn.close()


    # -------------------------------
    # Main program start
    # -------------------------------
    create_tables()

    print("[INFO] Starting video stream...")
    time.sleep(2.0)

    if str(cam).startswith(("http", "tcp")):
        vs = cv2.VideoCapture(str(cam))
    else:
        try:
            vs = cv2.VideoCapture(int(cam))  # Index als int
        except ValueError:
            print("[ERROR] Invalid camera index.")
            exit(1)

    time.sleep(2.0)

    if not vs.isOpened():
        print("[ERROR] Cannot open camera:", cam)
        exit(1)


    # Getting Produktname from DB 
    def get_product_name(barcode):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT product_name FROM products WHERE barcode = ?", (barcode,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else "Unknown Product"

    # -------------------------------
    # Main Loop mit Overlay
    # -------------------------------
    overlay_message = ""
    overlay_time = 0
    DISPLAY_DURATION = 2  # Sekunden
    # Button Position (x1, y1, x2, y2)
    button_pos = (50, 400, 200, 450)

    # --- Maus-Callback ---
    def click_event(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            x1, y1, x2, y2 = button_pos
            if x1 <= x <= x2 and y1 <= y <= y2 and last_scanned_barcode:
                process_barcode(last_scanned_barcode)
                print(f"Scan Button pressed for Barcode: {last_scanned_barcode}")
                global overlay_message, overlay_time
                product_name = get_product_name(last_scanned_barcode)
                overlay_message = f"Article '{product_name}' saved."
                overlay_time = time.time()

    cv2.namedWindow("Barcode Scanner")
    cv2.setMouseCallback("Barcode Scanner", click_event)

    try:
        while True:
            ret, frame = vs.read()
            if not ret:
                print("[ERROR] Failed to grab frame from video stream.")
                break

            current_time = time.time()
            barcodes = pyzbar.decode(frame)

            for barcode in barcodes:
                barcodeData = barcode.data.decode("utf-8")
                last_scanned_barcode = barcodeData  # for Button
                barcodeType = barcode.type
                (x, y, w, h) = barcode.rect
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

                # Barcode und Typ show
                text = "{} ({})".format(barcodeData, barcodeType)
                cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

                # --- Auto-Save ---
                if (barcodeData not in last_saved or
                    current_time - last_saved[barcodeData] > SAVE_INTERVAL):
                    
                    process_barcode(barcodeData)
                    last_saved[barcodeData] = current_time
                    product_name = get_product_name(barcodeData)
                    overlay_message = f"Article '{product_name}' saved."
                    overlay_time = current_time
                    print(f"[AUTO] Saved barcode: {barcodeData} ({product_name})")

            # Overlay show
            if overlay_message and (current_time - overlay_time < DISPLAY_DURATION):
                cv2.putText(frame, overlay_message, (50, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
            else:
                overlay_message = ""

            # Button draw
            x1, y1, x2, y2 = button_pos
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), -1)
            cv2.putText(frame, "Scan", (x1 + 20, y1 + 35), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            cv2.imshow("Barcode Scanner", frame)
            key = cv2.waitKey(1) & 0xFF

            # Scan over 's' key
            if key == ord("s") and last_scanned_barcode:
                process_barcode(last_scanned_barcode)
                product_name = get_product_name(last_scanned_barcode)
                overlay_message = f"Article '{product_name}' saved."
                overlay_time = current_time
        
            elif key == ord("q"):
                print("[INFO] Quitting...")
                break

    finally:
        vs.release()
        cv2.destroyAllWindows()
        


# -------------------------------
# Programm Start
# -------------------------------
if __name__ == "__main__":
    if len(sys.argv) >= 3:
        box_name = sys.argv[1]
        cam_input = sys.argv[2]
    else:
        # Fallback to Input, if no Parameter like : python3 app.py <box1 1>
        box_name = input("Enter the box name: ")
        cam_input = input("Enter cam index or URL: ")

    cam(box_name=box_name, cam=cam_input)
    print("Done")


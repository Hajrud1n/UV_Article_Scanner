# UV_Article_Scanner
Easy way to start the App
The Project will be updated after time


# UV_Article_Scanner
Einfacher Start der App  
Das Projekt wird im Laufe der Zeit aktualisiert

# 📦 UV_Article_Scanner – CRUD System mit Barcode-Scanner

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)  
[![SQLite](https://img.shields.io/badge/Database-SQLite-lightgrey.svg)](https://www.sqlite.org/)  
[![Eel](https://img.shields.io/badge/Framework-Eel-green.svg)](https://github.com/ChrisKnott/Eel)  


---

## 📖 Einleitung 

**UV_Article_Scanner** ist eine benutzerfreundliche **CRUD-Anwendung** (Create, Read, Update, Delete) zur Verwaltung von Artikeln mit Barcode-Scannern.  
Die Software basiert auf **Python**, **SQLite** und **Eel** und unterstützt verschiedene Scanner- und Kamera-Typen:

- ✅ **USB-Barcode-Scanner** (Plug & Play)  
- ✅ **Laptop-Kameras & USB-Kameras**  
- ✅ **IP-Kameras & Smartphones** (z. B. mit der *IP Webcam App*)  

Alle Daten werden in einer **SQLite-Datenbank nach der 3. Normalform** gespeichert.  
Zusätzlich könnten Artikel-Daten bequem als **PDF** oder **Excel-Datei** exportiert werden.  

---

## 🚀 Features 

- 📦 Verwaltung von **Boxen, Produkten, Items**  
- 🔎 Unterstützung von **Barcode-Scannern & Kameras**  
- 🗃 **3. Normalform SQLite-Datenbank**  
- 📝 **CRUD-Funktionen** (Create, Read, Update, Delete)  
- 📑 Export als **PDF**  
- 📊 Export als **Excel (.xlsx)**  
- 🌐 Benutzerfreundliches **Web-UI über Eel**

---

## 🗄 Datenbank-Struktur 

Die Datenbank folgt der **3. Normalform** mit den Tabellen:

- **boxes** → Boxenverwaltung  
- **products** → Produktinformationen (Barcode, Name, Marke, Verpackung)  
- **items** → Verknüpfung zwischen Box & Produkt (Menge, Haltbarkeit, Zähler, Bild)

### Beziehungen

- **boxes → items**: Eine Box kann viele Items enthalten (**1:N**)  
- **products → items**: Ein Produkt kann in vielen Items vorkommen (**1:N**)  
- **items** dient als Verknüpfungstabelle zwischen **boxes** und **products** und speichert zusätzliche Attribute wie Menge, Haltbarkeitsdatum, Zähler und Bild.  

Diese Struktur reduziert Redundanzen und stellt die **Datenkonsistenz gemäß der 3. Normalform** sicher.

---

## 🛠 Installation 

### Voraussetzungen
- Python **3.10+**
- Abhängigkeiten installieren:
  
- pip
```bash
pip install eel fpdf2 pandas openpyxl opencv-python pyzbar requests
```
- uv
```bash
uv add eel fpdf2 pandas openpyxl opencv-python pyzbar requests
```


---
---

# UV_Article_Scanner
Easy way to start the app  
The project will be updated over time

# 📦 UV_Article_Scanner – CRUD System with Barcode Scanner

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)  
[![SQLite](https://img.shields.io/badge/Database-SQLite-lightgrey.svg)](https://www.sqlite.org/)  
[![Eel](https://img.shields.io/badge/Framework-Eel-green.svg)](https://github.com/ChrisKnott/Eel) 

---

## 📖 Introduction 

**UV_Article_Scanner** is a user-friendly **CRUD application** (Create, Read, Update, Delete) for managing items with barcode scanners.  
The software is built with **Python**, **SQLite**, and **Eel**, and supports various scanner and camera types:

- ✅ **USB barcode scanners** (Plug & Play)  
- ✅ **Laptop cameras & USB cameras**  
- ✅ **IP cameras & smartphones** (e.g., using the *IP Webcam App*)  

All data is stored in a **3rd Normal Form SQLite database**.  
Additionally, users can export item data easily as **PDF** or **Excel files**.  

---

## 🚀 Features

- 📦 Manage **boxes, products, items**  
- 🔎 Support for **barcode scanners & cameras**  
- 🗃 **3rd Normal Form SQLite database**  
- 📝 **CRUD functions** (Create, Read, Update, Delete)  
- 📑 Posiblilty to export as **PDF**  will be impleneted shortly 
- 📊 Posiblilty to export as **Excel (.xlsx)** will be impleneted shortly 
- 🌐 User-friendly **Web-UI via Eel**

---

## 🗄 Database Structure 

The database follows the **3rd Normal Form** with the following tables:

- **boxes** → Box management  
- **products** → Product information (barcode, name, brand, packaging)  
- **items** → Linking boxes & products (quantity, expiration date, count, image)  

---
### Relationships

- **boxes → items**: One box can contain many items (**1:N**)  
- **products → items**: One product can appear in many items (**1:N**)  
- **items** acts as a junction table linking **boxes** and **products**, storing additional attributes like quantity, expiration date, count, and image.  

This structure eliminates redundancy and ensures data consistency according to **3rd Normal Form** rules.





## 🛠 Installation

### Requirements
- Python **3.10+**
- Install dependencies:
  
- pip
```bash
pip install eel fpdf2 pandas openpyxl opencv-python pyzbar requests
```
- uv
```bash
uv add eel fpdf2 pandas openpyxl opencv-python pyzbar requests
```




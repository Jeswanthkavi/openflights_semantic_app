"""
OpenFlights Semantic Embedding Project
--------------------------------------
This script connects to a MariaDB database, loads data from the OpenFlights dataset,
and generates semantic embeddings using the SentenceTransformer model.
Embeddings are stored in JSON or vector format inside MariaDB.

Author: Om Prakash Sekar
Database: openflights_semantic
Language: Python 3.x
Dependencies: mariadb, mysql-connector-python, pandas, sentence-transformers
"""

import mariadb
import mysql.connector
import pandas as pd
import json
import time
import sys
from sentence_transformers import SentenceTransformer

# -----------------------------
# 1️⃣ DATABASE CONFIGURATION
# -----------------------------
DB_CONFIG = {
    "user": "root",          # Change if needed
    "password": "root1",     # Your MariaDB password
    "host": "localhost",
    "port": 3308,            # Adjust if MariaDB uses a different port
    "database": "openflights_semantic"
}

# -----------------------------
# 2️⃣ CONNECT TO DATABASE
# -----------------------------
def connect_db():
    try:
        print("🔄 Connecting to MariaDB...")
        conn = mariadb.connect(**DB_CONFIG)
        print("✅ Successfully connected to MariaDB!")
        return conn
    except mariadb.Error as e:
        print(f"❌ Database connection failed: {e}")
        sys.exit(1)

# -----------------------------
# 3️⃣ LOAD SAMPLE CSV (OPTIONAL)
# -----------------------------
def preview_csv():
    try:
        df = pd.read_csv(r"C:\Users\Om Prakash Sekar\Desktop\OpenFlights_semantic\data\airports.csv")
        print(df.head())
        print(f"📊 Total rows: {len(df)}")
    except Exception as e:
        print(f"⚠️ CSV Preview Error: {e}")

# -----------------------------
# 4️⃣ INITIALIZE MODEL
# -----------------------------
def load_model():
    print("🧠 Loading sentence transformer model...")
    return SentenceTransformer('all-MiniLM-L6-v2')

# -----------------------------
# 5️⃣ GENERIC EMBEDDING FUNCTION
# -----------------------------
def generate_embeddings(cursor, query, update_query, text_formatter):
    cursor.execute(query)
    records = cursor.fetchall()
    print(f"📦 {len(records)} records found.")

    for record in records:
        text = text_formatter(record)
        embedding = model.encode(text).tolist()
        embedding_json = json.dumps(embedding)
        cursor.execute(update_query, (embedding_json, record[0]))
        time.sleep(0.01)

# -----------------------------
# 6️⃣ MAIN EXECUTION LOGIC
# -----------------------------
if __name__ == "__main__":
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    model = load_model()

    # 6.1 --- AIRPORTS ---
    print("\n✈️ Embedding airports...")
    generate_embeddings(
        cursor,
        "SELECT id, name, city, country FROM airports WHERE embedding IS NULL",
        "UPDATE airports SET embedding = %s WHERE id = %s",
        lambda r: f"{r[1]}, {r[2]}, {r[3]}"
    )
    conn.commit()

    # 6.2 --- ROUTES ---
    print("\n🗺️ Embedding routes...")
    generate_embeddings(
        cursor,
        "SELECT id, source_airport, dest_airport, airline FROM routes WHERE embedding IS NULL",
        "UPDATE routes SET embedding = %s WHERE id = %s",
        lambda r: f"{r[3]} from {r[1]} to {r[2]}"
    )
    conn.commit()

    # 6.3 --- AIRLINES ---
    print("\n🛫 Embedding airlines...")
    generate_embeddings(
        cursor,
        "SELECT id, name, country, callsign FROM airlines WHERE embedding_vec IS NULL",
        "UPDATE airlines SET embedding_vec = VEC_FROMTEXT(%s) WHERE id = %s",
        lambda r: f"{r[1]}, {r[2]}, {r[3]}"
    )
    conn.commit()

    # 6.4 --- PASSENGERS ---
    print("\n🧍 Embedding passengers...")
    generate_embeddings(
        cursor,
        "SELECT id, name, email, phone, nationality FROM passengers WHERE embedding_vec IS NULL",
        "UPDATE passengers SET embedding_vec = VEC_FROMTEXT(%s) WHERE id = %s",
        lambda r: f"Passenger {r[1]}, email {r[2]}, phone {r[3]}, nationality {r[4]}"
    )
    conn.commit()

    # 6.5 --- BOOKINGS ---
    print("\n📘 Embedding bookings...")
    generate_embeddings(
        cursor,
        """
        SELECT b.id, p.name, b.seat_number, b.status, f.flight_number
        FROM bookings b
        JOIN passengers p ON b.passenger_id = p.id
        JOIN flights f ON b.flight_id = f.id
        WHERE b.embedding_vec IS NULL
        """,
        "UPDATE bookings SET embedding_vec = VEC_FROMTEXT(%s) WHERE id = %s",
        lambda r: f"Booking for {r[1]} on flight {r[4]}, seat {r[2]}, status {r[3]}"
    )
    conn.commit()

    # 6.6 --- TICKETS ---
    print("\n🎟️ Embedding tickets...")
    generate_embeddings(
        cursor,
        """
        SELECT t.id, t.ticket_number, t.class, t.price, b.status, p.name
        FROM tickets t
        JOIN bookings b ON t.booking_id = b.id
        JOIN passengers p ON b.passenger_id = p.id
        WHERE t.embedding_vec IS NULL
        """,
        "UPDATE tickets SET embedding_vec = VEC_FROMTEXT(%s) WHERE id = %s",
        lambda r: f"Ticket {r[1]}, passenger {r[5]}, class {r[2]}, booking status {r[4]}, price {r[3]}"
    )
    conn.commit()

    cursor.close()
    conn.close()
    print("\n✅ All embeddings generated successfully!")

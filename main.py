import mariadb
import sys

# --- Database Connection Configuration ---
DB_CONFIG = {
    "user": "root",         # change if needed
    "password": "root1",     # change to your password
    "host": "localhost",    # or 127.0.0.1
    "port": 3308,           # check in HeidiSQL if different
    "database": "openflights_semantic"  # we’ll create this next
}

try:
    print("🔄 Connecting to MariaDB...")
    conn = mariadb.connect(**DB_CONFIG)
    print("✅ Successfully connected to MariaDB!")
    
    # --- Create a cursor object ---
    cur = conn.cursor()
    
    # --- Example query ---
    cur.execute("SELECT VERSION()")
    version = cur.fetchone()
    print(f"🧠 MariaDB version: {version[0]}")

    # --- Close connection ---
    conn.close()
    print("🔒 Connection closed successfully.")

except mariadb.Error as e:
    print(f"❌ Error connecting to MariaDB: {e}")
    sys.exit(1)
import pandas as pd

df = pd.read_csv(r"C:\Users\Om Prakash Sekar\Desktop\OpenFlights_semantic\data\airports.csv")
print(df.head())
print(f"Total rows: {len(df)}")


from sentence_transformers import SentenceTransformer
import mysql.connector
import json
import time

# --- Model ---
print("🧠 Loading model...")
model = SentenceTransformer('all-MiniLM-L6-v2')

# Connect to MariaDB
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='root1',
    database='openflights_semantic',
    port=3308
)
cursor = conn.cursor()


# --- Embed All Airports ---
cursor.execute("""
    SELECT id, name, city, country 
    FROM airports 
    WHERE embedding IS NULL
""")
airports = cursor.fetchall()

print(f"Embedding {len(airports)} airports...")
for airport in airports:
    airport_id, name, city, country = airport
    text = f"{name}, {city}, {country}"
    embedding = model.encode(text).tolist()
    cursor.execute("""
        UPDATE airports 
        SET embedding = %s 
        WHERE id = %s
    """, (json.dumps(embedding), airport_id))
    time.sleep(0.01)  # Optional: slow down to avoid overload

# --- Embed All Routes ---
cursor.execute("""
    SELECT id, source_airport, dest_airport, airline 
    FROM routes 
    WHERE embedding IS NULL
""")
routes = cursor.fetchall()

print(f"Embedding {len(routes)} routes...")
for route in routes:
    route_id, source, dest, airline = route
    text = f"{airline} from {source} to {dest}"
    embedding = model.encode(text).tolist()
    cursor.execute("""
        UPDATE routes 
        SET embedding = %s 
        WHERE id = %s
    """, (json.dumps(embedding), route_id))
    time.sleep(0.01)

# Finalize
conn.commit()
cursor.close()
conn.close()
print("✅ All embeddings updated.")

# --- Embed All Airlines ---
cursor.execute("""
    SELECT id, name, country, callsign
    FROM airlines
    WHERE embedding_vec IS NULL
""")
airlines = cursor.fetchall()

print(f"Embedding {len(airlines)} airlines...")
for airline in airlines:
    airline_id, name, country, callsign = airline
    text = f"{name}, {country}, {callsign}"
    embedding = model.encode(text).tolist()
    embedding_str = json.dumps(embedding)

    cursor.execute("""
        UPDATE airlines
        SET embedding_vec = VEC_FROMTEXT(%s)
        WHERE id = %s
    """, (embedding_str, airline_id))
    time.sleep(0.01)  # Optional: throttle updates

# Finalize
conn.commit()
cursor.close()
conn.close()
print("✅ Airline embeddings updated successfully.")


# --- Fetch passengers ---
cur.execute("SELECT id, name, email, phone, nationality FROM passengers;")
rows = cur.fetchall()
print(f"📦 {len(rows)} passengers found.")

# --- Generate embeddings ---
for r in rows:
    pid, name, email, phone, nat = r
    text = f"Passenger {name}, email {email}, phone {phone}, nationality {nat}"
    emb = model.encode(text)
    emb_txt = json.dumps(emb.tolist())  # ✅ JSON array format

    cur.execute("UPDATE passengers SET embedding_vec = VEC_FROMTEXT(?) WHERE id = ?", (emb_txt, pid))

conn.commit()
cur.close()
conn.close()
print("✅ Passenger embeddings saved.")

# ---------------------------
# 2️⃣ BOOKINGS
# ---------------------------
print("\n📘 Generating embeddings for bookings...")
cur.execute("""
SELECT b.id, p.name, b.seat_number, b.status, f.flight_number
FROM bookings b
JOIN passengers p ON b.passenger_id = p.id
JOIN flights f ON b.flight_id = f.id;
""")
rows = cur.fetchall()
print(f"📦 {len(rows)} bookings found.")

for row in rows:
    bid, pname, seat, status, flight = row
    text = f"Booking for {pname} on flight {flight}, seat {seat}, status {status}"
    embedding = model.encode(text)
    emb_txt = json.dumps(embedding.tolist())  # ✅ Proper JSON array

    cur.execute("UPDATE bookings SET embedding_vec = VEC_FROMTEXT(?) WHERE id = ?", (emb_txt, bid))

conn.commit()
print("✅ Bookings embeddings saved.")

# ---------------------------
# 3️⃣ TICKETS
# ---------------------------
print("\n🎟️ Generating embeddings for tickets...")
cur.execute("""
SELECT t.id, t.ticket_number, t.class, t.price, b.status, p.name
FROM tickets t
JOIN bookings b ON t.booking_id = b.id
JOIN passengers p ON b.passenger_id = p.id;
""")
rows = cur.fetchall()
print(f"📦 {len(rows)} tickets found.")

for row in rows:
    tid, tnum, tclass, price, bstatus, pname = row
    text = f"Ticket {tnum}, passenger {pname}, class {tclass}, booking status {bstatus}, price {price}"
    embedding = model.encode(text)
    emb_txt = json.dumps(embedding.tolist())  # ✅ Proper JSON array

    cur.execute("UPDATE tickets SET embedding_vec = VEC_FROMTEXT(?) WHERE id = ?", (emb_txt, tid))

conn.commit()
cur.close()
conn.close()
print("\n✅ All embeddings generated successfully!")

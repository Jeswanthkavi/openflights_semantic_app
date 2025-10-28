import mariadb
from sentence_transformers import SentenceTransformer
import json
import random
from datetime import datetime, timedelta

# --- Connect to MariaDB ---
conn = mariadb.connect(
    user="root",
    password="root1",
    host="localhost",
    database="openflights_semantic",
    port=3308
)
cur = conn.cursor()

# --- Load embedding model ---
print("🔄 Loading embedding model (all-MiniLM-L6-v2)...")
model = SentenceTransformer("all-MiniLM-L6-v2")

# --- Fetch routes and airline names ---
print("📦 Fetching routes and airlines...")
cur.execute("SELECT id, name FROM airlines")
airlines = {row[0]: row[1] for row in cur.fetchall()}

cur.execute("SELECT airline_id, source_airport, dest_airport FROM routes LIMIT 100")
routes = cur.fetchall()

# --- Generate and insert flights ---
print("✈️ Generating synthetic flights...")
for route in routes:
    airline_id, source, dest = route
    airline_name = airlines.get(airline_id, "Unknown Airline")
    flight_number = f"{airline_name[:2].upper()}{random.randint(100,999)}"
    dep_time = datetime.now() + timedelta(days=random.randint(1, 30), hours=random.randint(0, 23))
    arr_time = dep_time + timedelta(hours=random.randint(1, 5))
    price = round(random.uniform(100, 800), 2)
    status = random.choice(["Scheduled", "Delayed", "Cancelled"])

    # Insert flight
    insert_sql = """
        INSERT INTO flights (flight_number, airline_id, source_airport, dest_airport, departure_time, arrival_time, price, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    cur.execute(insert_sql, (
        flight_number, airline_id, source, dest,
        dep_time.strftime('%Y-%m-%d %H:%M:%S'),
        arr_time.strftime('%Y-%m-%d %H:%M:%S'),
        price, status
    ))

conn.commit()
print("✅ Flights loaded!")

# --- Fetch newly inserted flights for embedding ---
# --- Fetch newly inserted flights for embedding ---
print("🧠 Generating embeddings...")
cur.execute("""
    SELECT f.id, f.flight_number, f.price, f.status,
           a.name AS airline_name,
           f.source_airport, f.dest_airport
    FROM flights f
    JOIN airlines a ON f.airline_id = a.id
    WHERE f.embedding_vec IS NULL
""")
rows = cur.fetchall()

print(f"🔢 Found {len(rows)} flights to embed...")

for row in rows:
    flight_id, flight_number, price, status, airline, source, dest = row
    text = f"Flight {flight_number} by {airline} from {source} to {dest}, status {status}, price {price} rupees"

    try:
        embedding = model.encode(text)
        embedding_str = json.dumps(embedding.tolist())  # Convert to JSON array string

        # ✅ Safe insert using VEC_FROMTEXT
        update_sql = "UPDATE flights SET embedding_vec = VEC_FROMTEXT(?) WHERE id = ?"
        cur.execute(update_sql, (embedding_str, flight_id))

    except Exception as e:
        print(f"❌ Error embedding flight ID {flight_id}: {e}")

conn.commit()
print("✅ Embeddings saved for all new flights!")

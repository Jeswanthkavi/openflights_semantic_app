# ✈️ OpenFlights Semantic Search  
### An AI-powered semantic search engine for flights, passengers, bookings, and routes  
Built with **MariaDB VECTOR**, **Python**, and **SentenceTransformers**

---

## 🧠 Project Overview

**OpenFlights Semantic Search** is an intelligent system that allows users to search for flight-related information using **natural language queries** — such as:

> “Show me all flights from India to London”  
> “Find passengers who booked Air India”  
> “List routes with Emirates Airlines”  

Instead of relying on keyword matching, this project uses **semantic embeddings** to understand the *meaning* of the query and return the most relevant results.

---

## 💡 Features

✅ Semantic search across multiple flight-related entities (airlines, airports, routes, passengers, bookings, tickets)  
✅ Uses **MariaDB’s new VECTOR data type** for embedding storage and similarity search  
✅ Built using **SentenceTransformer (all-MiniLM-L6-v2)** for text embeddings  
✅ Flask web interface for easy querying and visualization  
✅ Modular structure for scalability and dataset expansion  
✅ Fast and efficient data loading from CSV files directly into MariaDB  

---

## 🏗️ Project Architecture
openflights_semantic_app(repo)/
│
├── openflights/ → Data loading & embeddings
│ ├── data/ → CSV datasets (airlines, airports, etc.)
│ ├── main/ → Embedding folder
│ └── flights.py → Do first before going to main.py
│ └── main.py → Embedding generator
├── openflights_semantic_app/ → Flask web app
│ ├── templates/ → HTML templates
│ └── run.py → Flask server entry point
│
├── requirements.txt
├── README.md
├── INSTRUCTIONS.txt




---

## ⚙️ Tech Stack

| Component | Technology Used |
|------------|-----------------|
| **Database** | MariaDB 11.7+ (VECTOR support) |
| **Backend** | Python 3.9+, Flask |
| **ML Model** | SentenceTransformer (`all-MiniLM-L6-v2`) |
| **Libraries** | mariadb, sentence-transformers, numpy |
| **Frontend** | HTML, CSS (Flask templates) |

---

## 🚀 Setup Guide

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/yourusername/Openflights_semantic_app.git
cd Openflights_semantic_app
_______________________________________________________________
2️⃣ Create Virtual Environment
python -m venv venv
venv\Scripts\activate  # Windows
# OR
source venv/bin/activate  # macOS/Linux
_______________________________________________________________
3️⃣ Install Dependencies
pip install -r requirements.txt
_______________________________________________________________
4️⃣ Setup MariaDB Database
CREATE DATABASE openflights_semantic;
CREATE USER 'openflights'@'localhost' IDENTIFIED BY 'openflights_pwd';
GRANT ALL PRIVILEGES ON openflights_semantic.* TO 'openflights'@'localhost';
FLUSH PRIVILEGES;
__________________________________________________________________
5️⃣ Create Tables

Run the commands from schema.sql or manually:

USE openflights_semantic;

CREATE TABLE IF NOT EXISTS flights (
 id INT AUTO_INCREMENT PRIMARY KEY,
 flight_number VARCHAR(50),
 airline_id INT,
 source_airport VARCHAR(50),
 dest_airport VARCHAR(50),
 departure_time DATETIME,
 price DECIMAL(10,2),
 status VARCHAR(50),
 embedding_vec VECTOR(384)
);

CREATE TABLE IF NOT EXISTS passengers (
 id INT AUTO_INCREMENT PRIMARY KEY,
 name VARCHAR(100),
 email VARCHAR(100),
 phone VARCHAR(30),
 nationality VARCHAR(50),
 embedding_vec VECTOR(384)
);

CREATE TABLE IF NOT EXISTS bookings (
 id INT AUTO_INCREMENT PRIMARY KEY,
 passenger_id INT,
 flight_id INT,
 seat_number VARCHAR(10),
 booking_date DATETIME,
 status VARCHAR(30),
 embedding_vec VECTOR(384),
 FOREIGN KEY (passenger_id) REFERENCES passengers(id),
 FOREIGN KEY (flight_id) REFERENCES flights(id)
);

CREATE TABLE IF NOT EXISTS tickets (
 id INT AUTO_INCREMENT PRIMARY KEY,
 booking_id INT,
 ticket_number VARCHAR(50),
 issue_date DATETIME,
 price DECIMAL(10,2),
 class VARCHAR(30),
 embedding_vec VECTOR(384),
 FOREIGN KEY (booking_id) REFERENCES bookings(id)
);
_______________________________________________________________
6️⃣ Load CSV Data Using MariaDB Command Prompt

Enable file loading:

SET GLOBAL local_infile = 1;


Then load data for each table:

LOAD DATA LOCAL INFILE 'C:/Users/Om Prakash Sekar/Desktop/OpenFlights_semantic/data/airlines.csv'
INTO TABLE airlines
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(id, name, alias, iata, icao, callsign, country, active);
______________________________________________________
LOAD DATA LOCAL INFILE 'C:/Users/Om Prakash Sekar/Desktop/OpenFlights_semantic/data/airports.csv'
INTO TABLE airports
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(id, name, city, country, iata, icao, latitude, longitude, altitude, timezone, dst, tz_database_time_zone);
__________________________________________________________

LOAD DATA LOCAL INFILE 'C:/Users/Om Prakash Sekar/Desktop/OpenFlights_semantic/data/routes.csv'
INTO TABLE routes
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(id, airline_id, source_airport_id, dest_airport_id, codeshare, stops, equipment);

_______________________________________________________________
Add sample flight data:

INSERT INTO flights (flight_number, airline_id, source_airport, dest_airport, departure_time, price, status)
VALUES ('AI217', 1, 'DEL', 'LHR', '2025-11-25 10:00:00', 45000.00, 'Scheduled');

_______________________________________________________________
And sample passengers/bookings:

INSERT INTO passengers (name, email, phone, nationality)
VALUES ('Priya Sharma', 'priya@example.com', '+91-9876543210', 'India'),
       ('John Smith', 'john.smith@example.com', '+1-2025550147', 'USA');
_______________________________________________________________
INSERT INTO bookings (passenger_id, flight_id, seat_number, booking_date, status)
VALUES (1, 1, '12A', '2025-10-10 10:00:00', 'Confirmed');

INSERT INTO tickets (booking_id, ticket_number, issue_date, price, class)
VALUES (1, 'AI-2025-001', '2025-10-09 09:00:00', 405.93, 'Economy');
_______________________________________________________________

❕The data loading and embedding for flights in a single file (flights.py) in openflights/main/flights.py
  
7️⃣ Generate Embeddings
cd openflights
python main.py


This script:

Connects to MariaDB

Reads each record

Generates semantic embeddings using SentenceTransformer(all-MiniLM-L6-v2)

Stores vectors into MariaDB VECTOR columns
_______________________________________________________________
8️⃣ Run the Web Application
cd ../openflights_semantic_app
python run.py
_______________________________________________________________

Access it in browser:

🌐 http://127.0.0.1:5000/
________________________________________________________________
🔍 Try Example Queries
🧭 “Flights from India to London”
👩‍✈️ “Passengers who booked Air India”
🛫 “Routes operated by Emirates Airlines”
🎟️ “Tickets for seat 12A”


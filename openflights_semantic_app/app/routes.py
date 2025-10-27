from flask import Blueprint, render_template, request, jsonify
from app.db import get_db_connection
from app.embeddings import get_text_embedding
import json

bp = Blueprint("main", __name__)

# -----------------------------
# Home Page
# -----------------------------
@bp.route("/")
def index():
    return render_template("index.html", mode="airports")

# -----------------------------
# Airport Semantic Search
# -----------------------------
@bp.route("/search/airport", methods=["POST"])
def search_airport():
    data = request.get_json() if request.is_json else request.form
    text_query = data.get("query", "")
    limit = int(data.get("limit", 5))

    # Create embedding from user query
    query_embedding = get_text_embedding(text_query)
    vector_str = json.dumps(query_embedding).replace(" ", "")

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    sql = """
        SELECT id, name, city, country,
               VEC_DISTANCE_COSINE(embedding_vec, VEC_FromText(%s)) AS similarity
        FROM airports
        WHERE embedding_vec IS NOT NULL
        ORDER BY similarity ASC
        LIMIT %s;
    """
    cur.execute(sql, (vector_str, limit))
    results = cur.fetchall()
    cur.close()
    conn.close()

    return jsonify(results)

# -----------------------------
# Route Semantic Search
# -----------------------------
@bp.route("/search/route", methods=["POST"])
def search_route():
    data = request.get_json() if request.is_json else request.form
    text_query = data.get("query", "")
    limit = int(data.get("limit", 5))

    # Create embedding for the query
    query_embedding = get_text_embedding(text_query)
    vector_str = json.dumps(query_embedding).replace(" ", "")

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    sql = """
        SELECT id, airline, source_airport, dest_airport,
               VEC_DISTANCE_COSINE(embedding_vec, VEC_FromText(%s)) AS similarity
        FROM routes
        WHERE embedding_vec IS NOT NULL
        ORDER BY similarity ASC
        LIMIT %s;
    """
    cur.execute(sql, (vector_str, limit))
    results = cur.fetchall()
    cur.close()
    conn.close()

    return jsonify(results)
@bp.route("/search/airline", methods=["POST"])
def search_airline():
    data = request.json
    text_query = data.get("query", "")
    limit = int(data.get("limit", 5))

    query_embedding = get_text_embedding(text_query)

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    # Convert embedding to JSON text for SQL
    import json
    vector_str = json.dumps(query_embedding)

    sql = f"""
        SELECT id, name, iata, icao, country,
               VEC_DISTANCE_COSINE(embedding_vec, VEC_FROMTEXT('{vector_str}')) AS similarity
        FROM airlines
        ORDER BY similarity ASC
        LIMIT {limit};
    """
    cur.execute(sql)
    results = cur.fetchall()
    cur.close()
    conn.close()

    return jsonify(results)
# @bp.route("/search/flight", methods=["POST"])
# def search_flight():
#     data = request.json
#     text_query = data.get("query", "")
#     limit = int(data.get("limit", 5))

#     query_embedding = get_text_embedding(text_query)

#     conn = get_db_connection()
#     cur = conn.cursor(dictionary=True)

#     import json
#     vector_str = json.dumps(query_embedding)

#     # sql = f"""
#     #     SELECT 
#     #         f.id, f.flight_number, f.price, f.status,
#     #         a.name AS airline_name,
#     #         r.source_airport, r.destination_airport,
#     #         VEC_DISTANCE_COSINE(f.embedding_vec, VEC_FROMTEXT('{vector_str}')) AS similarity
#     #     FROM flights f
#     #     JOIN airlines a ON f.airline_id = a.id
#     #     JOIN routes r ON f.route_id = r.id
#     #     ORDER BY similarity ASC
#     #     LIMIT {limit};
#     # """
#     # cur.execute(sql)
#     sql = """
#     SELECT id, name, iata, icao, country,
#            VEC_DISTANCE_COSINE(embedding_vec, VEC_FROMTEXT(%s)) AS similarity
#     FROM airlines
#     WHERE embedding_vec IS NOT NULL
#     ORDER BY similarity ASC
#     LIMIT %s;
# """
#     cur.execute(sql, (json.dumps(query_embedding), limit))

#     results = cur.fetchall()
#     results = [
#     {
#         "id": row["id"],
#         "flight_number": row["flight_number"],
#         "airline": row["airline_name"],
#         "source": row["source_airport"],
#         "destination": row["destination_airport"],
#         "price": row["price"],
#         "status": row["status"],
#         "similarity": round(row["similarity"], 4)
#     }
#     for row in cur.fetchall()
# ]

#     cur.close()
#     conn.close()

#     return jsonify(results)

@bp.route("/search/flight", methods=["POST"])
def search_flight():
    data = request.get_json()
    text_query = data.get("query", "")
    limit = int(data.get("limit", 5))

    query_embedding = get_text_embedding(text_query)
    vector_str = json.dumps(query_embedding)

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    sql = f"""
        SELECT 
            f.id,
            f.flight_number,
            f.price,
            f.status,
            f.source_airport,
            f.dest_airport,
            a.name AS airline_name,
            VEC_DISTANCE_COSINE(f.embedding_vec, VEC_FROMTEXT('{vector_str}')) AS similarity
        FROM flights f
        LEFT JOIN airlines a ON f.airline_id = a.id
        WHERE f.embedding_vec IS NOT NULL
        ORDER BY similarity ASC
        LIMIT {limit};
    """
    cur.execute(sql)
    results = cur.fetchall()
    cur.close()
    conn.close()

    return jsonify(results)


@bp.route("/search/passenger", methods=["POST"])
def search_passenger():
    data = request.get_json()
    text_query = data.get("query", "")
    limit = int(data.get("limit", 5))

    query_embedding = get_text_embedding(text_query)
    vector_str = json.dumps(query_embedding).replace(" ", "")

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    sql = """
        SELECT id, name, email, phone, nationality,
               VEC_DISTANCE_COSINE(embedding_vec, VEC_FROMTEXT(%s)) AS similarity
        FROM passengers
        WHERE embedding_vec IS NOT NULL
        ORDER BY similarity ASC
        LIMIT %s;
    """
    cur.execute(sql, (vector_str, limit))
    results = cur.fetchall()
    cur.close()
    conn.close()

    return jsonify(results)


@bp.route("/search/booking", methods=["POST"])
def search_booking():
    data = request.get_json()
    text_query = data.get("query", "")
    limit = int(data.get("limit", 5))

    query_embedding = get_text_embedding(text_query)
    vector_str = json.dumps(query_embedding).replace(" ", "")

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    sql = """
        SELECT b.id, b.seat_number, b.status, 
               f.flight_number, p.name AS passenger_name,
               VEC_DISTANCE_COSINE(b.embedding_vec, VEC_FROMTEXT(%s)) AS similarity
        FROM bookings b
        JOIN flights f ON b.flight_id = f.id
        JOIN passengers p ON b.passenger_id = p.id
        WHERE b.embedding_vec IS NOT NULL
        ORDER BY similarity ASC
        LIMIT %s;
    """
    cur.execute(sql, (vector_str, limit))
    results = cur.fetchall()
    cur.close()
    conn.close()

    return jsonify(results)


@bp.route("/search/ticket", methods=["POST"])
def search_ticket():
    data = request.get_json()
    text_query = data.get("query", "")
    limit = int(data.get("limit", 5))

    query_embedding = get_text_embedding(text_query)
    vector_str = json.dumps(query_embedding).replace(" ", "")

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    sql = """
        SELECT 
            t.id, 
            t.ticket_number, 
            t.class, 
            t.price, 
            b.status AS booking_status, 
            p.name AS passenger_name,
            f.flight_number,
            f.source_airport,
            f.dest_airport,
            VEC_DISTANCE_COSINE(t.embedding_vec, VEC_FROMTEXT(%s)) AS similarity
        FROM tickets t
        JOIN bookings b ON t.booking_id = b.id
        JOIN passengers p ON b.passenger_id = p.id
        JOIN flights f ON b.flight_id = f.id
        WHERE t.embedding_vec IS NOT NULL
        ORDER BY similarity ASC
        LIMIT %s;
    """
    cur.execute(sql, (vector_str, limit))
    results = cur.fetchall()
    cur.close()
    conn.close()

    return jsonify(results)


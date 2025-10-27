import mariadb

def get_db_connection():
    return mariadb.connect(
        user="root",
        password="root1",
        host="localhost",
        port=3308,
        database="openflights_semantic"  
    )

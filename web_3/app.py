from flask import Flask, render_template
import mysql.connector  # type: ignore
import os

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME")
}

app = Flask(__name__)

def init_db():
    conn = mysql.connector.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"]
    )
    cur = conn.cursor()
    cur.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
    cur.close()
    conn.close()

    conn = mysql.connector.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS access (
            id INT PRIMARY KEY,
            count INT NOT NULL
        )
    """)
    cur.execute("""
        INSERT INTO access (id, count)
        SELECT 1, 0 FROM DUAL
        WHERE NOT EXISTS (SELECT * FROM access WHERE id = 1)
    """)
    conn.commit()
    cur.close()
    conn.close()

init_db()

@app.route("/")
def index():
    conn = mysql.connector.connect(**DB_CONFIG)
    cur = conn.cursor()

    cur.execute("UPDATE access SET count = count + 1 WHERE id = 1")
    conn.commit()

    cur.execute("SELECT count FROM access WHERE id = 1")
    (count,) = cur.fetchone()

    cur.close()
    conn.close()

    return render_template("index.html", count=count)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8888, debug=True)

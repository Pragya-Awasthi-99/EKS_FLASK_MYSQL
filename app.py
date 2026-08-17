import os
from flask import Flask, render_template, request, jsonify
from flask_mysqldb import MySQL

app = Flask(__name__)

# ---------------------------------------------------------
# MySQL Configuration
# ---------------------------------------------------------

app.config["MYSQL_HOST"] = os.environ.get("MYSQL_HOST", "localhost")
app.config["MYSQL_USER"] = os.environ.get("MYSQL_USER", "root")
app.config["MYSQL_PASSWORD"] = os.environ.get("MYSQL_PASSWORD", "admin")
app.config["MYSQL_DB"] = os.environ.get("MYSQL_DB", "mydb")

mysql = MySQL(app)


# ---------------------------------------------------------
# Database Initialization
# ---------------------------------------------------------

def init_db():
    with app.app_context():
        cur = mysql.connection.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INT AUTO_INCREMENT PRIMARY KEY,
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        mysql.connection.commit()
        cur.close()


# ---------------------------------------------------------
# Dashboard
# ---------------------------------------------------------

@app.route("/")
def dashboard():
    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT id, message, created_at
        FROM messages
        ORDER BY id DESC
    """)

    messages = cur.fetchall()
    cur.close()

    return render_template(
        "index.html",
        messages=messages
    )


# ---------------------------------------------------------
# Add Team Update
# ---------------------------------------------------------

@app.route("/submit", methods=["POST"])
def submit():

    new_message = request.form.get("new_message", "").strip()

    if not new_message:
        return jsonify({
            "success": False,
            "error": "Please enter an update."
        }), 400

    if len(new_message) > 500:
        return jsonify({
            "success": False,
            "error": "Update must be less than 500 characters."
        }), 400

    cur = mysql.connection.cursor()

    cur.execute(
        "INSERT INTO messages (message) VALUES (%s)",
        (new_message,)
    )

    mysql.connection.commit()

    message_id = cur.lastrowid

    cur.close()

    return jsonify({
        "success": True,
        "id": message_id,
        "message": new_message
    })


# ---------------------------------------------------------
# Health Check
# ---------------------------------------------------------

@app.route("/health")
def health():

    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT 1")
        cur.fetchone()
        cur.close()

        return jsonify({
            "status": "healthy",
            "application": "CloudOps Hub",
            "database": "connected"
        })

    except Exception as error:

        return jsonify({
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(error)
        }), 500


# ---------------------------------------------------------
# Application Start
# ---------------------------------------------------------

if __name__ == "__main__":

    init_db()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )

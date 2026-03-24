import mysql.connector
from flask import Flask, render_template, jsonify, request 
import requests
import os

app = Flask(__name__)

# ডাটাবেস কনফিগারেশন
db_config = {
    "host": "pg-3689f3ca-samolsikder45-ea9b.c.aivencloud.com",
    "user": "avnadmin",
    "password": os.environ.get('DB_PASSWORD', 'AVNS_RgWvdbzCpHlr2n_J8VF'),
    "database": "defaultdb",
    "port": 23399,
    "ssl_ca": "ca.pem"
}

def load_jobs_from_db():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM jobs")
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return result

@app.route("/")
def hello_world():
    try:
        jobs = load_jobs_from_db()
        return render_template('home.html', jobs=jobs)
    except Exception as e:
        return f"Database Connection Error: {str(e)}"

@app.route("/job/<id>")
def show_job(id):
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM jobs WHERE id = %s", (id,))
        job = cursor.fetchone()
        cursor.close()
        connection.close()
        if not job:
            return "Job Not Found", 404
        return render_template('jobpage.html', job=job)
    except Exception as e:
        return f"Error: {str(e)}"

@app.route("/job/<id>/apply", methods=['POST'])
def apply_to_job(id):
    data = request.form
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        insert_query = "INSERT INTO applications (job_id, full_name, email) VALUES (%s, %s, %s)"
        cursor.execute(insert_query, (id, data.get('full_name'), data.get('email')))
        connection.commit()
        cursor.close()
        connection.close()
        return "Application Submitted Successfully!"
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    # Render-এর পোর্টের জন্য এটি জরুরি
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
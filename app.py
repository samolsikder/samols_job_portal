import pymysql  # mysql.connector এর বদলে এটি দিন (যেহেতু requirements এ PyMySQL আছে)
from flask import Flask, render_template, jsonify, request 
import requests
import os

app = Flask(__name__)

# ডাটাবেস কনফিগারেশন (PyMySQL ফরম্যাটে সামান্য পরিবর্তন)
db_config = {
    "host": "mysql-f560c3-samolsikder45-ea9b.c.aivencloud.com",
    "user": "avnadmin",
    "password": os.environ.get('DB_PASSWORD', 'AVNS_QrgIodgkrMRV4z05XBc'),
    "database": "defaultdb",
    "port": 23399,
    "ssl": {'ca': 'ca.pem'}, # PyMySQL-এ SSL এভাবে দিতে হয়
    "cursorclass": pymysql.cursors.DictCursor
}

def load_jobs_from_db():
    connection = pymysql.connect(**db_config)
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM jobs")
        result = cursor.fetchall()
    connection.close()
    return result

@app.route("/")
def hello_world():
    try:
        jobs = load_jobs_from_db()
        return render_template('home.html', jobs=jobs)
    except Exception as e:
        return f"Database Error: {str(e)}"

@app.route("/job/<id>")
def show_job(id):
    try:
        connection = pymysql.connect(**db_config)
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM jobs WHERE id = %s", (id,))
            job = cursor.fetchone()
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
        connection = pymysql.connect(**db_config)
        with connection.cursor() as cursor:
            # এখানে 'job_data' তৈরি করা হলো
            cursor.execute("SELECT * FROM jobs WHERE id = %s", (id,))
            job_data = cursor.fetchone() 

            # অ্যাপ্লিকেশন সেভ করার কোড
            insert_query = "INSERT INTO applications (job_id, full_name, email) VALUES (%s, %s, %s)"
            cursor.execute(insert_query, (id, data.get('full_name'), data.get('email')))
            connection.commit()
            
        connection.close()

        # সাকসেস পেজ রেন্ডার করা
        return render_template("application_submitted.html", application=data, job=job_data)

    except Exception as e:
        return f"Error: {str(e)}"
    
@app.route("/job/<id>/apply_form")
def apply_form(id):
    try:
        connection = pymysql.connect(**db_config)
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM jobs WHERE id = %s", (id,))
            job = cursor.fetchone()
        connection.close()
        
        # এখানে আমরা ইউজারের সামনে ফর্মটি ওপেন করছি
        return render_template('application_form.html', job=job)
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
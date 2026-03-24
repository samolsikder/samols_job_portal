import mysql.connector
from flask import Flask, render_template, jsonify, request 
import requests
import os

app = Flask(__name__)

# ডাটাবেস কানেকশন ডিটেইলস
app.config['MYSQL_HOST'] = 'pg-3689f3ca-samolsikder45-ea9b.c.aivencloud.com'
app.config['MYSQL_USER'] = 'avnadmin'
app.config['MYSQL_PASSWORD'] = os.environ.get('DB_PASSWORD', 'AVNS_RgWvdbzCpHlr2n_J8VF')
app.config['MYSQL_DB'] = 'defaultdb'
app.config['MYSQL_PORT'] = 23399
app.config['MYSQL_CUSTOM_OPTIONS'] = {'ssl': {'ca': 'ca.pem'}}

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
        print(f"Error: {e}")
        return "ডাটাবেস কানেক্ট করতে সমস্যা হচ্ছে।"

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
        print(f"Error: {e}")
        return "বিস্তারিত দেখাতে সমস্যা হচ্ছে।"

@app.route("/api/jobs")
def list_jobs():
    jobs = load_jobs_from_db()
    return jsonify(jobs)

@app.route("/job/<id>/apply", methods=['POST'])
def apply_to_job(id):
    # ১. ক্যাপচা চেক করা
    recaptcha_response = request.form.get('g-recaptcha-response')
    secret_key = "6LcCUpYsAAAAAN2X6l8ozXDNhqVTsVivARCJhp7j" # এখানে Secret Key দিন
    
    # গুগলের কাছে ভেরিফিকেশনের জন্য পাঠানো
    verify_url = f"https://www.google.com/recaptcha/api/siteverify?secret={secret_key}&response={recaptcha_response}"
    response = requests.post(verify_url).json()

    if not response.get('success'):
        # যদি ক্যাপচা পূরণ না করা হয় বা ভুল হয়
        return "দয়া করে 'I am not a robot' চেকবক্সটি পূরণ করুন!"

    # ২. ক্যাপচা সফল হলে বাকি কাজ (ডাটাবেসে সেভ করা)
    data = request.form
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        
        # আপনার আগের ইনসার্ট কুয়েরি এখানে চলবে...
        insert_query = "INSERT INTO applications (job_id, full_name, email) VALUES (%s, %s, %s)"
        cursor.execute(insert_query, (id, data.get('full_name'), data.get('email')))
        connection.commit()
        
        # জবের তথ্য আনা
        cursor.execute("SELECT * FROM jobs WHERE id = %s", (id,))
        job_info = cursor.fetchone()
        
        cursor.close()
        connection.close()

        return render_template('application_submitted.html', application=data, job=job_info)
                               
    except Exception as e:
        print(f"Error: {e}")
        return "আবেদন জমা দিতে সমস্যা হয়েছে।"

# এই অংশটি একদম বাম থেকে শুরু হবে
if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)            
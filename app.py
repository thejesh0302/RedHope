# app.py
from flask import Flask, render_template, request, redirect, session, url_for, flash
import sqlite3
from datetime import datetime
from database import create_connection

app = Flask(__name__)
app.secret_key = "redhope_secret_key"

@app.route('/')
def home():
    return redirect('/login')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/signup', methods=['GET','POST'])
def signup():

    if request.method == 'POST':

        name = request.form['full_name']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        phone = request.form['phone']
        location = request.form['city']

        conn = create_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email=?", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            conn.close()
            flash("Email already exists")
            return redirect('/signup')

        cursor.execute(
        "INSERT INTO users (full_name,email,password,role,phone,city) VALUES (?,?,?,?,?,?)",
        (name,email,password,role,phone,location)
        )

        conn.commit()
        conn.close()

        flash("Registration successful! Please login.")
        return redirect('/login')

    return render_template('signup.html')

@app.route('/login', methods=['POST'])
def login():

    email = request.form['email']
    password = request.form['password']

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE email=? AND password=?", (email,password))
    user = cursor.fetchone()

    conn.close()

    if user:

        session['user_id'] = user[0]
        session['name'] = user[1]
        session['role'] = user[4]

        if user[4] == 'Donor':
            return redirect('/donor_dashboard')

        elif user[4] == 'Patient':
            return redirect('/patient_dashboard')

    flash("Invalid Email or Password")
    return redirect('/login')

@app.route('/donor_dashboard')
def donor_dashboard():

    if 'user_id' not in session or session.get('role') != 'Donor':
        return redirect('/login')

    return render_template('donor_dashboard.html')

@app.route('/patient_dashboard')
def patient_dashboard():

    if 'user_id' not in session or session.get('role') != 'Patient':
        return redirect('/login')

    return render_template('patient_dashboard.html')

@app.route('/donor_form', methods=['GET','POST'])
def donor_form():

    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':

        user_id = session['user_id']
        blood_group = request.form.get('blood_group')
        last_donation = request.form.get('last_donation_date')
        medical = request.form.get('medical_conditions')
        medication = request.form.get('medication')
        chronic_disease = request.form.get('chronic_disease')
        tattoo_recent = request.form.get('tattoo_recent')
        alcohol_recent = request.form.get('alcohol_recent')

        try:
            age = int(request.form.get('age'))
            weight = float(request.form.get('weight'))
            hemoglobin = float(request.form.get('hemoglobin'))
        except (ValueError, TypeError):
            flash("Age, weight and hemoglobin must be valid numbers")
            return redirect('/donor_form')        
        
        eligible = True

        if age < 18 or age > 65:
            eligible = False

        if weight < 50:
            eligible = False

        if hemoglobin < 12.5:
            eligible = False

        if last_donation:
            last_date = datetime.strptime(last_donation,"%Y-%m-%d")
            today = datetime.today()
            days_gap = (today - last_date).days

            if days_gap < 90:
                eligible = False

        if medication == 'Yes':
            eligible = False

        if chronic_disease == 'Yes':
            eligible = False

        if tattoo_recent == 'Yes':
            eligible = False

        if alcohol_recent == 'Yes':
            eligible = False

        status = "Eligible" if eligible else "Not Eligible"

        conn = create_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT donor_id FROM donor_details WHERE donor_id = ?", (user_id,))
        existing = cursor.fetchone()

        if existing:
            cursor.execute("""
            UPDATE donor_details
            SET blood_group=?, age=?, weight=?, last_donation_date=?,
                availability_status=?, medical_conditions=?, hemoglobin_level=?,
                medication=?, chronic_disease=?, tattoo_recent=?, alcohol_recent=?
            WHERE donor_id=?
            """, (blood_group, age, weight, last_donation, status, medical, hemoglobin, medication, chronic_disease, tattoo_recent, alcohol_recent, user_id))
        else:
            cursor.execute("""
            INSERT INTO donor_details
            (donor_id, blood_group, age, weight, last_donation_date, availability_status, medical_conditions, hemoglobin_level, medication, chronic_disease, tattoo_recent, alcohol_recent)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
            """, (user_id, blood_group, age, weight, last_donation, status, medical, hemoglobin, medication, chronic_disease, tattoo_recent, alcohol_recent))

        conn.commit()
        conn.close()

        return f"Eligibility Status: {status}"

    return render_template('donor_form.html')

@app.route('/blood_request_form', methods=['GET', 'POST'])
def blood_request_form():

    if 'user_id' not in session or session.get('role') != 'Patient':
        return redirect('/login')

    if request.method == 'POST':

        patient_id = session['user_id']
        blood_group = request.form.get('blood_group')
        units = request.form.get('units')
        hospital = request.form.get('hospital')
        city = request.form.get('city')
        urgency = request.form.get('urgency')

        try:
            units = int(units)
        except (ValueError, TypeError):
            flash("Units must be a valid number")
            return redirect('/blood_request_form')

        conn = create_connection()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO patient_requests
        (patient_id, blood_group_needed, units_required, hospital_name, city, urgency_level, status)
        VALUES (?, ?, ?, ?, ?, ?, 'Pending')
        """, (patient_id, blood_group, units, hospital, city, urgency))

        conn.commit()
        conn.close()

        flash("Blood request submitted successfully")
        return redirect('/patient_dashboard')

    return render_template('blood_request_form.html')

@app.route('/match_donors/<int:request_id>')
def match_donors(request_id):

    if 'user_id' not in session:
        return redirect('/login')

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM patient_requests WHERE request_id=?", (request_id,))
    blood_request = cursor.fetchone()

    if not blood_request:
        conn.close()
        flash("Request not found")
        return redirect('/patient_dashboard')

    blood_group = blood_request[2]
    city = blood_request[5]

    cursor.execute("""
        SELECT u.full_name, u.phone, u.city, d.blood_group, d.age, d.weight, d.hemoglobin_level
        FROM donor_details d
        JOIN users u ON d.donor_id = u.id
        WHERE d.blood_group = ?
        AND u.city = ?
        AND d.availability_status = 'Eligible'
    """, (blood_group, city))

    matched_donors = cursor.fetchall()
    conn.close()

    return render_template('match_donors.html', donors=matched_donors, request=blood_request)

@app.route('/my_requests')
def my_requests():

    if 'user_id' not in session or session.get('role') != 'Patient':
        return redirect('/login')

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM patient_requests WHERE patient_id=? ORDER BY request_date DESC", (session['user_id'],))
    requests = cursor.fetchall()
    conn.close()

    return render_template('my_requests.html', requests=requests)

@app.route('/logout')
def logout():

    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
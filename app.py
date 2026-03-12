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

        status = "Eligible" if eligible else "Not Eligible"

        conn = create_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT donor_id FROM donor_details WHERE donor_id = ?", (user_id,))
        existing = cursor.fetchone()

        if existing:
            cursor.execute("""
            UPDATE donor_details
            SET blood_group=?, age=?, weight=?, last_donation_date=?,
                availability_status=?, medical_conditions=?, hemoglobin_level=?
            WHERE donor_id=?
            """, (blood_group, age, weight, last_donation, status, medical, hemoglobin, user_id))
        else:
            cursor.execute("""
            INSERT INTO donor_details
            (donor_id, blood_group, age, weight, last_donation_date, availability_status, medical_conditions, hemoglobin_level)
            VALUES (?,?,?,?,?,?,?,?)
            """, (user_id, blood_group, age, weight, last_donation, status, medical, hemoglobin))

        conn.commit()
        conn.close()

        return f"Eligibility Status: {status}"

    return render_template('donor_form.html')

@app.route('/logout')
def logout():

    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
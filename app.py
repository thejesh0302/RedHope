from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "redhope_super_secret_key"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('redhope.db')
        cursor = conn.cursor()

        cursor.execute("""
        SELECT * FROM users WHERE email=? AND password=?
        """, (email, password))

        user = cursor.fetchone()
        conn.close()

        if user:
            session['user_id'] = user[0]
            session['role'] = user[4]

            if user[4] == "Donor":
                return redirect('/donor')
            elif user[4] == "Patient":
                return redirect('/patient')
        else:
            return "Invalid Email or Password"

    return render_template('login.html')

@app.route('/donor')
def donor():
    return "Donor Dashboard"

@app.route('/patient')
def patient():
    return "Patient Dashboard"

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        phone = request.form['phone']
        city = request.form['city']

        try:
            conn = sqlite3.connect('redhope.db')
            cursor = conn.cursor()

            cursor.execute("""
            INSERT INTO users (full_name, email, password, role, phone, city)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (full_name, email, password, role, phone, city))

            conn.commit()
            conn.close()

            return redirect('/login')

        except sqlite3.IntegrityError:
            return "Email already exists"

    return render_template('signup.html')

if __name__ == '__main__':
    app.run(debug=True)
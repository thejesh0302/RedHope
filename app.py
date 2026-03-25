#app.py:
from flask import Flask, render_template, request, redirect, session, url_for, flash
import sqlite3
from datetime import datetime
from database import create_connection
import urllib.request
import json
import math
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def calculate_distance(lat1, lon1, lat2, lon2):
    if lat1 == None or lon1 == None or lat2 == None or lon2 == None:
        return float('inf')
    R = 6371 # km
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = math.sin(dLat/2) * math.sin(dLat/2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon/2) * math.sin(dLon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

HOSPITALS = {
    "Chennai": [
        {"name": "Apollo Hospitals", "lat": 13.0604, "lng": 80.2496},
        {"name": "Rajiv Gandhi Govt General Hospital", "lat": 13.0827, "lng": 80.2707},
        {"name": "MIOT International", "lat": 13.0163, "lng": 80.1903}
    ],
    "Bangalore": [
        {"name": "NIMHANS", "lat": 12.9373, "lng": 77.5936},
        {"name": "Manipal Hospital", "lat": 12.9592, "lng": 77.6485},
        {"name": "Fortis Hospital", "lat": 12.8938, "lng": 77.5985}
    ],
    "Coimbatore": [
        {"name": "Ganga Hospital", "lat": 11.0118, "lng": 76.9463},
        {"name": "Kovai Medical Center (KMCH)", "lat": 11.0371, "lng": 77.0347},
        {"name": "Ramakrishna Hospital", "lat": 11.0267, "lng": 76.9535}
    ],
    "Hyderabad": [
        {"name": "KIMS Hospital", "lat": 17.4357, "lng": 78.4842},
        {"name": "Yashoda Hospitals", "lat": 17.4272, "lng": 78.4610},
        {"name": "Apollo Health City", "lat": 17.4190, "lng": 78.4124}
    ]
}

app = Flask(__name__)
app.secret_key = "redhope_secret_key"

def get_ai_eligibility_explanation(age, weight, hemoglobin, last_donation, medication, chronic_disease, tattoo_recent, alcohol_recent):

    reasons = []
    if age < 18 or age > 65:
        reasons.append(f"age is {age} (must be between 18 and 65)")
    if weight < 50:
        reasons.append(f"weight is {weight}kg (minimum 50kg required)")
    if hemoglobin < 12.5:
        reasons.append(f"hemoglobin is {hemoglobin} g/dL (minimum 12.5 required)")
    if last_donation:
        last_date = datetime.strptime(last_donation, "%Y-%m-%d")
        days_gap = (datetime.today() - last_date).days
        if days_gap < 90:
            reasons.append(f"last donation was {days_gap} days ago (minimum 90 days gap required)")
    if medication == 'Yes':
        reasons.append("currently on medication")
    if chronic_disease == 'Yes':
        reasons.append("has a chronic disease")
    if tattoo_recent == 'Yes':
        reasons.append("got a tattoo in the last 6 months")
    if alcohol_recent == 'Yes':
        reasons.append("consumed alcohol in the last 24 hours")

    prompt = f"""A blood donor has been found NOT ELIGIBLE to donate blood for the following reasons: {', '.join(reasons)}.

Write a short, kind and encouraging message (3-4 sentences) explaining why they are not eligible right now, what they can do to become eligible, and encourage them to try again when they are ready. Address them directly as 'you'. Be warm and supportive, not clinical."""

    try:
        api_key = os.environ.get("GROQ_API_KEY")
        url = "https://api.groq.com/openai/v1/chat/completions"

        data = json.dumps({
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 200
        }).encode('utf-8')

        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
                "User-Agent": "Mozilla/5.0"
            }
        )

        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result['choices'][0]['message']['content']

    except Exception as e:
        print(f"Groq API error: {e}")
        return "You are currently not eligible to donate blood. Please review the eligibility criteria and try again when your health conditions meet the requirements."

@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect('/login')
    if session.get('role') == 'Donor':
        return redirect('/donor_dashboard')
    elif session.get('role') == 'Patient':
        return redirect('/patient_dashboard')
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
        
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        try:
            latitude = float(latitude) if latitude else None
            longitude = float(longitude) if longitude else None
        except ValueError:
            latitude = None
            longitude = None

        conn = create_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email=?", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            conn.close()
            flash("Email already exists")
            return redirect('/signup')

        cursor.execute(
            "INSERT INTO users (full_name,email,password,role,phone,city,latitude,longitude) VALUES (?,?,?,?,?,?,?,?)",
            (name, email, password, role, phone, location, latitude, longitude)
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
    cursor.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
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

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT availability_status FROM donor_details WHERE donor_id=?", (session['user_id'],))
    result = cursor.fetchone()
    conn.close()

    availability = result[0] if result else None
    return render_template('donor_dashboard.html', availability=availability)

@app.route('/patient_dashboard')
def patient_dashboard():
    if 'user_id' not in session or session.get('role') != 'Patient':
        return redirect('/login')
    return render_template('patient_dashboard.html')

@app.route('/donor_form', methods=['GET','POST'])
def donor_form():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    if request.method == 'POST':
        user_id = session['user_id']
        blood_group = request.form.get('blood_group')
        last_donation = request.form.get('last_donation_date')
        medical = request.form.get('medical_conditions')
        medication = request.form.get('medication')
        chronic_disease = request.form.get('chronic_disease')
        tattoo_recent = request.form.get('tattoo_recent')
        alcohol_recent = request.form.get('alcohol_recent')
        available_from = request.form.get('available_from')
        available_to = request.form.get('available_to')

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
            last_date = datetime.strptime(last_donation, "%Y-%m-%d")
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
                    medication=?, chronic_disease=?, tattoo_recent=?, alcohol_recent=?,
                    available_from=?, available_to=?
                WHERE donor_id=?
            """, (blood_group, age, weight, last_donation, status, medical, hemoglobin,
                  medication, chronic_disease, tattoo_recent, alcohol_recent,
                  available_from, available_to, user_id))
        else:
            cursor.execute("""
                INSERT INTO donor_details
                (donor_id, blood_group, age, weight, last_donation_date, availability_status,
                 medical_conditions, hemoglobin_level, medication, chronic_disease,
                 tattoo_recent, alcohol_recent, available_from, available_to)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (user_id, blood_group, age, weight, last_donation, status, medical, hemoglobin,
                  medication, chronic_disease, tattoo_recent, alcohol_recent,
                  available_from, available_to))

        conn.commit()
        conn.close()

        if status == "Eligible":
            flash("You are Eligible to donate blood. Thank you!")
            return redirect('/donor_dashboard')
        else:
            ai_explanation = get_ai_eligibility_explanation(
                age, weight, hemoglobin, last_donation,
                medication, chronic_disease, tattoo_recent, alcohol_recent
            )
            return render_template('not_eligible.html', explanation=ai_explanation)

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
        required_time = request.form.get('required_time')

        try:
            units = int(units)
        except (ValueError, TypeError):
            flash("Units must be a valid number")
            return redirect('/blood_request_form')

        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO patient_requests
            (patient_id, blood_group_needed, units_required, hospital_name, city, urgency_level, status, required_time)
            VALUES (?, ?, ?, ?, ?, ?, 'Pending', ?)
        """, (patient_id, blood_group, units, hospital, city, urgency, required_time))
        conn.commit()
        conn.close()

        flash("Blood request submitted successfully")
        return redirect('/patient_dashboard')

    return render_template('blood_request_form.html', hospitals=HOSPITALS)

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
    required_time = blood_request[9]
    urgency = blood_request[6]
    patient_id = blood_request[1]
    hospital_name = blood_request[4]

    patient_lat, patient_lon = None, None
    
    # Try getting coordinates for the selected hospital
    if city in HOSPITALS:
        for h in HOSPITALS[city]:
            if h['name'] == hospital_name:
                patient_lat = h['lat']
                patient_lon = h['lng']
                break

    # Fallback to patient's registered home location
    if patient_lat is None or patient_lon is None:
        cursor.execute("SELECT latitude, longitude FROM users WHERE id=?", (patient_id,))
        patient_loc = cursor.fetchone()
        patient_lat, patient_lon = patient_loc if patient_loc else (None, None)

    cursor.execute("""
        SELECT u.full_name, u.phone, u.city, d.blood_group, d.age, d.weight, d.hemoglobin_level, d.donor_id, u.latitude, u.longitude
        FROM donor_details d
        JOIN users u ON d.donor_id = u.id
        WHERE d.blood_group = ?
        AND u.city = ?
        AND d.availability_status = 'Eligible'
        AND d.available_from <= ?
        AND d.available_to >= ?
    """, (blood_group, city, required_time, required_time))

    matched_donors = cursor.fetchall()
    conn.close()

    donors_list = []
    for row in matched_donors:
        donor_lat, donor_lon = row[8], row[9]
        dist = calculate_distance(patient_lat, patient_lon, donor_lat, donor_lon)
        dist_str = f"{dist:.1f} km" if dist != float('inf') else "N/A"

        donors_list.append({
            'name': row[0],
            'phone': row[1],
            'city': row[2],
            'blood_group': row[3],
            'age': row[4],
            'weight': row[5],
            'hemoglobin': row[6],
            'donor_id': row[7],
            'distance_val': dist,
            'distance': dist_str
        })

    # Sort matching donors by distance, then hemoglobin level
    donors_list.sort(key=lambda x: (x['distance_val'], -x['hemoglobin']))
    donors_list = donors_list[:5] # limit to top 5 closest donors

    return render_template('match_donors.html', donors=donors_list, request=blood_request)

@app.route('/send_request/<int:request_id>/<int:donor_id>')
def send_request(request_id, donor_id):
    if 'user_id' not in session or session.get('role') != 'Patient':
        return redirect('/login')

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM blood_requests WHERE request_id=? AND donor_id=?", (request_id, donor_id))
    existing = cursor.fetchone()

    if existing:
        conn.close()
        flash("You have already sent a request to this donor")
        return redirect('/my_requests')

    cursor.execute("""
        INSERT INTO blood_requests (request_id, donor_id, match_status)
        VALUES (?, ?, 'Pending')
    """, (request_id, donor_id))
    conn.commit()
    conn.close()

    flash("Request sent to donor successfully")
    return redirect('/my_requests')

@app.route('/donor_notifications')
def donor_notifications():
    if 'user_id' not in session or session.get('role') != 'Donor':
        return redirect('/login')

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.full_name, u.phone, pr.blood_group_needed, pr.units_required,
               pr.hospital_name, pr.city, pr.urgency_level, pr.request_date,
               br.match_status, pr.status, br.match_id
        FROM blood_requests br
        JOIN patient_requests pr ON br.request_id = pr.request_id
        JOIN users u ON pr.patient_id = u.id
        WHERE br.donor_id = ?
        ORDER BY pr.request_date DESC
    """, (session['user_id'],))

    notifications = cursor.fetchall()
    conn.close()
    return render_template('donor_notifications.html', notifications=notifications)

@app.route('/respond_request/<int:match_id>/<string:action>')
def respond_request(match_id, action):
    if 'user_id' not in session or session.get('role') != 'Donor':
        return redirect('/login')

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM blood_requests WHERE match_id=?", (match_id,))
    match = cursor.fetchone()

    if not match:
        conn.close()
        flash("Request not found")
        return redirect('/donor_notifications')

    if action == 'accept':
        cursor.execute("UPDATE blood_requests SET match_status='Accepted' WHERE match_id=?", (match_id,))
        cursor.execute("UPDATE patient_requests SET status='Fulfilled' WHERE request_id=?", (match[1],))
        cursor.execute("UPDATE donor_details SET availability_status='Not Available' WHERE donor_id=?", (session['user_id'],))
        cursor.execute("""
            INSERT INTO donation_history (donor_id, patient_id, hospital_name, units_donated)
            SELECT br.donor_id, pr.patient_id, pr.hospital_name, pr.units_required
            FROM blood_requests br
            JOIN patient_requests pr ON br.request_id = pr.request_id
            WHERE br.match_id = ?
        """, (match_id,))
        flash("You have accepted the request. Thank you for donating!")

    elif action == 'reject':
        cursor.execute("UPDATE blood_requests SET match_status='Rejected' WHERE match_id=?", (match_id,))
        flash("You have rejected the request.")

    conn.commit()
    conn.close()
    return redirect('/donor_notifications')

@app.route('/my_requests')
def my_requests():
    if 'user_id' not in session or session.get('role') != 'Patient':
        return redirect('/login')

    conn = create_connection()
    cursor = conn.cursor()

    # Auto-expire requests older than 7 days
    cursor.execute("""
        UPDATE patient_requests
        SET status = 'Expired'
        WHERE status = 'Pending'
        AND request_date <= datetime('now', '-7 days')
    """)
    conn.commit()

    cursor.execute("SELECT * FROM patient_requests WHERE patient_id=? ORDER BY request_date DESC", (session['user_id'],))
    requests = cursor.fetchall()
    conn.close()
    return render_template('my_requests.html', requests=requests)

@app.route('/donation_history')
def donation_history():
    if 'user_id' not in session:
        return redirect('/login')

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT d.full_name, p.full_name, dh.donation_date, dh.hospital_name, dh.units_donated
        FROM donation_history dh
        JOIN users d ON dh.donor_id = d.id
        JOIN users p ON dh.patient_id = p.id
        ORDER BY dh.donation_date DESC
    """)
    rows = cursor.fetchall()
    conn.close()

    history = []
    for row in rows:
        history.append({
            'donor_name': row[0],
            'patient_name': row[1],
            'date': row[2],
            'hospital': row[3],
            'units': row[4]
        })
    return render_template('donation_history.html', history=history)

@app.route('/toggle_availability')
def toggle_availability():
    if 'user_id' not in session or session.get('role') != 'Donor':
        return redirect('/login')

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT availability_status FROM donor_details WHERE donor_id=?", (session['user_id'],))
    result = cursor.fetchone()

    if not result:
        conn.close()
        flash("Please fill your eligibility form first before changing availability.")
        return redirect('/donor_dashboard')

    current_status = result[0]

    if current_status == 'Eligible':
        new_status = 'Not Available'
        flash("You are now marked as Not Available.")
    else:
        new_status = 'Eligible'
        flash("You are now marked as Available.")

    cursor.execute("UPDATE donor_details SET availability_status=? WHERE donor_id=?", (new_status, session['user_id']))
    conn.commit()
    conn.close()

    return redirect('/donor_dashboard')

@app.route('/certificate/<int:match_id>')
def certificate(match_id):
    if 'user_id' not in session or session.get('role') != 'Donor':
        return redirect('/login')

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT u.full_name, pr.blood_group_needed, pr.units_required,
               pr.hospital_name, pr.city, dh.donation_date, p.full_name
        FROM blood_requests br
        JOIN patient_requests pr ON br.request_id = pr.request_id
        JOIN users u ON br.donor_id = u.id
        JOIN users p ON pr.patient_id = p.id
        JOIN donation_history dh ON dh.donor_id = br.donor_id AND dh.hospital_name = pr.hospital_name
        WHERE br.match_id = ?
    """, (match_id,))

    data = cursor.fetchone()
    conn.close()

    if not data:
        flash("Certificate not found")
        return redirect('/donor_dashboard')

    certificate_data = {
        'donor_name': data[0],
        'blood_group': data[1],
        'units': data[2],
        'hospital': data[3],
        'city': data[4],
        'date': data[5][:10],
        'patient_name': data[6]
    }

    return render_template('certificate.html', cert=certificate_data)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
# 🩸 RedHope
### AI-Integrated Smart Blood Donor Matching and Coordination System

[![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-Web%20Framework-black?logo=flask)](https://flask.palletsprojects.com)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?logo=sqlite&logoColor=white)](https://sqlite.org)
[![Groq AI](https://img.shields.io/badge/Groq-llama--3.3--70b-orange)](https://groq.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-red.svg)](LICENSE)

> **RedHope** connects blood donors with patients in need by automating the entire matching pipeline using blood group compatibility, geographic proximity, time availability, and urgency level — powered by AI.

---

## 📌 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Database Schema](#-database-schema)
- [Getting Started](#-getting-started)
- [Environment Setup](#-environment-setup)
- [How It Works](#-how-it-works)
- [AI Integration](#-ai-integration)
- [Screenshots](#-screenshots)
- [Test Accounts](#-test-accounts)
- [Known Limitations](#-known-limitations)
- [Future Enhancements](#-future-enhancements)
- [License](#-license)

---

## 🔍 Overview

RedHope is a full-stack web application built as an **MCA Final Year Project**. It solves the real-world problem of slow, manual blood donor coordination by automating every stage of the donor–patient pipeline:

- Donors register, fill a health eligibility form, and get matched to patients in their city
- Patients submit blood requests with urgency levels and find the closest eligible donors
- The system ranks donors by **real-world geographic distance** using the Haversine formula
- **Groq AI** (llama-3.3-70b-versatile) generates personalised, encouraging feedback for ineligible donors
- Completed donations are recorded and donors receive a **printable certificate**

---

## ✨ Features

### Core
- 🔐 **Role-based authentication** — Separate Donor and Patient dashboards with session protection
- 🏥 **8-criteria eligibility screening** — Age, weight, hemoglobin, last donation date, medication, chronic disease, tattoo, alcohol
- 🤖 **AI eligibility explanation** — Groq API generates warm, personalised feedback for ineligible donors
- 📍 **Haversine distance matching** — Ranks donors by real-world km distance from the patient's hospital
- 🩸 **Smart donor matching** — Filters by blood group, city, and time availability; returns top 5 donors
- 📋 **Request lifecycle management** — Submit, notify, accept/reject, auto-expiry after 7 days
- 📜 **Blood donation certificate** — Printable certificate generated on successful donation
- 🔄 **Availability toggle** — Donors can manually set themselves available or unavailable
- ⏰ **Double-booking prevention** — Donors marked unavailable after accepting a request
- 🗂️ **Donation history** — Complete record accessible to both donors and patients

### UI
- Split-layout login and signup pages with hero illustrations
- Dark charcoal sidebars with motivational content on dashboards
- Fully responsive design — stacks vertically on mobile screens
- Flash messages across all routes for success and error feedback
- Custom 404 error page
- No external CSS framework — 100% custom CSS

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.13, Flask |
| Database | SQLite (`redhope.db`) |
| Frontend | HTML5, CSS3, Jinja2 Templates |
| AI | Groq API — `llama-3.3-70b-versatile` |
| Distance | Haversine Formula |
| Fonts | DM Sans, Playfair Display (Google Fonts) |

---

## 📁 Project Structure

```
RedHope/
├── app.py                      # Main Flask application — all routes, logic, AI, Haversine
├── database.py                 # SQLite setup and create_connection() helper
├── generate_report.py          # Utility script for report generation
├── patch_db.py                 # Utility script for database patching
├── redhope.db                  # SQLite database file
├── LICENSE
├── .gitignore
│
├── screenshots/                # Application screenshots
│
├── static/
│   ├── css/
│   │   └── style.css           # Complete custom CSS with design tokens
│   └── images/
│       ├── redhope_logo.png
│       ├── redhope_name_logo.png
│       ├── redhope_name_logo2.png
│       ├── hero.svg            # Login page illustration
│       ├── hero2.svg           # Signup page illustration
│       ├── hero3.svg           # Donor dashboard sidebar
│       ├── hero4.svg           # Patient dashboard sidebar
│       ├── hero5.svg           # My Requests page
│       ├── hero6.svg           # Donation History page
│       ├── hero_community.png
│       ├── hero_doctor.png
│       └── hero_donate.png
│
└── templates/
    ├── base.html               # Base template with navbar and flash messages
    ├── index.html              # Welcome page
    ├── login.html
    ├── signup.html
    ├── donor_dashboard.html
    ├── patient_dashboard.html
    ├── donor_form.html
    ├── blood_request_form.html
    ├── match_donors.html
    ├── donor_notifications.html
    ├── my_requests.html
    ├── donation_history.html
    ├── not_eligible.html
    ├── certificate.html
    ├── patch_db.html
    └── 404.html
```

---

## 🗃 Database Schema

RedHope uses 5 SQLite tables:

```
users               → All user accounts (Donor and Patient)
donor_details       → Health screening data and availability
patient_requests    → Blood requests submitted by patients
blood_requests      → Donor–patient match records
donation_history    → Completed donation records
```

The `users` table stores `latitude` and `longitude` for geographic distance matching. The `donor_details` table records all 8 eligibility criteria and time availability windows.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- pip

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/thejesh0302/RedHope.git
cd RedHope

# 2. Create and activate a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# 3. Install dependencies
pip install flask

# 4. Initialise the database
python database.py

# 5. Run the application
python app.py
```

Then open your browser at:
```
http://127.0.0.1:5000
```

---

## ⚙️ Environment Setup

The Groq API key is currently stored directly in `app.py` inside the `get_ai_eligibility_explanation()` function. Before deploying to production, move it to an environment variable:

```python
import os
API_KEY = os.environ.get("GROQ_API_KEY")
```

Then set it in your shell:

```bash
# Windows
set GROQ_API_KEY=your_key_here

# macOS / Linux
export GROQ_API_KEY=your_key_here
```

Get your free API key at [console.groq.com](https://console.groq.com).

---

## ⚙️ How It Works

### Donor Flow
```
Register → Fill eligibility form → Marked Eligible
→ Appear in patient search results
→ Receive blood request notification
→ Accept → Donation recorded → Certificate generated
```

### Patient Flow
```
Register → Submit blood request (blood group, hospital, urgency)
→ Click Find Donors → View top 5 matched donors ranked by distance
→ Send request to chosen donor → Wait for acceptance
```

### Matching Algorithm

1. Filter donors by blood group, city, and time availability
2. Look up hospital coordinates from the `HOSPITALS` dictionary
3. Calculate Haversine distance from hospital to each donor
4. Sort by distance (ascending), then hemoglobin level (descending)
5. Return top 5 results

```python
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Earth's radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
```

---

## 🤖 AI Integration

RedHope uses the **Groq API** with the `llama-3.3-70b-versatile` model to generate personalised eligibility feedback for donors who do not pass the health screening.

**Trigger:** Donor submits eligibility form → fails one or more criteria → AI generates a 3–4 sentence warm, encouraging message explaining why and what to do next.

**Fallback:** If the Groq API is unavailable, a generic message is shown — the system never breaks.

**Endpoint:** `https://api.groq.com/openai/v1/chat/completions`

**Cities and Hospitals covered:**

| City | Hospitals |
|---|---|
| Chennai | Apollo Hospitals, Rajiv Gandhi Govt General Hospital, MIOT International |
| Bangalore | NIMHANS, Manipal Hospital, Fortis Hospital |
| Coimbatore | Ganga Hospital, KMCH, Ramakrishna Hospital |
| Hyderabad | KIMS Hospital, Yashoda Hospitals, Apollo Health City |

---

## 📸 Screenshots

| Page | Preview |
|---|---|
| Login | ![Login](screenshots/Login%20Page.png) |
| Donor Dashboard | ![Donor Dashboard](screenshots/Donor%20Dashboard.png) |
| Eligibility Form | ![Eligibility Form](screenshots/Donor%20Page.png) |
| Patient Dashboard | ![Patient Dashboard](screenshots/Patient%20(Requests)%20Dash....png) |
| Blood Request Form | ![Blood Request Form](screenshots/Blood%20Request%20Form.png) |
| Sign Up | ![Sign Up](screenshots/Sign%20Up%20Page.png) |

---

## 🧪 Test Accounts

| Name | Email | Password | Role | Details |
|---|---|---|---|---|
| Arjun Kumar | arjun@test.com | test123 | Donor | O+, Chennai |
| Priya Sharma | priya@test.com | test123 | Donor | AB+, Bangalore |
| Ravi Menon | ravi@test.com | test123 | Patient | Chennai |

---

## ⚠️ Known Limitations

- Passwords are stored in **plain text** — `werkzeug.security` hashing to be added before production
- Blood group compatibility logic (e.g. O- as universal donor) not yet implemented
- No real-time push/email/SMS notifications — requests are in-app only
- Hospital coordinates are hardcoded — limited to 12 hospitals across 4 cities
- Donors are not automatically re-marked Eligible after the 90-day wait period

---

## 🔮 Future Enhancements

- [ ] Password hashing with `werkzeug.security`
- [ ] Blood group compatibility matching (universal donor logic)
- [ ] Firebase / Twilio for real-time push and SMS notifications
- [ ] AI chatbot for donor and patient FAQs (Groq-powered)
- [ ] Auto re-eligibility after 90-day wait period
- [ ] Donation streak tracking and badge system
- [ ] Dynamic hospital database with admin panel
- [ ] Multi-city and rural expansion

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  Built with ❤️ by <strong>Thejesh</strong> · MCA Final Year Project · 2024–2025
</p>

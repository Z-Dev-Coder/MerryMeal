# 🍲 MerryMeal — Charity Meal Delivery Web Application

An academic team project built using an Agile/Scrum framework to deliver meals to vulnerable individuals and seniors.

> **Role & Context**: Developed in an Agile/Scrum team of 5 developers during the Higher National Diploma (HND) in Software Engineering program. Contributed to role-based access control, dispatch workflows, view templates, and sprint planning.

---

## 🌟 Key Features

- 👥 **Role-Based Portals**: Dedicated interfaces for Members, Caregivers, Partner Kitchens, Volunteer Riders, and Administrators.
- 📦 **Meal Preparation & Safety Tracking**: Food safety logging, dietary condition tracking, and hot/frozen meal categorization.
- 🗺️ **GIS Logistics & Dispatch**: Distance and route validation to ensure meals are delivered within safe temperature windows.
- 💳 **Donations & Donor Ledger**: Online fundraising and partner pledges tracking.
- 📧 **Automated Notifications**: Alert dispatchers and members upon order status changes.

---

## 🛠️ Technology Stack

- **Backend**: Python 3, Django Web Framework
- **Frontend**: Django Template Language (DTL), HTML5, CSS3, Bootstrap 5, JavaScript
- **Database**: SQLite / MySQL (via Django ORM)
- **Methodology**: Agile / Scrum (Sprints, Stand-ups, Backlog refinement)

---

## 🚀 Getting Started

### 1. Clone & Set Up Virtual Environment

```bash
git clone https://github.com/Z-Dev-Coder/MerryMeal.git
cd MerryMeal

python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install django
```

### 3. Run Migrations & Start Server

```bash
python manage.py migrate
python manage.py runserver
```

Open `http://127.0.0.1:8000/` in your browser.

---

## 📄 License

MIT License

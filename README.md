# MerryMeal — Meals on Wheels Charity Web Application

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.0-092E20.svg)](https://www.djangoproject.com/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5-7952B3.svg)](https://getbootstrap.com/)
[![Methodology](https://img.shields.io/badge/Agile-Scrum_Framework-success.svg)](https://scrumguides.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Academic Project: Agile Project Management (HDSE-PMI) & Enterprise Applications (HDSE-DEA)**  
> **Course**: Higher National Diploma in Software Engineering (EduCLaaS)  
> **Scrum Team**: **Tech Titans** (5 Developers, 1 Scrum Master, 1 Product Owner)  
> **Developer**: Zaw Myo Tun  
> **Client Scenario**: Unity One Solutions developed for *MerryMeal Charity Organization*

---

## 📖 Project Background & Scenario

MerryMeal is a non-profit charity initiative dedicated to preparing and delivering nutritious meals to qualified adults who cannot cook or purchase food for themselves due to age, chronic illness, or physical disability. 

To address the inefficiencies of manual scheduling, paper-based beneficiary intake, and uncoordinated logistics, our 5-developer Scrum team (**Tech Titans**) designed and implemented a unified web platform that coordinates:
- **Weekday Service**: Fresh hot meals cooked by local partner kitchens and delivered by volunteer riders within safe travel radiuses.
- **Weekend Service**: Safe frozen meal packages prepared and dispatched in advance for members living outside standard hot-meal delivery zones.

---

## 👥 Scrum Team Roles & Agile Methodology

| Role | Team Member | Responsibilities |
| :--- | :--- | :--- |
| **Product Owner** | Ms. Wutt Yi Htoo | Backlog prioritization, acceptance criteria & client requirements voice |
| **Scrum Master** | Myint Myat Aung | Sprint ceremonies, blocker resolution, ClickUp board facilitation |
| **Developers** | Zaw Myo Tun, Macasero Van Andrei, Mohamad Amirul, Phyo Min Khant, Kwok Jun Yew | Architecture, Django ORM schema, role dashboards, logistics logic & unit testing |

### Agile Workflow Adopted
- **2-Week Sprint Cycles**: Sprint Planning, Backlog Grooming, Daily Stand-Ups, Sprint Reviews, and Retrospectives.
- **Task Management**: User story mapping and velocity tracking managed in **ClickUp**.
- **Definition of Done (DoD)**: Passing code reviews, database migration checks, and feature validation against user stories.

---

## ✨ Functional Modules & Deliverables

1. **Member & Caregiver Onboarding**:
   - Intake forms capturing dietary restrictions, physical condition, and proof of eligibility.
   - Periodic reassessment workflows to maintain up-to-date beneficiary records.
2. **Food Service Partner & Volunteer Management**:
   - Verification and onboarding for local kitchens and volunteer delivery riders.
3. **Menu Planning & Food Safety Tracking**:
   - Kitchen interface for logging meal preparation times, expiry periods, and cold-chain safety.
4. **GIS Logistics & Dispatch Routing**:
   - Validation checks to verify distance between member locations and kitchen hubs, routing hot meals within a 10 km / safe time window and frozen alternatives beyond it.
5. **Fundraising & Donor Ledger**:
   - Public donation portal tracking financial contributions and partner support transparently.
6. **Management Information System (MIS) Dashboard**:
   - Central administrative overview of active meals delivered, volunteer hours, and operational status.

---

## 🛠️ Technology Stack

- **Backend**: Python 3, Django Web Framework (Django ORM, Authentication, Session Management)
- **Frontend**: Django Template Language (DTL), HTML5, CSS3, Bootstrap 5, Vanilla JavaScript
- **Database**: SQLite (Development) / MySQL compatible schema
- **Agile Tooling**: ClickUp for sprint task tracking and burn-down analytics

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- pip

### Installation & Local Run
```bash
# 1. Clone repository
git clone https://github.com/Z-Dev-Coder/MerryMeal.git
cd MerryMeal

# 2. Set up virtual environment
python -m venv venv
.\venv\Scripts\activate       # Windows
# source venv/bin/activate    # Linux/macOS

# 3. Install Django
pip install django

# 4. Migrate database and run server
python manage.py migrate
python manage.py runserver
```

Open your browser at `http://127.0.0.1:8000/`.

---

## 📄 License

Distributed under the [MIT License](LICENSE).

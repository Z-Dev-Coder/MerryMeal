# Unified Meals on Wheels (MerryMeal) Web Application (Django Version)

This repository contains the **Unified Meals on Wheels (MerryMeal) Web Application** portal, developed using a collaborative, Agile-driven methodology. It represents a unified solution merging accessibility-first design, GIS-driven logistics, kitchen safety/portion scaling, needs evaluation tracking, and a donation ledger.

---

## 🚀 Technology Stack

Our platform is engineered using professional, real-world development standards:

1.  **Frontend (UI/UX)**:
    *   **Structure**: HTML5.
    *   **Templating**: Django Template Language (DTL) (`{% block %}`, static tag loaders).
    *   **Styling & Layout**: Bootstrap 5 (Responsive grid and flexbox utilities) + Custom Premium CSS3 (animations, transitions, HSL color tokens, accessibility controls).
    *   **Client Logic**: Vanilla Javascript (ES6 modules, local event handling, fetch API).
2.  **Backend Server**:
    *   **Framework**: Python Django Web Framework.
3.  **Database**:
    *   **Engine**: MySQL (Relational schema modeling clients, caregivers, volunteers, partner kitchens, menus, routes, safety records, and fundraising via Django ORM models).
4.  **Agile Tracking**:
    *   Sprints managed through ClickUp workflows and documented backlogs.

---

## 🏛️ System Architecture Design

```
                     ┌───────────────────────────────────────────────┐
                     │          Django-Rendered Frontend Portal       │
                     │  (HTML5, DTL, Custom CSS3, Bootstrap, Vanilla JS)│
                     └───────────────────────┬───────────────────────┘
                                             │ HTTP Requests / Form Posts
                                             ▼
                     ┌───────────────────────────────────────────────┐
                     │             Django Web Backend                │
                     │      (Views, Forms, Middlewares, Admin Panel) │
                     └───────┬───────────────────────┬───────────────┘
                             │                       │
      Django ORM Connection  ▼                       ▼  Service Abstraction Layer
                     ┌───────────────┐       ┌───────────────────────────────┐
                     │ MySQL Database│       │     Geo & Payment Services    │
                     │ (Relational)  │       │ (Mock, ready for Maps/Stripe) │
                     └───────────────┘       └───────────────────────────────┘
```

---

## 📁 Repository Directory Structure

```
merrymeal_project/
├── manage.py               # Django CLI management command script
├── merrymeal/              # Django Main Project Settings
│   ├── __init__.py
│   ├── settings.py         # MySQL connection and template static directories
│   ├── urls.py             # Global URL patterns
│   └── wsgi.py             # Core entrypoint
├── core/                   # Django Application App
│   ├── __init__.py
│   ├── apps.py
│   ├── models.py           # MySQL tables modeled as Python Classes (ORM)
│   ├── views.py            # Business logic handlers (Auth, Kitchen, Dispatch, Donor)
│   ├── urls.py             # App-specific URL mappings
│   ├── services/           # Python services
│   │   ├── geo_service.py  # Haversine distance math class
│   │   └── payment_service.py # Mock billing module
│   ├── static/             # Static frontend files
│   │   ├── css/
│   │   │   └── style.css   # Custom CSS design systems & variable tokens
│   │   └── js/
│   │       └── script.js   # Custom JavaScript event animations
│   └── templates/          # Django Template Language HTML
│       ├── base.html       # Shared frame wrapper layout
│       ├── register.html   # Onboarding and form controls
│       ├── kitchen.html    # Chef panels & temp logging forms
│       ├── dispatch.html   # Map grids & volunteer route queue
│       ├── donor.html      # Pledge donation pages
│       └── dashboard.html  # Analytics charts
├── spec.md                 # Full technical system specifications
├── README.md               # Setup and running instructions
└── requirements.txt        # Python dependency manifest
```

---

## 📦 Getting Started & Setup

### Prerequisites
*   Python 3.8 or higher
*   MySQL Server 8.0 or higher
*   `mysqlclient` system libraries (for connecting Python to MySQL)

### Installation
1.  **Clone / Download** this workspace into your local system directory.
2.  **Create & Activate Python Virtual Environment**:
    ```bash
    python -m venv venv
    # On Windows:
    .\venv\Scripts\activate
    ```
3.  **Install Python Dependencies**:
    ```bash
    pip install django mysqlclient pymysql
    ```
4.  **MySQL Database Setup**:
    *   Create a schema named `merrymeal` in your MySQL server.
    *   Update your database credentials directly inside `merrymeal/settings.py` under the `DATABASES` section.
5.  **Compile Django Migrations**:
    ```bash
    python manage.py makemigrations core
    python manage.py migrate
    ```
6.  **Create Administrative Superuser**:
    ```bash
    python manage.py createsuperuser
    ```
7.  **Run the Server (Agile Dev Server)**:
    ```bash
    python manage.py runserver
    ```
    The application will bind to local host port `8000` (`http://127.0.0.1:8000/`).

---

## 📅 Sprint Lifecycle Progress

Refer to the **[task.md](file:///C:/Users/user/.gemini/antigravity/brain/fafad084-5bf8-47e8-84b1-87a4a7ec303f/task.md)** file to track current, active, and completed deliverables. All development is executed sequentially:

*   **Sprint 1**: Accessibility-First Onboarding & User Profiles (In Progress)
*   **Sprint 2**: Dynamic Kitchen Portions & Digital Temperature Loggers
*   **Sprint 3**: GIS Dispatch & 10km Delivery Sequencing
*   **Sprint 4**: Need Reassessments & Donor Pledging Systems
*   **Sprint 5**: Executive MIS Dashboard Analytics

# AgriTech – Crop Batch Management & Analytics Portal

A modern, full-stack enterprise web application designed for agricultural organizations, cooperatives, and farmers to manage crop cultivation lifecycles, field holdings, agricultural inputs, and yield analytics.

---

## 1. Project Overview

**AgriTech** is a complete, production-grade management and analytics platform built with a 3-tier architecture:
- **Presentation Tier**: Modern responsive frontend using HTML5, CSS3, JavaScript, Bootstrap 5, Font Awesome 6, and Chart.js.
- **Application Tier**: RESTful Python Flask backend with modular MVC architecture (Controllers, Services, Models, Routes, and Utils).
- **Data Tier**: Relational MySQL database (`agritech_db`) with strict normalization, foreign key constraints, and automatic seed data.

---

## 2. Key Features

### Role-Based Access Control (RBAC)
- **Admin**: Full control to manage farmers, fields, crop varieties, crop batches, cultivation logs, analytics, and user accounts.
- **Farmer / Standard User**: Access assigned fields, monitor active batches, log cultivation activities (irrigation, fertilization, pest control, harvesting), update batch progress, and view analytics.

### Visual Crop Lifecycle Tracker
Interactive 5-stage visual lifecycle progress indicator:
$$\text{Planting} \longrightarrow \text{Growing} \longrightarrow \text{Cultivation} \longrightarrow \text{Ready for Harvest} \longrightarrow \text{Harvested}$$
Dynamic stage progression, pulse animations, and real-time status transitions.

### Agricultural Analytics & Intelligence
- **KPI Summary Cards**: Total Farmers, Total Fields, Active Batches, Completed Batches, Total Production, Average Yield.
- **Production by Crop**: Multi-crop harvest output breakdown.
- **Batch Status Distribution**: Doughnut chart of batches currently in each lifecycle stage.
- **Historical Yield Trends**: Chronological curve charting harvest productivity.
- **Resource Utilization**: Aggregate usage charts for irrigation water, fertilizers, and pest treatments.
- **Expected vs. Actual Benchmark**: Variance analysis comparing actual yield against botanical standards.
- **CSV Data Export**: One-click export of batch records and cultivation activity logs for spreadsheet analysis.

### Comprehensive CRUD Operations
- **Farmer Management**: Search, pagination, contact records, village zones, and associated land holdings modal.
- **Field Holdings**: Acreage, soil profile classification (Alluvial, Black, Clay, Loamy, Red, etc.), and farmer assignment.
- **Crop Catalog**: Botanical classification (Cereals, Pulses, Cash Crops, Vegetables), seasonal tagging (Kharif, Rabi, Zaid, Year-Round), and expected yield benchmarks.
- **Crop Batch Operations**: Automatic batch code generation (e.g., `BATCH-2026-WHT01`), seed quantity, dates, and yield tracking.
- **Cultivation Activity Tracking**: Detailed logging of irrigation, fertilization, pest control, and harvesting with quantity and unit calculators.
- **User Governance**: Admin-only account creation, role assignment, and credential updates.

---

## 3. Technology Stack

| Layer | Technology | Description |
| :--- | :--- | :--- |
| **Frontend** | HTML5 / CSS3 / JavaScript | Vanilla ES6+ without complex build tools |
| **UI Framework** | Bootstrap 5.3.3 | Responsive grid, modals, and dropdowns |
| **Icons & Fonts** | Font Awesome 6.5.1 / Plus Jakarta Sans | Modern typography and agricultural icons |
| **Data Visualization** | Chart.js 4.x | Interactive animated charts (Bar, Line, Doughnut, Pie) |
| **Backend Framework** | Python 3.11 / Flask 3.x | REST API architecture |
| **Database ORM** | SQLAlchemy 2.x / Flask-SQLAlchemy | Object Relational Mapper with connection pooling |
| **MySQL Driver** | PyMySQL / Cryptography | Pure-Python MySQL connector for cross-platform stability |
| **Authentication** | PyJWT / Werkzeug Security | Secure JWT Bearer tokens & Scrypt password hashing |
| **Database** | MySQL 5.7+ / 8.0+ / MariaDB 10.x | Relational database (`agritech_db`) |

---

## 4. Database Schema (`agritech_db`)

The relational database is normalized and enforces referential integrity using foreign keys:

```
+---------------+        +-------------------------+
|     users     |        |   cultivation_activities|
|---------------+        |-------------------------|
| id (PK)       |<---+   | activity_id (PK)        |
| name          |    |   | batch_id (FK)           |---+
| email (UQ)    |    |   | activity_type           |   |
| password      |    |   | activity_date           |   |
| role          |    |   | description             |   |
| created_at    |    |   | quantity_used           |   |
+---------------+    |   | unit                    |   |
                     |   | created_at              |   |
+---------------+    |   +-------------------------+   |
|    farmers    |    |                                 |
|---------------+    |   +-------------------------+   |
| farmer_id (PK)|    |   |       crop_batches      |   |
| user_id (FK)  |----+   |-------------------------|   |
| name          |        | batch_id (PK)           |<--+
| phone         |        | field_id (FK)           |--+
| address       |        | crop_id (FK)            |-+|
| village       |        | batch_code (UQ)         | ||
| created_at    |        | planting_date           | ||
+---------------+        | expected_harvest_date   | ||
      |                  | actual_harvest_date     | ||
      |                  | quantity                | ||
      v                  | yield                   | ||
+---------------+        | status                  | ||
|     fields    |        | created_at              | ||
|---------------+        +-------------------------+ ||
| field_id (PK) |<------------------------------------+|
| farmer_id (FK)|                                      |
| field_name    |        +-------------------------+   |
| location      |        |          crops          |   |
| area          |        |-------------------------|   |
| soil_type     |        | crop_id (PK)            |<--+
| created_at    |        | crop_name (UQ)          |
+---------------+        | crop_type               |
                         | season                  |
                         | expected_yield          |
                         | created_at              |
                         +-------------------------+
```

### Standalone SQL Files
- [`database/schema.sql`](file:///c:/Users/HP/DBSE%20Project/database/schema.sql): Complete DDL queries creating tables, foreign keys, and indexes.
- [`database/seed_data.sql`](file:///c:/Users/HP/DBSE%20Project/database/seed_data.sql): Sample dataset featuring 6 users, 5 farmers, 6 fields, 6 crops, 10 batches, and 22 cultivation activities.

---

## 5. Project Directory Structure

```
DBSE Project/
├── backend/
│   ├── app.py                     # Flask application entry point & blueprint registration
│   ├── config.py                  # Environment config loader (.env)
│   ├── database.py                # Database factory, SQLAlchemy setup & auto-seeder
│   ├── requirements.txt           # Python dependency specifications
│   ├── .env                       # Active environment configuration
│   ├── .env.example               # Template environment configuration
│   ├── models/                    # SQLAlchemy ORM Models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── farmer.py
│   │   ├── field.py
│   │   ├── crop.py
│   │   ├── batch.py
│   │   └── activity.py
│   ├── utils/                     # Utilities & Authentication
│   │   ├── __init__.py
│   │   ├── auth.py                # JWT token generator, decoder & role decorators
│   │   └── validators.py          # Input sanitation & standard JSON response formatters
│   ├── services/                  # Business Logic Layer
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── assistant_service.py
│   │   ├── farmer_service.py
│   │   ├── field_service.py
│   │   ├── crop_service.py
│   │   ├── batch_service.py
│   │   ├── activity_service.py
│   │   ├── analytics_service.py
│   │   └── export_service.py
│   ├── controllers/               # HTTP Request Processing
│   │   ├── __init__.py
│   │   ├── auth_controller.py
│   │   ├── assistant_controller.py
│   │   ├── farmer_controller.py
│   │   ├── field_controller.py
│   │   ├── crop_controller.py
│   │   ├── batch_controller.py
│   │   ├── activity_controller.py
│   │   ├── analytics_controller.py
│   │   └── user_controller.py
│   └── routes/                    # Flask Blueprint Endpoint Routing
│       ├── __init__.py
│       ├── auth_routes.py
│       ├── assistant_routes.py
│       ├── farmer_routes.py
│       ├── field_routes.py
│       ├── crop_routes.py
│       ├── batch_routes.py
│       ├── activity_routes.py
│       ├── analytics_routes.py
│       └── user_routes.py
├── frontend/
│   ├── index.html                 # Gateway & automatic router
│   ├── login.html                 # Login page with demo credentials quick-fill
│   ├── dashboard.html             # Main analytics dashboard with 4 Chart.js charts
│   ├── farmers.html               # Farmer directory, land holdings & CRUD
│   ├── fields.html                # Field inventory & soil management
│   ├── crops.html                 # Crop catalog & seasonal varieties
│   ├── batches.html               # Crop batch lifecycle & operations
│   ├── activities.html            # Cultivation activities log (Irrigation, Fertilizer, etc.)
│   ├── analytics.html             # Multi-dimensional analytics & CSV report exports
│   ├── users.html                 # User administration (Admin only)
│   ├── css/
│   │   └── style.css              # AgriTech design system & animations
│   └── js/
│       ├── api.js                 # Centralized Fetch wrapper & JWT interceptor
│       ├── auth.js                # Session management & role-based visibility
│       ├── common.js              # Reusable sidebar, topbar & lifecycle generator
│       ├── login.js               # Login controller
│       ├── dashboard.js           # Dashboard metrics & Chart.js renderer
│       ├── farmers.js             # Farmer UI controller
│       ├── fields.js              # Field UI controller
│       ├── crops.js               # Crop UI controller
│       ├── batches.js             # Batch UI & visual lifecycle controller
│       ├── activities.js          # Activity UI controller
│       ├── analytics.js           # Analytics portal controller
│       └── users.js               # User management controller
├── database/
│   ├── schema.sql                 # Complete MySQL DDL schema
│   └── seed_data.sql              # Realistic agricultural dataset
├── run_app.py                     # Unified single-command portal runner
├── start_portal.bat               # Windows click-to-run batch launcher
├── start_mysql.bat                # Windows standalone MySQL server runner
└── README.md                      # Comprehensive project documentation
```

---

## 6. How to Run the Application

### Option A: One-Command Runner (Recommended)

Simply execute `run_app.py`:

```bash
python run_app.py
```

Or on Windows, double-click:
```
start_portal.bat
```

The runner automatically:
1. Verifies that MySQL / MariaDB server is active on `127.0.0.1:3306` (or launches the standalone engine).
2. Verifies/creates the `agritech_db` database.
3. Creates all normalized relational tables.
4. Populates realistic seed data if tables are empty.
5. Starts the Flask web server at `http://127.0.0.1:5000`.

Open your browser and navigate to:
**[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 7. Default Login Credentials

Use these credentials to test role-based capabilities:

| Role | Email | Password | Access Privileges |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin@agritech.com` | `Admin@123` | Full access: CRUD on all modules, user governance, batch controls |
| **Farmer (Ramesh)** | `farmer.ramesh@agritech.com` | `Farmer@123` | View assigned fields/batches, log cultivation activities, view analytics |
| **Farmer (Suresh)** | `farmer.suresh@agritech.com` | `Farmer@123` | Assigned to Kisan Nagar / Valley Sunshine Field |

> *Tip: On the login page, you can also use the one-click **"Admin"** or **"Farmer"** demo buttons to instantly fill in credentials!*

---

## 8. Local AI Assistant

The authenticated assistant runs through a local Ollama instance, so prompts and farm records are not sent to a cloud AI provider. Install Ollama for Windows, then download the default model:

```powershell
ollama pull qwen2.5:3b
```

Keep Ollama running while using the portal. The default endpoint is `http://127.0.0.1:11434`; set `OLLAMA_URL` or `OLLAMA_MODEL` in `backend/.env` only when changing the local endpoint or model. Non-local model hosts are rejected to protect farm data. Farmers' assistant context contains only their own farm; admins can ask about organization records. If Ollama is unavailable, the assistant reports that it needs setup.

## 9. REST API Documentation

All endpoints (except login and registration) require a Bearer token in the `Authorization` header:
`Authorization: Bearer <jwt_token>`

Farmer-role requests are automatically restricted to the signed-in farmer's own profile, fields, batches, activities, analytics, and exports. Admin requests can access organization-wide records.

### Authentication (`/api/auth`)
| Method | Endpoint | Description | Access |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/auth/login` | Authenticate with email/password; returns JWT token | Public |
| `POST` | `/api/auth/register` | Register a new user account | Public |
| `GET` | `/api/auth/me` | Fetch authenticated user profile | Authenticated |
| `PUT` | `/api/auth/profile` | Update profile information | Authenticated |

### Farmers (`/api/farmers`)
| Method | Endpoint | Description | Access |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/farmers` | List farmers with search and pagination | Admin: all; farmer: own profile |
| `GET` | `/api/farmers/<id>` | Get farmer details with assigned fields | Admin: all; farmer: own profile |
| `POST` | `/api/farmers` | Create a new farmer record | Admin |
| `PUT` | `/api/farmers/<id>` | Update an existing farmer | Admin |
| `DELETE`| `/api/farmers/<id>` | Delete farmer (protected against active batches) | Admin |

### Fields (`/api/fields`)
| Method | Endpoint | Description | Access |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/fields` | List fields (filterable by farmer or search query) | Admin: all; farmer: own fields |
| `GET` | `/api/fields/<id>` | Get field details with batch history | Admin: all; farmer: own fields |
| `POST` | `/api/fields` | Create a new field plot | Admin |
| `PUT` | `/api/fields/<id>` | Update field details | Admin |
| `DELETE`| `/api/fields/<id>` | Delete field | Admin |

### Crops (`/api/crops`)
| Method | Endpoint | Description | Access |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/crops` | List crop varieties | Authenticated |
| `GET` | `/api/crops/<id>` | Get crop details | Authenticated |
| `POST` | `/api/crops` | Create a new crop entry | Admin |
| `PUT` | `/api/crops/<id>` | Update crop details | Admin |
| `DELETE`| `/api/crops/<id>` | Delete crop | Admin |

### Crop Batches (`/api/batches`)
| Method | Endpoint | Description | Access |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/batches` | List batches with multi-field filters | Admin: all; farmer: own batches |
| `GET` | `/api/batches/<id>` | Get batch details, lifecycle status, & activities | Admin: all; farmer: own batches |
| `GET` | `/api/batches/generate-code` | Auto-generate unique batch code | Authenticated |
| `POST` | `/api/batches` | Create a new crop batch | Admin |
| `PUT` | `/api/batches/<id>` | Update batch attributes | Authenticated |
| `PATCH`| `/api/batches/<id>/status` | Update lifecycle stage (`Planned` -> `Harvested`) | Authenticated |
| `DELETE`| `/api/batches/<id>` | Delete batch | Admin |

### Cultivation Activities (`/api/activities`)
| Method | Endpoint | Description | Access |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/activities` | List activities (filter by batch, type, date) | Admin: all; farmer: own batches |
| `GET` | `/api/activities/<id>` | Get activity details | Admin: all; farmer: own batches |
| `POST` | `/api/activities` | Log new activity (Irrigation, Fertilizer, etc.) | Authenticated |
| `PUT` | `/api/activities/<id>` | Update activity | Authenticated |
| `DELETE`| `/api/activities/<id>` | Delete activity | Authenticated |

### Analytics & Reports (`/api/analytics`)
| Method | Endpoint | Description | Access |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/analytics/dashboard` | KPI metrics and Chart.js datasets | Authenticated |
| `GET` | `/api/analytics/reports` | Multi-dimension analytics data | Authenticated |
| `GET` | `/api/analytics/export-batches` | Export batches as downloadable CSV | Authenticated |
| `GET` | `/api/analytics/export-activities`| Export activities as downloadable CSV | Authenticated |

### User Management (`/api/users`)
| Method | Endpoint | Description | Access |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/users` | List all system accounts | Admin |
| `POST` | `/api/users` | Create a new user account | Admin |
| `PUT` | `/api/users/<id>` | Update user role or password | Admin |
| `DELETE`| `/api/users/<id>` | Delete user account | Admin |

### Assistant (`/api/assistant`)
| Method | Endpoint | Description | Access |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/assistant/chat` | Ask the local Ollama assistant; farmer context is own-farm-only | Authenticated |

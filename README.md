# GenTable 🎓🕒

A robust backend system built with FastAPI for automating and managing university course scheduling. The system uses Google OR-Tools to solve the complex timetable constraint programming problem in the background using Celery and Redis. 

It features a dual-database architecture: PostgreSQL for relational data and MongoDB for storing the generated schedule results.

## 🚀 Features

*   **Algorithmic Scheduling**: Automated timetable generation using Google OR-Tools.
*   **Asynchronous Processing**: Heavy scheduling tasks are offloaded to background workers using Celery and Redis.
*   **Dual Database Architecture**: 
    *   **PostgreSQL**: Manages structured data via SQLAlchemy ORM.
    *   **MongoDB**: Stores the generated, unstructured schedule outputs.
*   **Authentication & Authorization**: Secure JWT-based login (Access & Refresh tokens) with Argon2 password hashing.
*   **Role-Based Access Control (RBAC)**: Distinct permissions for Super Admins, Admins, and Normal Users.
*   **Database Migrations**: Handled seamlessly with Alembic.

## 🛠️ Tech Stack

*   **Framework**: FastAPI
*   **Task Queue**: Celery
*   **Message Broker / Result Backend**: Redis
*   **Relational Database**: PostgreSQL (asyncpg)
*   **NoSQL Database**: MongoDB (motor/pymongo)
*   **ORM**: SQLAlchemy (Async)
*   **Migrations**: Alembic
*   **Security**: Passlib (Argon2), python-jose (JWT)
*   **Solver**: Google OR-Tools

## 📁 Project Structure
```text
├── alembic/                  # Database migration scripts
├── apps/                     # Application modules (routers, services, tasks)
│   ├── time_table_maker/     # Scheduling domain
│   │   ├── services/         # Core OR-Tools and business logic
│   │   ├── tasks.py          # Celery background tasks
│   │   └── time_table.py     # FastAPI router for scheduling
│   └── users/                # User management domain
│       ├── security.py       # JWT and password hashing (Argon2)
│       └── users.py          # FastAPI router for users/auth
├── docs/                     # Documentation files
├── models/                   # SQLAlchemy models
│   ├── time_table_models.py  # Course and Teacher models
│   └── users_models.py       # User models
├── schemas/                  # Pydantic models for validation
│   ├── time_table_schema.py  
│   └── users_schema.py       
├── celery_worker.py          # Celery app configuration
├── config.py                 # Application configuration/settings
├── database.py               # Database connections (PostgreSQL & MongoDB)
├── dependencies.py           # FastAPI dependencies (Auth, DB session)
├── docker-compose.yml        # Docker compose settings
├── Dockerfile                # Project's image settings
├── main.py                   # FastAPI application entry point
├── pyproject.toml            # Poetry dependencies and metadata
├── poetry.lock               # Poetry lock file
├── alembic.ini               # Alembic configuration
├── CRUL_TEST_EXAMPLES.md     # API curl testing examples
├── README.md                 # Project documentation
└── throttling.py             # Rate limiting settings
```

## ⚙️ Prerequisites

*   Python 3.12+
*   PostgreSQL
*   MongoDB
*   Redis

## 🚀 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/university-timetable-scheduler.git
   cd university-timetable-scheduler
   ```

2. **Create and activate a virtual environment:**
   ```
   python3.12 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   poetry install --no-root
   ```

4. **Database Setup:**
   Ensure PostgreSQL, MongoDB, and Redis are running. Update your connection strings in the code or `.env` file accordingly.

5. **Run Migrations (PostgreSQL):**
   ```bash
   alembic upgrade head
   ```

## 🏃‍♂️ Running the Application

You need to run three separate processes for the application to work fully:

1. **Start the FastAPI server(Terminal 1):**
   ```bash
   python main.py
   ```

2. **Start the Celery worker (Linux/macOS, Terminal 2):**
   ```bash
   celery -A celery_worker.celery_app worker --loglevel=info
   ```
   *(Note for Windows users: Use `celery -A celery_worker.celery_app worker --loglevel=info -P solo`)*

## 📡 Key API Endpoints

**Authentication & Users**
*   `POST /users/login` - Get JWT access and refresh tokens.
*   `POST /users/sing-up` - Create a new user.
*   `GET /users/` - List all users (Admin only).
*   `DELETE /users/{id}` - Delete a user (Admin only).

**Scheduling**
*   `POST /schedule/start` - Trigger the background timetable generation task.
*   `GET /schedule/status/{task_id}` - Check the status of the scheduling task.

*Check the auto-generated Swagger UI at `http://127.0.0.1:8000/docs` for the complete API documentation once the server is running.*

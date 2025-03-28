quiz_master/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── config.py
│   ├── extensions.py
│   ├── auth/
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── admin/
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── user/
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── jobs/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   ├── async_jobs.py
│   │   ├── scheduler.py
│   │   └── cache.py
│   ├── templates/
│   │   ├── admin/
│   │   └── emails/
│   └── static/
│       ├── exports/
│       └── frontend/
│           └── src/
├── instance/
│   └── quiz_master.db
├── .env
├── README.md
├── run.py
└── requirements.txt



Application Flow

The core application flow works as follows:

1. Entry Point: run.py - Creates the Flask application and runs the server

2. App Initialization: app/__init__.py - Sets up the Flask app, including:
    Database initialization
    Route registration
    Extension configuration (JWT, CORS, etc.)
    Basic error handling

3. Authentication: app/auth/routes.py - Handles login/registration

4. Main Routes:
    app/admin/routes.py - Admin dashboard functionality
    app/user/routes.py - Student/user functionality
    app/jobs/routes.py - Background job API endpoints

5. Background Processing:
    app/jobs/scheduler.py - Manages scheduled tasks
    app/jobs/async_jobs.py - Handles asynchronous jobs like exports
    app/jobs/cache.py - Implements caching functionality

6. Frontend: app/static/frontend/ - Contains the Vue.js frontend application
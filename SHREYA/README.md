# Quiz Master Application

A comprehensive quiz management system for educational institutions.

## Features

### Core Features
- User authentication (admin and regular users)
- Subject, chapter, and quiz management
- Quiz assignment to users
- Quiz taking and scoring
- Performance tracking and history

### Advanced Features
- **Scheduled Daily Reminders**: Automatically notifies users about pending quizzes
- **Monthly Activity Reports**: Generates and emails detailed monthly performance reports
- **CSV Exports**: 
  - User-triggered export of quiz history
  - Admin-triggered export of user performance data
- **Performance Optimization**: Caching for improved application responsiveness

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Node.js and npm (for the Vue.js frontend)

### Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd Quiz-Master
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables (create a .env file):
   ```
   # Flask Application Environment Variables
   SECRET_KEY=your-secret-key
   JWT_SECRET_KEY=your-jwt-secret-key

   # Database Configuration
   DATABASE_URL=sqlite:///quiz_master.db

   # JWT Configuration
   JWT_ACCESS_TOKEN_EXPIRES=86400

   # Development Settings
   FLASK_APP=run.py
   FLASK_DEBUG=1  # For development only, use 0 in production

   # Email settings
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   FROM_EMAIL=Quiz Master <your-email@gmail.com>
   EMAIL_DEBUG_MODE=False  # Set to True in development
   
   # Caching Configuration
   CACHE_TYPE=simple
   CACHE_TIMEOUT=300
   ENABLE_CACHING=True
   ```

5. Initialize the database:
   The database will be automatically created when you first run the application. It will create:
   - Database tables
   - Admin user (username: admin@mail.com, password: admin)
   - Test student accounts
   - Sample subjects, chapters, and quizzes

6. Set up the frontend:
   ```
   cd app/static/frontend
   npm install
   npm run serve  # For development
   # OR
   npm run build  # For production build
   ```

7. Run the application:
   ```
   python run.py
   ```
   
   The application will be available at:
   - API Backend: http://localhost:5000
   - Frontend (if running npm serve): http://localhost:8080

## Default Login Credentials

### Admin User
- Username: admin@mail.com
- Password: admin

### Student User
- Username: student1@mail.com
- Password: student

## Email Configuration

To enable email notifications for reminders and reports, configure these environment variables:

```
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=Quiz Master <your-email@gmail.com>
EMAIL_DEBUG_MODE=False  # Set to True in development to log emails instead of sending
```

For Gmail, you'll need to use an App Password if 2FA is enabled.

### Development Email Setup

For development, you can:

1. Use a dummy SMTP server like [MailHog](https://github.com/mailhog/MailHog):
   ```
   SMTP_SERVER=localhost
   SMTP_PORT=1025
   ```

2. Or set `EMAIL_DEBUG_MODE=True` to just log emails without sending them

## Caching Configuration

For improved performance, the application uses caching. By default, it uses an in-memory cache, but for production, configure Redis:

```
CACHE_TYPE=redis
CACHE_REDIS_URL=redis://localhost:6379/0
CACHE_TIMEOUT=300
```

## Application Structure and Flow

The application follows this structure:

1. **Backend (Flask)**:
   - `app/__init__.py`: Application initialization and configuration
   - `app/models.py`: Database models
   - `app/auth/routes.py`: Authentication endpoints
   - `app/admin/routes.py`: Admin functionalities
   - `app/user/routes.py`: Student functionalities
   - `app/jobs/`: Background processing (reports, emails, exports)

2. **Frontend (Vue.js)**:
   - Located in `app/static/frontend/`
   - Single page application with separate admin and student interfaces
   - Communicates with the backend via REST API

## Troubleshooting

### Database Issues
If you encounter database issues, you can reset the database:
1. Stop the application
2. Delete the file `instance/quiz_master.db`
3. Restart the application (a new database will be created)

### Email Sending Issues
If emails fail to send:
1. Check your SMTP settings in the `.env` file
2. For Gmail, ensure you're using an app password
3. Set `EMAIL_DEBUG_MODE=True` to see what's happening without sending emails

## License

[MIT License](LICENSE) 
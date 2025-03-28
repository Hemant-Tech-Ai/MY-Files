from app import create_app, db
from app.models.user import User
from app.models.quiz import Quiz
from app.models.quiz_attempt import QuizAttempt
from app.models.question import Question
from app.models.chapter import Chapter
from app.models.subject import Subject

app = create_app()

with app.app_context():
    # Create all tables
    db.create_all()
    
    # Create admin user
    admin = User(
        email='admin@example.com',
        full_name='Admin User',
        role='admin'
    )
    admin.set_password('admin123')
    db.session.add(admin)
    db.session.commit()

print("Database initialized!") 
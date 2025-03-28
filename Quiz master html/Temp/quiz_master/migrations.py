import os
import sys
import shutil
from pathlib import Path

# Add the project root directory to Python path
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from app import create_app, db
from app.models import User, Subject, Chapter, Quiz, Question, QuizAttempt, UserAnswer
from werkzeug.security import generate_password_hash
from datetime import datetime

def init_db():
    app = create_app()
    
    with app.app_context():
        # Remove existing database file
        db_path = Path(app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', ''))
        if db_path.exists():
            try:
                db_path.unlink()
                print(f"Removed existing database: {db_path}")
            except Exception as e:
                print(f"Error removing database: {e}")
        
        print("Creating database tables...")
        db.create_all()
        
        print("Adding sample data...")
        try:
            # Create admin user
            admin = User(
                username='admin',
                email='admin@example.com',
                password=generate_password_hash('admin123'),
                is_admin=True
            )
            db.session.add(admin)
            
            # Create test user
            user = User(
                username='test_user',
                email='test@example.com',
                password=generate_password_hash('test123'),
                is_admin=False
            )
            db.session.add(user)
            
            # Create sample subject
            subject = Subject(
                name='Python Programming',
                description='Learn Python programming fundamentals'
            )
            db.session.add(subject)
            
            # Create sample chapter
            chapter = Chapter(
                name='Basic Syntax',
                description='Python basic syntax and data types',
                subject=subject
            )
            db.session.add(chapter)
            
            # Create sample quiz
            quiz = Quiz(
                title='Python Basics Quiz',
                description='Test your knowledge of Python basics',
                duration_minutes=30,
                chapter=chapter
            )
            db.session.add(quiz)
            
            # Create sample questions
            questions = [
                Question(
                    quiz=quiz,
                    question_text='What is the output of print("Hello " + "World")?',
                    option_a='Hello World',
                    option_b='HelloWorld',
                    option_c='Error',
                    option_d='None',
                    correct_option='A'
                ),
                Question(
                    quiz=quiz,
                    question_text='Which of these is NOT a Python data type?',
                    option_a='int',
                    option_b='float',
                    option_c='char',
                    option_d='str',
                    correct_option='C'
                )
            ]
            db.session.add_all(questions)
            
            # Create sample quiz attempt
            attempt = QuizAttempt(
                user=user,
                quiz=quiz,
                start_time=datetime.utcnow(),
                end_time=datetime.utcnow(),
                score=1
            )
            db.session.add(attempt)
            
            # Add user answers
            for question in questions:
                user_answer = UserAnswer(
                    quiz_attempt=attempt,
                    question=question,
                    selected_option='A',
                    is_correct=(question.correct_option == 'A')
                )
                db.session.add(user_answer)
            
            db.session.commit()
            print("Database initialized successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error initializing database: {e}")
            raise

if __name__ == '__main__':
    # Clean up any existing pyc files
    for root, dirs, files in os.walk(project_root):
        for file in files:
            if file.endswith('.pyc'):
                os.remove(os.path.join(root, file))
        if '__pycache__' in dirs:
            shutil.rmtree(os.path.join(root, '__pycache__'))
    
    print("Initializing database...")
    init_db() 
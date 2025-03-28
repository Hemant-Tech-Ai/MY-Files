from flask import Flask, send_from_directory, jsonify
from dotenv import load_dotenv
from .config import Config
from .extensions import db, migrate, jwt, cors
from werkzeug.security import generate_password_hash
from datetime import date, datetime, timedelta
import random
import os

from .models import User, Subject, Chapter, Quiz, Question, Score

def create_app(config_class=Config):
    # Load environment variables from .env file
    load_dotenv()
    
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions with the app
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app)
    
    # Initialize new extensions
    from app.jobs.cache import init_cache
    from app.jobs.scheduler import init_scheduler
    
    # Initialize cache
    init_cache(app)
    
    # Initialize scheduler
    init_scheduler(app)
    
    # Create exports directory
    exports_dir = os.path.join(app.static_folder, 'exports')
    os.makedirs(exports_dir, exist_ok=True)
    
    # Setup JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        print(f"Expired token: {jwt_payload}")
        return jsonify({
            'msg': 'The token has expired',
            'error': 'token_expired'
        }), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        print(f"Invalid token error: {error}")
        return jsonify({
            'msg': 'Signature verification failed',
            'error': 'invalid_token'
        }), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        print(f"Missing token error: {error}")
        return jsonify({
            'msg': 'Request does not contain an access token',
            'error': 'authorization_required'
        }), 401
    
    @jwt.token_verification_failed_loader
    def verification_failed_callback():
        print("Token verification failed")
        return jsonify({
            'msg': 'Token verification failed',
            'error': 'invalid_token'
        }), 401
    
    # Register blueprints
    from app.auth.routes import auth_bp
    from app.admin.routes import admin_bp
    from app.user.routes import user_bp
    from app.jobs.routes import jobs_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(jobs_bp, url_prefix='/api/jobs')
    
    # Add route to serve Vue.js SPA
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def catch_all(path):
        if path != "" and not path.startswith('auth/') and not path.startswith('admin/') and not path.startswith('user/'):
            return send_from_directory('static/frontend/dist', 'index.html')
        return app.send_static_file('index.html')
    
    # Initialize database and seed data
    with app.app_context():
        db.create_all()
        seed_database_if_empty()
        
        # Check if admin user exists, if not create one
        admin = User.query.filter_by(is_admin=True).first()
        if not admin:
            admin = User(
                username="admin@mail.com",
                full_name="Admin User",
                qualification="System Administrator",
                dob=date(1990, 1, 1),
                is_admin=True
            )
            admin.set_password("admin")
            db.session.add(admin)
            db.session.commit()
            print("Default admin user created")
    
    return app

def seed_database_if_empty():
    """Seed the database with initial data if it's empty"""
    # Check if database is empty
    if User.query.count() > 0:
        print("Database already contains data, skipping seed.")
        return
    
    print("Seeding database with initial data...")
    
    # Create admin user
    admin = User(
        username="admin@mail.com",
        full_name="Admin User",
        qualification="Admin",
        is_admin=True
    )
    admin.set_password("admin")
    db.session.add(admin)
    
    # Create test students
    student1 = User(
        username="student1@mail.com",
        full_name="Student One",
        qualification="Student",
        is_admin=False
    )
    student1.set_password("student")
    db.session.add(student1)
    
    student2 = User(
        username="student2@mail.com",
        full_name="Student Two",
        qualification="Student",
        is_admin=False
    )
    student2.set_password("student")
    db.session.add(student2)
    
    # Create subjects
    math = Subject(name="Mathematics", description="Mathematics subject for all students")
    science = Subject(name="Science", description="Science subject focusing on physics and chemistry")
    db.session.add(math)
    db.session.add(science)
    db.session.flush()  # Flush to get IDs
    
    # Create chapters
    algebra = Chapter(name="Algebra", subject_id=math.id, description="Basic algebraic concepts")
    geometry = Chapter(name="Geometry", subject_id=math.id, description="Study of shapes and spaces")
    physics = Chapter(name="Physics", subject_id=science.id, description="Basic physics principles")
    chemistry = Chapter(name="Chemistry", subject_id=science.id, description="Introduction to chemistry")
    db.session.add_all([algebra, geometry, physics, chemistry])
    db.session.flush()
    
    # Create quizzes
    math_quiz = Quiz(
        chapter_id=algebra.id,
        date_of_quiz=datetime.now().date(),
        time_duration=30,
        remarks="Basic algebra quiz"
    )
    science_quiz = Quiz(
        chapter_id=physics.id,
        date_of_quiz=datetime.now().date(),
        time_duration=45,
        remarks="Physics fundamentals quiz"
    )
    db.session.add_all([math_quiz, science_quiz])
    db.session.flush()
    
    # Create questions
    math_q1 = Question(
        quiz_id=math_quiz.id,
        question_statement="What is the value of x in 2x + 5 = 15?",
        option1="5",
        option2="7.5",
        option3="10",
        option4="3",
        correct_option=1
    )
    
    math_q2 = Question(
        quiz_id=math_quiz.id,
        question_statement="Simplify: 3(x - 2) + 4",
        option1="3x - 6 + 4",
        option2="3x - 2",
        option3="3x - 2 + 4",
        option4="3x + 2",
        correct_option=3
    )
    
    science_q1 = Question(
        quiz_id=science_quiz.id,
        question_statement="What is the SI unit of force?",
        option1="Joule",
        option2="Newton",
        option3="Watt",
        option4="Pascal",
        correct_option=2
    )
    
    science_q2 = Question(
        quiz_id=science_quiz.id,
        question_statement="Which law states that energy can neither be created nor destroyed?",
        option1="Newton's First Law",
        option2="Law of Conservation of Mass",
        option3="Law of Conservation of Energy",
        option4="Ohm's Law",
        correct_option=3
    )
    
    db.session.add_all([math_q1, math_q2, science_q1, science_q2])
    db.session.commit()
    
    print("Database has been seeded with test data.")

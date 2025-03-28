from app.tasks import celery
from app.models.user import User
from app.models.quiz import Quiz
from app.models.quiz_attempt import QuizAttempt
from app import db, mail
from flask_mail import Message
import csv
from io import StringIO
from datetime import datetime, timedelta

@celery.task
def export_user_quiz_data(user_id):
    """Export quiz attempts data for a specific user"""
    user = User.query.get(user_id)
    attempts = QuizAttempt.query.filter_by(user_id=user_id).all()
    
    # Create CSV in memory
    output = StringIO()
    writer = csv.writer(output)
    
    # Write headers
    writer.writerow([
        'Date', 'Subject', 'Chapter', 'Score', 'Total Questions',
        'Percentage', 'Time Taken (minutes)'
    ])
    
    # Write data
    for attempt in attempts:
        writer.writerow([
            attempt.started_at.strftime('%Y-%m-%d %H:%M'),
            attempt.quiz.chapter.subject.name,
            attempt.quiz.chapter.name,
            attempt.score,
            attempt.total_questions,
            f"{(attempt.score/attempt.total_questions * 100):.1f}%",
            ((attempt.completed_at - attempt.started_at).total_seconds() / 60)
        ])
    
    # Send email with CSV
    msg = Message(
        'Quiz Master - Your Quiz Data Export',
        recipients=[user.email]
    )
    
    msg.html = """
    <h2>Quiz Data Export</h2>
    <p>Please find attached your quiz attempt data.</p>
    """
    
    msg.attach(
        f"quiz_data_{datetime.now().strftime('%Y%m%d')}.csv",
        "text/csv",
        output.getvalue()
    )
    
    mail.send(msg)

@celery.task
def export_admin_quiz_data():
    """Export all quiz data for admin"""
    attempts = QuizAttempt.query.all()
    
    # Create CSV in memory
    output = StringIO()
    writer = csv.writer(output)
    
    # Write headers
    writer.writerow([
        'User', 'Email', 'Date', 'Subject', 'Chapter',
        'Score', 'Total Questions', 'Percentage', 'Time Taken (minutes)'
    ])
    
    # Write data
    for attempt in attempts:
        writer.writerow([
            attempt.user.full_name,
            attempt.user.email,
            attempt.started_at.strftime('%Y-%m-%d %H:%M'),
            attempt.quiz.chapter.subject.name,
            attempt.quiz.chapter.name,
            attempt.score,
            attempt.total_questions,
            f"{(attempt.score/attempt.total_questions * 100):.1f}%",
            ((attempt.completed_at - attempt.started_at).total_seconds() / 60)
        ])
    
    # Send email to admin
    admin = User.query.filter_by(role='admin').first()
    
    msg = Message(
        'Quiz Master - Complete Quiz Data Export',
        recipients=[admin.email]
    )
    
    msg.html = """
    <h2>Complete Quiz Data Export</h2>
    <p>Please find attached the complete quiz attempt data for all users.</p>
    """
    
    msg.attach(
        f"all_quiz_data_{datetime.now().strftime('%Y%m%d')}.csv",
        "text/csv",
        output.getvalue()
    )
    
    mail.send(msg) 
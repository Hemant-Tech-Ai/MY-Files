from app.tasks import celery
from app.models.user import User
from app.models.quiz import Quiz
from app.models.quiz_attempt import QuizAttempt
from app import db, mail
from flask_mail import Message
from datetime import datetime, timedelta
import requests

@celery.task
def send_daily_reminders():
    """Send daily reminders to users who haven't taken any quizzes recently"""
    
    # Get users who haven't attempted a quiz in the last 7 days
    one_week_ago = datetime.now() - timedelta(days=7)
    
    users = User.query.filter(
        ~User.quiz_attempts.any(QuizAttempt.started_at > one_week_ago)
    ).all()
    
    # Get upcoming quizzes
    upcoming_quizzes = Quiz.query.filter(
        Quiz.date_of_quiz > datetime.now()
    ).limit(3).all()
    
    for user in users:
        # Send email reminder
        send_email_reminder.delay(
            user.id,
            [quiz.id for quiz in upcoming_quizzes]
        )
        
        # Send Google Chat reminder if webhook URL is configured
        if user.gchat_webhook:
            send_gchat_reminder.delay(
                user.id,
                user.gchat_webhook,
                [quiz.id for quiz in upcoming_quizzes]
            )

@celery.task
def send_email_reminder(user_id, quiz_ids):
    """Send reminder email to a specific user"""
    user = User.query.get(user_id)
    quizzes = Quiz.query.filter(Quiz.id.in_(quiz_ids)).all()
    
    msg = Message(
        'Quiz Master - New Quizzes Available!',
        recipients=[user.email]
    )
    
    msg.html = f"""
    <h2>Hello {user.full_name}!</h2>
    <p>We noticed you haven't taken any quizzes recently. Here are some upcoming quizzes you might be interested in:</p>
    <ul>
    {''.join(f'<li>{quiz.chapter.subject.name} - {quiz.chapter.name} (Date: {quiz.date_of_quiz.strftime("%Y-%m-%d")})</li>' for quiz in quizzes)}
    </ul>
    <p>Visit <a href="http://localhost:5000">Quiz Master</a> to attempt these quizzes!</p>
    """
    
    mail.send(msg)

@celery.task
def send_gchat_reminder(user_id, webhook_url, quiz_ids):
    """Send reminder via Google Chat webhook"""
    user = User.query.get(user_id)
    quizzes = Quiz.query.filter(Quiz.id.in_(quiz_ids)).all()
    
    message = {
        "text": f"Hello {user.full_name}!\n\n"
                "We noticed you haven't taken any quizzes recently. "
                "Here are some upcoming quizzes:\n\n" +
                "\n".join(f"• {quiz.chapter.subject.name} - {quiz.chapter.name}" for quiz in quizzes)
    }
    
    requests.post(webhook_url, json=message) 
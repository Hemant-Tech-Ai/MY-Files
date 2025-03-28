"""
Scheduler module for Quiz Master application.
Handles scheduled jobs for daily reminders and monthly reports.
"""
from flask_apscheduler import APScheduler
from flask import current_app, render_template
from app.models import User, QuizAssignment, Quiz, Score, Chapter, Subject
from datetime import datetime, time, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import csv
import io
import os
import logging
import socket

# Initialize scheduler
scheduler = APScheduler()
_scheduler_initialized = False

def init_scheduler(app):
    """Initialize the scheduler with the Flask app"""
    global _scheduler_initialized
    
    # Only initialize once
    if _scheduler_initialized:
        app.logger.info("Scheduler already initialized, skipping")
        return
    
    # Configure the scheduler
    scheduler.api_enabled = True
    scheduler.init_app(app)
    
    # Store the Flask app instance for later use in jobs
    scheduler.app = app
    
    # Register jobs
    with app.app_context():
        # Remove any existing jobs to avoid duplicates
        for job in scheduler.get_jobs():
            job.remove()
            
        # Schedule daily reminder job (at 18:45 UTC)
        scheduler.add_job(
            id='send_daily_reminders',
            func=send_daily_reminders,
            trigger='cron',
            hour=19,
            minute=5,
            second=0,
            timezone='UTC',
            replace_existing=True
        )
        
        # Schedule monthly reports job (15th of each month at 18:45 UTC)
        scheduler.add_job(
            id='send_monthly_reports',
            func=send_monthly_reports,
            trigger='cron',
            day=15,
            hour=19,
            minute=5,
            second=0,
            timezone='UTC',
            replace_existing=True
        )
    
    # Start the scheduler after all jobs are registered
    if not scheduler.running:
        scheduler.start()
        
    _scheduler_initialized = True
    app.logger.info("Scheduled jobs initialized")

def send_daily_reminders():
    """Send daily reminders to users for their upcoming quizzes"""
    # Use the stored app for context
    with scheduler.app.app_context():
        app = scheduler.app
        
        try:
            # Get current date
            today = datetime.now().date()
            tomorrow = today + timedelta(days=1)
            
            # Find all users
            users = User.query.filter_by(is_admin=False).all()
            
            # Log the number of users found
            app.logger.info(f"Found {len(users)} users for daily reminders")
            
            # Track users who received emails
            users_with_reminders = []
            
            for user in users:
                # Find quizzes assigned to this user with upcoming deadlines
                upcoming_quizzes = QuizAssignment.query.join(Quiz).filter(
                    QuizAssignment.user_id == user.id,
                    Quiz.date_of_quiz >= today,
                    Quiz.date_of_quiz <= tomorrow
                ).all()
                
                if upcoming_quizzes:
                    # Send reminder for upcoming quizzes
                    send_reminder_notification(user, upcoming_quizzes)
                    users_with_reminders.append(user.username)
                else:
                    app.logger.info(f"No upcoming quizzes found for user {user.username}")
            
            # Log summary
            if users_with_reminders:
                app.logger.info(f"Daily reminders sent to: {', '.join(users_with_reminders)}")
            else:
                app.logger.info("No users had upcoming quizzes for reminders")
                
        except Exception as e:
            app.logger.error(f"Failed to send daily reminders: {str(e)}")

def send_reminder_notification(user, quizzes):
    """Send reminder notification to a user about upcoming quizzes"""
    # Use the stored app for context
    with scheduler.app.app_context():
        app = scheduler.app
        
        try:
            # Format quiz information
            quiz_list = []
            for assignment in quizzes:
                quiz = Quiz.query.get(assignment.quiz_id)
                chapter = Chapter.query.get(quiz.chapter_id)
                subject = Subject.query.get(chapter.subject_id)
                
                quiz_list.append({
                    'subject': subject.name,
                    'chapter': chapter.name,
                    'date': quiz.date_of_quiz.strftime('%d-%b-%Y')
                })
            
            # Get today's date in the same format for template comparison
            today_str = datetime.now().date().strftime('%d-%b-%Y')
            
            # Create email subject and body
            subject = "Upcoming Quiz Reminder"
            body = render_template('emails/reminder.html', 
                                  user=user, 
                                  quizzes=quiz_list, 
                                  today_str=today_str)
            
            # Send email
            app.logger.info(f"Sending reminder email to {user.username}")
            send_email(user.username, subject, body, is_html=True)
            app.logger.info(f"Reminder email sent successfully to {user.username}")
        except Exception as e:
            app.logger.error(f"Failed to send reminder to {user.username}: {str(e)}")

def send_monthly_reports():
    """Generate and send monthly reports for all users"""
    # Use the stored app for context
    with scheduler.app.app_context():
        app = scheduler.app
        
        try:
            # Get all regular users
            users = User.query.filter_by(is_admin=False).all()
            
            # Log the number of users found
            app.logger.info(f"Found {len(users)} users for monthly reports")
            
            # Calculate date ranges
            today = datetime.now()
            
            # Previous month range
            first_day_previous_month = datetime(today.year, today.month, 1) - timedelta(days=1)
            first_day_previous_month = datetime(first_day_previous_month.year, first_day_previous_month.month, 1)
            last_day_previous_month = datetime(today.year, today.month, 1) - timedelta(days=1)
            
            # Current month range (up to today)
            first_day_current_month = datetime(today.year, today.month, 1)
            current_month_end = datetime.now()
            
            # Format month names
            previous_month_name = first_day_previous_month.strftime('%B %Y')
            current_month_name = today.strftime('%B %Y')
            
            # Track users who received reports
            users_with_reports = []
            
            # Generate and send report for each user
            for user in users:
                try:
                    # Previous month report
                    app.logger.info(f"Generating previous month report for {user.username}")
                    prev_month_success = generate_monthly_report(
                        user=user,
                        start_date=first_day_previous_month,
                        end_date=last_day_previous_month,
                        month_name=f"Previous Month - {previous_month_name}"
                    )
                    
                    # Current month report (up to today)
                    app.logger.info(f"Generating current month report for {user.username}")
                    curr_month_success = generate_monthly_report(
                        user=user,
                        start_date=first_day_current_month,
                        end_date=current_month_end,
                        month_name=f"Current Month - {current_month_name} (Up to {today.strftime('%d-%b-%Y')})"
                    )
                    
                    if prev_month_success or curr_month_success:
                        users_with_reports.append(user.username)
                        
                except Exception as e:
                    app.logger.error(f"Error generating reports for {user.username}: {str(e)}")
            
            # Log summary
            if users_with_reports:
                app.logger.info(f"Monthly reports sent to: {', '.join(users_with_reports)}")
            else:
                app.logger.info("No users had activity for monthly reports")
                
        except Exception as e:
            app.logger.error(f"Failed to send monthly reports: {str(e)}")

def generate_monthly_report(user, start_date, end_date, month_name):
    """Generate and send monthly report for a specific user"""
    with scheduler.app.app_context():
        app = scheduler.app
        
        try:
            app.logger.info(f"Generating report for {user.username} from {start_date} to {end_date}")
            
            # Get user's quiz scores for the month
            scores = Score.query.filter(
                Score.user_id == user.id,
                Score.time_stamp_of_attempt >= start_date,
                Score.time_stamp_of_attempt <= end_date
            ).all()
            
            app.logger.info(f"Found {len(scores)} scores for the period")
            
            # If no activity, skip
            if not scores:
                app.logger.info(f"No activity for user {user.username} in {month_name}")
                return False
            
            # Calculate statistics
            total_quizzes = len(scores)
            total_score = sum(score.total_scored for score in scores)
            total_questions = sum(score.total_questions for score in scores)
            average_score = round((total_score / total_questions * 100) if total_questions > 0 else 0)
            
            app.logger.info(f"Statistics: {total_quizzes} quizzes, {total_score}/{total_questions} total score ({average_score}%)")
            
            # Prepare quiz details
            quiz_details = []
            for score in scores:
                quiz = Quiz.query.get(score.quiz_id)
                chapter = Chapter.query.get(quiz.chapter_id)
                subject = Subject.query.get(chapter.subject_id)
                
                # Calculate percentage
                percentage = round((score.total_scored / score.total_questions) * 100) if score.total_questions > 0 else 0
                
                quiz_detail = {
                    'subject': subject.name,
                    'chapter': chapter.name,
                    'quiz': quiz.remarks or f"{subject.name} - {chapter.name}",
                    'date': score.time_stamp_of_attempt.strftime('%d-%b-%Y'),
                    'score': f"{score.total_scored}/{score.total_questions}",
                    'percentage': percentage
                }
                quiz_details.append(quiz_detail)
            
            # Sort by date (newest first)
            quiz_details.sort(key=lambda x: datetime.strptime(x['date'], '%d-%b-%Y'), reverse=True)
            
            # Generate HTML report
            html_content = render_template(
                'emails/monthly_report.html',
                user=user,
                month=month_name,
                total_quizzes=total_quizzes,
                average_score=average_score,
                quiz_details=quiz_details
            )
            
            # Send email with report
            subject = f"Quiz Master - Monthly Report for {month_name}"
            app.logger.info(f"Sending monthly report email to {user.username}")
            send_email(user.username, subject, html_content, is_html=True)
            app.logger.info(f"Monthly report sent successfully to {user.username}")
            
            return True
            
        except Exception as e:
            app.logger.error(f"Failed to generate report for {user.username}: {str(e)}")
            return False

def send_email(to, subject, body, is_html=False):
    """Send an email using SMTP"""
    # Get email configuration from environment variables
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_username = os.getenv('SMTP_USERNAME', '')
    smtp_password = os.getenv('SMTP_PASSWORD', '')
    from_email = os.getenv('quizmaster@example.com')
    
    # Check if email credentials are configured
    if not smtp_username or not smtp_password:
        logging.warning(f"Email credentials not configured, skipping email to {to}")
        return
    
    # Create message
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to
    msg['Subject'] = subject
    
    # Attach body
    if is_html:
        msg.attach(MIMEText(body, 'html'))
    else:
        msg.attach(MIMEText(body, 'plain'))
    
    # Send email
    try:
        # Create server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        
        # Login
        server.login(smtp_username, smtp_password)
        
        # Send message
        server.send_message(msg)
        logging.info(f"Email sent successfully to {to}")
        
        # Close connection
        server.quit()
        
    except (smtplib.SMTPConnectError, socket.gaierror) as e:
        logging.error(f"Failed to connect to SMTP server: {str(e)}")
        logging.info("This is likely due to an invalid SMTP server address or network connectivity issues.")
        return
    except Exception as e:
        logging.error(f"Failed to send email: {str(e)}")
        raise 
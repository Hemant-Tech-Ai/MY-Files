"""
Async Jobs module for Quiz Master application.
Handles user-triggered asynchronous jobs like CSV exports.
"""
from flask import current_app, url_for
from app.models import User, Quiz, Score, Chapter, Subject
import csv
import io
import os
from datetime import datetime
import threading
import uuid
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import socket

# Dictionary to store job status
jobs = {}

def start_export_job(job_type, user_id=None, admin=False):
    """Start an export job and return the job ID"""
    job_id = str(uuid.uuid4())
    
    # Create job data
    job_data = {
        'id': job_id,
        'type': job_type,
        'status': 'running',
        'progress': 0,
        'user_id': user_id,
        'admin': admin,
        'created': datetime.now(),
        'completed': None,
        'file_path': None,
        'message': 'Job started'
    }
    
    # Store job data
    jobs[job_id] = job_data
    
    # Get the current app instance
    from flask import current_app
    app = current_app._get_current_object()
    
    # Start export thread
    if job_type == 'user_quiz_export':
        thread = threading.Thread(target=export_user_quizzes, args=(job_id, user_id, app))
    elif job_type == 'admin_user_export':
        thread = threading.Thread(target=export_all_users, args=(job_id, app))
    else:
        job_data['status'] = 'failed'
        job_data['message'] = f"Unknown job type: {job_type}"
        return job_id
    
    thread.daemon = True
    thread.start()
    
    return job_id

def export_user_quizzes(job_id, user_id, app):
    """Export all quizzes taken by a user to CSV"""
    job_data = jobs[job_id]
    
    # Use the app context within the thread
    with app.app_context():
        try:
            # Get user
            user = User.query.get(user_id)
            if not user:
                job_data['status'] = 'failed'
                job_data['message'] = f"User not found: {user_id}"
                return
            
            # Get scores
            scores = Score.query.filter_by(user_id=user_id).all()
            if not scores:
                job_data['status'] = 'completed'
                job_data['message'] = "No quiz scores found for user"
                job_data['completed'] = datetime.now()
                return
            
            # Create CSV data
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                'Quiz ID', 'Subject', 'Chapter', 'Date of Quiz', 
                'Score', 'Total Questions', 'Percentage', 'Time of Attempt'
            ])
            
            # Write data rows
            total_rows = len(scores)
            for i, score in enumerate(scores):
                quiz = Quiz.query.get(score.quiz_id)
                if quiz:
                    chapter = Chapter.query.get(quiz.chapter_id)
                    subject = Subject.query.get(chapter.subject_id) if chapter else None
                    
                    writer.writerow([
                        quiz.id,
                        subject.name if subject else 'N/A',
                        chapter.name if chapter else 'N/A',
                        quiz.date_of_quiz.strftime('%Y-%m-%d') if quiz.date_of_quiz else 'N/A',
                        score.total_scored,
                        score.total_questions,
                        f"{round(score.total_scored / score.total_questions * 100, 2)}%" if score.total_questions > 0 else '0%',
                        score.time_stamp_of_attempt.strftime('%Y-%m-%d %H:%M:%S')
                    ])
                
                # Update progress
                job_data['progress'] = int((i + 1) / total_rows * 100)
            
            # Save CSV file
            filename = f"user_{user_id}_quizzes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            export_dir = os.path.join(app.static_folder, 'exports')
            os.makedirs(export_dir, exist_ok=True)
            
            file_path = os.path.join(export_dir, filename)
            with open(file_path, 'w', newline='') as f:
                f.write(output.getvalue())
            
            # Update job data
            job_data['status'] = 'completed'
            job_data['completed'] = datetime.now()
            job_data['file_path'] = file_path
            job_data['message'] = f"Export completed: {filename}"
            
            # Send email notification
            try:
                send_export_notification(user.username, filename, file_path, 'quiz', app)
                app.logger.info(f"Export notification sent to {user.username}")
            except Exception as e:
                app.logger.error(f"Failed to send export notification: {str(e)}")
                job_data['message'] += f" (Failed to send notification: {str(e)})"
        
        except Exception as e:
            app.logger.error(f"Export failed: {str(e)}")
            job_data['status'] = 'failed'
            job_data['message'] = f"Export failed: {str(e)}"
            job_data['completed'] = datetime.now()

def export_all_users(job_id, app):
    """Export all users data for admin to CSV"""
    job_data = jobs[job_id]
    
    # Use the app context within the thread
    with app.app_context():
        try:
            # Get all non-admin users
            users = User.query.filter_by(is_admin=False).all()
            if not users:
                job_data['status'] = 'completed'
                job_data['message'] = "No users found"
                job_data['completed'] = datetime.now()
                return
            
            # Create CSV data
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                'User ID', 'Username', 'Full Name', 'Qualification',
                'Quizzes Taken', 'Average Score (%)', 'Last Activity'
            ])
            
            # Write data rows
            total_rows = len(users)
            for i, user in enumerate(users):
                # Get scores
                scores = Score.query.filter_by(user_id=user.id).all()
                
                # Calculate statistics
                quizzes_taken = len(scores)
                total_questions = sum(score.total_questions for score in scores)
                total_correct = sum(score.total_scored for score in scores)
                average_score = round((total_correct / total_questions * 100) if total_questions > 0 else 0, 2)
                
                # Get last activity
                last_activity = max([score.time_stamp_of_attempt for score in scores], default=None) if scores else None
                
                writer.writerow([
                    user.id,
                    user.username,
                    user.full_name,
                    user.qualification,
                    quizzes_taken,
                    f"{average_score}%",
                    last_activity.strftime('%Y-%m-%d %H:%M:%S') if last_activity else 'Never'
                ])
                
                # Update progress
                job_data['progress'] = int((i + 1) / total_rows * 100)
            
            # Save CSV file
            filename = f"all_users_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            export_dir = os.path.join(app.static_folder, 'exports')
            os.makedirs(export_dir, exist_ok=True)
            
            file_path = os.path.join(export_dir, filename)
            with open(file_path, 'w', newline='') as f:
                f.write(output.getvalue())
            
            # Update job data
            job_data['status'] = 'completed'
            job_data['completed'] = datetime.now()
            job_data['file_path'] = file_path
            job_data['message'] = f"Export completed: {filename}"
            
            # Find admin user who triggered the job
            admin_user = User.query.filter_by(is_admin=True).first()
            if admin_user:
                try:
                    send_export_notification(admin_user.username, filename, file_path, 'user', app)
                    app.logger.info(f"Export notification sent to admin {admin_user.username}")
                except Exception as e:
                    app.logger.error(f"Failed to send export notification: {str(e)}")
                    job_data['message'] += f" (Failed to send notification: {str(e)})"
        
        except Exception as e:
            app.logger.error(f"Export failed: {str(e)}")
            job_data['status'] = 'failed'
            job_data['message'] = f"Export failed: {str(e)}"
            job_data['completed'] = datetime.now()

def get_job_status(job_id):
    """Get the status of a job"""
    if job_id not in jobs:
        return None
    return jobs[job_id]

def send_export_notification(email, filename, file_path, export_type, app=None):
    """Send email notification with export attachment"""
    if app is None:
        from flask import current_app
        app = current_app._get_current_object()
    
    # Get email configuration
    smtp_server = app.config.get('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = app.config.get('SMTP_PORT', 587)
    smtp_username = app.config.get('SMTP_USERNAME', '')
    smtp_password = app.config.get('SMTP_PASSWORD', '')
    from_email = app.config.get('FROM_EMAIL', 'quizmaster@example.com')
    
    # Check if email credentials are configured
    if not smtp_username or not smtp_password:
        app.logger.warning("Email credentials not configured, skipping email")
        return
    
    # Create message
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = email
    
    # Set subject based on export type
    if export_type == 'quiz':
        msg['Subject'] = 'Your Quiz Results Export is Ready'
        body = f"""
        <html>
        <body>
            <h2>Quiz Results Export</h2>
            <p>Hello,</p>
            <p>Your requested export of quiz results is now ready. The file has been attached to this email.</p>
            <p>Filename: {filename}</p>
            <br>
            <p>Thank you for using Quiz Master!</p>
        </body>
        </html>
        """
    else:  # user export
        msg['Subject'] = 'User Data Export is Ready'
        body = f"""
        <html>
        <body>
            <h2>User Data Export</h2>
            <p>Hello Admin,</p>
            <p>Your requested export of user data is now ready. The file has been attached to this email.</p>
            <p>Filename: {filename}</p>
            <br>
            <p>Thank you for using Quiz Master!</p>
        </body>
        </html>
        """
    
    # Attach HTML body
    msg.attach(MIMEText(body, 'html'))
    
    # Attach CSV file
    with open(file_path, 'rb') as f:
        attachment = MIMEApplication(f.read(), _subtype='csv')
        attachment.add_header('Content-Disposition', 'attachment', filename=filename)
        msg.attach(attachment)
    
    # Send email
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(msg)
        server.quit()
    except (smtplib.SMTPConnectError, socket.gaierror) as e:
        app.logger.error(f"Failed to connect to SMTP server: {str(e)}")
        app.logger.info("This is likely due to an invalid SMTP server address or network connectivity issues.")
        # We'll just log the error but not re-raise it, so the export process can still be considered successful
        # This prevents the export from failing just because email couldn't be sent
        return
    except Exception as e:
        app.logger.error(f"Failed to send export notification: {str(e)}")
        raise 
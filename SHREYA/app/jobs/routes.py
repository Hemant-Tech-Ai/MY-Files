"""
Routes for job management and export functionality.
"""
from flask import Blueprint, jsonify, request, current_app, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models import User, Score, Quiz, Chapter, Subject
from app.jobs.async_jobs import start_export_job, get_job_status
from app.jobs.scheduler import send_monthly_reports, generate_monthly_report, send_daily_reminders
from datetime import datetime, timedelta
import os

jobs_bp = Blueprint('jobs', __name__)

@jobs_bp.route('/user/export/quiz', methods=['POST'])
@jwt_required()
def export_user_quizzes():
    """Trigger an export job for user quiz data"""
    # Get user ID from token
    current_user_id_str = get_jwt_identity()
    
    try:
        # Convert to integer for database lookup
        current_user_id = int(current_user_id_str)
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid user ID"}), 401
    
    # Start export job
    job_id = start_export_job('user_quiz_export', user_id=current_user_id)
    
    return jsonify({
        "message": "Export job started",
        "job_id": job_id
    }), 202

@jobs_bp.route('/admin/export/users', methods=['POST'])
@jwt_required()
def export_all_users():
    """Trigger an export job for all users data (admin only)"""
    # Get user ID from token
    current_user_id_str = get_jwt_identity()
    
    try:
        # Convert to integer for database lookup
        current_user_id = int(current_user_id_str)
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid user ID"}), 401
    
    # Check if user is admin
    user = User.query.get(current_user_id)
    if not user or not user.is_admin:
        return jsonify({"error": "Admin access required"}), 403
    
    # Start export job
    job_id = start_export_job('admin_user_export', admin=True)
    
    return jsonify({
        "message": "Export job started",
        "job_id": job_id
    }), 202

@jobs_bp.route('/status/<job_id>', methods=['GET'])
@jwt_required()
def get_job_status_route(job_id):
    """Get status of a job"""
    # Get user ID from token
    current_user_id_str = get_jwt_identity()
    
    try:
        # Convert to integer for database lookup
        current_user_id = int(current_user_id_str)
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid user ID"}), 401
    
    # Get job status
    job_data = get_job_status(job_id)
    
    if not job_data:
        return jsonify({"error": "Job not found"}), 404
    
    # Check if user has access to this job
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    if not user.is_admin and str(job_data.get('user_id')) != current_user_id_str:
        return jsonify({"error": "Access denied"}), 403
    
    # Create response data
    response = {
        "id": job_data['id'],
        "type": job_data['type'],
        "status": job_data['status'],
        "progress": job_data['progress'],
        "message": job_data['message'],
        "created": job_data['created'].isoformat() if job_data['created'] else None,
        "completed": job_data['completed'].isoformat() if job_data['completed'] else None
    }
    
    # Add download URL if job is completed and file exists
    if job_data['status'] == 'completed' and job_data['file_path']:
        filename = os.path.basename(job_data['file_path'])
        response['download_url'] = f"/api/jobs/download/{filename}"
    
    return jsonify(response), 200

@jobs_bp.route('/download/<filename>', methods=['GET'])
@jwt_required()
def download_export_file(filename):
    """Download an export file"""
    app = current_app._get_current_object()
    export_dir = os.path.join(app.static_folder, 'exports')
    
    return send_from_directory(
        export_dir, 
        filename, 
        as_attachment=True,
        download_name=filename
    )

@jobs_bp.route('/admin/trigger-monthly-reports', methods=['POST'])
@jwt_required()
def trigger_monthly_reports():
    """Admin endpoint to manually trigger monthly reports for all users"""
    # Get user ID from token
    current_user_id_str = get_jwt_identity()
    
    try:
        # Convert to integer for database lookup
        current_user_id = int(current_user_id_str)
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid user ID"}), 401
    
    # Check if user is admin
    user = User.query.get(current_user_id)
    if not user or not user.is_admin:
        return jsonify({"error": "Admin access required"}), 403
    
    # Get month parameter (optional)
    data = request.get_json() or {}
    month = data.get('month')
    year = data.get('year')
    specific_user_id = data.get('user_id')  # Optional: for sending to a specific user
    
    try:
        app = current_app._get_current_object()
        
        # If month and year are specified, generate report for that month
        if month and year:
            try:
                month = int(month)
                year = int(year)
                if month < 1 or month > 12:
                    return jsonify({"error": "Month must be between 1 and 12"}), 400
                
                # Calculate date range for specified month
                if month == 12:
                    start_date = datetime(year, month, 1)
                    end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
                else:
                    start_date = datetime(year, month, 1)
                    end_date = datetime(year, month + 1, 1) - timedelta(days=1)
                
                month_name = start_date.strftime("%B %Y")
                
                # If specific user is specified, generate report only for that user
                if specific_user_id:
                    try:
                        user_id = int(specific_user_id)
                        target_user = User.query.get(user_id)
                        if not target_user:
                            return jsonify({"error": "User not found"}), 404
                        
                        # Generate report for specific user
                        try:
                            with app.app_context():
                                # Get scores for the user within the date range
                                scores = Score.query.filter(
                                    Score.user_id == user_id,
                                    Score.time_stamp_of_attempt >= start_date,
                                    Score.time_stamp_of_attempt <= end_date
                                ).all()
                                
                                if not scores:
                                    return jsonify({
                                        "message": f"No activity found for this user in {month_name}, no report sent."
                                    }), 200
                                
                                # Generate and send the report
                                generate_monthly_report(target_user, start_date, end_date, month_name)
                            
                            return jsonify({
                                "message": f"Monthly report for {month_name} generated and sent to {target_user.username}"
                            }), 200
                        except Exception as e:
                            app.logger.error(f"Failed to generate report for user {user_id}: {str(e)}")
                            return jsonify({"error": f"Failed to generate report: {str(e)}"}), 500
                        
                    except (ValueError, TypeError):
                        return jsonify({"error": "Invalid user ID"}), 400
                
                # Generate reports for all users
                success_count = 0
                error_count = 0
                
                with app.app_context():
                    # Get all normal users
                    users = User.query.filter_by(is_admin=False).all()
                    total_users = len(users)
                    
                    for user in users:
                        try:
                            # Get scores for this user within the date range
                            scores = Score.query.filter(
                                Score.user_id == user.id,
                                Score.time_stamp_of_attempt >= start_date,
                                Score.time_stamp_of_attempt <= end_date
                            ).all()
                            
                            if scores:
                                # Generate and send the report
                                generate_monthly_report(user, start_date, end_date, month_name)
                                success_count += 1
                        except Exception as e:
                            app.logger.error(f"Failed to generate report for user {user.id}: {str(e)}")
                            error_count += 1
                
                return jsonify({
                    "message": f"Monthly reports for {month_name} processed. Sent: {success_count}/{total_users}. Errors: {error_count}."
                }), 200
                
            except (ValueError, TypeError) as e:
                app.logger.error(f"Invalid month or year format: {str(e)}")
                return jsonify({"error": "Invalid month or year format"}), 400
        
        # Otherwise, generate reports for the previous month (default behavior)
        try:
            with app.app_context():
                # Use the function from scheduler.py
                send_monthly_reports()
            
            return jsonify({
                "message": "Monthly reports generated and sent to all eligible users"
            }), 200
        except Exception as e:
            app.logger.error(f"Failed to generate default monthly reports: {str(e)}")
            return jsonify({"error": f"Failed to generate monthly reports: {str(e)}"}), 500
        
    except Exception as e:
        current_app.logger.error(f"Failed to generate monthly reports: {str(e)}")
        return jsonify({
            "error": f"Failed to generate monthly reports: {str(e)}"
        }), 500

@jobs_bp.route('/admin/preview-monthly-report', methods=['POST'])
@jwt_required()
def preview_monthly_report():
    """Preview a monthly report without sending it"""
    # Get user ID from token
    current_user_id_str = get_jwt_identity()
    
    try:
        # Convert to integer for database lookup
        current_user_id = int(current_user_id_str)
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid user ID"}), 401
    
    # Check if user is admin
    user = User.query.get(current_user_id)
    if not user or not user.is_admin:
        return jsonify({"error": "Admin access required"}), 403
    
    # Get month parameter and user
    data = request.get_json() or {}
    month = data.get('month')
    year = data.get('year')
    target_user_id = data.get('user_id')
    
    if not month or not year:
        return jsonify({"error": "Month and year are required"}), 400
    
    if not target_user_id:
        return jsonify({"error": "User ID is required for preview"}), 400
    
    try:
        month = int(month)
        year = int(year)
        target_user_id = int(target_user_id)
    except ValueError:
        return jsonify({"error": "Invalid month, year, or user ID format"}), 400
    
    # Get the target user
    target_user = User.query.get(target_user_id)
    if not target_user:
        return jsonify({"error": "User not found"}), 404
    
    # Calculate date range for specified month
    if month == 12:
        start_date = datetime(year, month, 1)
        end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        start_date = datetime(year, month, 1)
        end_date = datetime(year, month + 1, 1) - timedelta(days=1)
    
    month_name = start_date.strftime("%B %Y")
    
    try:
        app = current_app._get_current_object()
        
        with app.app_context():
            # Get scores for this user within the date range
            scores = Score.query.filter(
                Score.user_id == target_user_id,
                Score.time_stamp_of_attempt >= start_date,
                Score.time_stamp_of_attempt <= end_date
            ).all()
            
            if not scores:
                return jsonify({
                    "message": "No activity found for this user in the selected month",
                    "has_data": False
                }), 200
            
            # Calculate report data
            total_quizzes = len(scores)
            total_questions = sum(score.total_questions for score in scores)
            total_correct = sum(score.total_scored for score in scores)
            average_score = round((total_correct / total_questions * 100) if total_questions > 0 else 0, 2)
            
            # Get quiz details
            quiz_details = []
            for score in scores:
                quiz = Quiz.query.get(score.quiz_id)
                if quiz:
                    chapter = Chapter.query.get(quiz.chapter_id)
                    subject = Subject.query.get(chapter.subject_id) if chapter else None
                    
                    quiz_details.append({
                        'subject': subject.name if subject else 'Unknown',
                        'chapter': chapter.name if chapter else 'Unknown',
                        'quiz': quiz.remarks or f"Quiz {quiz.id}",
                        'date': score.time_stamp_of_attempt.strftime("%Y-%m-%d"),
                        'score': f"{score.total_scored}/{score.total_questions}",
                        'percentage': round(score.total_scored / score.total_questions * 100 if score.total_questions > 0 else 0, 2)
                    })
            
            # Return the preview data
            return jsonify({
                "has_data": True,
                "user": {
                    "id": target_user.id,
                    "full_name": target_user.full_name,
                    "email": target_user.username
                },
                "report_data": {
                    "month": month_name,
                    "total_quizzes": total_quizzes,
                    "average_score": average_score,
                    "quiz_details": quiz_details
                }
            }), 200
            
    except Exception as e:
        current_app.logger.error(f"Failed to generate report preview: {str(e)}")
        return jsonify({
            "error": f"Failed to generate report preview: {str(e)}"
        }), 500

@jobs_bp.route('/admin/trigger-daily-reminders', methods=['POST'])
@jwt_required()
def trigger_daily_reminders():
    """Admin endpoint to manually trigger daily reminders for testing"""
    # Get user ID from token
    current_user_id_str = get_jwt_identity()
    
    try:
        # Convert to integer for database lookup
        current_user_id = int(current_user_id_str)
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid user ID"}), 401
    
    # Check if user is admin
    user = User.query.get(current_user_id)
    if not user or not user.is_admin:
        return jsonify({"error": "Admin access required"}), 403
    
    try:
        # Manually trigger daily reminders
        send_daily_reminders()
        return jsonify({"message": "Daily reminders triggered successfully"}), 200
    except Exception as e:
        current_app.logger.error(f"Error triggering daily reminders: {str(e)}")
        return jsonify({"error": f"Failed to trigger reminders: {str(e)}"}), 500 
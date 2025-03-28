from flask import Blueprint, request, jsonify, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from functools import wraps
import requests

from app.models import db, Subject, Chapter, Quiz, Question, User, QuizAssignment, Score
from app.jobs.cache import cached_route, invalidate_quiz_cache, invalidate_user_cache

admin_bp = Blueprint('admin', __name__)

# Helper function to check if user is admin
def is_admin():
    current_user_id = get_jwt_identity()
    if not current_user_id:
        return False
    user = User.query.get(current_user_id)
    return user and user.is_admin

# Admin middleware
def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        # Get the JWT headers to debug token format issues
        auth_header = request.headers.get('Authorization', '')
        print(f"Authorization header: {auth_header}")
        
        # Get the identity from JWT token (will be string format)
        current_user_id_str = get_jwt_identity()
        print(f"JWT identity (string): {current_user_id_str}")
        
        if not current_user_id_str:
            print("No user ID in JWT token")
            return jsonify({"error": "Authentication required"}), 401
            
        # Convert to integer for database lookup
        try:
            current_user_id = int(current_user_id_str)
            print(f"Converted user ID to int: {current_user_id}")
        except (ValueError, TypeError):
            print(f"Failed to convert user ID to integer: {current_user_id_str}")
            return jsonify({"error": "Invalid user ID"}), 401
            
        user = User.query.get(current_user_id)
        
        if not user:
            print(f"User ID {current_user_id} not found in database")
            return jsonify({"error": "User not found"}), 401
            
        if not user.is_admin:
            print(f"User {user.username} (ID: {current_user_id}) is not an admin")
            return jsonify({"error": "Admin privileges required"}), 403
            
        print(f"Admin access granted to {user.username} (ID: {current_user_id})")
        
        # Call the original function with the user ID
        return fn(current_user_id, *args, **kwargs)
    return wrapper

# Dashboard stats endpoint
@admin_bp.route('/stats', methods=['GET'])
@admin_required
def get_dashboard_stats(current_user_id):
    # Count various entities
    subject_count = Subject.query.count()
    chapter_count = Chapter.query.count()
    quiz_count = Quiz.query.count()
    question_count = Question.query.count()
    user_count = User.query.filter_by(is_admin=False).count()
    
    return jsonify({
        'subjectCount': subject_count,
        'chapterCount': chapter_count,
        'quizCount': quiz_count,
        'questionCount': question_count,
        'userCount': user_count
    })

# Subject routes
@admin_bp.route('/subjects', methods=['GET'])
@admin_required
def get_subjects(current_user_id):
    subjects = Subject.query.all()
    
    results = []
    for subject in subjects:
        subject_dict = {
            'id': subject.id,
            'name': subject.name,
            'description': getattr(subject, 'description', ''),
            'chapters_count': len(subject.chapters) if hasattr(subject, 'chapters') else 0
        }
        results.append(subject_dict)
    
    return jsonify(results)

@admin_bp.route('/subjects', methods=['POST'])
@admin_required
def create_subject(current_user_id):
    data = request.get_json()
    
    if not data or 'name' not in data:
        return jsonify({'message': 'Subject name is required'}), 400
    
    # Check if subject with same name already exists
    existing = Subject.query.filter_by(name=data['name']).first()
    if existing:
        return jsonify({'message': 'Subject with this name already exists'}), 400
    
    # Create new subject
    subject = Subject(
        name=data['name'],
        description=data.get('description', '')
    )
    
    db.session.add(subject)
    db.session.commit()
    
    return jsonify({
        'id': subject.id,
        'name': subject.name,
        'description': subject.description,
        'message': 'Subject created successfully'
    }), 201

@admin_bp.route('/subjects/<int:id>', methods=['PUT'])
@admin_required
def update_subject(current_user_id, id):
    data = request.get_json()
    
    if not data or 'name' not in data:
        return jsonify({'message': 'Subject name is required'}), 400
    
    # Find subject
    subject = Subject.query.get_or_404(id)
    
    # Check if another subject with the same name exists
    existing = Subject.query.filter(Subject.name == data['name'], Subject.id != id).first()
    if existing:
        return jsonify({'message': 'Another subject with this name already exists'}), 400
    
    # Update subject
    subject.name = data['name']
    subject.description = data.get('description', subject.description)
    db.session.commit()
    
    return jsonify({
        'id': subject.id,
        'name': subject.name,
        'description': subject.description,
        'message': 'Subject updated successfully'
    })

@admin_bp.route('/subjects/<int:id>', methods=['DELETE'])
@admin_required
def delete_subject(current_user_id, id):
    # Find subject
    subject = Subject.query.get_or_404(id)
    
    # Check if subject has chapters
    if hasattr(subject, 'chapters') and len(subject.chapters) > 0:
        return jsonify({'message': 'Cannot delete subject with existing chapters'}), 400
    
    # Delete subject
    db.session.delete(subject)
    db.session.commit()
    
    return jsonify({'message': 'Subject deleted successfully'})

# Chapter routes
@admin_bp.route('/chapters', methods=['GET'])
@admin_required
def get_chapters(current_user_id):
    chapters = db.session.query(
        Chapter, Subject.name.label('subject_name')
    ).join(
        Subject, Chapter.subject_id == Subject.id
    ).all()
    
    results = []
    for chapter, subject_name in chapters:
        chapter_dict = {
            'id': chapter.id,
            'name': chapter.name,
            'subject_id': chapter.subject_id,
            'subject_name': subject_name,
            'description': getattr(chapter, 'description', '')
        }
        results.append(chapter_dict)
    
    return jsonify(results)

@admin_bp.route('/chapters', methods=['POST'])
@admin_required
def create_chapter(current_user_id):
    data = request.get_json()
    
    if not data or 'name' not in data or 'subject_id' not in data:
        return jsonify({'message': 'Chapter name and subject ID are required'}), 400
    
    # Check if subject exists
    subject = Subject.query.get(data['subject_id'])
    if not subject:
        return jsonify({'message': 'Subject not found'}), 404
    
    # Check if chapter with same name already exists in this subject
    existing = Chapter.query.filter_by(name=data['name'], subject_id=data['subject_id']).first()
    if existing:
        return jsonify({'message': 'Chapter with this name already exists for this subject'}), 400
    
    # Create new chapter
    chapter = Chapter(
        name=data['name'],
        subject_id=data['subject_id'],
        description=data.get('description', '')
    )
    
    db.session.add(chapter)
    db.session.commit()
    
    return jsonify({
        'id': chapter.id,
        'name': chapter.name,
        'subject_id': chapter.subject_id,
        'description': chapter.description,
        'message': 'Chapter created successfully'
    }), 201

@admin_bp.route('/chapters/<int:id>', methods=['PUT'])
@admin_required
def update_chapter(current_user_id, id):
    chapter = Chapter.query.get_or_404(id)
    data = request.get_json()
    
    if 'name' in data:
        chapter.name = data['name']
    if 'subject_id' in data:
        chapter.subject_id = data['subject_id']
    if 'description' in data:
        chapter.description = data['description']
    
    db.session.commit()
    
    return jsonify({
        'id': chapter.id,
        'name': chapter.name,
        'subject_id': chapter.subject_id,
        'description': chapter.description
    })

@admin_bp.route('/chapters/<int:id>', methods=['DELETE'])
@admin_required
def delete_chapter(current_user_id, id):
    chapter = Chapter.query.get_or_404(id)
    db.session.delete(chapter)
    db.session.commit()
    
    return jsonify({'message': 'Chapter deleted successfully'})

# Quiz routes
@admin_bp.route('/quizzes', methods=['GET'])
@admin_required
def get_quizzes(current_user_id):
    quizzes = db.session.query(
        Quiz, Chapter.name.label('chapter_name'), Subject.name.label('subject_name')
    ).join(
        Chapter, Quiz.chapter_id == Chapter.id
    ).join(
        Subject, Chapter.subject_id == Subject.id
    ).all()
    
    results = []
    for quiz, chapter_name, subject_name in quizzes:
        # Count the number of questions for this quiz
        question_count = Question.query.filter_by(quiz_id=quiz.id).count()
        
        quiz_dict = {
            'id': quiz.id,
            'chapter_id': quiz.chapter_id,
            'chapter_name': chapter_name,
            'subject_name': subject_name,
            'date_of_quiz': quiz.date_of_quiz.strftime('%Y-%m-%d') if quiz.date_of_quiz else None,
            'time_duration': quiz.time_duration,
            'remarks': quiz.remarks,
            'questions_count': question_count  # Add the question count
        }
        results.append(quiz_dict)
    
    return jsonify(results)

@admin_bp.route('/quizzes', methods=['POST'])
@admin_required
def create_quiz(current_user_id):
    data = request.get_json()
    
    if not data or 'chapter_id' not in data:
        return jsonify({'message': 'Chapter ID is required'}), 400
    
    # Check if chapter exists
    chapter = Chapter.query.get(data['chapter_id'])
    if not chapter:
        return jsonify({'message': 'Chapter not found'}), 404
    
    # Parse date if provided
    date_of_quiz = None
    if 'date_of_quiz' in data and data['date_of_quiz']:
        try:
            date_of_quiz = datetime.strptime(data['date_of_quiz'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'message': 'Invalid date format. Use YYYY-MM-DD.'}), 400
    
    # Create new quiz
    quiz = Quiz(
        chapter_id=data['chapter_id'],
        date_of_quiz=date_of_quiz,
        time_duration=data.get('time_duration', 30),
        remarks=data.get('remarks', '')
    )
    
    db.session.add(quiz)
    db.session.commit()
    
    return jsonify({
        'id': quiz.id,
        'chapter_id': quiz.chapter_id,
        'date_of_quiz': quiz.date_of_quiz.strftime('%Y-%m-%d') if quiz.date_of_quiz else None,
        'time_duration': quiz.time_duration,
        'remarks': quiz.remarks,
        'message': 'Quiz created successfully'
    }), 201

@admin_bp.route('/quizzes/<int:id>', methods=['PUT'])
@admin_required
def update_quiz(current_user_id, id):
    quiz = Quiz.query.get_or_404(id)
    data = request.get_json()
    
    if 'chapter_id' in data:
        quiz.chapter_id = data['chapter_id']
    
    if 'date_of_quiz' in data and data['date_of_quiz']:
        try:
            quiz.date_of_quiz = datetime.strptime(data['date_of_quiz'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'message': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    if 'time_duration' in data:
        quiz.time_duration = data['time_duration']
    
    if 'remarks' in data:
        quiz.remarks = data['remarks']
    
    db.session.commit()
    
    return jsonify({
        'id': quiz.id,
        'chapter_id': quiz.chapter_id,
        'date_of_quiz': quiz.date_of_quiz.strftime('%Y-%m-%d') if quiz.date_of_quiz else None,
        'time_duration': quiz.time_duration,
        'remarks': quiz.remarks
    })

@admin_bp.route('/quizzes/<int:id>', methods=['DELETE'])
@admin_required
def delete_quiz(current_user_id, id):
    quiz = Quiz.query.get_or_404(id)
    db.session.delete(quiz)
    db.session.commit()
    
    return jsonify({'message': 'Quiz deleted successfully'})

@admin_bp.route('/quizzes/<int:id>/assignments', methods=['GET'])
@admin_required
def get_quiz_assignments(current_user_id, id):
    # Verify quiz exists
    quiz = Quiz.query.get(id)
    if not quiz:
        return jsonify({"error": "Quiz not found"}), 404
    
    try:
        from sqlalchemy import text
        # Get all assignments for this quiz
        result = db.session.execute(
            text("""
            SELECT qa.id, qa.user_id, u.username, u.full_name
            FROM quiz_assignment qa
            JOIN user u ON qa.user_id = u.id
            WHERE qa.quiz_id = :quiz_id
            """), 
            {"quiz_id": id}
        )
        
        # Convert result to list of dictionaries
        assignments = []
        for row in result:
            assignments.append({
                'id': row[0],
                'user_id': row[1],
                'username': row[2],
                'full_name': row[3]
            })
        
        return jsonify({'assignments': assignments})
    except Exception as e:
        print(f"Error fetching assignments: {str(e)}")
        return jsonify({'assignments': [], 'error': str(e)}), 500

@admin_bp.route('/quizzes/<int:id>/assign', methods=['POST'])
@admin_required
def assign_quiz(current_user_id, id):
    # Verify that quiz exists
    quiz = Quiz.query.get(id)
    if not quiz:
        return jsonify({"error": "Quiz not found"}), 404
    
    data = request.get_json()
    if not data or not data.get('userIds'):
        return jsonify({"error": "No user IDs provided"}), 400
    
    user_ids = data.get('userIds')
    assignments = []
    errors = []
    
    try:
        from sqlalchemy import text
        # Create quiz_assignment table if it doesn't exist
        try:
            db.session.execute(
                text("""
                CREATE TABLE IF NOT EXISTS quiz_assignment (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    quiz_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    FOREIGN KEY (quiz_id) REFERENCES quiz (id),
                    FOREIGN KEY (user_id) REFERENCES user (id),
                    UNIQUE(quiz_id, user_id)
                )
                """)
            )
            db.session.commit()
        except Exception as e:
            print(f"Error creating quiz_assignment table: {str(e)}")
            db.session.rollback()
    
        # Insert assignments
        for user_id in user_ids:
            try:
                # Check if user exists
                user = User.query.get(user_id)
                if not user:
                    errors.append(f"User with ID {user_id} not found")
                    continue
                
                # Check if assignment already exists
                existing = db.session.execute(
                    text("SELECT id FROM quiz_assignment WHERE quiz_id = :quiz_id AND user_id = :user_id"),
                    {"quiz_id": id, "user_id": user_id}
                ).fetchone()
                
                if existing:
                    assignments.append({
                        'quiz_id': id,
                        'user_id': user_id,
                        'username': user.username,
                        'full_name': user.full_name,
                        'status': 'already assigned'
                    })
                    continue
                
                # Insert new assignment
                result = db.session.execute(
                    text("""
                    INSERT INTO quiz_assignment (quiz_id, user_id)
                    VALUES (:quiz_id, :user_id)
                    """),
                    {"quiz_id": id, "user_id": user_id}
                )
                db.session.commit()
                
                # Invalidate cache for this user and quiz
                invalidate_user_cache(user_id)
                invalidate_quiz_cache(id)
                
                assignments.append({
                    'quiz_id': id,
                    'user_id': user_id,
                    'username': user.username,
                    'full_name': user.full_name,
                    'status': 'assigned'
                })
                
            except Exception as e:
                db.session.rollback()
                errors.append(f"Error assigning quiz to user {user_id}: {str(e)}")
    
        return jsonify({
            'success': True,
            'assignments': assignments,
            'errors': errors
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_bp.route('/quizzes/<int:quiz_id>/assignments/<int:user_id>', methods=['DELETE'])
@admin_required
def remove_quiz_assignment(current_user_id, quiz_id, user_id):
    try:
        from sqlalchemy import text
        # Delete the assignment
        db.session.execute(
            text("""
            DELETE FROM quiz_assignment 
            WHERE quiz_id = :quiz_id AND user_id = :user_id
            """), 
            {"quiz_id": quiz_id, "user_id": user_id}
        )
        db.session.commit()
        
        # Invalidate cache for this user and quiz
        invalidate_user_cache(user_id)
        invalidate_quiz_cache(quiz_id)
        
        return jsonify({'success': True, 'message': 'Assignment removed successfully'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f"Error removing assignment: {str(e)}"}), 500

@admin_bp.route('/assignments', methods=['GET'])
@admin_required
def get_all_quiz_assignments(current_user_id):
    try:
        from sqlalchemy import text
        # Get all quiz assignments with quiz, subject, chapter, and user details
        result = db.session.execute(
            text("""
            SELECT 
                qa.id, 
                qa.quiz_id, 
                qa.user_id, 
                u.username, 
                u.full_name as student_name,
                q.date_of_quiz,
                q.time_duration,
                s.name as subject_name,
                c.name as chapter_name,
                CASE WHEN sc.id IS NOT NULL THEN 1 ELSE 0 END as completed
            FROM quiz_assignment qa
            JOIN user u ON qa.user_id = u.id
            JOIN quiz q ON qa.quiz_id = q.id
            JOIN chapter c ON q.chapter_id = c.id
            JOIN subject s ON c.subject_id = s.id
            LEFT JOIN score sc ON qa.user_id = sc.user_id AND qa.quiz_id = sc.quiz_id
            ORDER BY qa.id DESC
            """)
        )
        
        # Convert result to list of dictionaries
        assignments = []
        for row in result:
            # Safely handle date formatting
            date_of_quiz = None
            if row[5]:
                # Check if it's already a string or a datetime object
                if hasattr(row[5], 'strftime'):
                    date_of_quiz = row[5].strftime('%Y-%m-%d')
                else:
                    # If it's a string, just use it directly
                    date_of_quiz = row[5]
            
            assignments.append({
                'id': row[0],
                'quiz_id': row[1],
                'user_id': row[2],
                'username': row[3],
                'student_name': row[4],
                'date_of_quiz': date_of_quiz,
                'time_duration': row[6],
                'subject_name': row[7],
                'chapter_name': row[8],
                'completed': bool(row[9])
            })
        
        return jsonify(assignments)
    except Exception as e:
        print(f"Error fetching all assignments: {str(e)}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_users(current_user_id):
    users = User.query.all()
    
    results = []
    for user in users:
        user_dict = {
            'id': user.id,
            'username': user.username,
            'full_name': user.full_name,
            'qualification': user.qualification,
            'is_admin': user.is_admin
        }
        results.append(user_dict)
    
    return jsonify(results)

# Question routes
@admin_bp.route('/questions', methods=['GET'])
@admin_required
def get_questions(current_user_id):
    quiz_id = request.args.get('quiz_id')
    
    query = db.session.query(
        Question, Quiz.id.label('quiz_id'), 
        Chapter.name.label('chapter_name'), 
        Subject.name.label('subject_name')
    ).join(
        Quiz, Question.quiz_id == Quiz.id
    ).join(
        Chapter, Quiz.chapter_id == Chapter.id
    ).join(
        Subject, Chapter.subject_id == Subject.id
    )
    
    if quiz_id:
        query = query.filter(Question.quiz_id == quiz_id)
        
    questions = query.all()
    
    results = []
    for question, quiz_id, chapter_name, subject_name in questions:
        question_dict = {
            'id': question.id,
            'quiz_id': quiz_id,
            'question_statement': question.question_statement,
            'option1': question.option1,
            'option2': question.option2,
            'option3': question.option3,
            'option4': question.option4,
            'correct_option': question.correct_option,
            'quiz_name': f"{subject_name} - {chapter_name}"
        }
        results.append(question_dict)
    
    return jsonify(results)

@admin_bp.route('/questions', methods=['POST'])
@admin_required
def create_question(current_user_id):
    data = request.get_json()
    
    if not data or 'quiz_id' not in data or 'question_statement' not in data:
        return jsonify({'message': 'Quiz ID and question statement are required'}), 400
    
    # Check if quiz exists
    quiz = Quiz.query.get(data['quiz_id'])
    if not quiz:
        return jsonify({'message': 'Quiz not found'}), 404
    
    # Create new question
    question = Question(
        quiz_id=data['quiz_id'],
        question_statement=data['question_statement'],
        option1=data.get('option1', ''),
        option2=data.get('option2', ''),
        option3=data.get('option3', ''),
        option4=data.get('option4', ''),
        correct_option=data.get('correct_option', 1)
    )
    
    db.session.add(question)
    db.session.commit()
    
    return jsonify({
        'id': question.id,
        'quiz_id': question.quiz_id,
        'question_statement': question.question_statement,
        'message': 'Question created successfully'
    }), 201

@admin_bp.route('/questions/<int:id>', methods=['PUT'])
@admin_required
def update_question(current_user_id, id):
    question = Question.query.get_or_404(id)
    data = request.get_json()
    
    if 'quiz_id' in data:
        question.quiz_id = data['quiz_id']
    
    if 'question_statement' in data:
        question.question_statement = data['question_statement']
    
    if 'option1' in data:
        question.option1 = data['option1']
    
    if 'option2' in data:
        question.option2 = data['option2']
    
    if 'option3' in data:
        question.option3 = data['option3']
    
    if 'option4' in data:
        question.option4 = data['option4']
    
    if 'correct_option' in data:
        if not (1 <= data['correct_option'] <= 4):
            return jsonify({'message': 'Correct option must be between 1 and 4'}), 400
        question.correct_option = data['correct_option']
    
    db.session.commit()
    
    return jsonify({
        'id': question.id,
        'quiz_id': question.quiz_id,
        'question_statement': question.question_statement,
        'option1': question.option1,
        'option2': question.option2,
        'option3': question.option3,
        'option4': question.option4,
        'correct_option': question.correct_option
    })

@admin_bp.route('/questions/<int:id>', methods=['DELETE'])
@admin_required
def delete_question(current_user_id, id):
    question = Question.query.get_or_404(id)
    db.session.delete(question)
    db.session.commit()
    
    return jsonify({'message': 'Question deleted successfully'})

# Add new routes for report management
@admin_bp.route('/reports/monthly', methods=['GET'])
@admin_required
def get_monthly_report_options(current_user_id):
    """Get users and month options for monthly reports"""
    try:
        # Get all non-admin users for the dropdown
        users = User.query.filter_by(is_admin=False).all()
        user_options = [{'id': user.id, 'name': user.full_name, 'email': user.username} for user in users]
        
        # Get months with activity for the dropdown
        # Find unique months from score records
        scores = Score.query.all()
        months = set()
        
        for score in scores:
            if score.time_stamp_of_attempt:
                month_year = score.time_stamp_of_attempt.strftime('%Y-%m')
                months.add(month_year)
        
        # Format month options
        month_options = []
        for month_year in sorted(months, reverse=True):
            year, month = month_year.split('-')
            date_obj = datetime(int(year), int(month), 1)
            month_options.append({
                'value': month_year,
                'label': date_obj.strftime('%B %Y'),
                'month': int(month),
                'year': int(year)
            })
        
        return jsonify({
            'users': user_options,
            'months': month_options
        }), 200
    
    except Exception as e:
        print(f"Error in get_monthly_report_options: {str(e)}")
        return jsonify({"error": f"Failed to fetch report options: {str(e)}"}), 500

@admin_bp.route('/reports/monthly/trigger', methods=['POST'])
@admin_required
def trigger_monthly_report(current_user_id):
    """Trigger a monthly report generation"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Get parameters
        month = data.get('month')
        year = data.get('year')
        user_id = data.get('user_id')  # Optional
        
        # Validate parameters
        if not month or not year:
            return jsonify({"error": "Month and year are required"}), 400
        
        # Prepare request payload
        payload = {
            'month': month,
            'year': year
        }
        
        if user_id:
            payload['user_id'] = user_id
        
        # Get the JWT token
        auth_header = request.headers.get('Authorization', '')
        
        # Make request to jobs API
        api_url = request.host_url.rstrip('/') + '/api/jobs/admin/trigger-monthly-reports'
        
        response = requests.post(
            api_url,
            json=payload,
            headers={'Authorization': auth_header}
        )
        
        # Return the response from the API
        return jsonify(response.json()), response.status_code
    
    except Exception as e:
        print(f"Error in trigger_monthly_report: {str(e)}")
        return jsonify({"error": f"Failed to trigger monthly report: {str(e)}"}), 500

@admin_bp.route('/reports/stats', methods=['GET'])
@admin_required
def get_report_stats(current_user_id):
    """Get statistics about report generation"""
    try:
        # Get count of users
        user_count = User.query.filter_by(is_admin=False).count()
        
        # Get count of scores in the last month
        one_month_ago = datetime.now().replace(day=1)
        scores_last_month = Score.query.filter(Score.time_stamp_of_attempt >= one_month_ago).count()
        
        # Get count of total quizzes
        quiz_count = Quiz.query.count()
        
        # Get top performing users (based on average score)
        users = User.query.filter_by(is_admin=False).all()
        user_stats = []
        
        for user in users:
            scores = Score.query.filter_by(user_id=user.id).all()
            if scores:
                total_correct = sum(score.total_scored for score in scores)
                total_questions = sum(score.total_questions for score in scores)
                avg_score = round((total_correct / total_questions * 100), 1) if total_questions > 0 else 0
                
                user_stats.append({
                    'id': user.id,
                    'name': user.full_name,
                    'email': user.username,
                    'quizzes_taken': len(scores),
                    'average_score': avg_score
                })
        
        # Sort by average score (descending)
        user_stats.sort(key=lambda x: x['average_score'], reverse=True)
        
        return jsonify({
            'user_count': user_count,
            'scores_last_month': scores_last_month,
            'quiz_count': quiz_count,
            'top_users': user_stats[:5]  # Return top 5 users
        }), 200
    
    except Exception as e:
        print(f"Error in get_report_stats: {str(e)}")
        return jsonify({"error": f"Failed to fetch report stats: {str(e)}"}), 500

# Add route to serve the reports page
@admin_bp.route('/reports', methods=['GET'])
@admin_required
def reports_page(current_user_id):
    """Serve the admin reports dashboard page"""
    return render_template('admin/reports.html')

# Preview Monthly Report
@admin_bp.route('/reports/monthly/preview', methods=['POST'])
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
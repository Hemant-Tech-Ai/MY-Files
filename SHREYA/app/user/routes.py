from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

from app.models import db, Quiz, Question, Score, Chapter, Subject, User, QuizAssignment
from app.jobs.cache import cached_route, invalidate_quiz_cache, invalidate_user_cache

user_bp = Blueprint('user', __name__)

# User middleware 
def user_required(fn):
    @jwt_required()
    def wrapper(*args, **kwargs):
        # Get user ID from token (as string)
        current_user_id_str = get_jwt_identity()
        
        # Convert to integer for database lookup
        try:
            current_user_id = int(current_user_id_str)
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid user ID"}), 401
            
        return fn(current_user_id, *args, **kwargs)
    wrapper.__name__ = fn.__name__
    return wrapper

@user_bp.route('/quizzes', methods=['GET'])
@jwt_required()
@cached_route(timeout=300)  # Cache for 5 minutes
def get_assigned_quizzes():
    # Get user ID from token (as string)
    current_user_id_str = get_jwt_identity()
    
    # Convert to integer for database lookup
    try:
        current_user_id = int(current_user_id_str)
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid user ID"}), 401
    
    try:
        # Check if user exists
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
            
        # Get quizzes assigned to the user
        assignments = QuizAssignment.query.filter_by(user_id=current_user_id).all()
        
        quizzes = []
        for assignment in assignments:
            quiz = assignment.quiz
            if not quiz:
                continue  # Skip if quiz is None
                
            chapter = quiz.chapter
            if not chapter:
                # Skip quizzes with no chapter or log them for debugging
                print(f"Warning: Quiz ID {quiz.id} has no associated chapter")
                continue
                
            # Check if the user has a score for this quiz
            scores = Score.query.filter_by(user_id=current_user_id, quiz_id=quiz.id).all()
            completed = len(scores) > 0
            
            quizzes.append({
                'id': quiz.id,
                'chapter_id': quiz.chapter_id,
                'chapter_name': chapter.name,
                'subject_name': chapter.subject.name if chapter.subject else "Unknown Subject",
                'date_of_quiz': quiz.date_of_quiz.isoformat() if quiz.date_of_quiz else None,
                'time_duration': quiz.time_duration,
                'remarks': quiz.remarks,
                'completed': completed,
                'score': scores[0].total_scored if completed else None,
                'total_questions': scores[0].total_questions if completed else None
            })
            
        return jsonify(quizzes), 200
    except Exception as e:
        print(f"Error in get_assigned_quizzes: {str(e)}")
        return jsonify({"error": "Failed to fetch quizzes"}), 500

@user_bp.route('/quizzes/<int:id>/questions', methods=['GET'])
@user_required
@cached_route(timeout=300)  # Cache for 5 minutes
def get_quiz_questions(current_user_id, id):
    # Verify quiz exists
    quiz = Quiz.query.get(id)
    if not quiz:
        return jsonify({"error": "Quiz not found"}), 404
    
    # Verify user is assigned to this quiz
    assignment = QuizAssignment.query.filter_by(user_id=current_user_id, quiz_id=id).first()
    if not assignment:
        return jsonify({"error": "User not assigned to this quiz"}), 403
    
    try:
        # Check if user has already completed this quiz
        score = Score.query.filter_by(user_id=current_user_id, quiz_id=id).first()
        if score:
            return jsonify({
                "error": "Quiz already completed",
                "score": score.total_scored,
                "total_questions": score.total_questions,
                "completed_at": score.time_stamp_of_attempt.isoformat()
            }), 400
        
        questions = Question.query.filter_by(quiz_id=id).all()
        if not questions:
            return jsonify({"error": "No questions found for this quiz"}), 404
        
        # Format questions, removing correct answers
        formatted_questions = []
        for q in questions:
            formatted_questions.append({
                'id': q.id,
                'question_statement': q.question_statement,
                'options': [
                    q.option1,
                    q.option2,
                    q.option3,
                    q.option4
                ]
            })
            
        return jsonify({
            'quiz_id': id,
            'time_duration': quiz.time_duration,
            'questions': formatted_questions
        }), 200
    except Exception as e:
        print(f"Error in get_quiz_questions: {str(e)}")
        return jsonify({"error": "Failed to fetch quiz questions"}), 500

@user_bp.route('/quizzes/submit', methods=['POST'])
@user_required
def submit_quiz(current_user_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    quiz_id = data.get('quiz_id')
    answers = data.get('answers', [])
    
    if not quiz_id or not answers:
        return jsonify({"error": "Missing required fields"}), 400
    
    # Verify quiz exists
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return jsonify({"error": "Quiz not found"}), 404
    
    # Verify user is assigned to this quiz
    assignment = QuizAssignment.query.filter_by(user_id=current_user_id, quiz_id=quiz_id).first()
    if not assignment:
        return jsonify({"error": "User not assigned to this quiz"}), 403
    
    # Check if user has already completed this quiz
    existing_score = Score.query.filter_by(user_id=current_user_id, quiz_id=quiz_id).first()
    if existing_score:
        return jsonify({
            "error": "Quiz already submitted",
            "score": existing_score.total_scored,
            "total_questions": existing_score.total_questions
        }), 400
    
    try:
        # Get questions and validate answers
        questions = Question.query.filter_by(quiz_id=quiz_id).all()
        if not questions:
            return jsonify({"error": "No questions found for this quiz"}), 404
        
        question_map = {q.id: q for q in questions}
        total_correct = 0
        
        for answer in answers:
            question_id = answer.get('question_id')
            selected_option = answer.get('selected_option')
            
            if question_id in question_map and selected_option is not None:
                question = question_map[question_id]
                if selected_option == question.correct_option:
                    total_correct += 1
        
        # Create score record
        score = Score(
            user_id=current_user_id,
            quiz_id=quiz_id,
            total_scored=total_correct,
            total_questions=len(questions),
            time_stamp_of_attempt=datetime.now()
        )
        
        db.session.add(score)
        db.session.commit()
        
        # Invalidate quiz and user cache
        invalidate_quiz_cache(quiz_id)
        invalidate_user_cache(current_user_id)
        
        return jsonify({
            "message": "Quiz submitted successfully",
            "score": total_correct,
            "total_questions": len(questions),
            "percentage": round(total_correct / len(questions) * 100, 2)
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error in submit_quiz: {str(e)}")
        return jsonify({"error": "Failed to submit quiz"}), 500

@user_bp.route('/scores', methods=['GET'])
@jwt_required()
@cached_route(timeout=300)  # Cache for 5 minutes
def get_user_scores():
    # Get user ID from token (as string)
    current_user_id_str = get_jwt_identity()
    
    # Convert to integer for database lookup
    try:
        current_user_id = int(current_user_id_str)
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid user ID"}), 401
    
    try:
        # Check if user exists
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Get scores
        scores = Score.query.filter_by(user_id=current_user_id).all()
        
        result = []
        for score in scores:
            quiz = Quiz.query.get(score.quiz_id)
            if quiz:
                chapter = Chapter.query.get(quiz.chapter_id)
                subject = Subject.query.get(chapter.subject_id) if chapter else None
                
                result.append({
                    'id': score.id,
                    'quiz_id': score.quiz_id,
                    'quiz_remarks': quiz.remarks,
                    'chapter_name': chapter.name if chapter else None,
                    'subject_name': subject.name if subject else None,
                    'score': score.total_scored,
                    'total_questions': score.total_questions,
                    'percentage': round(score.total_scored / score.total_questions * 100, 2) if score.total_questions > 0 else 0,
                    'date': score.time_stamp_of_attempt.isoformat()
                })
        
        return jsonify(result), 200
    except Exception as e:
        print(f"Error in get_user_scores: {str(e)}")
        return jsonify({"error": "Failed to fetch scores"}), 500

@user_bp.route('/profile', methods=['GET'])
@jwt_required()
@cached_route(timeout=300)  # Cache for 5 minutes
def get_profile():
    # Get user ID from token (as string)
    current_user_id_str = get_jwt_identity()
    
    # Convert to integer for database lookup
    try:
        current_user_id = int(current_user_id_str)
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid user ID"}), 401
    
    try:
        # Get user
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Get scores and stats
        scores = Score.query.filter_by(user_id=current_user_id).all()
        total_quizzes = len(scores)
        total_questions = sum(score.total_questions for score in scores)
        total_correct = sum(score.total_scored for score in scores)
        avg_score = round(total_correct / total_questions * 100, 2) if total_questions > 0 else 0
        
        return jsonify({
            'id': user.id,
            'username': user.username,
            'full_name': user.full_name,
            'qualification': user.qualification,
            'dob': user.dob.isoformat() if user.dob else None,
            'stats': {
                'total_quizzes': total_quizzes,
                'total_questions': total_questions,
                'total_correct': total_correct,
                'avg_score': avg_score
            }
        }), 200
    except Exception as e:
        print(f"Error in get_profile: {str(e)}")
        return jsonify({"error": "Failed to fetch profile"}), 500

@user_bp.route('/subjects', methods=['GET'])
@jwt_required()
@cached_route(timeout=600)  # Cache for 10 minutes
def get_subjects():
    try:
        subjects = Subject.query.all()
        result = []
        
        for subject in subjects:
            result.append({
                'id': subject.id,
                'name': subject.name,
                'description': subject.description
            })
        
        return jsonify(result), 200
    except Exception as e:
        print(f"Error in get_subjects: {str(e)}")
        return jsonify({"error": "Failed to fetch subjects"}), 500

@user_bp.route('/chapters', methods=['GET'])
@jwt_required()
@cached_route(timeout=600)  # Cache for 10 minutes
def get_chapters():
    subject_id = request.args.get('subject_id', type=int)
    
    try:
        query = Chapter.query
        if subject_id:
            query = query.filter_by(subject_id=subject_id)
        
        chapters = query.all()
        result = []
        
        for chapter in chapters:
            result.append({
                'id': chapter.id,
                'name': chapter.name,
                'subject_id': chapter.subject_id,
                'description': chapter.description
            })
        
        return jsonify(result), 200
    except Exception as e:
        print(f"Error in get_chapters: {str(e)}")
        return jsonify({"error": "Failed to fetch chapters"}), 500

@user_bp.route('/dashboard/performance', methods=['GET'])
@jwt_required()
@cached_route(timeout=300)  # Cache for 5 minutes
def get_dashboard_performance():
    """Get formatted performance statistics for the dashboard"""
    # Get user ID from token (as string)
    current_user_id_str = get_jwt_identity()
    
    # Convert to integer for database lookup
    try:
        current_user_id = int(current_user_id_str)
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid user ID"}), 401
    
    try:
        # Check if user exists
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Get scores
        scores = Score.query.filter_by(user_id=current_user_id).all()
        
        # Calculate performance metrics with proper handling for zero/empty values
        total_quizzes = len(scores)
        
        # Initialize with default values
        avg_score = "0%"
        highest_score = "0%"
        
        if total_quizzes > 0:
            # Calculate average score
            total_questions = sum(score.total_questions for score in scores)
            total_correct = sum(score.total_scored for score in scores)
            
            if total_questions > 0:
                avg_score_value = round(total_correct / total_questions * 100, 1)
                avg_score = f"{avg_score_value}%"
            
            # Calculate highest score
            percentages = [
                (score.total_scored / score.total_questions * 100) 
                for score in scores 
                if score.total_questions > 0
            ]
            
            if percentages:
                highest_score_value = round(max(percentages), 1)
                highest_score = f"{highest_score_value}%"
        
        # Get recent attempts (limited to last 5)
        recent_attempts = []
        sorted_scores = sorted(scores, key=lambda x: x.time_stamp_of_attempt, reverse=True)[:5]
        
        for score in sorted_scores:
            quiz = Quiz.query.get(score.quiz_id)
            if quiz:
                chapter = Chapter.query.get(quiz.chapter_id)
                subject = Subject.query.get(chapter.subject_id) if chapter else None
                
                percentage = "0%"
                if score.total_questions > 0:
                    percentage = f"{round(score.total_scored / score.total_questions * 100, 1)}%"
                
                recent_attempts.append({
                    'id': score.id,
                    'title': f"{subject.name if subject else 'Unknown'}: {chapter.name if chapter else 'Unknown'}",
                    'date': score.time_stamp_of_attempt.strftime("%m/%d/%Y"),
                    'raw_date': score.time_stamp_of_attempt.isoformat(),
                    'score': f"{score.total_scored}/{score.total_questions}",
                    'percentage': percentage
                })
        
        return jsonify({
            'quizzes_taken': total_quizzes,
            'average_score': avg_score,
            'highest_score': highest_score,
            'recent_attempts': recent_attempts
        }), 200
    
    except Exception as e:
        print(f"Error in get_dashboard_performance: {str(e)}")
        return jsonify({"error": "Failed to fetch dashboard performance"}), 500 
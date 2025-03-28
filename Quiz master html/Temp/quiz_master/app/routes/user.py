from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from app.models.quiz import Quiz
from app.models.quiz_attempt import QuizAttempt
from app.models.question import Question
from app.models.chapter import Chapter
from app.models.subject import Subject
from app import db
from flask_login import login_required, current_user
from datetime import datetime
import json

user_bp = Blueprint('user', __name__, url_prefix='/user')

def calculate_average_score(attempts):
    """Helper function to calculate average score"""
    if not attempts:
        return 0.0
    total_score = 0
    for attempt in attempts:
        if attempt.completed:
            total_questions = attempt.total_questions or len(attempt.quiz.questions)
            if total_questions > 0:
                total_score += (attempt.score or 0) / total_questions * 100
    return total_score / len(attempts) if attempts else 0.0

@user_bp.route('/dashboard')
@login_required
def dashboard():
    # Get user's quiz attempts
    attempts = QuizAttempt.query.filter_by(user_id=current_user.id)\
        .order_by(QuizAttempt.start_time.desc()).all()
    
    # Calculate statistics
    total_attempts = len(attempts)
    completed_attempts = [a for a in attempts if a.completed]
    average_score = calculate_average_score(completed_attempts)
    
    # Convert attempts to JSON-serializable format
    attempts_json = [attempt.to_dict() for attempt in attempts]
    
    return render_template('user/dashboard.html',
                         attempts=attempts_json,
                         total_attempts=total_attempts,
                         average_score=average_score)

@user_bp.route('/quizzes')
@login_required
def available_quizzes():
    subject_id = request.args.get('subject_id', type=int)
    subjects = Subject.query.all()
    
    # Base query
    quiz_query = Quiz.query.join(Quiz.chapter)
    
    # Apply subject filter if provided
    if subject_id:
        quiz_query = quiz_query.filter(Chapter.subject_id == subject_id)
    
    # Get available quizzes
    quizzes = quiz_query.all()
    
    return render_template('user/available_quizzes.html', 
                         quizzes=quizzes, 
                         subjects=subjects,
                         selected_subject=subject_id)

@user_bp.route('/quiz/<int:quiz_id>')
@login_required
def start_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    
    # Check if user has an incomplete attempt
    existing_attempt = QuizAttempt.query.filter_by(
        user_id=current_user.id,
        quiz_id=quiz_id,
        completed=False
    ).first()
    
    if existing_attempt:
        return redirect(url_for('quiz.take_quiz', attempt_id=existing_attempt.id))
    
    # Create new attempt
    attempt = QuizAttempt(
        user_id=current_user.id,
        quiz_id=quiz_id,
        total_questions=len(quiz.questions),
        start_time=datetime.utcnow()
    )
    db.session.add(attempt)
    db.session.commit()
    
    return redirect(url_for('quiz.take_quiz', attempt_id=attempt.id))

@user_bp.route('/quiz/submit/<int:attempt_id>', methods=['POST'])
@login_required
def submit_quiz(attempt_id):
    attempt = QuizAttempt.query.get_or_404(attempt_id)
    
    if attempt.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if attempt.completed_at:
        return jsonify({'error': 'Quiz already submitted'}), 400
    
    answers = request.get_json()
    score = 0
    
    for question_id, answer in answers.items():
        question = Question.query.get(int(question_id))
        if question and int(answer) == question.correct_option:
            score += 1
    
    attempt.score = score
    attempt.completed_at = datetime.now()
    db.session.commit()
    
    return jsonify({
        'score': score,
        'total': attempt.total_questions,
        'redirect': url_for('user.quiz_result', attempt_id=attempt_id)
    })

@user_bp.route('/result/<int:attempt_id>')
@login_required
def quiz_result(attempt_id):
    attempt = QuizAttempt.query.get_or_404(attempt_id)
    
    if attempt.user_id != current_user.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('user.dashboard'))
    
    return render_template('user/quiz_result.html', attempt=attempt)

@user_bp.route('/history')
@login_required
def quiz_history():
    attempts = QuizAttempt.query.filter_by(user_id=current_user.id)\
        .order_by(QuizAttempt.start_time.desc()).all()
    subjects = Subject.query.all()
    
    attempts_json = [attempt.to_dict() for attempt in attempts]
    
    return render_template('user/quiz_history.html', 
                         attempts=attempts_json,
                         subjects=subjects) 
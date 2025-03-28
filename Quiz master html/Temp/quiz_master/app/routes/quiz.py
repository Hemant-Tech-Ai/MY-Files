from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.models import Quiz, Question, QuizAttempt, UserAnswer, Subject, Chapter

quiz_bp = Blueprint('quiz', __name__)

@quiz_bp.route('/subjects')
@login_required
def subject_list():
    subjects = Subject.query.all()
    return render_template('quiz/subject_list.html', subjects=subjects)

@quiz_bp.route('/chapters/<int:subject_id>')
@login_required
def chapter_list(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    chapters = Chapter.query.filter_by(subject_id=subject_id).all()
    return render_template('quiz/chapter_list.html', subject=subject, chapters=chapters)

@quiz_bp.route('/quiz/<int:quiz_id>/start')
@login_required
def start_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    
    # Check if user has an incomplete attempt
    existing_attempt = QuizAttempt.query.filter_by(
        user_id=current_user.id,
        quiz_id=quiz_id,
        end_time=None
    ).first()
    
    if existing_attempt:
        return redirect(url_for('quiz.continue_quiz', attempt_id=existing_attempt.id))
    
    # Create new attempt
    attempt = QuizAttempt(
        user_id=current_user.id,
        quiz_id=quiz_id,
        start_time=datetime.utcnow()
    )
    db.session.add(attempt)
    db.session.commit()
    
    return redirect(url_for('quiz.take_quiz', attempt_id=attempt.id))

@quiz_bp.route('/quiz/attempt/<int:attempt_id>')
@login_required
def take_quiz(attempt_id):
    attempt = QuizAttempt.query.get_or_404(attempt_id)
    
    if attempt.user_id != current_user.id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('quiz.subject_list'))
    
    if attempt.end_time:
        return redirect(url_for('quiz.quiz_result', attempt_id=attempt_id))
    
    return render_template('quiz/take_quiz.html', attempt=attempt, quiz=attempt.quiz)

@quiz_bp.route('/quiz/attempt/<int:attempt_id>/submit', methods=['POST'])
@login_required
def submit_quiz(attempt_id):
    attempt = QuizAttempt.query.get_or_404(attempt_id)
    
    if attempt.user_id != current_user.id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('quiz.subject_list'))
    
    if attempt.end_time:
        flash('This quiz has already been submitted', 'error')
        return redirect(url_for('quiz.quiz_result', attempt_id=attempt_id))
    
    score = 0
    for question in attempt.quiz.questions:
        answer = request.form.get(f'question_{question.id}')
        if answer:
            user_answer = UserAnswer(
                quiz_attempt_id=attempt_id,
                question_id=question.id,
                selected_option=answer,
                is_correct=(answer == question.correct_option)
            )
            if user_answer.is_correct:
                score += 1
            db.session.add(user_answer)
    
    attempt.end_time = datetime.utcnow()
    attempt.score = score
    
    try:
        db.session.commit()
        flash('Quiz submitted successfully!', 'success')
    except:
        db.session.rollback()
        flash('Error submitting quiz. Please try again.', 'error')
    
    return redirect(url_for('quiz.quiz_result', attempt_id=attempt_id))

@quiz_bp.route('/quiz/result/<int:attempt_id>')
@login_required
def quiz_result(attempt_id):
    attempt = QuizAttempt.query.get_or_404(attempt_id)
    
    if attempt.user_id != current_user.id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('quiz.subject_list'))
    
    return render_template('quiz/quiz_result.html', attempt=attempt) 
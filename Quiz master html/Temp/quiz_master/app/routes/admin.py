from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models.user import User
from app.models.subject import Subject
from app.models.chapter import Chapter
from app.models.quiz import Quiz
from app.models.quiz_attempt import QuizAttempt
from app.models.question import Question, QuestionOption
from app import db
from functools import wraps
from datetime import datetime

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Helper function to check if user is admin
def check_admin():
    return current_user.is_authenticated and current_user.is_admin

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    total_users = User.query.filter_by(role='user').count()
    total_subjects = Subject.query.count()
    total_quizzes = Quiz.query.count()
    total_attempts = QuizAttempt.query.count()
    
    recent_quizzes = Quiz.query.order_by(Quiz.created_at.desc()).limit(5).all()
    recent_attempts = QuizAttempt.query.order_by(QuizAttempt.started_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_subjects=total_subjects,
                         total_quizzes=total_quizzes,
                         total_attempts=total_attempts,
                         recent_quizzes=recent_quizzes,
                         recent_attempts=recent_attempts)

@admin_bp.route('/users')
@login_required
def manage_users():
    users = User.query.filter_by(role='user').all()
    return render_template('admin/users.html', users=users)

# Subject Management
@admin_bp.route('/subjects', methods=['GET', 'POST'])
@login_required
def manage_subjects():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        subject = Subject(name=name, description=description)
        db.session.add(subject)
        db.session.commit()
        flash('Subject added successfully!', 'success')
        
    subjects = Subject.query.all()
    return render_template('admin/subjects.html', subjects=subjects)

@admin_bp.route('/subjects/<int:subject_id>', methods=['PUT', 'DELETE'])
@login_required
def api_manage_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    
    if request.method == 'PUT':
        data = request.get_json()
        subject.name = data.get('name', subject.name)
        subject.description = data.get('description', subject.description)
        db.session.commit()
        return jsonify({'message': 'Subject updated successfully'})
        
    elif request.method == 'DELETE':
        db.session.delete(subject)
        db.session.commit()
        return jsonify({'message': 'Subject deleted successfully'})

# Chapter Management
@admin_bp.route('/chapters', methods=['GET', 'POST'])
@login_required
def manage_chapters():
    if request.method == 'POST':
        subject_id = request.form.get('subject_id')
        name = request.form.get('name')
        description = request.form.get('description')
        
        # Check for existing chapter
        existing = Chapter.query.filter_by(subject_id=subject_id, name=name).first()
        if existing:
            flash('A chapter with this name already exists for this subject.', 'danger')
            return redirect(url_for('admin.manage_chapters'))
        
        chapter = Chapter(
            subject_id=subject_id,
            name=name,
            description=description
        )
        try:
            db.session.add(chapter)
            db.session.commit()
            flash('Chapter added successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Error adding chapter. Please try again.', 'danger')
            
        return redirect(url_for('admin.manage_chapters'))

    subjects = Subject.query.all()
    chapters = Chapter.query.join(Subject).order_by(Subject.name, Chapter.name).all()
    return render_template('admin/chapters.html', subjects=subjects, chapters=chapters)

@admin_bp.route('/chapters/<int:chapter_id>', methods=['PUT', 'DELETE'])
@login_required
def manage_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    
    if request.method == 'DELETE':
        try:
            # Check if chapter has quizzes
            if chapter.quizzes:
                return jsonify({
                    'success': False,
                    'message': 'Cannot delete chapter with existing quizzes'
                })
            
            db.session.delete(chapter)
            db.session.commit()
            return jsonify({
                'success': True,
                'message': 'Chapter deleted successfully'
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'message': str(e)
            })
    
    elif request.method == 'PUT':
        data = request.get_json()
        try:
            # Check for duplicate name
            existing = Chapter.query.filter(
                Chapter.subject_id == data['subject_id'],
                Chapter.name == data['name'],
                Chapter.id != chapter_id
            ).first()
            
            if existing:
                return jsonify({
                    'success': False,
                    'message': 'A chapter with this name already exists for this subject'
                })
            
            chapter.subject_id = data['subject_id']
            chapter.name = data['name']
            chapter.description = data['description']
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Chapter updated successfully',
                'chapter': {
                    'id': chapter.id,
                    'name': chapter.name,
                    'description': chapter.description,
                    'subject_name': chapter.subject.name
                }
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'message': str(e)
            })

# Quiz Management
@admin_bp.route('/quizzes', methods=['GET', 'POST'])
@login_required
def manage_quizzes():
    if request.method == 'POST':
        chapter_id = request.form.get('chapter_id')
        date_of_quiz = datetime.strptime(request.form.get('date_of_quiz'), '%Y-%m-%d')
        time_duration = int(request.form.get('time_duration'))
        remarks = request.form.get('remarks')

        quiz = Quiz(
            chapter_id=chapter_id,
            date_of_quiz=date_of_quiz,
            time_duration=time_duration,
            remarks=remarks
        )
        db.session.add(quiz)
        db.session.commit()
        flash('Quiz created successfully!', 'success')
        return redirect(url_for('admin.manage_questions', quiz_id=quiz.id))

    chapters = Chapter.query.all()
    quizzes = Quiz.query.order_by(Quiz.created_at.desc()).all()
    return render_template('admin/quizzes.html', quizzes=quizzes, chapters=chapters)

# Question Management
@admin_bp.route('/quizzes/<int:quiz_id>/questions')
@login_required
def manage_questions(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    return render_template('admin/questions.html', quiz=quiz, questions=questions)

@admin_bp.route('/quizzes/<int:quiz_id>/questions/add', methods=['GET', 'POST'])
@login_required
def add_question(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    
    if request.method == 'POST':
        question = Question(
            quiz_id=quiz_id,
            question_statement=request.form.get('question_statement'),
            marks=int(request.form.get('marks', 1))
        )
        db.session.add(question)
        db.session.flush()  # Get the question ID

        # Handle options
        options = request.form.getlist('options[]')
        correct_option = int(request.form.get('correct_option', 0))
        
        for i, option_text in enumerate(options):
            option = QuestionOption(
                question_id=question.id,
                option_text=option_text,
                is_correct=(i == correct_option)
            )
            db.session.add(option)
        
        db.session.commit()
        flash('Question added successfully!', 'success')
        return redirect(url_for('admin.manage_questions', quiz_id=quiz_id))
    
    return render_template('admin/add_question.html', quiz=quiz)

@admin_bp.route('/questions/<int:question_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def manage_question(question_id):
    question = Question.query.get_or_404(question_id)
    
    if request.method == 'DELETE':
        try:
            db.session.delete(question)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Question deleted successfully'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)})
            
    elif request.method == 'PUT':
        data = request.get_json()
        try:
            question.question_statement = data.get('question_statement')
            question.marks = data.get('marks', 1)
            
            # Update options
            # First, delete existing options
            QuestionOption.query.filter_by(question_id=question.id).delete()
            
            # Add new options
            options = data.get('options', [])
            correct_option = data.get('correct_option', 0)
            
            for i, option_text in enumerate(options):
                option = QuestionOption(
                    question_id=question.id,
                    option_text=option_text,
                    is_correct=(i == correct_option)
                )
                db.session.add(option)
                
            db.session.commit()
            return jsonify({
                'success': True,
                'message': 'Question updated successfully',
                'question': {
                    'id': question.id,
                    'question_statement': question.question_statement,
                    'marks': question.marks,
                    'options': [{'text': opt.option_text, 'is_correct': opt.is_correct} 
                              for opt in question.options]
                }
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)})
    
    return jsonify({
        'id': question.id,
        'question_statement': question.question_statement,
        'marks': question.marks,
        'options': [{'text': opt.option_text, 'is_correct': opt.is_correct} 
                   for opt in question.options]
    })

@admin_bp.route('/api/users/<int:user_id>', methods=['GET', 'DELETE'])
@login_required
def api_manage_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if request.method == 'GET':
        # Calculate statistics
        total_attempts = len(user.quiz_attempts)
        average_score = 0
        if total_attempts > 0:
            average_score = sum(attempt.score / attempt.total_questions * 100 
                              for attempt in user.quiz_attempts) / total_attempts
        
        return jsonify({
            'id': user.id,
            'full_name': user.full_name,
            'email': user.email,
            'qualification': user.qualification,
            'dob': user.dob.strftime('%Y-%m-%d') if user.dob else 'Not provided',
            'total_attempts': total_attempts,
            'average_score': round(average_score, 2)
        })
        
    elif request.method == 'DELETE':
        if user.role == 'admin':
            return jsonify({'error': 'Cannot delete admin user'}), 403
        
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted successfully'})

@admin_bp.route('/admin/subject/create', methods=['GET', 'POST'])
@login_required
def create_subject():
    if not check_admin():
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        subject = Subject(name=name, description=description)
        db.session.add(subject)
        try:
            db.session.commit()
            flash('Subject created successfully!', 'success')
            return redirect(url_for('admin.manage_subjects'))
        except:
            db.session.rollback()
            flash('Error creating subject. Please try again.', 'error')
    
    return render_template('admin/create_subject.html')

@admin_bp.route('/admin/chapter/create/<int:subject_id>', methods=['GET', 'POST'])
@login_required
def create_chapter(subject_id):
    if not check_admin():
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.index'))
        
    subject = Subject.query.get_or_404(subject_id)
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        chapter = Chapter(name=name, description=description, subject_id=subject_id)
        db.session.add(chapter)
        try:
            db.session.commit()
            flash('Chapter created successfully!', 'success')
            return redirect(url_for('admin.manage_chapters', subject_id=subject_id))
        except:
            db.session.rollback()
            flash('Error creating chapter. Please try again.', 'error')
    
    return render_template('admin/create_chapter.html', subject=subject)

@admin_bp.route('/admin/quiz/create/<int:chapter_id>', methods=['GET', 'POST'])
@login_required
def create_quiz(chapter_id):
    if not check_admin():
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.index'))
        
    chapter = Chapter.query.get_or_404(chapter_id)
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        duration = request.form.get('duration_minutes', type=int)
        
        quiz = Quiz(
            title=title,
            description=description,
            duration_minutes=duration,
            chapter_id=chapter_id
        )
        db.session.add(quiz)
        try:
            db.session.commit()
            flash('Quiz created successfully!', 'success')
            return redirect(url_for('admin.manage_quizzes', chapter_id=chapter_id))
        except:
            db.session.rollback()
            flash('Error creating quiz. Please try again.', 'error')
    
    return render_template('admin/create_quiz.html', chapter=chapter) 
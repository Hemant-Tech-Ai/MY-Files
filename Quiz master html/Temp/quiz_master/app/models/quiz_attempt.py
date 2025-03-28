from datetime import datetime
from app import db

class QuizAttempt(db.Model):
    __tablename__ = 'quiz_attempt'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    score = db.Column(db.Float, default=0.0)
    completed = db.Column(db.Boolean, default=False)
    total_questions = db.Column(db.Integer)
    completed_at = db.Column(db.DateTime)
    
    # Relationships
    user = db.relationship('User', back_populates='quiz_attempts')
    quiz = db.relationship('Quiz', back_populates='attempts')
    user_answers = db.relationship('UserAnswer', back_populates='quiz_attempt', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'quiz_id': self.quiz_id,
            'quiz_title': self.quiz.title,
            'chapter_name': self.quiz.chapter.name,
            'subject_name': self.quiz.chapter.subject.name,
            'start_time': self.start_time.strftime('%Y-%m-%d %H:%M:%S') if self.start_time else None,
            'end_time': self.end_time.strftime('%Y-%m-%d %H:%M:%S') if self.end_time else None,
            'completed_at': self.completed_at.strftime('%Y-%m-%d %H:%M:%S') if self.completed_at else None,
            'score': self.score,
            'completed': self.completed,
            'total_questions': self.total_questions or len(self.quiz.questions),
            'correct_answers': len([a for a in self.user_answers if a.is_correct])
        }

class UserAnswer(db.Model):
    __tablename__ = 'user_answer'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    quiz_attempt_id = db.Column(db.Integer, db.ForeignKey('quiz_attempt.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    selected_answer = db.Column(db.String(500))
    is_correct = db.Column(db.Boolean)
    points = db.Column(db.Float)
    answered_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with fully qualified path
    question = db.relationship('app.models.question.Question', lazy=True)
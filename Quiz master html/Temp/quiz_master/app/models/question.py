from app import db
from datetime import datetime

class Question(db.Model):
    __tablename__ = 'question'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(200), nullable=False)
    option_b = db.Column(db.String(200), nullable=False)
    option_c = db.Column(db.String(200), nullable=False)
    option_d = db.Column(db.String(200), nullable=False)
    correct_option = db.Column(db.String(1), nullable=False)  # 'A', 'B', 'C', or 'D'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    points = db.Column(db.Float, default=1.0)
    explanation = db.Column(db.Text)
    
    # Relationships
    quiz = db.relationship('Quiz', back_populates='questions')
    user_answers = db.relationship('UserAnswer', back_populates='question')

class QuestionOption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    option_text = db.Column(db.String(200), nullable=False)
    is_correct = db.Column(db.Boolean, default=False) 
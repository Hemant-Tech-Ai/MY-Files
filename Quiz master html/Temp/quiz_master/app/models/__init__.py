# This file can be empty 

from app import db

# Clear all previous imports and define them properly
from .user import User
from .subject import Subject
from .chapter import Chapter
from .quiz import Quiz
from .question import Question
from .quiz_attempt import QuizAttempt
from .user_answer import UserAnswer

# Define what should be available when importing from app.models
__all__ = [
    'User',
    'Subject',
    'Chapter',
    'Quiz',
    'Question',
    'QuizAttempt',
    'UserAnswer'
]

# Initialize model relationships
def init_models():
    # This ensures all models are properly initialized
    for model in [User, Subject, Chapter, Quiz, Question, QuizAttempt, UserAnswer]:
        if hasattr(model, '__table__'):
            model.__table__.info = {'bind_key': None} 
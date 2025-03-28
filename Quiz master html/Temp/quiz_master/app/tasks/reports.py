from app.tasks import celery
from app.models.user import User
from app.models.quiz_attempt import QuizAttempt
from app.models.quiz import Quiz
from app import db, mail
from flask_mail import Message
from datetime import datetime, timedelta
import pandas as pd
from io import BytesIO
import matplotlib.pyplot as plt
from weasyprint import HTML
import jinja2

@celery.task
def generate_monthly_reports():
    """Generate and send monthly activity reports for all users"""
    users = User.query.filter_by(role='user').all()
    
    for user in users:
        generate_user_report.delay(user.id)

@celery.task
def generate_user_report(user_id):
    """Generate and send monthly report for a specific user"""
    user = User.query.get(user_id)
    
    # Get last month's attempts
    last_month = datetime.now() - timedelta(days=30)
    attempts = QuizAttempt.query.filter(
        QuizAttempt.user_id == user.id,
        QuizAttempt.started_at > last_month
    ).all()
    
    # Calculate statistics
    total_attempts = len(attempts)
    if total_attempts > 0:
        average_score = sum(a.score/a.total_questions for a in attempts) / total_attempts * 100
        subjects_attempted = len(set(a.quiz.chapter.subject.id for a in attempts))
        best_score = max(a.score/a.total_questions for a in attempts) * 100
    else:
        average_score = 0
        subjects_attempted = 0
        best_score = 0
    
    # Generate HTML report
    template = jinja2.Template("""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; }
            .header { text-align: center; padding: 20px; }
            .stats { display: flex; justify-content: space-around; margin: 20px 0; }
            .stat-box { text-align: center; padding: 10px; border: 1px solid #ddd; }
            .chart { text-align: center; margin: 20px 0; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Monthly Activity Report</h1>
            <p>{{ user.full_name }} - {{ month_year }}</p>
        </div>
        
        <div class="stats">
            <div class="stat-box">
                <h3>Total Quizzes</h3>
                <p>{{ total_attempts }}</p>
            </div>
            <div class="stat-box">
                <h3>Average Score</h3>
                <p>{{ "%.1f"|format(average_score) }}%</p>
            </div>
            <div class="stat-box">
                <h3>Subjects Covered</h3>
                <p>{{ subjects_attempted }}</p>
            </div>
            <div class="stat-box">
                <h3>Best Score</h3>
                <p>{{ "%.1f"|format(best_score) }}%</p>
            </div>
        </div>
        
        <div class="chart">
            <img src="data:image/png;base64,{{ performance_chart }}" />
        </div>
        
        <div class="recent-attempts">
            <h2>Recent Attempts</h2>
            <table border="1" style="width: 100%; border-collapse: collapse;">
                <tr>
                    <th>Date</th>
                    <th>Subject</th>
                    <th>Chapter</th>
                    <th>Score</th>
                </tr>
                {% for attempt in attempts %}
                <tr>
                    <td>{{ attempt.started_at.strftime('%Y-%m-%d') }}</td>
                    <td>{{ attempt.quiz.chapter.subject.name }}</td>
                    <td>{{ attempt.quiz.chapter.name }}</td>
                    <td>{{ "%.1f"|format(attempt.score/attempt.total_questions * 100) }}%</td>
                </tr>
                {% endfor %}
            </table>
        </div>
    </body>
    </html>
    """)
    
    # Generate performance chart
    plt.figure(figsize=(10, 6))
    dates = [a.started_at for a in attempts]
    scores = [a.score/a.total_questions * 100 for a in attempts]
    plt.plot(dates, scores, marker='o')
    plt.title('Performance Trend')
    plt.xlabel('Date')
    plt.ylabel('Score (%)')
    plt.grid(True)
    
    # Save chart to BytesIO
    chart_io = BytesIO()
    plt.savefig(chart_io, format='png')
    plt.close()
    
    # Convert chart to base64
    import base64
    chart_base64 = base64.b64encode(chart_io.getvalue()).decode()
    
    # Render HTML
    html_content = template.render(
        user=user,
        month_year=datetime.now().strftime('%B %Y'),
        total_attempts=total_attempts,
        average_score=average_score,
        subjects_attempted=subjects_attempted,
        best_score=best_score,
        performance_chart=chart_base64,
        attempts=attempts
    )
    
    # Generate PDF
    pdf = HTML(string=html_content).write_pdf()
    
    # Send email with PDF attachment
    msg = Message(
        f'Quiz Master - Monthly Activity Report - {datetime.now().strftime("%B %Y")}',
        recipients=[user.email]
    )
    
    msg.html = f"""
    <h2>Hello {user.full_name}!</h2>
    <p>Please find attached your monthly activity report for {datetime.now().strftime('%B %Y')}.</p>
    <p>Keep up the good work!</p>
    """
    
    msg.attach(
        f"report_{datetime.now().strftime('%Y_%m')}.pdf",
        "application/pdf",
        pdf
    )
    
    mail.send(msg) 
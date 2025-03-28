"""
Test script for the Quiz Master scheduler module.
This script tests if the scheduler is working correctly by:
1. Verifying scheduler initialization
2. Checking if jobs are scheduled correctly
3. Testing the functionality of each scheduled job
4. Mocking email sending to verify the process
"""
import unittest
from unittest.mock import patch, MagicMock, call
import os
import sys
import logging
from datetime import datetime, timedelta
from flask import Flask

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import the scheduler module
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
from app.jobs.scheduler import (
    init_scheduler, 
    scheduler, 
    send_daily_reminders,
    send_monthly_reports,
    send_reminder_notification,
    generate_monthly_report,
    send_email
)

class TestScheduler(unittest.TestCase):
    """Test cases for the scheduler module"""
    
    def setUp(self):
        """Set up test environment"""
        # Create a test Flask app
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        
        # Configure app context for testing
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Reset scheduler initialization flag for testing
        from app.jobs.scheduler import _scheduler_initialized
        import app.jobs.scheduler
        app.jobs.scheduler._scheduler_initialized = False
        
        logger.info("Test setup complete")
    
    def tearDown(self):
        """Clean up after tests"""
        self.app_context.pop()
        logger.info("Test teardown complete")
    
    def test_scheduler_initialization(self):
        """Test that the scheduler initializes correctly"""
        with patch('app.jobs.scheduler.scheduler.add_job') as mock_add_job:
            with patch('app.jobs.scheduler.scheduler.start') as mock_start:
                # Initialize the scheduler
                init_scheduler(self.app)
                
                # Check if scheduler was initialized
                from app.jobs.scheduler import _scheduler_initialized
                self.assertTrue(_scheduler_initialized)
                
                # Check if jobs were added
                self.assertEqual(mock_add_job.call_count, 2)
                
                # Check if scheduler was started
                mock_start.assert_called_once()
                
                logger.info("Scheduler initialization test passed")
    
    def test_scheduler_initialization_once(self):
        """Test that the scheduler is only initialized once"""
        with patch('app.jobs.scheduler.scheduler.add_job') as mock_add_job:
            # Initialize twice
            init_scheduler(self.app)
            init_scheduler(self.app)
            
            # Check that add_job was only called for the first initialization
            self.assertEqual(mock_add_job.call_count, 2)
            
            logger.info("Scheduler single initialization test passed")
    
    def test_daily_reminder_job_scheduling(self):
        """Test that the daily reminder job is scheduled correctly"""
        with patch('app.jobs.scheduler.scheduler.add_job') as mock_add_job:
            # Initialize the scheduler
            init_scheduler(self.app)
            
            # Check the first call to add_job (daily reminders)
            args, kwargs = mock_add_job.call_args_list[0]
            
            # Verify job ID and function
            self.assertEqual(kwargs['id'], 'send_daily_reminders')
            self.assertEqual(kwargs['func'], send_daily_reminders)
            
            # Verify schedule (18:45 UTC daily)
            self.assertEqual(kwargs['trigger'], 'cron')
            self.assertEqual(kwargs['hour'], 18)
            self.assertEqual(kwargs['minute'], 45)
            self.assertEqual(kwargs['second'], 0)
            self.assertEqual(kwargs['timezone'], 'UTC')
            
            logger.info("Daily reminder job scheduling test passed")
    
    def test_monthly_report_job_scheduling(self):
        """Test that the monthly report job is scheduled correctly"""
        with patch('app.jobs.scheduler.scheduler.add_job') as mock_add_job:
            # Initialize the scheduler
            init_scheduler(self.app)
            
            # Check the second call to add_job (monthly reports)
            args, kwargs = mock_add_job.call_args_list[1]
            
            # Verify job ID and function
            self.assertEqual(kwargs['id'], 'send_monthly_reports')
            self.assertEqual(kwargs['func'], send_monthly_reports)
            
            # Verify schedule (15th of each month at 18:45 UTC)
            self.assertEqual(kwargs['trigger'], 'cron')
            self.assertEqual(kwargs['day'], 15)
            self.assertEqual(kwargs['hour'], 18)
            self.assertEqual(kwargs['minute'], 45)
            self.assertEqual(kwargs['second'], 0)
            self.assertEqual(kwargs['timezone'], 'UTC')
            
            logger.info("Monthly report job scheduling test passed")
    
    @patch('app.jobs.scheduler.User')
    @patch('app.jobs.scheduler.QuizAssignment')
    @patch('app.jobs.scheduler.Quiz')
    @patch('app.jobs.scheduler.send_reminder_notification')
    def test_send_daily_reminders(self, mock_send_reminder, mock_quiz, mock_assignment, mock_user):
        """Test the daily reminders functionality"""
        # Setup mock users
        user1 = MagicMock()
        user1.id = 1
        user1.username = 'user1'
        user1.is_admin = False
        
        user2 = MagicMock()
        user2.id = 2
        user2.username = 'user2'
        user2.is_admin = False
        
        mock_user.query.filter_by.return_value.all.return_value = [user1, user2]
        
        # Setup mock quiz assignments
        mock_quiz1 = MagicMock()
        mock_assignment.query.join.return_value.filter.return_value.all.side_effect = [
            [mock_quiz1],  # user1 has an upcoming quiz
            []             # user2 has no upcoming quizzes
        ]
        
        # Store app in scheduler for context
        scheduler.app = self.app
        
        # Call the function
        send_daily_reminders()
        
        # Verify that send_reminder_notification was called for user1 only
        mock_send_reminder.assert_called_once_with(user1, [mock_quiz1])
        
        logger.info("Daily reminders functionality test passed")
    
    @patch('app.jobs.scheduler.User')
    @patch('app.jobs.scheduler.generate_monthly_report')
    def test_send_monthly_reports(self, mock_generate_report, mock_user):
        """Test the monthly reports functionality"""
        # Setup mock users
        user1 = MagicMock()
        user1.id = 1
        user1.username = 'user1'
        user1.is_admin = False
        
        mock_user.query.filter_by.return_value.all.return_value = [user1]
        
        # Setup mock report generation results
        mock_generate_report.side_effect = [True, True]  # Both reports successful
        
        # Store app in scheduler for context
        scheduler.app = self.app
        
        # Call the function
        send_monthly_reports()
        
        # Verify that generate_monthly_report was called twice (prev month and current month)
        self.assertEqual(mock_generate_report.call_count, 2)
        
        # Check the arguments for the first call (previous month)
        args1, kwargs1 = mock_generate_report.call_args_list[0]
        self.assertEqual(kwargs1['user'], user1)
        
        # Check the arguments for the second call (current month)
        args2, kwargs2 = mock_generate_report.call_args_list[1]
        self.assertEqual(kwargs2['user'], user1)
        
        logger.info("Monthly reports functionality test passed")
    
    @patch('app.jobs.scheduler.Quiz')
    @patch('app.jobs.scheduler.Chapter')
    @patch('app.jobs.scheduler.Subject')
    @patch('app.jobs.scheduler.render_template')
    @patch('app.jobs.scheduler.send_email')
    def test_send_reminder_notification(self, mock_send_email, mock_render, mock_subject, mock_chapter, mock_quiz):
        """Test the reminder notification functionality"""
        # Setup mocks
        user = MagicMock()
        user.username = 'testuser'
        
        quiz = MagicMock()
        quiz.quiz_id = 1
        
        mock_quiz_obj = MagicMock()
        mock_quiz_obj.chapter_id = 1
        mock_quiz.query.get.return_value = mock_quiz_obj
        
        mock_chapter_obj = MagicMock()
        mock_chapter_obj.subject_id = 1
        mock_chapter.query.get.return_value = mock_chapter_obj
        
        mock_subject_obj = MagicMock()
        mock_subject_obj.name = 'Test Subject'
        mock_subject.query.get.return_value = mock_subject_obj
        
        mock_render.return_value = '<html>Test Email</html>'
        
        # Store app in scheduler for context
        scheduler.app = self.app
        
        # Call the function
        send_reminder_notification(user, [quiz])
        
        # Verify that send_email was called with correct parameters
        mock_send_email.assert_called_once()
        args, kwargs = mock_send_email.call_args
        self.assertEqual(args[0], 'testuser')
        self.assertEqual(args[1], 'Upcoming Quiz Reminder')
        self.assertEqual(args[2], '<html>Test Email</html>')
        self.assertTrue(kwargs['is_html'])
        
        logger.info("Reminder notification functionality test passed")
    
    @patch('app.jobs.scheduler.Score')
    @patch('app.jobs.scheduler.Quiz')
    @patch('app.jobs.scheduler.Chapter')
    @patch('app.jobs.scheduler.Subject')
    @patch('app.jobs.scheduler.render_template')
    @patch('app.jobs.scheduler.send_email')
    def test_generate_monthly_report(self, mock_send_email, mock_render, mock_subject, mock_chapter, mock_quiz, mock_score):
        """Test the monthly report generation functionality"""
        # Setup mocks
        user = MagicMock()
        user.id = 1
        user.username = 'testuser'
        
        # Create mock scores
        score1 = MagicMock()
        score1.quiz_id = 1
        score1.total_scored = 8
        score1.total_questions = 10
        score1.time_stamp_of_attempt = datetime.now()
        
        mock_score.query.filter.return_value.all.return_value = [score1]
        
        # Setup quiz, chapter, subject mocks
        mock_quiz_obj = MagicMock()
        mock_quiz_obj.chapter_id = 1
        mock_quiz_obj.remarks = 'Test Quiz'
        mock_quiz.query.get.return_value = mock_quiz_obj
        
        mock_chapter_obj = MagicMock()
        mock_chapter_obj.subject_id = 1
        mock_chapter_obj.name = 'Test Chapter'
        mock_chapter.query.get.return_value = mock_chapter_obj
        
        mock_subject_obj = MagicMock()
        mock_subject_obj.name = 'Test Subject'
        mock_subject.query.get.return_value = mock_subject_obj
        
        mock_render.return_value = '<html>Test Report</html>'
        
        # Store app in scheduler for context
        scheduler.app = self.app
        
        # Call the function
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()
        result = generate_monthly_report(user, start_date, end_date, 'Test Month')
        
        # Verify the result
        self.assertTrue(result)
        
        # Verify that send_email was called with correct parameters
        mock_send_email.assert_called_once()
        args, kwargs = mock_send_email.call_args
        self.assertEqual(args[0], 'testuser')
        self.assertEqual(args[1], 'Quiz Master - Monthly Report for Test Month')
        self.assertEqual(args[2], '<html>Test Report</html>')
        self.assertTrue(kwargs['is_html'])
        
        logger.info("Monthly report generation test passed")
    
    @patch('app.jobs.scheduler.smtplib.SMTP')
    @patch('app.jobs.scheduler.os.getenv')
    def test_send_email(self, mock_getenv, mock_smtp):
        """Test the email sending functionality"""
        # Setup environment variable mocks
        mock_getenv.side_effect = lambda key, default=None: {
            'SMTP_SERVER': 'smtp.test.com',
            'SMTP_PORT': '587',
            'SMTP_USERNAME': 'testuser',
            'SMTP_PASSWORD': 'testpass',
            'quizmaster@example.com': 'test@example.com'
        }.get(key, default)
        
        # Setup SMTP mock
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        # Call the function
        send_email('recipient@example.com', 'Test Subject', 'Test Body', False)
        
        # Verify SMTP interactions
        mock_smtp.assert_called_once_with('smtp.test.com', 587)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with('testuser', 'testpass')
        mock_server.send_message.assert_called_once()
        mock_server.quit.assert_called_once()
        
        logger.info("Email sending test passed")

    @patch('app.jobs.scheduler.os.getenv')
    def test_send_email_missing_credentials(self, mock_getenv):
        """Test email sending with missing credentials"""
        # Setup environment variable mocks to return empty credentials
        mock_getenv.side_effect = lambda key, default=None: {
            'SMTP_SERVER': 'smtp.test.com',
            'SMTP_PORT': '587',
            'SMTP_USERNAME': '',  # Empty username
            'SMTP_PASSWORD': '',  # Empty password
            'quizmaster@example.com': 'test@example.com'
        }.get(key, default)
        
        # Call the function with missing credentials
        with patch('app.jobs.scheduler.logging.warning') as mock_warning:
            send_email('recipient@example.com', 'Test Subject', 'Test Body', False)
            
            # Verify warning was logged
            mock_warning.assert_called_once()
            
        logger.info("Email missing credentials test passed")

def run_tests():
    """Run the test suite"""
    unittest.main()

if __name__ == '__main__':
    run_tests() 
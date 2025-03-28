"""
Manual test script for the Quiz Master scheduler module.
This script allows you to manually trigger the scheduled jobs to verify they work correctly.
"""
import os
import sys
import logging
from flask import Flask
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add parent directory to path to import scheduler
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

def create_app():
    """Create a Flask app for testing"""
    app = Flask(__name__)
    app.config['TESTING'] = True
    
    # Configure email settings for testing
    # You can set these environment variables before running the script
    # or modify the values here for testing
    os.environ.setdefault('SMTP_SERVER', 'smtp.gmail.com')
    os.environ.setdefault('SMTP_PORT', '587')
    os.environ.setdefault('SMTP_USERNAME', '')  # Add your test email username
    os.environ.setdefault('SMTP_PASSWORD', '')  # Add your test email password
    
    return app

def init_scheduler_for_test(app):
    """Initialize the scheduler with the Flask app"""
    from app.jobs.scheduler import init_scheduler, scheduler
    
    # Initialize the scheduler
    init_scheduler(app)
    
    # Print scheduler info
    logger.info(f"Scheduler initialized: {scheduler.running}")
    logger.info(f"Scheduler jobs: {[job.id for job in scheduler.get_jobs()]}")
    
    # Print job details
    for job in scheduler.get_jobs():
        logger.info(f"Job ID: {job.id}")
        logger.info(f"Job Function: {job.func}")
        logger.info(f"Job Trigger: {job.trigger}")
        logger.info(f"Next Run Time: {job.next_run_time}")
        logger.info("---")
    
    return scheduler

def run_daily_reminders(app):
    """Manually run the daily reminders job"""
    from app.jobs.scheduler import send_daily_reminders
    
    logger.info("Manually triggering daily reminders job...")
    with app.app_context():
        send_daily_reminders()
    logger.info("Daily reminders job completed")

def run_monthly_reports(app):
    """Manually run the monthly reports job"""
    from app.jobs.scheduler import send_monthly_reports
    
    logger.info("Manually triggering monthly reports job...")
    with app.app_context():
        send_monthly_reports()
    logger.info("Monthly reports job completed")

def main():
    """Main function to run the manual test"""
    parser = argparse.ArgumentParser(description='Manually test the scheduler')
    parser.add_argument('--job', choices=['daily', 'monthly', 'info'], 
                        help='Job to run (daily reminders, monthly reports, or just show info)')
    
    args = parser.parse_args()
    
    # Create Flask app
    app = create_app()
    
    # Initialize scheduler
    scheduler = init_scheduler_for_test(app)
    
    # Run the specified job
    if args.job == 'daily':
        run_daily_reminders(app)
    elif args.job == 'monthly':
        run_monthly_reports(app)
    elif args.job == 'info' or args.job is None:
        logger.info("Showing scheduler information only")
    
    # Stop the scheduler
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler shutdown")

if __name__ == '__main__':
    main() 
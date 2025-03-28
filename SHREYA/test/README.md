# Quiz Master Scheduler Tests

This directory contains test scripts for verifying the functionality of the Quiz Master scheduler module.

## Test Files

1. `test_scheduler.py` - Automated unit tests for the scheduler module
2. `manual_test_scheduler.py` - Script for manually triggering scheduler jobs

## Running Automated Tests

The automated tests use Python's unittest framework and mock objects to test the scheduler functionality without actually sending emails or requiring a database connection.

To run the automated tests:

```bash
python -m test.test_scheduler
```

These tests verify:
- Scheduler initialization
- Job scheduling (daily reminders at 18:45 UTC, monthly reports on the 15th at 18:45 UTC)
- Daily reminder functionality
- Monthly report functionality
- Email sending capability

## Manual Testing

The manual test script allows you to trigger the scheduler jobs directly to verify they work in a real environment.

### Prerequisites

Before running manual tests:

1. Make sure you have set up the database with test data
2. Configure email settings in the script or set environment variables:
   - `SMTP_SERVER` (default: smtp.gmail.com)
   - `SMTP_PORT` (default: 587)
   - `SMTP_USERNAME` (your email username)
   - `SMTP_PASSWORD` (your email password)

### Usage

To run the manual test script:

```bash
# Show scheduler information
python -m test.manual_test_scheduler --job info

# Trigger daily reminders job
python -m test.manual_test_scheduler --job daily

# Trigger monthly reports job
python -m test.manual_test_scheduler --job monthly
```

## Scheduler Details

The scheduler is configured to run two jobs:

1. **Daily Reminders** - Runs every day at 18:45 UTC
   - Sends email reminders to users about quizzes scheduled for the next day

2. **Monthly Reports** - Runs on the 15th of each month at 18:45 UTC
   - Generates and sends performance reports for the previous month and current month (up to the current date)

## Troubleshooting

If you encounter issues with the tests:

1. **Import errors**: Make sure you're running the tests from the project root directory
2. **Email errors**: Check your SMTP settings and credentials
3. **Database errors**: Ensure your database is properly set up with test data
4. **Flask context errors**: The tests create a Flask app context, but it might not have all the configurations of your actual app

For more detailed logging, you can modify the logging level in the test scripts. 
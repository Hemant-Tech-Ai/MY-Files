from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, EmailStr
import logging
from typing import Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from ..config import settings

router = APIRouter(prefix="/contact", tags=["contact"])

# Create a logger
logger = logging.getLogger(__name__)

class ContactMessage(BaseModel):
    name: str
    email: EmailStr
    subject: str
    message: str

async def send_email_async(message_data: ContactMessage):
    """
    Background task to send an email
    """
    try:
        # This is a placeholder for actual email sending logic
        # In a real application, you would use SMTP or an email service API
        
        # Example SMTP implementation (commented out)
        '''
        msg = MIMEMultipart()
        msg['From'] = settings.EMAIL_FROM
        msg['To'] = settings.EMAIL_TO
        msg['Subject'] = f"Portfolio Contact: {message_data.subject}"
        
        body = f"""
        Name: {message_data.name}
        Email: {message_data.email}
        
        Message:
        {message_data.message}
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.send_message(msg)
        '''
        
        # For now, just log the message
        logger.info(f"Contact form submission from {message_data.name} <{message_data.email}>")
        logger.info(f"Subject: {message_data.subject}")
        logger.info(f"Message: {message_data.message}")
        
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        raise

@router.post("/", status_code=201)
async def send_contact_message(message: ContactMessage, background_tasks: BackgroundTasks):
    """
    Endpoint to handle contact form submissions
    """
    try:
        # Add email sending as a background task
        background_tasks.add_task(send_email_async, message)
        
        return {
            "status": "success",
            "message": "Your message has been received. We'll get back to you soon!"
        }
    except Exception as e:
        logger.error(f"Error processing contact form: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to process your message. Please try again later."
        ) 
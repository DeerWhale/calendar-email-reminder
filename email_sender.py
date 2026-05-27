"""Email sending functionality using Gmail SMTP."""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict

logger = logging.getLogger(__name__)


def send_reminder_email(
    event: Dict,
    sender_email: str,
    sender_password: str,
    recipient_email: str
) -> bool:
    """
    Send a reminder email for a calendar event.
    
    Args:
        event: Dictionary containing event details
        sender_email: Gmail address to send from
        sender_password: Gmail app password
        recipient_email: Email address to send to
    
    Returns:
        True if email sent successfully, False otherwise
    """
    try:
        # Create message
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = recipient_email
        message['Subject'] = f"⏰ Reminder: {event['summary']} in minutes!"
        
        # Format email body
        from calendar_auth import format_event_time
        
        body = f"""
Hello!

This is a reminder for your upcoming event:

📅 Event: {event['summary']}
🕐 Start Time: {format_event_time(event['start'])}

This event will start in approximately 10 minutes.

---
Automated reminder from Calendar Email Reminder
        """
        
        message.attach(MIMEText(body, 'plain'))
        
        # Connect to Gmail SMTP server
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(message)

        logger.info(f"Email sent successfully for event: {event['summary']}")
        return True
    
    except Exception as e:
        logger.error(f"Failed to send email for event '{event['summary']}': {e}")
        return False

"""Main script for calendar email reminder system."""

import json
import logging
import os
import sys
from datetime import datetime

from dotenv import load_dotenv

from calendar_auth import get_calendar_service, get_red_events_in_next_10_minutes
from email_sender import send_reminder_email

logger = logging.getLogger(__name__)


def setup_logging(log_level: str = "INFO") -> None:
    """Configure logging for the application."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )


def load_sent_notifications(notification_file: str) -> dict:
    """Load the record of already sent notifications."""
    if os.path.exists(notification_file):
        try:
            with open(notification_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}


def save_sent_notifications(notification_file: str, notifications: dict):
    """Save the record of sent notifications."""
    with open(notification_file, 'w') as f:
        json.dump(notifications, f, indent=2)


def clean_old_notifications(notifications: dict, hours: int = 24) -> dict:
    """Remove notification records older than specified hours."""
    current_time = datetime.utcnow().timestamp()
    cutoff_time = current_time - (hours * 3600)
    
    return {
        event_key: timestamp 
        for event_key, timestamp in notifications.items() 
        if timestamp > cutoff_time
    }


def create_event_key(event_id: str, start_time: str) -> str:
    """Create a unique key combining event ID and start time."""
    return f"{event_id}_{start_time}"


def main():
    """Main function to check calendar and send reminders."""
    # Setup logging
    setup_logging(os.getenv("LOG_LEVEL", "INFO"))

    logger.info("=" * 60)
    logger.info(
        f"Calendar Email Reminder - Running at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    logger.info("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    gmail_address = os.getenv('GMAIL_ADDRESS')
    gmail_password = os.getenv('GMAIL_APP_PASSWORD')
    recipient_email = os.getenv('RECIPIENT_EMAIL')
    calendar_id = os.getenv('CALENDAR_ID', 'primary')
    notification_file = os.getenv('NOTIFICATION_FILE', '.sent_notifications.json')
    
    # Validate configuration
    if not all([gmail_address, gmail_password, recipient_email]):
        logger.error("Missing email configuration in .env file")
        logger.error(
            "Please ensure GMAIL_ADDRESS, GMAIL_APP_PASSWORD, and RECIPIENT_EMAIL are set."
        )
        return
    
    # Load notification history
    sent_notifications = load_sent_notifications(notification_file)
    sent_notifications = clean_old_notifications(sent_notifications)
    
    # Get Google Calendar service
    try:
        service = get_calendar_service()
        if not service:
            logger.error("Failed to authenticate with Google Calendar")
            return
    except FileNotFoundError as e:
        logger.error(f"Credentials file not found: {e}")
        logger.error("Please follow the setup instructions in README.md")
        return
    except Exception as e:
        logger.error(f"Error during authentication: {e}")
        return
    
    # Fetch red events in next 7-12 minutes
    logger.info("Checking for red-tagged events in the next 7-12 minutes...")
    red_events = get_red_events_in_next_10_minutes(service, calendar_id)
    
    if not red_events:
        logger.info("No red-tagged events found in the next 7-12 minutes.")
        save_sent_notifications(notification_file, sent_notifications)
        return

    logger.info(f"Found {len(red_events)} red-tagged event(s)")
    
    # Process each event
    events_processed = 0
    emails_sent = 0
    
    for event in red_events:
        event_id = event['id']
        start_time = event['start']
        event_key = create_event_key(event_id, start_time)
        
        # Check if we've already sent a notification for this event at this time
        if event_key in sent_notifications:
            logger.debug(f"Skipping '{event['summary']}' - notification already sent")
            continue
        
        events_processed += 1
        logger.info(f"Processing event: {event['summary']}")
        
        # Send reminder email
        success = send_reminder_email(
            event=event,
            sender_email=gmail_address,
            sender_password=gmail_password,
            recipient_email=recipient_email
        )
        
        if success:
            # Record that we sent a notification for this event at this time
            sent_notifications[event_key] = datetime.utcnow().timestamp()
            emails_sent += 1
    
    # Save updated notification history
    save_sent_notifications(notification_file, sent_notifications)

    logger.info("=" * 60)
    logger.info(f"Summary: Processed {events_processed} event(s), sent {emails_sent} email(s)")
    logger.info("=" * 60)
    print("=" * 60)


if __name__ == "__main__":
    main()

"""Tests for email_sender module."""

from unittest.mock import MagicMock, patch

import pytest

from email_sender import send_reminder_email


class TestSendReminderEmail:
    """Tests for send_reminder_email function."""

    @patch("email_sender.smtplib.SMTP_SSL")
    def test_successful_email_send(self, mock_smtp):
        """Test that email is sent successfully."""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        event = {
            "id": "event123",
            "summary": "Test Event",
            "start": "2026-05-22T15:00:00Z",
            "end": "2026-05-22T16:00:00Z",
        }

        result = send_reminder_email(
            event=event,
            sender_email="sender@gmail.com",
            sender_password="password",
            recipient_email="recipient@gmail.com",
        )

        assert result is True
        mock_server.login.assert_called_once_with("sender@gmail.com", "password")
        mock_server.send_message.assert_called_once()

    @patch("email_sender.smtplib.SMTP_SSL")
    def test_email_subject_contains_event_name(self, mock_smtp):
        """Test that email subject includes event summary."""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        event = {
            "summary": "Important Meeting",
            "start": "2026-05-22T15:00:00Z",
        }

        send_reminder_email(
            event=event,
            sender_email="sender@gmail.com",
            sender_password="password",
            recipient_email="recipient@gmail.com",
        )

        # Check that send_message was called
        assert mock_server.send_message.called
        # Get the message object that was sent
        sent_message = mock_server.send_message.call_args[0][0]
        assert "Important Meeting" in sent_message["Subject"]

    @patch("email_sender.smtplib.SMTP_SSL")
    def test_failed_email_send(self, mock_smtp):
        """Test that email send failure is handled gracefully."""
        mock_smtp.return_value.__enter__.side_effect = Exception("SMTP Error")

        event = {
            "summary": "Test Event",
            "start": "2026-05-22T15:00:00Z",
        }

        result = send_reminder_email(
            event=event,
            sender_email="sender@gmail.com",
            sender_password="password",
            recipient_email="recipient@gmail.com",
        )

        assert result is False

    @patch("email_sender.smtplib.SMTP_SSL")
    def test_email_uses_correct_smtp_settings(self, mock_smtp):
        """Test that correct SMTP server and port are used."""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        event = {
            "summary": "Test Event",
            "start": "2026-05-22T15:00:00Z",
        }

        send_reminder_email(
            event=event,
            sender_email="sender@gmail.com",
            sender_password="password",
            recipient_email="recipient@gmail.com",
        )

        mock_smtp.assert_called_once_with("smtp.gmail.com", 465)

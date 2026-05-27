"""Tests for calendar_auth module."""

from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

from calendar_auth import format_event_time, get_red_events_in_next_10_minutes


class TestFormatEventTime:
    """Tests for format_event_time function."""

    def test_format_datetime_with_z(self):
        """Test formatting ISO datetime with Z timezone."""
        datetime_str = "2026-05-22T15:30:00Z"
        result = format_event_time(datetime_str)
        assert "May" in result
        assert "2026" in result

    def test_format_datetime_with_timezone(self):
        """Test formatting ISO datetime with timezone offset."""
        datetime_str = "2026-05-22T15:30:00-07:00"
        result = format_event_time(datetime_str)
        assert "May" in result
        assert "2026" in result

    def test_invalid_datetime_returns_original(self):
        """Test that invalid datetime returns original string."""
        invalid_str = "not-a-valid-datetime"
        result = format_event_time(invalid_str)
        assert result == invalid_str


class TestGetRedEventsInNext10Minutes:
    """Tests for get_red_events_in_next_10_minutes function."""

    @patch("calendar_auth.datetime")
    def test_returns_red_events_only(self, mock_datetime):
        """Test that only red-colored events are returned."""
        # Mock datetime.utcnow()
        mock_now = datetime(2026, 5, 22, 15, 0, 0)
        mock_datetime.utcnow.return_value = mock_now
        mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

        # Mock service
        mock_service = MagicMock()
        mock_events_result = {
            "items": [
                {
                    "id": "event1",
                    "summary": "Red Event",
                    "colorId": "11",  # Red color
                    "start": {"dateTime": "2026-05-22T15:10:00Z"},
                    "end": {"dateTime": "2026-05-22T15:30:00Z"},
                },
                {
                    "id": "event2",
                    "summary": "Blue Event",
                    "colorId": "9",  # Not red
                    "start": {"dateTime": "2026-05-22T15:10:00Z"},
                    "end": {"dateTime": "2026-05-22T15:30:00Z"},
                },
            ]
        }
        mock_service.events().list().execute.return_value = mock_events_result

        result = get_red_events_in_next_10_minutes(mock_service, "primary")

        assert len(result) == 1
        assert result[0]["summary"] == "Red Event"
        assert result[0]["id"] == "event1"

    def test_returns_empty_for_no_events(self):
        """Test that empty list is returned when no events exist."""
        mock_service = MagicMock()
        mock_service.events().list().execute.return_value = {"items": []}

        result = get_red_events_in_next_10_minutes(mock_service, "primary")

        assert result == []

    def test_handles_http_error(self):
        """Test that HttpError is handled gracefully."""
        from googleapiclient.errors import HttpError

        mock_service = MagicMock()
        mock_resp = MagicMock()
        mock_resp.status = 500
        mock_service.events().list().execute.side_effect = HttpError(
            mock_resp, b"Server error"
        )

        result = get_red_events_in_next_10_minutes(mock_service, "primary")

        assert result == []

    def test_event_without_color_excluded(self):
        """Test that events without colorId are excluded."""
        mock_service = MagicMock()
        mock_events_result = {
            "items": [
                {
                    "id": "event1",
                    "summary": "No Color Event",
                    # No colorId
                    "start": {"dateTime": "2026-05-22T15:10:00Z"},
                    "end": {"dateTime": "2026-05-22T15:30:00Z"},
                }
            ]
        }
        mock_service.events().list().execute.return_value = mock_events_result

        result = get_red_events_in_next_10_minutes(mock_service, "primary")

        assert len(result) == 0

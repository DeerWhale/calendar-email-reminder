"""Tests for main module."""

import json
import os
from datetime import datetime
from unittest.mock import mock_open, patch

import pytest

from main import (
    clean_old_notifications,
    create_event_key,
    load_sent_notifications,
    save_sent_notifications,
)


class TestLoadSentNotifications:
    """Tests for load_sent_notifications function."""

    def test_load_existing_file(self, tmp_path):
        """Test loading notifications from existing file."""
        test_file = tmp_path / "notifications.json"
        test_data = {"event1": 1234567890.0}
        test_file.write_text(json.dumps(test_data))

        result = load_sent_notifications(str(test_file))
        assert result == test_data

    def test_load_nonexistent_file(self):
        """Test loading notifications when file doesn't exist."""
        result = load_sent_notifications("nonexistent.json")
        assert result == {}

    def test_load_invalid_json(self, tmp_path):
        """Test loading notifications from file with invalid JSON."""
        test_file = tmp_path / "invalid.json"
        test_file.write_text("invalid json {")

        result = load_sent_notifications(str(test_file))
        assert result == {}


class TestSaveSentNotifications:
    """Tests for save_sent_notifications function."""

    def test_save_notifications(self, tmp_path):
        """Test saving notifications to file."""
        test_file = tmp_path / "notifications.json"
        test_data = {"event1": 1234567890.0, "event2": 1234567900.0}

        save_sent_notifications(str(test_file), test_data)

        assert test_file.exists()
        saved_data = json.loads(test_file.read_text())
        assert saved_data == test_data


class TestCleanOldNotifications:
    """Tests for clean_old_notifications function."""

    def test_remove_old_notifications(self):
        """Test that old notifications are removed."""
        current_time = datetime.utcnow().timestamp()
        old_time = current_time - (25 * 3600)  # 25 hours ago
        recent_time = current_time - (1 * 3600)  # 1 hour ago

        notifications = {
            "old_event": old_time,
            "recent_event": recent_time,
        }

        result = clean_old_notifications(notifications, hours=24)

        assert "recent_event" in result
        assert "old_event" not in result
        assert result["recent_event"] == recent_time

    def test_keep_all_recent_notifications(self):
        """Test that all recent notifications are kept."""
        current_time = datetime.utcnow().timestamp()
        recent_time1 = current_time - (1 * 3600)
        recent_time2 = current_time - (5 * 3600)

        notifications = {
            "event1": recent_time1,
            "event2": recent_time2,
        }

        result = clean_old_notifications(notifications, hours=24)

        assert len(result) == 2
        assert result == notifications


class TestCreateEventKey:
    """Tests for create_event_key function."""

    def test_create_key_format(self):
        """Test that event key is created correctly."""
        event_id = "abc123"
        start_time = "2026-05-22T15:00:00-07:00"

        result = create_event_key(event_id, start_time)

        assert result == "abc123_2026-05-22T15:00:00-07:00"
        assert "_" in result
        assert result.startswith(event_id)
        assert result.endswith(start_time)

    def test_different_times_different_keys(self):
        """Test that same event with different times creates different keys."""
        event_id = "event123"
        time1 = "2026-05-22T15:00:00-07:00"
        time2 = "2026-05-22T16:00:00-07:00"

        key1 = create_event_key(event_id, time1)
        key2 = create_event_key(event_id, time2)

        assert key1 != key2

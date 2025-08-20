"""
External integrations for Protocol Home.

This module contains integrations with external services like
Google Calendar, Slack, email systems, etc.
"""

from .calendar import CalendarIntegration
from .notifications import NotificationSystem

__all__ = [
    "CalendarIntegration",
    "NotificationSystem",
]

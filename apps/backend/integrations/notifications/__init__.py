"""
Remote Notifications Integration
================================
Integration with remote notification services (WeCom, Feishu, DingTalk).
"""
from .config import NotificationConfig
from .service import (
    NotificationService,
    NotificationContext,
    NullNotificationService,
    get_notification_service,
    load_friendly_task_name,
)
from .wecom import WeComNotificationService

__all__ = [
    "NotificationConfig",
    "NotificationService",
    "NotificationContext",
    "NullNotificationService",
    "WeComNotificationService",
    "get_notification_service",
    "load_friendly_task_name",
]

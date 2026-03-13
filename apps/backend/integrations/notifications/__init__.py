"""
Remote Notifications Integration
================================
Integration with remote notification services (WeCom, Feishu, DingTalk).
"""
from .config import NotificationConfig
from .service import NotificationService, NotificationContext, get_notification_service
from .wecom import WeComNotificationService

__all__ = [
    "NotificationConfig",
    "NotificationService",
    "NotificationContext",
    "WeComNotificationService",
    "get_notification_service",
]

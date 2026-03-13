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
from .i18n import (
    translate,
    get_language,
    get_phase_display_name,
    LANGUAGE_EN,
    LANGUAGE_ZH,
)

__all__ = [
    "NotificationConfig",
    "NotificationService",
    "NotificationContext",
    "NullNotificationService",
    "WeComNotificationService",
    "get_notification_service",
    "load_friendly_task_name",
    "translate",
    "get_language",
    "get_phase_display_name",
    "LANGUAGE_EN",
    "LANGUAGE_ZH",
]

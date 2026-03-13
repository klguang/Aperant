"""
Notification Service Interface
==============================
Abstract base class for notification services and factory pattern.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from .config import (
    NotificationConfig,
    NOTIFICATION_METHOD_WECOM,
    NOTIFICATION_METHOD_FEISHU,
    NOTIFICATION_METHOD_DINGTALK,
)


@dataclass
class NotificationContext:
    """Context for a notification event."""

    project_name: str
    task_name: str
    phase: str  # "plan", "code", "qa"
    spec_dir: Optional[str] = None
    project_dir: Optional[str] = None


class NotificationService(ABC):
    """Abstract base class for notification services."""

    @abstractmethod
    def send(self, context: NotificationContext) -> bool:
        """
        Send a notification.

        Args:
            context: Notification context with project/task/phase info

        Returns:
            True if successful
        """
        pass

    @abstractmethod
    def send_test(self, project_name: str) -> bool:
        """
        Send a test notification.

        Args:
            project_name: Name of the project for test message

        Returns:
            True if successful
        """
        pass


class NullNotificationService(NotificationService):
    """No-op service when notifications are disabled."""

    def send(self, context: NotificationContext) -> bool:
        return True

    def send_test(self, project_name: str) -> bool:
        return True


def get_notification_service(config: NotificationConfig) -> NotificationService:
    """
    Factory function to get the appropriate notification service.

    Args:
        config: Notification configuration

    Returns:
        NotificationService instance
    """
    if not config.is_valid():
        return NullNotificationService()

    if config.method == NOTIFICATION_METHOD_WECOM:
        from .wecom import WeComNotificationService

        return WeComNotificationService(config)

    # Future: add Feishu and DingTalk here
    # if config.method == NOTIFICATION_METHOD_FEISHU:
    #     from .feishu import FeishuNotificationService
    #     return FeishuNotificationService(config)

    return NullNotificationService()

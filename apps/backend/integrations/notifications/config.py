"""
Notification Configuration
==========================
Configuration constants and helpers for remote notifications.
"""
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

NOTIFICATION_METHOD_WECOM = "wecom"
NOTIFICATION_METHOD_FEISHU = "feishu"
NOTIFICATION_METHOD_DINGTALK = "dingtalk"

# Environment variable names
ENV_ENABLED = "REMOTE_NOTIFICATION_ENABLED"
ENV_METHOD = "REMOTE_NOTIFICATION_METHOD"
ENV_WEBHOOK_URL = "REMOTE_NOTIFICATION_WEBHOOK_URL"
ENV_TRIGGER_PLAN = "REMOTE_NOTIFICATION_TRIGGER_PLAN_COMPLETE"
ENV_TRIGGER_CODE = "REMOTE_NOTIFICATION_TRIGGER_CODE_COMPLETE"
ENV_TRIGGER_QA = "REMOTE_NOTIFICATION_TRIGGER_QA_COMPLETE"
ENV_LANGUAGE = "NOTIFICATION_LANGUAGE"


@dataclass
class NotificationConfig:
    """Configuration for remote notifications."""

    enabled: bool = False
    method: str = NOTIFICATION_METHOD_WECOM
    webhook_url: str = ""
    trigger_plan_complete: bool = True
    trigger_code_complete: bool = True
    trigger_qa_complete: bool = True

    @classmethod
    def from_env(cls) -> "NotificationConfig":
        """Create config from environment variables."""
        return cls(
            enabled=os.environ.get(ENV_ENABLED, "false").lower() == "true",
            method=os.environ.get(ENV_METHOD, NOTIFICATION_METHOD_WECOM),
            webhook_url=os.environ.get(ENV_WEBHOOK_URL, ""),
            trigger_plan_complete=os.environ.get(ENV_TRIGGER_PLAN, "true").lower() == "true",
            trigger_code_complete=os.environ.get(ENV_TRIGGER_CODE, "true").lower() == "true",
            trigger_qa_complete=os.environ.get(ENV_TRIGGER_QA, "true").lower() == "true",
        )

    def is_valid(self) -> bool:
        """Check if config has minimum required values."""
        if not self.enabled:
            return False
        if self.method == NOTIFICATION_METHOD_WECOM:
            return bool(self.webhook_url)
        # Future methods can add their validation here
        return False

    def should_trigger(self, phase: str) -> bool:
        """Check if notification should trigger for the given phase."""
        if not self.is_valid():
            return False
        if phase == "plan":
            return self.trigger_plan_complete
        elif phase == "code":
            return self.trigger_code_complete
        elif phase == "qa":
            return self.trigger_qa_complete
        return False

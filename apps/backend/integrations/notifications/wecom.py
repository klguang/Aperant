"""
WeCom Notification Service
=========================
Implementation of WeCom group bot webhook notifications.
"""
import json
import logging
from typing import Any
import urllib.request
import urllib.error
import os

from .config import NotificationConfig
from .service import NotificationService, NotificationContext
from .i18n import translate, get_phase_display_name

logger = logging.getLogger(__name__)


class WeComNotificationService(NotificationService):
    """WeCom group bot notification service."""

    def __init__(self, config: NotificationConfig) -> None:
        self.config = config
        self.webhook_url = config.webhook_url

    def _build_message(self, content: str) -> dict[str, Any]:
        """Build WeCom message payload."""
        return {"msgtype": "text", "text": {"content": content}}

    def _send_request(self, payload: dict[str, Any]) -> bool:
        """Send HTTP request to WeCom webhook."""
        if not self.webhook_url:
            logger.warning("[WeCom] No webhook URL configured")
            return False

        try:
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                self.webhook_url,
                data=data,
                headers={"Content-Type": "application/json"},
            )

            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode("utf-8"))
                if result.get("errcode") == 0:
                    logger.debug("[WeCom] Notification sent successfully")
                    return True
                else:
                    logger.warning(
                        "[WeCom] Failed to send: %s",
                        result.get("errmsg", "Unknown error"),
                    )
                    return False

        except urllib.error.URLError as e:
            logger.warning("[WeCom] Network error: %s", e)
            return False
        except json.JSONDecodeError as e:
            logger.warning("[WeCom] Invalid response: %s", e)
            return False
        except Exception as e:
            logger.warning("[WeCom] Unexpected error: %s", e)
            return False

    def send(self, context: NotificationContext) -> bool:
        """Send notification for task phase completion."""
        # Get localized phase name
        phase_display = get_phase_display_name(context.phase)

        # Get localized completion message
        translation_key = f"task.{context.phase}.complete"
        content = translate(
            translation_key,
            task_name=context.task_name,
            phase=phase_display,
        )
        # Fallback to generic if specific phase key not found
        if content == translation_key:
            content = translate(
                "task.phase.complete",
                task_name=context.task_name,
                phase=phase_display,
            )

        logger.debug(
            "[WeCom] Sending notification: task=%s, phase=%s",
            context.task_name,
            context.phase,
        )

        payload = self._build_message(content)
        return self._send_request(payload)

    def send_test(self) -> bool:
        """Send a test notification."""
        content = translate("notification.test")
        payload = self._build_message(content)
        logger.info("[WeCom] Sending test notification")
        return self._send_request(payload)

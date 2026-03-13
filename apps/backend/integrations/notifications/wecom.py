"""
WeCom (企业微信) Notification Service
=====================================
Implementation of WeCom group bot webhook notifications.
"""
import json
import logging
from typing import Any
import urllib.request
import urllib.error

from .config import NotificationConfig
from .service import NotificationService, NotificationContext

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
        phase_display = {
            "plan": "Plan",
            "code": "Code",
            "qa": "QA",
        }.get(context.phase, context.phase)

        content = f"{context.project_name} - {context.task_name} {phase_display} 已经完成！"

        logger.debug(
            "[WeCom] Sending notification: project=%s, task=%s, phase=%s",
            context.project_name,
            context.task_name,
            context.phase,
        )

        payload = self._build_message(content)
        return self._send_request(payload)

    def send_test(self, project_name: str) -> bool:
        """Send a test notification."""
        content = f"测试通知：{project_name} 测试成功！"
        payload = self._build_message(content)
        logger.debug("[WeCom] Sending test notification")
        return self._send_request(payload)

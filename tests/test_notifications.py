#!/usr/bin/env python3
"""
Notification Service Tests
===========================

Tests for the notifications integration module.
"""

import json
import os
import sys
from unittest.mock import MagicMock, patch
from urllib.error import URLError

import pytest

# Add backend to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "apps", "backend")))

# Import modules directly to avoid Pylance resolution issues
from integrations.notifications import (
    NotificationConfig,
    NotificationService,
    NotificationContext,
    NullNotificationService,
    WeComNotificationService,
    get_notification_service,
)
from integrations.notifications.config import (
    NOTIFICATION_METHOD_WECOM,
    NOTIFICATION_METHOD_FEISHU,
    NOTIFICATION_METHOD_DINGTALK,
    ENV_ENABLED,
    ENV_METHOD,
    ENV_WEBHOOK_URL,
    ENV_TRIGGER_PLAN,
    ENV_TRIGGER_CODE,
    ENV_TRIGGER_QA,
)


# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def sample_webhook_url():
    """Sample webhook URL for testing."""
    return "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=test-key-123"


@pytest.fixture
def real_webhook_url():
    """Real webhook URL for integration tests (from user)."""
    return "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=8cb7be60-236a-4bf8-bde0-6d40cdee9f79"


@pytest.fixture
def notification_context():
    """Sample notification context."""
    return NotificationContext(
        task_name="Implement Feature X",
        phase="plan",
        spec_dir="/tmp/spec",
        project_dir="/tmp/project",
    )


# ============================================================================
# NotificationConfig Tests
# ============================================================================


class TestNotificationConfig:
    """Tests for NotificationConfig class."""

    def test_default_config_values(self):
        """Test default configuration values."""
        config = NotificationConfig()
        assert config.enabled is False
        assert config.method == NOTIFICATION_METHOD_WECOM
        assert config.webhook_url == ""
        assert config.trigger_plan_complete is True
        assert config.trigger_code_complete is True
        assert config.trigger_qa_complete is True

    def test_from_env_with_no_env_vars(self):
        """Test loading config with no environment variables set."""
        with patch.dict(os.environ, {}, clear=True):
            config = NotificationConfig.from_env()
            assert config.enabled is False
            assert config.method == NOTIFICATION_METHOD_WECOM
            assert config.webhook_url == ""

    def test_from_env_with_env_vars(self, sample_webhook_url):
        """Test loading config from environment variables."""
        env_vars = {
            ENV_ENABLED: "true",
            ENV_METHOD: NOTIFICATION_METHOD_WECOM,
            ENV_WEBHOOK_URL: sample_webhook_url,
            ENV_TRIGGER_PLAN: "false",
            ENV_TRIGGER_CODE: "true",
            ENV_TRIGGER_QA: "false",
        }
        with patch.dict(os.environ, env_vars, clear=True):
            config = NotificationConfig.from_env()
            assert config.enabled is True
            assert config.method == NOTIFICATION_METHOD_WECOM
            assert config.webhook_url == sample_webhook_url
            assert config.trigger_plan_complete is False
            assert config.trigger_code_complete is True
            assert config.trigger_qa_complete is False

    def test_is_valid_disabled(self):
        """Test is_valid() when notifications are disabled."""
        config = NotificationConfig(enabled=False)
        assert config.is_valid() is False

    def test_is_valid_wecom_missing_url(self):
        """Test is_valid() for WeCom with missing webhook URL."""
        config = NotificationConfig(
            enabled=True, method=NOTIFICATION_METHOD_WECOM, webhook_url=""
        )
        assert config.is_valid() is False

    def test_is_valid_wecom_with_url(self, sample_webhook_url):
        """Test is_valid() for WeCom with valid webhook URL."""
        config = NotificationConfig(
            enabled=True, method=NOTIFICATION_METHOD_WECOM, webhook_url=sample_webhook_url
        )
        assert config.is_valid() is True

    def test_should_trigger_invalid_config(self):
        """Test should_trigger() with invalid config."""
        config = NotificationConfig(enabled=False)
        assert config.should_trigger("plan") is False

    def test_should_trigger_plan_phase(self, sample_webhook_url):
        """Test should_trigger() for plan phase."""
        config = NotificationConfig(
            enabled=True,
            method=NOTIFICATION_METHOD_WECOM,
            webhook_url=sample_webhook_url,
            trigger_plan_complete=True,
            trigger_code_complete=False,
            trigger_qa_complete=False,
        )
        assert config.should_trigger("plan") is True
        assert config.should_trigger("code") is False
        assert config.should_trigger("qa") is False

    def test_should_trigger_code_phase(self, sample_webhook_url):
        """Test should_trigger() for code phase."""
        config = NotificationConfig(
            enabled=True,
            method=NOTIFICATION_METHOD_WECOM,
            webhook_url=sample_webhook_url,
            trigger_plan_complete=False,
            trigger_code_complete=True,
            trigger_qa_complete=False,
        )
        assert config.should_trigger("plan") is False
        assert config.should_trigger("code") is True
        assert config.should_trigger("qa") is False

    def test_should_trigger_qa_phase(self, sample_webhook_url):
        """Test should_trigger() for QA phase."""
        config = NotificationConfig(
            enabled=True,
            method=NOTIFICATION_METHOD_WECOM,
            webhook_url=sample_webhook_url,
            trigger_plan_complete=False,
            trigger_code_complete=False,
            trigger_qa_complete=True,
        )
        assert config.should_trigger("plan") is False
        assert config.should_trigger("code") is False
        assert config.should_trigger("qa") is True

    def test_should_trigger_unknown_phase(self, sample_webhook_url):
        """Test should_trigger() for unknown phase."""
        config = NotificationConfig(
            enabled=True,
            method=NOTIFICATION_METHOD_WECOM,
            webhook_url=sample_webhook_url,
        )
        assert config.should_trigger("unknown") is False


# ============================================================================
# NotificationService Tests
# ============================================================================


class TestNullNotificationService:
    """Tests for NullNotificationService class."""

    def test_send_returns_true(self, notification_context):
        """Test send() always returns True."""
        service = NullNotificationService()
        assert service.send(notification_context) is True

    def test_send_test_returns_true(self):
        """Test send_test() always returns True."""
        service = NullNotificationService()
        assert service.send_test() is True


class TestGetNotificationService:
    """Tests for get_notification_service() factory function."""

    def test_invalid_config_returns_null_service(self):
        """Test invalid config returns NullNotificationService."""
        config = NotificationConfig(enabled=False)
        service = get_notification_service(config)
        assert isinstance(service, NullNotificationService)

    def test_wecom_method_returns_wecom_service(self, sample_webhook_url):
        """Test WeCom method returns WeComNotificationService."""
        config = NotificationConfig(
            enabled=True, method=NOTIFICATION_METHOD_WECOM, webhook_url=sample_webhook_url
        )
        service = get_notification_service(config)
        assert isinstance(service, WeComNotificationService)

    def test_unknown_method_returns_null_service(self, sample_webhook_url):
        """Test unknown method returns NullNotificationService."""
        config = NotificationConfig(
            enabled=True, method="unknown_method", webhook_url=sample_webhook_url
        )
        # The is_valid() check will fail for unknown methods
        config.is_valid = MagicMock(return_value=True)
        service = get_notification_service(config)
        assert isinstance(service, NullNotificationService)


# ============================================================================
# WeComNotificationService Tests
# ============================================================================


class TestWeComNotificationService:
    """Tests for WeComNotificationService class."""

    def test_init_stores_config(self, sample_webhook_url):
        """Test __init__ stores config and webhook URL."""
        config = NotificationConfig(
            enabled=True, method=NOTIFICATION_METHOD_WECOM, webhook_url=sample_webhook_url
        )
        service = WeComNotificationService(config)
        assert service.config == config
        assert service.webhook_url == sample_webhook_url

    def test_build_message(self, sample_webhook_url):
        """Test _build_message() creates correct payload structure."""
        config = NotificationConfig(
            enabled=True, method=NOTIFICATION_METHOD_WECOM, webhook_url=sample_webhook_url
        )
        service = WeComNotificationService(config)
        content = "Test message"
        payload = service._build_message(content)
        assert payload["msgtype"] == "text"
        assert payload["text"]["content"] == content

    @patch("urllib.request.urlopen")
    def test_send_request_success(self, mock_urlopen, sample_webhook_url):
        """Test _send_request() with successful response."""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({"errcode": 0, "errmsg": "ok"}).encode()
        mock_urlopen.return_value.__enter__.return_value = mock_response

        config = NotificationConfig(
            enabled=True, method=NOTIFICATION_METHOD_WECOM, webhook_url=sample_webhook_url
        )
        service = WeComNotificationService(config)
        payload = service._build_message("Test")
        result = service._send_request(payload)

        assert result is True
        mock_urlopen.assert_called_once()

    @patch("urllib.request.urlopen")
    def test_send_request_error_code(self, mock_urlopen, sample_webhook_url):
        """Test _send_request() with error code response."""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(
            {"errcode": 93000, "errmsg": "invalid webhook url"}
        ).encode()
        mock_urlopen.return_value.__enter__.return_value = mock_response

        config = NotificationConfig(
            enabled=True, method=NOTIFICATION_METHOD_WECOM, webhook_url=sample_webhook_url
        )
        service = WeComNotificationService(config)
        payload = service._build_message("Test")
        result = service._send_request(payload)

        assert result is False

    @patch("urllib.request.urlopen")
    def test_send_request_network_error(self, mock_urlopen, sample_webhook_url):
        """Test _send_request() with network error."""
        mock_urlopen.side_effect = URLError("Connection refused")

        config = NotificationConfig(
            enabled=True, method=NOTIFICATION_METHOD_WECOM, webhook_url=sample_webhook_url
        )
        service = WeComNotificationService(config)
        payload = service._build_message("Test")
        result = service._send_request(payload)

        assert result is False

    @patch("urllib.request.urlopen")
    def test_send_request_json_error(self, mock_urlopen, sample_webhook_url):
        """Test _send_request() with invalid JSON response."""
        mock_response = MagicMock()
        mock_response.read.return_value = b"not json"
        mock_urlopen.return_value.__enter__.return_value = mock_response

        config = NotificationConfig(
            enabled=True, method=NOTIFICATION_METHOD_WECOM, webhook_url=sample_webhook_url
        )
        service = WeComNotificationService(config)
        payload = service._build_message("Test")
        result = service._send_request(payload)

        assert result is False

    def test_send_request_no_webhook_url(self):
        """Test _send_request() with no webhook URL."""
        config = NotificationConfig(
            enabled=True, method=NOTIFICATION_METHOD_WECOM, webhook_url=""
        )
        service = WeComNotificationService(config)
        payload = service._build_message("Test")
        result = service._send_request(payload)

        assert result is False

    @patch.object(WeComNotificationService, "_send_request")
    def test_send_plan_phase(self, mock_send_request, sample_webhook_url, notification_context):
        """Test send() for plan phase."""
        mock_send_request.return_value = True
        notification_context.phase = "plan"

        config = NotificationConfig(
            enabled=True, method=NOTIFICATION_METHOD_WECOM, webhook_url=sample_webhook_url
        )
        service = WeComNotificationService(config)
        result = service.send(notification_context)

        assert result is True
        mock_send_request.assert_called_once()
        # Verify payload contains the phase information
        args, _ = mock_send_request.call_args
        payload = args[0]
        assert "Plan" in payload["text"]["content"]

    @patch.object(WeComNotificationService, "_send_request")
    def test_send_code_phase(self, mock_send_request, sample_webhook_url, notification_context):
        """Test send() for code phase."""
        mock_send_request.return_value = True
        notification_context.phase = "code"

        config = NotificationConfig(
            enabled=True, method=NOTIFICATION_METHOD_WECOM, webhook_url=sample_webhook_url
        )
        service = WeComNotificationService(config)
        result = service.send(notification_context)

        assert result is True
        mock_send_request.assert_called_once()
        args, _ = mock_send_request.call_args
        payload = args[0]
        assert "Code" in payload["text"]["content"]

    @patch.object(WeComNotificationService, "_send_request")
    def test_send_qa_phase(self, mock_send_request, sample_webhook_url, notification_context):
        """Test send() for QA phase."""
        mock_send_request.return_value = True
        notification_context.phase = "qa"

        config = NotificationConfig(
            enabled=True, method=NOTIFICATION_METHOD_WECOM, webhook_url=sample_webhook_url
        )
        service = WeComNotificationService(config)
        result = service.send(notification_context)

        assert result is True
        mock_send_request.assert_called_once()
        args, _ = mock_send_request.call_args
        payload = args[0]
        assert "QA" in payload["text"]["content"]

    @patch.object(WeComNotificationService, "_send_request")
    def test_send_test(self, mock_send_request, sample_webhook_url):
        """Test send_test() method."""
        mock_send_request.return_value = True

        config = NotificationConfig(
            enabled=True, method=NOTIFICATION_METHOD_WECOM, webhook_url=sample_webhook_url
        )
        service = WeComNotificationService(config)
        result = service.send_test()

        assert result is True
        mock_send_request.assert_called_once()
        args, _ = mock_send_request.call_args
        payload = args[0]
        assert "测试通知" in payload["text"]["content"]


# ============================================================================
# Integration Tests (Real Webhook)
# ============================================================================


@pytest.mark.integration
class TestWeComNotificationServiceIntegration:
    """Integration tests using real WeCom webhook."""

    @pytest.mark.skipif(
        not os.environ.get("RUN_NOTIFICATION_INTEGRATION_TESTS"),
        reason="Set RUN_NOTIFICATION_INTEGRATION_TESTS=true to run",
    )
    def test_send_test_real_webhook(self, real_webhook_url):
        """Test send_test() with real webhook URL."""
        config = NotificationConfig(
            enabled=True, method=NOTIFICATION_METHOD_WECOM, webhook_url=real_webhook_url
        )
        service = WeComNotificationService(config)
        result = service.send_test()
        assert result is True, "Failed to send test notification"

    @pytest.mark.skipif(
        not os.environ.get("RUN_NOTIFICATION_INTEGRATION_TESTS"),
        reason="Set RUN_NOTIFICATION_INTEGRATION_TESTS=true to run",
    )
    def test_send_real_webhook_plan_phase(self, real_webhook_url, notification_context):
        """Test send() with real webhook URL for plan phase."""
        notification_context.phase = "plan"
        notification_context.project_name = "Aperant Test Project"
        notification_context.task_name = "Integration Test Task"

        config = NotificationConfig(
            enabled=True, method=NOTIFICATION_METHOD_WECOM, webhook_url=real_webhook_url
        )
        service = WeComNotificationService(config)
        result = service.send(notification_context)
        assert result is True, "Failed to send plan phase notification"

    @pytest.mark.skipif(
        not os.environ.get("RUN_NOTIFICATION_INTEGRATION_TESTS"),
        reason="Set RUN_NOTIFICATION_INTEGRATION_TESTS=true to run",
    )
    def test_send_real_webhook_all_phases(self, real_webhook_url, notification_context):
        """Test send() with real webhook URL for all phases."""
        config = NotificationConfig(
            enabled=True, method=NOTIFICATION_METHOD_WECOM, webhook_url=real_webhook_url
        )
        service = WeComNotificationService(config)

        notification_context.project_name = "Aperant Test Project"
        notification_context.task_name = "Full Phase Test"

        for phase in ["plan", "code", "qa"]:
            notification_context.phase = phase
            result = service.send(notification_context)
            assert result is True, f"Failed to send {phase} phase notification"

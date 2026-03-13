"""
Notification Commands
=====================

CLI commands for testing and managing remote notifications.
"""

import argparse
import json
import os
import sys
from pathlib import Path

# Ensure parent directory is in path for imports (before other imports)
_PARENT_DIR = Path(__file__).parent.parent
if str(_PARENT_DIR) not in sys.path:
    sys.path.insert(0, str(_PARENT_DIR))


def handle_test_notification_command(
    method: str,
    webhook_url: str,
) -> dict:
    """
    Handle the test notification command.

    Args:
        method: Notification method (wecom, feishu, dingtalk)
        webhook_url: Webhook URL for the notification service

    Returns:
        Dictionary with success status and error message if applicable
    """
    try:
        from integrations.notifications.config import (
            NotificationConfig,
            NOTIFICATION_METHOD_WECOM,
            NOTIFICATION_METHOD_FEISHU,
            NOTIFICATION_METHOD_DINGTALK,
        )
        from integrations.notifications.service import get_notification_service

        # Create a temporary config for testing
        config = NotificationConfig(
            enabled=True,
            method=method,
            webhook_url=webhook_url,
        )

        # Get the appropriate notification service
        service = get_notification_service(config)

        # Send the test notification
        success = service.send_test()

        if success:
            return {"success": True, "error": None}
        else:
            return {"success": False, "error": "Failed to send test notification"}

    except Exception as e:
        return {"success": False, "error": str(e)}


def main():
    """Main entry point for standalone notification command."""
    parser = argparse.ArgumentParser(
        description="Test remote notifications",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--method",
        type=str,
        required=True,
        choices=["wecom", "feishu", "dingtalk"],
        help="Notification method",
    )
    parser.add_argument(
        "--webhook-url",
        type=str,
        required=True,
        help="Webhook URL",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output result as JSON",
    )

    args = parser.parse_args()

    result = handle_test_notification_command(
        method=args.method,
        webhook_url=args.webhook_url,
    )

    if args.json:
        print(json.dumps(result))
    else:
        if result["success"]:
            print("✓ Test notification sent successfully!")
            sys.exit(0)
        else:
            print(f"✗ Failed to send test notification: {result['error']}")
            sys.exit(1)


if __name__ == "__main__":
    main()

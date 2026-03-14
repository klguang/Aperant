"""
Internationalization (i18n) Support
==================================

Simple i18n system for notification messages with support for English and Chinese.
"""
import os
import logging
from typing import Dict, Optional

# Configure logger
logger = logging.getLogger(__name__)

# Supported languages
LANGUAGE_EN = "en"
LANGUAGE_ZH = "zh"
SUPPORTED_LANGUAGES = [LANGUAGE_EN, LANGUAGE_ZH]

# Default language
DEFAULT_LANGUAGE = LANGUAGE_EN

# Translation strings
TRANSLATIONS = {
    LANGUAGE_EN: {
        # Task phase completion messages
        "task.plan.complete": "{task_name} Plan phase has been completed!",
        "task.code.complete": "{task_name} Code phase has been completed!",
        "task.qa.complete": "{task_name} QA phase has been completed!",
        "task.phase.complete": "{task_name} {phase} phase has been completed!",

        # Test notification
        "notification.test": "Test notification: Success!",

        # Error messages
        "error.translation.fallback": "Using fallback translation for key '{key}'",
        "error.translation.missing": "Translation key '{key}' not found",
        "error.translation.format": "Failed to format message '{key}'",
        "error.language.unsupported": "Unsupported language '{lang}', using '{fallback}'",
    },
    LANGUAGE_ZH: {
        # Task phase completion messages
        "task.plan.complete": "{task_name} 规划阶段已完成！",
        "task.code.complete": "{task_name} 编码阶段已完成！",
        "task.qa.complete": "{task_name} 质量保证阶段已完成！",
        "task.phase.complete": "{task_name} {phase} 阶段已完成！",

        # Test notification
        "notification.test": "测试通知：测试成功！",

        # Error messages
        "error.translation.fallback": "正在为键 '{key}' 使用备用翻译",
        "error.translation.missing": "未找到翻译键 '{key}'",
        "error.translation.format": "格式化消息 '{key}' 失败",
        "error.language.unsupported": "不支持的语言 '{lang}'，正在使用 '{fallback}'",
    },
}


def get_language() -> str:
    """
    Get the current language from environment variable or defaults to English.

    Supports mapping from frontend languages:
    - en -> en
    - fr -> en (fallback)
    - zh -> zh
    - Any other -> en (fallback)

    Returns:
        Current language code (en or zh)
    """
    lang = os.environ.get("LANGUAGE", "en").lower().strip()

    # 显式的语言映射
    language_mapping = {
        'en': LANGUAGE_EN,
        'english': LANGUAGE_EN,
        'zh': LANGUAGE_ZH,
        'zh-cn': LANGUAGE_ZH,
        'zh-tw': LANGUAGE_ZH,
        'chinese': LANGUAGE_ZH,
        'fr': LANGUAGE_EN,  # 法语映射到英语
        'french': LANGUAGE_EN,
    }

    if lang in language_mapping:
        return language_mapping[lang]

    if lang in SUPPORTED_LANGUAGES:
        return lang

    if lang:
        logger.warning("Unsupported language '%s', falling back to English", lang)
    return DEFAULT_LANGUAGE


def translate(key: str, language: Optional[str] = None, **kwargs) -> str:
    """
    Translate a message key to the specified language.

    Args:
        key: Translation key
        language: Target language (en/zh), defaults to environment setting
        **kwargs: Variables to interpolate into the translated string

    Returns:
        Translated message with variables interpolated
    """
    lang = language or get_language()
    fallback_lang = DEFAULT_LANGUAGE

    if lang not in SUPPORTED_LANGUAGES:
        logger.warning("Unsupported language '%s', using fallback language '%s'", lang, fallback_lang)
        lang = fallback_lang

    try:
        # Try to get translation in requested language
        if lang in TRANSLATIONS and key in TRANSLATIONS[lang]:
            translation = TRANSLATIONS[lang][key]
            return translation.format(**kwargs)

        # Fallback to default language if translation not found
        logger.warning("Translation key '%s' not found in language '%s', falling back to '%s'",
                       key, lang, fallback_lang)
        if fallback_lang in TRANSLATIONS and key in TRANSLATIONS[fallback_lang]:
            translation = TRANSLATIONS[fallback_lang][key]
            return translation.format(**kwargs)

        # Final fallback: return raw key with parameters
        logger.error("Translation key '%s' not found in any supported language", key)
        return _format_fallback_message(key, **kwargs)

    except KeyError as e:
        logger.error("Translation key error: %s", e)
        return _format_fallback_message(key, **kwargs)
    except Exception as e:
        logger.error("Translation error for key '%s': %s", key, e)
        return _format_fallback_message(key, **kwargs)


def get_phase_display_name(phase: str, language: Optional[str] = None) -> str:
    """
    Get localized display name for a phase.

    Args:
        phase: Phase identifier (plan/code/qa)
        language: Target language (en/zh)

    Returns:
        Localized phase display name
    """
    phase_display = {
        LANGUAGE_EN: {
            "plan": "Plan",
            "code": "Code",
            "qa": "QA",
        },
        LANGUAGE_ZH: {
            "plan": "规划",
            "code": "编码",
            "qa": "质量保证",
        },
    }

    lang = language or get_language()
    lang = lang if lang in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE

    try:
        if lang in phase_display and phase in phase_display[lang]:
            return phase_display[lang][phase]
        logger.warning("Phase display name not found for phase '%s' in language '%s'", phase, lang)
        return phase
    except Exception as e:
        logger.error("Error getting phase display name: %s", e)
        return phase


def _format_fallback_message(key: str, **kwargs) -> str:
    """
    Format a fallback message when translation fails.

    Args:
        key: Original translation key
        **kwargs: Variables to interpolate

    Returns:
        Formatted fallback message
    """
    if not kwargs:
        return key
    # Create a string with key and parameters
    params_str = ", ".join(f"{k}={v}" for k, v in kwargs.items())
    return f"{key} ({params_str})"

/**
 * Internationalization constants
 * Available languages and display labels
 *
 * NOTE: When adding new languages, also update the language mapping
 * in the backend notification system (apps/backend/integrations/notifications/i18n.py)
 * and the agent process environment setup (apps/frontend/src/main/agent/agent-process.ts)
 */

export type SupportedLanguage = 'en' | 'fr';

export const AVAILABLE_LANGUAGES = [
  { value: 'en' as const, label: 'English', nativeLabel: 'English' },
  { value: 'fr' as const, label: 'French', nativeLabel: 'Français' }
] as const;

export const DEFAULT_LANGUAGE: SupportedLanguage = 'en';

/**
 * Maps frontend language to backend notification language.
 * Backend only supports 'en' and 'zh', so other languages fall back to 'en'.
 */
export function mapToNotificationLanguage(lang: SupportedLanguage): 'en' | 'zh' {
  switch (lang) {
    case 'en': return 'en';
    case 'fr': return 'en'; // French falls back to English
    default: return 'en';
  }
}

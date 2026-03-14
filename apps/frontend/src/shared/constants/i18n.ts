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
import { ipcMain, app } from 'electron';
import type { BrowserWindow } from 'electron';
import { IPC_CHANNELS } from '../../shared/constants';
import type { IPCResult } from '../../shared/types';
import path from 'path';
import { spawn } from 'child_process';
import { existsSync } from 'fs';
import { parsePythonCommand } from '../python-detector';
import { getConfiguredPythonPath, pythonEnvManager } from '../python-env-manager';
import { getEffectiveSourcePath } from '../updater/path-resolver';
import { fileURLToPath } from 'url';
import { debugError } from '../../shared/utils/debug-logger';

/**
 * Register all notification-related IPC handlers
 */
export function registerNotificationHandlers(
  _getMainWindow: () => BrowserWindow | null
): void {
  ipcMain.handle(
    IPC_CHANNELS.ENV_TEST_REMOTE_NOTIFICATION,
    async (_, config: any): Promise<IPCResult<{ success: boolean; error?: string }>> => {
      console.log('[Notification] Handler called with config:', config);
      try {
        const { method, wecom, feishu, dingtalk } = config;
        let webhookUrl: string | undefined;

        switch (method) {
          case 'wecom':
            webhookUrl = wecom?.webhookUrl;
            break;
          case 'feishu':
            webhookUrl = feishu?.webhookUrl;
            break;
          case 'dingtalk':
            webhookUrl = dingtalk?.webhookUrl;
            break;
          default:
            return { success: false, error: 'Unsupported notification method' };
        }

        if (!webhookUrl) {
          return { success: false, error: 'Webhook URL is required' };
        }

        // 使用可靠的路径解析器获取 backend 路径
        let backendDir = getEffectiveSourcePath();
        let notificationCmdPath = path.join(backendDir, 'cli', 'notification_commands.py');

        console.log('[Notification] Using backend directory:', backendDir);
        console.log('[Notification] Using notification_commands.py path:', notificationCmdPath);

        if (!existsSync(notificationCmdPath)) {
          console.error('[Notification] notification_commands.py not found at:', notificationCmdPath);
          return {
            success: false,
            error: 'Backend notification module not found. Please check installation.'
          };
        }
        console.log('[Notification] notification_commands.py exists');

        // 获取 Python 命令
        const pythonCmd = getConfiguredPythonPath();
        console.log('[Notification] Using Python command:', pythonCmd);

        const [pythonExecutable, pythonArgs] = parsePythonCommand(pythonCmd);

        // 构建命令参数
        const args = [
          ...pythonArgs,
          notificationCmdPath,
          '--method',
          method,
          '--webhook-url',
          webhookUrl,
          '--project-name',
          'Aperant Test Project',
          '--json'
        ];

        console.log('[Notification] Running test notification command:', pythonExecutable, args.join(' '));

        // 获取正确的 Python 环境（包括 PYTHONPATH 等）
        const env = pythonEnvManager.isEnvReady()
          ? pythonEnvManager.getPythonEnv()
          : { ...process.env, PYTHONUNBUFFERED: '1' };

        // Spawn the backend process
        const result = await new Promise<{ success: boolean; error?: string }>((resolve) => {
          const proc = spawn(pythonExecutable, args, {
            cwd: backendDir,
            env: env,
            shell: false
          });

          let stdout = '';
          let stderr = '';

          proc.stdout?.on('data', (data: Buffer) => {
            stdout += data.toString('utf-8');
            console.log('[Notification] stdout chunk:', JSON.stringify(data.toString('utf-8')));
          });

          proc.stderr?.on('data', (data: Buffer) => {
            stderr += data.toString('utf-8');
            console.log('[Notification] stderr chunk:', JSON.stringify(data.toString('utf-8')));
          });

          proc.on('close', (code: number | null) => {
            console.log('[Notification] Test notification process completed with code:', code);
            console.log('[Notification] Full stdout:', JSON.stringify(stdout));
            console.log('[Notification] Full stderr:', JSON.stringify(stderr));

            try {
              // Try to parse JSON response - look for any valid JSON line
              const lines = stdout.trim().split('\n');
              let parsedResult: any = null;

              for (const line of lines) {
                const trimmedLine = line.trim();
                if (trimmedLine.startsWith('{') && trimmedLine.endsWith('}')) {
                  try {
                    parsedResult = JSON.parse(trimmedLine);
                    break; // Found valid JSON, stop looking
                  } catch (e) {
                    continue; // Invalid JSON, try next line
                  }
                }
              }

              if (parsedResult) {
                console.log('[Notification] Successfully parsed backend response:', parsedResult);
                resolve(parsedResult);
              } else {
                // If no JSON, check exit code
                console.error('[Notification] No valid JSON response found. stdout:', stdout, 'stderr:', stderr);
                if (code === 0) {
                  resolve({ success: true });
                } else {
                  resolve({
                    success: false,
                    error: stderr || 'Failed to send test notification'
                  });
                }
              }
            } catch (parseError) {
              console.error('[Notification] Failed to parse backend response:', parseError);
              resolve({
                success: false,
                error: stderr || 'Failed to parse backend response'
              });
            }
          });

          proc.on('error', (err: Error) => {
            debugError('[Notification] Failed to spawn test notification process:', err);
            resolve({
              success: false,
              error: err.message
            });
          });
        });

        console.log('[Notification] Final result to return to frontend:', { success: true, data: result });
        return { success: true, data: result };
      } catch (error) {
        console.error('[Notification] Test notification error:', error);
        return {
          success: false,
          error: error instanceof Error ? error.message : 'Failed to send test notification'
        };
      }
    }
  );
}

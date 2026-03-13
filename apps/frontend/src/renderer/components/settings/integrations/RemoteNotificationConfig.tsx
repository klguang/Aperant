import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Loader2, CheckCircle2, AlertCircle } from 'lucide-react';
import { Button } from '../../ui/button';
import { Input } from '../../ui/input';
import { Label } from '../../ui/label';
import { Switch } from '../../ui/switch';
import { Separator } from '../../ui/separator';
import { Checkbox } from '../../ui/checkbox';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from '../../ui/select';
import type { ProjectEnvConfig } from '../../../../shared/types';

interface RemoteNotificationConfigProps {
  envConfig: ProjectEnvConfig | null;
  updateEnvConfig: (updates: Partial<ProjectEnvConfig>) => void;
}

/**
 * 远程通知配置组件
 * 管理远程通知的启用状态、通知方式、Webhook URL 和触发阶段
 */
export function RemoteNotificationConfig({
  envConfig,
  updateEnvConfig
}: RemoteNotificationConfigProps) {
  const { t } = useTranslation(['settings']);
  const [isTesting, setIsTesting] = useState(false);
  const [testResult, setTestResult] = useState<'success' | 'error' | null>(null);

  if (!envConfig) return null;

  const config = envConfig.remoteNotificationConfig || {
    enabled: false,
    method: 'wecom' as const,
    wecom: { webhookUrl: '' },
    triggers: {
      planComplete: false,
      codeComplete: false,
      qaComplete: false
    }
  };

  // 获取当前方法的webhook url
  const getWebhookUrl = (): string => {
    switch (config.method) {
      case 'wecom':
        return config.wecom?.webhookUrl || '';
      case 'feishu':
        return config.feishu?.webhookUrl || '';
      case 'dingtalk':
        return config.dingtalk?.webhookUrl || '';
      default:
        return '';
    }
  };

  // 更新webhook url
  const handleWebhookChange = (value: string) => {
    const updatedConfig = { ...config };

    switch (config.method) {
      case 'wecom':
        updatedConfig.wecom = { webhookUrl: value };
        break;
      case 'feishu':
        updatedConfig.feishu = { webhookUrl: value };
        break;
      case 'dingtalk':
        updatedConfig.dingtalk = { webhookUrl: value };
        break;
    }

    updateEnvConfig({
      remoteNotificationConfig: updatedConfig
    });
  };

  // 切换通知方法
  const handleMethodChange = (method: 'wecom' | 'feishu' | 'dingtalk') => {
    // 保留当前的webhook url到新的方法中
    const currentWebhookUrl = getWebhookUrl();
    const updatedConfig: any = {
      ...config,
      method,
      // 清除旧的方法配置
      wecom: undefined,
      feishu: undefined,
      dingtalk: undefined
    };

    // 将当前webhook设置到新方法中
    if (currentWebhookUrl) {
      updatedConfig[method] = { webhookUrl: currentWebhookUrl };
    } else {
      updatedConfig[method] = { webhookUrl: '' };
    }

    updateEnvConfig({
      remoteNotificationConfig: updatedConfig
    });
  };

  const handleEnableChange = (checked: boolean) => {
    updateEnvConfig({
      remoteNotificationConfig: {
        ...config,
        enabled: checked
      }
    });
  };

  const handleTriggerChange = (trigger: keyof typeof config.triggers, checked: boolean) => {
    updateEnvConfig({
      remoteNotificationConfig: {
        ...config,
        triggers: {
          ...config.triggers,
          [trigger]: checked
        }
      }
    });
  };

  const handleTestNotification = async () => {
    const webhookUrl = getWebhookUrl();
    if (!webhookUrl) {
      setTestResult('error');
      return;
    }

    setIsTesting(true);
    setTestResult(null);

    try {
      const result = await window.electronAPI.testRemoteNotification(config);
      if (result.success && result.data?.success) {
        setTestResult('success');
      } else {
        setTestResult('error');
      }
    } catch (error) {
      setTestResult('error');
    } finally {
      setIsTesting(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="space-y-0.5">
          <Label className="font-normal text-foreground">
            {t('settings:projectSections.remoteNotification.enable')}
          </Label>
          <p className="text-xs text-muted-foreground">
            {t('settings:projectSections.remoteNotification.enableDescription')}
          </p>
        </div>
        <Switch
          checked={config.enabled}
          onCheckedChange={handleEnableChange}
        />
      </div>

      {config.enabled && (
        <>
          <div className="space-y-2">
            <Label className="text-sm font-medium text-foreground">
              {t('settings:projectSections.remoteNotification.method')}
            </Label>
            <p className="text-xs text-muted-foreground">
              {t('settings:projectSections.remoteNotification.methodDescription')}
            </p>
            <Select
              value={config.method}
              onValueChange={(value: 'wecom' | 'feishu' | 'dingtalk') => handleMethodChange(value)}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="wecom">
                  {t('settings:projectSections.remoteNotification.methods.wecom')}
                </SelectItem>
                <SelectItem value="feishu">
                  {t('settings:projectSections.remoteNotification.methods.feishu')}
                </SelectItem>
                <SelectItem value="dingtalk">
                  {t('settings:projectSections.remoteNotification.methods.dingtalk')}
                </SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label className="text-sm font-medium text-foreground">
              {t('settings:projectSections.remoteNotification.webhook')}
            </Label>
            <p className="text-xs text-muted-foreground">
              {t('settings:projectSections.remoteNotification.webhookDescription')}
            </p>
            <Input
              type="text"
              placeholder={`https://...`}
              value={getWebhookUrl()}
              onChange={(e) => handleWebhookChange(e.target.value)}
            />
          </div>

          <Separator />

          <div className="space-y-2">
            <Label className="text-sm font-medium text-foreground">
              {t('settings:projectSections.remoteNotification.triggers')}
            </Label>
            <p className="text-xs text-muted-foreground">
              {t('settings:projectSections.remoteNotification.triggersDescription')}
            </p>

            <div className="space-y-2">
              <div className="flex items-center gap-3">
                <Checkbox
                  id="trigger-plan"
                  checked={config.triggers.planComplete}
                  onCheckedChange={(checked) => handleTriggerChange('planComplete', !!checked)}
                />
                <Label htmlFor="trigger-plan" className="text-sm">
                  {t('settings:projectSections.remoteNotification.planComplete')}
                </Label>
              </div>

              <div className="flex items-center gap-3">
                <Checkbox
                  id="trigger-code"
                  checked={config.triggers.codeComplete}
                  onCheckedChange={(checked) => handleTriggerChange('codeComplete', !!checked)}
                />
                <Label htmlFor="trigger-code" className="text-sm">
                  {t('settings:projectSections.remoteNotification.codeComplete')}
                </Label>
              </div>

              <div className="flex items-center gap-3">
                <Checkbox
                  id="trigger-qa"
                  checked={config.triggers.qaComplete}
                  onCheckedChange={(checked) => handleTriggerChange('qaComplete', !!checked)}
                />
                <Label htmlFor="trigger-qa" className="text-sm">
                  {t('settings:projectSections.remoteNotification.qaComplete')}
                </Label>
              </div>
            </div>
          </div>

          <Separator />

          <div className="space-y-2">
            <Label className="text-sm font-medium text-foreground">
              {t('settings:projectSections.remoteNotification.test')}
            </Label>
            <p className="text-xs text-muted-foreground">
              {t('settings:projectSections.remoteNotification.testDescription')}
            </p>

            <Button
              onClick={handleTestNotification}
              disabled={isTesting || !getWebhookUrl()}
              className="w-full"
            >
              {isTesting ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  {t('settings:projectSections.remoteNotification.sending')}
                </>
              ) : (
                t('settings:projectSections.remoteNotification.sendTest')
              )}
            </Button>

            {testResult === 'success' && (
              <div className="flex items-center gap-2 text-xs text-success">
                <CheckCircle2 className="h-4 w-4" />
                {t('settings:projectSections.remoteNotification.testSuccess')}
              </div>
            )}

            {testResult === 'error' && (
              <div className="flex items-center gap-2 text-xs text-error">
                <AlertCircle className="h-4 w-4" />
                {t('settings:projectSections.remoteNotification.testError')}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}

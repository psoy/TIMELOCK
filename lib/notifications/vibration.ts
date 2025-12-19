/**
 * 진동 알림
 * Vibration API를 사용하여 햅틱 피드백을 제공합니다.
 * Android에서만 동작합니다 (iOS Safari는 미지원)
 */

export class VibrationNotification {
  /**
   * Vibration API 지원 여부 확인
   */
  isSupported(): boolean {
    return 'vibrate' in navigator;
  }

  /**
   * 진동 실행
   * @param pattern 진동 패턴 (밀리초 단위 배열) - [진동, 정지, 진동, 정지, ...]
   * @returns 성공 여부
   */
  vibrate(pattern: number[] | number = [200, 100, 200, 100, 200]): boolean {
    if (!this.isSupported()) {
      console.warn('Vibration API is not supported on this device');
      return false;
    }

    try {
      const result = navigator.vibrate(pattern);
      if (result) {
        console.log('Vibration triggered:', pattern);
      } else {
        console.warn('Vibration request was rejected');
      }
      return result;
    } catch (err) {
      console.error('Vibration failed:', err);
      return false;
    }
  }

  /**
   * 사전 정의된 패턴으로 진동
   */
  vibratePreset(preset: 'short' | 'medium' | 'long' | 'urgent'): boolean {
    const patterns = {
      short: [200],
      medium: [200, 100, 200, 100, 200],
      long: [400, 200, 400, 200, 400],
      urgent: [100, 50, 100, 50, 100, 50, 100, 50, 100],
    };

    return this.vibrate(patterns[preset]);
  }

  /**
   * 진동 중단
   */
  stop(): boolean {
    if (!this.isSupported()) {
      return false;
    }

    return navigator.vibrate(0);
  }

  /**
   * 플랫폼 정보 가져오기
   */
  getPlatformInfo(): {
    supported: boolean;
    platform: string;
    userAgent: string;
  } {
    const ua = navigator.userAgent;
    const isAndroid = /Android/i.test(ua);
    const isIOS = /iPhone|iPad|iPod/i.test(ua);

    return {
      supported: this.isSupported(),
      platform: isAndroid ? 'Android' : isIOS ? 'iOS' : 'Unknown',
      userAgent: ua,
    };
  }
}

// 싱글톤 인스턴스
export const vibration = new VibrationNotification();

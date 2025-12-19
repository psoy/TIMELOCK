/**
 * 화면 플래시 알림
 * Screen Wake Lock API를 사용하여 화면을 깨우고 플래시 효과를 제공합니다.
 * 모든 플랫폼에서 동작합니다 (iOS, Android, Desktop)
 */

export class ScreenFlashNotification {
  private wakeLock: WakeLockSentinel | null = null;
  private isFlashing: boolean = false;

  /**
   * Wake Lock API 지원 여부 확인
   */
  isSupported(): boolean {
    return 'wakeLock' in navigator;
  }

  /**
   * 화면 플래시 효과 실행
   * @param pattern 깜박임 패턴 (밀리초 단위 배열) - [켜짐, 꺼짐, 켜짐, 꺼짐, ...]
   * @param color 플래시 색상 (기본값: 흰색)
   */
  async flash(
    pattern: number[] = [500, 300, 500, 300, 500],
    color: string = '#ffffff'
  ): Promise<void> {
    if (this.isFlashing) {
      console.warn('Flash already in progress');
      return;
    }

    this.isFlashing = true;

    try {
      // Wake Lock 요청 (화면이 꺼지지 않도록)
      if (this.isSupported()) {
        try {
          this.wakeLock = await navigator.wakeLock.request('screen');
          console.log('Wake Lock activated');
        } catch (err) {
          console.warn('Wake Lock request failed:', err);
          // Wake Lock이 실패해도 플래시는 계속 진행
        }
      }

      // 전체 화면 플래시 오버레이 생성
      const overlay = document.createElement('div');
      overlay.id = 'timelock-flash-overlay';
      overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background-color: ${color};
        z-index: 99999;
        opacity: 0;
        pointer-events: none;
        transition: opacity 0.05s ease-in-out;
      `;
      document.body.appendChild(overlay);

      // 깜박임 패턴 실행
      for (let i = 0; i < pattern.length; i++) {
        const isOn = i % 2 === 0;
        overlay.style.opacity = isOn ? '0.95' : '0';
        await this.sleep(pattern[i]);
      }

      // 오버레이 제거
      overlay.style.opacity = '0';
      await this.sleep(100);
      document.body.removeChild(overlay);
    } finally {
      // Wake Lock 해제
      if (this.wakeLock) {
        try {
          await this.wakeLock.release();
          this.wakeLock = null;
          console.log('Wake Lock released');
        } catch (err) {
          console.warn('Wake Lock release failed:', err);
        }
      }

      this.isFlashing = false;
    }
  }

  /**
   * 사전 정의된 패턴으로 플래시
   */
  async flashPreset(preset: 'short' | 'medium' | 'long' | 'urgent'): Promise<void> {
    const patterns = {
      short: [200, 150, 200],
      medium: [300, 200, 300, 200, 300],
      long: [500, 300, 500, 300, 500, 300, 500],
      urgent: [100, 100, 100, 100, 100, 100, 100, 100, 100],
    };

    await this.flash(patterns[preset]);
  }

  /**
   * 플래시 중단
   */
  async stop(): Promise<void> {
    const overlay = document.getElementById('timelock-flash-overlay');
    if (overlay) {
      overlay.remove();
    }

    if (this.wakeLock) {
      await this.wakeLock.release();
      this.wakeLock = null;
    }

    this.isFlashing = false;
  }

  /**
   * 대기 함수
   */
  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}

// 싱글톤 인스턴스
export const screenFlash = new ScreenFlashNotification();

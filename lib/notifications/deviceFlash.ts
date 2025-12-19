/**
 * 디바이스 플래시 알림 (카메라 LED)
 * MediaStream API의 Torch 기능을 사용하여 카메라 LED를 제어합니다.
 * Android PWA에서만 동작합니다 (iOS는 미지원)
 */

export class DeviceFlashNotification {
  private stream: MediaStream | null = null;
  private track: MediaStreamTrack | null = null;
  private isFlashing: boolean = false;

  /**
   * Torch API 지원 여부 확인
   */
  async isSupported(): Promise<boolean> {
    try {
      // MediaDevices API 존재 확인
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        return false;
      }

      // 카메라 권한 확인
      const devices = await navigator.mediaDevices.enumerateDevices();
      const hasCamera = devices.some((device) => device.kind === 'videoinput');

      return hasCamera;
    } catch (err) {
      console.warn('Torch support check failed:', err);
      return false;
    }
  }

  /**
   * 카메라 스트림 초기화
   */
  private async initializeStream(): Promise<boolean> {
    if (this.stream) {
      return true; // 이미 초기화됨
    }

    try {
      // 후면 카메라 요청
      this.stream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: 'environment', // 후면 카메라
        },
      });

      const videoTrack = this.stream.getVideoTracks()[0];

      // Torch 기능 지원 여부 확인
      const capabilities = videoTrack.getCapabilities() as any;
      if (!capabilities.torch) {
        console.warn('Torch capability not available on this device');
        this.cleanup();
        return false;
      }

      this.track = videoTrack;
      console.log('Camera stream initialized with torch capability');
      return true;
    } catch (err) {
      console.error('Failed to initialize camera stream:', err);
      this.cleanup();
      return false;
    }
  }

  /**
   * 디바이스 플래시 실행
   * @param pattern 깜박임 패턴 (밀리초 단위 배열) - [켜짐, 꺼짐, 켜짐, 꺼짐, ...]
   */
  async flash(pattern: number[] = [500, 300, 500, 300, 500]): Promise<void> {
    if (this.isFlashing) {
      console.warn('Flash already in progress');
      return;
    }

    this.isFlashing = true;

    try {
      // 스트림 초기화
      const initialized = await this.initializeStream();
      if (!initialized || !this.track) {
        console.error('Failed to initialize camera for flash');
        return;
      }

      // 깜박임 패턴 실행
      for (let i = 0; i < pattern.length; i++) {
        const isOn = i % 2 === 0;

        try {
          await this.track.applyConstraints({
            advanced: [{ torch: isOn } as any],
          });
        } catch (err) {
          console.error('Failed to apply torch constraint:', err);
          break;
        }

        await this.sleep(pattern[i]);
      }

      // 마지막에 반드시 끄기
      if (this.track) {
        await this.track.applyConstraints({
          advanced: [{ torch: false } as any],
        });
      }
    } finally {
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
   * 플래시 중단 및 정리
   */
  async stop(): Promise<void> {
    if (this.track) {
      try {
        await this.track.applyConstraints({
          advanced: [{ torch: false } as any],
        });
      } catch (err) {
        console.error('Failed to turn off torch:', err);
      }
    }

    this.cleanup();
    this.isFlashing = false;
  }

  /**
   * 리소스 정리
   */
  private cleanup(): void {
    if (this.track) {
      this.track.stop();
      this.track = null;
    }

    if (this.stream) {
      this.stream.getTracks().forEach((track) => track.stop());
      this.stream = null;
    }
  }

  /**
   * 대기 함수
   */
  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  /**
   * 플랫폼 정보 가져오기
   */
  getPlatformInfo(): {
    platform: string;
    userAgent: string;
    isPWA: boolean;
  } {
    const ua = navigator.userAgent;
    const isAndroid = /Android/i.test(ua);
    const isIOS = /iPhone|iPad|iPod/i.test(ua);
    const isPWA = window.matchMedia('(display-mode: standalone)').matches;

    return {
      platform: isAndroid ? 'Android' : isIOS ? 'iOS' : 'Unknown',
      userAgent: ua,
      isPWA,
    };
  }
}

// 싱글톤 인스턴스
export const deviceFlash = new DeviceFlashNotification();

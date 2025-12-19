'use client';

import { useState, useEffect } from 'react';
import { screenFlash } from '@/lib/notifications/screenFlash';
import { vibration } from '@/lib/notifications/vibration';
import { deviceFlash } from '@/lib/notifications/deviceFlash';

type NotificationType = 'screen' | 'vibration' | 'device';
type PresetPattern = 'short' | 'medium' | 'long' | 'urgent';

export default function PrototypePage() {
  const [selectedType, setSelectedType] = useState<NotificationType>('screen');
  const [selectedPreset, setSelectedPreset] = useState<PresetPattern>('medium');
  const [isTesting, setIsTesting] = useState(false);
  const [supportInfo, setSupportInfo] = useState({
    screen: false,
    vibration: false,
    device: false,
  });
  const [platformInfo, setPlatformInfo] = useState<string>('');

  useEffect(() => {
    // 지원 여부 확인
    const checkSupport = async () => {
      const deviceSupported = await deviceFlash.isSupported();

      setSupportInfo({
        screen: screenFlash.isSupported(),
        vibration: vibration.isSupported(),
        device: deviceSupported,
      });

      // 플랫폼 정보
      const vibInfo = vibration.getPlatformInfo();
      const flashInfo = deviceFlash.getPlatformInfo();
      setPlatformInfo(
        `Platform: ${vibInfo.platform} | PWA: ${flashInfo.isPWA ? 'Yes' : 'No'}`
      );
    };

    checkSupport();
  }, []);

  const handleTest = async () => {
    setIsTesting(true);

    try {
      switch (selectedType) {
        case 'screen':
          await screenFlash.flashPreset(selectedPreset);
          break;
        case 'vibration':
          vibration.vibratePreset(selectedPreset);
          break;
        case 'device':
          await deviceFlash.flashPreset(selectedPreset);
          break;
      }
    } catch (error) {
      console.error('Notification test failed:', error);
      alert(`테스트 실패: ${error}`);
    } finally {
      setIsTesting(false);
    }
  };

  const handleStop = async () => {
    await screenFlash.stop();
    vibration.stop();
    await deviceFlash.stop();
    setIsTesting(false);
  };

  const notificationTypes = [
    {
      id: 'screen' as NotificationType,
      name: '화면 플래시',
      description: '화면 전체가 깜박입니다',
      emoji: '💡',
      platforms: 'iOS, Android, Desktop',
    },
    {
      id: 'vibration' as NotificationType,
      name: '진동',
      description: '기기가 진동합니다',
      emoji: '📳',
      platforms: 'Android만 지원',
    },
    {
      id: 'device' as NotificationType,
      name: '카메라 플래시',
      description: '카메라 LED가 깜박입니다',
      emoji: '📸',
      platforms: 'Android PWA만 지원',
    },
  ];

  const presetPatterns = [
    { id: 'short' as PresetPattern, name: '짧게', duration: '0.5초' },
    { id: 'medium' as PresetPattern, name: '중간', duration: '1.2초' },
    { id: 'long' as PresetPattern, name: '길게', duration: '2.5초' },
    { id: 'urgent' as PresetPattern, name: '긴급', duration: '0.9초 (빠른 반복)' },
  ];

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <a href="/" className="text-sm text-gray-500 hover:text-gray-700 mb-4 inline-block">
            ← 홈으로
          </a>
          <h1 className="text-3xl font-bold mb-2">무음 알림 프로토타입</h1>
          <p className="text-gray-600">
            독서실에서 사용할 수 있는 무음 알림 방식을 테스트해보세요
          </p>
          <p className="text-sm text-gray-500 mt-2">{platformInfo}</p>
        </div>

        {/* Notification Type Selection */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4">알림 유형 선택</h2>
          <div className="grid gap-3">
            {notificationTypes.map((type) => {
              const isSupported = supportInfo[type.id];
              return (
                <button
                  key={type.id}
                  onClick={() => setSelectedType(type.id)}
                  disabled={!isSupported}
                  className={`p-4 rounded-lg border-2 text-left transition-all ${
                    selectedType === type.id
                      ? 'border-black bg-gray-50'
                      : 'border-gray-200 hover:border-gray-300'
                  } ${!isSupported ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-2xl">{type.emoji}</span>
                        <h3 className="font-semibold">{type.name}</h3>
                        {!isSupported && (
                          <span className="text-xs bg-red-100 text-red-600 px-2 py-0.5 rounded">
                            미지원
                          </span>
                        )}
                        {isSupported && (
                          <span className="text-xs bg-green-100 text-green-600 px-2 py-0.5 rounded">
                            지원
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-gray-600 mb-1">{type.description}</p>
                      <p className="text-xs text-gray-500">{type.platforms}</p>
                    </div>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Pattern Selection */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4">알림 패턴 선택</h2>
          <div className="grid grid-cols-2 gap-3">
            {presetPatterns.map((preset) => (
              <button
                key={preset.id}
                onClick={() => setSelectedPreset(preset.id)}
                className={`p-4 rounded-lg border-2 text-left transition-all ${
                  selectedPreset === preset.id
                    ? 'border-black bg-gray-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <h3 className="font-semibold mb-1">{preset.name}</h3>
                <p className="text-sm text-gray-600">{preset.duration}</p>
              </button>
            ))}
          </div>
        </div>

        {/* Test Buttons */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex gap-3">
            <button
              onClick={handleTest}
              disabled={isTesting || !supportInfo[selectedType]}
              className="flex-1 bg-black text-white py-4 px-6 rounded-lg font-semibold hover:bg-gray-800 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
            >
              {isTesting ? '테스트 중...' : '테스트 시작'}
            </button>
            <button
              onClick={handleStop}
              disabled={!isTesting}
              className="px-6 py-4 rounded-lg border-2 border-red-500 text-red-500 font-semibold hover:bg-red-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              중단
            </button>
          </div>
        </div>

        {/* Info Panel */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="font-semibold mb-2 flex items-center gap-2">
            <span>ℹ️</span>
            테스트 가이드
          </h3>
          <ul className="text-sm text-gray-700 space-y-2">
            <li>
              <strong>화면 플래시:</strong> 모든 기기에서 동작합니다. 화면이 밝게 깜박입니다.
            </li>
            <li>
              <strong>진동:</strong> Android에서만 동작합니다. iOS Safari는 지원하지 않습니다.
            </li>
            <li>
              <strong>카메라 플래시:</strong> Android PWA에서만 동작합니다. 처음 실행 시
              카메라 권한을 허용해야 합니다.
            </li>
            <li className="pt-2 border-t border-blue-200">
              <strong>실제 기기 테스트:</strong> 데스크톱에서는 화면 플래시만 테스트할 수
              있습니다. 진동과 카메라 플래시는 실제 모바일 기기에서 테스트하세요.
            </li>
          </ul>
        </div>

        {/* Support Status */}
        <div className="mt-6 bg-white rounded-lg shadow-sm p-6">
          <h3 className="font-semibold mb-3">현재 기기 지원 현황</h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between items-center">
              <span>화면 플래시 (Screen Wake Lock API)</span>
              <span
                className={`font-semibold ${
                  supportInfo.screen ? 'text-green-600' : 'text-red-600'
                }`}
              >
                {supportInfo.screen ? '✅ 지원' : '❌ 미지원'}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span>진동 (Vibration API)</span>
              <span
                className={`font-semibold ${
                  supportInfo.vibration ? 'text-green-600' : 'text-red-600'
                }`}
              >
                {supportInfo.vibration ? '✅ 지원' : '❌ 미지원'}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span>카메라 플래시 (MediaStream Torch API)</span>
              <span
                className={`font-semibold ${
                  supportInfo.device ? 'text-green-600' : 'text-red-600'
                }`}
              >
                {supportInfo.device ? '✅ 지원' : '❌ 미지원'}
              </span>
            </div>
          </div>
        </div>

        {/* Mobile Testing Instructions */}
        <div className="mt-6 bg-yellow-50 border border-yellow-200 rounded-lg p-6">
          <h3 className="font-semibold mb-2 flex items-center gap-2">
            <span>📱</span>
            모바일 기기에서 테스트하기
          </h3>
          <ol className="text-sm text-gray-700 space-y-2 list-decimal list-inside">
            <li>개발 서버를 실행합니다: <code className="bg-white px-2 py-1 rounded">npm run dev</code></li>
            <li>같은 Wi-Fi 네트워크에 연결된 모바일 기기에서 접속합니다</li>
            <li>컴퓨터의 로컬 IP 주소로 접속합니다 (예: http://192.168.0.10:3000)</li>
            <li>Android: Chrome 브라우저 사용 권장</li>
            <li>iOS: Safari 브라우저 사용 (화면 플래시만 동작)</li>
          </ol>
        </div>
      </div>
    </div>
  );
}

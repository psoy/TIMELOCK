# TIMELOCK - 무음 타임블로킹

독서실에서도 눈치 안 보고 쓰는 무음 타이머

## 프로젝트 개요

TIMELOCK은 독서실, 도서관 등 조용한 공간에서도 사용할 수 있는 무음 알림 기능을 가진 타임블로킹 앱입니다. 기존 타이머의 소리 알림 대신 화면 플래시, 진동, 카메라 LED 등을 활용하여 주변에 방해 없이 시간을 관리할 수 있습니다.

## 핵심 차별점

### 무음 알림 시스템

1. **화면 플래시** (모든 플랫폼 지원)
   - Screen Wake Lock API 사용
   - 화면 전체가 밝게 깜박여 알림
   - iOS, Android, Desktop 모두 지원

2. **진동 알림** (Android만 지원)
   - Vibration API 사용
   - 햅틱 피드백으로 알림
   - iOS Safari는 미지원

3. **카메라 플래시** (Android PWA만 지원)
   - MediaStream Torch API 사용
   - 카메라 LED가 깜박여 알림
   - 처음 사용 시 카메라 권한 필요

## 현재 구현 상태

✅ **완료된 작업:**
- Screen Wake Lock API 구현 (화면 플래시)
- Vibration API 구현 (진동)
- Device Flash API 구현 (카메라 플래시)
- 프로토타입 테스트 페이지 작성
- Next.js 14 + TypeScript 개발 환경 설정

⏳ **진행 예정:**
- 실제 모바일 기기에서 테스트
- PWA 설정 (manifest.json, service worker)
- 타임블로킹 핵심 기능 구현
- Supabase 연동
- 사용자 인증

## 시작하기

### 필수 요구사항

- Node.js v20 이상
- npm 또는 yarn

### 설치 및 실행

1. 저장소 클론
```bash
git clone https://github.com/psoy/TIMELOCK.git
cd TIMELOCK
```

2. 의존성 설치
```bash
npm install
```

3. 개발 서버 실행
```bash
npm run dev
```

4. 브라우저에서 접속
```
http://localhost:3000
```

## 무음 알림 프로토타입 테스트

### 데스크톱에서 테스트

1. 개발 서버를 실행합니다
```bash
npm run dev
```

2. 브라우저에서 http://localhost:3000/prototype 접속

3. 화면 플래시만 테스트 가능합니다
   - 진동과 카메라 플래시는 모바일 기기에서만 동작합니다

### 모바일 기기에서 테스트

#### 1. 로컬 네트워크를 통한 테스트

1. 개발 서버를 실행합니다
```bash
npm run dev
```

2. 터미널에 표시된 Network URL을 확인합니다
```
- Local:    http://localhost:3000
- Network:  http://192.168.x.x:3000  ← 이 주소를 사용
```

3. 모바일 기기를 **같은 Wi-Fi 네트워크**에 연결합니다

4. 모바일 브라우저에서 Network URL로 접속합니다
   - **Android**: Chrome 브라우저 사용 (모든 기능 지원)
   - **iOS**: Safari 브라우저 사용 (화면 플래시만 지원)

5. `/prototype` 페이지로 이동하여 테스트합니다

#### 2. 테스트 순서

1. **화면 플래시 테스트**
   - 알림 유형: "화면 플래시" 선택
   - 패턴: "중간" 선택
   - "테스트 시작" 버튼 클릭
   - ✅ 화면 전체가 밝게 깜박이는지 확인

2. **진동 테스트** (Android만)
   - 알림 유형: "진동" 선택
   - 패턴: "중간" 선택
   - "테스트 시작" 버튼 클릭
   - ✅ 기기가 진동하는지 확인
   - ⚠️ iOS에서는 "미지원" 표시

3. **카메라 플래시 테스트** (Android만)
   - 알림 유형: "카메라 플래시" 선택
   - 패턴: "중간" 선택
   - "테스트 시작" 버튼 클릭
   - ⚠️ 처음 실행 시 카메라 권한 허용 필요
   - ✅ 후면 카메라 LED가 깜박이는지 확인

#### 3. 플랫폼별 지원 현황

| 알림 유형 | iOS Safari | Android Chrome | Desktop Chrome |
|----------|-----------|----------------|----------------|
| 화면 플래시 | ✅ 완전 지원 | ✅ 완전 지원 | ✅ 완전 지원 |
| 진동 | ❌ 미지원 | ✅ 완전 지원 | ❌ 미지원 |
| 카메라 플래시 | ❌ 미지원 | ⚠️ PWA만 지원 | ❌ 미지원 |

## 프로젝트 구조

```
TIMELOCK/
├── app/                      # Next.js App Router
│   ├── layout.tsx           # 루트 레이아웃
│   ├── page.tsx             # 홈 페이지
│   ├── globals.css          # 글로벌 스타일
│   └── prototype/           # 프로토타입 페이지
│       └── page.tsx         # 무음 알림 테스트 페이지
├── lib/                      # 유틸리티 및 라이브러리
│   └── notifications/       # 무음 알림 구현
│       ├── screenFlash.ts   # 화면 플래시 (Screen Wake Lock API)
│       ├── vibration.ts     # 진동 (Vibration API)
│       └── deviceFlash.ts   # 카메라 플래시 (MediaStream Torch API)
├── public/                   # 정적 파일
├── next.config.ts           # Next.js 설정
├── tailwind.config.ts       # Tailwind CSS 설정
├── tsconfig.json            # TypeScript 설정
├── package.json             # 프로젝트 의존성
├── time_lock_prd.md         # 제품 기획서
├── tech_stack.md            # 기술 스택 문서
├── SETUP_GUIDE.md           # 개발 환경 설정 가이드
└── user_personas_and_value_proposition.md  # 사용자 페르소나 및 가치 제안

```

## 기술 스택

### 프론트엔드
- **Next.js 16**: React 프레임워크
- **TypeScript**: 타입 안전성
- **Tailwind CSS**: 유틸리티 CSS 프레임워크
- **React 19**: UI 라이브러리

### 브라우저 API
- **Screen Wake Lock API**: 화면 플래시 알림
- **Vibration API**: 진동 알림
- **MediaStream API**: 카메라 플래시 알림

### 향후 추가 예정
- Supabase (PostgreSQL): 데이터베이스
- Supabase Auth: 사용자 인증
- Zustand: 상태 관리
- TanStack Query: 서버 상태 관리
- PWA: 오프라인 지원, 설치 가능

## API 사용법

### 화면 플래시

```typescript
import { screenFlash } from '@/lib/notifications/screenFlash';

// 기본 패턴으로 플래시
await screenFlash.flash();

// 커스텀 패턴 (밀리초)
await screenFlash.flash([500, 300, 500], '#ffffff');

// 사전 정의 패턴
await screenFlash.flashPreset('short');   // 짧게
await screenFlash.flashPreset('medium');  // 중간
await screenFlash.flashPreset('long');    // 길게
await screenFlash.flashPreset('urgent');  // 긴급

// 지원 여부 확인
if (screenFlash.isSupported()) {
  await screenFlash.flash();
}

// 중단
await screenFlash.stop();
```

### 진동

```typescript
import { vibration } from '@/lib/notifications/vibration';

// 기본 패턴으로 진동
vibration.vibrate();

// 커스텀 패턴 (밀리초)
vibration.vibrate([200, 100, 200]);

// 사전 정의 패턴
vibration.vibratePreset('short');   // 짧게
vibration.vibratePreset('medium');  // 중간
vibration.vibratePreset('long');    // 길게
vibration.vibratePreset('urgent');  // 긴급

// 지원 여부 확인
if (vibration.isSupported()) {
  vibration.vibrate();
}

// 플랫폼 정보
const info = vibration.getPlatformInfo();
console.log(info.platform);  // 'Android' | 'iOS' | 'Unknown'

// 중단
vibration.stop();
```

### 카메라 플래시

```typescript
import { deviceFlash } from '@/lib/notifications/deviceFlash';

// 기본 패턴으로 플래시
await deviceFlash.flash();

// 커스텀 패턴 (밀리초)
await deviceFlash.flash([500, 300, 500]);

// 사전 정의 패턴
await deviceFlash.flashPreset('short');   // 짧게
await deviceFlash.flashPreset('medium');  // 중간
await deviceFlash.flashPreset('long');    // 길게
await deviceFlash.flashPreset('urgent');  // 긴급

// 지원 여부 확인
const supported = await deviceFlash.isSupported();
if (supported) {
  await deviceFlash.flash();
}

// 플랫폼 정보
const info = deviceFlash.getPlatformInfo();
console.log(info.platform);  // 'Android' | 'iOS' | 'Unknown'
console.log(info.isPWA);     // PWA 모드 여부

// 중단 및 정리
await deviceFlash.stop();
```

## 문서

- [제품 기획서 (PRD)](./time_lock_prd.md)
- [기술 스택 문서](./tech_stack.md)
- [개발 환경 설정 가이드](./SETUP_GUIDE.md)
- [사용자 페르소나 및 가치 제안](./user_personas_and_value_proposition.md)

## 라이선스

ISC

## 저장소

https://github.com/psoy/TIMELOCK

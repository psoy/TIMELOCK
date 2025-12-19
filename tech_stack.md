# TIMELOCK 기술 스택 (Technology Stack)

## 목차
1. [기술 스택 개요](#기술-스택-개요)
2. [프론트엔드](#프론트엔드)
3. [백엔드](#백엔드)
4. [데이터베이스](#데이터베이스)
5. [인증 및 보안](#인증-및-보안)
6. [결제](#결제)
7. [호스팅 및 인프라](#호스팅-및-인프라)
8. [개발 도구 및 DevOps](#개발-도구-및-devops)
9. [모니터링 및 분석](#모니터링-및-분석)
10. [비용 추정](#비용-추정)
11. [기술 검증 체크리스트](#기술-검증-체크리스트)

---

## 기술 스택 개요

### 선정 원칙

1. **PWA First**: iOS와 Android 모두 지원하는 Progressive Web App
2. **1인 개발 최적화**: 빠른 개발 속도, 적은 유지보수 부담
3. **무음 알림 구현**: Screen Wake Lock API, Vibration API, MediaStream API 지원
4. **비용 효율성**: 초기 투자 최소화, 사용량 기반 과금
5. **확장 가능성**: 사용자 증가 시 수평 확장 가능
6. **보안 우선**: DevSecOps 원칙 적용, 개인정보 보호

### 아키텍처 개요

```
┌─────────────────────────────────────────────────────────┐
│                     Frontend (PWA)                      │
│  Next.js + React + TypeScript + Tailwind CSS + PWA     │
│  - Vibration API, Screen Wake Lock API                 │
│  - MediaStream API (Device Flash)                      │
│  - Service Worker (Background)                         │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTPS/REST API
                       ↓
┌─────────────────────────────────────────────────────────┐
│              Backend API (Serverless)                   │
│        Vercel Edge Functions (Node.js)                  │
│        or AWS Lambda + API Gateway                      │
└──────────────────────┬──────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        ↓              ↓              ↓
┌──────────────┐ ┌───────────┐ ┌────────────┐
│  PostgreSQL  │ │   Redis   │ │  Firebase  │
│   (Supabase) │ │  (Upstash)│ │    Auth    │
│   Database   │ │   Cache   │ │   인증     │
└──────────────┘ └───────────┘ └────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────────┐
│              Third-Party Services                       │
│  Stripe (결제) | Vercel Analytics | Sentry (모니터링)  │
└─────────────────────────────────────────────────────────┘
```

---

## 프론트엔드

### 1. 코어 프레임워크

#### **Next.js 14** (App Router) ✅ 선택

**선택 이유**
- ✅ PWA 완벽 지원 (`next-pwa` 플러그인)
- ✅ SSR/SSG/ISR 지원으로 SEO 최적화
- ✅ React Server Components로 성능 향상
- ✅ Vercel 배포 시 최적화
- ✅ TypeScript 기본 지원
- ✅ API Routes로 Backend 통합 가능 (초기 단순 API)
- ✅ 빠른 개발 속도, 풍부한 생태계

**대안 검토**
- ❌ **Vite + React**: PWA 설정 복잡, SSR 부족
- ❌ **Remix**: 생태계가 Next.js보다 작음
- ❌ **Svelte/SvelteKit**: 학습 곡선, 생태계 작음

**버전**
```json
{
  "next": "^14.2.0",
  "react": "^18.3.0",
  "react-dom": "^18.3.0"
}
```

---

### 2. 프로그래밍 언어

#### **TypeScript 5.x** ✅ 선택

**선택 이유**
- ✅ 타입 안정성으로 런타임 에러 감소
- ✅ IDE 자동완성 및 리팩토링 지원
- ✅ 1인 개발 시 유지보수성 향상
- ✅ Next.js와 완벽 통합

**설정**
```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["DOM", "DOM.Iterable", "ES2022"],
    "jsx": "preserve",
    "strict": true,
    "moduleResolution": "bundler",
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

---

### 3. UI 프레임워크 및 스타일링

#### **Tailwind CSS 3.x** + **shadcn/ui** ✅ 선택

**선택 이유**
- ✅ 유틸리티 우선 - 빠른 UI 개발
- ✅ shadcn/ui: 복사 가능한 컴포넌트 (의존성 최소화)
- ✅ 다크 모드 기본 지원
- ✅ 반응형 디자인 간편
- ✅ 번들 크기 최적화 (사용하지 않는 CSS 제거)

**컴포넌트 라이브러리**
```bash
# shadcn/ui (복사 방식, 라이브러리 아님)
npx shadcn-ui@latest init

# 필요 컴포넌트만 선택적 설치
npx shadcn-ui@latest add button
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add calendar
```

**대안 검토**
- ❌ **Material-UI (MUI)**: 번들 크기 크고, 커스터마이징 어려움
- ❌ **Ant Design**: 디자인이 너무 정형화됨
- ⚠️ **Chakra UI**: 고려 가능하나 shadcn/ui가 더 가벼움

---

### 4. 상태 관리

#### **Zustand** ✅ 선택

**선택 이유**
- ✅ 매우 가벼움 (1KB)
- ✅ Redux보다 간단한 API
- ✅ TypeScript 지원 우수
- ✅ React Server Components와 호환
- ✅ 1인 개발에 적합한 단순함

**사용 예시**
```typescript
// store/timeBlockStore.ts
import { create } from 'zustand'

interface TimeBlock {
  id: string
  title: string
  startTime: string
  duration: number
  completed: boolean
}

interface TimeBlockStore {
  blocks: TimeBlock[]
  addBlock: (block: TimeBlock) => void
  updateBlock: (id: string, updates: Partial<TimeBlock>) => void
  deleteBlock: (id: string) => void
}

export const useTimeBlockStore = create<TimeBlockStore>((set) => ({
  blocks: [],
  addBlock: (block) => set((state) => ({ blocks: [...state.blocks, block] })),
  updateBlock: (id, updates) =>
    set((state) => ({
      blocks: state.blocks.map((b) => (b.id === id ? { ...b, ...updates } : b))
    })),
  deleteBlock: (id) =>
    set((state) => ({ blocks: state.blocks.filter((b) => b.id !== id) }))
}))
```

**대안 검토**
- ❌ **Redux Toolkit**: 보일러플레이트 많음, 과함
- ⚠️ **Jotai/Recoil**: 원자 단위 상태 관리, TIMELOCK에는 Zustand로 충분
- ❌ **Context API**: 성능 이슈, 복잡한 상태에 부적합

---

### 5. PWA 설정

#### **next-pwa** ✅ 선택

**선택 이유**
- ✅ Next.js에 최적화된 PWA 플러그인
- ✅ Service Worker 자동 생성
- ✅ 오프라인 캐싱 전략 설정 가능
- ✅ Manifest.json 자동 생성

**설정 예시**
```javascript
// next.config.js
const withPWA = require('next-pwa')({
  dest: 'public',
  register: true,
  skipWaiting: true,
  disable: process.env.NODE_ENV === 'development',
  runtimeCaching: [
    {
      urlPattern: /^https:\/\/fonts\.(?:gstatic)\.com\/.*/i,
      handler: 'CacheFirst',
      options: {
        cacheName: 'google-fonts-webfonts',
        expiration: {
          maxEntries: 4,
          maxAgeSeconds: 365 * 24 * 60 * 60 // 1 year
        }
      }
    }
  ]
})

module.exports = withPWA({
  reactStrictMode: true,
  // ... other config
})
```

**Manifest 설정**
```json
// public/manifest.json
{
  "name": "TIMELOCK - 무음 타임블로킹",
  "short_name": "TIMELOCK",
  "description": "독서실에서도 눈치 안 보고 쓰는 무음 타이머",
  "theme_color": "#000000",
  "background_color": "#ffffff",
  "display": "standalone",
  "orientation": "portrait",
  "scope": "/",
  "start_url": "/",
  "icons": [
    {
      "src": "/icon-192x192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "any maskable"
    },
    {
      "src": "/icon-512x512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "any maskable"
    }
  ]
}
```

---

### 6. 무음 알림 구현 라이브러리

#### **직접 구현 (Web APIs 활용)** ✅ 선택

**Screen Wake Lock API**
```typescript
// utils/screenFlash.ts
export class ScreenFlashNotification {
  private wakeLock: WakeLockSentinel | null = null

  async flash(pattern: number[] = [500, 300, 500, 300, 500]) {
    // 화면 깨우기 유지
    if ('wakeLock' in navigator) {
      this.wakeLock = await navigator.wakeLock.request('screen')
    }

    // 전체 화면 플래시 오버레이 생성
    const overlay = document.createElement('div')
    overlay.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      background-color: white;
      z-index: 9999;
      opacity: 0;
    `
    document.body.appendChild(overlay)

    // 깜박임 패턴 실행
    for (let i = 0; i < pattern.length; i++) {
      overlay.style.opacity = i % 2 === 0 ? '1' : '0'
      await new Promise(resolve => setTimeout(resolve, pattern[i]))
    }

    // 정리
    document.body.removeChild(overlay)
    if (this.wakeLock) {
      await this.wakeLock.release()
      this.wakeLock = null
    }
  }
}
```

**Vibration API**
```typescript
// utils/vibration.ts
export class VibrationNotification {
  vibrate(pattern: number[] = [200, 100, 200, 100, 200]) {
    if ('vibrate' in navigator) {
      navigator.vibrate(pattern)
      return true
    }
    return false
  }
}
```

**Device Flash API (Android)**
```typescript
// utils/deviceFlash.ts
export class DeviceFlashNotification {
  private stream: MediaStream | null = null

  async flash(duration: number = 3000) {
    try {
      // 카메라 접근 (플래시 사용 위해)
      this.stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment' }
      })

      const track = this.stream.getVideoTracks()[0]
      const capabilities = track.getCapabilities() as any

      if (capabilities.torch) {
        await track.applyConstraints({
          advanced: [{ torch: true } as any]
        })

        // duration 후 끄기
        setTimeout(async () => {
          await track.applyConstraints({
            advanced: [{ torch: false } as any]
          })
          this.stop()
        }, duration)

        return true
      }
    } catch (error) {
      console.error('Device flash not supported:', error)
    }
    return false
  }

  stop() {
    if (this.stream) {
      this.stream.getTracks().forEach(track => track.stop())
      this.stream = null
    }
  }
}
```

---

### 7. 데이터 페칭

#### **TanStack Query (React Query) v5** ✅ 선택

**선택 이유**
- ✅ 서버 상태 관리 최적화
- ✅ 자동 캐싱, 재검증
- ✅ 낙관적 업데이트 지원
- ✅ 로딩/에러 상태 관리 간편
- ✅ TypeScript 지원 우수

**사용 예시**
```typescript
// hooks/useTimeBlocks.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'

export function useTimeBlocks(date: string) {
  return useQuery({
    queryKey: ['timeBlocks', date],
    queryFn: () => fetch(`/api/timeblocks?date=${date}`).then(res => res.json())
  })
}

export function useCreateTimeBlock() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (block: TimeBlock) =>
      fetch('/api/timeblocks', {
        method: 'POST',
        body: JSON.stringify(block)
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['timeBlocks'] })
    }
  })
}
```

---

### 8. 폼 관리

#### **React Hook Form** + **Zod** ✅ 선택

**선택 이유**
- ✅ 비제어 컴포넌트로 성능 최적화
- ✅ Zod로 타입 안전한 검증
- ✅ 적은 리렌더링
- ✅ shadcn/ui와 완벽 통합

**사용 예시**
```typescript
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'

const timeBlockSchema = z.object({
  title: z.string().min(1, '제목을 입력하세요').max(100),
  duration: z.number().min(10).max(480),
  startTime: z.string()
})

type TimeBlockForm = z.infer<typeof timeBlockSchema>

export function TimeBlockForm() {
  const form = useForm<TimeBlockForm>({
    resolver: zodResolver(timeBlockSchema),
    defaultValues: {
      title: '',
      duration: 60,
      startTime: ''
    }
  })

  const onSubmit = (data: TimeBlockForm) => {
    console.log(data)
  }

  return <form onSubmit={form.handleSubmit(onSubmit)}>...</form>
}
```

---

### 9. 차트 및 시각화

#### **Recharts** ✅ 선택

**선택 이유**
- ✅ React 네이티브 차트 라이브러리
- ✅ 반응형 차트 기본 제공
- ✅ 커스터마이징 쉬움
- ✅ 히트맵, 바 차트, 원형 차트 지원

**사용 예시**
```typescript
import { BarChart, Bar, XAxis, YAxis, Tooltip } from 'recharts'

const data = [
  { hour: '08:00', focus: 90 },
  { hour: '09:00', focus: 85 },
  { hour: '10:00', focus: 95 }
]

export function FocusChart() {
  return (
    <BarChart width={600} height={300} data={data}>
      <XAxis dataKey="hour" />
      <YAxis />
      <Tooltip />
      <Bar dataKey="focus" fill="#8884d8" />
    </BarChart>
  )
}
```

---

## 백엔드

### 1. API 서버

#### **Option A: Vercel Edge Functions** (추천 - MVP) ✅

**선택 이유**
- ✅ Next.js API Routes 활용
- ✅ 자동 스케일링
- ✅ 글로벌 CDN Edge에서 실행
- ✅ 추가 서버 관리 불필요
- ✅ 무료 티어 넉넉함 (100GB-hours/월)

**구조**
```
app/
├── api/
│   ├── timeblocks/
│   │   └── route.ts        # GET, POST /api/timeblocks
│   ├── analytics/
│   │   └── route.ts        # GET /api/analytics
│   └── users/
│       └── [id]/
│           └── route.ts    # GET /api/users/:id
```

**예시**
```typescript
// app/api/timeblocks/route.ts
import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@/lib/supabase/server'

export async function GET(req: NextRequest) {
  const supabase = createClient()
  const { data: user } = await supabase.auth.getUser()

  if (!user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  const date = req.nextUrl.searchParams.get('date')
  const { data, error } = await supabase
    .from('time_blocks')
    .select('*')
    .eq('user_id', user.user.id)
    .eq('date', date)

  if (error) {
    return NextResponse.json({ error: error.message }, { status: 500 })
  }

  return NextResponse.json(data)
}

export async function POST(req: NextRequest) {
  const supabase = createClient()
  const { data: user } = await supabase.auth.getUser()

  if (!user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  const body = await req.json()
  const { data, error } = await supabase
    .from('time_blocks')
    .insert({ ...body, user_id: user.user.id })
    .select()
    .single()

  if (error) {
    return NextResponse.json({ error: error.message }, { status: 500 })
  }

  return NextResponse.json(data, { status: 201 })
}
```

#### **Option B: AWS Lambda + API Gateway** (확장 시)

**사용 시점**
- DAU 5,000+ 넘어갈 때
- 복잡한 백그라운드 작업 필요 시
- Vercel Edge Functions 제약 초과 시

---

### 2. API 스펙

#### **RESTful API** ✅ 선택

**엔드포인트 설계**

| Method | Endpoint | 설명 | 인증 |
|--------|----------|------|------|
| GET | `/api/timeblocks?date=2026-01-15` | 특정 날짜 시간 블록 조회 | ✅ |
| POST | `/api/timeblocks` | 시간 블록 생성 | ✅ |
| PATCH | `/api/timeblocks/:id` | 시간 블록 수정 | ✅ |
| DELETE | `/api/timeblocks/:id` | 시간 블록 삭제 | ✅ |
| POST | `/api/timeblocks/:id/complete` | 시간 블록 완료 처리 | ✅ |
| GET | `/api/analytics/daily` | 일일 분석 데이터 | ✅ |
| GET | `/api/analytics/weekly` | 주간 분석 데이터 | ✅ |
| GET | `/api/analytics/heatmap` | 집중 패턴 히트맵 (프리미엄) | ✅ |
| GET | `/api/users/me` | 내 프로필 조회 | ✅ |
| PATCH | `/api/users/me` | 내 프로필 수정 | ✅ |
| POST | `/api/subscriptions/checkout` | 구독 결제 시작 | ✅ |
| POST | `/api/webhooks/stripe` | Stripe Webhook | ❌ |

**대안 검토**
- ❌ **GraphQL**: 1인 개발에 과함, REST로 충분
- ❌ **tRPC**: End-to-end 타입 안전성 좋으나, 클라이언트가 웹만 있어서 REST가 더 범용적

---

## 데이터베이스

### **Supabase (PostgreSQL)** ✅ 선택

**선택 이유**
- ✅ PostgreSQL 기반 (관계형 DB)
- ✅ 실시간 구독 기능 내장
- ✅ Row Level Security (RLS)로 보안 강화
- ✅ 인증 시스템 내장
- ✅ 자동 백업
- ✅ 무료 티어: 500MB DB, 5GB 파일 저장
- ✅ RESTful API 자동 생성

**스키마 설계**

```sql
-- users 테이블 (Supabase Auth 자동 생성)
-- auth.users 테이블 활용

-- user_profiles 테이블
CREATE TABLE user_profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  full_name TEXT,
  avatar_url TEXT,
  subscription_tier TEXT DEFAULT 'free' CHECK (subscription_tier IN ('free', 'premium')),
  subscription_expires_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- time_blocks 테이블
CREATE TABLE time_blocks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  description TEXT,
  date DATE NOT NULL,
  start_time TIME NOT NULL,
  duration INTEGER NOT NULL, -- minutes
  category TEXT, -- 과목/프로젝트명
  color TEXT DEFAULT '#3b82f6',
  completed BOOLEAN DEFAULT FALSE,
  actual_duration INTEGER, -- 실제 소요 시간 (minutes)
  completed_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스
CREATE INDEX idx_time_blocks_user_date ON time_blocks(user_id, date);
CREATE INDEX idx_time_blocks_user_created ON time_blocks(user_id, created_at);

-- daily_summaries 테이블 (일일 집계)
CREATE TABLE daily_summaries (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  date DATE NOT NULL,
  total_planned_minutes INTEGER DEFAULT 0,
  total_actual_minutes INTEGER DEFAULT 0,
  completion_rate DECIMAL(5,2), -- 실행률 %
  blocks_completed INTEGER DEFAULT 0,
  blocks_total INTEGER DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, date)
);

CREATE INDEX idx_daily_summaries_user_date ON daily_summaries(user_id, date DESC);

-- focus_patterns 테이블 (프리미엄 - 시간대별 집중도)
CREATE TABLE focus_patterns (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  hour INTEGER NOT NULL CHECK (hour >= 0 AND hour <= 23),
  day_of_week INTEGER NOT NULL CHECK (day_of_week >= 0 AND day_of_week <= 6),
  avg_completion_rate DECIMAL(5,2),
  total_blocks INTEGER DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, hour, day_of_week)
);

-- Row Level Security (RLS) 정책
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE time_blocks ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_summaries ENABLE ROW LEVEL SECURITY;
ALTER TABLE focus_patterns ENABLE ROW LEVEL SECURITY;

-- 정책: 사용자는 자기 데이터만 접근 가능
CREATE POLICY "Users can view own profile"
  ON user_profiles FOR SELECT
  USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
  ON user_profiles FOR UPDATE
  USING (auth.uid() = id);

CREATE POLICY "Users can view own time blocks"
  ON time_blocks FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own time blocks"
  ON time_blocks FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own time blocks"
  ON time_blocks FOR UPDATE
  USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own time blocks"
  ON time_blocks FOR DELETE
  USING (auth.uid() = user_id);

-- daily_summaries, focus_patterns도 동일하게 설정
```

**대안 검토**
- ⚠️ **Firebase Firestore**: NoSQL, 관계형 데이터에 부적합, Supabase가 더 나음
- ❌ **MongoDB Atlas**: NoSQL, 시계열 데이터와 집계에는 PostgreSQL이 더 적합
- ❌ **PlanetScale (MySQL)**: 좋으나 Supabase의 통합 기능이 더 매력적

---

### **캐싱: Upstash Redis** ✅ 선택

**선택 이유**
- ✅ Serverless Redis (사용량 기반 과금)
- ✅ Vercel과 통합 우수
- ✅ 글로벌 복제 지원
- ✅ 무료 티어: 10,000 요청/일

**사용 케이스**
- 사용자 세션 캐싱
- API 응답 캐싱 (일일 요약 등)
- Rate limiting

```typescript
// lib/redis.ts
import { Redis } from '@upstash/redis'

export const redis = new Redis({
  url: process.env.UPSTASH_REDIS_REST_URL!,
  token: process.env.UPSTASH_REDIS_REST_TOKEN!
})

// 사용 예시
export async function getCachedDailySummary(userId: string, date: string) {
  const cacheKey = `summary:${userId}:${date}`
  const cached = await redis.get(cacheKey)

  if (cached) {
    return cached
  }

  // DB에서 조회
  const summary = await fetchDailySummaryFromDB(userId, date)

  // 1시간 캐싱
  await redis.set(cacheKey, summary, { ex: 3600 })

  return summary
}
```

---

## 인증 및 보안

### **Firebase Authentication** ✅ 선택

**선택 이유**
- ✅ 이메일/비밀번호, Google, Apple 로그인 지원
- ✅ 무료 티어 넉넉함 (50,000 MAU)
- ✅ JWT 토큰 자동 관리
- ✅ 보안 규칙 내장
- ✅ Supabase RLS와 통합 가능

**대안: Supabase Auth도 가능**
- Supabase Auth를 사용하면 DB와 완전 통합
- Firebase Auth를 사용하면 더 성숙한 에코시스템

**최종 선택: Supabase Auth** ✅

이유: DB가 Supabase이므로 RLS와 완벽 통합, 별도 서비스 없이 관리 가능

```typescript
// lib/supabase/client.ts
import { createBrowserClient } from '@supabase/ssr'

export function createClient() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  )
}

// 사용 예시
const supabase = createClient()

// 회원가입
const { data, error } = await supabase.auth.signUp({
  email: 'user@example.com',
  password: 'password123'
})

// 로그인
await supabase.auth.signInWithPassword({
  email: 'user@example.com',
  password: 'password123'
})

// 소셜 로그인 (Google)
await supabase.auth.signInWithOAuth({
  provider: 'google',
  options: {
    redirectTo: 'https://timelock.app/auth/callback'
  }
})
```

---

## 결제

### **Stripe** ✅ 선택

**선택 이유**
- ✅ 한국 결제 지원 (카드, 간편결제)
- ✅ 구독 결제 자동화
- ✅ Webhook으로 이벤트 처리
- ✅ 개발자 친화적 API
- ✅ 테스트 환경 완벽 지원

**가격**
- 수수료: 3.4% + 50원/건 (국내 카드)
- 구독: 추가 수수료 없음

**구현 예시**
```typescript
// lib/stripe.ts
import Stripe from 'stripe'

export const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2023-10-16'
})

// 구독 결제 세션 생성
export async function createCheckoutSession(userId: string, priceId: string) {
  const session = await stripe.checkout.sessions.create({
    customer_email: user.email,
    line_items: [{ price: priceId, quantity: 1 }],
    mode: 'subscription',
    success_url: `${process.env.NEXT_PUBLIC_URL}/dashboard?success=true`,
    cancel_url: `${process.env.NEXT_PUBLIC_URL}/pricing?canceled=true`,
    metadata: {
      userId
    }
  })

  return session
}

// Webhook 처리
export async function handleStripeWebhook(event: Stripe.Event) {
  switch (event.type) {
    case 'checkout.session.completed':
      const session = event.data.object as Stripe.Checkout.Session
      // DB 업데이트: 사용자를 프리미엄으로 변경
      await updateUserSubscription(session.metadata.userId, 'premium')
      break

    case 'customer.subscription.deleted':
      // 구독 취소 처리
      break
  }
}
```

**Stripe Products 설정**
- **TIMELOCK Premium Monthly**: ₩5,900/월
- **TIMELOCK Premium Yearly**: ₩59,000/년 (16% 할인)

---

## 호스팅 및 인프라

### **Vercel** ✅ 선택

**선택 이유**
- ✅ Next.js 최적화
- ✅ 자동 HTTPS, 글로벌 CDN
- ✅ Git 기반 자동 배포
- ✅ 프리뷰 환경 자동 생성
- ✅ Edge Functions 지원
- ✅ 무료 티어: 100GB 대역폭/월

**가격**
- **Free**: $0 (Hobby 프로젝트)
- **Pro**: $20/월 (상업용, 무제한 팀원)

**배포 설정**
```bash
# Vercel CLI 설치
npm i -g vercel

# 배포
vercel --prod

# 환경 변수 설정
vercel env add NEXT_PUBLIC_SUPABASE_URL
vercel env add NEXT_PUBLIC_SUPABASE_ANON_KEY
vercel env add SUPABASE_SERVICE_ROLE_KEY
vercel env add STRIPE_SECRET_KEY
vercel env add STRIPE_WEBHOOK_SECRET
```

**대안 검토**
- ⚠️ **Netlify**: Vercel과 유사, Next.js는 Vercel이 더 나음
- ❌ **AWS Amplify**: 복잡함, Vercel이 더 간편
- ❌ **Railway/Render**: 서버 관리 필요, Serverless가 더 효율적

---

## 개발 도구 및 DevOps

### 1. 버전 관리

#### **GitHub** ✅

- Private Repository
- GitHub Actions (CI/CD)
- Branch 전략: `main` (production), `develop` (staging), `feature/*`

---

### 2. CI/CD

#### **GitHub Actions** ✅

**워크플로우 예시**
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'

      - name: Install dependencies
        run: npm ci

      - name: Run tests
        run: npm test

      - name: Run linter
        run: npm run lint

      - name: Type check
        run: npm run type-check

      - name: Build
        run: npm run build

      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          vercel-args: '--prod'
```

---

### 3. 코드 품질

#### **ESLint** + **Prettier** ✅

```json
// .eslintrc.json
{
  "extends": ["next/core-web-vitals", "prettier"],
  "rules": {
    "no-console": ["warn", { "allow": ["warn", "error"] }],
    "@typescript-eslint/no-unused-vars": "error"
  }
}

// .prettierrc
{
  "semi": false,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5"
}
```

---

### 4. 테스팅

#### **Vitest** + **React Testing Library** ✅

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: './tests/setup.ts'
  }
})

// tests/setup.ts
import '@testing-library/jest-dom'
```

**테스트 예시**
```typescript
// components/TimeBlockCard.test.tsx
import { render, screen } from '@testing-library/react'
import { TimeBlockCard } from './TimeBlockCard'

describe('TimeBlockCard', () => {
  it('renders time block title', () => {
    render(<TimeBlockCard title="행정법" duration={90} />)
    expect(screen.getByText('행정법')).toBeInTheDocument()
  })

  it('displays duration in minutes', () => {
    render(<TimeBlockCard title="행정법" duration={90} />)
    expect(screen.getByText('90분')).toBeInTheDocument()
  })
})
```

---

## 모니터링 및 분석

### 1. 에러 모니터링

#### **Sentry** ✅

**선택 이유**
- ✅ 프론트엔드 + 백엔드 에러 추적
- ✅ 소스맵 지원
- ✅ 사용자 피드백 수집
- ✅ 무료 티어: 5,000 이벤트/월

```typescript
// sentry.client.config.ts
import * as Sentry from '@sentry/nextjs'

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  tracesSampleRate: 1.0,
  environment: process.env.NODE_ENV
})
```

---

### 2. 사용자 분석

#### **Vercel Analytics** + **Plausible** ✅

**Vercel Analytics**
- 웹 바이탈 (Core Web Vitals) 자동 수집
- 무료 (Vercel Pro 플랜 포함)

**Plausible Analytics**
- 개인정보 보호 중시 (GDPR 준수)
- 쿠키 없이 작동
- 경량 (< 1KB)
- 가격: $9/월 (10,000 페이지뷰)

**대안 검토**
- ❌ **Google Analytics**: 개인정보 우려, 무겁고 복잡
- ⚠️ **PostHog**: 오픈소스, 자체 호스팅 가능하나 설정 복잡

---

## 비용 추정

### MVP 단계 (DAU 100)

| 서비스 | 플랜 | 월 비용 |
|--------|------|---------|
| **Vercel** | Hobby (Free) | ₩0 |
| **Supabase** | Free (500MB DB) | ₩0 |
| **Upstash Redis** | Free (10K 요청/일) | ₩0 |
| **Stripe** | 수수료만 (거래 발생 시) | ~₩0 |
| **Sentry** | Developer (5K 이벤트/월) | ₩0 |
| **Plausible** | 10K 페이지뷰/월 | $9 (₩12,000) |
| **도메인** | .com | ₩15,000/년 (₩1,250/월) |
| **총합** | | **₩13,250/월** |

### Growth 단계 (DAU 1,000)

| 서비스 | 플랜 | 월 비용 |
|--------|------|---------|
| **Vercel** | Pro | $20 (₩26,000) |
| **Supabase** | Pro (8GB DB) | $25 (₩32,500) |
| **Upstash Redis** | Pay as you go | ~₩10,000 |
| **Stripe** | 수수료 3.4% + ₩50 | ~₩50,000 (구독 수익 기준) |
| **Sentry** | Team (50K 이벤트/월) | $26 (₩34,000) |
| **Plausible** | 100K 페이지뷰/월 | $19 (₩25,000) |
| **총합** | | **₩177,500/월** |

### Scale 단계 (DAU 10,000)

| 서비스 | 플랜 | 월 비용 |
|--------|------|---------|
| **Vercel** | Pro + Add-ons | ~₩100,000 |
| **Supabase** | Pro + Add-ons | ~₩150,000 |
| **Upstash Redis** | Pay as you go | ~₩50,000 |
| **Stripe** | 수수료 | ~₩500,000 |
| **Sentry** | Business | ~₩100,000 |
| **Plausible** | 1M 페이지뷰/월 | $69 (₩90,000) |
| **총합** | | **₩990,000/월** |

---

## 기술 검증 체크리스트

### Phase 1: MVP 개발 시작 전 (2주)

- [ ] **Next.js 14 PWA 프로토타입** 작성 (2일)
  - [ ] next-pwa 설정
  - [ ] Manifest.json 생성
  - [ ] 모바일에서 "홈 화면에 추가" 테스트

- [ ] **무음 알림 API 검증** (3일)
  - [ ] Screen Wake Lock API 테스트 (iOS Safari, Chrome)
  - [ ] Vibration API 테스트 (Android Chrome)
  - [ ] MediaStream API (Device Flash) 테스트 (Android)
  - [ ] 폴백 로직 구현 및 테스트

- [ ] **Supabase 세팅** (2일)
  - [ ] 프로젝트 생성
  - [ ] 스키마 작성 및 마이그레이션
  - [ ] Row Level Security 정책 설정
  - [ ] Supabase Auth 테스트

- [ ] **Stripe 테스트 모드** (1일)
  - [ ] Stripe 계정 생성
  - [ ] 테스트 결제 플로우 구현
  - [ ] Webhook 로컬 테스트 (Stripe CLI)

- [ ] **성능 벤치마크** (1일)
  - [ ] Lighthouse 점수 목표: 90+ (Performance, Accessibility, Best Practices, SEO)
  - [ ] Core Web Vitals: LCP < 2.5s, FID < 100ms, CLS < 0.1

---

### Phase 2: MVP 개발 중 (4주)

- [ ] **컴포넌트 단위 테스트** (지속적)
  - [ ] React Testing Library로 핵심 컴포넌트 커버리지 80% 이상

- [ ] **API 통합 테스트** (1주차)
  - [ ] Supabase CRUD 작업 검증
  - [ ] 인증 플로우 End-to-End 테스트

- [ ] **크로스 브라우저 테스트** (2주차)
  - [ ] iOS Safari, Chrome (iOS)
  - [ ] Android Chrome, Samsung Internet
  - [ ] Desktop: Chrome, Firefox, Safari, Edge

- [ ] **보안 감사** (3주차)
  - [ ] OWASP Top 10 체크
  - [ ] SQL Injection 방지 (Supabase RLS)
  - [ ] XSS 방지 (React 기본 보호 + DOMPurify)
  - [ ] CSRF 방지 (SameSite 쿠키)
  - [ ] Rate Limiting (Upstash Redis)

---

### Phase 3: 베타 출시 전 (1주)

- [ ] **부하 테스트**
  - [ ] k6 또는 Artillery로 동시 사용자 100명 시뮬레이션
  - [ ] API 응답 시간 < 200ms (p95)

- [ ] **배포 파이프라인 검증**
  - [ ] GitHub Actions CI/CD 테스트
  - [ ] Vercel 프로덕션 배포 확인
  - [ ] 환경 변수 검증

- [ ] **모니터링 설정**
  - [ ] Sentry 에러 알림 설정
  - [ ] Vercel Analytics 대시보드 확인
  - [ ] Plausible 이벤트 추적 설정

---

## 다음 단계

1. ✅ **프로토타입 개발** (1주)
   - Next.js 14 + PWA 기본 세팅
   - 무음 알림 3가지 방식 구현 및 테스트
   - Supabase 연동 기본 CRUD

2. ✅ **MVP 기능 개발** (4주)
   - 타임블로킹 스케줄러 UI
   - 무음 타이머 통합
   - 일일/주간 리포트
   - Supabase Auth 통합

3. ✅ **베타 테스트** (2주)
   - 독서실 수험생 10명 테스터 모집
   - 피드백 수집 및 개선

4. ✅ **프리미엄 기능 개발** (4주)
   - 집중 패턴 히트맵
   - Stripe 결제 통합
   - AI 분석 기초

---

**작성일**: 2025-12-19
**작성자**: AICANSMILE / 박소영
**버전**: 1.0

# TIMELOCK 개발 환경 세팅 가이드

이 가이드는 TIMELOCK 프로젝트의 개발 환경을 처음부터 세팅하는 단계별 지침입니다.

## 사전 요구사항

다음 도구들이 설치되어 있어야 합니다:

- **Node.js**: v20.x 이상 ([다운로드](https://nodejs.org/))
- **Git**: 최신 버전 ([다운로드](https://git-scm.com/))
- **VS Code**: 권장 에디터 ([다운로드](https://code.visualstudio.com/))

버전 확인:
```bash
node --version  # v20.x.x 이상
npm --version   # v10.x.x 이상
git --version   # v2.x.x 이상
```

---

## Step 1: Next.js 프로젝트 생성

### 1.1 프로젝트 생성

터미널을 열고 다음 명령어를 실행하세요:

```bash
# C:\TIMELOCK 디렉토리에서 실행
cd C:\TIMELOCK

# Next.js 프로젝트 생성 (대화형 프롬프트)
npx create-next-app@latest timelock
```

**프롬프트 응답:**
```
✔ Would you like to use TypeScript? … Yes
✔ Would you like to use ESLint? … Yes
✔ Would you like to use Tailwind CSS? … Yes
✔ Would you like to use `src/` directory? … Yes
✔ Would you like to use App Router? … Yes
✔ Would you like to customize the default import alias (@/*)? … No
```

### 1.2 프로젝트 디렉토리 이동

```bash
cd timelock
```

---

## Step 2: 필수 패키지 설치

### 2.1 PWA 관련

```bash
npm install next-pwa
npm install -D webpack
```

### 2.2 Supabase (데이터베이스 & 인증)

```bash
npm install @supabase/ssr @supabase/supabase-js
```

### 2.3 상태 관리 & 데이터 페칭

```bash
npm install zustand
npm install @tanstack/react-query
npm install @tanstack/react-query-devtools
```

### 2.4 폼 관리 & 검증

```bash
npm install react-hook-form
npm install @hookform/resolvers
npm install zod
```

### 2.5 차트 & 시각화

```bash
npm install recharts
npm install date-fns  # 날짜 처리
```

### 2.6 Stripe (결제)

```bash
npm install stripe @stripe/stripe-js
```

### 2.7 UI 컴포넌트 (shadcn/ui)

```bash
# shadcn/ui 초기화
npx shadcn-ui@latest init
```

**프롬프트 응답:**
```
✔ Would you like to use TypeScript? … yes
✔ Which style would you like to use? › Default
✔ Which color would you like to use as base color? › Slate
✔ Where is your global CSS file? › src/app/globals.css
✔ Would you like to use CSS variables for colors? › yes
✔ Are you using a custom tailwind prefix? › no
✔ Where is your tailwind.config.js located? › tailwind.config.ts
✔ Configure the import alias for components: › @/components
✔ Configure the import alias for utils: › @/lib/utils
✔ Are you using React Server Components? › yes
```

필요한 컴포넌트 설치:
```bash
npx shadcn-ui@latest add button
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add calendar
npx shadcn-ui@latest add card
npx shadcn-ui@latest add tabs
npx shadcn-ui@latest add toast
npx shadcn-ui@latest add dropdown-menu
npx shadcn-ui@latest add switch
npx shadcn-ui@latest add slider
```

### 2.8 개발 도구

```bash
npm install -D vitest @vitejs/plugin-react
npm install -D @testing-library/react @testing-library/jest-dom
npm install -D prettier prettier-plugin-tailwindcss
```

---

## Step 3: 프로젝트 구조 생성

다음 디렉토리 구조를 생성하세요:

```
timelock/
├── src/
│   ├── app/
│   │   ├── (auth)/
│   │   │   ├── login/
│   │   │   │   └── page.tsx
│   │   │   └── signup/
│   │   │       └── page.tsx
│   │   ├── dashboard/
│   │   │   ├── page.tsx
│   │   │   └── layout.tsx
│   │   ├── analytics/
│   │   │   └── page.tsx
│   │   ├── settings/
│   │   │   └── page.tsx
│   │   ├── api/
│   │   │   ├── timeblocks/
│   │   │   │   └── route.ts
│   │   │   ├── analytics/
│   │   │   │   └── route.ts
│   │   │   └── webhooks/
│   │   │       └── stripe/
│   │   │           └── route.ts
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   └── globals.css
│   ├── components/
│   │   ├── ui/              # shadcn/ui 컴포넌트
│   │   ├── timeblock/
│   │   │   ├── TimeBlockCard.tsx
│   │   │   ├── TimeBlockForm.tsx
│   │   │   └── Timer.tsx
│   │   ├── analytics/
│   │   │   ├── DailySummary.tsx
│   │   │   ├── WeeklyChart.tsx
│   │   │   └── Heatmap.tsx
│   │   ├── notifications/
│   │   │   ├── ScreenFlash.tsx
│   │   │   ├── VibrationAlert.tsx
│   │   │   └── NotificationSettings.tsx
│   │   └── layout/
│   │       ├── Header.tsx
│   │       ├── Sidebar.tsx
│   │       └── Footer.tsx
│   ├── lib/
│   │   ├── supabase/
│   │   │   ├── client.ts
│   │   │   ├── server.ts
│   │   │   └── middleware.ts
│   │   ├── stripe/
│   │   │   └── client.ts
│   │   ├── notifications/
│   │   │   ├── screenFlash.ts
│   │   │   ├── vibration.ts
│   │   │   └── deviceFlash.ts
│   │   └── utils.ts
│   ├── hooks/
│   │   ├── useTimeBlocks.ts
│   │   ├── useTimer.ts
│   │   ├── useNotification.ts
│   │   └── useAuth.ts
│   ├── store/
│   │   ├── timeBlockStore.ts
│   │   ├── timerStore.ts
│   │   └── userStore.ts
│   └── types/
│       ├── timeblock.ts
│       ├── user.ts
│       └── analytics.ts
├── public/
│   ├── icons/
│   │   ├── icon-192x192.png
│   │   ├── icon-512x512.png
│   │   └── favicon.ico
│   └── manifest.json
├── .env.local
├── .env.example
├── .gitignore
├── next.config.js
├── package.json
├── tsconfig.json
├── tailwind.config.ts
├── vitest.config.ts
└── README.md
```

---

## Step 4: 설정 파일 작성

### 4.1 PWA 설정 (`next.config.js`)

기존 `next.config.js`를 다음으로 교체:

```javascript
/** @type {import('next').NextConfig} */
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
          maxAgeSeconds: 365 * 24 * 60 * 60 // 1년
        }
      }
    },
    {
      urlPattern: /^https:\/\/fonts\.(?:googleapis)\.com\/.*/i,
      handler: 'StaleWhileRevalidate',
      options: {
        cacheName: 'google-fonts-stylesheets',
        expiration: {
          maxEntries: 4,
          maxAgeSeconds: 7 * 24 * 60 * 60 // 1주일
        }
      }
    },
    {
      urlPattern: /\.(?:eot|otf|ttc|ttf|woff|woff2|font.css)$/i,
      handler: 'StaleWhileRevalidate',
      options: {
        cacheName: 'static-font-assets',
        expiration: {
          maxEntries: 4,
          maxAgeSeconds: 7 * 24 * 60 * 60 // 1주일
        }
      }
    },
    {
      urlPattern: /\.(?:jpg|jpeg|gif|png|svg|ico|webp)$/i,
      handler: 'StaleWhileRevalidate',
      options: {
        cacheName: 'static-image-assets',
        expiration: {
          maxEntries: 64,
          maxAgeSeconds: 24 * 60 * 60 // 24시간
        }
      }
    }
  ]
})

const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  experimental: {
    optimizePackageImports: ['@supabase/ssr', 'recharts', 'date-fns']
  }
}

module.exports = withPWA(nextConfig)
```

### 4.2 PWA Manifest (`public/manifest.json`)

```json
{
  "name": "TIMELOCK - 무음 타임블로킹",
  "short_name": "TIMELOCK",
  "description": "독서실에서도 눈치 안 보고 쓰는 무음 타이머. 계획부터 실행, 분석까지 하나의 앱에서.",
  "theme_color": "#000000",
  "background_color": "#ffffff",
  "display": "standalone",
  "orientation": "portrait",
  "scope": "/",
  "start_url": "/",
  "icons": [
    {
      "src": "/icons/icon-192x192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "any maskable"
    },
    {
      "src": "/icons/icon-512x512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "any maskable"
    }
  ],
  "categories": ["productivity", "education"],
  "shortcuts": [
    {
      "name": "오늘의 계획",
      "short_name": "계획",
      "description": "오늘의 타임블록 확인",
      "url": "/dashboard",
      "icons": [{ "src": "/icons/icon-192x192.png", "sizes": "192x192" }]
    },
    {
      "name": "타이머 시작",
      "short_name": "타이머",
      "description": "빠른 타이머 시작",
      "url": "/dashboard?timer=start",
      "icons": [{ "src": "/icons/icon-192x192.png", "sizes": "192x192" }]
    }
  ]
}
```

### 4.3 환경 변수 (`.env.example`)

```env
# Supabase
NEXT_PUBLIC_SUPABASE_URL=your_supabase_project_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key

# Stripe
STRIPE_SECRET_KEY=sk_test_xxx
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx

# Upstash Redis (옵션)
UPSTASH_REDIS_REST_URL=your_redis_url
UPSTASH_REDIS_REST_TOKEN=your_redis_token

# App
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

### 4.4 `.env.local` 생성

```bash
# .env.example을 복사
cp .env.example .env.local

# 실제 값으로 채우기 (아직은 테스트 값 사용)
```

### 4.5 TypeScript 설정 (`tsconfig.json`)

이미 생성되어 있지만, 다음 내용 확인:

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["DOM", "DOM.Iterable", "ES2022"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

### 4.6 Prettier 설정 (`.prettierrc`)

```json
{
  "semi": false,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5",
  "printWidth": 100,
  "plugins": ["prettier-plugin-tailwindcss"]
}
```

### 4.7 ESLint 설정 (`.eslintrc.json`)

```json
{
  "extends": ["next/core-web-vitals", "prettier"],
  "rules": {
    "no-console": ["warn", { "allow": ["warn", "error"] }],
    "@typescript-eslint/no-unused-vars": ["error", { "argsIgnorePattern": "^_" }],
    "react-hooks/exhaustive-deps": "warn"
  }
}
```

### 4.8 Vitest 설정 (`vitest.config.ts`)

```typescript
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: './tests/setup.ts',
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})
```

### 4.9 테스트 설정 (`tests/setup.ts`)

```typescript
import '@testing-library/jest-dom'
import { expect, afterEach } from 'vitest'
import { cleanup } from '@testing-library/react'
import * as matchers from '@testing-library/jest-dom/matchers'

expect.extend(matchers)

afterEach(() => {
  cleanup()
})
```

---

## Step 5: Git 설정

### 5.1 .gitignore 확인

`.gitignore` 파일에 다음 내용이 포함되어 있는지 확인:

```gitignore
# See https://help.github.com/articles/ignoring-files/ for more about ignoring files.

# dependencies
/node_modules
/.pnp
.pnp.js

# testing
/coverage

# next.js
/.next/
/out/

# production
/build

# misc
.DS_Store
*.pem

# debug
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# local env files
.env*.local
.env

# vercel
.vercel

# typescript
*.tsbuildinfo
next-env.d.ts

# PWA files
**/public/workbox-*.js
**/public/sw.js
**/public/worker-*.js
**/public/sw.js.map
**/public/workbox-*.js.map
**/public/worker-*.js.map
```

### 5.2 Git 초기화 및 첫 커밋

```bash
git init
git add .
git commit -m "Initial setup: Next.js + PWA + TypeScript + Tech Stack"
```

### 5.3 GitHub 리포지토리 연결

```bash
# 이미 GitHub 리포지토리가 있으므로 연결
git remote add origin https://github.com/psoy/TIMELOCK.git
git branch -M main
git push -u origin main
```

---

## Step 6: 개발 서버 실행

### 6.1 개발 서버 시작

```bash
npm run dev
```

브라우저에서 http://localhost:3000 을 열어 Next.js 기본 페이지 확인

### 6.2 빌드 테스트

```bash
npm run build
npm run start
```

---

## Step 7: VS Code 설정 (권장)

### 7.1 VS Code Extensions 설치

다음 확장을 설치하세요:

1. **ESLint** - dbaeumer.vscode-eslint
2. **Prettier** - esbenp.prettier-vscode
3. **Tailwind CSS IntelliSense** - bradlc.vscode-tailwindcss
4. **TypeScript Vue Plugin (Volar)** - Vue.vscode-typescript-vue-plugin
5. **Error Lens** - usernamehw.errorlens

### 7.2 VS Code 설정 (`.vscode/settings.json`)

프로젝트 루트에 `.vscode/settings.json` 생성:

```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": "explicit"
  },
  "typescript.tsdk": "node_modules/typescript/lib",
  "typescript.enablePromptUseWorkspaceTsdk": true,
  "tailwindCSS.experimental.classRegex": [
    ["cva\\(([^)]*)\\)", "[\"'`]([^\"'`]*).*?[\"'`]"],
    ["cx\\(([^)]*)\\)", "(?:'|\"|`)([^']*)(?:'|\"|`)"]
  ]
}
```

---

## Step 8: 다음 단계

개발 환경 세팅이 완료되었습니다! 이제 다음 작업을 진행할 수 있습니다:

### 8.1 Supabase 프로젝트 생성
1. https://supabase.com 에 가입
2. 새 프로젝트 생성
3. Database 스키마 생성 (tech_stack.md 참조)
4. API Keys 복사하여 `.env.local`에 입력

### 8.2 무음 알림 프로토타입 개발
1. `src/lib/notifications/screenFlash.ts` 구현
2. `src/lib/notifications/vibration.ts` 구현
3. 테스트 페이지 생성하여 검증

### 8.3 기본 컴포넌트 개발
1. 타임블록 카드 컴포넌트
2. 타이머 컴포넌트
3. 대시보드 레이아웃

---

## 트러블슈팅

### 문제: `npm install` 시 에러 발생

```bash
# npm 캐시 클리어
npm cache clean --force

# node_modules 삭제 후 재설치
rm -rf node_modules
npm install
```

### 문제: PWA가 로드되지 않음

1. 개발 모드에서는 PWA가 비활성화됩니다
2. 프로덕션 빌드 후 테스트: `npm run build && npm run start`
3. 브라우저 개발자 도구 → Application → Service Workers 확인

### 문제: TypeScript 에러

```bash
# TypeScript 재시작 (VS Code)
Ctrl+Shift+P → "TypeScript: Restart TS Server"

# 타입 체크
npm run type-check
```

---

## 체크리스트

개발 환경 세팅 완료 체크리스트:

- [ ] Node.js v20+ 설치 확인
- [ ] Next.js 프로젝트 생성 완료
- [ ] 모든 필수 패키지 설치 완료
- [ ] PWA 설정 완료 (`manifest.json`, `next.config.js`)
- [ ] 환경 변수 파일 생성 (`.env.local`)
- [ ] 프로젝트 구조 생성 완료
- [ ] Git 초기화 및 첫 커밋 완료
- [ ] GitHub 리포지토리 연결 완료
- [ ] 개발 서버 정상 실행 (`npm run dev`)
- [ ] 빌드 테스트 성공 (`npm run build`)
- [ ] VS Code 설정 완료

---

**다음 문서**: [무음 알림 프로토타입 개발 가이드](./PROTOTYPE_GUIDE.md)

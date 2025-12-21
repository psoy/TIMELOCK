# OAuth 2.0 소셜 로그인 구현 가이드

TIMELOCK에서 Google과 Kakao 소셜 로그인을 사용하는 방법입니다.

---

## 구현된 기능

✅ **Google 로그인** - Google OAuth 2.0
✅ **Kakao 로그인** - Kakao OAuth 2.0
✅ **자동 회원가입** - 첫 로그인 시 자동으로 계정 생성
✅ **계정 연동** - 이메일로 기존 계정 자동 연결
✅ **JWT 토큰 발급** - 로그인 성공 시 access & refresh 토큰 반환

---

## 1. Google OAuth 설정

### 1.1 Google Cloud Console에서 프로젝트 생성

1. **Google Cloud Console** 접속: https://console.cloud.google.com/
2. 새 프로젝트 생성 또는 기존 프로젝트 선택
3. **API 및 서비스 > OAuth 동의 화면** 메뉴로 이동
4. 사용자 유형: **외부** 선택
5. 앱 정보 입력:
   - 앱 이름: `TIMELOCK`
   - 사용자 지원 이메일: 본인 이메일
   - 승인된 도메인: `localhost`, `vercel.app` 등
   - 개발자 연락처 정보: 본인 이메일

### 1.2 OAuth 2.0 클라이언트 ID 생성

1. **API 및 서비스 > 사용자 인증 정보** 메뉴로 이동
2. **+ 사용자 인증 정보 만들기 > OAuth 2.0 클라이언트 ID**
3. 애플리케이션 유형: **웹 애플리케이션**
4. 승인된 JavaScript 원본:
   ```
   http://localhost:3000
   http://localhost:8000
   https://your-production-domain.com
   ```
5. 승인된 리디렉션 URI:
   ```
   http://localhost:3000/auth/callback
   https://your-production-domain.com/auth/callback
   ```

### 1.3 환경 변수 설정

`.env` 파일에 추가:
```env
GOOGLE_CLIENT_ID=1234567890-abcdefghijklmnop.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your-secret-here
```

---

## 2. Kakao OAuth 설정

### 2.1 Kakao Developers에서 앱 생성

1. **Kakao Developers** 접속: https://developers.kakao.com/
2. 내 애플리케이션 > 애플리케이션 추가하기
3. 앱 이름: `TIMELOCK`
4. 사업자명: 개인 또는 회사명

### 2.2 플랫폼 설정

1. **앱 설정 > 플랫폼** 메뉴로 이동
2. **Web 플랫폼 등록**
   - 사이트 도메인: `http://localhost:3000`, `https://your-domain.com`

### 2.3 Kakao 로그인 활성화

1. **제품 설정 > Kakao 로그인** 메뉴로 이동
2. **Kakao 로그인 활성화** ON
3. **Redirect URI 등록**:
   ```
   http://localhost:3000/auth/callback
   https://your-production-domain.com/auth/callback
   ```

### 2.4 동의 항목 설정

1. **제품 설정 > Kakao 로그인 > 동의항목** 메뉴로 이동
2. 필수 동의 항목 설정:
   - **프로필 정보(닉네임/프로필 사진)**: 선택 동의
   - **카카오계정(이메일)**: **필수 동의** ⭐

### 2.5 환경 변수 설정

`.env` 파일에 추가:
```env
KAKAO_REST_API_KEY=your_kakao_rest_api_key_here
```

---

## 3. Backend API 엔드포인트

### 3.1 Google 로그인

```http
POST http://localhost:8000/api/auth/google/
Content-Type: application/json

{
  "id_token": "google_id_token_from_frontend"
}
```

**응답:**
```json
{
  "access": "jwt_access_token",
  "refresh": "jwt_refresh_token",
  "user": {
    "id": "uuid",
    "email": "user@gmail.com",
    "username": "Google User",
    "oauth_provider": "google",
    "profile_image": "https://lh3.googleusercontent.com/..."
  }
}
```

### 3.2 Kakao 로그인

```http
POST http://localhost:8000/api/auth/kakao/
Content-Type: application/json

{
  "access_token": "kakao_access_token_from_frontend"
}
```

**응답:**
```json
{
  "access": "jwt_access_token",
  "refresh": "jwt_refresh_token",
  "user": {
    "id": "uuid",
    "email": "user@kakao.com",
    "username": "Kakao User",
    "oauth_provider": "kakao",
    "profile_image": "http://k.kakaocdn.net/..."
  }
}
```

---

## 4. Frontend 연동 (React/Next.js)

### 4.1 Google 로그인 구현

#### 설치
```bash
npm install @react-oauth/google
```

#### 구현
```typescript
// app/login/page.tsx
'use client';

import { GoogleOAuthProvider, GoogleLogin } from '@react-oauth/google';

export default function LoginPage() {
  const handleGoogleSuccess = async (credentialResponse: any) => {
    try {
      const response = await fetch('http://localhost:8000/api/auth/google/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          id_token: credentialResponse.credential,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        // 토큰 저장
        localStorage.setItem('accessToken', data.access);
        localStorage.setItem('refreshToken', data.refresh);

        // 홈으로 리디렉트
        window.location.href = '/';
      } else {
        console.error('Login failed:', data.error);
      }
    } catch (error) {
      console.error('Error:', error);
    }
  };

  return (
    <GoogleOAuthProvider clientId={process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID!}>
      <div>
        <h1>Login to TIMELOCK</h1>
        <GoogleLogin
          onSuccess={handleGoogleSuccess}
          onError={() => console.log('Login Failed')}
        />
      </div>
    </GoogleOAuthProvider>
  );
}
```

### 4.2 Kakao 로그인 구현

#### 설치
```bash
npm install react-kakao-login
```

#### 구현
```typescript
// app/login/page.tsx
import KakaoLogin from 'react-kakao-login';

export default function LoginPage() {
  const handleKakaoSuccess = async (response: any) => {
    try {
      const backendResponse = await fetch('http://localhost:8000/api/auth/kakao/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          access_token: response.response.access_token,
        }),
      });

      const data = await backendResponse.json();

      if (backendResponse.ok) {
        // 토큰 저장
        localStorage.setItem('accessToken', data.access);
        localStorage.setItem('refreshToken', data.refresh);

        // 홈으로 리디렉트
        window.location.href = '/';
      } else {
        console.error('Login failed:', data.error);
      }
    } catch (error) {
      console.error('Error:', error);
    }
  };

  return (
    <div>
      <h1>Login to TIMELOCK</h1>
      <KakaoLogin
        token={process.env.NEXT_PUBLIC_KAKAO_APP_KEY!}
        onSuccess={handleKakaoSuccess}
        onFail={(error: any) => console.log(error)}
      />
    </div>
  );
}
```

### 4.3 환경 변수 (.env.local)

```env
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your_google_client_id
NEXT_PUBLIC_KAKAO_APP_KEY=your_kakao_javascript_key
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 5. 사용자 흐름

### 첫 로그인 (신규 사용자)
1. Google/Kakao 로그인 버튼 클릭
2. OAuth provider에서 인증
3. Backend가 사용자 정보 수신
4. **자동으로 계정 생성** (User + NotificationPreferences)
5. JWT 토큰 발급 및 반환
6. Frontend에서 토큰 저장 후 로그인 상태 유지

### 재로그인 (기존 사용자)
1. Google/Kakao 로그인 버튼 클릭
2. OAuth provider에서 인증
3. Backend가 `oauth_provider` + `oauth_id`로 사용자 찾기
4. JWT 토큰 발급 및 반환
5. Frontend에서 토큰 저장 후 로그인 상태 유지

### 계정 연동 (이메일이 같은 기존 계정)
1. 이미 이메일로 가입된 계정이 있는 경우
2. Backend가 이메일로 사용자 찾기
3. **자동으로 OAuth 정보 업데이트** (oauth_provider, oauth_id)
4. JWT 토큰 발급 및 반환

---

## 6. 보안 고려사항

### Backend 검증
- ✅ Google ID 토큰 서버 측 검증
- ✅ Kakao Access 토큰 API 호출로 검증
- ✅ 이메일 필수 확인
- ✅ OAuth provider별 고유 ID 저장

### 프론트엔드 보안
- ✅ HTTPS 사용 (프로덕션)
- ✅ 토큰을 httpOnly 쿠키에 저장 (권장)
- ✅ XSS 방지 (React 자동 escape)

### Django 설정
```python
# settings/base.py
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'https://your-production-domain.com',
]

GOOGLE_CLIENT_ID = config('GOOGLE_CLIENT_ID')
KAKAO_REST_API_KEY = config('KAKAO_REST_API_KEY')
```

---

## 7. 에러 처리

### Google 로그인 실패
```json
{
  "error": "Invalid Google token: Token used too late"
}
```
→ ID 토큰이 만료됨. 프론트엔드에서 재요청 필요.

### Kakao 로그인 실패
```json
{
  "error": "Email not provided by Kakao"
}
```
→ Kakao Developers에서 이메일 동의항목을 **필수**로 설정 필요.

### 일반 에러
```json
{
  "error": "id_token is required"
}
```
→ 요청 body에 필수 파라미터 누락.

---

## 8. 테스트

### curl로 테스트 (Google)
```bash
# 1. 프론트엔드에서 Google ID token 받기
# 2. Backend API 호출
curl -X POST http://localhost:8000/api/auth/google/ \
  -H "Content-Type: application/json" \
  -d '{"id_token":"your_google_id_token"}'
```

### curl로 테스트 (Kakao)
```bash
# 1. 프론트엔드에서 Kakao access token 받기
# 2. Backend API 호출
curl -X POST http://localhost:8000/api/auth/kakao/ \
  -H "Content-Type: application/json" \
  -d '{"access_token":"your_kakao_access_token"}'
```

---

## 9. 프로덕션 배포 체크리스트

### Backend
- [ ] `.env` 파일에 실제 OAuth 클라이언트 ID/Secret 설정
- [ ] `CORS_ALLOWED_ORIGINS`에 프로덕션 도메인 추가
- [ ] HTTPS 활성화
- [ ] PostgreSQL 연결 (SQLite에서 마이그레이션)

### Frontend
- [ ] `.env.local`에 실제 OAuth 클라이언트 ID 설정
- [ ] `NEXT_PUBLIC_API_URL`을 프로덕션 API URL로 변경
- [ ] Google Cloud Console에서 승인된 도메인 추가
- [ ] Kakao Developers에서 플랫폼 도메인 추가

### OAuth Provider 설정
- [ ] Google: 승인된 리디렉션 URI에 프로덕션 URL 추가
- [ ] Kakao: Redirect URI에 프로덕션 URL 추가
- [ ] Kakao: 비즈 앱 전환 (선택사항, 일일 사용자 수 제한 해제)

---

## 10. 참고 자료

- **Google OAuth 2.0**: https://developers.google.com/identity/protocols/oauth2
- **Google Sign-In (React)**: https://www.npmjs.com/package/@react-oauth/google
- **Kakao Login**: https://developers.kakao.com/docs/latest/ko/kakaologin/rest-api
- **Django REST Framework**: https://www.django-rest-framework.org/
- **Simple JWT**: https://django-rest-framework-simplejwt.readthedocs.io/

---

## 문제 해결

### Google ID 토큰 검증 실패
```
ValueError: Token used too late
```
→ 시스템 시간이 정확한지 확인. NTP 동기화 필요.

### Kakao 이메일 미제공
→ Kakao Developers > 동의항목에서 이메일을 **필수 동의**로 변경.

### CORS 에러
→ Django `settings/base.py`의 `CORS_ALLOWED_ORIGINS`에 프론트엔드 URL 추가.

---

**구현 완료!** 🎉
이제 TIMELOCK에서 Google과 Kakao 소셜 로그인을 사용할 수 있습니다.

# TIMELOCK Backend API Endpoints

Django REST Framework API 엔드포인트 문서

**Base URL**: `http://localhost:8000/api/`

---

## Authentication

### JWT Token Endpoints

#### 1. Obtain Token (Email + Password Login)
```http
POST /api/auth/token/
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access": "eyJhbGci...",  // 15분 유효
  "refresh": "eyJhbGci..."  // 7일 유효
}
```

#### 2. Refresh Token
```http
POST /api/auth/token/refresh/
```

**Request Body:**
```json
{
  "refresh": "eyJhbGci..."
}
```

**Response:**
```json
{
  "access": "eyJhbGci..."  // 새로운 access token
}
```

### OAuth 2.0 Social Login

#### 3. Google Login
```http
POST /api/auth/google/
```

**Request Body:**
```json
{
  "id_token": "google_id_token_from_frontend"
}
```

**Response:**
```json
{
  "access": "eyJhbGci...",
  "refresh": "eyJhbGci...",
  "user": {
    "id": "uuid",
    "email": "user@gmail.com",
    "username": "Google User",
    "oauth_provider": "google",
    "oauth_id": "123456789",
    "profile_image": "https://lh3.googleusercontent.com/..."
  }
}
```

**Features:**
- ✅ 자동 회원가입 (첫 로그인 시)
- ✅ 기존 계정 자동 연동 (이메일 기준)
- ✅ JWT 토큰 즉시 발급

#### 4. Kakao Login
```http
POST /api/auth/kakao/
```

**Request Body:**
```json
{
  "access_token": "kakao_access_token_from_frontend"
}
```

**Response:**
```json
{
  "access": "eyJhbGci...",
  "refresh": "eyJhbGci...",
  "user": {
    "id": "uuid",
    "email": "user@kakao.com",
    "username": "Kakao User",
    "oauth_provider": "kakao",
    "oauth_id": "987654321",
    "profile_image": "http://k.kakaocdn.net/..."
  }
}
```

**Features:**
- ✅ 자동 회원가입 (첫 로그인 시)
- ✅ 기존 계정 자동 연동 (이메일 기준)
- ✅ JWT 토큰 즉시 발급

---

## Users API

**Base**: `/api/auth/`

### User Management

#### 1. Get Current User
```http
GET /api/auth/users/me/
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "username": "username",
  "oauth_provider": null,
  "timezone": "Asia/Seoul",
  "is_premium": false,
  "is_premium_active": false,
  "notification_preferences": {...},
  "created_at": "2025-12-20T..."
}
```

#### 2. Update Current User
```http
PATCH /api/auth/users/me/
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "username": "new_username",
  "timezone": "America/New_York"
}
```

#### 3. Change Password
```http
POST /api/auth/users/change-password/
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "old_password": "current123",
  "new_password": "newpass123",
  "new_password_confirm": "newpass123"
}
```

### Notification Preferences

#### 4. Get Notification Preferences
```http
GET /api/auth/users/notifications/
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "id": "uuid",
  "sound_enabled": false,
  "screen_flash_enabled": true,
  "vibration_enabled": true,
  "device_flash_enabled": false,
  "flash_pattern": {
    "duration": 500,
    "count": 3,
    "interval": 200,
    "color": "#10b981"
  }
}
```

#### 5. Update Notification Preferences
```http
PATCH /api/auth/users/notifications/
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "screen_flash_enabled": false,
  "vibration_enabled": true
}
```

---

## Plans API

**Base**: `/api/plans/`

### Daily Plans

#### 1. List Daily Plans
```http
GET /api/plans/daily-plans/
Authorization: Bearer {access_token}

# Query params:
?date=2025-12-20  # Filter by date
```

**Response:**
```json
{
  "count": 10,
  "next": "...",
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "date": "2025-12-20",
      "priorities": ["Task 1", "Task 2", "Task 3"],
      "completion_rate": "75.00",
      "time_blocks_count": 8,
      "completed_blocks_count": 6,
      "created_at": "..."
    }
  ]
}
```

#### 2. Get Today's Plan
```http
GET /api/plans/daily-plans/today/
Authorization: Bearer {access_token}
```

#### 3. Create Daily Plan
```http
POST /api/plans/daily-plans/
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "date": "2025-12-20",
  "priorities": ["Priority 1", "Priority 2", "Priority 3"],
  "brain_dump": "My thoughts for today..."
}
```

#### 4. Update Daily Plan (Auto-save)
```http
PATCH /api/plans/daily-plans/{id}/
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "priorities": ["Updated priority"],
  "brain_dump": "Updated thoughts"
}
```

#### 5. Recalculate Completion Rate
```http
POST /api/plans/daily-plans/{id}/recalculate/
Authorization: Bearer {access_token}
```

### Time Blocks

#### 6. List Time Blocks
```http
GET /api/plans/time-blocks/
Authorization: Bearer {access_token}

# Query params:
?daily_plan={uuid}  # Filter by plan
?date=2025-12-20    # Filter by date
```

**Response:**
```json
{
  "count": 8,
  "results": [
    {
      "id": "uuid",
      "period": "am",
      "hour": 9,
      "title": "Morning meeting",
      "category": "work",
      "planned_duration": 60,
      "actual_duration": 55,
      "is_completed": true,
      "execution_rate": "91.67"
    }
  ]
}
```

#### 7. Create Time Block
```http
POST /api/plans/time-blocks/
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "daily_plan_id": "uuid",
  "period": "am",
  "hour": 10,
  "title": "Focus work",
  "category": "study",
  "planned_duration": 60
}
```

#### 8. Mark Time Block Completed
```http
POST /api/plans/time-blocks/{id}/mark-completed/
Authorization: Bearer {access_token}
```

#### 9. Add Actual Time
```http
POST /api/plans/time-blocks/{id}/add-time/
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "minutes": 30
}
```

---

## Timer API

**Base**: `/api/timer/`

### Timer Sessions

#### 1. List Timer Sessions
```http
GET /api/timer/sessions/
Authorization: Bearer {access_token}

# Query params:
?status=running         # Filter by status
?date=2025-12-20       # Filter by date
?time_block={uuid}     # Filter by time block
```

**Response:**
```json
{
  "count": 5,
  "results": [
    {
      "id": "uuid",
      "time_block_title": "Focus work",
      "scheduled_duration": 3600,
      "elapsed_time": 2400,
      "status": "running",
      "completion_percentage": "66.67",
      "started_at": "2025-12-20T10:00:00+0900",
      "completed_at": null
    }
  ]
}
```

#### 2. Get Active Sessions
```http
GET /api/timer/sessions/active/
Authorization: Bearer {access_token}
```

#### 3. Get Today's Sessions
```http
GET /api/timer/sessions/today/
Authorization: Bearer {access_token}
```

#### 4. Start Timer Session
```http
POST /api/timer/sessions/
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "scheduled_duration": 3600,  // seconds
  "time_block_id": "uuid"      // optional
}
```

#### 5. Update Elapsed Time
```http
POST /api/timer/sessions/{id}/update-elapsed/
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "elapsed_seconds": 1200
}
```

#### 6. Pause Timer
```http
POST /api/timer/sessions/{id}/pause/
Authorization: Bearer {access_token}
```

#### 7. Resume Timer
```http
POST /api/timer/sessions/{id}/resume/
Authorization: Bearer {access_token}
```

#### 8. Complete Timer
```http
POST /api/timer/sessions/{id}/complete/
Authorization: Bearer {access_token}
```

#### 9. Cancel Timer
```http
POST /api/timer/sessions/{id}/cancel/
Authorization: Bearer {access_token}
```

---

## Statistics API

**Base**: `/api/stats/`

### Daily Statistics

#### 1. Get Daily Statistics
```http
GET /api/stats/daily/?date=YYYY-MM-DD
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `date` (optional): Target date in YYYY-MM-DD format. Defaults to today.

**Response:**
```json
{
  "date": "2025-12-20",
  "total_focus_time": 420,
  "total_blocks": 8,
  "completed_blocks": 6,
  "block_completion_rate": "75.00",
  "execution_rate": "87.50",
  "category_breakdown": {
    "study": 360,
    "work": 30,
    "rest": 30
  },
  "hourly_breakdown": [
    {
      "hour": 9,
      "focus_time": 60,
      "blocks": 1
    }
  ]
}
```

### Weekly Statistics

#### 2. Get Weekly Statistics
```http
GET /api/stats/weekly/?start_date=YYYY-MM-DD
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `start_date` (optional): Week start date (Monday). Defaults to current week.

**Response:**
```json
{
  "start_date": "2025-12-15",
  "end_date": "2025-12-21",
  "total_focus_time": 2940,
  "average_daily_focus": 420,
  "total_blocks": 56,
  "completed_blocks": 42,
  "block_completion_rate": "75.00",
  "execution_rate": "85.00",
  "daily_breakdown": [
    {
      "date": "2025-12-15",
      "focus_time": 420,
      "blocks": 8,
      "completed_blocks": 6
    }
  ],
  "category_breakdown": {
    "study": 2520,
    "work": 210,
    "rest": 210
  }
}
```

### Monthly Statistics

#### 3. Get Monthly Statistics
```http
GET /api/stats/monthly/?year=2025&month=12
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `year` (optional): Target year. Defaults to current year.
- `month` (optional): Target month (1-12). Defaults to current month.

**Response:**
```json
{
  "year": 2025,
  "month": 12,
  "total_focus_time": 12600,
  "average_daily_focus": 406,
  "total_blocks": 240,
  "completed_blocks": 180,
  "block_completion_rate": "75.00",
  "execution_rate": "83.00",
  "weekly_breakdown": [
    {
      "week_start": "2025-12-01",
      "week_end": "2025-12-07",
      "focus_time": 2940,
      "blocks": 56
    }
  ],
  "category_breakdown": {
    "study": 10800,
    "work": 900,
    "rest": 900
  },
  "most_productive_day": "Monday",
  "most_productive_hour": 9
}
```

### Heatmap

#### 4. Get GitHub-style Heatmap
```http
GET /api/stats/heatmap/?year=2025
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `year` (optional): Target year. Defaults to current year.

**Response:**
- Returns PNG image (Content-Type: image/png)
- GitHub-style 52-week contribution heatmap
- Color scale:
  - `#ebedf0` - No activity
  - `#9be9a8` - < 1 hour
  - `#40c463` - 1-3 hours
  - `#30a14e` - 3-5 hours
  - `#216e39` - 5+ hours

**Example:**
```bash
curl -X GET "http://localhost:8000/api/stats/heatmap/?year=2025" \
  -H "Authorization: Bearer {access_token}" \
  -o heatmap.png
```

---

## Response Formats

### Success Response
```json
{
  "data": {...}
}
```

### Error Response
```json
{
  "detail": "Error message",
  "code": "error_code"
}
```

### Validation Error
```json
{
  "field_name": ["Error message for this field"],
  "another_field": ["Another error message"]
}
```

---

## Status Codes

- `200 OK` - Success
- `201 Created` - Resource created
- `204 No Content` - Success with no response body
- `400 Bad Request` - Validation error
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Permission denied
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

---

## Testing with curl

### 1. Login and save token
```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@timelock.com","password":"admin123"}' \
  | grep -o '"access":"[^"]*"' | cut -d'"' -f4)
```

### 2. Get current user
```bash
curl -X GET http://localhost:8000/api/auth/users/me/ \
  -H "Authorization: Bearer $TOKEN"
```

### 3. Create daily plan
```bash
curl -X POST http://localhost:8000/api/plans/daily-plans/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2025-12-20",
    "priorities": ["Task 1", "Task 2"],
    "brain_dump": "Today I will focus on..."
  }'
```

### 4. Start timer
```bash
curl -X POST http://localhost:8000/api/timer/sessions/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "scheduled_duration": 3600
  }'
```

---

## Notes

- All timestamps are in ISO 8601 format with timezone
- UUIDs are used for all primary keys
- Pagination is enabled for list endpoints (50 items per page)
- JWT access token expires after 15 minutes
- JWT refresh token expires after 7 days
- Auto-refresh tokens are enabled (new refresh token on refresh)

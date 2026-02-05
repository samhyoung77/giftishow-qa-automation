# Google Sheets 설정 및 템플릿 생성 가이드

## 📋 목차
1. [Google Cloud 설정](#1-google-cloud-설정)
2. [Google Sheets 생성](#2-google-sheets-생성)
3. [템플릿 자동 생성](#3-템플릿-자동-생성)
4. [시트 구조 설명](#4-시트-구조-설명)
5. [사용 방법](#5-사용-방법)

---

## 1. Google Cloud 설정

### 1-1. Google Cloud Console 접속

https://console.cloud.google.com 접속

### 1-2. 프로젝트 생성

1. 상단의 프로젝트 선택 드롭다운 클릭
2. "새 프로젝트" 클릭
3. 프로젝트 이름 입력: `Giftishow-Test`
4. "만들기" 클릭

### 1-3. API 활성화

**Google Sheets API 활성화**:
1. 좌측 메뉴 → "API 및 서비스" → "라이브러리"
2. 검색: "Google Sheets API"
3. "Google Sheets API" 클릭
4. "사용" 버튼 클릭

**Google Drive API 활성화**:
1. 다시 라이브러리로 이동
2. 검색: "Google Drive API"
3. "Google Drive API" 클릭
4. "사용" 버튼 클릭

### 1-4. 서비스 계정 생성

1. 좌측 메뉴 → "API 및 서비스" → "사용자 인증 정보"
2. 상단 "사용자 인증 정보 만들기" → "서비스 계정" 선택
3. 서비스 계정 세부정보:
   - **이름**: `giftishow-test-automation`
   - **설명**: `Giftishow 자동화 테스트용 서비스 계정`
4. "만들고 계속하기" 클릭
5. 역할 부여:
   - **역할 선택**: "편집자" 또는 "기본" → "편집자"
6. "계속" 클릭
7. "완료" 클릭

### 1-5. JSON 키 파일 다운로드

1. 생성된 서비스 계정 목록에서 방금 만든 계정 클릭
2. 상단 "키" 탭 클릭
3. "키 추가" → "새 키 만들기"
4. 키 유형: **JSON** 선택
5. "만들기" 클릭
6. JSON 파일 자동 다운로드됨

**다운로드된 파일 처리**:
```powershell
# PowerShell에서 실행
# 다운로드 폴더의 JSON 파일을 프로젝트로 이동
cd E:\claude_code\giftishow_test

# 파일명 예시: giftishow-test-123456-a1b2c3d4e5f6.json
# 이름을 credentials.json으로 변경하여 복사
copy "$env:USERPROFILE\Downloads\giftishow-test-*.json" credentials.json

# 파일 확인
dir credentials.json
```

**중요**: `credentials.json` 파일 내용 확인
```json
{
  "type": "service_account",
  "project_id": "giftishow-test-123456",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...",
  "client_email": "giftishow-test-automation@giftishow-test-123456.iam.gserviceaccount.com",
  "client_id": "...",
  ...
}
```

`client_email` 값을 복사해두세요 (다음 단계에서 사용)

---

## 2. Google Sheets 생성

### 2-1. 새 Spreadsheet 생성

1. https://sheets.google.com 접속
2. 빈 스프레드시트 만들기
3. 제목 변경: **"Giftishow Test Results"**

### 2-2. 서비스 계정과 공유

1. 우측 상단 "공유" 버튼 클릭
2. `credentials.json`에서 복사한 `client_email` 붙여넣기
   ```
   예: giftishow-test-automation@giftishow-test-123456.iam.gserviceaccount.com
   ```
3. 권한: **편집자** 선택
4. "전송" 클릭 (알림 전송 체크 해제 가능)

### 2-3. Spreadsheet URL 복사

브라우저 주소창의 URL 전체 복사:
```
https://docs.google.com/spreadsheets/d/1ABC...XYZ/edit#gid=0
```

### 2-4. .env 파일에 URL 설정

`.env` 파일 열어서 수정:
```env
GOOGLE_SHEET_URL=https://docs.google.com/spreadsheets/d/YOUR_ACTUAL_SHEET_ID/edit
```

---

## 3. 템플릿 자동 생성

### 방법 1: 배치 파일 실행 (권장)

```powershell
# 더블클릭 또는 PowerShell에서 실행
.\create_sheets.bat
```

### 방법 2: Python 직접 실행

```powershell
# 가상환경 활성화
.\venv\Scripts\Activate.ps1

# 스크립트 실행
python utils\create_sheets_template.py
```

### 실행 결과

```
============================================================
Giftishow Test Results - Google Sheets 템플릿 생성
============================================================

[1/5] Google Sheets API 인증 중...
✓ 인증 성공

[2/5] Spreadsheet 열기...
URL: https://docs.google.com/spreadsheets/d/...
✓ 'Giftishow Test Results' 열기 성공

[3/5] TestCase_Template 시트 생성 중...
  - 기존 시트 삭제됨
✓ TestCase_Template 시트 생성 완료 (6개 샘플 포함)

[4/5] TestResults 시트 생성 중...
  - 기존 시트 삭제됨
✓ TestResults 시트 생성 완료 (샘플 2건)

[5/5] TestSummary 시트 생성 중...
  - 기존 시트 삭제됨
✓ TestSummary 시트 생성 완료

[보너스] DailyTrend 시트 생성 중...
✓ DailyTrend 시트 생성 완료

============================================================
✓ 모든 시트 생성 완료!
============================================================
```

---

## 4. 시트 구조 설명

### Sheet 1: TestCase_Template

**목적**: 테스트 케이스 정의 및 관리

**컬럼 구조** (10개):

| 컬럼 | 설명 | 예시 |
|------|------|------|
| **TC ID** | 테스트 케이스 고유 ID | GS_LOGIN_001 |
| **Category** | 기능 분류 | Authentication, Product, Cart |
| **Scenario Name** | 시나리오명 | 정상 로그인 |
| **Pre-condition** | 선행 조건 | 1. 유효한 계정 존재<br>2. 로그인 페이지 접근 가능 |
| **Test Steps** | 테스트 단계 | 1. 로그인 페이지 접속<br>2. ID 입력<br>3. PW 입력 |
| **Locators** | UI 요소 식별자 | id: username<br>id: password |
| **Expected Result** | 예상 결과 | 메인 페이지 이동 완료 |
| **Priority** | 우선순위 | High / Medium / Low |
| **Automation Status** | 자동화 상태 | ✅ Done / In Progress / Pending |
| **Note** | 비고 | 추가 정보 |

**포함된 샘플 테스트 케이스**:
1. `GS_LOGIN_001` - 정상 로그인
2. `GS_LOGIN_002` - 잘못된 비밀번호 로그인
3. `GS_PRODUCT_001` - 상품 검색
4. `GS_PRODUCT_002` - 상품 상세 조회
5. `GS_CART_001` - 장바구니 추가
6. `GS_ORDER_001` - 주문하기

---

### Sheet 2: TestResults

**목적**: 테스트 실행 결과 자동 기록

**컬럼 구조** (20개):

| 컬럼 | 설명 | 자동/수동 |
|------|------|---------|
| **Timestamp** | 실행 시간 | 자동 |
| **Test Run ID** | 배치 실행 ID | 자동 |
| **TC ID** | 테스트 케이스 ID | 자동 |
| **Page** | 페이지명 | 자동 |
| **Category** | 카테고리 | 자동 |
| **Scenario Name** | 시나리오명 | 자동 |
| **Browser** | 브라우저 | 자동 |
| **OS** | 운영체제 | 자동 |
| **Login** | 로그인 결과 | 자동 |
| **Product Search** | 상품 검색 결과 | 자동 |
| **Product Detail** | 상품 상세 결과 | 자동 |
| **Cart** | 장바구니 결과 | 자동 |
| **Order** | 주문 결과 | 자동 |
| **Overall Result** | 전체 결과 (PASS/FAIL) | 자동 |
| **Error Message** | 에러 메시지 | 자동 |
| **Duration (sec)** | 실행 시간(초) | 자동 |
| **Screenshot URL** | 스크린샷 경로 | 자동 |
| **Tester** | 실행자 | 자동 |
| **Environment** | 환경 | 자동 |
| **Comment** | 코멘트 | 수동 |

**결과 값**:
- `PASS` - 성공
- `FAIL` - 실패
- `N/A` - 해당 없음

---

### Sheet 3: TestSummary

**목적**: 대시보드 - 전체 테스트 현황 한눈에 보기

**섹션**:

1. **Overall Summary** - 전체 요약
   - Last Updated
   - Total Tests
   - Pass Count
   - Fail Count
   - Pass Rate

2. **Test Results by Category** - 카테고리별 결과
   - Authentication
   - Product
   - Cart
   - Order

3. **Recent Failures** - 최근 실패 로그 (Last 10)
   - Timestamp
   - TC ID
   - Scenario
   - Error

4. **Daily Trend** - 일별 트렌드
   - Date
   - Total / Pass / Fail
   - Pass Rate

---

### Sheet 4: DailyTrend

**목적**: 일별 테스트 결과 트렌드 분석

**컬럼**:
- Date
- Total
- Pass
- Fail
- Pass Rate

**용도**: Looker Studio 차트 데이터 소스

---

## 5. 사용 방법

### 5-1. 테스트 케이스 추가

`TestCase_Template` 시트에 새 행 추가:

```
TC ID: GS_PRODUCT_003
Category: Product
Scenario Name: 상품 필터링
Pre-condition: 1. 로그인 완료
               2. 상품 목록 페이지 접속
Test Steps: 1. 카테고리 필터 선택
            2. 가격 범위 설정
            3. 검색 버튼 클릭
            4. 필터링된 결과 확인
Locators: class: category-filter
          id: price-range
          id: search-btn
Expected Result: 조건에 맞는 상품만 표시
Priority: Medium
Automation Status: Pending
```

### 5-2. 테스트 실행 및 자동 기록

```powershell
# 테스트 실행 (자동으로 Google Sheets에 기록)
pytest tests/test_example.py -v
```

실행 후 `TestResults` 시트에 자동으로 결과 추가됨

### 5-3. Summary 업데이트

테스트 실행이 끝나면 자동으로 업데이트되지만, 수동으로도 가능:

```python
from utils.google_sheets import GoogleSheetsReporter
from utils.config import Config

reporter = GoogleSheetsReporter(Config.GOOGLE_SHEET_URL)
reporter.update_summary()
reporter.add_daily_trend()
```

### 5-4. 데이터 분석

**Looker Studio 연동**:
1. https://lookerstudio.google.com 접속
2. "만들기" → "보고서"
3. 데이터 소스: Google Sheets 선택
4. "Giftishow Test Results" 선택
5. 차트 추가:
   - **성공률 트렌드**: 시계열 (Date, Pass Rate)
   - **카테고리별 분포**: 막대 (Category, Pass/Fail)
   - **최근 실패**: 표 (TestResults 시트)

---

## 6. 트러블슈팅

### 문제 1: 인증 오류

```
gspread.exceptions.APIError: {'code': 403}
```

**해결 방법**:
1. Google Sheets가 서비스 계정과 공유되었는지 확인
2. 편집자 권한이 부여되었는지 확인
3. `credentials.json` 파일이 올바른 위치에 있는지 확인

### 문제 2: Sheet not found

```
gspread.exceptions.WorksheetNotFound
```

**해결 방법**:
```powershell
# 템플릿 다시 생성
python utils\create_sheets_template.py
```

### 문제 3: credentials.json 없음

```
FileNotFoundError: credentials.json
```

**해결 방법**:
1. Google Cloud Console에서 JSON 키 다시 다운로드
2. 프로젝트 루트에 `credentials.json`으로 저장
3. 파일 경로 확인:
```powershell
dir credentials.json
# 출력: credentials.json
```

### 문제 4: API 사용 한도 초과

```
APIError: Quota exceeded
```

**해결 방법**:
- Google Sheets API는 무료로 분당 100회 요청 제한
- 대량 업데이트는 `batch_update` 사용
- 재시도 간격 추가

---

## 7. 고급 사용법

### 7-1. 수동 데이터 기록

```python
from utils.google_sheets import GoogleSheetsReporter
from utils.config import Config

reporter = GoogleSheetsReporter(Config.GOOGLE_SHEET_URL)

# 단일 결과 기록
reporter.log_test_result(
    tc_id="GS_LOGIN_001",
    page="Login Page",
    scenario="정상 로그인",
    result="PASS",
    browser="Chrome 120",
    os_name="Windows 11",
    duration=3.24,
    error_msg="",
    screenshot_url="",
    environment="Production"
)

# 여러 결과 한번에 기록
results = [
    {
        'tc_id': 'GS_LOGIN_001',
        'page': 'Login Page',
        'scenario': '정상 로그인',
        'result': 'PASS',
        'duration': 3.5
    },
    {
        'tc_id': 'GS_LOGIN_002',
        'page': 'Login Page',
        'scenario': '실패 로그인',
        'result': 'PASS',
        'duration': 2.8
    }
]
reporter.log_multiple_results(results)
```

### 7-2. 시나리오 가져오기

```python
# 모든 시나리오 가져오기
scenarios = reporter.get_test_scenarios()

# 자동화 완료된 시나리오만
done_scenarios = reporter.get_scenarios_by_status("✅ Done")

# 진행 중인 시나리오
in_progress = reporter.get_scenarios_by_status("In Progress")
```

---

## 체크리스트

- [ ] Google Cloud 프로젝트 생성
- [ ] Google Sheets API 활성화
- [ ] Google Drive API 활성화
- [ ] 서비스 계정 생성
- [ ] credentials.json 다운로드 및 저장
- [ ] Google Sheets 생성
- [ ] 서비스 계정과 공유 (편집자 권한)
- [ ] .env 파일에 GOOGLE_SHEET_URL 설정
- [ ] create_sheets.bat 실행
- [ ] 4개 시트 생성 확인
- [ ] 샘플 데이터 확인
- [ ] pytest 실행으로 자동 기록 테스트

---

**작성일**: 2026-02-03
**버전**: 1.0

# 기프티쇼 자동화 테스트

ython + Selenium WebDriver 기반의 웹 테스트 자동화 프레임워크로, pytest를 테스트 러너로 사용하며 Page Object Model(POM) 패턴을 적용했습니다. 
로그인/로그아웃, 상품 카테고리 조회, 상품 검색 등 핵심 기능에 대한 자동화 테스트를 수행합니다. 
테스트 결과는 Google Sheets에 실시간 기록되며, TestSummary 대시보드를 통해 전체 현황, OS별/TC별 통계, 실패 로그를 확인할 수 있습니다. HTML 리포트 자동 생성, 실패 시 스크린샷 저장, macOS/Windows 크로스 플랫폼 지원 기능을 제공합니다.


> Selenium + POM 패턴 + Google Sheets 연동 자동화 테스트 프레임워크

## 📋 프로젝트 개요

기프티쇼 비즈 웹사이트(https://biz.giftishow.com)의 자동화 테스트 프로젝트입니다.

**주요 기능**:
- POM (Page Object Model) 패턴 적용
- Google Sheets를 통한 실시간 테스트 결과 수집
- Looker Studio 연동 대시보드
- pytest 기반 테스트 프레임워크
- 자동 스크린샷 캡처 (실패 시)

## 🏗️ 프로젝트 구조

```
giftishow_test/
├── pages/                    # Page Object Models
│   ├── __init__.py
│   ├── base_page.py         # 기본 페이지 클래스
│   └── ...                  # 각 페이지별 POM 클래스
├── tests/                    # 테스트 케이스
│   ├── __init__.py
│   ├── conftest.py          # pytest 설정 및 fixtures
│   └── test_*.py            # 테스트 시나리오
├── utils/                    # 유틸리티
│   ├── __init__.py
│   ├── config.py            # 설정 관리
│   ├── logger.py            # 로깅
│   └── google_sheets.py     # Google Sheets 연동
├── data/                     # 테스트 데이터
│   └── test_data.json
├── reports/                  # 테스트 리포트
│   ├── screenshots/         # 스크린샷
│   └── logs/                # 로그 파일
├── requirements.txt          # Python 의존성
├── pytest.ini               # pytest 설정
├── .env.example             # 환경 변수 템플릿
└── README.md
```

## 🚀 시작하기

### 1. 사전 요구사항

- Python 3.9 이상
- Chrome 또는 Edge 브라우저
- Google 계정 (Google Sheets 연동용)

### 2. 설치

```bash
# 저장소 클론
git clone <repository-url>
cd giftishow_test

# 가상환경 생성 (권장)
python -m venv venv

# 가상환경 활성화
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

### 3. 환경 설정

```bash
# .env 파일 생성
cp .env.example .env
```

`.env` 파일 편집:

```env
# Google Sheets
GOOGLE_SHEET_URL=https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit
GOOGLE_CREDENTIALS_PATH=credentials.json

# Test Environment
BASE_URL=https://biz.giftishow.com
HEADLESS=false
BROWSER=chrome

# Test Data
TEST_USERNAME=your_test_username
TEST_PASSWORD=your_test_password
```

### 4. Google Sheets API 설정

1. [Google Cloud Console](https://console.cloud.google.com) 접속
2. 새 프로젝트 생성
3. "Google Sheets API" 및 "Google Drive API" 활성화
4. 서비스 계정 생성 및 JSON 키 다운로드
5. `credentials.json` 파일을 프로젝트 루트에 저장
6. Google Sheets를 서비스 계정 이메일과 공유 (편집자 권한)

상세한 설정 방법은 [기프티쇼_자동화_테스트_프로젝트.md](기프티쇼_자동화_테스트_프로젝트.md) 참고

## 📊 Google Sheets 구조

테스트 결과를 기록할 Google Sheets에 다음 4개 시트를 생성하세요:

1. **TestCase_Scenarios** - 테스트 시나리오 정의
2. **TestResults** - 실행 결과 상세
3. **TestSummary** - 전체 요약
4. **DailyTrend** - 일별 트렌드

시트 자동 생성:

```python
from utils.google_sheets import GoogleSheetsReporter

reporter = GoogleSheetsReporter(sheet_url="YOUR_SHEET_URL")
reporter.create_default_sheets()
```

## 🧪 테스트 실행

### 기본 실행

```bash
# 모든 테스트 실행
pytest

# 상세 출력
pytest -v

# 특정 테스트 파일 실행
pytest tests/test_login.py

# 특정 테스트 함수 실행
pytest tests/test_login.py::TestLogin::test_successful_login
```

### 마커 사용

```bash
# smoke 테스트만 실행
pytest -m smoke

# regression 테스트 실행
pytest -m regression

# 특정 페이지 테스트
pytest -m login
pytest -m product
```

### 커스텀 옵션

```bash
# 브라우저 선택
pytest --browser=chrome
pytest --browser=edge

# Headless 모드
pytest --headless

# 환경 선택
pytest --env=production
pytest --env=staging

# 병렬 실행 (4개 프로세스)
pytest -n 4

# 실패 시 재시도
pytest --reruns 2
```

### HTML 리포트 생성

```bash
pytest --html=reports/report.html --self-contained-html
```

## 📝 테스트 작성 예시

### 1. Page Object 생성

```python
# pages/login_page.py
from selenium.webdriver.common.by import By
from pages.base_page import BasePage

class LoginPage(BasePage):
    # Locators
    USERNAME_INPUT = (By.ID, "username")
    PASSWORD_INPUT = (By.ID, "password")
    LOGIN_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")

    def __init__(self, driver):
        super().__init__(driver)
        self.url = f"{self.driver.current_url}/login"

    def navigate(self):
        self.navigate_to(self.url)

    def login(self, username, password):
        self.input_text(self.USERNAME_INPUT, username)
        self.input_text(self.PASSWORD_INPUT, password)
        self.click(self.LOGIN_BUTTON)

    def is_login_successful(self):
        return "main" in self.get_current_url()
```

### 2. 테스트 케이스 작성

```python
# tests/test_login.py
import pytest
from pages.login_page import LoginPage

@pytest.mark.login
@pytest.mark.smoke
class TestLogin:

    @pytest.mark.tc_id("GS_LOGIN_001")
    @pytest.mark.page("Login Page")
    @pytest.mark.scenario("정상 로그인")
    def test_successful_login(self, driver, test_data):
        """정상 로그인 테스트"""
        login_page = LoginPage(driver)
        login_page.navigate()

        login_page.login(
            test_data['valid_user']['username'],
            test_data['valid_user']['password']
        )

        assert login_page.is_login_successful(), "로그인 실패"
```

## 🔍 주요 기능

### BasePage 클래스

모든 페이지 객체의 기본 클래스로 다음 기능 제공:

- `find_element(locator)` - 요소 찾기
- `click(locator)` - 클릭
- `input_text(locator, text)` - 텍스트 입력
- `get_text(locator)` - 텍스트 가져오기
- `is_element_visible(locator)` - 요소 표시 여부 확인
- `scroll_to_element(locator)` - 요소까지 스크롤
- `take_screenshot(name)` - 스크린샷 저장
- `wait_for_page_load()` - 페이지 로드 대기

### Google Sheets 연동

```python
from utils.google_sheets import GoogleSheetsReporter

# 리포터 초기화
reporter = GoogleSheetsReporter(sheet_url="YOUR_SHEET_URL")

# 테스트 결과 기록
reporter.log_test_result(
    tc_id="GS_001",
    page="Login Page",
    scenario="정상 로그인",
    result="PASS",
    duration=3.5
)

# Summary 업데이트
reporter.update_summary()

# Daily Trend 추가
reporter.add_daily_trend()
```

### 설정 관리

```python
from utils.config import Config

# 설정 값 사용
print(Config.BASE_URL)
print(Config.BROWSER)
print(Config.HEADLESS)

# 현재 설정 출력
Config.print_config()
```

### 로깅

```python
from utils.logger import get_test_logger

logger = get_test_logger("MyTest")
logger.info("테스트 시작")
logger.debug("디버그 메시지")
logger.error("에러 발생")
```

## 🎯 pytest 마커

- `@pytest.mark.smoke` - 스모크 테스트
- `@pytest.mark.regression` - 리그레션 테스트
- `@pytest.mark.login` - 로그인 관련
- `@pytest.mark.product` - 상품 관련
- `@pytest.mark.order` - 주문 관련
- `@pytest.mark.e2e` - End-to-End 시나리오

커스텀 마커:
- `@pytest.mark.tc_id("GS_001")` - 테스트 케이스 ID
- `@pytest.mark.page("Login Page")` - 페이지명
- `@pytest.mark.scenario("정상 로그인")` - 시나리오명

## 📈 Looker Studio 연동

1. [Looker Studio](https://lookerstudio.google.com) 접속
2. 새 보고서 생성
3. 데이터 소스로 Google Sheets 선택
4. TestResults, TestSummary, DailyTrend 시트 연결
5. 차트 추가:
   - 성공률 트렌드 (시계열)
   - 페이지별 Pass/Fail 분포 (막대)
   - 최근 실패 케이스 (표)
   - 전체 요약 (스코어카드)

## 🛠️ 트러블슈팅

### ChromeDriver 오류

```bash
# webdriver-manager 캐시 삭제
rm -rf ~/.wdm
```

### Google Sheets 권한 오류

- `credentials.json`의 `client_email`을 Google Sheets에 공유했는지 확인
- 편집자 권한이 부여되었는지 확인

### 요소를 찾을 수 없는 오류

- `Config.EXPLICIT_WAIT` 값 증가
- 동적 로딩이 있는 경우 `wait_for_page_load()` 사용
- Locator 전략 변경 (CSS → XPath 등)

## 📚 참고 자료

- [Selenium Python Docs](https://selenium-python.readthedocs.io/)
- [Pytest Documentation](https://docs.pytest.org/)
- [gspread Documentation](https://docs.gspread.org/)
- [POM Pattern Guide](https://martinfowler.com/bliki/PageObject.html)

## 📄 라이선스

MIT License

## 👥 기여

Pull Request는 언제나 환영합니다!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📧 문의

프로젝트 관련 문의사항이 있으시면 이슈를 등록해주세요.

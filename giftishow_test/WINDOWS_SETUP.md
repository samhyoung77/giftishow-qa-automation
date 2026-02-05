# Windows 환경 설정 가이드

## 📋 목차
1. [Python 가상환경 설정](#1-python-가상환경-설정)
2. [환경 변수 설정](#2-환경-변수-설정)
3. [Google Sheets 설정](#3-google-sheets-설정)
4. [테스트 실행](#4-테스트-실행)

---

## 1. Python 가상환경 설정

### 1-1. 가상환경 생성

```powershell
# PowerShell 또는 CMD에서 실행
cd E:\claude_code\giftishow_test

# 가상환경 생성
python -m venv venv
```

### 1-2. 가상환경 활성화

#### PowerShell 사용 시

```powershell
# 실행 정책 확인 (최초 1회)
Get-ExecutionPolicy

# 실행 정책이 Restricted라면 변경 필요 (관리자 권한)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 가상환경 활성화
.\venv\Scripts\Activate.ps1

# 활성화 확인 (프롬프트 앞에 (venv) 표시)
# (venv) PS E:\claude_code\giftishow_test>
```

#### CMD 사용 시

```cmd
# 가상환경 활성화
venv\Scripts\activate.bat

# 활성화 확인
# (venv) E:\claude_code\giftishow_test>
```

#### Git Bash 사용 시

```bash
# 가상환경 활성화
source venv/Scripts/activate

# 활성화 확인
# (venv) user@computer MINGW64 /e/claude_code/giftishow_test
```

### 1-3. 의존성 설치

```powershell
# 가상환경 활성화 후
pip install -r requirements.txt

# 설치 확인
pip list
```

---

## 2. 환경 변수 설정

### 방법 1: .env 파일 사용 (권장)

#### 2-1-1. .env 파일 생성

```powershell
# .env.example 파일을 .env로 복사
copy .env.example .env

# 또는 새로 생성
notepad .env
```

#### 2-1-2. .env 파일 편집

메모장 또는 VS Code로 `.env` 파일을 열어 다음과 같이 편집:

```env
# Google Sheets Configuration
GOOGLE_SHEET_URL=https://docs.google.com/spreadsheets/d/1M4512WY_ZctjJo200OdwCty6k-ObDxvxRQTHp2hdWkA/edit
GOOGLE_CREDENTIALS_PATH=credentials.json

# Test Environment
BASE_URL=https://biz.giftishow.com
HEADLESS=false
BROWSER=chrome
IMPLICIT_WAIT=10
EXPLICIT_WAIT=20

# Test Data
TEST_USERNAME=your_test_username
TEST_PASSWORD=your_test_password

# Reporting
ENABLE_SCREENSHOTS=true
SCREENSHOT_PATH=reports/screenshots
LOG_LEVEL=INFO

# Optional: CI/CD
RUN_ENVIRONMENT=local
```

**주의사항**:
- `=` 앞뒤에 공백 없이 작성
- 문자열에 따옴표 불필요
- 실제 값으로 변경 필요:
  - `GOOGLE_SHEET_URL`: 실제 Google Sheets URL
  - `TEST_USERNAME`: 테스트 계정 ID
  - `TEST_PASSWORD`: 테스트 계정 비밀번호

#### 2-1-3. .env 파일 로드 확인

```powershell
# Python으로 환경 변수 확인
python -c "from utils.config import Config; Config.print_config()"
```

---

### 방법 2: Windows 시스템 환경 변수 설정

#### 2-2-1. GUI로 설정

1. **시스템 환경 변수 창 열기**
   ```
   Win + R → sysdm.cpl → Enter
   → "고급" 탭 → "환경 변수" 버튼 클릭
   ```

2. **사용자 변수 추가** (현재 사용자만 적용)
   - "사용자 변수" 섹션에서 "새로 만들기" 클릭
   - 변수 이름과 값 입력:

   | 변수 이름 | 변수 값 |
   |---------|---------|
   | `GIFTISHOW_BASE_URL` | `https://biz.giftishow.com` |
   | `GIFTISHOW_TEST_USER` | `your_username` |
   | `GIFTISHOW_TEST_PASS` | `your_password` |
   | `GIFTISHOW_BROWSER` | `chrome` |

3. **확인 및 적용**
   - "확인" 버튼으로 모든 창 닫기
   - PowerShell/CMD 재시작 필요

#### 2-2-2. PowerShell로 설정 (현재 세션만)

```powershell
# 현재 세션에서만 유효
$env:BASE_URL = "https://biz.giftishow.com"
$env:TEST_USERNAME = "your_username"
$env:TEST_PASSWORD = "your_password"
$env:BROWSER = "chrome"
$env:HEADLESS = "false"

# 확인
echo $env:BASE_URL
```

#### 2-2-3. PowerShell로 영구 설정 (사용자 환경 변수)

```powershell
# 사용자 환경 변수로 영구 저장
[System.Environment]::SetEnvironmentVariable('BASE_URL', 'https://biz.giftishow.com', 'User')
[System.Environment]::SetEnvironmentVariable('TEST_USERNAME', 'your_username', 'User')
[System.Environment]::SetEnvironmentVariable('TEST_PASSWORD', 'your_password', 'User')
[System.Environment]::SetEnvironmentVariable('BROWSER', 'chrome', 'User')

# 확인 (PowerShell 재시작 후)
[System.Environment]::GetEnvironmentVariable('BASE_URL', 'User')
```

#### 2-2-4. CMD로 설정 (현재 세션만)

```cmd
REM 현재 세션에서만 유효
set BASE_URL=https://biz.giftishow.com
set TEST_USERNAME=your_username
set TEST_PASSWORD=your_password

REM 확인
echo %BASE_URL%
```

#### 2-2-5. setx로 영구 설정 (CMD)

```cmd
REM 사용자 환경 변수로 영구 저장 (CMD 재시작 필요)
setx BASE_URL "https://biz.giftishow.com"
setx TEST_USERNAME "your_username"
setx TEST_PASSWORD "your_password"
setx BROWSER "chrome"

REM 확인 (CMD 재시작 후)
echo %BASE_URL%
```

**주의**: `setx`는 현재 세션에 적용되지 않으므로 CMD/PowerShell을 재시작해야 합니다.

---

### 방법 3: 프로필 스크립트에 추가 (PowerShell)

#### 2-3-1. PowerShell 프로필 파일 생성/편집

```powershell
# 프로필 파일 위치 확인
$PROFILE

# 프로필 파일이 없으면 생성
if (!(Test-Path -Path $PROFILE)) {
    New-Item -ItemType File -Path $PROFILE -Force
}

# 프로필 파일 열기
notepad $PROFILE
```

#### 2-3-2. 환경 변수 추가

프로필 파일에 다음 내용 추가:

```powershell
# Giftishow Test Environment Variables
$env:BASE_URL = "https://biz.giftishow.com"
$env:TEST_USERNAME = "your_username"
$env:TEST_PASSWORD = "your_password"
$env:BROWSER = "chrome"
$env:HEADLESS = "false"
$env:GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit"
```

#### 2-3-3. 프로필 적용

```powershell
# 프로필 다시 로드
. $PROFILE

# 또는 PowerShell 재시작
```

---

## 3. Google Sheets 설정

### 3-1. Google Cloud Console 설정

1. **Google Cloud Console 접속**
   - https://console.cloud.google.com

2. **프로젝트 생성**
   - 프로젝트 이름: `Giftishow-Test`

3. **API 활성화**
   - "API 및 서비스" → "라이브러리"
   - "Google Sheets API" 검색 → 사용 설정
   - "Google Drive API" 검색 → 사용 설정

4. **서비스 계정 생성**
   - "API 및 서비스" → "사용자 인증 정보"
   - "사용자 인증 정보 만들기" → "서비스 계정"
   - 서비스 계정 이름: `giftishow-test-automation`
   - 역할: "편집자"

5. **JSON 키 다운로드**
   - 생성된 서비스 계정 클릭
   - "키" 탭 → "키 추가" → "새 키 만들기"
   - 키 유형: JSON
   - 다운로드된 파일을 `credentials.json`으로 이름 변경
   - 프로젝트 루트(`E:\claude_code\giftishow_test\`)에 저장

### 3-2. credentials.json 저장

```powershell
# 다운로드 폴더에서 프로젝트 폴더로 이동
move "$env:USERPROFILE\Downloads\giftishow-test-*.json" "E:\claude_code\giftishow_test\credentials.json"

# 파일 확인
dir credentials.json
```

### 3-3. Google Sheets 생성 및 공유

1. **새 Google Sheets 생성**
   - https://sheets.google.com
   - 새 스프레드시트 만들기
   - 이름: "Giftishow Test Results"

2. **서비스 계정과 공유**
   - "공유" 버튼 클릭
   - `credentials.json` 파일 열어서 `client_email` 값 복사
     ```json
     "client_email": "giftishow-test-automation@PROJECT_ID.iam.gserviceaccount.com"
     ```
   - 복사한 이메일 주소를 공유에 추가
   - 권한: "편집자"

3. **Sheet URL 복사**
   - 브라우저 주소창의 URL 복사
   - `.env` 파일의 `GOOGLE_SHEET_URL`에 설정

### 3-4. 기본 시트 구조 생성

```powershell
# Python으로 기본 시트 생성
python -c "from utils.google_sheets import GoogleSheetsReporter; from utils.config import Config; reporter = GoogleSheetsReporter(Config.GOOGLE_SHEET_URL); reporter.create_default_sheets()"
```

---

## 4. 테스트 실행

### 4-1. 환경 확인

```powershell
# 가상환경 활성화 확인
# 프롬프트 앞에 (venv) 표시 확인

# Python 버전 확인
python --version
# Python 3.9 이상

# pip 버전 확인
pip --version

# 설정 출력
python -c "from utils.config import Config; Config.print_config()"
```

### 4-2. 예제 테스트 실행

```powershell
# 모든 테스트 실행
pytest tests/test_example.py -v

# 스모크 테스트만 실행
pytest tests/test_example.py -m smoke -v

# 특정 테스트만 실행
pytest tests/test_example.py::TestExample::test_open_main_page -v

# HTML 리포트 생성
pytest tests/test_example.py --html=reports/report.html --self-contained-html

# 병렬 실행
pytest tests/test_example.py -n 2 -v
```

### 4-3. 브라우저 옵션으로 실행

```powershell
# Chrome으로 실행 (기본값)
pytest --browser=chrome -v

# Edge로 실행
pytest --browser=edge -v

# Headless 모드
pytest --headless -v

# 환경 지정
pytest --env=staging -v
```

### 4-4. 리포트 확인

```powershell
# HTML 리포트 열기
start reports/report.html

# 스크린샷 폴더 열기
start reports/screenshots

# 로그 파일 보기
type reports/logs/pytest.log

# 또는 메모장으로 열기
notepad reports/logs/pytest.log
```

---

## 5. 트러블슈팅

### 5-1. PowerShell 실행 정책 오류

```
오류: 이 시스템에서 스크립트를 실행할 수 없으므로...
```

**해결 방법**:
```powershell
# 관리자 권한으로 PowerShell 실행
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 또는 현재 프로세스만
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
```

### 5-2. pip 설치 오류

```
ERROR: Could not install packages due to an OSError: [WinError 5]
```

**해결 방법**:
```powershell
# 관리자 권한 없이 설치
pip install -r requirements.txt --user

# 또는 캐시 삭제 후 재시도
pip cache purge
pip install -r requirements.txt
```

### 5-3. Chrome Driver 오류

```
selenium.common.exceptions.WebDriverException
```

**해결 방법**:
```powershell
# Chrome 브라우저 업데이트
# webdriver-manager가 자동으로 처리하지만, 수동 삭제 후 재시도

# 캐시 삭제 (PowerShell)
Remove-Item -Recurse -Force "$env:USERPROFILE\.wdm"

# 테스트 재실행
pytest tests/test_example.py -v
```

### 5-4. 한글 인코딩 오류

```powershell
# PowerShell에서 UTF-8 설정
$OutputEncoding = [Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# 또는 환경 변수로 설정
$env:PYTHONIOENCODING = "utf-8"
```

### 5-5. Google Sheets 인증 오류

```
gspread.exceptions.APIError: {'code': 403, 'message': 'Forbidden'}
```

**확인 사항**:
1. `credentials.json` 파일이 프로젝트 루트에 있는지 확인
2. Google Sheets가 서비스 계정 이메일과 공유되었는지 확인
3. 편집자 권한이 부여되었는지 확인

---

## 6. 배치 파일로 자동화

### 6-1. 테스트 실행 배치 파일 생성

`run_tests.bat` 파일 생성:

```batch
@echo off
echo ========================================
echo Giftishow Test Automation
echo ========================================

REM 가상환경 활성화
call venv\Scripts\activate.bat

REM 설정 출력
echo.
echo Current Configuration:
python -c "from utils.config import Config; Config.print_config()"

REM 테스트 실행
echo.
echo Running Tests...
pytest tests/ -v --html=reports/report.html --self-contained-html

REM 리포트 열기
echo.
echo Opening Report...
start reports/report.html

echo.
echo Test Completed!
pause
```

### 6-2. 실행

```powershell
# 배치 파일 실행
.\run_tests.bat
```

---

## 7. VS Code 설정 (선택사항)

### 7-1. settings.json 추가

`.vscode/settings.json` 파일:

```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/venv/Scripts/python.exe",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": [
        "tests",
        "-v"
    ],
    "python.envFile": "${workspaceFolder}/.env",
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true
    }
}
```

### 7-2. VS Code에서 테스트 실행

1. 테스트 탭(플라스크 아이콘) 클릭
2. "Configure Python Tests" → "pytest"
3. 테스트 디렉토리: `tests`
4. 테스트 실행 버튼 클릭

---

## 체크리스트

- [ ] Python 3.9+ 설치 확인
- [ ] 가상환경 생성 및 활성화
- [ ] requirements.txt 패키지 설치
- [ ] .env 파일 생성 및 편집
- [ ] Google Cloud 서비스 계정 생성
- [ ] credentials.json 다운로드 및 저장
- [ ] Google Sheets 생성 및 공유
- [ ] 기본 시트 구조 생성
- [ ] 예제 테스트 실행 성공
- [ ] HTML 리포트 확인

---

**작성일**: 2026-02-03
**버전**: 1.0

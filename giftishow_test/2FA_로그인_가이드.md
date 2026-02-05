# 2FA 로그인 테스트 가이드

작성일: 2026-02-04
상태: ✅ Akamai + 2FA 우회 솔루션 완료

---

## 🔐 문제 상황

기프티쇼 로그인에 **두 가지 장애물**이 있습니다:

1. **Akamai Bot Manager** - 자동화 도구(Selenium) 감지 및 차단
2. **2FA (2단계 인증)** - 카카오톡으로 인증번호 전송

**결과**: 일반 Selenium 테스트로는 자동 로그인 불가능

---

## ✅ 해결 방법: 수동 로그인 + 쿠키 저장

한 번만 수동으로 로그인하고, 세션 쿠키를 저장해서 재사용합니다.

### 작동 원리

```
[첫 번째 실행]
1. manual_login.py 실행
2. 브라우저 열림 (undetected-chromedriver 사용)
3. 사람이 직접 로그인
   - ID/PW 입력
   - 카카오톡 인증번호 확인
   - 인증 완료
4. 세션 쿠키 저장 (data/session_cookies.pkl)

[이후 모든 테스트]
1. 저장된 쿠키 자동 로드
2. 로그인 없이 바로 접속
3. 2FA 우회!
```

---

## 🚀 사용 방법

### STEP 1: 수동 로그인 (최초 1회만)

```bash
python manual_login.py
```

**진행 과정**:

1. Chrome 브라우저가 자동으로 열립니다
2. 로그인 페이지로 이동됩니다
3. **브라우저에서 직접 로그인하세요**:
   - 아이디/이메일 입력
   - 비밀번호 입력
   - 로그인 버튼 클릭
   - 📱 카카오톡에서 인증번호 확인
   - 인증번호 입력
   - 로그인 완료!
4. 로그인 완료 후 터미널로 돌아와서 **Enter 키 입력**
5. ✅ 쿠키 자동 저장됨!

**출력 예시**:
```
================================================================================
기프티쇼 수동 로그인 - 쿠키 저장
================================================================================

[1/5] Chrome 브라우저 실행 중...
✓ 브라우저 실행 완료

[2/5] 로그인 페이지 접속 중...
✓ 로그인 페이지 열림: https://biz.giftishow.com/login

================================================================================
✋ 중요: 브라우저 창에서 직접 로그인하세요!
================================================================================

로그인 완료 후 Enter 키를 누르세요...
```

### STEP 2: 테스트 실행

이제 저장된 쿠키로 자동 로그인됩니다:

```bash
# 로그인 테스트 실행
pytest tests/test_login.py -v

# 특정 테스트만
pytest tests/test_login.py::TestLogin::test_successful_login -v

# 상세 출력
pytest tests/test_login.py -v -s
```

**테스트 실행 과정**:

```
[로그인 방법 1] 저장된 쿠키 확인 중...
✓ 저장된 쿠키 발견! 쿠키로 자동 로그인 시도...
✓ 쿠키 로그인 성공!
```

✅ **2FA 없이 바로 로그인!**

---

## 📁 저장된 파일

### `data/session_cookies.pkl`

- 로그인 세션 쿠키 저장 파일
- manual_login.py 실행 시 자동 생성
- 테스트 실행 시 자동 로드
- ⚠️ **보안 주의**: .gitignore에 포함됨 (Git에 커밋 안 됨)

### 쿠키 정보 확인

```python
from utils.cookie_manager import CookieManager

cookie_manager = CookieManager()
cookie_manager.print_cookie_info()
```

**출력 예시**:
```
================================================================================
저장된 쿠키 정보
================================================================================
URL: https://biz.giftishow.com/main
쿠키 개수: 12

쿠키 목록:
  [1] SESSION
      domain: .giftishow.com
      expiry: 2026-02-05 12:30:15
  [2] JSESSIONID
      domain: biz.giftishow.com
      expiry: 2026-02-05 12:30:15
  ...
```

---

## 🔄 쿠키 갱신

쿠키가 만료되면 (보통 24시간 후):

```
⚠ 쿠키 로그인 실패. 쿠키가 만료되었을 수 있습니다.
```

**해결**: `manual_login.py` 다시 실행

```bash
python manual_login.py
```

---

## 🧪 테스트 시나리오별 동작

### GS_AUTH_001: 정상 로그인

```python
def test_successful_login(self, driver, test_data):
    # 1. 쿠키 있음? → 쿠키 로그인 (성공!)
    # 2. 쿠키 없음? → 일반 로그인 시도 (2FA 때문에 실패)
```

**권장**: manual_login.py 실행 후 테스트

### GS_AUTH_002: 잘못된 비밀번호

```python
def test_login_with_wrong_password(self, driver, test_data):
    # 쿠키 사용 안 함
    # 일반 로그인 시도 → 로그인 페이지 유지 확인
```

✅ 이 테스트는 쿠키 없이도 동작 (2FA 전 단계)

---

## ⚙️ 고급 사용법

### 쿠키 삭제

```python
from utils.cookie_manager import CookieManager

cookie_manager = CookieManager()
cookie_manager.delete_cookies()
```

또는:

```bash
# Windows
del data\session_cookies.pkl

# Linux/Mac
rm data/session_cookies.pkl
```

### 프로그래밍 방식으로 쿠키 저장

테스트 중에 현재 세션 저장:

```python
def test_example(self):
    # 로그인 후...
    self.login_page.save_current_session()
```

---

## 🔧 기술 구성

### 사용된 라이브러리

1. **undetected-chromedriver**
   - Selenium 감지 우회
   - Akamai Bot Manager 우회
   - 일반 사용자처럼 보이게 함

2. **CookieManager** (utils/cookie_manager.py)
   - 쿠키 저장/로드 관리
   - pickle 형식으로 저장
   - 도메인 및 만료시간 관리

### conftest.py 변경사항

```python
import undetected_chromedriver as uc

# Chrome Driver 초기화 시
driver = uc.Chrome(options=options, use_subprocess=True)
```

### LoginPage 추가 메서드

```python
# 쿠키로 로그인
login_page.login_with_saved_cookies()

# 현재 세션 저장
login_page.save_current_session()

# 쿠키 존재 여부 확인
login_page.cookie_manager.cookies_exist()
```

---

## 🐛 문제 해결

### 1. "쿠키 파일이 없습니다"

```
WARNING  LoginPage:login_page.py:xxx 저장된 쿠키가 없습니다. manual_login.py를 먼저 실행하세요.
```

**해결**:
```bash
python manual_login.py
```

### 2. "쿠키 로그인 실패"

```
⚠ 쿠키 로그인 실패. 쿠키가 만료되었을 수 있습니다.
```

**원인**: 세션 만료 (보통 24시간 후)

**해결**:
```bash
python manual_login.py  # 쿠키 재생성
```

### 3. Akamai Bot Manager 여전히 나타남

`manual_login.py` 실행 시에도 Akamai가 나타나면:

1. 잠시 기다리기 (5-10초)
2. Akamai가 자동으로 새로고침할 때까지 대기
3. 수동으로 새로고침 (F5)
4. 로그인 시도

**undetected-chromedriver**가 대부분 우회하지만, 100% 보장은 안 됩니다.

### 4. 2FA 인증번호가 안 옴

- 카카오톡 알림 확인
- 카카오톡 앱 열어서 확인
- 인증번호 유효시간 확인 (보통 3-5분)

---

## 📊 테스트 실행 흐름도

```
┌─────────────────────────────────┐
│ pytest tests/test_login.py      │
└────────────┬────────────────────┘
             │
             ▼
    ┌────────────────────┐
    │ 쿠키 파일 있음?    │
    └────────┬───────────┘
             │
      YES ◀──┴──▶ NO
       │           │
       │           ▼
       │    ┌──────────────────┐
       │    │ 일반 로그인 시도 │
       │    │ (2FA 필요)       │
       │    └────────┬─────────┘
       │             │
       │             ▼
       │       ❌ 실패
       │       "manual_login.py
       │        실행하세요"
       │
       ▼
 ┌──────────────────┐
 │ 쿠키 로드 및     │
 │ 자동 로그인      │
 └────────┬─────────┘
          │
          ▼
     ✅ 성공!
```

---

## 💡 팁

### 1. CI/CD 환경에서 사용

GitHub Actions 등에서:

1. Secret에 쿠키 파일 저장
2. 테스트 실행 전에 쿠키 파일 복원
3. 테스트 실행

```yaml
# .github/workflows/test.yml
- name: Restore cookies
  run: |
    echo "${{ secrets.SESSION_COOKIES }}" | base64 -d > data/session_cookies.pkl

- name: Run tests
  run: pytest tests/test_login.py -v
```

### 2. 여러 계정 관리

```python
# 계정별 쿠키 파일
cookie_manager_user1 = CookieManager("data/cookies_user1.pkl")
cookie_manager_user2 = CookieManager("data/cookies_user2.pkl")
```

### 3. 쿠키 유효성 확인

```python
# 쿠키 로드 후 바로 확인
if login_page.login_with_saved_cookies():
    if not login_page.is_logged_in():
        # 쿠키 만료 → 재로그인 필요
        cookie_manager.delete_cookies()
```

---

## 📚 관련 파일

| 파일 | 설명 |
|------|------|
| `manual_login.py` | 수동 로그인 + 쿠키 저장 스크립트 |
| `utils/cookie_manager.py` | 쿠키 관리 클래스 |
| `pages/login_page.py` | LoginPage + 쿠키 로그인 메서드 |
| `tests/test_login.py` | 로그인 테스트 (쿠키 우선 사용) |
| `data/session_cookies.pkl` | 저장된 쿠키 파일 (생성됨) |

---

## ✅ 체크리스트

로그인 테스트 실행 전:

- [ ] Python 환경 활성화
- [ ] undetected-chromedriver 설치 확인
- [ ] `python manual_login.py` 실행
- [ ] 브라우저에서 직접 로그인
- [ ] 카카오톡 인증 완료
- [ ] Enter 키 입력
- [ ] 쿠키 저장 확인
- [ ] `pytest tests/test_login.py -v` 실행
- [ ] 쿠키 로그인 성공 확인

---

## 🎯 요약

**문제**: Akamai + 2FA 때문에 자동 로그인 불가

**해결**: 수동 로그인 1회 + 쿠키 재사용

**방법**:
1. `python manual_login.py` (최초 1회)
2. 브라우저에서 직접 로그인 (2FA 포함)
3. 쿠키 자동 저장
4. `pytest tests/test_login.py` (이후 모든 테스트)
5. 쿠키로 자동 로그인!

**결과**: ✅ 2FA 우회, ✅ Akamai 우회, ✅ 자동화 테스트 가능!

---

**작성자**: Claude Code
**최종 수정**: 2026-02-04
**버전**: 1.0
**상태**: ✅ 완료

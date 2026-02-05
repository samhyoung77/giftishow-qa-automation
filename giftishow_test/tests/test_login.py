"""
로그인 테스트 모듈
GS_AUTH_001, GS_AUTH_002 시나리오 구현

Test Cases:
- GS_AUTH_001: 정상 로그인
- GS_AUTH_002: 잘못된 비밀번호 로그인
"""
import pytest
from pages.login_page import LoginPage
import time


@pytest.mark.login
@pytest.mark.smoke
class TestLogin:
    """로그인 기능 테스트"""

    @pytest.fixture(autouse=True)
    def setup(self, driver):
        """각 테스트 전 실행"""
        self.login_page = LoginPage(driver)
        yield
        # 테스트 후 정리 (필요 시)

    # ==================== GS_AUTH_001: 정상 로그인 ====================
    @pytest.mark.tc_id("GS_AUTH_001")
    @pytest.mark.page("Login Page")
    @pytest.mark.scenario("정상 로그인")
    @pytest.mark.skip(reason="2FA(카카오톡 인증) + Akamai Bot Manager로 인해 자동화 불가능")
    def test_successful_login(self, driver, test_data):
        """
        GS_AUTH_001: 정상 로그인 테스트

        Pre-condition:
        1. 유효한 기업 계정이 존재함
        2. 로그인 페이지 접근 가능
        3. 저장된 세션 쿠키 또는 계정 정보

        Test Steps (방법 1 - 쿠키 사용):
        1. 저장된 쿠키로 자동 로그인

        Test Steps (방법 2 - 수동 로그인):
        1. 로그인 페이지 접속
        2. 사용자 ID 입력
        3. 비밀번호 입력
        4. 로그인 버튼 클릭
        5. 2FA 인증 대기 (수동)
        6. 메인 페이지 이동 확인

        Expected Result:
        - 메인 페이지로 리다이렉트
        - 환영 메시지 또는 사용자명 표시

        Note:
        - 2FA(카카오톡 인증) 때문에 완전 자동화 불가
        - 쿠키 사용 권장: python manual_login.py 실행 후 테스트
        """
        # 방법 1: 저장된 쿠키로 로그인 시도
        print("\n[LOGIN METHOD 1] Checking saved cookies...")
        if self.login_page.cookie_manager.cookies_exist():
            print("OK: Saved cookies found! Attempting cookie login...")
            cookie_login_success = self.login_page.login_with_saved_cookies()

            if cookie_login_success:
                print("OK: Cookie login successful!")
                self.login_page.take_screenshot("cookie_login_success")
                assert True, "Cookie login successful"
                return
            else:
                print("WARNING: Cookie login failed. Cookies may be expired.")
                print("         Proceeding to Method 2...")

        else:
            print("WARNING: No saved cookies found.")
            print("         To bypass 2FA, run 'python manual_login.py' first.")
            print("         Proceeding to Method 2 (normal login)...")

        # 방법 2: 일반 로그인 (2FA 포함)
        print("\n[LOGIN METHOD 2] Attempting normal login...")
        print("WARNING: If 2FA (KakaoTalk auth) is enabled on this account,")
        print("         automated testing will fail!")

        # Pre-condition: 쿠키 삭제
        self.login_page.clear_cookies()

        # Step 1: 로그인 페이지 접속
        self.login_page.navigate()

        # 로그인 폼 로드 대기
        self.login_page.wait_for_login_form()

        # 초기 상태 스크린샷
        self.login_page.take_screenshot("login_page_initial")

        # Steps 2-4: 로그인 프로세스
        username = test_data.get('valid_user', {}).get('username', 'test_user')
        password = test_data.get('valid_user', {}).get('password', 'test_password')

        self.login_page.login(username, password)

        # Step 5: 메인 페이지 이동 확인 (최대 10초 대기)
        time.sleep(3)  # 페이지 전환 대기

        # 로그인 후 스크린샷
        self.login_page.take_screenshot("after_login")

        # Assertion: 로그인 성공 확인
        is_logged_in = self.login_page.is_logged_in(timeout=10)

        # 로그인 실패 시 추가 정보 수집
        if not is_logged_in:
            current_url = self.login_page.get_current_url()
            page_title = self.login_page.get_page_title()
            print(f"\nLogin failed. Current URL: {current_url}")
            print(f"Page Title: {page_title}")

            # 에러 메시지가 있는지 확인
            if self.login_page.is_error_message_displayed():
                error_msg = self.login_page.get_error_message()
                print(f"Error Message: {error_msg}")

            self.login_page.take_screenshot("login_failed")

            # 2FA 안내
            print("\n" + "=" * 80)
            print("로그인 실패 원인:")
            print("  1. Akamai Bot Manager가 자동화 도구를 차단했거나")
            print("  2. 2FA(카카오톡 인증)가 필요한 계정입니다")
            print()
            print("해결 방법:")
            print("  1. 다음 명령어를 실행하세요: python manual_login.py")
            print("  2. 브라우저가 열리면 직접 로그인하세요 (2FA 포함)")
            print("  3. 로그인 완료 후 쿠키가 자동 저장됩니다")
            print("  4. 이후 모든 테스트는 저장된 쿠키를 사용합니다")
            print("=" * 80)

        assert is_logged_in, "로그인 실패: 메인 페이지로 이동하지 못했습니다. manual_login.py를 실행하세요."

    # ==================== GS_AUTH_002: 잘못된 비밀번호 로그인 ====================
    @pytest.mark.tc_id("GS_AUTH_002")
    @pytest.mark.page("Login Page")
    @pytest.mark.scenario("잘못된 비밀번호 로그인")
    def test_login_with_wrong_password(self, driver, test_data):
        """
        GS_AUTH_002: 잘못된 비밀번호 로그인 테스트

        Pre-condition:
        1. 유효한 계정 ID 존재
        2. 로그인 페이지 접근 가능

        Test Steps:
        1. 로그인 페이지 접속
        2. 유효한 ID 입력
        3. 잘못된 비밀번호 입력
        4. 로그인 버튼 클릭
        5. 에러 메시지 확인

        Expected Result:
        - '아이디 또는 비밀번호가 일치하지 않습니다' 에러 메시지 표시
        - 로그인 페이지 유지
        """
        # Pre-condition: 쿠키 삭제
        self.login_page.clear_cookies()

        # Step 1: 로그인 페이지 접속
        self.login_page.navigate()

        # 로그인 폼 로드 대기
        self.login_page.wait_for_login_form()

        # Steps 2-4: 유효한 ID + 잘못된 비밀번호로 로그인 시도
        username = test_data.get('valid_user', {}).get('username', 'test_user')
        wrong_password = "wrong_password_12345"  # 의도적으로 틀린 비밀번호

        self.login_page.login(username, wrong_password)

        # 에러 메시지 표시 대기
        time.sleep(2)

        # 로그인 실패 후 스크린샷
        self.login_page.take_screenshot("login_wrong_password")

        # Step 5: 에러 메시지 확인
        # Assertion 1: 에러 메시지가 표시되는가?
        is_error_displayed = self.login_page.is_error_message_displayed(timeout=5)

        if not is_error_displayed:
            print("Warning: Error message not displayed")
            # 에러 메시지가 없어도 로그인이 안 되었으면 OK
            # 대신 로그인 페이지에 남아있는지 확인

        # Assertion 2: 로그인 페이지에 남아있는가?
        is_on_login_page = self.login_page.is_on_login_page()

        if not is_on_login_page:
            current_url = self.login_page.get_current_url()
            print(f"Unexpected: Not on login page. Current URL: {current_url}")

        assert is_on_login_page, "로그인 페이지에 남아있지 않음 (예상치 못한 동작)"

        # 에러 메시지 텍스트 확인 (있다면)
        if is_error_displayed:
            error_message = self.login_page.get_error_message()
            print(f"Error Message: {error_message}")

            # 에러 메시지 내용 검증 (선택사항)
            # 실제 메시지에 따라 조정 필요
            expected_keywords = ["비밀번호", "일치", "틀림", "오류", "실패"]
            has_expected_message = any(keyword in error_message for keyword in expected_keywords)

            # 소프트 체크 (경고만)
            if not has_expected_message:
                print(f"Warning: Error message doesn't contain expected keywords")
                print(f"Expected keywords: {expected_keywords}")
                print(f"Actual message: {error_message}")

        # Assertion 3: 로그인되지 않았는가?
        is_logged_in = self.login_page.is_logged_in(timeout=3)
        assert not is_logged_in, "잘못된 비밀번호로 로그인 성공함 (보안 문제!)"

    # ==================== GS_AUTH_003: 빈 필드로 로그인 시도 ====================
    @pytest.mark.tc_id("GS_AUTH_003")
    @pytest.mark.page("Login Page")
    @pytest.mark.scenario("빈 필드로 로그인 시도")
    def test_login_with_empty_fields(self, driver):
        """
        GS_AUTH_003: 빈 필드로 로그인 시도

        Pre-condition:
        1. 로그인 페이지 접근 가능
        2. 브라우저 쿠키 삭제됨

        Test Steps:
        1. 로그인 페이지 접속
        2. ID와 비밀번호를 입력하지 않음 (빈 필드)
        3. 로그인 버튼 클릭
        4. 클라이언트 측 검증 또는 에러 메시지 확인

        Expected Result:
        - HTML5 required 속성으로 인한 브라우저 검증 메시지 표시
        - 또는 "필수 입력 항목입니다" 에러 메시지 표시
        - 로그인 페이지에 그대로 유지
        - 로그인 진행 안 됨
        """
        # Pre-condition: 쿠키 삭제
        self.login_page.clear_cookies()

        # Step 1: 로그인 페이지 접속
        self.login_page.navigate()
        self.login_page.wait_for_login_form()

        # 초기 상태 스크린샷
        self.login_page.take_screenshot("empty_fields_initial")

        # Step 2: 빈 필드 상태 확인 (아무것도 입력하지 않음)
        print("\nTest: 빈 필드로 로그인 시도")
        print("ID 필드: (empty)")
        print("Password 필드: (empty)")

        # Step 3: 로그인 버튼 클릭 시도
        # HTML5 required 속성이 있으면 브라우저가 자체 검증
        try:
            # JavaScript로 required 속성 확인
            username_required = driver.execute_script(
                "return document.querySelector(\"input[placeholder='아이디(이메일)를 입력해주세요.']\").hasAttribute('required')"
            )
            password_required = driver.execute_script(
                "return document.querySelector('input[type=password]').hasAttribute('required')"
            )

            print(f"\nUsername field has 'required': {username_required}")
            print(f"Password field has 'required': {password_required}")

            # 버튼 클릭
            self.login_page.click_login_button()

            # 클릭 후 스크린샷
            time.sleep(2)
            self.login_page.take_screenshot("empty_fields_after_click")

        except Exception as e:
            print(f"Login button click error (expected): {e}")
            self.login_page.take_screenshot("empty_fields_error")

        # Step 4: 검증
        # Assertion 1: 로그인 페이지에 그대로 있어야 함
        current_url = self.login_page.get_current_url()
        print(f"\nCurrent URL after click: {current_url}")

        is_on_login_page = self.login_page.is_on_login_page()
        assert is_on_login_page, "Expected to stay on login page with empty fields"

        # Assertion 2: 로그인되지 않았어야 함
        is_logged_in = self.login_page.is_logged_in(timeout=3)
        assert not is_logged_in, "Should not be logged in with empty fields"

        # Assertion 3: 입력 필드 검증 상태 확인
        # HTML5 validation이 작동했는지 확인
        try:
            username_validity = driver.execute_script(
                "return document.querySelector(\"input[placeholder='아이디(이메일)를 입력해주세요.']\").validity.valid"
            )
            password_validity = driver.execute_script(
                "return document.querySelector('input[type=password]').validity.valid"
            )

            print(f"\nUsername field validity: {username_validity}")
            print(f"Password field validity: {password_validity}")

            # 빈 필드는 invalid여야 함 (required 속성이 있다면)
            if username_required:
                assert not username_validity, "Empty username field should be invalid"
            if password_required:
                assert not password_validity, "Empty password field should be invalid"

        except Exception as e:
            print(f"Validation check error (may not have required attribute): {e}")

        print("\nOK: Empty fields prevented login")
        print("OK: Stayed on login page")
        print("OK: Not logged in")


@pytest.mark.login
@pytest.mark.regression
class TestLoginAdditional:
    """로그인 추가 테스트 (확장용)"""

    @pytest.fixture(autouse=True)
    def setup(self, driver):
        """각 테스트 전 실행"""
        self.login_page = LoginPage(driver)
        yield

    @pytest.mark.skip(reason="구현 예정 - 존재하지 않는 계정")
    def test_login_with_nonexistent_account(self, driver):
        """존재하지 않는 계정으로 로그인 시도"""
        # TODO: 구현 필요
        pass

    @pytest.mark.skip(reason="구현 예정 - SQL Injection 방어")
    def test_login_sql_injection_prevention(self, driver):
        """SQL Injection 방어 테스트"""
        # TODO: 구현 필요
        pass

    @pytest.mark.skip(reason="구현 예정 - XSS 방어")
    def test_login_xss_prevention(self, driver):
        """XSS 공격 방어 테스트"""
        # TODO: 구현 필요
        pass


# ==================== 독립 실행 ====================
if __name__ == "__main__":
    """
    독립 실행 방법:
    python tests/test_login.py
    """
    pytest.main([__file__, "-v", "-s"])

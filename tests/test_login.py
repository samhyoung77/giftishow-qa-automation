"""
로그인 테스트 모듈

Test Cases:
- GS_AUTH_001 + GS_AUTH_004: 로그인/로그아웃 통합 테스트 (test_login_and_logout)
- GS_AUTH_002: 잘못된 비밀번호 로그인 (test_login_with_wrong_password)
- GS_AUTH_003: 빈 필드로 로그인 시도 (test_login_with_empty_fields)

실행 방법:
- 로그인/로그아웃: pytest tests/test_login.py::TestLogin::test_login_and_logout -v -s
- 전체: pytest tests/test_login.py -v -s
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

    @pytest.mark.tc_id("GS_AUTH_001_004")
    @pytest.mark.page("Login Page")
    @pytest.mark.scenario("정상 로그인 및 로그아웃")
    def test_login_and_logout(self, driver, test_data, sheets_reporter):
        """
        GS_AUTH_001 + GS_AUTH_004: 로그인/로그아웃 통합 테스트

        Test Steps:
        1. 로그인 페이지 접속 및 아이디/비밀번호 자동 입력
        2. 수동 로그인 (2FA 포함)
        3. 로그인 성공 확인
        4. 로그아웃 수행 및 확인
        """
        # ==================== PART 1: GS_AUTH_001 로그인 ====================
        print("\n" + "=" * 60)
        print("📌 [GS_AUTH_001] 정상 로그인 테스트")
        print("=" * 60)

        # Step 1: 로그인 페이지로 이동 및 자동 입력
        print("\n[Step 1] 로그인 페이지 이동...")
        self.login_page.navigate()
        time.sleep(2)

        username = test_data.get('valid_user', {}).get('username', '')
        password = test_data.get('valid_user', {}).get('password', '')

        if username and password:
            self.login_page.enter_username(username)
            self.login_page.enter_password(password)
            print(f"✓ 계정 정보 자동 입력 완료 (ID: {username[:3]}***)")

        # Step 2: 수동 로그인 대기
        print("\n" + "🔔" * 20)
        print("\n  👆 브라우저 창을 확인하세요!")
        print("  1️⃣  [로그인] 버튼 클릭")
        print("  2️⃣  카카오톡 인증번호 입력")
        print("  3️⃣  로그인 완료 후 여기로 돌아오세요")
        print("\n" + "🔔" * 20)
        input("\n>>> 로그인 완료 후 Enter 키를 누르세요: ")

        # Step 3: 로그인 확인
        print("\n[Step 2] 로그인 상태 확인...")
        time.sleep(2)

        if self.login_page.is_logged_in(timeout=10):
            print("✅ [GS_AUTH_001] 로그인 성공!")
            self.login_page.take_screenshot("GS_AUTH_001_login_success")
        else:
            self.login_page.take_screenshot("GS_AUTH_001_login_failed")
            assert False, "GS_AUTH_001 실패: 로그인 실패"

        # ==================== PART 2: GS_AUTH_004 로그아웃 ====================
        print("\n" + "=" * 60)
        print("📌 [GS_AUTH_004] 정상 로그아웃 테스트")
        print("=" * 60)

        print("\n[Step 3] 로그아웃 수행...")
        if self.login_page.logout():
            print("✅ [GS_AUTH_004] 로그아웃 성공!")
            self.login_page.take_screenshot("GS_AUTH_004_logout_success")
        else:
            self.login_page.take_screenshot("GS_AUTH_004_logout_failed")
            assert False, "GS_AUTH_004 실패: 로그아웃 실패"

        time.sleep(2)
        assert self.login_page.is_logged_out(), "로그아웃 후에도 로그인 상태가 유지됨"

        print("\n" + "=" * 60)
        print("🎉 테스트 완료!")
        print("   - GS_AUTH_001 (로그인): PASS")
        print("   - GS_AUTH_004 (로그아웃): PASS")
        print("=" * 60)

    @pytest.mark.tc_id("GS_AUTH_002")
    @pytest.mark.page("Login Page")
    @pytest.mark.scenario("잘못된 비밀번호 로그인")
    def test_login_with_wrong_password(self, driver, test_data, sheets_reporter):
        """
        GS_AUTH_002: 잘못된 비밀번호 로그인 테스트

        Expected Result:
        - 에러 메시지 표시
        - 로그인 페이지 유지
        """
        self.login_page.navigate()
        self.login_page.wait_for_login_form()

        username = test_data.get('valid_user', {}).get('username', 'test_user')
        self.login_page.login(username, "wrong_password_12345")

        time.sleep(2)
        self.login_page.take_screenshot("login_wrong_password")

        # 로그인 페이지에 남아있어야 함
        assert self.login_page.is_on_login_page(), "로그인 페이지에 남아있지 않음"
        assert not self.login_page.is_logged_in(timeout=3), "잘못된 비밀번호로 로그인됨"

    @pytest.mark.tc_id("GS_AUTH_003")
    @pytest.mark.page("Login Page")
    @pytest.mark.scenario("빈 필드로 로그인 시도")
    def test_login_with_empty_fields(self, driver, test_data, sheets_reporter):
        """
        GS_AUTH_003: 빈 필드로 로그인 시도

        Case 1: 둘 다 빈 필드 → '아이디를 입력해주세요'
        Case 2: 아이디만 입력 → '비밀번호를 입력해주세요'
        """
        self.login_page.navigate()
        self.login_page.wait_for_login_form()

        # Case 1: 둘 다 빈 필드
        print("\n[Case 1] 아이디/비밀번호 둘 다 빈 필드")
        self.login_page.click_login_button()
        time.sleep(1)
        self.login_page.take_screenshot("GS_AUTH_003_case1_empty_both")

        assert self.login_page.is_username_error_displayed(), "'아이디를 입력해주세요' 에러가 표시되어야 함"
        print("✓ '아이디를 입력해주세요' 에러 메시지 확인")

        # Case 2: 아이디만 입력, 비밀번호 빈 필드
        print("\n[Case 2] 아이디만 입력, 비밀번호 빈 필드")
        self.login_page.navigate()  # 페이지 새로고침
        self.login_page.wait_for_login_form()

        username = test_data.get('valid_user', {}).get('username', 'test@test.com')
        self.login_page.enter_username(username)
        self.login_page.click_login_button()
        time.sleep(1)
        self.login_page.take_screenshot("GS_AUTH_003_case2_empty_password")

        assert self.login_page.is_password_error_displayed(), "'비밀번호를 입력해주세요' 에러가 표시되어야 함"
        print("✓ '비밀번호를 입력해주세요' 에러 메시지 확인")

        # 공통 검증
        assert self.login_page.is_on_login_page(), "로그인 페이지에 남아있어야 함"
        assert not self.login_page.is_logged_in(timeout=3), "빈 필드로 로그인되면 안 됨"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

"""
LoginPage - 로그인 페이지 Page Object
GS_AUTH_001, GS_AUTH_002 시나리오 구현
"""
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from pages.base_page import BasePage
from utils.cookie_manager import CookieManager
import time


class LoginPage(BasePage):
    """
    기프티쇼 비즈 로그인 페이지

    Test Cases:
    - GS_AUTH_001: 정상 로그인
    - GS_AUTH_002: 잘못된 비밀번호 로그인
    """

    # ==================== Locators ====================
    # Chrome plugin으로 확인한 실제 기프티쇼 로그인 페이지 Locator

    # 입력 필드
    USERNAME_INPUT = (By.CSS_SELECTOR, "input[placeholder='아이디(이메일)를 입력해주세요.']")
    PASSWORD_INPUT = (By.CSS_SELECTOR, "input[type='password']")

    # 버튼
    LOGIN_BUTTON = (By.XPATH, "//button[contains(., '로그인')]")

    # 에러/성공 메시지
    ERROR_MESSAGE = (By.CLASS_NAME, "login-error")  # find_login_elements.py로 발견
    SUCCESS_MESSAGE = (By.CLASS_NAME, "success-message")

    # 로그인 후 확인용 요소
    USER_MENU = (By.CLASS_NAME, "user-menu")  # 로그인 후 표시되는 사용자 메뉴
    LOGOUT_BUTTON = (By.ID, "logout_btn")

    # 대체 Locators (웹사이트에 따라 주석 해제)
    # USERNAME_INPUT = (By.NAME, "email")
    # USERNAME_INPUT = (By.CSS_SELECTOR, "input[name='username']")
    # PASSWORD_INPUT = (By.CSS_SELECTOR, "input[type='password']")
    # LOGIN_BUTTON = (By.XPATH, "//button[contains(text(), '로그인')]")
    # ERROR_MESSAGE = (By.XPATH, "//div[contains(@class, 'error')]")

    # ==================== URL ====================
    def __init__(self, driver, base_url=None):
        """
        LoginPage 초기화

        Args:
            driver: Selenium WebDriver 인스턴스
            base_url: 기본 URL (None이면 Config에서 가져옴)
        """
        super().__init__(driver)

        if base_url:
            self.base_url = base_url
        else:
            from utils.config import Config
            self.base_url = Config.BASE_URL

        # 로그인 페이지 URL (find_login_elements.py로 확인완료)
        self.login_url = "https://biz.giftishow.com/login"

        # Cookie Manager 초기화 (2FA 우회용)
        self.cookie_manager = CookieManager()

    # ==================== Navigation ====================
    def navigate(self):
        """
        로그인 페이지로 이동

        Test Step:
        - GS_AUTH_001 Step 1: 로그인 페이지 접속
        - GS_AUTH_002 Step 1: 로그인 페이지 접속
        """
        self.navigate_to(self.login_url)
        self.wait_for_page_load()
        self.logger.info(f"Navigated to login page: {self.login_url}")

    # ==================== Actions ====================
    def enter_username(self, username):
        """
        사용자 ID 입력

        Args:
            username: 사용자 ID 또는 이메일

        Test Step:
        - GS_AUTH_001 Step 2: 사용자 ID 입력
        - GS_AUTH_002 Step 2: 유효한 ID 입력
        """
        try:
            self.input_text(self.USERNAME_INPUT, username)
            self.logger.info(f"Entered username: {username}")
        except Exception as e:
            self.logger.error(f"Failed to enter username: {e}")
            self.take_screenshot("error_enter_username")
            raise

    def enter_password(self, password):
        """
        비밀번호 입력

        Args:
            password: 비밀번호

        Test Step:
        - GS_AUTH_001 Step 3: 비밀번호 입력
        - GS_AUTH_002 Step 3: 잘못된 비밀번호 입력
        """
        try:
            self.input_text(self.PASSWORD_INPUT, password)
            self.logger.info("Entered password (hidden)")
        except Exception as e:
            self.logger.error(f"Failed to enter password: {e}")
            self.take_screenshot("error_enter_password")
            raise

    def click_login_button(self):
        """
        로그인 버튼 클릭

        Test Step:
        - GS_AUTH_001 Step 4: 로그인 버튼 클릭
        - GS_AUTH_002 Step 4: 로그인 버튼 클릭
        """
        try:
            self.click(self.LOGIN_BUTTON)
            self.logger.info("Clicked login button")

            # 로그인 처리 대기 (페이지 전환 또는 에러 메시지)
            time.sleep(2)
        except Exception as e:
            self.logger.error(f"Failed to click login button: {e}")
            self.take_screenshot("error_click_login")
            raise

    def login(self, username, password):
        """
        로그인 전체 프로세스 (ID 입력 → PW 입력 → 로그인 버튼 클릭)

        Args:
            username: 사용자 ID
            password: 비밀번호

        Test Steps:
        - GS_AUTH_001 Steps 2-4: 전체 로그인 프로세스
        - GS_AUTH_002 Steps 2-4: 전체 로그인 프로세스
        """
        self.enter_username(username)
        self.enter_password(password)
        self.click_login_button()
        self.logger.info(f"Login process completed for user: {username}")

    # ==================== Verifications ====================
    def is_logged_in(self, timeout=10):
        """
        로그인 성공 여부 확인

        다음 중 하나로 확인:
        1. URL이 메인 페이지로 변경됨 (login 페이지가 아님)
        2. "마이비즈" 텍스트가 페이지에 표시됨
        3. mybiz URL로 이동됨

        Args:
            timeout: 대기 시간 (초)

        Returns:
            bool: 로그인 성공 시 True

        Test Step:
        - GS_AUTH_001 Step 5: 메인 페이지 이동 확인
        - GS_AUTH_001 Expected: 메인 페이지로 리다이렉트
        """
        try:
            import time
            # 페이지 전환 대기
            time.sleep(2)

            # 방법 1: URL 확인 (로그인 페이지가 아니면 성공)
            current_url = self.get_current_url()
            if "login" not in current_url.lower() and "signin" not in current_url.lower():
                self.logger.info(f"Login successful - URL changed to: {current_url}")
                return True

            # 방법 2: "마이비즈" 텍스트 확인 (Chrome plugin 권장사항)
            try:
                from selenium.webdriver.common.by import By
                mybiz_element = self.driver.find_element(By.XPATH, "//span[contains(text(), '마이비즈')]")
                if mybiz_element:
                    self.logger.info("Login successful - '마이비즈' text found")
                    return True
            except:
                pass

            # 방법 3: mybiz URL 확인
            if "mybiz" in current_url.lower():
                self.logger.info(f"Login successful - mybiz URL detected: {current_url}")
                return True

            self.logger.warning("Could not verify login success")
            return False

        except Exception as e:
            self.logger.error(f"Error checking login status: {e}")
            return False

    def is_error_message_displayed(self, timeout=5):
        """
        에러 메시지 표시 여부 확인

        Args:
            timeout: 대기 시간 (초)

        Returns:
            bool: 에러 메시지가 표시되면 True

        Test Step:
        - GS_AUTH_002 Step 5: 에러 메시지 확인
        """
        try:
            is_visible = self.is_element_visible(self.ERROR_MESSAGE, timeout=timeout)
            if is_visible:
                self.logger.info("Error message is displayed")
            return is_visible
        except Exception as e:
            self.logger.error(f"Error checking error message: {e}")
            return False

    def get_error_message(self):
        """
        에러 메시지 텍스트 가져오기

        Returns:
            str: 에러 메시지 텍스트

        Test Step:
        - GS_AUTH_002 Expected: '아이디 또는 비밀번호가 일치하지 않습니다' 메시지
        """
        try:
            if self.is_error_message_displayed():
                error_text = self.get_text(self.ERROR_MESSAGE)
                self.logger.info(f"Error message: {error_text}")
                return error_text
            else:
                self.logger.warning("No error message found")
                return ""
        except Exception as e:
            self.logger.error(f"Failed to get error message: {e}")
            return ""

    def is_on_login_page(self):
        """
        현재 로그인 페이지에 있는지 확인

        Returns:
            bool: 로그인 페이지면 True

        Test Step:
        - GS_AUTH_002 Expected: 로그인 페이지 유지
        """
        current_url = self.get_current_url()
        is_login_page = "login" in current_url.lower() or "signin" in current_url.lower()

        if is_login_page:
            self.logger.info(f"Currently on login page: {current_url}")
        else:
            self.logger.info(f"Not on login page. Current URL: {current_url}")

        return is_login_page

    # ==================== Helper Methods ====================
    def clear_cookies(self):
        """
        브라우저 쿠키 삭제

        Test Pre-condition:
        - GS_AUTH_001: 브라우저 쿠키 삭제됨
        """
        try:
            self.driver.delete_all_cookies()
            self.logger.info("All cookies cleared")
        except Exception as e:
            self.logger.error(f"Failed to clear cookies: {e}")

    def wait_for_login_form(self, timeout=10):
        """
        로그인 폼이 로드될 때까지 대기

        Args:
            timeout: 대기 시간 (초)
        """
        try:
            self.wait_for_page_load(timeout)
            self.is_element_visible(self.USERNAME_INPUT, timeout)
            self.is_element_visible(self.PASSWORD_INPUT, timeout)
            self.is_element_visible(self.LOGIN_BUTTON, timeout)
            self.logger.info("Login form is ready")
        except TimeoutException:
            self.logger.error("Login form did not load in time")
            self.take_screenshot("error_login_form_timeout")
            raise

    def take_login_screenshot(self, name="login_page"):
        """
        로그인 페이지 스크린샷 저장

        Args:
            name: 파일명
        """
        return self.take_screenshot(name)

    # ==================== Cookie-based Login (2FA 우회) ====================
    def login_with_saved_cookies(self):
        """
        저장된 쿠키로 자동 로그인 (2FA 우회)

        Returns:
            bool: 성공 여부
        """
        if not self.cookie_manager.cookies_exist():
            self.logger.warning("저장된 쿠키가 없습니다. manual_login.py를 먼저 실행하세요.")
            return False

        try:
            # 로그인 페이지로 이동
            self.navigate_to(self.login_url)

            # 쿠키 로드
            self.logger.info("저장된 쿠키로 로그인 시도 중...")
            success = self.cookie_manager.load_cookies(self.driver, self.login_url)

            if success:
                time.sleep(2)  # 쿠키 적용 대기

                # 로그인 확인
                if self.is_logged_in(timeout=5):
                    self.logger.info("✓ 쿠키 로그인 성공!")
                    return True
                else:
                    self.logger.warning("쿠키 로드 후 로그인 확인 실패")
                    return False
            else:
                return False

        except Exception as e:
            self.logger.error(f"쿠키 로그인 실패: {e}")
            return False

    def save_current_session(self):
        """
        현재 세션의 쿠키 저장

        Returns:
            bool: 성공 여부
        """
        try:
            current_url = self.get_current_url()
            success = self.cookie_manager.save_cookies(self.driver, url=current_url)
            if success:
                self.logger.info("✓ 현재 세션 쿠키 저장 완료")
            return success
        except Exception as e:
            self.logger.error(f"세션 저장 실패: {e}")
            return False

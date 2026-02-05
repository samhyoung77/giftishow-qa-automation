"""
LoginPage - 로그인 페이지 Page Object
"""
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from pages.base_page import BasePage
import time


class LoginPage(BasePage):
    """기프티쇼 비즈 로그인 페이지"""

    # ==================== Locators ====================
    USERNAME_INPUT = (By.CSS_SELECTOR, "input[placeholder='아이디(이메일)를 입력해주세요.']")
    PASSWORD_INPUT = (By.CSS_SELECTOR, "input[type='password']")
    LOGIN_BUTTON = (By.XPATH, "//button[contains(., '로그인')]")
    ERROR_POPUP = (By.XPATH, "//div[contains(text(), '등록되지 않은') or contains(text(), '비밀번호를 잘못')]")
    ERROR_MESSAGE = (By.CLASS_NAME, "login-error")

    # 빈 필드 에러 메시지
    USERNAME_EMPTY_ERROR = (By.XPATH, "//*[contains(text(), '아이디를 입력해주세요')]")
    PASSWORD_EMPTY_ERROR = (By.XPATH, "//*[contains(text(), '비밀번호를 입력해주세요')]")

    def __init__(self, driver, base_url=None):
        super().__init__(driver)

        if base_url:
            self.base_url = base_url
        else:
            from utils.config import Config
            self.base_url = Config.BASE_URL

        self.login_url = "https://biz.giftishow.com/login"

    # ==================== Navigation ====================
    def navigate(self):
        """로그인 페이지로 이동"""
        self.navigate_to(self.login_url)
        self.wait_for_page_load()
        self.logger.info(f"Navigated to login page: {self.login_url}")

    # ==================== Actions ====================
    def enter_username(self, username):
        """사용자 ID 입력"""
        try:
            self.input_text(self.USERNAME_INPUT, username)
            self.logger.info(f"Entered username: {username}")
        except Exception as e:
            self.logger.error(f"Failed to enter username: {e}")
            raise

    def enter_password(self, password):
        """비밀번호 입력"""
        try:
            self.input_text(self.PASSWORD_INPUT, password)
            self.logger.info("Entered password")
        except Exception as e:
            self.logger.error(f"Failed to enter password: {e}")
            raise

    def click_login_button(self):
        """로그인 버튼 클릭"""
        try:
            self.click(self.LOGIN_BUTTON)
            self.logger.info("Clicked login button")
            time.sleep(2)
        except Exception as e:
            self.logger.error(f"Failed to click login button: {e}")
            raise

    def login(self, username, password):
        """로그인 전체 프로세스"""
        self.enter_username(username)
        self.enter_password(password)
        self.click_login_button()

    # ==================== Verifications ====================
    def is_logged_in(self, timeout=10):
        """로그인 성공 여부 확인"""
        try:
            time.sleep(2)
            current_url = self.get_current_url()

            # 로그인 폼이 보이면 로그인 안 됨
            try:
                login_form = self.driver.find_element(By.XPATH, "//input[@placeholder='아이디(이메일)를 입력해주세요.']")
                if login_form.is_displayed():
                    return False
            except:
                pass

            # 방법 1: "마이비즈" 텍스트 확인
            try:
                mybiz_element = self.driver.find_element(By.XPATH, "//span[contains(text(), '마이비즈')]")
                if mybiz_element and mybiz_element.is_displayed():
                    self.logger.info("✓ 로그인 확인 - 마이비즈 텍스트")
                    return True
            except:
                pass

            # 방법 2: gBizUserNo 쿠키 확인
            try:
                cookies = self.driver.get_cookies()
                for cookie in cookies:
                    if cookie.get('name') == 'gBizUserNo' and cookie.get('value'):
                        self.logger.info("✓ 로그인 확인 - gBizUserNo 쿠키")
                        return True
            except:
                pass

            # 방법 3: 로그아웃 버튼 확인
            try:
                logout_selectors = [
                    "//*[contains(text(), '로그아웃')]",
                    "//a[contains(., '로그아웃')]",
                    "//button[contains(., '로그아웃')]",
                ]
                for selector in logout_selectors:
                    try:
                        logout_elem = self.driver.find_element(By.XPATH, selector)
                        if logout_elem and logout_elem.is_displayed():
                            self.logger.info("✓ 로그인 확인 - 로그아웃 버튼")
                            return True
                    except:
                        continue
            except:
                pass

            # 방법 4: mybiz URL 확인
            if "mybiz" in current_url.lower():
                self.logger.info("✓ 로그인 확인 - mybiz URL")
                return True

            return False

        except Exception as e:
            self.logger.error(f"Error checking login status: {e}")
            return False

    def is_error_message_displayed(self, timeout=5):
        """에러 메시지 표시 여부 확인"""
        try:
            if self.is_element_visible(self.ERROR_POPUP, timeout=timeout):
                return True

            page_source = self.driver.page_source
            error_keywords = ["등록되지 않은", "비밀번호를 잘못", "일치하지 않습니다"]
            for keyword in error_keywords:
                if keyword in page_source:
                    return True

            return False
        except:
            return False

    def is_on_login_page(self):
        """현재 로그인 페이지에 있는지 확인"""
        current_url = self.get_current_url()
        return "login" in current_url.lower()

    def is_empty_field_error_displayed(self):
        """빈 필드 에러 메시지 표시 여부 확인 (둘 중 하나라도)"""
        return self.is_username_error_displayed() or self.is_password_error_displayed()

    def is_username_error_displayed(self):
        """'아이디를 입력해주세요' 에러 메시지 표시 여부 확인"""
        try:
            if self.is_element_visible(self.USERNAME_EMPTY_ERROR, timeout=2):
                self.logger.info("✓ 에러 표시됨: 아이디를 입력해주세요")
                return True
            return False
        except:
            return False

    def is_password_error_displayed(self):
        """'비밀번호를 입력해주세요' 에러 메시지 표시 여부 확인"""
        try:
            if self.is_element_visible(self.PASSWORD_EMPTY_ERROR, timeout=2):
                self.logger.info("✓ 에러 표시됨: 비밀번호를 입력해주세요")
                return True
            return False
        except:
            return False

    # ==================== Helper Methods ====================
    def clear_cookies(self):
        """브라우저 쿠키 삭제"""
        try:
            self.driver.delete_all_cookies()
            self.logger.info("All cookies cleared")
        except Exception as e:
            self.logger.error(f"Failed to clear cookies: {e}")

    def wait_for_login_form(self, timeout=10):
        """로그인 폼이 로드될 때까지 대기"""
        try:
            self.wait_for_page_load(timeout)
            self.is_element_visible(self.USERNAME_INPUT, timeout)
            self.is_element_visible(self.PASSWORD_INPUT, timeout)
            self.is_element_visible(self.LOGIN_BUTTON, timeout)
            self.logger.info("Login form is ready")
        except TimeoutException:
            self.logger.error("Login form did not load in time")
            raise

    # ==================== Logout ====================
    def logout(self):
        """로그아웃 수행"""
        try:
            # 방법 1: 로그아웃 버튼 클릭
            logout_selectors = [
                (By.XPATH, "//*[contains(text(), '로그아웃')]"),
                (By.XPATH, "//a[contains(., '로그아웃')]"),
                (By.XPATH, "//a[contains(@href, 'logout')]"),
            ]

            for selector in logout_selectors:
                try:
                    logout_btn = self.driver.find_element(*selector)
                    if logout_btn and logout_btn.is_displayed():
                        logout_btn.click()
                        self.logger.info("Logout button clicked")
                        time.sleep(2)

                        if "login" in self.get_current_url().lower():
                            return True
                except:
                    continue

            # 방법 2: 로그아웃 URL 직접 호출
            try:
                self.navigate_to(f"{self.base_url}/logout")
                time.sleep(2)
                if "login" in self.get_current_url().lower():
                    return True
            except:
                pass

            # 방법 3: 쿠키 삭제로 강제 로그아웃
            self.clear_cookies()
            self.navigate_to(self.login_url)
            time.sleep(2)
            return self.is_on_login_page()

        except Exception as e:
            self.logger.error(f"로그아웃 중 오류: {e}")
            return False

    def is_logged_out(self, timeout=5):
        """로그아웃 상태 확인"""
        if self.is_on_login_page():
            return True
        return not self.is_logged_in(timeout=timeout)

"""
BasePage - 모든 Page Object의 기본 클래스
공통 메서드와 유틸리티 함수 제공
"""
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging
from datetime import datetime
import os


class BasePage:
    """모든 페이지 객체의 기본 클래스"""

    def __init__(self, driver, timeout=10):
        """
        BasePage 초기화

        Args:
            driver: Selenium WebDriver 인스턴스
            timeout: 기본 대기 시간 (초)
        """
        self.driver = driver
        self.timeout = timeout
        self.wait = WebDriverWait(driver, timeout)
        self.logger = logging.getLogger(self.__class__.__name__)

    def find_element(self, locator):
        """
        요소 찾기 (대기 포함)

        Args:
            locator: (By.METHOD, "value") 형식의 튜플

        Returns:
            WebElement
        """
        try:
            element = self.wait.until(EC.presence_of_element_located(locator))
            self.logger.debug(f"Element found: {locator}")
            return element
        except TimeoutException:
            self.logger.error(f"Element not found: {locator}")
            raise

    def find_elements(self, locator):
        """
        여러 요소 찾기

        Args:
            locator: (By.METHOD, "value") 형식의 튜플

        Returns:
            List[WebElement]
        """
        try:
            elements = self.wait.until(EC.presence_of_all_elements_located(locator))
            self.logger.debug(f"Elements found: {locator}, count: {len(elements)}")
            return elements
        except TimeoutException:
            self.logger.error(f"Elements not found: {locator}")
            return []

    def click(self, locator):
        """
        요소 클릭

        Args:
            locator: (By.METHOD, "value") 형식의 튜플
        """
        element = self.wait.until(EC.element_to_be_clickable(locator))
        element.click()
        self.logger.debug(f"Clicked: {locator}")

    def input_text(self, locator, text):
        """
        텍스트 입력

        Args:
            locator: (By.METHOD, "value") 형식의 튜플
            text: 입력할 텍스트
        """
        element = self.find_element(locator)
        element.clear()
        element.send_keys(text)
        self.logger.debug(f"Input text: {locator} = '{text}'")

    def get_text(self, locator):
        """
        요소의 텍스트 가져오기

        Args:
            locator: (By.METHOD, "value") 형식의 튜플

        Returns:
            str: 요소의 텍스트
        """
        element = self.find_element(locator)
        text = element.text
        self.logger.debug(f"Get text: {locator} = '{text}'")
        return text

    def get_attribute(self, locator, attribute_name):
        """
        요소의 속성값 가져오기

        Args:
            locator: (By.METHOD, "value") 형식의 튜플
            attribute_name: 속성명

        Returns:
            str: 속성값
        """
        element = self.find_element(locator)
        value = element.get_attribute(attribute_name)
        self.logger.debug(f"Get attribute: {locator}[{attribute_name}] = '{value}'")
        return value

    def is_element_visible(self, locator, timeout=None):
        """
        요소가 보이는지 확인

        Args:
            locator: (By.METHOD, "value") 형식의 튜플
            timeout: 대기 시간 (None이면 기본값 사용)

        Returns:
            bool: 요소가 보이면 True
        """
        try:
            wait_time = timeout if timeout else self.timeout
            wait = WebDriverWait(self.driver, wait_time)
            wait.until(EC.visibility_of_element_located(locator))
            self.logger.debug(f"Element visible: {locator}")
            return True
        except TimeoutException:
            self.logger.debug(f"Element not visible: {locator}")
            return False

    def is_element_present(self, locator):
        """
        요소가 존재하는지 확인 (보이지 않아도 됨)

        Args:
            locator: (By.METHOD, "value") 형식의 튜플

        Returns:
            bool: 요소가 존재하면 True
        """
        try:
            self.driver.find_element(*locator)
            return True
        except NoSuchElementException:
            return False

    def wait_for_element_to_disappear(self, locator, timeout=None):
        """
        요소가 사라질 때까지 대기

        Args:
            locator: (By.METHOD, "value") 형식의 튜플
            timeout: 대기 시간 (None이면 기본값 사용)
        """
        wait_time = timeout if timeout else self.timeout
        wait = WebDriverWait(self.driver, wait_time)
        wait.until(EC.invisibility_of_element_located(locator))
        self.logger.debug(f"Element disappeared: {locator}")

    def scroll_to_element(self, locator):
        """
        요소까지 스크롤

        Args:
            locator: (By.METHOD, "value") 형식의 튜플
        """
        element = self.find_element(locator)
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        self.logger.debug(f"Scrolled to: {locator}")

    def hover_over_element(self, locator):
        """
        요소 위에 마우스 오버

        Args:
            locator: (By.METHOD, "value") 형식의 튜플
        """
        element = self.find_element(locator)
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        self.logger.debug(f"Hovered over: {locator}")

    def take_screenshot(self, name=None):
        """
        스크린샷 저장

        Args:
            name: 파일명 (None이면 타임스탬프 사용)

        Returns:
            str: 저장된 파일 경로
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if name is None:
            name = f"screenshot_{timestamp}"
        else:
            # 기존 이름에 타임스탬프 추가
            name = f"{name}_{timestamp}"

        # .png 확장자가 없으면 추가
        if not name.endswith('.png'):
            name = f"{name}.png"

        screenshot_dir = "reports/screenshots"
        os.makedirs(screenshot_dir, exist_ok=True)

        filepath = os.path.join(screenshot_dir, name)
        self.driver.save_screenshot(filepath)
        self.logger.info(f"Screenshot saved: {filepath}")
        return filepath

    def get_current_url(self):
        """
        현재 URL 가져오기

        Returns:
            str: 현재 URL
        """
        url = self.driver.current_url
        self.logger.debug(f"Current URL: {url}")
        return url

    def get_page_title(self):
        """
        페이지 타이틀 가져오기

        Returns:
            str: 페이지 타이틀
        """
        title = self.driver.title
        self.logger.debug(f"Page title: {title}")
        return title

    def navigate_to(self, url):
        """
        URL로 이동

        Args:
            url: 이동할 URL
        """
        self.driver.get(url)
        self.logger.info(f"Navigated to: {url}")

    def refresh_page(self):
        """페이지 새로고침"""
        self.driver.refresh()
        self.logger.debug("Page refreshed")

    def go_back(self):
        """뒤로 가기"""
        self.driver.back()
        self.logger.debug("Navigated back")

    def switch_to_iframe(self, locator):
        """
        iframe으로 전환

        Args:
            locator: (By.METHOD, "value") 형식의 튜플
        """
        iframe = self.find_element(locator)
        self.driver.switch_to.frame(iframe)
        self.logger.debug(f"Switched to iframe: {locator}")

    def switch_to_default_content(self):
        """기본 컨텐츠로 전환 (iframe에서 나오기)"""
        self.driver.switch_to.default_content()
        self.logger.debug("Switched to default content")

    def execute_javascript(self, script, *args):
        """
        JavaScript 실행

        Args:
            script: 실행할 JavaScript 코드
            *args: JavaScript에 전달할 인자

        Returns:
            JavaScript 실행 결과
        """
        result = self.driver.execute_script(script, *args)
        self.logger.debug(f"Executed JS: {script[:50]}...")
        return result

    def wait_for_page_load(self, timeout=30):
        """
        페이지 로드 완료 대기

        Args:
            timeout: 대기 시간 (초)
        """
        wait = WebDriverWait(self.driver, timeout)
        wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
        self.logger.debug("Page loaded")

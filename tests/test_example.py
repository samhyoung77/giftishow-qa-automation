"""
예제 테스트 파일
프로젝트 구조 확인 및 기본 동작 테스트
"""
import pytest
from pages.base_page import BasePage


@pytest.mark.smoke
class TestExample:
    """예제 테스트 클래스"""

    @pytest.mark.tc_id("GS_EXAMPLE_001")
    @pytest.mark.page("Main Page")
    @pytest.mark.scenario("기프티쇼 메인 페이지 접속")
    def test_open_main_page(self, driver, config):
        """메인 페이지 접속 테스트"""
        # Given
        base_page = BasePage(driver)

        # When
        base_page.navigate_to(config.BASE_URL)
        base_page.wait_for_page_load()

        # Then
        current_url = base_page.get_current_url()
        assert config.BASE_URL in current_url, f"URL 불일치: {current_url}"

        # 페이지 타이틀 확인
        title = base_page.get_page_title()
        assert title is not None, "페이지 타이틀이 없습니다"
        print(f"Page Title: {title}")

    @pytest.mark.tc_id("GS_EXAMPLE_002")
    @pytest.mark.page("Main Page")
    @pytest.mark.scenario("스크린샷 저장 테스트")
    def test_screenshot(self, driver, config):
        """스크린샷 기능 테스트"""
        # Given
        base_page = BasePage(driver)
        base_page.navigate_to(config.BASE_URL)
        base_page.wait_for_page_load()

        # When
        screenshot_path = base_page.take_screenshot("example_screenshot")

        # Then
        import os
        assert os.path.exists(screenshot_path), "스크린샷이 저장되지 않았습니다"
        print(f"Screenshot saved: {screenshot_path}")

    @pytest.mark.tc_id("GS_EXAMPLE_003")
    @pytest.mark.page("Config Test")
    @pytest.mark.scenario("설정 로드 테스트")
    def test_config_loaded(self, config):
        """설정 파일 로드 확인"""
        # 필수 설정 값 확인
        assert config.BASE_URL is not None
        assert config.BROWSER is not None
        assert config.IMPLICIT_WAIT > 0
        assert config.EXPLICIT_WAIT > 0

        print(f"BASE_URL: {config.BASE_URL}")
        print(f"BROWSER: {config.BROWSER}")
        print(f"HEADLESS: {config.HEADLESS}")

    @pytest.mark.tc_id("GS_EXAMPLE_004")
    @pytest.mark.page("Data Test")
    @pytest.mark.scenario("테스트 데이터 로드 확인")
    def test_data_loaded(self, test_data):
        """테스트 데이터 로드 확인"""
        # 테스트 데이터 구조 확인
        assert 'valid_user' in test_data
        assert 'username' in test_data['valid_user']
        assert 'password' in test_data['valid_user']

        print(f"Test data keys: {test_data.keys()}")

    @pytest.mark.tc_id("GS_EXAMPLE_005")
    @pytest.mark.page("Google Sheets")
    @pytest.mark.scenario("Google Sheets 연결 테스트")
    def test_google_sheets_connection(self, sheets_reporter):
        """Google Sheets 연결 확인"""
        if sheets_reporter is None:
            pytest.skip("Google Sheets reporter not available")

        # 연결 상태 확인
        assert sheets_reporter.client is not None, "Google Sheets client not initialized"
        print("Google Sheets connection successful")


@pytest.mark.regression
class TestBasicNavigation:
    """기본 네비게이션 테스트"""

    @pytest.mark.tc_id("GS_NAV_001")
    @pytest.mark.page("Navigation")
    @pytest.mark.scenario("페이지 새로고침")
    def test_page_refresh(self, driver, config):
        """페이지 새로고침 테스트"""
        base_page = BasePage(driver)
        base_page.navigate_to(config.BASE_URL)

        # 새로고침
        base_page.refresh_page()
        base_page.wait_for_page_load()

        # URL이 동일한지 확인
        assert config.BASE_URL in base_page.get_current_url()

    @pytest.mark.tc_id("GS_NAV_002")
    @pytest.mark.page("Navigation")
    @pytest.mark.scenario("JavaScript 실행")
    def test_javascript_execution(self, driver, config):
        """JavaScript 실행 테스트"""
        base_page = BasePage(driver)
        base_page.navigate_to(config.BASE_URL)

        # JavaScript로 페이지 타이틀 가져오기
        title = base_page.execute_javascript("return document.title;")
        assert title is not None
        print(f"Title from JS: {title}")

        # 스크롤 테스트
        base_page.execute_javascript("window.scrollTo(0, 100);")
        scroll_position = base_page.execute_javascript("return window.pageYOffset;")
        assert scroll_position >= 0

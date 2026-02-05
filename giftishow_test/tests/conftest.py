"""
conftest.py - pytest 설정 및 fixtures
"""
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import undetected_chromedriver as uc
from datetime import datetime
import json
import os
import sys

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.config import Config
from utils.logger import get_test_logger
from utils.google_sheets import GoogleSheetsReporter


# 전역 변수
test_run_id = f"RUN_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
logger = get_test_logger()


@pytest.fixture(scope="session")
def config():
    """설정 fixture"""
    Config.ensure_directories()
    Config.print_config()
    return Config


@pytest.fixture(scope="session")
def test_data():
    """테스트 데이터 로드"""
    data_file = Config.get_test_data_path('test_data.json')

    if data_file.exists():
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            logger.info(f"Test data loaded from {data_file}")
            return data
    else:
        logger.warning(f"Test data file not found: {data_file}")
        # 기본 테스트 데이터 반환
        return {
            "valid_user": {
                "username": Config.TEST_USERNAME,
                "password": Config.TEST_PASSWORD
            },
            "base_url": Config.BASE_URL
        }


@pytest.fixture(scope="session")
def sheets_reporter():
    """Google Sheets 리포터 fixture (세션 범위)"""
    try:
        reporter = GoogleSheetsReporter(
            sheet_url=Config.GOOGLE_SHEET_URL,
            credentials_path=Config.GOOGLE_CREDENTIALS_PATH
        )
        logger.info("Google Sheets reporter initialized")
        return reporter
    except Exception as e:
        logger.warning(f"Failed to initialize Google Sheets reporter: {e}")
        return None


@pytest.fixture(scope="function")
def driver(config):
    """
    WebDriver fixture (함수 범위)
    각 테스트마다 새로운 브라우저 인스턴스 생성
    """
    logger.info(f"Initializing {config.BROWSER} browser...")

    driver_instance = None

    try:
        if config.BROWSER == "chrome":
            options = webdriver.ChromeOptions()

            # Headless 모드
            if config.HEADLESS:
                options.add_argument('--headless')
                options.add_argument('--disable-gpu')

            # 봇 감지 우회 옵션 (Akamai Bot Manager 대응)
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--start-maximized')

            # 추가 anti-detection 옵션
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)

            # Preferences 설정
            prefs = {
                "credentials_enable_service": False,
                "profile.password_manager_enabled": False
            }
            options.add_experimental_option("prefs", prefs)

            # User-Agent 설정 (최신 Chrome 버전)
            options.add_argument(
                'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/144.0.0.0 Safari/537.36'
            )

            service = ChromeService(ChromeDriverManager().install())
            driver_instance = webdriver.Chrome(service=service, options=options)

            # navigator.webdriver 속성 제거 (JavaScript 실행)
            driver_instance.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                '''
            })

        elif config.BROWSER == "edge":
            options = webdriver.EdgeOptions()

            if config.HEADLESS:
                options.add_argument('--headless')
                options.add_argument('--disable-gpu')

            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--start-maximized')

            service = EdgeService(EdgeChromiumDriverManager().install())
            driver_instance = webdriver.Edge(service=service, options=options)

        else:
            raise ValueError(f"Unsupported browser: {config.BROWSER}")

        # Timeouts 설정
        driver_instance.implicitly_wait(config.IMPLICIT_WAIT)
        driver_instance.set_page_load_timeout(config.PAGE_LOAD_TIMEOUT)

        logger.info(f"{config.BROWSER.capitalize()} browser initialized successfully")

        yield driver_instance

    finally:
        # 테스트 종료 후 브라우저 종료
        if driver_instance:
            driver_instance.quit()
            logger.info("Browser closed")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    테스트 실행 후 결과 처리
    실패 시 스크린샷 저장 및 Google Sheets 기록
    """
    outcome = yield
    report = outcome.get_result()

    # 테스트 실행 단계만 처리 (setup, teardown 제외)
    if report.when == "call":
        # 테스트 메타데이터 추출
        test_name = item.name
        test_file = item.location[0]

        # Marker에서 메타데이터 추출
        tc_id = item.get_closest_marker("tc_id")
        page = item.get_closest_marker("page")
        scenario = item.get_closest_marker("scenario")

        tc_id_value = tc_id.args[0] if tc_id else test_name
        page_value = page.args[0] if page else test_file
        scenario_value = scenario.args[0] if scenario else test_name

        # 테스트 결과
        result = "PASS" if report.passed else "FAIL"
        duration = report.duration
        error_msg = str(report.longrepr) if report.failed else ""

        # 스크린샷 저장 (실패 시)
        screenshot_path = ""
        if report.failed and Config.ENABLE_SCREENSHOTS:
            driver = item.funcargs.get('driver')
            if driver:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_filename = f"fail_{test_name}_{timestamp}.png"
                screenshot_path = os.path.join(Config.SCREENSHOT_PATH, screenshot_filename)

                os.makedirs(Config.SCREENSHOT_PATH, exist_ok=True)
                driver.save_screenshot(screenshot_path)
                logger.info(f"Screenshot saved: {screenshot_path}")

        # Google Sheets에 기록
        sheets_reporter = item.funcargs.get('sheets_reporter')
        if sheets_reporter:
            try:
                sheets_reporter.log_test_result(
                    tc_id=tc_id_value,
                    page=page_value,
                    scenario=scenario_value,
                    result=result,
                    browser=Config.BROWSER.capitalize(),
                    os_name="Windows" if os.name == 'nt' else "Linux",
                    duration=duration,
                    error_msg=error_msg[:500] if error_msg else "",  # 길이 제한
                    screenshot_url=screenshot_path,
                    test_run_id=test_run_id,
                    environment=Config.RUN_ENVIRONMENT
                )
                logger.info(f"Test result logged to Google Sheets: {tc_id_value} - {result}")
            except Exception as e:
                logger.error(f"Failed to log to Google Sheets: {e}")


def pytest_sessionfinish(session, exitstatus):
    """
    전체 테스트 세션 종료 후 실행
    Summary 및 Daily Trend 업데이트
    """
    logger.info("Test session finished")

    # Google Sheets Summary 업데이트
    try:
        reporter = GoogleSheetsReporter(
            sheet_url=Config.GOOGLE_SHEET_URL,
            credentials_path=Config.GOOGLE_CREDENTIALS_PATH
        )

        if reporter.sheet:
            reporter.update_summary()
            reporter.add_daily_trend()
            logger.info("Google Sheets summary and daily trend updated")
    except Exception as e:
        logger.error(f"Failed to update Google Sheets summary: {e}")


def pytest_configure(config):
    """pytest 설정 초기화"""
    # 커스텀 마커 등록
    config.addinivalue_line(
        "markers", "tc_id(id): Test Case ID marker"
    )
    config.addinivalue_line(
        "markers", "page(name): Page name marker"
    )
    config.addinivalue_line(
        "markers", "scenario(name): Scenario name marker"
    )


# Pytest 명령줄 옵션 추가
def pytest_addoption(parser):
    """커스텀 명령줄 옵션 추가"""
    parser.addoption(
        "--browser",
        action="store",
        default="chrome",
        help="Browser to use: chrome or edge"
    )
    parser.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="Run browser in headless mode"
    )
    parser.addoption(
        "--env",
        action="store",
        default="production",
        help="Test environment: production, staging, local"
    )
    # GS_PRODUCT_001 (test_category_urls.py) 옵션
    parser.addoption(
        "--max",
        action="store",
        default=None,
        type=int,
        help="Maximum number of categories to test (GS_PRODUCT_001)"
    )
    parser.addoption(
        "--level",
        action="store",
        default=None,
        type=int,
        help="Category level filter (1, 2, 3) for GS_PRODUCT_001"
    )


@pytest.fixture(scope="session", autouse=True)
def configure_from_cli(request):
    """CLI 옵션을 Config에 반영"""
    browser = request.config.getoption("--browser")
    headless = request.config.getoption("--headless")
    env = request.config.getoption("--env")

    if browser:
        Config.BROWSER = browser
    if headless:
        Config.HEADLESS = True
    if env:
        Config.RUN_ENVIRONMENT = env

    logger.info(f"CLI options applied: browser={Config.BROWSER}, headless={Config.HEADLESS}, env={Config.RUN_ENVIRONMENT}")

"""
Config - 설정 관리 모듈
환경 변수 및 설정 값 관리
"""
import os
from dotenv import load_dotenv
from pathlib import Path


# .env 파일 로드
load_dotenv()


class Config:
    """테스트 설정 관리"""

    # Google Sheets
    GOOGLE_SHEET_URL = os.getenv(
        'GOOGLE_SHEET_URL',
        'https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit'
    )
    GOOGLE_CREDENTIALS_PATH = os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials.json')

    # Test Environment
    BASE_URL = os.getenv('BASE_URL', 'https://biz.giftishow.com')
    HEADLESS = os.getenv('HEADLESS', 'false').lower() == 'true'
    BROWSER = os.getenv('BROWSER', 'chrome').lower()

    # Timeouts (seconds)
    IMPLICIT_WAIT = int(os.getenv('IMPLICIT_WAIT', '10'))
    EXPLICIT_WAIT = int(os.getenv('EXPLICIT_WAIT', '20'))
    PAGE_LOAD_TIMEOUT = int(os.getenv('PAGE_LOAD_TIMEOUT', '30'))

    # Test Data
    TEST_USERNAME = os.getenv('TEST_USERNAME', '')
    TEST_PASSWORD = os.getenv('TEST_PASSWORD', '')

    # Reporting
    ENABLE_SCREENSHOTS = os.getenv('ENABLE_SCREENSHOTS', 'true').lower() == 'true'
    SCREENSHOT_PATH = os.getenv('SCREENSHOT_PATH', 'reports/screenshots')
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()

    # Environment
    RUN_ENVIRONMENT = os.getenv('RUN_ENVIRONMENT', 'local')

    # Paths
    PROJECT_ROOT = Path(__file__).parent.parent
    DATA_DIR = PROJECT_ROOT / 'data'
    REPORTS_DIR = PROJECT_ROOT / 'reports'
    SCREENSHOTS_DIR = REPORTS_DIR / 'screenshots'
    LOGS_DIR = REPORTS_DIR / 'logs'

    @classmethod
    def ensure_directories(cls):
        """필요한 디렉토리 생성"""
        cls.SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
        cls.LOGS_DIR.mkdir(parents=True, exist_ok=True)
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)

    @classmethod
    def get_test_data_path(cls, filename: str) -> Path:
        """
        테스트 데이터 파일 경로 반환

        Args:
            filename: 파일명

        Returns:
            Path: 파일 절대 경로
        """
        return cls.DATA_DIR / filename

    @classmethod
    def print_config(cls):
        """현재 설정 출력 (디버깅용)"""
        print("=" * 50)
        print("Current Configuration")
        print("=" * 50)
        print(f"BASE_URL: {cls.BASE_URL}")
        print(f"BROWSER: {cls.BROWSER}")
        print(f"HEADLESS: {cls.HEADLESS}")
        print(f"IMPLICIT_WAIT: {cls.IMPLICIT_WAIT}s")
        print(f"EXPLICIT_WAIT: {cls.EXPLICIT_WAIT}s")
        print(f"LOG_LEVEL: {cls.LOG_LEVEL}")
        print(f"ENABLE_SCREENSHOTS: {cls.ENABLE_SCREENSHOTS}")
        print(f"RUN_ENVIRONMENT: {cls.RUN_ENVIRONMENT}")
        print(f"GOOGLE_SHEET_URL: {cls.GOOGLE_SHEET_URL[:50]}...")
        print("=" * 50)


# 앱 시작 시 디렉토리 생성
Config.ensure_directories()

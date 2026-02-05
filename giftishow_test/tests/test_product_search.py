"""
상품 검색 - 키워드 테스트 (GS_PRODUCT_002)

TestCase_Scenarios의 GS_PRODUCT_002 시나리오:
- Pre-condition: 로그인 완료, 상품 목록 또는 메인 페이지 접근
- Test Steps:
    1. 검색 아이콘 클릭
    2. 검색창에 키워드 입력 (예: 스타벅스)
    3. 검색 버튼 클릭
    4. 검색 결과 확인
    5. 검색 아이콘 클릭
    6. 검색창에 키워드 입력 (예: 생일)
    7. Enter 입력
    8. 검색 결과 확인
    9. 검색 아이콘 클릭
    10. 쿠폰 인기 검색어중 첫번째 항목 클릭
    11. 검색 결과 확인
    12. 검색 아이콘 클릭
    13. 판촉 인기 검색어 중 첫번째 항목 클릭
    14. 검색 결과 확인
    15. 검색 아이콘 클릭
    16. 검색창에 키워드 입력 (예: 가나다라마바사아자차카타파하)
    17. 검색 결과 확인
- Expected Result:
    - 키워드와 관련된 상품 목록 표시
    - 검색어 하이라이트 또는 표시
    - 결과 없을 시 '검색 결과가 없습니다' 메시지
    - 상품 상세 정보 표시: 상품명, 이미지, 가격

실행 방법:
- pytest: pytest tests/test_product_search.py -v
- 독립 실행: python -m tests.test_product_search --full-scenario --headless
"""
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from utils.google_sheets import GoogleSheetsReporter
from dotenv import load_dotenv
import os
import time
import logging
from datetime import datetime

# 환경 변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class _ProductSearchTester:
    """상품 검색 테스트 헬퍼 클래스 (내부용, GS_PRODUCT_002)"""

    # 테스트할 검색 키워드 목록
    DEFAULT_KEYWORDS = [
        "스타벅스",       # 인기 키워드
        "파리바게뜨",     # 인기 키워드
        "CU",            # 편의점
        "이마트",         # 대형마트
        "치킨",          # 음식 카테고리
        "커피",          # 음료 카테고리
        "아이스크림",     # 디저트
        "영화",          # 문화/레저
        "XYZNONEXIST123" # 존재하지 않는 키워드 (검색 결과 없음 테스트)
    ]

    # 기프티쇼 비즈 기본 URL (실제 운영 도메인)
    BASE_URL = "https://biz.giftishow.com"
    SEARCH_URL = "https://biz.giftishow.com/panchok/products/filtered?bigCateSeq=1"

    def __init__(self, headless=False, driver=None, sheets_reporter=None):
        """
        테스터 초기화

        Args:
            headless: 헤드리스 모드 여부 (독립 실행 시)
            driver: 외부에서 주입받은 WebDriver (pytest fixture)
            sheets_reporter: 외부에서 주입받은 GoogleSheetsReporter (pytest fixture)
        """
        self.driver = driver
        self.external_driver = driver is not None
        self.headless = headless
        self.sheets_reporter = sheets_reporter
        self.external_sheets = sheets_reporter is not None
        self.test_results = []
        self.test_run_id = f"SEARCH_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Google Sheets 연결 (외부 주입이 없는 경우만)
        if not self.external_sheets:
            sheet_url = os.getenv('GOOGLE_SHEET_URL')
            creds_path = os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials.json')

            if sheet_url:
                try:
                    self.sheets_reporter = GoogleSheetsReporter(sheet_url, creds_path)
                    logger.info("Google Sheets connected successfully")
                except Exception as e:
                    logger.warning(f"Failed to connect Google Sheets: {e}")

    def setup_driver(self):
        """WebDriver 설정 (외부 주입이 없는 경우만)"""
        if self.external_driver:
            logger.info("Using external WebDriver (pytest fixture)")
            return

        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_experimental_option(
            "prefs", {"profile.default_content_setting_values.notifications": 2}
        )

        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(10)
        logger.info("WebDriver initialized")

    def teardown_driver(self):
        """WebDriver 종료 (외부 주입이 없는 경우만)"""
        if self.external_driver:
            logger.info("Skipping driver teardown (external driver)")
            return

        if self.driver:
            self.driver.quit()
            logger.info("WebDriver closed")

    def navigate_to_search_page(self):
        """
        검색 가능한 페이지로 이동

        Returns:
            bool: 페이지 로딩 성공 여부
        """
        try:
            logger.info(f"Navigating to {self.SEARCH_URL}")
            self.driver.get(self.SEARCH_URL)
            time.sleep(3)

            # 페이지 로딩 확인
            wait = WebDriverWait(self.driver, 15)

            # 상품 이미지 또는 페이지 콘텐츠 확인
            try:
                wait.until(
                    EC.presence_of_element_located((
                        By.CSS_SELECTOR,
                        "img[alt$='이미지'], [class*='product']"
                    ))
                )
                logger.info("Search page loaded - product content found")
                return True
            except TimeoutException:
                pass

            # 검색 버튼 확인
            try:
                buttons = self.driver.find_elements(By.TAG_NAME, "button")
                for btn in buttons:
                    if "검색" in btn.text:
                        logger.info("Search page loaded - search button found")
                        return True
            except:
                pass

            # 페이지 제목으로 확인
            if "기프티쇼" in self.driver.title:
                logger.info("Search page loaded - title verified")
                return True

            logger.warning("Search elements not found on page")
            return False

        except Exception as e:
            logger.error(f"Failed to navigate to search page: {e}")
            return False

    def open_search_panel(self):
        """
        검색 패널 열기 (검색 버튼 클릭)

        Returns:
            bool: 검색 패널 열림 성공 여부
        """
        try:
            wait = WebDriverWait(self.driver, 10)

            # 검색 버튼을 항상 클릭하여 검색 패널 활성화
            # (검색 입력창이 DOM에 존재해도 클릭해야 패널이 활성화됨)
            try:
                buttons = self.driver.find_elements(By.TAG_NAME, "button")
                for btn in buttons:
                    if "검색" in btn.text and btn.is_displayed():
                        btn.click()
                        time.sleep(1)
                        logger.info("Clicked search button to activate panel")
                        break
            except Exception as e:
                logger.debug(f"Search button click failed: {e}")

            # 검색 입력창 확인
            try:
                search_input = wait.until(
                    EC.visibility_of_element_located((
                        By.CSS_SELECTOR,
                        "input[placeholder*='고민될 땐'], input[placeholder*='검색'], input[type='search']"
                    ))
                )
                if search_input.is_displayed():
                    logger.info("Search panel opened successfully")
                    return True
            except TimeoutException:
                pass

            # 대체 방법: CSS 셀렉터로 검색 트리거 찾기
            search_triggers = [
                "button[aria-label*='검색']",
                "[class*='search-btn']",
                "[class*='search-icon']",
            ]

            for selector in search_triggers:
                try:
                    trigger = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if trigger.is_displayed():
                        trigger.click()
                        time.sleep(1)

                        # 검색 입력창이 나타났는지 확인
                        search_input = wait.until(
                            EC.visibility_of_element_located((
                                By.CSS_SELECTOR,
                                "input[placeholder*='고민될 땐'], input[placeholder*='검색'], input[type='search']"
                            ))
                        )
                        logger.info("Search panel opened successfully")
                        return True
                except:
                    continue

            logger.warning("Could not open search panel")
            return False

        except Exception as e:
            logger.error(f"Failed to open search panel: {e}")
            return False

    def find_search_input(self):
        """
        검색 입력창 찾기

        Returns:
            WebElement: 검색 입력창 요소 또는 None
        """
        selectors = [
            "input[placeholder*='고민될 땐']",
            "input[placeholder*='검색']",
            "input[type='search']",
            "input[name='search']",
            "input[name='keyword']",
            "input[name='query']",
        ]

        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                if element.is_displayed():
                    return element
            except NoSuchElementException:
                continue

        return None

    def find_search_button(self):
        """
        검색 실행 버튼 찾기

        Returns:
            WebElement: 검색 버튼 요소 또는 None
        """
        try:
            # 검색 입력창 기준으로 인접한 버튼 찾기
            search_input = self.find_search_input()
            if search_input:
                # 형제 요소 중 버튼 찾기
                try:
                    # 다음 형제 버튼
                    button = search_input.find_element(
                        By.XPATH, "following-sibling::button | ../button | ../..//button"
                    )
                    if button.is_displayed():
                        return button
                except:
                    pass

            # 일반적인 검색 버튼 셀렉터
            button_selectors = [
                "button[type='submit']",
                "button[aria-label*='검색']",
                "button[class*='search']",
                "[class*='search-btn']",
            ]

            for selector in button_selectors:
                try:
                    button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if button.is_displayed():
                        return button
                except:
                    continue

        except Exception as e:
            logger.debug(f"Search button not found: {e}")

        return None

    def click_popular_keyword(self, keyword_type: str = "coupon"):
        """
        인기 검색어 클릭

        Args:
            keyword_type: "coupon" (쿠폰 인기 검색어) 또는 "panchok" (판촉 인기 검색어)

        Returns:
            tuple: (성공 여부, 클릭한 키워드명)
        """
        try:
            # 먼저 검색 버튼을 클릭하여 검색 패널 열기
            try:
                buttons = self.driver.find_elements(By.TAG_NAME, "button")
                for btn in buttons:
                    if "검색" in btn.text and btn.is_displayed():
                        btn.click()
                        logger.info("Clicked search button to open panel")
                        time.sleep(2)
                        break
            except Exception as e:
                logger.debug(f"Search button click failed: {e}")

            # 인기 검색어 섹션 찾기
            if keyword_type == "coupon":
                section_text = "쿠폰 인기 검색어"
                # 쿠폰 인기 검색어의 첫번째 항목: 파리바게뜨, 신세계, 이마트 등
                first_keywords = ["파리바게뜨", "신세계", "이마트"]
            else:
                section_text = "판촉 인기 검색어"
                # 판촉 인기 검색어의 첫번째 항목: 핫팩, 손난로, 에코백 등
                first_keywords = ["핫팩", "손난로", "에코백"]

            # 방법 1: 섹션 헤더 찾고 그 다음 링크 클릭
            try:
                section_header = self.driver.find_element(
                    By.XPATH, f"//*[contains(text(), '{section_text}')]"
                )
                logger.info(f"Found section header: {section_text}")

                # 섹션 헤더의 부모 요소에서 첫번째 링크 찾기
                parent = section_header.find_element(By.XPATH, "./..")
                links = parent.find_elements(By.TAG_NAME, "a")

                if links:
                    first_link = links[0]
                    keyword_name = first_link.text.strip()
                    first_link.click()
                    logger.info(f"Clicked popular keyword: {keyword_name}")
                    time.sleep(3)
                    return True, keyword_name
            except Exception as e:
                logger.debug(f"Method 1 failed: {e}")

            # 방법 2: following 형제 요소에서 링크 찾기
            try:
                first_keyword = self.driver.find_element(
                    By.XPATH,
                    f"//*[contains(text(), '{section_text}')]/following-sibling::*//a[1] | "
                    f"//*[contains(text(), '{section_text}')]/..//a[1]"
                )
                keyword_name = first_keyword.text.strip()
                first_keyword.click()
                logger.info(f"Clicked popular keyword (method 2): {keyword_name}")
                time.sleep(3)
                return True, keyword_name
            except Exception as e:
                logger.debug(f"Method 2 failed: {e}")

            # 방법 3: 알려진 첫번째 키워드로 직접 찾기
            for keyword in first_keywords:
                try:
                    keyword_link = self.driver.find_element(
                        By.XPATH, f"//a[contains(text(), '{keyword}')]"
                    )
                    if keyword_link.is_displayed():
                        keyword_link.click()
                        logger.info(f"Clicked popular keyword (direct): {keyword}")
                        time.sleep(3)
                        return True, keyword
                except:
                    continue

            # 방법 4: 모든 링크 중 인기 검색어 찾기
            try:
                all_links = self.driver.find_elements(By.TAG_NAME, "a")
                for link in all_links:
                    link_text = link.text.strip()
                    if link_text in first_keywords and link.is_displayed():
                        link.click()
                        logger.info(f"Clicked popular keyword (all links): {link_text}")
                        time.sleep(3)
                        return True, link_text
            except Exception as e:
                logger.debug(f"Method 4 failed: {e}")

            logger.error(f"Could not find {section_text} first keyword")
            return False, ""

        except Exception as e:
            logger.error(f"Failed to click popular keyword: {e}")
            return False, ""

    def execute_search(self, keyword: str, method: str = "enter"):
        """
        검색 실행

        Args:
            keyword: 검색 키워드
            method: 검색 방법 ("enter" 또는 "button")

        Returns:
            bool: 검색 실행 성공 여부
        """
        try:
            search_input = self.find_search_input()
            if not search_input:
                logger.error("Search input not found")
                return False

            # 입력창 클리어 및 키워드 입력
            search_input.clear()
            time.sleep(0.3)
            search_input.send_keys(keyword)
            time.sleep(0.5)
            logger.info(f"Entered keyword: {keyword}")

            # 검색 실행
            if method == "enter":
                search_input.send_keys(Keys.ENTER)
                logger.info("Search executed via Enter key")
            else:
                search_button = self.find_search_button()
                if search_button:
                    search_button.click()
                    logger.info("Search executed via button click")
                else:
                    # 버튼을 못 찾으면 Enter로 시도
                    search_input.send_keys(Keys.ENTER)
                    logger.info("Search executed via Enter key (button not found)")

            time.sleep(3)  # 검색 결과 로딩 대기
            return True

        except Exception as e:
            logger.error(f"Failed to execute search: {e}")
            return False

    def verify_search_results(self, keyword: str):
        """
        검색 결과 검증

        Args:
            keyword: 검색 키워드

        Returns:
            dict: 검증 결과
        """
        result = {
            'has_results': False,
            'result_count': 0,
            'keyword_displayed': False,
            'no_results_message': False,
            'url_contains_keyword': False,
            'error': ''
        }

        try:
            wait = WebDriverWait(self.driver, 10)

            # 1. URL에 검색어가 포함되어 있는지 확인
            current_url = self.driver.current_url
            if keyword in current_url or 'search' in current_url.lower():
                result['url_contains_keyword'] = True
                logger.info(f"URL contains search context: {current_url}")

            # 2. 검색 결과 상품 개수 확인
            product_count = self._count_search_results()
            result['result_count'] = product_count

            if product_count > 0:
                result['has_results'] = True
                logger.info(f"Found {product_count} search results")
            else:
                # 결과 없음 메시지 확인
                no_results_selectors = [
                    "//*[contains(text(), '검색 결과가 없습니다')]",
                    "//*[contains(text(), '결과가 없습니다')]",
                    "//*[contains(text(), '상품이 없습니다')]",
                    "//*[contains(text(), '검색결과가 없습니다')]",
                    "//*[contains(text(), '일치하는 상품이 없습니다')]",
                ]

                for selector in no_results_selectors:
                    try:
                        no_result_elem = self.driver.find_element(By.XPATH, selector)
                        if no_result_elem.is_displayed():
                            result['no_results_message'] = True
                            logger.info("No results message found")
                            break
                    except:
                        continue

            # 3. 검색어가 페이지에 표시되는지 확인
            try:
                # 검색어 하이라이트 또는 표시 확인
                keyword_display_selectors = [
                    f"//*[contains(text(), '{keyword}')]",
                    f"//mark[contains(text(), '{keyword}')]",
                    f"//*[@class='highlight'][contains(text(), '{keyword}')]",
                    f"//input[@value='{keyword}']",
                ]

                for selector in keyword_display_selectors:
                    try:
                        keyword_elem = self.driver.find_element(By.XPATH, selector)
                        if keyword_elem.is_displayed():
                            result['keyword_displayed'] = True
                            logger.info(f"Keyword '{keyword}' displayed on page")
                            break
                    except:
                        continue
            except:
                pass

            # 4. "검색결과 N개" 또는 "총 N개" 텍스트에서 결과 수 확인
            import re
            try:
                # 검색결과 N개 패턴 확인
                result_text = self.driver.find_element(
                    By.XPATH, "//*[contains(text(), '검색결과') and contains(text(), '개')]"
                )
                if result_text.is_displayed():
                    match = re.search(r'검색결과\s*(\d+)\s*개', result_text.text)
                    if match:
                        result['result_count'] = int(match.group(1))
                        result['has_results'] = result['result_count'] > 0
                        logger.info(f"Search result count from page: {result['result_count']}")
            except:
                pass

            # 총 N개 패턴 확인
            if result['result_count'] == 0:
                try:
                    total_text = self.driver.find_element(
                        By.XPATH, "//*[contains(text(), '총') and contains(text(), '개')]"
                    )
                    if total_text.is_displayed():
                        match = re.search(r'총\s*(\d+)\s*개', total_text.text)
                        if match:
                            result['result_count'] = int(match.group(1))
                            result['has_results'] = result['result_count'] > 0
                            logger.info(f"Total count from page: {result['result_count']}")
                except:
                    pass

        except Exception as e:
            result['error'] = str(e)
            logger.error(f"Failed to verify search results: {e}")

        return result

    def _count_search_results(self):
        """
        검색 결과 상품 개수 세기

        Returns:
            int: 상품 개수
        """
        try:
            # 기프티쇼 비즈: 상품 이미지로 카운트
            product_images = self.driver.find_elements(
                By.CSS_SELECTOR, "img[alt$='이미지']"
            )
            visible_count = len([img for img in product_images if img.is_displayed()])
            if visible_count > 0:
                return visible_count
        except:
            pass

        try:
            # 상품 카드/아이템으로 카운트
            product_items = self.driver.find_elements(
                By.CSS_SELECTOR, "[class*='product-item'], [class*='product-card'], article"
            )
            visible_count = len([item for item in product_items if item.is_displayed()])
            if visible_count > 0:
                return visible_count
        except:
            pass

        return 0

    def test_keyword_search(self, keyword: str, method: str = "enter"):
        """
        단일 키워드 검색 테스트

        Args:
            keyword: 검색 키워드
            method: 검색 방법

        Returns:
            dict: 테스트 결과
        """
        test_result = {
            'keyword': keyword,
            'method': method,
            'search_executed': False,
            'page_loaded': False,
            'has_results': False,
            'result_count': 0,
            'keyword_displayed': False,
            'no_results_message': False,
            'passed': False,
            'error': '',
            'duration': 0
        }

        start_time = time.time()

        try:
            logger.info(f"\n{'='*50}")
            logger.info(f"Testing keyword: '{keyword}' (method: {method})")
            logger.info('='*50)

            # 검색 페이지로 이동
            if not self.navigate_to_search_page():
                test_result['error'] = "Failed to navigate to search page"
                return test_result

            test_result['page_loaded'] = True

            # 검색 패널 열기
            if not self.open_search_panel():
                test_result['error'] = "Failed to open search panel"
                return test_result

            # 검색 실행
            if not self.execute_search(keyword, method):
                test_result['error'] = "Failed to execute search"
                return test_result

            test_result['search_executed'] = True

            # 검색 결과 검증
            verification = self.verify_search_results(keyword)
            test_result['has_results'] = verification['has_results']
            test_result['result_count'] = verification['result_count']
            test_result['keyword_displayed'] = verification['keyword_displayed']
            test_result['no_results_message'] = verification['no_results_message']

            if verification.get('error'):
                test_result['error'] = verification['error']

            # 테스트 Pass/Fail 판정
            # Pass 조건:
            # 1. 검색이 실행되고 (search_executed)
            # 2. 결과가 있으면 has_results=True 또는
            # 3. 결과가 없으면 no_results_message=True
            if test_result['search_executed']:
                if test_result['has_results'] and test_result['result_count'] > 0:
                    test_result['passed'] = True
                    logger.info(f"[PASS] Found {test_result['result_count']} results for '{keyword}'")
                elif test_result['no_results_message']:
                    test_result['passed'] = True
                    logger.info(f"[PASS] No results message shown for '{keyword}'")
                else:
                    test_result['error'] = "No results and no 'no results' message"
                    logger.warning(f"[FAIL] Unexpected state for '{keyword}'")

        except Exception as e:
            test_result['error'] = str(e)
            logger.error(f"[ERROR] Test failed for '{keyword}': {e}")

        test_result['duration'] = round(time.time() - start_time, 2)
        return test_result

    def test_popular_keyword_search(self, keyword_type: str):
        """
        인기 검색어 클릭 테스트

        Args:
            keyword_type: "coupon" (쿠폰 인기 검색어) 또는 "panchok" (판촉 인기 검색어)

        Returns:
            dict: 테스트 결과
        """
        type_name = "쿠폰 인기 검색어" if keyword_type == "coupon" else "판촉 인기 검색어"

        test_result = {
            'keyword': f"[{type_name}]",
            'method': 'popular_click',
            'search_executed': False,
            'page_loaded': False,
            'has_results': False,
            'result_count': 0,
            'keyword_displayed': False,
            'no_results_message': False,
            'passed': False,
            'error': '',
            'duration': 0
        }

        start_time = time.time()

        try:
            logger.info(f"\n{'='*50}")
            logger.info(f"Testing: {type_name} 첫번째 항목 클릭")
            logger.info('='*50)

            # 검색 페이지로 이동
            if not self.navigate_to_search_page():
                test_result['error'] = "Failed to navigate to search page"
                return test_result

            test_result['page_loaded'] = True

            # 인기 검색어 클릭
            success, clicked_keyword = self.click_popular_keyword(keyword_type)

            if not success:
                test_result['error'] = f"Failed to click {type_name}"
                return test_result

            test_result['keyword'] = f"[{type_name}] {clicked_keyword}"
            test_result['search_executed'] = True

            # 검색 결과 검증
            verification = self.verify_search_results(clicked_keyword)
            test_result['has_results'] = verification['has_results']
            test_result['result_count'] = verification['result_count']
            test_result['keyword_displayed'] = verification['keyword_displayed']
            test_result['no_results_message'] = verification['no_results_message']

            if verification.get('error'):
                test_result['error'] = verification['error']

            # 테스트 Pass/Fail 판정
            if test_result['search_executed']:
                if test_result['has_results'] and test_result['result_count'] > 0:
                    test_result['passed'] = True
                    logger.info(f"[PASS] Found {test_result['result_count']} results for '{clicked_keyword}'")
                elif test_result['no_results_message']:
                    test_result['passed'] = True
                    logger.info(f"[PASS] No results message shown for '{clicked_keyword}'")
                else:
                    test_result['error'] = "No results and no 'no results' message"
                    logger.warning(f"[FAIL] Unexpected state for '{clicked_keyword}'")

        except Exception as e:
            test_result['error'] = str(e)
            logger.error(f"[ERROR] Test failed for {type_name}: {e}")

        test_result['duration'] = round(time.time() - start_time, 2)
        return test_result

    def run_full_scenario_steps(self):
        """
        GS_PRODUCT_002 전체 시나리오 실행 (브라우저 관리 없이, pytest용)

        Test Steps:
        1-4: 스타벅스 + 버튼 클릭
        5-8: 생일 + Enter
        9-11: 쿠폰 인기 검색어 첫번째 클릭
        12-14: 판촉 인기 검색어 첫번째 클릭
        15-17: 가나다라마바사아자차카타파하 (결과 없음 예상)

        Returns:
            list: 테스트 결과 리스트
        """
        logger.info("\n" + "="*60)
        logger.info("GS_PRODUCT_002 Full Scenario Test (pytest mode)")
        logger.info("="*60)

        self.test_results = []

        # Step 1-4: 스타벅스 + 버튼 클릭
        logger.info("\n[Step 1-4] 키워드 '스타벅스' + 검색 버튼 클릭")
        result = self.test_keyword_search("스타벅스", method="button")
        result['step'] = "1-4"
        self.test_results.append(result)
        time.sleep(1)

        # Step 5-8: 생일 + Enter
        logger.info("\n[Step 5-8] 키워드 '생일' + Enter 입력")
        result = self.test_keyword_search("생일", method="enter")
        result['step'] = "5-8"
        self.test_results.append(result)
        time.sleep(1)

        # Step 9-11: 쿠폰 인기 검색어 첫번째 클릭
        logger.info("\n[Step 9-11] 쿠폰 인기 검색어 첫번째 항목 클릭")
        result = self.test_popular_keyword_search("coupon")
        result['step'] = "9-11"
        self.test_results.append(result)
        time.sleep(1)

        # Step 12-14: 판촉 인기 검색어 첫번째 클릭
        logger.info("\n[Step 12-14] 판촉 인기 검색어 첫번째 항목 클릭")
        result = self.test_popular_keyword_search("panchok")
        result['step'] = "12-14"
        self.test_results.append(result)
        time.sleep(1)

        # Step 15-17: 가나다라마바사아자차카타파하 (결과 없음 예상)
        logger.info("\n[Step 15-17] 키워드 '가나다라마바사아자차카타파하' (결과 없음 예상)")
        result = self.test_keyword_search("가나다라마바사아자차카타파하", method="enter")
        result['step'] = "15-17"
        self.test_results.append(result)

        # 결과 요약
        self._print_full_scenario_summary()

        # 시나리오 상태 업데이트
        self._update_scenario_status()

        # TestResults 시트에 결과 기록
        self._log_results_to_sheets()

        return self.test_results

    def run_full_scenario(self):
        """
        GS_PRODUCT_002 전체 시나리오 실행 (독립 실행용, 브라우저 관리 포함)

        Test Steps:
        1-4: 스타벅스 + 버튼 클릭
        5-8: 생일 + Enter
        9-11: 쿠폰 인기 검색어 첫번째 클릭
        12-14: 판촉 인기 검색어 첫번째 클릭
        15-17: 가나다라마바사아자차카타파하 (결과 없음 예상)

        Returns:
            list: 테스트 결과 리스트
        """
        # WebDriver 설정
        self.setup_driver()

        try:
            return self.run_full_scenario_steps()
        finally:
            self.teardown_driver()

    def _print_full_scenario_summary(self):
        """전체 시나리오 테스트 결과 요약 출력"""
        total = len(self.test_results)
        if total == 0:
            logger.info("No test results")
            return

        passed = sum(1 for r in self.test_results if r['passed'])
        failed = total - passed
        pass_rate = (passed / total * 100) if total > 0 else 0

        print("\n" + "=" * 70)
        print("GS_PRODUCT_002 Full Scenario Test Summary")
        print("=" * 70)
        print(f"Total Steps: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Pass Rate: {pass_rate:.1f}%")
        print("=" * 70)

        # 상세 결과
        print("\nDetailed Results by Step:")
        print("-" * 70)
        for r in self.test_results:
            step = r.get('step', 'N/A')
            status = "PASS" if r['passed'] else "FAIL"
            count_info = f"({r['result_count']} results)" if r['result_count'] > 0 else "(no results)"
            error_info = f" - {r['error']}" if r['error'] and not r['passed'] else ""
            print(f"  [Step {step}] [{status}] '{r['keyword']}' {count_info}{error_info}")

    def run_tests(self, keywords: list = None, method: str = "enter"):
        """
        여러 키워드 검색 테스트 실행

        Args:
            keywords: 검색할 키워드 목록 (None이면 기본 목록 사용)
            method: 검색 방법

        Returns:
            list: 테스트 결과 리스트
        """
        if keywords is None:
            keywords = self.DEFAULT_KEYWORDS

        logger.info(f"Starting search test for {len(keywords)} keywords...")

        # WebDriver 설정
        self.setup_driver()

        try:
            for idx, keyword in enumerate(keywords, 1):
                logger.info(f"\n[{idx}/{len(keywords)}] Testing keyword: '{keyword}'")

                result = self.test_keyword_search(keyword, method)
                self.test_results.append(result)

                # 간격 두기
                time.sleep(1)

        finally:
            self.teardown_driver()

        # 결과 요약
        self._print_summary()

        # 시나리오 상태 업데이트
        self._update_scenario_status()

        # TestResults 시트에 결과 기록
        self._log_results_to_sheets()

        return self.test_results

    def _print_summary(self):
        """테스트 결과 요약 출력"""
        total = len(self.test_results)
        if total == 0:
            logger.info("No test results")
            return

        passed = sum(1 for r in self.test_results if r['passed'])
        failed = total - passed
        pass_rate = (passed / total * 100) if total > 0 else 0

        print("\n" + "=" * 60)
        print("Product Search Test Summary (GS_PRODUCT_002)")
        print("=" * 60)
        print(f"Total Keywords: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Pass Rate: {pass_rate:.1f}%")
        print("=" * 60)

        # 상세 결과
        print("\nDetailed Results:")
        print("-" * 60)
        for r in self.test_results:
            status = "PASS" if r['passed'] else "FAIL"
            count_info = f"({r['result_count']} results)" if r['result_count'] > 0 else "(no results)"
            error_info = f" - {r['error']}" if r['error'] and not r['passed'] else ""
            print(f"  [{status}] '{r['keyword']}' {count_info} {error_info}")

        # 실패 목록
        failures = [r for r in self.test_results if not r['passed']]
        if failures:
            print("\n" + "-" * 60)
            print("Failed Keywords:")
            for f in failures:
                print(f"  - '{f['keyword']}': {f['error']}")

    def _update_scenario_status(self):
        """
        테스트 완료 후 TestCase_Scenarios의 GS_PRODUCT_002 상태 업데이트
        """
        if not self.sheets_reporter:
            return

        try:
            # 전체 Pass 여부 확인
            total = len(self.test_results)
            passed = sum(1 for r in self.test_results if r['passed'])

            # 80% 이상 Pass면 Done으로 변경
            if total > 0 and (passed / total) >= 0.8:
                self.sheets_reporter.update_scenario_status("GS_PRODUCT_002", "Done")
                logger.info("Updated GS_PRODUCT_002 scenario status to 'Done'")
            else:
                # 부분 성공이면 In Progress 유지
                logger.info(f"GS_PRODUCT_002 status unchanged (Pass rate: {passed}/{total})")

        except Exception as e:
            logger.error(f"Failed to update scenario status: {e}")

    def _log_results_to_sheets(self):
        """
        테스트 결과를 TestResults 시트에 기록
        """
        if not self.sheets_reporter or not self.test_results:
            logger.warning("Cannot log results: No sheets reporter or no test results")
            return

        try:
            results_to_log = []
            for r in self.test_results:
                # 시나리오명 생성 (step 정보가 있으면 포함)
                step_info = f"Step {r.get('step', 'N/A')}: " if r.get('step') else ""
                scenario_name = f"{step_info}{r.get('keyword', 'N/A')}"

                results_to_log.append({
                    'tc_id': 'GS_PRODUCT_002',
                    'page': 'Search',
                    'scenario': scenario_name,
                    'result': 'PASS' if r['passed'] else 'FAIL',
                    'duration': r.get('duration', 0),
                    'error_msg': r.get('error', ''),
                    'test_run_id': self.test_run_id
                })

            # TestResults 시트에 여러 결과 기록
            self.sheets_reporter.log_multiple_results(results_to_log)
            logger.info(f"Logged {len(results_to_log)} test results to TestResults sheet")

        except Exception as e:
            logger.error(f"Failed to log results to TestResults sheet: {e}")


# =============================================================================
# pytest 호환 테스트 클래스
# =============================================================================

@pytest.mark.regression
class TestProductSearch:
    """GS_PRODUCT_002: 상품 검색 테스트 (pytest 호환)"""

    @pytest.mark.tc_id("GS_PRODUCT_002")
    @pytest.mark.page("Search")
    @pytest.mark.scenario("상품 검색 전체 시나리오 테스트")
    def test_full_scenario(self, driver, sheets_reporter):
        """
        GS_PRODUCT_002 전체 시나리오 테스트 (pytest 실행용)

        Test Steps:
        1-4: 스타벅스 + 버튼 클릭
        5-8: 생일 + Enter
        9-11: 쿠폰 인기 검색어 첫번째 클릭
        12-14: 판촉 인기 검색어 첫번째 클릭
        15-17: 가나다라마바사아자차카타파하 (결과 없음 예상)

        예: pytest tests/test_product_search.py -v
        """
        # 테스터 생성 (외부 driver, sheets_reporter 사용)
        tester = _ProductSearchTester(driver=driver, sheets_reporter=sheets_reporter)

        # 테스트 실행
        results = tester.run_full_scenario_steps()

        # 검증
        assert len(results) > 0, "테스트 결과가 없습니다"

        passed = sum(1 for r in results if r['passed'])
        pass_rate = passed / len(results) if len(results) > 0 else 0

        # 80% 이상 Pass 필요
        assert pass_rate >= 0.8, f"Pass rate {pass_rate:.1%} < 80% ({passed}/{len(results)})"

        logger.info(f"Product search test completed: {passed}/{len(results)} passed ({pass_rate:.1%})")


# =============================================================================
# 독립 실행 모드 (python -m tests.test_product_search)
# =============================================================================

def main():
    """메인 함수 (독립 실행용)"""
    import argparse

    parser = argparse.ArgumentParser(description='Product Search Test (GS_PRODUCT_002)')
    parser.add_argument('--keywords', nargs='+', default=None, help='Keywords to test')
    parser.add_argument('--method', choices=['enter', 'button'], default='enter',
                       help='Search method (enter or button)')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode')
    parser.add_argument('--full-scenario', action='store_true',
                       help='Run full GS_PRODUCT_002 test scenario (all Test Steps)')
    args = parser.parse_args()

    print("=" * 60)
    print("Product Search Test - GS_PRODUCT_002")
    print("=" * 60)

    tester = _ProductSearchTester(headless=args.headless)

    if args.full_scenario:
        # 전체 시나리오 실행 (Test Steps 순서대로)
        print("Running full scenario (Test Steps 1-17)...")
        results = tester.run_full_scenario()
        print(f"\nFull scenario completed. {len(results)} steps tested.")
    else:
        # 개별 키워드 테스트
        results = tester.run_tests(keywords=args.keywords, method=args.method)
        print(f"\nTest completed. {len(results)} keywords tested.")


if __name__ == "__main__":
    main()

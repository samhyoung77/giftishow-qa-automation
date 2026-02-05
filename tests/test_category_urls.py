"""
카테고리 URL 및 상품 상세 페이지 테스트 (GS_PRODUCT_001)

Google Sheets의 Menu_tree_check_list에서 URL을 가져와서:
1. 각 카테고리 페이지가 정상 로딩되는지 확인
2. 임의 상품 클릭 시 상세 페이지가 정상 표시되는지 확인
3. 테스트 결과를 Google Sheets에 기록

실행 방법:
- pytest: pytest tests/test_category_urls.py -v --max 5 --level 1
- 독립 실행: python -m tests.test_category_urls --max 5 --headless
"""
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from utils.google_sheets import GoogleSheetsReporter
from dotenv import load_dotenv
import os
import platform
import time
import logging
import random
from datetime import datetime

# 환경 변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class _CategoryURLTester:
    """카테고리 URL 및 상품 상세 페이지 테스트 헬퍼 클래스 (내부용)"""

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
        self.test_run_id = f"CAT_URL_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

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

    def get_categories_from_sheets(self):
        """
        Google Sheets에서 카테고리 목록 가져오기

        Returns:
            list: 카테고리 정보 리스트
        """
        if not self.sheets_reporter:
            logger.error("Google Sheets not connected")
            return []

        categories = self.sheets_reporter.get_menu_tree_categories()
        # URL이 있는 카테고리만 필터링
        valid_categories = [
            cat for cat in categories
            if cat.get('URL') and str(cat.get('URL')).startswith('http')
        ]
        logger.info(f"Found {len(valid_categories)} categories with valid URLs")
        return valid_categories

    def test_category_page(self, category):
        """
        카테고리 페이지 로딩 테스트

        Args:
            category: 카테고리 정보 딕셔너리

        Returns:
            dict: 테스트 결과
        """
        cat_name = category.get('Category_Name', 'Unknown')
        cat_url = category.get('URL', '')
        level = category.get('Level', 1)

        result = {
            'category_name': cat_name,
            'url': cat_url,
            'level': level,
            'page_load': False,
            'product_count': 0,
            'product_click': False,
            'detail_page': False,
            'error_msg': '',
            'duration': 0
        }

        start_time = time.time()

        try:
            # 1. 카테고리 페이지 로딩
            logger.info(f"Testing: [L{level}] {cat_name}")
            self.driver.get(cat_url)
            time.sleep(2)

            # 페이지 로딩 확인 - 상품 목록 또는 페이지 컨텐츠 확인
            wait = WebDriverWait(self.driver, 15)

            # 기프티쇼 비즈 페이지 로딩 확인
            # 1. 상품 이미지 확인 (alt 속성에 "이미지" 포함)
            # 2. breadcrumb 네비게이션 확인
            # 3. 총 N개 텍스트 확인
            page_loaded = False

            try:
                # 상품 이미지 확인
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "img[alt$='이미지']")))
                page_loaded = True
            except TimeoutException:
                pass

            # breadcrumb 또는 article 요소로 확인
            if not page_loaded:
                try:
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "nav[aria-label='Breadcrumb'], article")))
                    page_loaded = True
                except TimeoutException:
                    pass

            # 상품 개수 텍스트 확인 ("총 N개")
            if not page_loaded:
                try:
                    wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), '총') and contains(text(), '개')]")))
                    page_loaded = True
                except TimeoutException:
                    pass

            result['page_load'] = page_loaded

            if not page_loaded:
                result['error_msg'] = "Category page load failed"
                logger.warning(f"  [FAIL] Page load failed: {cat_name}")
                return result

            logger.info(f"  [OK] Page loaded: {cat_name}")

            # 2. 상품 개수 확인
            product_count = self._count_products()
            result['product_count'] = product_count
            logger.info(f"  [INFO] Product count: {product_count}")

            # 3. 상품 클릭 및 상세 페이지 테스트
            if product_count > 0:
                detail_result = self._test_product_detail()
                result['product_click'] = detail_result['clicked']
                result['detail_page'] = detail_result['detail_loaded']
                if detail_result.get('error'):
                    result['error_msg'] = detail_result['error']

        except Exception as e:
            result['error_msg'] = str(e)
            logger.error(f"  [ERROR] {cat_name}: {e}")

        result['duration'] = round(time.time() - start_time, 2)
        return result

    def _count_products(self):
        """
        현재 페이지의 상품 개수 세기

        Returns:
            int: 상품 개수
        """
        # 기프티쇼 비즈: 상품 이미지는 alt 속성에 "이미지"가 포함됨
        # 예: "리오3색터치 이미지", "파스텔라바초저점도 이미지"
        try:
            product_images = self.driver.find_elements(
                By.CSS_SELECTOR, "img[alt$='이미지']"
            )
            visible_images = [img for img in product_images if img.is_displayed()]
            if visible_images:
                return len(visible_images)
        except:
            pass

        # 대체 방법: 가격 요소로 카운트 (원 문자 포함)
        try:
            price_elements = self.driver.find_elements(
                By.XPATH, "//*[contains(text(), '원') and string-length(text()) < 20]"
            )
            # 가격 형식 필터링 (숫자+원)
            import re
            price_pattern = re.compile(r'[\d,]+원')
            price_count = 0
            for elem in price_elements:
                if elem.is_displayed() and price_pattern.match(elem.text.strip()):
                    price_count += 1
            if price_count > 0:
                return price_count // 2  # 정가와 할인가가 함께 표시되므로 2로 나눔
        except:
            pass

        return 0

    def _test_product_detail(self):
        """
        임의 상품 클릭하여 상세 페이지 테스트

        Returns:
            dict: 테스트 결과
        """
        result = {
            'clicked': False,
            'detail_loaded': False,
            'error': ''
        }

        try:
            # 기프티쇼 비즈: 상품 이미지 클릭 (alt 속성에 "이미지" 포함)
            # 예: "리오3색터치 이미지", "파스텔라바초저점도 이미지"
            product_images = self.driver.find_elements(
                By.CSS_SELECTOR, "img[alt$='이미지']"
            )
            visible_images = [img for img in product_images if img.is_displayed()]

            if not visible_images:
                result['error'] = "No product images found"
                logger.warning("    [WARN] No product images found")
                return result

            # 첫 번째 상품 이미지 선택
            selected_element = visible_images[0]
            product_name = selected_element.get_attribute("alt").replace(" 이미지", "")
            logger.info(f"    [INFO] Selected product: {product_name}")

            # 원래 URL 저장
            original_url = self.driver.current_url

            # 요소 클릭
            try:
                # 스크롤하여 요소가 보이도록
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", selected_element)
                time.sleep(0.5)

                selected_element.click()
                result['clicked'] = True
                logger.info("    [OK] Product clicked")
            except:
                # JavaScript 클릭 시도
                try:
                    self.driver.execute_script("arguments[0].click();", selected_element)
                    result['clicked'] = True
                    logger.info("    [OK] Product clicked (JS)")
                except Exception as click_err:
                    result['error'] = f"Click failed: {click_err}"
                    return result

            time.sleep(3)  # 페이지 로딩 대기

            # 상세 페이지 로딩 확인
            new_url = self.driver.current_url

            # 기프티쇼 비즈 상세 페이지 URL 패턴: /panchok/product/{id}
            if "/panchok/product/" in new_url:
                result['detail_loaded'] = True
                logger.info(f"    [OK] Detail page loaded (URL: {new_url})")
            elif new_url != original_url:
                # URL이 변경됨 - DOM 요소로 확인
                # 기프티쇼 비즈 상세 페이지 특징:
                # - heading (상품명)
                # - tablist (상품설명/상품리뷰/배송결제)
                # - 상품코드 텍스트
                detail_checks = [
                    # 상품코드 (G로 시작하는 코드)
                    ("xpath", "//*[contains(text(), '상품코드')]"),
                    # 탭 목록 (상품설명, 상품리뷰, 배송/결제)
                    ("css", "[role='tablist']"),
                    # 주문서 접수 버튼
                    ("xpath", "//*[contains(text(), '주문서 접수')]"),
                    # 장바구니 버튼
                    ("xpath", "//*[contains(text(), '장바구니')]"),
                    # 상세정보 헤딩
                    ("xpath", "//h2[contains(text(), '상세정보')] | //heading[contains(text(), '상세정보')]"),
                ]

                for check_type, selector in detail_checks:
                    try:
                        if check_type == "css":
                            element = self.driver.find_element(By.CSS_SELECTOR, selector)
                        else:
                            element = self.driver.find_element(By.XPATH, selector)
                        if element.is_displayed():
                            result['detail_loaded'] = True
                            logger.info(f"    [OK] Detail page verified (found: {selector[:30]})")
                            break
                    except:
                        continue

                # 페이지 타이틀로 확인 (상품명 | 기프티쇼 비즈)
                if not result['detail_loaded']:
                    page_title = self.driver.title
                    if page_title and "기프티쇼 비즈" in page_title and "|" in page_title:
                        result['detail_loaded'] = True
                        logger.info(f"    [OK] Detail page loaded (title: {page_title[:40]})")

                if not result['detail_loaded']:
                    result['error'] = "Detail page content not verified"
                    logger.warning("    [WARN] Detail page content not verified")

            else:
                result['error'] = "URL did not change after click"
                logger.warning("    [WARN] URL did not change after click")

            # 원래 페이지로 돌아가기
            if result['clicked']:
                self.driver.back()
                time.sleep(1.5)

        except Exception as e:
            result['error'] = str(e)
            logger.error(f"    [ERROR] Product detail test: {e}")

        return result

    def run_tests(self, max_categories=None, level_filter=None):
        """
        테스트 실행

        Args:
            max_categories: 테스트할 최대 카테고리 수 (None이면 전체)
            level_filter: 특정 레벨만 테스트 (1, 2, 3 또는 None)

        Returns:
            list: 테스트 결과 리스트
        """
        # 카테고리 목록 가져오기
        categories = self.get_categories_from_sheets()

        if not categories:
            logger.error("No categories found in Google Sheets")
            return []

        # 레벨 필터 (Google Sheets에서 가져온 Level은 문자열이므로 문자열 비교)
        if level_filter:
            categories = [c for c in categories if str(c.get('Level', '')) == str(level_filter)]
            logger.info(f"Filtered to Level {level_filter}: {len(categories)} categories")

        # 최대 개수 제한
        if max_categories:
            categories = categories[:max_categories]

        logger.info(f"Starting test for {len(categories)} categories...")

        # WebDriver 설정
        self.setup_driver()

        try:
            for idx, category in enumerate(categories, 1):
                logger.info(f"\n[{idx}/{len(categories)}] Testing category...")

                result = self.test_category_page(category)
                self.test_results.append(result)

                # Google Sheets에 결과 업데이트
                self._update_sheets_result(category, result)

                # 간격 두기 (서버 부하 방지)
                time.sleep(1)

        finally:
            self.teardown_driver()

        # 최종 요약
        self._print_summary()

        return self.test_results

    def _update_sheets_result(self, category, result):
        """
        Google Sheets에 테스트 결과 업데이트

        Args:
            category: 카테고리 정보
            result: 테스트 결과

        결과 기록:
            J열: Pass 또는 Fail
            K열: 실패 시 오류 메시지
        """
        if not self.sheets_reporter:
            return

        try:
            cat_name = category.get('Category_Name', '')

            # 종합 결과 판정 (페이지 로딩 + 상세페이지 모두 성공해야 Pass)
            if result['page_load'] and result['detail_page']:
                test_result = "Pass"
                error_msg = ""  # 성공 시 오류 메시지 없음
            else:
                test_result = "Fail"
                # 오류 메시지 생성
                errors = []
                if not result['page_load']:
                    errors.append("Page load failed")
                if result['product_count'] == 0:
                    errors.append("No products found")
                if not result['product_click']:
                    errors.append("Product click failed")
                if not result['detail_page']:
                    errors.append("Detail page not loaded")
                if result['error_msg']:
                    errors.append(result['error_msg'][:50])

                error_msg = "; ".join(errors) if errors else "Unknown error"

            # Sheets 업데이트 (J열: Pass/Fail, K열: Error Message)
            self.sheets_reporter.update_category_test_result(
                category_name=cat_name,
                result=test_result,
                product_count=result['product_count'],
                error_msg=error_msg
            )

        except Exception as e:
            logger.error(f"Failed to update sheets: {e}")

    def _print_summary(self):
        """테스트 결과 요약 출력"""
        total = len(self.test_results)
        if total == 0:
            logger.info("No test results")
            return

        page_pass = sum(1 for r in self.test_results if r['page_load'])
        detail_pass = sum(1 for r in self.test_results if r['detail_page'])
        full_pass = sum(1 for r in self.test_results if r['page_load'] and r['detail_page'])

        print("\n" + "=" * 60)
        print("Category URL Test Summary")
        print("=" * 60)
        print(f"Total Categories: {total}")
        print(f"Page Load Success: {page_pass}/{total} ({page_pass*100//total}%)")
        print(f"Detail Page Success: {detail_pass}/{total} ({detail_pass*100//total}%)")
        print(f"Full Pass: {full_pass}/{total} ({full_pass*100//total}%)")
        print("=" * 60)

        # 실패 목록
        failures = [r for r in self.test_results if not r['page_load'] or not r['detail_page']]
        if failures:
            print("\nFailed/Partial Categories:")
            for f in failures:
                status = "FAIL" if not f['page_load'] else "PARTIAL"
                print(f"  [{status}] {f['category_name']}: {f['error_msg']}")

        # TestResults 시트에 결과 기록
        self._log_results_to_sheets()

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
                # 종합 결과 판정 (페이지 로딩 + 상세페이지 모두 성공해야 Pass)
                is_pass = r['page_load'] and r['detail_page']

                # 시나리오명 생성: [Level] Category_Name
                scenario_name = f"[L{r.get('level', '?')}] {r.get('category_name', 'Unknown')}"

                # OS 감지
                os_name = "Windows" if os.name == 'nt' else ("macOS" if platform.system() == "Darwin" else "Linux")

                results_to_log.append({
                    'tc_id': 'GS_PRODUCT_001',
                    'page': 'Category',
                    'scenario': scenario_name,
                    'result': 'PASS' if is_pass else 'FAIL',
                    'duration': r.get('duration', 0),
                    'error_msg': r.get('error_msg', ''),
                    'test_run_id': self.test_run_id,
                    'os': os_name,
                    'browser': 'Chrome'
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
class TestCategoryURLs:
    """GS_PRODUCT_001: 카테고리 URL 테스트 (pytest 호환)"""

    @pytest.mark.tc_id("GS_PRODUCT_001")
    @pytest.mark.page("Category")
    @pytest.mark.scenario("카테고리 페이지 및 상품 상세 페이지 테스트")
    def test_category_urls(self, driver, sheets_reporter, request):
        """
        카테고리 URL 테스트 (pytest 실행용)

        CLI 옵션:
        - --max N: 최대 N개 카테고리만 테스트
        - --level N: 특정 레벨만 테스트 (1, 2, 3)

        예: pytest tests/test_category_urls.py -v --max 5 --level 1
        """
        # CLI 옵션 가져오기
        max_categories = request.config.getoption("--max", default=None)
        level_filter = request.config.getoption("--level", default=None)

        # 테스터 생성 (외부 driver, sheets_reporter 사용)
        tester = _CategoryURLTester(driver=driver, sheets_reporter=sheets_reporter)

        # 테스트 실행
        results = tester.run_tests(max_categories=max_categories, level_filter=level_filter)

        # 검증
        assert len(results) > 0, "테스트할 카테고리가 없습니다"

        passed = sum(1 for r in results if r['page_load'] and r['detail_page'])
        pass_rate = passed / len(results) if len(results) > 0 else 0

        # 80% 이상 Pass 필요
        assert pass_rate >= 0.8, f"Pass rate {pass_rate:.1%} < 80% ({passed}/{len(results)})"

        logger.info(f"Category URL test completed: {passed}/{len(results)} passed ({pass_rate:.1%})")


# =============================================================================
# 독립 실행 모드 (python -m tests.test_category_urls)
# =============================================================================

def main():
    """메인 함수 (독립 실행용)"""
    import argparse

    parser = argparse.ArgumentParser(description='Category URL Test (GS_PRODUCT_001)')
    parser.add_argument('--max', type=int, default=None, help='Max categories to test')
    parser.add_argument('--level', type=int, default=None, help='Filter by level (1, 2, 3)')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode')
    args = parser.parse_args()

    print("=" * 60)
    print("Category URL & Product Detail Page Test (GS_PRODUCT_001)")
    print("=" * 60)

    tester = _CategoryURLTester(headless=args.headless)
    results = tester.run_tests(max_categories=args.max, level_filter=args.level)

    print(f"\nTest completed. {len(results)} categories tested.")


if __name__ == "__main__":
    main()

"""
ProductPage - 상품 페이지 Page Object
GS_PRODUCT_001, GS_PRODUCT_002, GS_PRODUCT_003 시나리오 구현

Updated: 2026-02-04
- 카테고리 버튼 클릭 → 동적 팝업 메뉴 대응
- 실제 웹사이트 HTML 구조에 맞는 Locator로 수정
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from pages.base_page import BasePage
import time


class ProductPage(BasePage):
    """
    기프티쇼 비즈 상품 페이지

    Test Cases:
    - GS_PRODUCT_001: 상품 카테고리 조회
    - GS_PRODUCT_002: 상품 검색
    - GS_PRODUCT_003: 상품 상세 조회
    """

    # ==================== Locators ====================
    # 2026-02-04 업데이트: 실제 웹사이트 구조에 맞게 수정

    # 메인 페이지
    MAIN_URL = "https://biz.giftishow.com"

    # ==================== 카테고리 관련 (동적 팝업 메뉴) ====================
    # 카테고리 버튼 (클릭하면 팝업 메뉴 열림)
    CATEGORY_BUTTON = (By.XPATH, "//button[contains(., '카테고리')]")
    CATEGORY_BUTTON_ALT = (By.XPATH, "//button[.//text()[contains(., '카테고리')]]")

    # 카테고리 메뉴 아이템 (팝업 내부)
    CATEGORY_ITEMS = (By.CSS_SELECTOR, "listitem > link")
    CATEGORY_ITEMS_XPATH = (By.XPATH, "//listitem/link")

    # 모바일쿠폰/배송상품 탭
    MOBILE_COUPON_TAB = (By.XPATH, "//link[text()='모바일쿠폰']")
    DELIVERY_PRODUCT_TAB = (By.XPATH, "//link[text()='배송상품']")

    # 특정 카테고리 (자주 사용되는 것들)
    CATEGORY_TOP100 = (By.XPATH, "//*[contains(text(), '인기 TOP100')]")
    CATEGORY_NEW_BRAND = (By.XPATH, "//*[contains(text(), '신규 브랜드')]")
    CATEGORY_COFFEE = (By.XPATH, "//*[contains(text(), '커피/음료')]")

    # 브랜드 링크
    BRAND_STARBUCKS = (By.XPATH, "//link[text()='스타벅스']")
    BRAND_GS25 = (By.XPATH, "//link[text()='GS25']")

    # ==================== 상품 목록 ====================
    PRODUCT_LIST = (By.CSS_SELECTOR, ".product-list")
    PRODUCT_ITEMS = (By.CSS_SELECTOR, ".product-item")
    PRODUCT_CARD = (By.CSS_SELECTOR, ".product-card")
    # 대체 Locator (실제 구조에 따라)
    PRODUCT_ITEMS_ALT = (By.XPATH, "//*[contains(@class, 'goods')]")

    # ==================== 검색 ====================
    SEARCH_INPUT = (By.CSS_SELECTOR, "input[type='search']")
    SEARCH_INPUT_ALT = (By.CSS_SELECTOR, "input[placeholder*='검색']")
    SEARCH_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")

    # ==================== 상품 상세 ====================
    PRODUCT_TITLE = (By.CSS_SELECTOR, ".product-title")
    PRODUCT_PRICE = (By.CSS_SELECTOR, ".product-price")
    PRODUCT_IMAGE = (By.CSS_SELECTOR, ".product-image img")
    PRODUCT_DESCRIPTION = (By.CSS_SELECTOR, ".product-description")

    # ==================== URL ====================
    def __init__(self, driver, base_url=None):
        """
        ProductPage 초기화

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

        # 상품 페이지 URL
        self.product_url = f"{self.base_url}"  # 메인 페이지에서 시작

    # ==================== Navigation ====================
    def navigate_to_main(self):
        """
        메인 페이지로 이동

        Test Step:
        - GS_PRODUCT_001 Step 1: 메인 페이지 접속
        """
        self.navigate_to(self.base_url)
        self.wait_for_page_load()
        self.logger.info(f"Navigated to main page: {self.base_url}")

    def navigate_to_products(self):
        """
        상품 페이지로 이동
        """
        self.navigate_to(self.product_url)
        self.wait_for_page_load()
        self.logger.info(f"Navigated to product page: {self.product_url}")

    # ==================== Category Actions (동적 팝업 대응) ====================
    def open_category_menu(self, timeout=10):
        """
        카테고리 버튼을 클릭하여 팝업 메뉴 열기

        Args:
            timeout: 대기 시간 (초)

        Returns:
            bool: 성공 여부
        """
        try:
            wait = WebDriverWait(self.driver, timeout)

            # 카테고리 버튼 찾기 (여러 방법 시도)
            category_button = None
            button_locators = [
                self.CATEGORY_BUTTON,
                self.CATEGORY_BUTTON_ALT,
                (By.XPATH, "//button[contains(text(), '카테고리')]"),
                (By.XPATH, "//*[contains(text(), '카테고리') and (self::button or self::a)]"),
            ]

            for locator in button_locators:
                try:
                    category_button = wait.until(
                        EC.element_to_be_clickable(locator)
                    )
                    if category_button:
                        self.logger.info(f"Found category button with locator: {locator}")
                        break
                except:
                    continue

            if not category_button:
                self.logger.error("Category button not found")
                return False

            # 버튼 클릭
            category_button.click()
            self.logger.info("Category button clicked")

            # 팝업 메뉴 로드 대기 (애니메이션 고려)
            time.sleep(1)

            return True

        except Exception as e:
            self.logger.error(f"Failed to open category menu: {e}")
            return False

    def get_category_elements(self, timeout=10):
        """
        카테고리 요소 찾기 (동적 팝업 메뉴 내부)

        2026-02-04 Update: 실제 웹사이트 구조 기반
        - div.category-area 또는 div.category-menu-item.panchok-pannel
        - a.text-with-badge 클래스

        Returns:
            list: 카테고리 요소 리스트
        """
        try:
            wait = WebDriverWait(self.driver, timeout)

            # 실제 카테고리 메뉴 구조에 맞는 Locator (디버깅 결과 기반)
            locators = [
                # 최우선: text-with-badge 클래스를 가진 링크
                (By.CSS_SELECTOR, "a.text-with-badge"),
                # 카테고리 컨테이너 내부의 링크
                (By.CSS_SELECTOR, "div.category-area a"),
                (By.CSS_SELECTOR, "div.category-menu-item a"),
                (By.CSS_SELECTOR, "div.panchok-pannel a"),
                # 일반 카테고리 메뉴
                (By.CSS_SELECTOR, "div.comm-category-pannel a"),
                # 대체 방법
                (By.XPATH, "//div[@class='category-area']//a"),
                (By.XPATH, "//div[contains(@class, 'category-menu-item')]//a"),
            ]

            for locator in locators:
                try:
                    elements = self.driver.find_elements(*locator)
                    if elements and len(elements) > 0:
                        # 유효한 카테고리만 필터링 (네비게이션 링크 제외)
                        filtered = self._filter_category_elements(elements)
                        if filtered and len(filtered) > 0:
                            self.logger.info(f"Found {len(filtered)} category elements with locator: {locator}")
                            return filtered
                except:
                    continue

            self.logger.warning("No category elements found with any locator")
            return []

        except Exception as e:
            self.logger.error(f"Failed to get category elements: {e}")
            return []

    def _filter_category_elements(self, elements):
        """
        카테고리 요소 필터링 (네비게이션 링크 제외)

        2026-02-04 Update: 실제 웹사이트 구조 기반
        - text-with-badge 클래스 우선 허용
        - 판촉물 카테고리: 사무용품, 가방/의류, USB/디지털/가전 등

        Args:
            elements: 원본 요소 리스트

        Returns:
            list: 필터링된 카테고리 요소
        """
        # 제외할 텍스트 패턴 (네비게이션 링크)
        exclude_patterns = [
            "로그인", "회원가입", "마이페이지", "인증관리", "장바구니", "판촉견적함",
            "고객센터", "공지사항", "BLOG", "linkedin", "NAVER", "부가서비스",
            "혜택 받기 >", "기프티쇼 비즈", "TOP"
        ]

        # 허용할 카테고리 패턴 (판촉물 카테고리)
        allow_patterns = [
            "사무용품", "가방", "의류", "USB", "디지털", "가전", "가정", "생활용품",
            "텀블러", "주방용품", "식품", "건강", "레저", "차량", "상패", "트로피",
            "명패", "깃발", "B2B", "특가", "볼펜", "필기류", "점착메모", "포스트잇",
            "파일", "바인더", "다이어리", "수첩", "노트", "레이저", "포인터",
            "원목", "문구", "다색펜", "멀티펜"
        ]

        filtered = []
        for element in elements:
            try:
                text = element.text.strip()
                classes = element.get_attribute("class") or ""

                # 빈 텍스트 제외
                if not text:
                    continue

                # text-with-badge 클래스를 가진 요소는 무조건 포함
                if "text-with-badge" in classes:
                    filtered.append(element)
                    continue

                # 제외 패턴에 해당하면 스킵
                if any(pattern in text for pattern in exclude_patterns):
                    continue

                # 허용 패턴에 해당하면 포함
                if any(pattern in text for pattern in allow_patterns):
                    filtered.append(element)
                    continue

                # 카테고리 컨테이너 내부의 짧은 텍스트 (보통 실제 카테고리)
                if len(text) <= 30 and not any(c in text for c in ['[', ']', '>']):
                    # 부모 요소가 category 관련 클래스를 가지고 있는지 확인
                    try:
                        parent = element.find_element(By.XPATH, "..")
                        parent_class = parent.get_attribute("class") or ""
                        if "category" in parent_class.lower() or "menu" in parent_class.lower():
                            filtered.append(element)
                    except:
                        pass

            except:
                continue

        return filtered

    def get_all_categories(self):
        """
        모든 카테고리 조회 (팝업 메뉴 열기 → 목록 추출)

        Returns:
            list: 카테고리 이름 리스트

        Test Step:
        - GS_PRODUCT_001 Step 2: 카테고리 목록 확인
        """
        try:
            # 1단계: 카테고리 메뉴 열기
            if not self.open_category_menu():
                self.logger.error("Failed to open category menu")
                return []

            # 2단계: 카테고리 요소 찾기
            elements = self.get_category_elements()

            # 3단계: 카테고리 텍스트 추출
            categories = []
            for element in elements:
                try:
                    category_name = element.text.strip()
                    if category_name and len(category_name) > 0:
                        categories.append(category_name)
                except Exception as e:
                    self.logger.debug(f"Failed to get text from element: {e}")
                    continue

            # 중복 제거
            categories = list(dict.fromkeys(categories))

            self.logger.info(f"Found {len(categories)} categories: {categories[:10]}...")  # 처음 10개만 로그
            return categories

        except Exception as e:
            self.logger.error(f"Failed to get categories: {e}")
            return []

    def get_all_categories_with_urls(self, collect_urls_by_click=False):
        """
        모든 카테고리 조회 (이름 + URL 포함)

        2026-02-04 신규 추가: GS_PRODUCT_001에서 URL 수집, GS_PRODUCT_003에서 활용

        Args:
            collect_urls_by_click: True면 각 카테고리를 클릭하여 URL 수집 (시간 소요)
                                   False면 href 속성만 사용 (빠름, URL 없을 수 있음)

        Returns:
            list[dict]: 카테고리 정보 리스트
                - name: 카테고리 이름
                - url: 카테고리 URL
                - element: 카테고리 요소 (선택적 사용)

        Test Step:
        - GS_PRODUCT_001 Step 2: 카테고리 목록 및 URL 확인
        """
        try:
            # 1단계: 카테고리 메뉴 열기
            if not self.open_category_menu():
                self.logger.error("Failed to open category menu")
                return []

            # 2단계: 카테고리 요소 찾기
            elements = self.get_category_elements()

            # 3단계: 카테고리 이름 + URL 추출
            categories = []
            seen_names = set()

            for element in elements:
                try:
                    category_name = element.text.strip()
                    category_url = element.get_attribute("href") or ""

                    if category_name and len(category_name) > 0 and category_name not in seen_names:
                        seen_names.add(category_name)
                        categories.append({
                            "name": category_name,
                            "url": category_url,
                        })
                except Exception as e:
                    self.logger.debug(f"Failed to get category info: {e}")
                    continue

            self.logger.info(f"Found {len(categories)} categories with URLs")
            for cat in categories[:5]:
                self.logger.info(f"  - {cat['name']}: {cat['url'][:60]}..." if cat['url'] else f"  - {cat['name']}: (no URL)")

            # URL이 없는 카테고리가 있고, collect_urls_by_click=True면 클릭하여 URL 수집
            if collect_urls_by_click:
                categories = self._collect_category_urls_by_clicking(categories)

            return categories

        except Exception as e:
            self.logger.error(f"Failed to get categories with URLs: {e}")
            return []

    def _collect_category_urls_by_clicking(self, categories):
        """
        각 카테고리를 클릭하여 실제 URL 수집

        JavaScript로 동작하는 카테고리 메뉴의 경우, href 속성이 비어있어서
        실제로 클릭한 후 URL을 캡처해야 합니다.

        Args:
            categories: 기존 카테고리 리스트 (name, url)

        Returns:
            list[dict]: URL이 업데이트된 카테고리 리스트
        """
        self.logger.info("Collecting category URLs by clicking each category...")
        original_url = self.get_current_url()
        updated_categories = []

        for idx, cat in enumerate(categories):
            cat_name = cat["name"]
            cat_url = cat.get("url", "")

            # 이미 URL이 있으면 스킵
            if cat_url and cat_url.startswith("http"):
                updated_categories.append(cat)
                continue

            try:
                # 1. 카테고리 메뉴 다시 열기
                if not self.open_category_menu():
                    self.logger.warning(f"Failed to open menu for '{cat_name}'")
                    updated_categories.append(cat)
                    continue

                time.sleep(0.5)

                # 2. 해당 카테고리 찾기 및 클릭
                # 슬래시(/)가 포함된 카테고리는 첫 번째 단어만 사용
                search_name = cat_name.split('/')[0].strip() if '/' in cat_name else cat_name
                wait = WebDriverWait(self.driver, 5)
                locators = [
                    (By.XPATH, f"//a[contains(@class, 'text-with-badge') and contains(text(), '{search_name}')]"),
                    (By.XPATH, f"//a[contains(text(), '{search_name}')]"),
                    (By.PARTIAL_LINK_TEXT, search_name),
                ]

                clicked = False
                for locator in locators:
                    try:
                        element = wait.until(EC.element_to_be_clickable(locator))
                        if element:
                            element.click()
                            clicked = True
                            break
                    except:
                        continue

                if not clicked:
                    self.logger.warning(f"Could not click category '{cat_name}'")
                    updated_categories.append(cat)
                    continue

                # 3. 페이지 로드 대기 및 URL 캡처
                time.sleep(2)
                new_url = self.get_current_url()

                if new_url != original_url:
                    cat["url"] = new_url
                    self.logger.info(f"[{idx+1}/{len(categories)}] {cat_name}: {new_url}")
                else:
                    self.logger.warning(f"[{idx+1}/{len(categories)}] {cat_name}: URL unchanged")

                updated_categories.append(cat)

                # 4. 메인 페이지로 돌아가기
                self.navigate_to(original_url)
                time.sleep(1)

            except Exception as e:
                self.logger.error(f"Error collecting URL for '{cat_name}': {e}")
                updated_categories.append(cat)
                # 오류 시 메인 페이지로 복구
                try:
                    self.navigate_to(original_url)
                    time.sleep(1)
                except:
                    pass

        self.logger.info(f"URL collection complete: {len([c for c in updated_categories if c.get('url')])} categories with URLs")
        return updated_categories

    def navigate_to_category_by_url(self, category_url):
        """
        URL을 사용하여 카테고리 페이지로 직접 이동

        Args:
            category_url: 카테고리 페이지 URL

        Returns:
            bool: 성공 여부
        """
        try:
            if not category_url:
                self.logger.error("Category URL is empty")
                return False

            self.navigate_to(category_url)
            time.sleep(3)  # 페이지 로딩 대기
            self.wait_for_page_load()

            current_url = self.get_current_url()
            self.logger.info(f"Navigated to category URL: {current_url}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to navigate to category URL: {e}")
            return False

    def get_first_product_from_current_page(self):
        """
        현재 카테고리 페이지에서 첫 번째 상품 상세 페이지 접근
        (카테고리 URL로 직접 접속한 후 사용)

        Returns:
            dict: 결과 정보
        """
        result = {
            "product_clicked": False,
            "detail_page_verified": False,
            "product_info": {},
            "error": ""
        }

        try:
            # 페이지 로딩 대기
            time.sleep(3)
            self.wait_for_page_load()

            # 상품 클릭
            product_result = self.click_first_product()
            result["product_clicked"] = product_result["success"]
            result["product_info"] = product_result

            if not product_result["success"]:
                result["error"] = product_result.get("error", "Failed to click product")
                return result

            # 상세 페이지 검증
            detail_result = self.verify_product_detail_page()
            result["detail_page_verified"] = detail_result["is_detail_page"]
            result["detail_verification"] = detail_result

            return result

        except Exception as e:
            result["error"] = str(e)
            self.logger.error(f"Failed to get first product: {e}")
            return result

    def click_category(self, category_name):
        """
        특정 카테고리 클릭 (팝업 메뉴 열기 → 카테고리 클릭)

        Args:
            category_name: 카테고리 이름

        Test Step:
        - GS_PRODUCT_001 Step 3: 카테고리 클릭
        """
        try:
            # 1단계: 카테고리 메뉴 열기
            if not self.open_category_menu():
                self.logger.error("Failed to open category menu")
                return False

            # 2단계: 특정 카테고리 찾기 (텍스트 기반)
            wait = WebDriverWait(self.driver, 10)

            # 다양한 방법으로 카테고리 찾기
            category_locators = [
                (By.XPATH, f"//link[text()='{category_name}']"),
                (By.XPATH, f"//*[text()='{category_name}']"),
                (By.XPATH, f"//a[contains(text(), '{category_name}')]"),
                (By.XPATH, f"//*[contains(text(), '{category_name}')]"),
                (By.LINK_TEXT, category_name),
                (By.PARTIAL_LINK_TEXT, category_name),
            ]

            category_element = None
            for locator in category_locators:
                try:
                    category_element = wait.until(
                        EC.element_to_be_clickable(locator)
                    )
                    if category_element:
                        self.logger.info(f"Found category '{category_name}' with locator: {locator}")
                        break
                except:
                    continue

            if not category_element:
                self.logger.warning(f"Category '{category_name}' not found")
                return False

            # 3단계: 카테고리 클릭
            category_element.click()
            self.logger.info(f"Clicked category: {category_name}")

            # 페이지 로드 대기
            time.sleep(2)

            return True

        except Exception as e:
            self.logger.error(f"Failed to click category '{category_name}': {e}")
            return False

    def click_category_by_text(self, category_text):
        """
        텍스트를 포함하는 카테고리 클릭 (부분 일치)

        2026-02-04 Update: 실제 웹사이트 구조 기반
        - text-with-badge 클래스 링크 우선 검색

        Args:
            category_text: 카테고리 텍스트 (부분 일치)

        Returns:
            bool: 성공 여부
        """
        try:
            # 카테고리 메뉴 열기
            if not self.open_category_menu():
                return False

            time.sleep(1)  # 팝업 애니메이션 대기

            # 부분 일치로 카테고리 찾기 (여러 방법 시도)
            wait = WebDriverWait(self.driver, 10)

            locators = [
                # text-with-badge 클래스 우선
                (By.XPATH, f"//a[contains(@class, 'text-with-badge') and contains(text(), '{category_text}')]"),
                # 카테고리 영역 내부
                (By.XPATH, f"//div[@class='category-area']//a[contains(text(), '{category_text}')]"),
                (By.XPATH, f"//div[contains(@class, 'category-menu-item')]//a[contains(text(), '{category_text}')]"),
                # 일반 검색
                (By.XPATH, f"//a[contains(text(), '{category_text}')]"),
                (By.PARTIAL_LINK_TEXT, category_text),
            ]

            category_element = None
            for locator in locators:
                try:
                    category_element = wait.until(EC.element_to_be_clickable(locator))
                    if category_element:
                        self.logger.info(f"Found category with text '{category_text}' using locator: {locator}")
                        break
                except:
                    continue

            if not category_element:
                self.logger.error(f"Category containing '{category_text}' not found")
                return False

            # 클릭 (JavaScript 클릭 시도)
            try:
                category_element.click()
            except:
                # 일반 클릭이 안 되면 JavaScript 클릭
                self.driver.execute_script("arguments[0].click();", category_element)

            self.logger.info(f"Clicked category containing: {category_text}")
            time.sleep(3)  # 페이지 로딩 대기

            return True

        except Exception as e:
            self.logger.error(f"Failed to click category containing '{category_text}': {e}")
            return False

    # ==================== Product Actions ====================
    def get_product_elements(self):
        """
        상품 요소 찾기 (여러 Locator 시도)

        Returns:
            list: 상품 요소 리스트
        """
        locators = [
            (By.CSS_SELECTOR, ".product-item"),
            (By.CSS_SELECTOR, ".product-card"),
            (By.CSS_SELECTOR, "[class*='product']"),
            (By.XPATH, "//*[contains(@class, 'product')]"),
        ]

        for locator in locators:
            try:
                elements = self.driver.find_elements(*locator)
                if elements and len(elements) > 0:
                    self.logger.info(f"Found {len(elements)} product elements with locator: {locator}")
                    return elements
            except Exception as e:
                self.logger.debug(f"Locator {locator} failed: {e}")
                continue

        self.logger.warning("No product elements found with any locator")
        return []

    def get_product_count(self):
        """
        표시된 상품 개수 조회

        Returns:
            int: 상품 개수

        Test Step:
        - GS_PRODUCT_001 Step 4: 상품 목록 확인
        """
        try:
            products = self.get_product_elements()
            count = len(products)
            self.logger.info(f"Found {count} products on page")
            return count

        except Exception as e:
            self.logger.error(f"Failed to get product count: {e}")
            return 0

    # ==================== Search Actions ====================
    def search_product(self, keyword):
        """
        상품 검색

        Args:
            keyword: 검색 키워드

        Test Step:
        - GS_PRODUCT_002: 상품 검색
        """
        try:
            # 검색창 찾기 (여러 Locator 시도)
            search_locators = [
                (By.CSS_SELECTOR, "input[type='search']"),
                (By.CSS_SELECTOR, "input[placeholder*='검색']"),
                (By.CSS_SELECTOR, "input[name='search']"),
                (By.XPATH, "//input[@type='search']"),
            ]

            search_input = None
            for locator in search_locators:
                try:
                    search_input = self.driver.find_element(*locator)
                    if search_input:
                        break
                except:
                    continue

            if not search_input:
                self.logger.error("Search input not found")
                return False

            # 검색어 입력
            search_input.clear()
            search_input.send_keys(keyword)
            self.logger.info(f"Entered search keyword: {keyword}")

            # 검색 버튼 클릭 또는 Enter
            try:
                search_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                search_button.click()
            except:
                # 버튼이 없으면 Enter 키
                from selenium.webdriver.common.keys import Keys
                search_input.send_keys(Keys.RETURN)

            time.sleep(2)
            self.logger.info(f"Search executed for: {keyword}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to search: {e}")
            return False

    # ==================== Verification ====================
    def is_on_product_page(self):
        """
        현재 상품 페이지에 있는지 확인

        Returns:
            bool: 상품 페이지면 True
        """
        current_url = self.get_current_url()
        is_product_page = (
            "product" in current_url.lower() or
            "category" in current_url.lower() or
            current_url == self.base_url
        )

        if is_product_page:
            self.logger.info(f"On product page: {current_url}")
        else:
            self.logger.info(f"Not on product page. Current URL: {current_url}")

        return is_product_page

    def has_products_displayed(self):
        """
        상품이 표시되어 있는지 확인

        Returns:
            bool: 상품이 있으면 True
        """
        product_count = self.get_product_count()
        return product_count > 0

    # ==================== Product Detail Actions (GS_PRODUCT_003) ====================
    def get_clickable_product_items(self, timeout=10):
        """
        클릭 가능한 상품 아이템 조회 (상품 상세 페이지 이동용)

        2026-02-04 Update: 실제 웹사이트 HTML 구조 기반
        - 판촉물 페이지: div.product-wrapper (JavaScript 클릭 이벤트 사용)
        - 모바일쿠폰 페이지: a[href*='/ggoods/detail?goodsNo=']

        Returns:
            list: 클릭 가능한 상품 요소 리스트
        """
        try:
            wait = WebDriverWait(self.driver, timeout)

            # 실제 상품 카드/아이템 Locator (클릭하면 상세 페이지로 이동)
            # 2026-02-04: 페이지 소스 분석 결과 기반
            locators = [
                # ============ 판촉물 페이지 전용 (JavaScript 클릭) ============
                # 최우선: div.product-wrapper (상품 카드 컨테이너)
                (By.CSS_SELECTOR, "div.product-wrapper"),
                (By.CSS_SELECTOR, ".product-wrapper"),
                # 상품 이미지 클릭 (product-image-wrap 또는 product-image)
                (By.CSS_SELECTOR, "div.product-image-wrap"),
                (By.CSS_SELECTOR, ".product-image-wrap"),
                (By.CSS_SELECTOR, "img.product-image"),
                # products-section 내부의 상품 요소
                (By.CSS_SELECTOR, ".products-section .product-wrapper"),
                (By.CSS_SELECTOR, ".products-section div.product-wrapper"),
                # ============ 모바일쿠폰 페이지 전용 (a 태그) ============
                (By.CSS_SELECTOR, "a[href*='/ggoods/detail?goodsNo=']"),
                (By.CSS_SELECTOR, "a[href*='/ggoods/detail']"),
                (By.XPATH, "//a[contains(@href, '/ggoods/detail?goodsNo=')]"),
                (By.XPATH, "//a[contains(@href, '/ggoods/detail')]"),
                # ============ 일반적인 상품 링크 패턴 (백업) ============
                (By.CSS_SELECTOR, "a[href*='/goods/detail']"),
                (By.CSS_SELECTOR, "a[href*='/product/detail']"),
                (By.CSS_SELECTOR, "a[href*='goodsNo=']"),
                # 상품 카드 클래스 패턴
                (By.CSS_SELECTOR, "[class*='goods-card']"),
                (By.CSS_SELECTOR, "[class*='product-card']"),
                (By.CSS_SELECTOR, "[class*='item-card']"),
            ]

            for locator in locators:
                try:
                    # WebDriverWait로 요소가 나타날 때까지 대기
                    wait.until(EC.presence_of_element_located(locator))
                    elements = self.driver.find_elements(*locator)
                    # 유효한 상품 요소만 필터링 (표시되고 있는 것)
                    valid_elements = [
                        el for el in elements
                        if el.is_displayed()
                    ]
                    if valid_elements and len(valid_elements) > 0:
                        self.logger.info(f"Found {len(valid_elements)} clickable products with locator: {locator}")
                        return valid_elements
                except TimeoutException:
                    self.logger.debug(f"Timeout waiting for locator: {locator}")
                    continue
                except Exception as e:
                    self.logger.debug(f"Error with locator {locator}: {e}")
                    continue

            # 디버깅: 페이지의 모든 링크에서 상품 관련 href 패턴 로깅
            self._debug_log_page_links()
            self.logger.warning("No clickable product items found")
            return []

        except Exception as e:
            self.logger.error(f"Failed to get clickable products: {e}")
            return []

    def _debug_log_page_links(self):
        """디버깅용: 페이지의 모든 링크 href 패턴 및 클릭 가능 요소 로깅"""
        try:
            all_links = self.driver.find_elements(By.TAG_NAME, "a")
            href_patterns = set()
            all_hrefs = []
            for link in all_links[:100]:  # 처음 100개 확인
                try:
                    href = link.get_attribute("href")
                    if href:
                        all_hrefs.append(href)
                        if ("goods" in href.lower() or "detail" in href.lower() or
                            "product" in href.lower() or "panchok" in href.lower()):
                            # URL에서 goodsNo 등 숫자 부분 제거하여 패턴 추출
                            import re
                            pattern = re.sub(r'\d+', '{N}', href)
                            href_patterns.add(pattern)
                except:
                    continue
            if href_patterns:
                self.logger.info(f"[DEBUG] Product-related href patterns on page: {list(href_patterns)[:15]}")
            else:
                self.logger.info("[DEBUG] No product-related href patterns found")
            # 모든 링크에서 panchok 포함된 것들만 출력
            panchok_hrefs = [h for h in all_hrefs if "panchok" in h.lower()]
            if panchok_hrefs:
                self.logger.info(f"[DEBUG] Panchok hrefs found: {panchok_hrefs[:10]}")

            # 클릭 가능한 요소 클래스 확인
            clickable_elements = self.driver.find_elements(By.XPATH, "//*[contains(@class, 'goods') or contains(@class, 'product') or contains(@class, 'item')]")
            classes_found = set()
            for el in clickable_elements[:50]:
                try:
                    class_attr = el.get_attribute("class")
                    if class_attr:
                        classes_found.add(class_attr[:50])  # 처음 50자만
                except:
                    continue
            if classes_found:
                self.logger.info(f"[DEBUG] Element classes with goods/product/item: {list(classes_found)[:10]}")
        except Exception as e:
            self.logger.debug(f"Debug logging failed: {e}")

    def save_page_source_for_analysis(self, filename="page_source_debug.html"):
        """
        페이지 소스를 파일로 저장하여 분석용

        Args:
            filename: 저장할 파일명

        Returns:
            str: 저장된 파일 경로
        """
        try:
            import os
            # 스크린샷 폴더에 저장
            save_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "screenshots")
            os.makedirs(save_dir, exist_ok=True)
            filepath = os.path.join(save_dir, filename)

            page_source = self.driver.page_source
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(page_source)

            self.logger.info(f"Page source saved to: {filepath}")
            return filepath
        except Exception as e:
            self.logger.error(f"Failed to save page source: {e}")
            return ""

    def analyze_clickable_elements(self):
        """
        클릭 가능한 상품 요소 분석 (onclick 이벤트 포함)

        Returns:
            dict: 분석 결과
        """
        result = {
            "onclick_elements": [],
            "data_attributes": [],
            "card_elements": [],
            "img_with_parent_link": []
        }

        try:
            # 1. onclick 속성을 가진 요소 찾기
            onclick_elements = self.driver.find_elements(By.XPATH, "//*[@onclick and (contains(@onclick, 'goods') or contains(@onclick, 'detail') or contains(@onclick, 'product'))]")
            for el in onclick_elements[:10]:
                try:
                    onclick = el.get_attribute("onclick")
                    tag = el.tag_name
                    class_attr = el.get_attribute("class") or ""
                    result["onclick_elements"].append({
                        "tag": tag,
                        "class": class_attr[:50],
                        "onclick": onclick[:100] if onclick else ""
                    })
                except:
                    continue

            # 2. data-* 속성에 goods/product 정보가 있는 요소
            data_elements = self.driver.find_elements(By.XPATH, "//*[starts-with(@data-goods, '') or starts-with(@data-product, '') or @data-id or @data-no]")
            for el in data_elements[:10]:
                try:
                    tag = el.tag_name
                    attrs = {}
                    for attr in ["data-goods", "data-product", "data-id", "data-no", "data-goods-no", "data-goodsno"]:
                        val = el.get_attribute(attr)
                        if val:
                            attrs[attr] = val
                    if attrs:
                        result["data_attributes"].append({
                            "tag": tag,
                            "class": el.get_attribute("class") or "",
                            "attributes": attrs
                        })
                except:
                    continue

            # 3. 카드 형태의 요소 (class에 card/item/goods 포함)
            card_selectors = [
                "[class*='card']",
                "[class*='item']",
                "[class*='goods-box']",
                "[class*='product-box']",
                "[class*='goods-wrap']",
                "[class*='product-wrap']"
            ]
            for selector in card_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for el in elements[:5]:
                        class_attr = el.get_attribute("class") or ""
                        tag = el.tag_name
                        # 내부에 링크가 있는지 확인
                        inner_links = el.find_elements(By.TAG_NAME, "a")
                        link_hrefs = [a.get_attribute("href") for a in inner_links[:3] if a.get_attribute("href")]
                        result["card_elements"].append({
                            "selector": selector,
                            "tag": tag,
                            "class": class_attr[:80],
                            "inner_links": link_hrefs[:3]
                        })
                except:
                    continue

            # 4. 이미지의 부모가 링크인 경우
            images = self.driver.find_elements(By.CSS_SELECTOR, "a img")
            for img in images[:10]:
                try:
                    parent_a = img.find_element(By.XPATH, "..")
                    href = parent_a.get_attribute("href")
                    if href and ("goods" in href.lower() or "product" in href.lower() or "detail" in href.lower()):
                        result["img_with_parent_link"].append({
                            "href": href,
                            "img_src": img.get_attribute("src")[:50] if img.get_attribute("src") else ""
                        })
                except:
                    continue

            self.logger.info(f"[ANALYSIS] onclick elements: {len(result['onclick_elements'])}")
            self.logger.info(f"[ANALYSIS] data-* elements: {len(result['data_attributes'])}")
            self.logger.info(f"[ANALYSIS] card elements: {len(result['card_elements'])}")
            self.logger.info(f"[ANALYSIS] img with parent link: {len(result['img_with_parent_link'])}")

            # 상세 로깅
            if result["onclick_elements"]:
                self.logger.info(f"[ANALYSIS] onclick samples: {result['onclick_elements'][:3]}")
            if result["data_attributes"]:
                self.logger.info(f"[ANALYSIS] data-* samples: {result['data_attributes'][:3]}")
            if result["card_elements"]:
                self.logger.info(f"[ANALYSIS] card samples: {result['card_elements'][:3]}")
            if result["img_with_parent_link"]:
                self.logger.info(f"[ANALYSIS] img link samples: {result['img_with_parent_link'][:3]}")

            return result

        except Exception as e:
            self.logger.error(f"Analysis failed: {e}")
            return result

    def click_first_product(self):
        """
        첫 번째 상품 클릭하여 상세 페이지로 이동

        2026-02-04 Update: 판촉물 페이지는 div.product-wrapper를 JavaScript로 클릭

        Returns:
            dict: 결과 정보 (success, product_url, product_name)
        """
        result = {
            "success": False,
            "product_url": "",
            "product_name": "",
            "error": ""
        }

        try:
            # 클릭 가능한 상품 찾기
            products = self.get_clickable_product_items()

            if not products or len(products) == 0:
                result["error"] = "No clickable products found"
                return result

            # 첫 번째 상품 정보 수집
            first_product = products[0]
            result["product_url"] = first_product.get_attribute("href") or ""

            # 상품명 추출 시도 (product-wrapper 내부의 item-title 또는 전체 텍스트)
            try:
                # item-title 클래스에서 상품명 찾기
                try:
                    title_el = first_product.find_element(By.CSS_SELECTOR, ".item-title")
                    result["product_name"] = title_el.text.strip()[:50]
                except:
                    result["product_name"] = first_product.text.strip()[:50] if first_product.text else "Unknown"
            except:
                result["product_name"] = "Unknown"

            self.logger.info(f"Clicking product: {result['product_name']}")

            # 현재 URL 저장
            original_url = self.get_current_url()

            # 클릭 시도 (JavaScript 클릭 우선 - div 요소는 일반 클릭이 안 될 수 있음)
            try:
                # JavaScript 클릭 (div.product-wrapper에 onclick 핸들러가 있을 가능성)
                self.driver.execute_script("arguments[0].click();", first_product)
            except Exception as e1:
                self.logger.debug(f"JavaScript click failed: {e1}")
                try:
                    # 일반 클릭 시도
                    first_product.click()
                except Exception as e2:
                    self.logger.debug(f"Normal click also failed: {e2}")
                    # 이미지 요소 클릭 시도
                    try:
                        img_el = first_product.find_element(By.CSS_SELECTOR, "img.product-image")
                        self.driver.execute_script("arguments[0].click();", img_el)
                    except:
                        pass

            # 페이지 로드 대기
            time.sleep(3)

            # 상세 페이지 이동 확인
            new_url = self.get_current_url()
            if new_url != original_url:
                result["success"] = True
                result["product_url"] = new_url
                self.logger.info(f"Navigated to product detail: {new_url}")
            else:
                result["error"] = "URL unchanged after click"

            return result

        except Exception as e:
            result["error"] = str(e)
            self.logger.error(f"Failed to click first product: {e}")
            return result

    def verify_product_detail_page(self):
        """
        상품 상세 페이지 요소 확인

        Returns:
            dict: 검증 결과 (is_detail_page, found_elements)
        """
        result = {
            "is_detail_page": False,
            "url": self.get_current_url(),
            "found_elements": [],
            "missing_elements": []
        }

        # URL 기반 확인
        url = result["url"].lower()
        if any(keyword in url for keyword in ["goods", "product", "detail", "item"]):
            result["is_detail_page"] = True

        # 상품 상세 페이지 요소 확인
        detail_elements = {
            "상품명": [
                (By.CSS_SELECTOR, ".goods-name"),
                (By.CSS_SELECTOR, ".product-name"),
                (By.CSS_SELECTOR, "[class*='goods-title']"),
                (By.CSS_SELECTOR, "[class*='product-title']"),
                (By.CSS_SELECTOR, "h1"),
                (By.CSS_SELECTOR, "h2"),
            ],
            "가격": [
                (By.CSS_SELECTOR, ".goods-price"),
                (By.CSS_SELECTOR, ".product-price"),
                (By.CSS_SELECTOR, "[class*='price']"),
                (By.XPATH, "//*[contains(text(), '원')]"),
            ],
            "이미지": [
                (By.CSS_SELECTOR, ".goods-image img"),
                (By.CSS_SELECTOR, ".product-image img"),
                (By.CSS_SELECTOR, "[class*='goods'] img"),
                (By.CSS_SELECTOR, "[class*='product'] img"),
                (By.CSS_SELECTOR, "img[src*='goods']"),
            ],
            "구매버튼": [
                (By.XPATH, "//button[contains(text(), '구매')]"),
                (By.XPATH, "//button[contains(text(), '장바구니')]"),
                (By.XPATH, "//button[contains(text(), '담기')]"),
                (By.CSS_SELECTOR, "button[class*='buy']"),
                (By.CSS_SELECTOR, "button[class*='cart']"),
            ]
        }

        for element_name, locators in detail_elements.items():
            found = False
            for locator in locators:
                try:
                    elements = self.driver.find_elements(*locator)
                    if elements and len(elements) > 0:
                        result["found_elements"].append(element_name)
                        found = True
                        break
                except:
                    continue
            if not found:
                result["missing_elements"].append(element_name)

        # 2개 이상의 요소가 있으면 상세 페이지로 인정
        if len(result["found_elements"]) >= 2:
            result["is_detail_page"] = True

        self.logger.info(f"Product detail verification: {result}")
        return result

    def navigate_to_category_and_get_first_product(self, category_name):
        """
        특정 카테고리로 이동 후 첫 번째 상품 상세 페이지 접근

        Args:
            category_name: 카테고리 이름

        Returns:
            dict: 결과 정보
        """
        result = {
            "category": category_name,
            "category_clicked": False,
            "product_clicked": False,
            "detail_page_verified": False,
            "product_info": {},
            "error": ""
        }

        try:
            # 1. 메인 페이지로 이동
            self.navigate_to_main()
            time.sleep(2)

            # 2. 카테고리 클릭
            category_clicked = self.click_category_by_text(category_name)
            result["category_clicked"] = category_clicked

            if not category_clicked:
                result["error"] = f"Failed to click category: {category_name}"
                return result

            # 페이지 완전 로딩 대기 (동적 콘텐츠 로드)
            time.sleep(5)
            self.wait_for_page_load()

            # 3. 첫 번째 상품 클릭
            product_result = self.click_first_product()
            result["product_clicked"] = product_result["success"]
            result["product_info"] = product_result

            if not product_result["success"]:
                result["error"] = product_result.get("error", "Failed to click product")
                return result

            # 4. 상세 페이지 검증
            detail_result = self.verify_product_detail_page()
            result["detail_page_verified"] = detail_result["is_detail_page"]
            result["detail_verification"] = detail_result

            return result

        except Exception as e:
            result["error"] = str(e)
            self.logger.error(f"Failed category product test: {e}")
            return result

    # ==================== Helper Methods ====================
    def get_page_info(self):
        """
        현재 페이지 정보 수집 (디버깅용)

        Returns:
            dict: 페이지 정보
        """
        info = {
            "url": self.get_current_url(),
            "title": self.get_page_title(),
            "categories": self.get_all_categories(),
            "product_count": self.get_product_count(),
        }

        self.logger.info(f"Page info: {info}")
        return info

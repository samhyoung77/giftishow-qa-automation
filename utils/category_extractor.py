"""
카테고리 메뉴 구조 추출 모듈
기프티쇼 비즈 웹사이트의 전체 카테고리 메뉴 구조를 URL과 함께 추출

메뉴 구조:
- 대분류 (Level 1): 사무용품, 가방/의류, USB/디지털/가전 등
- 중분류 (Level 2): 에코백/장바구니/쇼핑백, 가방, 지갑/명함케이스 등
- 소분류 (Level 3): 에코백, 리유저블백, 장바구니 등

사용법:
    from utils.category_extractor import CategoryMenuExtractor

    extractor = CategoryMenuExtractor(driver)
    menu_data = extractor.extract_menu_structure()
    extractor.export_to_json("category_menu.json")
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
import json
import csv
import os
from datetime import datetime
import logging
import time


class CategoryMenuExtractor:
    """카테고리 메뉴 구조를 추출하는 클래스 (계층 구조 지원)"""

    def __init__(self, driver, base_url="https://biz.giftishow.com"):
        """
        CategoryMenuExtractor 초기화

        Args:
            driver: Selenium WebDriver 인스턴스
            base_url: 기본 URL
        """
        self.driver = driver
        self.base_url = base_url
        self.logger = logging.getLogger(self.__class__.__name__)
        self.menu_data = {
            "extraction_time": "",
            "main_categories": [],      # Level 1: 대분류
            "sub_categories": [],       # Level 2: 중분류
            "detail_categories": [],    # Level 3: 소분류
            "all_categories": [],       # 전체 평면 리스트
            "tree_structure": []        # 트리 구조 (계층형)
        }

    def extract_menu_structure(self, collect_urls_by_click=True, max_level=2):
        """
        전체 메뉴 구조를 URL과 함께 추출 (계층 구조 포함)

        Args:
            collect_urls_by_click: True면 각 카테고리 클릭하여 URL 수집
            max_level: 추출할 최대 레벨 (1=대분류만, 2=중분류까지, 3=소분류까지)

        Returns:
            dict: 메뉴 데이터
        """
        self.menu_data["extraction_time"] = datetime.now().isoformat()
        self.max_level = max_level

        try:
            # 1. 홈페이지로 이동
            self.driver.get(self.base_url)
            time.sleep(2)

            # 2. 카테고리 버튼 클릭하여 메뉴 열기
            if not self._open_category_menu():
                self.logger.error("Failed to open category menu")
                return self.menu_data

            # 3. 계층 구조로 메뉴 아이템 추출
            self._extract_hierarchical_menu()

            # 4. URL 수집 (클릭 방식)
            if collect_urls_by_click:
                self._collect_urls_by_clicking_hierarchical()

            self.logger.info(f"Menu extraction complete: {len(self.menu_data['all_categories'])} categories")
            return self.menu_data

        except Exception as e:
            self.logger.error(f"Menu extraction error: {e}")
            import traceback
            traceback.print_exc()
            return self.menu_data

    def _open_category_menu(self):
        """카테고리 메뉴 열기"""
        try:
            wait = WebDriverWait(self.driver, 10)

            # 카테고리 버튼 찾기
            button_locators = [
                (By.XPATH, "//button[contains(., '카테고리')]"),
                (By.XPATH, "//button[contains(text(), '카테고리')]"),
                (By.CSS_SELECTOR, "button.category-button"),
            ]

            for locator in button_locators:
                try:
                    category_button = wait.until(EC.element_to_be_clickable(locator))
                    if category_button:
                        category_button.click()
                        time.sleep(1)
                        self.logger.info("Category menu opened")
                        return True
                except:
                    continue

            return False

        except Exception as e:
            self.logger.error(f"Failed to open category menu: {e}")
            return False

    def _extract_hierarchical_menu(self):
        """계층 구조로 메뉴 아이템 추출 (대분류 → 중분류 → 소분류)"""
        try:
            time.sleep(1)

            # 제외할 키워드
            exclude_patterns = [
                "로그인", "회원가입", "마이페이지", "장바구니",
                "고객센터", "공지사항", "혜택 받기", "베스트 100",
                "MD 인증", "맞춤 추천", "증정 플러스", "판촉", "쿠폰"
            ]

            # 대분류 추출 (첫 번째 컬럼)
            main_categories = self._extract_main_categories(exclude_patterns)

            if not main_categories:
                self.logger.warning("No main categories found, trying alternative method")
                self._extract_all_menu_items_flat()
                return

            self.logger.info(f"Found {len(main_categories)} main categories")

            # 각 대분류에 대해 중분류/소분류 추출
            for main_cat in main_categories:
                main_name = main_cat["name"]
                self.logger.info(f"Processing main category: {main_name}")

                # 카테고리 메뉴 다시 열기 (각 대분류 처리 전)
                self._open_category_menu()
                time.sleep(0.5)

                # 대분류에 마우스 호버하여 하위 메뉴 표시
                sub_categories = self._extract_sub_categories_for_main(main_name, exclude_patterns)
                main_cat["children"] = sub_categories

                # 중분류 데이터 추가
                for sub_cat in sub_categories:
                    sub_cat["parent"] = main_name
                    self.menu_data["sub_categories"].append(sub_cat)

                    # 중분류는 all_categories에 추가 (children 제외)
                    self.menu_data["all_categories"].append({
                        "name": sub_cat["name"],
                        "url": sub_cat.get("url", ""),
                        "full_url": sub_cat.get("full_url", ""),
                        "level": 2,
                        "parent": main_name,
                        "children": [c["name"] for c in sub_cat.get("children", [])]
                    })

                    # 소분류 추가
                    for detail_cat in sub_cat.get("children", []):
                        self.menu_data["detail_categories"].append(detail_cat)
                        self.menu_data["all_categories"].append({
                            "name": detail_cat["name"],
                            "url": detail_cat.get("url", ""),
                            "full_url": detail_cat.get("full_url", ""),
                            "level": 3,
                            "parent": sub_cat["name"],
                            "children": []
                        })

                # 대분류 데이터 추가 (마지막에)
                self.menu_data["main_categories"].append(main_cat)
                self.menu_data["all_categories"].insert(0, {
                    "name": main_cat["name"],
                    "url": main_cat.get("url", ""),
                    "full_url": main_cat.get("full_url", ""),
                    "level": 1,
                    "parent": "",
                    "children": [c["name"] for c in sub_categories]
                })

            # 트리 구조 저장
            self.menu_data["tree_structure"] = main_categories

            self.logger.info(f"Extracted hierarchical menu: {len(self.menu_data['main_categories'])} main, "
                           f"{len(self.menu_data['sub_categories'])} sub, "
                           f"{len(self.menu_data['detail_categories'])} detail")

        except Exception as e:
            self.logger.error(f"Failed to extract hierarchical menu: {e}")
            import traceback
            traceback.print_exc()

    def _extract_main_categories(self, exclude_patterns):
        """대분류 카테고리 추출 (기프티쇼 비즈 전용)"""
        main_categories = []
        seen_names = set()

        try:
            # 기프티쇼 비즈의 대분류 메뉴: a.text-with-badge
            # 참고: href가 없고 JavaScript로 동작함
            elements = self.driver.find_elements(By.CSS_SELECTOR, "a.text-with-badge")

            # 대분류만 필터링 (처음 8개가 주요 대분류)
            main_category_names = [
                "사무용품", "가방/의류", "USB/디지털/가전", "가정/생활용품",
                "텀블러/주방용품/식품", "건강/레저/차량", "상패/트로피/명패/깃발", "B2B 특가상품"
            ]

            for element in elements:
                try:
                    name = element.text.strip()

                    if not name or name in seen_names:
                        continue

                    if any(pattern in name for pattern in exclude_patterns):
                        continue

                    # 대분류 리스트에 있거나, 처음 발견되는 카테고리인 경우
                    if name in main_category_names or (len(main_categories) < 8 and not any(pattern in name for pattern in exclude_patterns)):
                        seen_names.add(name)
                        main_categories.append({
                            "name": name,
                            "url": "",  # href 없음, 나중에 클릭으로 수집
                            "full_url": "",
                            "level": 1,
                            "parent": "",
                            "children": []
                        })

                except StaleElementReferenceException:
                    continue
                except Exception as e:
                    self.logger.debug(f"Error processing element: {e}")
                    continue

            # 대분류가 없으면 text-with-badge에서 처음 8개 사용
            if not main_categories:
                for element in elements[:8]:
                    try:
                        name = element.text.strip()
                        if name and name not in seen_names:
                            seen_names.add(name)
                            main_categories.append({
                                "name": name,
                                "url": "",
                                "full_url": "",
                                "level": 1,
                                "parent": "",
                                "children": []
                            })
                    except:
                        continue

        except Exception as e:
            self.logger.error(f"Error extracting main categories: {e}")

        return main_categories

    def _extract_sub_categories_for_main(self, main_name, exclude_patterns):
        """특정 대분류에 대한 모든 중분류 추출 (기프티쇼 비즈 전용)

        기프티쇼 비즈 메뉴 구조:
        - 처음 8개: 대분류 (고정)
        - 9번째부터: 중분류/소분류 (호버한 대분류에 따라 변경)
        - 중분류: 두 번째 컬럼에 표시 (div.category-menu-item 내부의 첫 번째 그룹)
        - 소분류: 세 번째 컬럼에 표시 (중분류 호버 시)
        """
        sub_categories = []
        seen_sub_names = set()
        max_level = getattr(self, 'max_level', 2)

        try:
            # 대분류 요소에 호버
            self._hover_main_category(main_name)
            time.sleep(0.8)

            # 호버 후 표시되는 모든 링크 가져오기
            all_links = self.driver.find_elements(By.CSS_SELECTOR, "a.text-with-badge")
            visible_links = [l for l in all_links if l.is_displayed()]

            # 처음 8개는 대분류이므로 건너뛰기
            sub_detail_links = visible_links[8:]

            self.logger.debug(f"  {main_name}: Found {len(sub_detail_links)} items after main categories")

            # 기프티쇼 비즈의 중분류/소분류 패턴 분석
            # - 중분류: 보통 첫 번째 그룹, 이름에 '/' 포함되는 경우 많음
            # - 소분류: 중분류 다음에 오는 단일 명칭
            # - 'on' 클래스: 현재 선택된 항목 (중분류일 가능성 높음)

            current_sub = None

            for idx, link in enumerate(sub_detail_links):
                try:
                    name = link.text.strip()

                    if not name:
                        continue

                    if any(pattern in name for pattern in exclude_patterns):
                        continue

                    # 부모 요소의 class로 선택 상태 확인
                    parent_elem = link.find_element(By.XPATH, "..")
                    parent_class = parent_elem.get_attribute("class") or ""
                    is_on = "on" in parent_class.lower()

                    # 중분류 판단 조건 (더 포괄적으로):
                    # 1. 'on' 클래스가 있으면 중분류
                    # 2. 첫 번째 항목은 항상 중분류
                    # 3. 이름에 슬래시(/)가 포함되면 중분류 (에코백/장바구니/쇼핑백)
                    # 4. 이전에 소분류가 있었고, 새로운 그룹 시작처럼 보이면 중분류
                    #    (이름이 비교적 일반적인 카테고리명인 경우)

                    # 일반적인 중분류 패턴 (단독으로 쓰이는 명칭)
                    common_sub_patterns = [
                        "가방", "지갑", "파우치", "의류", "모자", "우산", "양말",
                        "USB", "보조배터리", "충전기", "케이블", "이어폰", "스피커",
                        "텀블러", "머그컵", "식기", "주방용품",
                        "수건", "담요", "쿠션", "생활용품",
                        "골프", "레저", "건강", "뷰티",
                        "상패", "트로피", "명패", "현판",
                        "볼펜", "필기구", "메모", "다이어리", "노트", "달력"
                    ]

                    is_common_sub = any(pattern in name for pattern in common_sub_patterns)
                    has_slash = "/" in name
                    is_first = (idx == 0)

                    # 중분류로 판단
                    is_sub_category = is_on or is_first or has_slash or is_common_sub

                    if is_sub_category and name not in seen_sub_names:
                        seen_sub_names.add(name)
                        current_sub = {
                            "name": name,
                            "url": "",  # 나중에 클릭으로 수집
                            "full_url": "",
                            "level": 2,
                            "parent": main_name,
                            "children": []
                        }
                        sub_categories.append(current_sub)
                        self.logger.debug(f"    [L2] {name} (on={is_on}, slash={has_slash}, common={is_common_sub})")
                    elif not is_sub_category and max_level >= 3 and current_sub:
                        # 소분류로 추가 (max_level >= 3일 때만)
                        current_sub["children"].append({
                            "name": name,
                            "url": "",
                            "full_url": "",
                            "level": 3,
                            "parent": current_sub["name"],
                            "children": []
                        })
                        self.logger.debug(f"      [L3] {name}")

                except StaleElementReferenceException:
                    continue
                except Exception as e:
                    self.logger.debug(f"Error processing link: {e}")
                    continue

            self.logger.info(f"  {main_name}: Found {len(sub_categories)} sub-categories")

        except Exception as e:
            self.logger.debug(f"Error extracting sub categories for {main_name}: {e}")

        return sub_categories

    def _extract_detail_categories_for_sub(self, sub_name, exclude_patterns):
        """특정 중분류에 대한 소분류 추출"""
        detail_categories = []
        seen_names = set()

        try:
            # 중분류 요소에 호버
            self._hover_sub_category(sub_name)
            time.sleep(0.3)

            # 소분류 링크 찾기 (세 번째 컬럼)
            detail_locators = [
                "div.category-menu-wrap > div:nth-child(3) a",
                "div.depth3 a",
                "ul.detail-category > li > a",
            ]

            for selector in detail_locators:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)

                    for element in elements:
                        try:
                            name = element.text.strip()
                            href = element.get_attribute("href") or ""

                            if not name or name in seen_names:
                                continue

                            if any(pattern in name for pattern in exclude_patterns):
                                continue

                            seen_names.add(name)
                            detail_categories.append({
                                "name": name,
                                "url": href,
                                "full_url": self._build_full_url(href),
                                "level": 3,
                                "parent": sub_name,
                                "children": []
                            })
                        except StaleElementReferenceException:
                            continue
                        except Exception as e:
                            continue

                    if detail_categories:
                        break

                except Exception as e:
                    continue

        except Exception as e:
            self.logger.debug(f"Error extracting detail categories for {sub_name}: {e}")

        return detail_categories

    def _hover_main_category(self, main_name):
        """대분류 요소에 마우스 호버"""
        try:
            locators = [
                (By.XPATH, f"//a[contains(@class, 'text-with-badge') and contains(text(), '{main_name}')]"),
                (By.XPATH, f"//a[text()='{main_name}']"),
                (By.PARTIAL_LINK_TEXT, main_name),
            ]

            for locator in locators:
                try:
                    element = self.driver.find_element(*locator)
                    ActionChains(self.driver).move_to_element(element).perform()
                    return True
                except:
                    continue

        except Exception as e:
            self.logger.debug(f"Hover failed for main category '{main_name}': {e}")

        return False

    def _hover_sub_category(self, sub_name):
        """중분류 요소에 마우스 호버"""
        try:
            locators = [
                (By.XPATH, f"//a[text()='{sub_name}']"),
                (By.PARTIAL_LINK_TEXT, sub_name),
            ]

            for locator in locators:
                try:
                    element = self.driver.find_element(*locator)
                    ActionChains(self.driver).move_to_element(element).perform()
                    return True
                except:
                    continue

        except Exception as e:
            self.logger.debug(f"Hover failed for sub category '{sub_name}': {e}")

        return False

    def _extract_all_menu_items_flat(self):
        """모든 메뉴 아이템을 평면 구조로 추출 (fallback)"""
        try:
            time.sleep(1)

            locators = [
                (By.CSS_SELECTOR, "a.text-with-badge", 1),
                (By.CSS_SELECTOR, "div.category-area a", 1),
            ]

            seen_names = set()
            exclude_patterns = [
                "로그인", "회원가입", "마이페이지", "장바구니",
                "고객센터", "공지사항", "혜택 받기"
            ]

            for locator_tuple in locators:
                by, selector, level = locator_tuple
                try:
                    elements = self.driver.find_elements(by, selector)

                    for element in elements:
                        try:
                            title = element.text.strip()
                            href = element.get_attribute("href") or ""

                            if not title or title in seen_names:
                                continue

                            if any(pattern in title for pattern in exclude_patterns):
                                continue

                            seen_names.add(title)

                            menu_item = {
                                "name": title,
                                "url": href,
                                "full_url": self._build_full_url(href),
                                "level": level,
                                "parent": "",
                                "children": []
                            }

                            if level == 1:
                                self.menu_data["main_categories"].append(menu_item)
                            elif level == 2:
                                self.menu_data["sub_categories"].append(menu_item)
                            else:
                                self.menu_data["detail_categories"].append(menu_item)

                            self.menu_data["all_categories"].append(menu_item)

                        except Exception as e:
                            continue

                except Exception as e:
                    continue

            self.logger.info(f"Extracted {len(self.menu_data['all_categories'])} menu items (flat)")

        except Exception as e:
            self.logger.error(f"Failed to extract menu items: {e}")

    def _collect_urls_by_clicking_hierarchical(self):
        """각 카테고리를 클릭하여 실제 URL 수집 (대분류 + 중분류만)"""
        self.logger.info("Collecting URLs by clicking each category...")

        original_url = self.driver.current_url
        max_level = getattr(self, 'max_level', 2)

        # URL이 없는 카테고리만 수집 (max_level까지만)
        categories_to_update = [
            cat for cat in self.menu_data["all_categories"]
            if (not cat.get("url") or not cat["url"].startswith("http"))
            and cat.get("level", 1) <= max_level
        ]

        total = len(categories_to_update)
        self.logger.info(f"Categories needing URL collection (L1-L{max_level}): {total}")

        for idx, cat in enumerate(categories_to_update):
            cat_name = cat["name"]
            cat_level = cat.get("level", 1)
            cat_parent = cat.get("parent", "")

            try:
                # 카테고리 메뉴 열기
                if not self._open_category_menu():
                    continue

                time.sleep(0.5)

                # 계층에 따라 클릭 방식 다르게 처리
                clicked = False

                if cat_level == 1:
                    # 대분류: 직접 클릭
                    clicked = self._click_category_by_name(cat_name)
                elif cat_level == 2:
                    # 중분류: 대분류 호버 후 클릭
                    if cat_parent:
                        self._hover_main_category(cat_parent)
                        time.sleep(0.5)
                    clicked = self._click_category_by_name(cat_name)

                if clicked:
                    time.sleep(1.5)
                    new_url = self.driver.current_url

                    if new_url != original_url:
                        cat["url"] = new_url
                        cat["full_url"] = new_url
                        self.logger.info(f"[{idx+1}/{total}] L{cat_level} {cat_name}: {new_url}")
                    else:
                        self.logger.warning(f"[{idx+1}/{total}] L{cat_level} {cat_name}: URL unchanged")
                else:
                    self.logger.warning(f"[{idx+1}/{total}] L{cat_level} {cat_name}: Click failed")

                # 메인 페이지로 돌아가기
                self.driver.get(original_url)
                time.sleep(0.8)

            except Exception as e:
                self.logger.error(f"Error collecting URL for '{cat_name}': {e}")
                try:
                    self.driver.get(original_url)
                    time.sleep(0.8)
                except:
                    pass

        # 트리 구조에도 URL 업데이트
        self._update_tree_urls()

        collected_count = len([c for c in self.menu_data["all_categories"] if c.get("url")])
        self.logger.info(f"URL collection complete: {collected_count}/{len(self.menu_data['all_categories'])} with URLs")

    def _update_tree_urls(self):
        """트리 구조의 URL 업데이트"""
        url_map = {cat["name"]: cat.get("url", "") for cat in self.menu_data["all_categories"] if cat.get("url")}

        def update_node(node):
            if node["name"] in url_map:
                node["url"] = url_map[node["name"]]
                node["full_url"] = url_map[node["name"]]
            for child in node.get("children", []):
                if isinstance(child, dict):
                    update_node(child)

        for main_cat in self.menu_data.get("tree_structure", []):
            update_node(main_cat)

    def _click_category_by_name(self, search_name):
        """카테고리명으로 클릭"""
        try:
            wait = WebDriverWait(self.driver, 5)

            # 슬래시가 있으면 첫 부분만 사용
            if '/' in search_name:
                search_name = search_name.split('/')[0].strip()

            locators = [
                (By.XPATH, f"//a[contains(@class, 'text-with-badge') and contains(text(), '{search_name}')]"),
                (By.XPATH, f"//a[contains(text(), '{search_name}')]"),
                (By.PARTIAL_LINK_TEXT, search_name),
            ]

            for locator in locators:
                try:
                    element = wait.until(EC.element_to_be_clickable(locator))
                    if element:
                        element.click()
                        return True
                except:
                    continue

            return False

        except Exception as e:
            self.logger.debug(f"Click failed for '{search_name}': {e}")
            return False

    def _build_full_url(self, href):
        """전체 URL 생성"""
        if not href:
            return ""
        if href.startswith("http"):
            return href
        if href.startswith("/"):
            return self.base_url + href
        return self.base_url + "/" + href

    # ==================== 내보내기 메서드 ====================

    def export_to_json(self, filename="category_menu.json", output_dir=None):
        """JSON 파일로 내보내기 (트리 구조 포함)"""
        try:
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
                filepath = os.path.join(output_dir, filename)
            else:
                filepath = filename

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.menu_data, f, ensure_ascii=False, indent=2)

            self.logger.info(f"Exported to JSON: {filepath}")
            return filepath

        except Exception as e:
            self.logger.error(f"JSON export failed: {e}")
            return None

    def export_to_csv(self, filename="category_menu.csv", output_dir=None):
        """CSV 파일로 내보내기 (계층 정보 포함)"""
        try:
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
                filepath = os.path.join(output_dir, filename)
            else:
                filepath = filename

            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["No", "Level", "Parent_Category", "Category_Name", "URL", "Full_URL", "Children_Count"])

                for idx, item in enumerate(self.menu_data["all_categories"], start=1):
                    children = item.get("children", [])
                    children_count = len(children) if isinstance(children, list) else 0

                    writer.writerow([
                        idx,
                        item.get("level", 1),
                        item.get("parent", ""),
                        item.get("name", ""),
                        item.get("url", ""),
                        item.get("full_url", ""),
                        children_count
                    ])

            self.logger.info(f"Exported to CSV: {filepath}")
            return filepath

        except Exception as e:
            self.logger.error(f"CSV export failed: {e}")
            return None

    def export_to_html(self, filename="category_menu.html", output_dir=None):
        """HTML 트리로 내보내기 (계층 구조 시각화)"""
        try:
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
                filepath = os.path.join(output_dir, filename)
            else:
                filepath = filename

            html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>기프티쇼 비즈 카테고리 메뉴 트리</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f9f9f9; }}
        h1 {{ color: #d41f75; }}
        .tree {{ margin-left: 20px; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .level-1 {{ font-weight: bold; color: #d41f75; margin: 20px 0 10px 0; font-size: 16px; border-bottom: 2px solid #d41f75; padding-bottom: 5px; }}
        .level-2 {{ margin-left: 25px; color: #333; font-size: 14px; margin: 8px 0; font-weight: 600; }}
        .level-3 {{ margin-left: 50px; color: #666; font-size: 13px; margin: 4px 0; }}
        a {{ text-decoration: none; color: inherit; }}
        a:hover {{ text-decoration: underline; color: #0066cc; }}
        .info {{ background: #fffbea; padding: 15px; border-radius: 5px; border-left: 4px solid #d41f75; margin-bottom: 20px; }}
        .stats {{ display: flex; gap: 20px; margin-top: 10px; flex-wrap: wrap; }}
        .stat-item {{ background: #f0f0f0; padding: 10px 15px; border-radius: 5px; }}
        .no-url {{ color: #cc0000; }}
        .parent-info {{ color: #888; font-size: 11px; margin-left: 10px; }}
        .children-toggle {{ cursor: pointer; color: #0066cc; font-size: 12px; margin-left: 10px; }}
        .category-group {{ margin-bottom: 15px; border-left: 3px solid #eee; padding-left: 10px; }}
    </style>
</head>
<body>
    <h1>🎁 기프티쇼 비즈 카테고리 메뉴 구조</h1>
    <div class="info">
        <p><strong>추출 시간:</strong> {self.menu_data["extraction_time"]}</p>
        <div class="stats">
            <div class="stat-item">대분류 (L1): {len(self.menu_data["main_categories"])}개</div>
            <div class="stat-item">중분류 (L2): {len(self.menu_data["sub_categories"])}개</div>
            <div class="stat-item">소분류 (L3): {len(self.menu_data["detail_categories"])}개</div>
            <div class="stat-item">총계: {len(self.menu_data["all_categories"])}개</div>
        </div>
    </div>
    <div class="tree">
"""

            # 트리 구조로 출력
            tree_structure = self.menu_data.get("tree_structure", [])

            if tree_structure:
                # 트리 구조가 있으면 계층적으로 출력
                for main_cat in tree_structure:
                    main_name = main_cat.get("name", "")
                    main_url = main_cat.get("full_url", "") or main_cat.get("url", "")

                    html_content += f'        <div class="category-group">\n'

                    if main_url:
                        html_content += f'            <div class="level-1"><a href="{main_url}" target="_blank">📁 {main_name}</a></div>\n'
                    else:
                        html_content += f'            <div class="level-1 no-url">📁 {main_name} (URL 없음)</div>\n'

                    # 중분류 (children)
                    for sub_cat in main_cat.get("children", []):
                        if isinstance(sub_cat, dict):
                            sub_name = sub_cat.get("name", "")
                            sub_url = sub_cat.get("full_url", "") or sub_cat.get("url", "")

                            if sub_url:
                                html_content += f'            <div class="level-2"><a href="{sub_url}" target="_blank">📂 {sub_name}</a></div>\n'
                            else:
                                html_content += f'            <div class="level-2 no-url">📂 {sub_name} (URL 없음)</div>\n'

                            # 소분류 (sub children)
                            for detail_cat in sub_cat.get("children", []):
                                if isinstance(detail_cat, dict):
                                    detail_name = detail_cat.get("name", "")
                                    detail_url = detail_cat.get("full_url", "") or detail_cat.get("url", "")

                                    if detail_url:
                                        html_content += f'            <div class="level-3"><a href="{detail_url}" target="_blank">📄 {detail_name}</a></div>\n'
                                    else:
                                        html_content += f'            <div class="level-3 no-url">📄 {detail_name} (URL 없음)</div>\n'

                    html_content += f'        </div>\n'
            else:
                # 트리 구조가 없으면 평면 리스트로 출력 (기존 방식)
                for item in self.menu_data["all_categories"]:
                    level = item.get("level", 1)
                    name = item.get("name", "")
                    url = item.get("full_url", "") or item.get("url", "")
                    parent = item.get("parent", "")

                    parent_info = f'<span class="parent-info">(상위: {parent})</span>' if parent else ''

                    if url:
                        html_content += f'        <div class="level-{level}"><a href="{url}" target="_blank">{name}</a>{parent_info}</div>\n'
                    else:
                        html_content += f'        <div class="level-{level} no-url">{name} (URL 없음){parent_info}</div>\n'

            html_content += """    </div>
</body>
</html>
"""

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)

            self.logger.info(f"Exported to HTML: {filepath}")
            return filepath

        except Exception as e:
            self.logger.error(f"HTML export failed: {e}")
            return None

    def get_categories_for_sheets(self):
        """
        Google Sheets 저장용 카테고리 리스트 반환 (계층 정보 포함)

        Returns:
            list[dict]: 카테고리 정보 리스트
        """
        return [
            {
                "name": cat.get("name", ""),
                "url": cat.get("full_url", "") or cat.get("url", ""),
                "parent": cat.get("parent", ""),
                "level": cat.get("level", 1)
            }
            for cat in self.menu_data["all_categories"]
        ]

    def get_category_urls_dict(self):
        """
        카테고리명 -> URL 딕셔너리 반환 (테스트에서 활용)

        Returns:
            dict: {카테고리명: URL}
        """
        return {
            cat.get("name", ""): cat.get("full_url", "") or cat.get("url", "")
            for cat in self.menu_data["all_categories"]
            if cat.get("name") and (cat.get("full_url") or cat.get("url"))
        }

    def print_tree(self):
        """콘솔에 트리 구조 출력"""
        print("\n" + "=" * 60)
        print("Category Menu Tree Structure")
        print("=" * 60)

        tree_structure = self.menu_data.get("tree_structure", [])

        if tree_structure:
            for main_cat in tree_structure:
                print(f"\n[L1] {main_cat['name']}")

                for sub_cat in main_cat.get("children", []):
                    if isinstance(sub_cat, dict):
                        print(f"   +-- [L2] {sub_cat['name']}")

                        detail_children = sub_cat.get("children", [])
                        for i, detail_cat in enumerate(detail_children):
                            if isinstance(detail_cat, dict):
                                prefix = "       +--" if i == len(detail_children) - 1 else "       +--"
                                print(f"{prefix} [L3] {detail_cat['name']}")
        else:
            for cat in self.menu_data["all_categories"]:
                level = cat.get("level", 1)
                indent = "  " * (level - 1)
                print(f"{indent}[L{level}] {cat['name']}")

        print("\n" + "=" * 60)


# ==================== 독립 실행 ====================
if __name__ == "__main__":
    """
    독립 실행 방법:
    python utils/category_extractor.py
    """
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options

    # Chrome 옵션 설정
    chrome_options = Options()
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_experimental_option(
        "prefs", {
            "profile.default_content_setting_values.notifications": 2
        }
    )

    print("=" * 60)
    print("기프티쇼 비즈 카테고리 메뉴 추출기 (계층 구조)")
    print("=" * 60)

    # 드라이버 시작
    driver = webdriver.Chrome(options=chrome_options)

    try:
        # 추출기 생성 및 실행
        extractor = CategoryMenuExtractor(driver)
        menu_data = extractor.extract_menu_structure(collect_urls_by_click=True)

        if menu_data and menu_data.get("all_categories"):
            print(f"\n✅ 추출 완료!")
            print(f"   대분류: {len(menu_data['main_categories'])}개")
            print(f"   중분류: {len(menu_data['sub_categories'])}개")
            print(f"   소분류: {len(menu_data['detail_categories'])}개")
            print(f"   총계: {len(menu_data['all_categories'])}개")

            # 트리 출력
            extractor.print_tree()

            # 내보내기
            output_dir = "reports"
            extractor.export_to_json("category_menu.json", output_dir)
            extractor.export_to_csv("category_menu.csv", output_dir)
            extractor.export_to_html("category_menu.html", output_dir)

            print(f"\n📊 모든 메뉴 데이터가 '{output_dir}' 폴더에 저장되었습니다!")
        else:
            print("❌ 카테고리 추출에 실패했습니다.")

    finally:
        driver.quit()
        print("\n드라이버 종료됨")

"""
Google Sheets 연동 모듈
테스트 결과를 Google Sheets에 기록하고 관리
"""
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import logging
import os
from typing import List, Dict, Optional


class GoogleSheetsReporter:
    """Google Sheets 테스트 결과 리포터"""

    def __init__(self, sheet_url: str, credentials_path: str = "credentials.json"):
        """
        GoogleSheetsReporter 초기화

        Args:
            sheet_url: Google Sheets URL
            credentials_path: Google API 인증 파일 경로
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.sheet_url = sheet_url
        self.credentials_path = credentials_path
        self.client = None
        self.sheet = None
        self._authorize()

    def _authorize(self):
        """Google Sheets API 인증"""
        try:
            if not os.path.exists(self.credentials_path):
                self.logger.warning(f"Credentials file not found: {self.credentials_path}")
                self.logger.warning("Google Sheets reporting will be disabled")
                return

            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                self.credentials_path, scope
            )
            self.client = gspread.authorize(creds)
            self.sheet = self.client.open_by_url(self.sheet_url)
            self.logger.info("Google Sheets authorization successful")
        except Exception as e:
            self.logger.error(f"Failed to authorize Google Sheets: {e}")
            self.client = None
            self.sheet = None

    def log_test_result(
        self,
        tc_id: str,
        page: str,
        scenario: str,
        result: str,
        browser: str = "Chrome",
        os_name: str = "Windows",
        duration: float = 0.0,
        error_msg: str = "",
        screenshot_url: str = "",
        test_run_id: str = "",
        environment: str = "Production",
        tester: str = "Automation"
    ):
        """
        테스트 결과를 TestResults 시트에 기록

        Args:
            tc_id: 테스트 케이스 ID
            page: 페이지명
            scenario: 시나리오명
            result: 결과 (PASS/FAIL)
            browser: 브라우저명
            os_name: 운영체제
            duration: 실행 시간(초)
            error_msg: 에러 메시지
            screenshot_url: 스크린샷 경로
            test_run_id: 배치 실행 ID
            environment: 실행 환경
            tester: 실행자
        """
        if not self.sheet:
            self.logger.warning("Google Sheets not available, skipping log")
            return

        try:
            worksheet = self.sheet.worksheet("TestResults")

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if not test_run_id:
                test_run_id = f"RUN_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            row = [
                timestamp,
                test_run_id,
                tc_id,
                page,
                scenario,
                browser,
                os_name,
                result,
                round(duration, 2),
                error_msg,
                screenshot_url,
                tester,
                environment
            ]

            worksheet.append_row(row)
            self.logger.info(f"Test result logged: {tc_id} - {result}")

        except Exception as e:
            self.logger.error(f"Failed to log test result: {e}")

    def log_multiple_results(self, results: List[Dict]):
        """
        여러 테스트 결과를 한번에 기록

        Args:
            results: 테스트 결과 딕셔너리 리스트
        """
        if not self.sheet:
            self.logger.warning("Google Sheets not available, skipping log")
            return

        try:
            worksheet = self.sheet.worksheet("TestResults")

            rows = []
            for result in results:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                test_run_id = result.get('test_run_id',
                    f"RUN_{datetime.now().strftime('%Y%m%d_%H%M%S')}")

                row = [
                    timestamp,
                    test_run_id,
                    result.get('tc_id', ''),
                    result.get('page', ''),
                    result.get('scenario', ''),
                    result.get('browser', 'Chrome'),
                    result.get('os', 'Windows'),
                    result.get('result', 'FAIL'),
                    round(result.get('duration', 0.0), 2),
                    result.get('error_msg', ''),
                    result.get('screenshot_url', ''),
                    result.get('tester', 'Automation'),
                    result.get('environment', 'Production')
                ]
                rows.append(row)

            if rows:
                worksheet.append_rows(rows)
                self.logger.info(f"Logged {len(rows)} test results")

        except Exception as e:
            self.logger.error(f"Failed to log multiple results: {e}")

    def update_summary(self):
        """
        TestSummary 시트 업데이트 (대시보드 형태)

        구성:
        1. 전체 현황 (총 테스트, PASS, FAIL, 성공률)
        2. OS별 테스트 결과
        3. TC별 테스트 결과
        4. 최근 실패 로그 (Last 10)
        """
        if not self.sheet:
            self.logger.warning("Google Sheets not available, skipping summary update")
            return

        try:
            results_sheet = self.sheet.worksheet("TestResults")
            summary_sheet = self.sheet.worksheet("TestSummary")

            # 전체 결과 가져오기
            all_results = results_sheet.get_all_records()

            if not all_results:
                self.logger.warning("No test results found")
                return

            # ==================== 1. 전체 현황 ====================
            total = len(all_results)
            pass_count = sum(1 for r in all_results if r.get('Result') == 'PASS')
            fail_count = total - pass_count
            pass_rate = (pass_count / total * 100) if total > 0 else 0

            # 시트 초기화 (기존 데이터 클리어)
            summary_sheet.clear()

            # 전체 현황 헤더
            summary_sheet.update(values=[["📊 전체 현황"]], range_name='A1')
            summary_sheet.update(values=[["마지막 업데이트", "총 테스트", "PASS", "FAIL", "성공률"]], range_name='A2:E2')
            summary_sheet.update(values=[[
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                total,
                pass_count,
                fail_count,
                f"{pass_rate:.1f}%"
            ]], range_name='A3:E3')

            # ==================== 2. OS별 테스트 결과 ====================
            os_stats = {}
            for r in all_results:
                os_name = r.get('OS', 'Unknown')
                if os_name not in os_stats:
                    os_stats[os_name] = {'pass': 0, 'fail': 0}
                if r.get('Result') == 'PASS':
                    os_stats[os_name]['pass'] += 1
                else:
                    os_stats[os_name]['fail'] += 1

            summary_sheet.update(values=[["📱 OS별 테스트 결과"]], range_name='A5')
            summary_sheet.update(values=[["OS", "PASS", "FAIL", "성공률"]], range_name='A6:D6')

            row = 7
            for os_name, stats in os_stats.items():
                os_total = stats['pass'] + stats['fail']
                os_rate = (stats['pass'] / os_total * 100) if os_total > 0 else 0
                summary_sheet.update(values=[[
                    os_name,
                    stats['pass'],
                    stats['fail'],
                    f"{os_rate:.1f}%"
                ]], range_name=f'A{row}:D{row}')
                row += 1

            # ==================== 3. TC별 테스트 결과 ====================
            tc_stats = {}
            for r in all_results:
                tc_id = r.get('TC_ID', 'Unknown')
                if tc_id not in tc_stats:
                    tc_stats[tc_id] = {'pass': 0, 'fail': 0}
                if r.get('Result') == 'PASS':
                    tc_stats[tc_id]['pass'] += 1
                else:
                    tc_stats[tc_id]['fail'] += 1

            row += 1  # 빈 줄
            summary_sheet.update(values=[["🧪 TC별 테스트 결과"]], range_name=f'A{row}')
            row += 1
            summary_sheet.update(values=[["TC_ID", "PASS", "FAIL", "성공률"]], range_name=f'A{row}:D{row}')
            row += 1

            for tc_id, stats in tc_stats.items():
                tc_total = stats['pass'] + stats['fail']
                tc_rate = (stats['pass'] / tc_total * 100) if tc_total > 0 else 0
                summary_sheet.update(values=[[
                    tc_id,
                    stats['pass'],
                    stats['fail'],
                    f"{tc_rate:.1f}%"
                ]], range_name=f'A{row}:D{row}')
                row += 1

            # ==================== 4. 최근 실패 로그 (Last 10) ====================
            failed_results = [r for r in all_results if r.get('Result') == 'FAIL']
            # 최신순 정렬 (Timestamp 기준)
            failed_results.sort(key=lambda x: x.get('Timestamp', ''), reverse=True)
            recent_failures = failed_results[:10]

            row += 1  # 빈 줄
            summary_sheet.update(values=[["🚨 최근 실패 로그 (Last 10)"]], range_name=f'A{row}')
            row += 1
            summary_sheet.update(values=[["발생 시간", "TC_ID", "Scenario", "에러 내용"]], range_name=f'A{row}:D{row}')
            row += 1

            for fail in recent_failures:
                error_msg = fail.get('Error_Message', '')[:50]  # 50자 제한
                summary_sheet.update(values=[[
                    fail.get('Timestamp', ''),
                    fail.get('TC_ID', ''),
                    fail.get('Scenario_Name', '')[:30],  # 30자 제한
                    error_msg
                ]], range_name=f'A{row}:D{row}')
                row += 1

            self.logger.info(f"Summary dashboard updated: {total} tests, {pass_rate:.1f}% pass rate")

        except Exception as e:
            self.logger.error(f"Failed to update summary: {e}")

    def add_daily_trend(self):
        """
        DailyTrend 시트에 오늘의 결과 추가
        """
        if not self.sheet:
            self.logger.warning("Google Sheets not available, skipping daily trend")
            return

        try:
            results_sheet = self.sheet.worksheet("TestResults")
            trend_sheet = self.sheet.worksheet("DailyTrend")

            # 오늘 날짜
            today = datetime.now().strftime("%Y-%m-%d")

            # 오늘의 결과만 필터링
            all_results = results_sheet.get_all_records()
            today_results = [
                r for r in all_results
                if r.get('Timestamp', '').startswith(today)
            ]

            if not today_results:
                self.logger.warning("No test results for today")
                return

            total = len(today_results)
            pass_count = sum(1 for r in today_results if r.get('Result') == 'PASS')
            fail_count = total - pass_count
            pass_rate = f"{(pass_count / total * 100):.0f}%" if total > 0 else "0%"

            # 오늘 날짜가 이미 있는지 확인
            trend_data = trend_sheet.get_all_records()
            existing_row = None
            for idx, row in enumerate(trend_data, start=2):  # 헤더 제외
                if row.get('Date') == today:
                    existing_row = idx
                    break

            row_data = [today, total, pass_count, fail_count, pass_rate]

            if existing_row:
                # 기존 행 업데이트
                trend_sheet.update(values=[row_data], range_name=f'A{existing_row}:E{existing_row}')
                self.logger.info(f"Daily trend updated for {today}")
            else:
                # 새 행 추가
                trend_sheet.append_row(row_data)
                self.logger.info(f"Daily trend added for {today}")

        except Exception as e:
            self.logger.error(f"Failed to add daily trend: {e}")

    def get_test_scenarios(self) -> List[Dict]:
        """
        TestCase_Scenarios 시트에서 테스트 시나리오 가져오기

        Returns:
            List[Dict]: 테스트 시나리오 리스트
        """
        if not self.sheet:
            self.logger.warning("Google Sheets not available")
            return []

        try:
            scenarios_sheet = self.sheet.worksheet("TestCase_Scenarios")
            scenarios = scenarios_sheet.get_all_records()
            self.logger.info(f"Retrieved {len(scenarios)} test scenarios")
            return scenarios

        except Exception as e:
            self.logger.error(f"Failed to get test scenarios: {e}")
            return []

    def get_scenarios_by_status(self, status: str = "Done") -> List[Dict]:
        """
        자동화 상태별 시나리오 가져오기

        Args:
            status: Automation_Status (Done/In Progress/Pending)

        Returns:
            List[Dict]: 필터링된 시나리오 리스트
        """
        all_scenarios = self.get_test_scenarios()
        filtered = [
            s for s in all_scenarios
            if s.get('Automation_Status') == status
        ]
        self.logger.info(f"Found {len(filtered)} scenarios with status: {status}")
        return filtered

    def create_default_sheets(self):
        """
        기본 시트 구조 생성 (TestCase_Scenarios, TestResults, TestSummary, DailyTrend)
        """
        if not self.sheet:
            self.logger.error("Google Sheets not available")
            return

        try:
            # TestCase_Scenarios 시트
            try:
                self.sheet.worksheet("TestCase_Scenarios")
            except gspread.exceptions.WorksheetNotFound:
                scenarios_sheet = self.sheet.add_worksheet(
                    title="TestCase_Scenarios", rows=100, cols=10
                )
                headers = [
                    "TC_ID", "Page", "Category", "Scenario_Name", "Pre_Condition",
                    "Test_Steps", "Expected_Result", "Priority", "Automation_Status", "Note"
                ]
                scenarios_sheet.update(values=[headers], range_name='A1:J1')
                self.logger.info("Created TestCase_Scenarios sheet")

            # TestResults 시트
            try:
                self.sheet.worksheet("TestResults")
            except gspread.exceptions.WorksheetNotFound:
                results_sheet = self.sheet.add_worksheet(
                    title="TestResults", rows=1000, cols=13
                )
                headers = [
                    "Timestamp", "Test_Run_ID", "TC_ID", "Page", "Scenario_Name",
                    "Browser", "OS", "Result", "Duration_Sec", "Error_Message",
                    "Screenshot_URL", "Tester", "Environment"
                ]
                results_sheet.update(values=[headers], range_name='A1:M1')
                self.logger.info("Created TestResults sheet")

            # TestSummary 시트
            try:
                self.sheet.worksheet("TestSummary")
            except gspread.exceptions.WorksheetNotFound:
                summary_sheet = self.sheet.add_worksheet(
                    title="TestSummary", rows=10, cols=5
                )
                headers = ["Last_Updated", "Total_Tests", "Pass_Count", "Fail_Count", "Pass_Rate"]
                summary_sheet.update(values=[headers], range_name='A1:E1')
                self.logger.info("Created TestSummary sheet")

            # DailyTrend 시트
            try:
                self.sheet.worksheet("DailyTrend")
            except gspread.exceptions.WorksheetNotFound:
                trend_sheet = self.sheet.add_worksheet(
                    title="DailyTrend", rows=365, cols=5
                )
                headers = ["Date", "Total", "Pass", "Fail", "Pass_Rate"]
                trend_sheet.update(values=[headers], range_name='A1:E1')
                self.logger.info("Created DailyTrend sheet")

            self.logger.info("All default sheets created successfully")

        except Exception as e:
            self.logger.error(f"Failed to create default sheets: {e}")

    # ==================== Menu Tree Check List 관련 메서드 ====================
    def update_menu_tree_checklist(self, categories: List[Dict]):
        """
        Menu_tree_check_list 시트에 카테고리 정보 기록

        GS_PRODUCT_001에서 수집된 카테고리 정보를 시트에 기록합니다.

        Args:
            categories: 카테고리 정보 리스트
                - name: 카테고리 이름
                - url: 카테고리 URL
                - parent: 상위 카테고리 (선택)
                - level: 메뉴 레벨 (1=대분류, 2=중분류, 3=소분류)
        """
        if not self.sheet:
            self.logger.warning("Google Sheets not available, skipping menu tree update")
            return False

        try:
            # Menu_tree_check_list 시트 가져오기 (없으면 생성)
            try:
                menu_sheet = self.sheet.worksheet("Menu_tree_check_list")
            except gspread.exceptions.WorksheetNotFound:
                self.logger.info("Creating Menu_tree_check_list sheet...")
                menu_sheet = self.sheet.add_worksheet(
                    title="Menu_tree_check_list", rows=200, cols=10
                )
                # 헤더 추가
                headers = [
                    "No", "Level", "Parent_Category", "Category_Name", "URL",
                    "Status", "Last_Checked", "Product_Count", "Note", "Test_Result"
                ]
                menu_sheet.update(values=[headers], range_name='A1:J1')
                self.logger.info("Menu_tree_check_list sheet created with headers")

            # 기존 데이터 확인
            existing_data = menu_sheet.get_all_records()
            existing_names = {row.get('Category_Name', ''): idx + 2 for idx, row in enumerate(existing_data)}

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_rows = []
            updated_count = 0
            new_count = 0

            for idx, cat in enumerate(categories, start=1):
                cat_name = cat.get('name', '')
                cat_url = cat.get('url', '')
                parent = cat.get('parent', '')
                level = cat.get('level', 1)

                if cat_name in existing_names:
                    # 기존 행 업데이트 (URL, Last_Checked)
                    row_num = existing_names[cat_name]
                    menu_sheet.update(values=[[cat_url]], range_name=f'E{row_num}')
                    menu_sheet.update(values=[[timestamp]], range_name=f'G{row_num}')
                    updated_count += 1
                else:
                    # 새 행 추가
                    new_row = [
                        len(existing_data) + new_count + 1,  # No
                        level,  # Level
                        parent,  # Parent_Category
                        cat_name,  # Category_Name
                        cat_url,  # URL
                        "Active",  # Status
                        timestamp,  # Last_Checked
                        "",  # Product_Count (나중에 채울 수 있음)
                        "",  # Note
                        ""  # Test_Result
                    ]
                    new_rows.append(new_row)
                    new_count += 1

            # 새 행 일괄 추가
            if new_rows:
                menu_sheet.append_rows(new_rows)
                self.logger.info(f"Added {len(new_rows)} new categories to Menu_tree_check_list")

            self.logger.info(f"Menu tree updated: {new_count} new, {updated_count} updated")
            return True

        except Exception as e:
            self.logger.error(f"Failed to update menu tree checklist: {e}")
            return False

    def get_menu_tree_categories(self) -> List[Dict]:
        """
        Menu_tree_check_list 시트에서 카테고리 정보 가져오기

        실제 시트 구조:
        A: No, B: Level, C: BigCateSeq (대분류), D: MiddleCateSeq (중분류),
        E: URL, F: Status, G: Last_Checked, H: Product_Count,
        I: Note, J: Test_Result, K: Note (오류메시지)

        Returns:
            List[Dict]: 카테고리 정보 리스트
        """
        if not self.sheet:
            self.logger.warning("Google Sheets not available")
            return []

        try:
            menu_sheet = self.sheet.worksheet("Menu_tree_check_list")

            # 모든 값을 가져와서 수동으로 딕셔너리 변환 (중복 헤더 문제 회피)
            all_values = menu_sheet.get_all_values()

            if not all_values or len(all_values) < 2:
                self.logger.warning("No data in Menu_tree_check_list")
                return []

            # 실제 시트 구조에 맞는 헤더 매핑
            fixed_headers = [
                'No', 'Level', 'BigCateSeq', 'MiddleCateSeq', 'URL',
                'Status', 'Last_Checked', 'Product_Count', 'Note',
                'Test_Result', 'Error_Message'
            ]

            # 데이터 행을 딕셔너리로 변환
            categories = []
            for row in all_values[1:]:
                if not row or not any(row):  # 빈 행 건너뛰기
                    continue
                category = {}
                for i, header in enumerate(fixed_headers):
                    value = row[i] if i < len(row) else ""
                    category[header] = value

                # Category_Name 필드 추가 (호환성을 위해)
                # MiddleCateSeq가 있으면 중분류, 없으면 대분류
                if category.get('MiddleCateSeq'):
                    category['Category_Name'] = category['MiddleCateSeq']
                else:
                    category['Category_Name'] = category['BigCateSeq']

                categories.append(category)

            self.logger.info(f"Retrieved {len(categories)} categories from Menu_tree_check_list")
            return categories

        except gspread.exceptions.WorksheetNotFound:
            self.logger.warning("Menu_tree_check_list sheet not found")
            return []
        except Exception as e:
            self.logger.error(f"Failed to get menu tree categories: {e}")
            return []

    def update_category_test_result(self, category_name: str, result: str, product_count: int = None, error_msg: str = ""):
        """
        특정 카테고리의 테스트 결과 업데이트

        실제 시트 구조:
        A: No, B: Level, C: BigCateSeq (대분류), D: MiddleCateSeq (중분류),
        E: URL, F: Status, G: Last_Checked, H: Product_Count,
        I: Note, J: Test_Result, K: Note (오류메시지)

        Args:
            category_name: 카테고리 이름 (MiddleCateSeq 또는 BigCateSeq)
            result: 테스트 결과 (Pass/Fail)
            product_count: 상품 개수 (선택)
            error_msg: 오류 메시지 (Fail 시)

        결과 기록:
            J열: Pass/Fail
            K열: 오류 메시지
        """
        if not self.sheet:
            self.logger.warning("Google Sheets not available")
            return False

        try:
            menu_sheet = self.sheet.worksheet("Menu_tree_check_list")

            # 모든 값을 가져오기
            all_values = menu_sheet.get_all_values()

            if not all_values or len(all_values) < 2:
                self.logger.warning("No data in Menu_tree_check_list")
                return False

            # 해당 카테고리 찾기 (C열: BigCateSeq, D열: MiddleCateSeq 둘 다 확인)
            for row_idx, row in enumerate(all_values[1:], start=2):
                if len(row) >= 4:
                    big_cate = row[2] if len(row) > 2 else ""   # C열
                    mid_cate = row[3] if len(row) > 3 else ""   # D열

                    # MiddleCateSeq 또는 BigCateSeq와 일치하는지 확인
                    if mid_cate == category_name or (not mid_cate and big_cate == category_name):
                        # 테스트 결과 업데이트
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                        # J열: Test_Result (Pass/Fail)
                        menu_sheet.update(values=[[result]], range_name=f'J{row_idx}')

                        # G열: Last_Checked (마지막 확인 시간)
                        menu_sheet.update(values=[[timestamp]], range_name=f'G{row_idx}')

                        # H열: Product_Count (상품 개수)
                        if product_count is not None:
                            menu_sheet.update(values=[[product_count]], range_name=f'H{row_idx}')

                        # K열: Error_Message (오류 메시지 - Fail 시)
                        menu_sheet.update(values=[[error_msg]], range_name=f'K{row_idx}')

                        self.logger.info(f"Updated test result for '{category_name}': {result}")
                        return True

            self.logger.warning(f"Category '{category_name}' not found in Menu_tree_check_list")
            return False

        except Exception as e:
            self.logger.error(f"Failed to update category test result: {e}")
            return False

    def update_scenario_status(self, tc_id: str, status: str):
        """
        TestCase_Scenarios 시트에서 특정 TC의 Automation Status 업데이트

        Args:
            tc_id: 테스트 케이스 ID (예: GS_PRODUCT_001)
            status: 상태 (Done, In Progress, Pending)

        Returns:
            bool: 업데이트 성공 여부
        """
        if not self.sheet:
            self.logger.warning("Google Sheets not available")
            return False

        try:
            scenarios_sheet = self.sheet.worksheet("TestCase_Scenarios")

            # 모든 값을 가져오기
            all_values = scenarios_sheet.get_all_values()

            if not all_values or len(all_values) < 2:
                self.logger.warning("No data in TestCase_Scenarios")
                return False

            # TC ID 찾기 (A열)
            for row_idx, row in enumerate(all_values[1:], start=2):
                if len(row) > 0 and row[0] == tc_id:
                    # I열(Automation Status) 업데이트 (0-indexed = 8, 1-indexed = I)
                    scenarios_sheet.update(values=[[status]], range_name=f'I{row_idx}')
                    self.logger.info(f"Updated scenario status for '{tc_id}': {status}")
                    return True

            self.logger.warning(f"TC ID '{tc_id}' not found in TestCase_Scenarios")
            return False

        except gspread.exceptions.WorksheetNotFound:
            self.logger.warning("TestCase_Scenarios sheet not found")
            return False
        except Exception as e:
            self.logger.error(f"Failed to update scenario status: {e}")
            return False

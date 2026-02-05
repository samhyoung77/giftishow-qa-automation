"""
Giftishow Test Results Google Sheets 템플릿 생성 스크립트 (수정 버전)
gspread 최신 버전 호환
"""
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import sys
import os
from datetime import datetime

# 프로젝트 루트 경로 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.config import Config


def set_column_widths(sheet, worksheet, column_widths):
    """컬럼 너비 일괄 설정"""
    try:
        requests = []
        for col_idx, width in column_widths:
            requests.append({
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": worksheet.id,
                        "dimension": "COLUMNS",
                        "startIndex": col_idx,
                        "endIndex": col_idx + 1
                    },
                    "properties": {
                        "pixelSize": width
                    },
                    "fields": "pixelSize"
                }
            })

        if requests:
            sheet.batch_update({"requests": requests})
            print("  - 컬럼 너비 조정 완료")
    except Exception as e:
        print(f"  - 컬럼 너비 조정 건너뜀: {e}")


def create_giftishow_test_sheets():
    """Giftishow Test Results Google Sheets 템플릿 생성"""

    print("=" * 60)
    print("Giftishow Test Results - Google Sheets 템플릿 생성")
    print("=" * 60)

    # Google Sheets API 인증
    print("\n[1/5] Google Sheets API 인증 중...")
    try:
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            Config.GOOGLE_CREDENTIALS_PATH, scope
        )
        client = gspread.authorize(creds)
        print("✓ 인증 성공")
    except Exception as e:
        print(f"✗ 인증 실패: {e}")
        return

    # Spreadsheet 열기
    print(f"\n[2/5] Spreadsheet 열기...")
    try:
        sheet = client.open_by_url(Config.GOOGLE_SHEET_URL)
        print(f"✓ '{sheet.title}' 열기 성공")
    except Exception as e:
        print(f"✗ Spreadsheet 열기 실패: {e}")
        return

    # 1. TestCase_Template 시트 생성
    print("\n[3/5] TestCase_Template 시트 생성 중...")
    try:
        try:
            old_sheet = sheet.worksheet("TestCase_Template")
            sheet.del_worksheet(old_sheet)
            print("  - 기존 시트 삭제됨")
        except:
            pass

        testcase_sheet = sheet.add_worksheet(
            title="TestCase_Template",
            rows=100,
            cols=10
        )

        headers = [
            "TC ID", "Category", "Scenario Name", "Pre-condition",
            "Test Steps", "Locators (ID/XPath/CSS)", "Expected Result",
            "Priority", "Automation Status", "Note"
        ]
        testcase_sheet.update(values=[headers], range_name='A1:J1')

        testcase_sheet.format('A1:J1', {
            'textFormat': {'bold': True},
            'backgroundColor': {'red': 0.2, 'green': 0.6, 'blue': 0.8},
            'horizontalAlignment': 'CENTER'
        })

        sample_data = [
            ["GS_LOGIN_001", "Authentication", "정상 로그인",
             "1. 유효한 테스트 계정 존재\n2. 로그인 페이지 접근 가능",
             "1. 로그인 페이지 접속\n2. ID 입력\n3. 비밀번호 입력\n4. 로그인 버튼 클릭\n5. 메인 페이지 이동 확인",
             "id: username\nid: password\nid: login_btn",
             "메인 페이지로 이동 완료", "High", "✅ Done", "기본 로그인 플로우"],
            ["GS_LOGIN_002", "Authentication", "잘못된 비밀번호 로그인",
             "1. 유효한 계정 ID 존재\n2. 로그인 페이지 접근 가능",
             "1. 로그인 페이지 접속\n2. 유효한 ID 입력\n3. 잘못된 비밀번호 입력\n4. 로그인 버튼 클릭\n5. 에러 메시지 확인",
             "id: username\nid: password\nid: login_btn\nclass: error-message",
             "'비밀번호가 일치하지 않습니다' 에러 메시지 표시", "High", "✅ Done", "네거티브 테스트"],
            ["GS_PRODUCT_001", "Product", "상품 검색",
             "1. 로그인 완료\n2. 메인 페이지 접속",
             "1. 검색창에 상품명 입력\n2. 검색 버튼 클릭\n3. 검색 결과 확인",
             "id: search_input\nid: search_btn\nclass: product-list",
             "검색 결과 목록 표시", "Medium", "In Progress", ""],
        ]
        testcase_sheet.update(values=sample_data, range_name='A2:J4')

        # 컬럼 너비
        set_column_widths(sheet, testcase_sheet, [
            (0, 150), (1, 120), (2, 200), (3, 250), (4, 300),
            (5, 250), (6, 250), (7, 100), (8, 150), (9, 200)
        ])

        print("✓ TestCase_Template 시트 생성 완료")

    except Exception as e:
        print(f"✗ TestCase_Template 시트 생성 실패: {e}")

    # 2. TestResults 시트 생성
    print("\n[4/5] TestResults 시트 생성 중...")
    try:
        try:
            old_sheet = sheet.worksheet("TestResults")
            sheet.del_worksheet(old_sheet)
        except:
            pass

        results_sheet = sheet.add_worksheet(title="TestResults", rows=1000, cols=20)

        headers = [
            "Timestamp", "Test Run ID", "TC ID", "Page", "Category", "Scenario Name",
            "Browser", "OS", "Login", "Product Search", "Product Detail", "Cart",
            "Order", "Overall Result", "Error Message", "Duration (sec)",
            "Screenshot URL", "Tester", "Environment", "Comment"
        ]
        results_sheet.update(values=[headers], range_name='A1:T1')

        results_sheet.format('A1:T1', {
            'textFormat': {'bold': True},
            'backgroundColor': {'red': 0.2, 'green': 0.8, 'blue': 0.6},
            'horizontalAlignment': 'CENTER'
        })

        sample_results = [
            [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "RUN_20260203_001", "GS_LOGIN_001",
             "Login Page", "Authentication", "정상 로그인", "Chrome 120.0", "Windows 11",
             "PASS", "N/A", "N/A", "N/A", "N/A", "PASS", "", "3.24", "",
             "Automation", "Production", ""]
        ]
        results_sheet.update(values=sample_results, range_name='A2:T2')

        set_column_widths(sheet, results_sheet, [
            (0, 150), (1, 150), (2, 150), (14, 300)
        ])

        print("✓ TestResults 시트 생성 완료")

    except Exception as e:
        print(f"✗ TestResults 시트 생성 실패: {e}")

    # 3. TestSummary 시트 생성
    print("\n[5/5] TestSummary 시트 생성 중...")
    try:
        try:
            old_sheet = sheet.worksheet("TestSummary")
            sheet.del_worksheet(old_sheet)
        except:
            pass

        summary_sheet = sheet.add_worksheet(title="TestSummary", rows=50, cols=10)

        summary_sheet.update(values=[["Giftishow Test Summary Dashboard"]], range_name='A1:J1')
        summary_sheet.merge_cells('A1:J1')
        summary_sheet.format('A1', {
            'textFormat': {'bold': True, 'fontSize': 16},
            'backgroundColor': {'red': 0.2, 'green': 0.6, 'blue': 0.8},
            'horizontalAlignment': 'CENTER'
        })

        summary_sheet.update(values=[["Overall Summary", ""]], range_name='A3:B3')
        summary_sheet.format('A3:B3', {
            'textFormat': {'bold': True, 'fontSize': 12},
            'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
        })

        summary_headers = ["Last Updated", "Total Tests", "Pass Count", "Fail Count", "Pass Rate", "Trend"]
        summary_sheet.update(values=[summary_headers], range_name='A4:F4')
        summary_sheet.format('A4:F4', {
            'textFormat': {'bold': True},
            'backgroundColor': {'red': 0.8, 'green': 0.8, 'blue': 0.8},
            'horizontalAlignment': 'CENTER'
        })

        summary_sheet.update(values=[[
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "1", "1", "0", "100.0%"
        ]], range_name='A5:E5')

        set_column_widths(sheet, summary_sheet, [(0, 150), (5, 150), (8, 300)])

        print("✓ TestSummary 시트 생성 완료")

    except Exception as e:
        print(f"✗ TestSummary 시트 생성 실패: {e}")

    # 4. DailyTrend 시트 생성
    print("\n[보너스] DailyTrend 시트 생성 중...")
    try:
        try:
            old_sheet = sheet.worksheet("DailyTrend")
            sheet.del_worksheet(old_sheet)
        except:
            pass

        trend_sheet = sheet.add_worksheet(title="DailyTrend", rows=365, cols=5)

        headers = ["Date", "Total", "Pass", "Fail", "Pass Rate"]
        trend_sheet.update(values=[headers], range_name='A1:E1')
        trend_sheet.format('A1:E1', {
            'textFormat': {'bold': True},
            'backgroundColor': {'red': 0.2, 'green': 0.8, 'blue': 0.6},
            'horizontalAlignment': 'CENTER'
        })

        print("✓ DailyTrend 시트 생성 완료")

    except Exception as e:
        print(f"✗ DailyTrend 시트 생성 실패: {e}")

    print("\n" + "=" * 60)
    print("✓ 모든 시트 생성 완료!")
    print("=" * 60)
    print(f"\nGoogle Sheets URL:")
    print(Config.GOOGLE_SHEET_URL)
    print("\n생성된 시트:")
    print("  1. TestCase_Template - 테스트 케이스 정의 (3개 샘플)")
    print("  2. TestResults - 실행 결과 기록 (1개 샘플)")
    print("  3. TestSummary - 대시보드")
    print("  4. DailyTrend - 일별 트렌드")
    print("=" * 60)


if __name__ == "__main__":
    create_giftishow_test_sheets()

"""
기프티쇼 테스트 시나리오를 Google Sheets에 업로드하는 스크립트
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.config import Config
from utils.google_sheets import GoogleSheetsReporter


def upload_giftishow_scenarios():
    """기프티쇼 테스트 시나리오 업로드"""

    print("=" * 80)
    print("기프티쇼 테스트 시나리오 업로드")
    print("=" * 80)

    # Google Sheets 연결
    print("\n[1/3] Google Sheets 연결 중...")
    try:
        reporter = GoogleSheetsReporter(
            sheet_url=Config.GOOGLE_SHEET_URL,
            credentials_path=Config.GOOGLE_CREDENTIALS_PATH
        )

        if not reporter.sheet:
            print("✗ Google Sheets 연결 실패")
            return

        print("✓ Google Sheets 연결 성공")
    except Exception as e:
        print(f"✗ 연결 실패: {e}")
        return

    # TestCase_Scenarios 시트 가져오기
    print("\n[2/3] TestCase_Scenarios 시트 준비 중...")
    try:
        # 기존 시트 삭제 후 재생성
        try:
            old_sheet = reporter.sheet.worksheet("TestCase_Scenarios")
            reporter.sheet.del_worksheet(old_sheet)
            print("  - 기존 시트 삭제")
        except:
            pass

        # 새 시트 생성
        scenarios_sheet = reporter.sheet.add_worksheet(
            title="TestCase_Scenarios",
            rows=100,
            cols=10
        )

        # 헤더 설정
        headers = [
            "TC ID",
            "Category",
            "Scenario Name",
            "Pre-condition",
            "Test Steps",
            "Locators (ID/XPath/CSS)",
            "Expected Result",
            "Priority",
            "Automation Status",
            "Note"
        ]
        scenarios_sheet.update(values=[headers], range_name='A1:J1')

        # 헤더 서식
        scenarios_sheet.format('A1:J1', {
            'textFormat': {'bold': True, 'fontSize': 11},
            'backgroundColor': {'red': 0.2, 'green': 0.6, 'blue': 0.8},
            'horizontalAlignment': 'CENTER',
            'verticalAlignment': 'MIDDLE'
        })

        print("✓ TestCase_Scenarios 시트 생성 완료")

    except Exception as e:
        print(f"✗ 시트 생성 실패: {e}")
        return

    # 테스트 시나리오 데이터
    print("\n[3/3] 테스트 시나리오 업로드 중...")

    scenarios = [
        # ========== 1. Authentication (로그인/인증) ==========
        [
            "GS_AUTH_001",
            "Authentication",
            "정상 로그인",
            "1. 유효한 기업 계정이 존재함\n2. 로그인 페이지 접근 가능\n3. 브라우저 쿠키 삭제됨",
            "1. 로그인 페이지 접속\n2. 사용자 ID 입력\n3. 비밀번호 입력\n4. 로그인 버튼 클릭\n5. 메인 페이지 이동 확인",
            "id: user_id\nid: password\nid: login_btn\nclass: main-container",
            "메인 페이지로 리다이렉트\n환영 메시지 또는 사용자명 표시",
            "High",
            "✅ Done",
            "가장 기본적인 로그인 플로우"
        ],
        [
            "GS_AUTH_002",
            "Authentication",
            "잘못된 비밀번호 로그인",
            "1. 유효한 계정 ID 존재\n2. 로그인 페이지 접근 가능",
            "1. 로그인 페이지 접속\n2. 유효한 ID 입력\n3. 잘못된 비밀번호 입력\n4. 로그인 버튼 클릭\n5. 에러 메시지 확인",
            "id: user_id\nid: password\nid: login_btn\nclass: error-message",
            "에러 메시지 표시: '아이디 또는 비밀번호가 일치하지 않습니다'\n로그인 페이지 유지",
            "High",
            "✅ Done",
            "네거티브 테스트 - 보안"
        ],
        [
            "GS_AUTH_003",
            "Authentication",
            "빈 필드로 로그인 시도",
            "1. 로그인 페이지 접근 가능",
            "1. 로그인 페이지 접속\n2. ID와 비밀번호를 입력하지 않음\n3. 로그인 버튼 클릭\n4. 에러 메시지 확인",
            "id: user_id\nid: password\nid: login_btn\nclass: validation-error",
            "필수 입력 항목 에러 메시지 표시\n로그인 진행 안 됨",
            "Medium",
            "In Progress",
            "필드 유효성 검사"
        ],
        [
            "GS_AUTH_004",
            "Authentication",
            "로그아웃",
            "1. 로그인 완료 상태\n2. 메인 페이지 또는 서브 페이지 접속",
            "1. 로그아웃 버튼 또는 메뉴 클릭\n2. 로그아웃 확인\n3. 로그인 페이지로 리다이렉트 확인",
            "id: logout_btn\nclass: logout-link",
            "로그인 페이지로 이동\n세션 종료됨\n이전 페이지 접근 시 로그인 요구",
            "High",
            "In Progress",
            "세션 관리"
        ],
        [
            "GS_AUTH_005",
            "Authentication",
            "세션 만료 후 재접속",
            "1. 로그인 완료 상태\n2. 일정 시간 비활성 상태 유지",
            "1. 로그인 후 30분 이상 비활성\n2. 페이지 새로고침 또는 새 작업 시도\n3. 세션 만료 메시지 확인\n4. 로그인 페이지 리다이렉트 확인",
            "class: session-expired-msg",
            "세션 만료 메시지 표시\n로그인 페이지로 자동 이동",
            "Medium",
            "Pending",
            "보안 - 세션 타임아웃"
        ],

        # ========== 2. Product (상품 검색/조회) ==========
        [
            "GS_PRODUCT_001",
            "Product",
            "상품 카테고리 조회",
            "1. 로그인 완료\n2. 메인 페이지 또는 상품 목록 페이지 접속",
            "1. 상품 카테고리 메뉴 클릭 (예: 커피/음료)\n2. 해당 카테고리 상품 목록 표시 확인\n3. 상품 이미지 및 정보 표시 확인",
            "class: category-menu\nclass: product-list\nclass: product-item",
            "선택한 카테고리의 상품만 표시\n각 상품의 이름, 이미지, 가격 표시",
            "High",
            "In Progress",
            "카테고리: 커피/음료, 편의점, 외식, 베이커리 등"
        ],
        [
            "GS_PRODUCT_002",
            "Product",
            "상품 검색 - 키워드",
            "1. 로그인 완료\n2. 상품 목록 페이지 또는 메인 페이지 접속",
            "1. 검색창에 키워드 입력 (예: 스타벅스)\n2. 검색 버튼 클릭 또는 Enter\n3. 검색 결과 확인",
            "id: search_input\nid: search_btn\nclass: search-results",
            "키워드와 관련된 상품 목록 표시\n검색어 하이라이트 또는 표시\n결과 없을 시 '검색 결과가 없습니다' 메시지",
            "High",
            "In Progress",
            "검색 기능"
        ],
        [
            "GS_PRODUCT_003",
            "Product",
            "상품 상세 조회",
            "1. 로그인 완료\n2. 상품 목록 페이지 접속",
            "1. 상품 목록에서 특정 상품 클릭\n2. 상품 상세 페이지 이동 확인\n3. 상세 정보 표시 확인",
            "class: product-item\nclass: product-detail\nclass: product-info",
            "상품 상세 정보 표시:\n- 상품명, 이미지, 가격\n- 상품 설명\n- 사용 조건\n- 유효기간",
            "High",
            "In Progress",
            "상세 페이지 필수 정보"
        ],
        [
            "GS_PRODUCT_004",
            "Product",
            "상품 필터링 - 가격대",
            "1. 로그인 완료\n2. 상품 목록 페이지 접속",
            "1. 가격 필터 옵션 선택 (예: 5,000원 이하)\n2. 필터 적용 버튼 클릭\n3. 필터링된 결과 확인",
            "class: price-filter\nid: apply_filter_btn\nclass: filtered-results",
            "선택한 가격대의 상품만 표시\n필터 조건이 화면에 표시됨",
            "Medium",
            "Pending",
            "필터링 기능"
        ],
        [
            "GS_PRODUCT_005",
            "Product",
            "인기 상품 조회",
            "1. 로그인 완료\n2. 메인 페이지 접속",
            "1. 인기 상품 섹션 확인\n2. '인기 상품 더보기' 클릭 (있을 경우)\n3. 인기 상품 목록 표시 확인",
            "class: popular-products\nclass: product-ranking",
            "인기 순위 또는 추천 상품 표시\n상품별 순위 또는 태그 표시",
            "Low",
            "Pending",
            "추천/인기 상품"
        ],

        # ========== 3. Cart (장바구니) ==========
        [
            "GS_CART_001",
            "Cart",
            "장바구니에 상품 추가",
            "1. 로그인 완료\n2. 상품 상세 페이지 접속",
            "1. 수량 선택 (예: 10개)\n2. 장바구니 추가 버튼 클릭\n3. 장바구니 카운트 증가 확인\n4. 성공 메시지 확인",
            "id: quantity_input\nid: add_to_cart_btn\nclass: cart-badge\nclass: success-message",
            "장바구니 아이콘에 수량 표시 증가\n성공 메시지: '장바구니에 추가되었습니다'\n상품 상세 페이지 유지",
            "High",
            "Pending",
            "기본 장바구니 기능"
        ],
        [
            "GS_CART_002",
            "Cart",
            "장바구니 페이지 조회",
            "1. 로그인 완료\n2. 장바구니에 상품 1개 이상 존재",
            "1. 장바구니 아이콘 또는 메뉴 클릭\n2. 장바구니 페이지 이동\n3. 담긴 상품 목록 확인",
            "id: cart_icon\nclass: cart-page\nclass: cart-items",
            "장바구니에 담긴 상품 목록 표시:\n- 상품명, 이미지, 가격\n- 수량\n- 소계\n- 총 합계",
            "High",
            "Pending",
            "장바구니 목록"
        ],
        [
            "GS_CART_003",
            "Cart",
            "장바구니에서 수량 변경",
            "1. 로그인 완료\n2. 장바구니에 상품 존재\n3. 장바구니 페이지 접속",
            "1. 상품 수량 증가 버튼 클릭\n2. 수량 변경 확인\n3. 총 금액 재계산 확인",
            "class: quantity-increase\nclass: quantity-decrease\nclass: item-subtotal\nclass: total-amount",
            "수량 변경 즉시 반영\n소계 및 총 금액 자동 재계산\n변경 사항 저장됨",
            "Medium",
            "Pending",
            "수량 조절"
        ],
        [
            "GS_CART_004",
            "Cart",
            "장바구니에서 상품 삭제",
            "1. 로그인 완료\n2. 장바구니에 상품 2개 이상 존재\n3. 장바구니 페이지 접속",
            "1. 특정 상품의 삭제 버튼 클릭\n2. 삭제 확인 (팝업 있을 경우 확인)\n3. 상품 목록에서 제거 확인\n4. 총 금액 재계산 확인",
            "class: remove-item-btn\nclass: confirm-delete\nclass: cart-items",
            "선택한 상품이 장바구니에서 제거됨\n총 금액 재계산\n장바구니 카운트 감소",
            "Medium",
            "Pending",
            "상품 삭제"
        ],
        [
            "GS_CART_005",
            "Cart",
            "빈 장바구니 확인",
            "1. 로그인 완료\n2. 장바구니에 상품이 없는 상태",
            "1. 장바구니 아이콘 클릭\n2. 빈 장바구니 메시지 확인",
            "id: cart_icon\nclass: empty-cart-message",
            "'장바구니가 비어있습니다' 메시지 표시\n쇼핑 계속하기 버튼 또는 링크 표시",
            "Low",
            "Pending",
            "빈 상태 처리"
        ],

        # ========== 4. Order (주문/결제) ==========
        [
            "GS_ORDER_001",
            "Order",
            "주문서 작성 - 기본 정보",
            "1. 로그인 완료\n2. 장바구니에 상품 존재\n3. 장바구니 페이지 접속",
            "1. 주문하기 버튼 클릭\n2. 주문서 페이지 이동\n3. 주문 정보 입력:\n   - 받는 사람 이름\n   - 연락처\n   - 발송 메시지\n4. 다음 단계 진행",
            "id: checkout_btn\nid: recipient_name\nid: recipient_phone\nid: message_input",
            "주문서 페이지 표시\n입력 필드 정상 작동\n필수 항목 표시",
            "High",
            "Pending",
            "주문서 작성"
        ],
        [
            "GS_ORDER_002",
            "Order",
            "주문서 작성 - 대량 발송",
            "1. 로그인 완료\n2. 장바구니에 대량 상품 존재 (10개 이상)\n3. 주문서 페이지 접속",
            "1. 대량 발송 옵션 선택\n2. 엑셀 파일 업로드 또는 수동 입력\n3. 발송 대상 목록 확인\n4. 발송 정보 검증",
            "id: bulk_send_option\nid: excel_upload\nclass: recipient-list",
            "대량 발송 옵션 표시\n엑셀 양식 다운로드 가능\n수신자 목록 미리보기",
            "High",
            "Pending",
            "B2B 핵심 기능"
        ],
        [
            "GS_ORDER_003",
            "Order",
            "결제 수단 선택",
            "1. 로그인 완료\n2. 주문서 작성 완료\n3. 결제 단계 진입",
            "1. 결제 수단 선택 (신용카드/계좌이체/무통장입금)\n2. 결제 정보 입력\n3. 결제 진행",
            "class: payment-method\nid: credit_card_option\nid: bank_transfer_option",
            "선택한 결제 수단 활성화\n필요 정보 입력 필드 표시\nKCP 결제 연동 확인",
            "High",
            "Pending",
            "결제 연동 필요"
        ],
        [
            "GS_ORDER_004",
            "Order",
            "주문 완료 확인",
            "1. 로그인 완료\n2. 결제 완료 (또는 테스트 결제)",
            "1. 결제 완료 페이지 이동 확인\n2. 주문 번호 표시 확인\n3. 주문 내역 페이지 링크 확인\n4. 이메일 또는 SMS 발송 확인 (선택)",
            "class: order-complete\nclass: order-number\nid: view_order_btn",
            "주문 완료 메시지 표시\n주문 번호 발급\n주문 내역 조회 가능",
            "High",
            "Pending",
            "주문 완료 프로세스"
        ],
        [
            "GS_ORDER_005",
            "Order",
            "주문 내역 조회",
            "1. 로그인 완료\n2. 과거 주문 1건 이상 존재",
            "1. 마이페이지 또는 주문 내역 메뉴 클릭\n2. 주문 내역 목록 확인\n3. 특정 주문 클릭하여 상세 조회",
            "id: my_page\nclass: order-history\nclass: order-detail",
            "주문 목록 표시:\n- 주문 번호\n- 주문 일자\n- 상품명\n- 금액\n- 상태",
            "Medium",
            "Pending",
            "주문 관리"
        ],

        # ========== 5. MyPage (마이페이지/계정 관리) ==========
        [
            "GS_MYPAGE_001",
            "MyPage",
            "회원 정보 조회",
            "1. 로그인 완료",
            "1. 마이페이지 메뉴 클릭\n2. 회원 정보 페이지 이동\n3. 계정 정보 확인",
            "id: mypage_menu\nclass: account-info",
            "회원 정보 표시:\n- 회사명\n- 담당자명\n- 이메일\n- 연락처",
            "Medium",
            "Pending",
            "계정 정보"
        ],
        [
            "GS_MYPAGE_002",
            "MyPage",
            "회원 정보 수정",
            "1. 로그인 완료\n2. 마이페이지 접속",
            "1. 회원 정보 수정 버튼 클릭\n2. 변경할 정보 입력 (예: 연락처)\n3. 저장 버튼 클릭\n4. 변경 완료 메시지 확인",
            "id: edit_profile_btn\nid: phone_number\nid: save_btn",
            "정보 수정 성공 메시지 표시\n변경된 정보 즉시 반영",
            "Medium",
            "Pending",
            "정보 수정"
        ],
        [
            "GS_MYPAGE_003",
            "MyPage",
            "비밀번호 변경",
            "1. 로그인 완료\n2. 마이페이지 접속",
            "1. 비밀번호 변경 메뉴 클릭\n2. 현재 비밀번호 입력\n3. 새 비밀번호 입력\n4. 새 비밀번호 확인 입력\n5. 변경 버튼 클릭",
            "id: change_password_menu\nid: current_password\nid: new_password\nid: confirm_password",
            "비밀번호 변경 성공 메시지\n재로그인 요구 또는 세션 유지",
            "Medium",
            "Pending",
            "보안 - 비밀번호 관리"
        ],
        [
            "GS_MYPAGE_004",
            "MyPage",
            "포인트/쿠폰 조회",
            "1. 로그인 완료\n2. 마이페이지 접속",
            "1. 포인트/쿠폰 메뉴 클릭\n2. 보유 포인트 확인\n3. 사용 가능한 쿠폰 확인",
            "id: points_menu\nclass: point-balance\nclass: coupon-list",
            "보유 포인트 표시\n사용 가능 쿠폰 목록 표시\n유효기간 표시",
            "Low",
            "Pending",
            "포인트/쿠폰 시스템"
        ],

        # ========== 6. E2E (End-to-End 시나리오) ==========
        [
            "GS_E2E_001",
            "E2E",
            "상품 구매 전체 플로우",
            "1. 유효한 계정 존재\n2. 브라우저 쿠키 삭제\n3. 테스트 결제 환경 설정",
            "1. 로그인\n2. 상품 검색\n3. 상품 상세 조회\n4. 장바구니 추가\n5. 장바구니 확인\n6. 주문서 작성\n7. 결제 (테스트)\n8. 주문 완료 확인\n9. 주문 내역 조회\n10. 로그아웃",
            "모든 페이지의 주요 locator 포함",
            "전체 구매 플로우 정상 완료\n각 단계별 페이지 전환 정상\n주문 번호 발급 및 내역 저장",
            "High",
            "Pending",
            "전체 플로우 통합 테스트"
        ],
        [
            "GS_E2E_002",
            "E2E",
            "대량 쿠폰 발송 전체 플로우",
            "1. 로그인 완료\n2. 대량 발송용 엑셀 파일 준비",
            "1. 로그인\n2. 대량 발송 상품 선택\n3. 장바구니 추가\n4. 주문서 작성 (대량 발송 옵션)\n5. 엑셀 파일 업로드\n6. 발송 대상 확인\n7. 결제\n8. 발송 완료 확인",
            "모든 대량 발송 관련 locator",
            "대량 발송 프로세스 정상 완료\n모든 수신자에게 발송 완료\n발송 내역 확인 가능",
            "High",
            "Pending",
            "B2B 핵심 E2E 시나리오"
        ],
        [
            "GS_E2E_003",
            "E2E",
            "재구매 시나리오",
            "1. 로그인 완료\n2. 과거 주문 내역 존재",
            "1. 로그인\n2. 주문 내역 조회\n3. 과거 주문 상품 다시 담기\n4. 장바구니 확인\n5. 주문 진행\n6. 결제\n7. 완료",
            "class: reorder-btn\nclass: order-history",
            "과거 주문 상품 재주문 가능\n장바구니에 정상 추가\n결제 완료",
            "Medium",
            "Pending",
            "재구매 편의성"
        ]
    ]

    try:
        # 시나리오 업로드
        scenarios_sheet.update(values=scenarios, range_name=f'A2:J{len(scenarios) + 1}')

        # 컬럼 너비 조정 (batch_update 사용)
        try:
            requests = []
            # 컬럼 너비 설정
            column_widths = [
                (0, 150),   # A: TC ID
                (1, 120),   # B: Category
                (2, 220),   # C: Scenario Name
                (3, 280),   # D: Pre-condition
                (4, 350),   # E: Test Steps
                (5, 250),   # F: Locators
                (6, 280),   # G: Expected Result
                (7, 90),    # H: Priority
                (8, 150),   # I: Automation Status
                (9, 200),   # J: Note
            ]

            for col_idx, width in column_widths:
                requests.append({
                    "updateDimensionProperties": {
                        "range": {
                            "sheetId": scenarios_sheet.id,
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

            reporter.sheet.batch_update({"requests": requests})
            print("  - 컬럼 너비 조정 완료")
        except Exception as e:
            print(f"  - 컬럼 너비 조정 건너뜀: {e}")

        # 필터 설정
        try:
            scenarios_sheet.set_basic_filter()
            print("  - 필터 설정 완료")
        except Exception as e:
            print(f"  - 필터 설정 건너뜀: {e}")

        print(f"✓ {len(scenarios)}개 테스트 시나리오 업로드 완료")

        # 카테고리별 통계
        categories = {}
        for scenario in scenarios:
            category = scenario[1]
            categories[category] = categories.get(category, 0) + 1

        print("\n카테고리별 시나리오 수:")
        for category, count in sorted(categories.items()):
            print(f"  - {category}: {count}건")

        print("\n우선순위별 시나리오 수:")
        priorities = {}
        for scenario in scenarios:
            priority = scenario[7]
            priorities[priority] = priorities.get(priority, 0) + 1

        for priority, count in sorted(priorities.items()):
            print(f"  - {priority}: {count}건")

        print("\n자동화 상태별:")
        statuses = {}
        for scenario in scenarios:
            status = scenario[8]
            statuses[status] = statuses.get(status, 0) + 1

        for status, count in sorted(statuses.items()):
            print(f"  - {status}: {count}건")

    except Exception as e:
        print(f"✗ 시나리오 업로드 실패: {e}")
        return

    print("\n" + "=" * 80)
    print("✓ 업로드 완료!")
    print("=" * 80)
    print(f"\nGoogle Sheets URL:")
    print(Config.GOOGLE_SHEET_URL)
    print("\n다음 단계:")
    print("  1. Google Sheets에서 시나리오 확인")
    print("  2. 필요 시 시나리오 수정/추가")
    print("  3. 우선순위 High 시나리오부터 자동화 구현")
    print("=" * 80)


if __name__ == "__main__":
    upload_giftishow_scenarios()

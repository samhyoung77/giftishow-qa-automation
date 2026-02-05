"""
수동 로그인 스크립트
2단계 인증(카카오톡 인증)을 포함한 수동 로그인 후 쿠키 저장

사용법:
1. 이 스크립트 실행: python manual_login.py
2. 브라우저가 열리면 로그인 진행 (카카오톡 인증 포함)
3. 로그인 완료 후 Enter 키 입력
4. 쿠키가 자동 저장됨
5. 이후 모든 테스트에서 이 쿠키 사용
"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as uc
from utils.cookie_manager import CookieManager
from utils.config import Config
import time
import sys
import io

# Windows 인코딩 문제 해결
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def manual_login():
    """수동 로그인 프로세스"""

    print("=" * 80)
    print("기프티쇼 수동 로그인 - 쿠키 저장")
    print("=" * 80)
    print()
    print("이 스크립트는 다음 작업을 수행합니다:")
    print("1. Chrome 브라우저를 엽니다")
    print("2. 기프티쇼 로그인 페이지로 이동합니다")
    print("3. 직접 로그인하세요 (카카오톡 2단계 인증 포함)")
    print("4. 로그인 완료 후 이 창에서 Enter를 누르세요")
    print("5. 세션 쿠키가 자동으로 저장됩니다")
    print()
    print("=" * 80)
    input("\n계속하려면 Enter 키를 누르세요...")

    cookie_manager = CookieManager()
    driver = None

    try:
        print("\n[1/5] Chrome 브라우저 실행 중...")

        # undetected_chromedriver 사용 (Akamai 우회)
        options = uc.ChromeOptions()
        options.add_argument('--start-maximized')

        # headless 모드 비활성화 (수동 로그인을 위해)
        # options.add_argument('--headless')

        try:
            driver = uc.Chrome(options=options, use_subprocess=True)

            # 타임아웃을 길게 설정 (카카오톡 인증 대기용)
            driver.set_page_load_timeout(180)  # 3분

            print("✓ 브라우저 실행 완료")
            print("  (페이지 로드 타임아웃: 3분)")
        except Exception as e:
            print(f"❌ 브라우저 실행 실패: {e}")
            print("\n문제 해결:")
            print("  1. Chrome 브라우저가 설치되어 있는지 확인")
            print("  2. 다른 Chrome 창을 모두 닫고 다시 시도")
            print("  3. 관리자 권한으로 실행")
            raise

        print("\n[2/5] 로그인 페이지 접속 중...")
        login_url = "https://biz.giftishow.com/login"

        try:
            driver.get(login_url)
            time.sleep(3)
            print(f"✓ 로그인 페이지 로드 완료: {login_url}")
        except Exception as e:
            print(f"⚠️  페이지 로드 타임아웃: {e}")
            print("  Akamai Bot Manager가 차단했을 수 있습니다.")
            print("  브라우저 창을 확인하세요...")
            print("  로그인 페이지가 보이면 계속 진행하세요.")

        print("\n" + "=" * 80)
        print("✋ 중요: 브라우저 창에서 직접 로그인하세요!")
        print("=" * 80)
        print()
        print("로그인 절차:")
        print("  1. 아이디/이메일 입력")
        print("  2. 비밀번호 입력")
        print("  3. 로그인 버튼 클릭")
        print("  4. 📱 카카오톡에서 인증번호 확인 (최대 5분 대기)")
        print("  5. 인증번호 입력")
        print("  6. 로그인 완료!")
        print()
        print("⏰ 충분한 시간을 드립니다:")
        print("   - 카카오톡 알림 확인")
        print("   - 인증번호 입력")
        print("   - 로그인 완료 및 메인 페이지 로드")
        print()
        print("로그인이 완료되고 메인 페이지로 이동하면,")
        print("이 창으로 돌아와서 Enter 키를 눌러주세요.")
        print()
        print("💡 팁: 천천히 진행하셔도 됩니다. 시간 제한 없습니다!")
        print("=" * 80)

        input("\n✅ 로그인 완료 후 Enter 키를 누르세요...")

        print("\n[3/5] 로그인 상태 확인 중...")

        # 페이지가 완전히 로드될 때까지 대기
        print("페이지 로딩 대기 중... (최대 10초)")
        time.sleep(10)

        # JavaScript 실행이 완료될 때까지 추가 대기
        try:
            driver.execute_script("return document.readyState")
            print("✓ 페이지 로드 완료")
        except Exception as e:
            print(f"페이지 상태 확인 중 에러 (무시됨): {e}")

        current_url = driver.current_url
        page_title = driver.title
        print(f"현재 URL: {current_url}")
        print(f"페이지 제목: {page_title}")

        # 스크린샷 저장
        try:
            import os
            os.makedirs("reports/screenshots", exist_ok=True)
            screenshot_path = "reports/screenshots/manual_login_before_save.png"
            driver.save_screenshot(screenshot_path)
            print(f"스크린샷 저장: {screenshot_path}")
        except Exception as e:
            print(f"스크린샷 저장 실패: {e}")

        if "login" in current_url.lower():
            print("\n" + "=" * 80)
            print("⚠️  경고: 아직 로그인 페이지에 있는 것 같습니다!")
            print("=" * 80)
            print()
            print("가능한 원인:")
            print("  1. 로그인 버튼을 클릭하지 않았습니다")
            print("  2. ID/PW가 틀렸습니다")
            print("  3. 카카오톡 인증을 완료하지 않았습니다")
            print("  4. Akamai Bot Manager가 차단했습니다")
            print()
            print("해결 방법:")
            print("  - 브라우저 창을 확인하세요")
            print("  - 로그인이 완료되고 메인 페이지로 이동했는지 확인하세요")
            print("  - Akamai 로딩 화면이 나오면 잠시 기다리세요")
            print()
            print("=" * 80)

            proceed = input("\n그래도 계속하시겠습니까? (y/N): ")
            if proceed.lower() != 'y':
                print("\n❌ 취소됨. 다시 시도해주세요.")
                print("\n💡 팁:")
                print("  1. 브라우저에서 완전히 로그인 완료")
                print("  2. 메인 페이지 (또는 대시보드)로 이동 확인")
                print("  3. 그 다음에 Enter 키를 누르세요")
                return
        else:
            print()
            print("=" * 80)
            print("✅ 로그인 완료 확인!")
            print("=" * 80)
            print(f"URL이 변경되었습니다: {current_url}")
            print("로그인 페이지가 아닌 다른 페이지에 있습니다.")
            print("=" * 80)

        print("\n[4/5] 쿠키 저장 중...")

        # 쿠키 개수 확인
        cookies = driver.get_cookies()
        print(f"수집된 쿠키 개수: {len(cookies)}")

        if len(cookies) == 0:
            print("\n❌ 경고: 쿠키가 없습니다!")
            print("브라우저가 제대로 로그인 상태가 아닐 수 있습니다.")

        success = cookie_manager.save_cookies(driver, url=current_url)

        if success:
            print("\n[5/5] 완료!")
            print()
            print("=" * 80)
            print("✅ 세션 쿠키가 성공적으로 저장되었습니다!")
            print("=" * 80)
            print()
            print(f"📁 저장 위치: {cookie_manager.cookie_file.absolute()}")
            print(f"📊 쿠키 개수: {len(cookies)}")
            print()
            print("🎯 다음 단계:")
            print("  1. 다음 명령어로 로그인 테스트 실행:")
            print("     pytest tests/test_login.py::TestLogin::test_successful_login -v")
            print()
            print("  2. 테스트가 다음과 같이 시작합니다:")
            print("     [LOGIN METHOD 1] Checking saved cookies...")
            print("     OK: Saved cookies found! Attempting cookie login...")
            print("     OK: Cookie login successful!")
            print()
            print("✨ 이제 2FA 인증 없이 자동으로 로그인됩니다!")
            print("=" * 80)
            print()

            # 쿠키 정보 출력
            cookie_manager.print_cookie_info()

        else:
            print("\n" + "=" * 80)
            print("❌ 쿠키 저장 실패")
            print("=" * 80)
            print("다시 시도해주세요.")
            print()
            print("문제 해결:")
            print("  1. 브라우저가 정상적으로 열렸는지 확인")
            print("  2. 로그인이 완전히 완료되었는지 확인")
            print("  3. 메인 페이지로 이동했는지 확인")
            print("=" * 80)

        print("\n" + "=" * 80)
        print("🎉 모든 작업이 완료되었습니다!")
        print("=" * 80)
        print()
        print("브라우저를 30초 후에 자동으로 닫습니다...")
        print("(쿠키가 제대로 저장되었는지 로그인된 상태를 확인하세요)")
        print()

        for i in range(30, 0, -5):
            print(f"  {i}초 남음...")
            time.sleep(5)

        print("\n브라우저를 닫는 중...")

    except KeyboardInterrupt:
        print("\n\n사용자가 중단했습니다 (Ctrl+C)")
        print("브라우저를 닫는 중...")

    except Exception as e:
        print(f"\n" + "=" * 80)
        print("❌ 오류 발생")
        print("=" * 80)
        print(f"{e}")
        print()
        import traceback
        traceback.print_exc()
        print()
        print("브라우저를 5초 후에 닫습니다...")
        time.sleep(5)

    finally:
        if driver:
            try:
                driver.quit()
                print("✓ 브라우저 종료 완료")
            except Exception as e:
                print(f"브라우저 종료 중 에러: {e}")


if __name__ == "__main__":
    try:
        manual_login()
    except KeyboardInterrupt:
        print("\n\n사용자가 중단했습니다.")
    except Exception as e:
        print(f"\n예상치 못한 오류: {e}")
        import traceback
        traceback.print_exc()

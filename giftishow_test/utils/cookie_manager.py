"""
Cookie Manager - 로그인 세션 쿠키 저장 및 로드
2단계 인증(2FA) 우회를 위한 세션 재사용
"""
import json
import pickle
import os
from pathlib import Path
from selenium import webdriver
import logging

logger = logging.getLogger(__name__)


class CookieManager:
    """세션 쿠키 관리 클래스"""

    def __init__(self, cookie_file="data/session_cookies.pkl"):
        """
        Args:
            cookie_file: 쿠키 저장 파일 경로
        """
        self.cookie_file = Path(cookie_file)
        self.cookie_file.parent.mkdir(parents=True, exist_ok=True)

    def save_cookies(self, driver, url=None):
        """
        현재 브라우저의 쿠키를 파일로 저장

        Args:
            driver: Selenium WebDriver 인스턴스
            url: 쿠키가 유효한 도메인 URL (선택)

        Returns:
            bool: 성공 여부
        """
        try:
            cookies = driver.get_cookies()

            cookie_data = {
                "url": url if url else driver.current_url,
                "cookies": cookies
            }

            with open(self.cookie_file, 'wb') as f:
                pickle.dump(cookie_data, f)

            logger.info(f"✓ 쿠키 저장 완료: {self.cookie_file}")
            logger.info(f"  저장된 쿠키 개수: {len(cookies)}")
            logger.info(f"  도메인: {cookie_data['url']}")

            return True

        except Exception as e:
            logger.error(f"쿠키 저장 실패: {e}")
            return False

    def load_cookies(self, driver, url=None):
        """
        저장된 쿠키를 브라우저에 로드

        Args:
            driver: Selenium WebDriver 인스턴스
            url: 쿠키를 로드할 페이지 URL (선택)

        Returns:
            bool: 성공 여부
        """
        try:
            if not self.cookie_file.exists():
                logger.warning(f"쿠키 파일이 없습니다: {self.cookie_file}")
                return False

            with open(self.cookie_file, 'rb') as f:
                cookie_data = pickle.load(f)

            # 쿠키 로드 전에 도메인에 먼저 접속
            target_url = url if url else cookie_data.get('url')
            if target_url:
                logger.info(f"쿠키 로드를 위해 {target_url}에 접속합니다...")
                driver.get(target_url)

            # 쿠키 추가
            cookies = cookie_data.get('cookies', [])
            for cookie in cookies:
                try:
                    # 만료된 쿠키 필드 제거
                    if 'expiry' in cookie:
                        # expiry가 과거 시간이면 스킵
                        import time
                        if cookie['expiry'] < time.time():
                            continue

                    driver.add_cookie(cookie)
                except Exception as e:
                    logger.debug(f"쿠키 추가 실패 (무시됨): {cookie.get('name')} - {e}")
                    continue

            logger.info(f"✓ 쿠키 로드 완료: {len(cookies)}개")

            # 쿠키 로드 후 페이지 새로고침
            driver.refresh()

            return True

        except Exception as e:
            logger.error(f"쿠키 로드 실패: {e}")
            return False

    def cookies_exist(self):
        """
        저장된 쿠키 파일이 있는지 확인

        Returns:
            bool: 쿠키 파일 존재 여부
        """
        return self.cookie_file.exists()

    def delete_cookies(self):
        """저장된 쿠키 파일 삭제"""
        try:
            if self.cookie_file.exists():
                self.cookie_file.unlink()
                logger.info(f"✓ 쿠키 파일 삭제: {self.cookie_file}")
                return True
            else:
                logger.warning("삭제할 쿠키 파일이 없습니다")
                return False
        except Exception as e:
            logger.error(f"쿠키 파일 삭제 실패: {e}")
            return False

    def print_cookie_info(self):
        """저장된 쿠키 정보 출력"""
        try:
            if not self.cookie_file.exists():
                print("저장된 쿠키가 없습니다")
                return

            with open(self.cookie_file, 'rb') as f:
                cookie_data = pickle.load(f)

            print("=" * 80)
            print("저장된 쿠키 정보")
            print("=" * 80)
            print(f"URL: {cookie_data.get('url')}")
            print(f"쿠키 개수: {len(cookie_data.get('cookies', []))}")
            print("\n쿠키 목록:")

            for idx, cookie in enumerate(cookie_data.get('cookies', []), 1):
                print(f"  [{idx}] {cookie.get('name')}")
                print(f"      domain: {cookie.get('domain')}")
                if 'expiry' in cookie:
                    import datetime
                    expiry_time = datetime.datetime.fromtimestamp(cookie['expiry'])
                    print(f"      expiry: {expiry_time}")

            print("=" * 80)

        except Exception as e:
            print(f"쿠키 정보 조회 실패: {e}")

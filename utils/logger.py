"""
Logger - 로깅 유틸리티
테스트 실행 로그 관리
"""
import logging
import sys
from datetime import datetime
from pathlib import Path
import colorlog


def setup_logger(
    name: str = "GiftishowTest",
    log_level: str = "INFO",
    log_file: str = None
) -> logging.Logger:
    """
    로거 설정

    Args:
        name: 로거 이름
        log_level: 로그 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: 로그 파일 경로 (None이면 파일에 저장 안함)

    Returns:
        logging.Logger: 설정된 로거
    """
    logger = logging.getLogger(name)

    # 이미 핸들러가 있으면 반환 (중복 설정 방지)
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # 콘솔 핸들러 (컬러 로그)
    console_handler = colorlog.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)

    console_format = colorlog.ColoredFormatter(
        '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    # 파일 핸들러
    if log_file:
        # 로그 디렉토리 생성
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)

        file_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)

    return logger


def get_test_logger(test_name: str = None) -> logging.Logger:
    """
    테스트용 로거 가져오기

    Args:
        test_name: 테스트 이름

    Returns:
        logging.Logger: 로거
    """
    from utils.config import Config

    # 로그 파일명 생성
    timestamp = datetime.now().strftime('%Y%m%d')
    log_filename = f"test_{timestamp}.log"
    log_filepath = Config.LOGS_DIR / log_filename

    logger_name = f"Test.{test_name}" if test_name else "Test"

    return setup_logger(
        name=logger_name,
        log_level=Config.LOG_LEVEL,
        log_file=str(log_filepath)
    )


# 기본 로거
default_logger = get_test_logger()

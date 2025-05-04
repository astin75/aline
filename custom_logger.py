import os
import logging


def get_logger(name: str, use_file_handler: bool = False) -> logging.Logger:
    # 로거 생성
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # 이미 핸들러가 있다면 추가하지 않음
    if not logger.handlers:
        # 포매터 설정
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        # 콘솔 핸들러 추가
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # 파일 핸들러 추가
        if use_file_handler:
            if not os.path.exists("logs"):
                os.makedirs("logs")
            file_handler = logging.FileHandler(f"logs/{name}.log")
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

    return logger

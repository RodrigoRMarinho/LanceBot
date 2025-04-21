"""
Este módulo fornece funcionalidades de logging para o LanceBot,
permitindo o registro de eventos, erros e informações durante a execução.
"""

import logging
import os
from datetime import datetime
from typing import Optional

class LanceLogger:
    """
    Classe para gerenciar logs do LanceBot.
    """

    def __init__(self, log_level: int = logging.INFO, log_to_file: bool = True, log_dir: Optional[str] = None):
        self.logger = logging.getLogger("LanceBot")
        self.logger.setLevel(log_level)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        if log_to_file:
            if log_dir is None:
                log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
            os.makedirs(log_dir, exist_ok=True)

            log_file = os.path.join(log_dir, f"lancebot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def debug(self, message: str):
        self.logger.debug(message)

    def info(self, message: str):
        self.logger.info(message)

    def warning(self, message: str):
        self.logger.warning(message)

    def error(self, message: str):
        self.logger.error(message)

    def critical(self, message: str):
        self.logger.critical(message)

    def log_exception(self, exception: Exception, context: str = ""):
        if context:
            self.logger.error(f"{context}: {str(exception)}", exc_info=True)
        else:
            self.logger.error(str(exception), exc_info=True)

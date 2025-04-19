"""
Logger para o LanceBot.

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
    
    Permite registrar eventos, erros e informações durante a execução do bot,
    com suporte a diferentes níveis de log e saída para arquivo.
    """
    
    def __init__(self, log_level: int = logging.INFO, log_to_file: bool = True, log_dir: Optional[str] = None):
        """
        Inicializa o logger.
        
        Args:
            log_level: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_to_file: Se True, salva logs em arquivo
            log_dir: Diretório para salvar os arquivos de log
        """
        self.logger = logging.getLogger("LanceBot")
        self.logger.setLevel(log_level)
        
        # Configurar formato do log
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # Adicionar handler para console
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # Adicionar handler para arquivo se necessário
        if log_to_file:
            if log_dir is None:
                log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
            
            os.makedirs(log_dir, exist_ok=True)
            
            log_file = os.path.join(log_dir, f"lancebot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def debug(self, message: str):
        """Registra mensagem de nível DEBUG."""
        self.logger.debug(message)
    
    def info(self, message: str):
        """Registra mensagem de nível INFO."""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Registra mensagem de nível WARNING."""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Registra mensagem de nível ERROR."""
        self.logger.error(message)
    
    def critical(self, message: str):
        """Registra mensagem de nível CRITICAL."""
        self.logger.critical(message)
    
    def log_exception(self, exception: Exception, context: str = ""):
        """
        Registra uma exceção com contexto adicional.
        
        Args:
            exception: A exceção a ser registrada
            context: Contexto adicional sobre onde a exceção ocorreu
        """
        if context:
            self.logger.error(f"{context}: {str(exception)}", exc_info=True)
        else:
            self.logger.error(str(exception), exc_info=True)

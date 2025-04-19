import pytest
from unittest.mock import MagicMock, patch
import sys
import os

# Adiciona o diretório raiz ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.logger import LanceLogger


class TestLanceLogger:
    """Testes para o sistema de logging."""
    
    def setup_method(self):
        """Configuração para cada teste."""
        # Cria um diretório temporário para os logs
        self.test_log_dir = os.path.join(os.path.dirname(__file__), "test_logs")
        os.makedirs(self.test_log_dir, exist_ok=True)
    
    def teardown_method(self):
        """Limpeza após cada teste."""
        # Remove os arquivos de log criados durante o teste
        for file in os.listdir(self.test_log_dir):
            os.remove(os.path.join(self.test_log_dir, file))
        
        # Remove o diretório de logs
        os.rmdir(self.test_log_dir)
    
    @patch('logging.FileHandler')
    @patch('logging.StreamHandler')
    def test_logger_initialization(self, mock_stream_handler, mock_file_handler):
        """Testa a inicialização do logger."""
        # Cria o logger
        logger = LanceLogger(log_to_file=True, log_dir=self.test_log_dir)
        
        # Verifica se os handlers foram criados
        assert mock_stream_handler.called
        assert mock_file_handler.called
    
    @patch('logging.Logger.debug')
    def test_debug_method(self, mock_debug):
        """Testa o método debug."""
        logger = LanceLogger(log_to_file=False)
        message = "Mensagem de debug"
        
        logger.debug(message)
        
        mock_debug.assert_called_once_with(message)
    
    @patch('logging.Logger.info')
    def test_info_method(self, mock_info):
        """Testa o método info."""
        logger = LanceLogger(log_to_file=False)
        message = "Mensagem de info"
        
        logger.info(message)
        
        mock_info.assert_called_once_with(message)
    
    @patch('logging.Logger.warning')
    def test_warning_method(self, mock_warning):
        """Testa o método warning."""
        logger = LanceLogger(log_to_file=False)
        message = "Mensagem de warning"
        
        logger.warning(message)
        
        mock_warning.assert_called_once_with(message)
    
    @patch('logging.Logger.error')
    def test_error_method(self, mock_error):
        """Testa o método error."""
        logger = LanceLogger(log_to_file=False)
        message = "Mensagem de erro"
        
        logger.error(message)
        
        mock_error.assert_called_once_with(message)
    
    @patch('logging.Logger.critical')
    def test_critical_method(self, mock_critical):
        """Testa o método critical."""
        logger = LanceLogger(log_to_file=False)
        message = "Mensagem crítica"
        
        logger.critical(message)
        
        mock_critical.assert_called_once_with(message)
    
    @patch('logging.Logger.error')
    def test_log_exception_with_context(self, mock_error):
        """Testa o método log_exception com contexto."""
        logger = LanceLogger(log_to_file=False)
        exception = ValueError("Erro de valor")
        context = "Contexto do erro"
        
        logger.log_exception(exception, context)
        
        mock_error.assert_called_once_with(f"{context}: {str(exception)}", exc_info=True)
    
    @patch('logging.Logger.error')
    def test_log_exception_without_context(self, mock_error):
        """Testa o método log_exception sem contexto."""
        logger = LanceLogger(log_to_file=False)
        exception = ValueError("Erro de valor")
        
        logger.log_exception(exception)
        
        mock_error.assert_called_once_with(str(exception), exc_info=True)
    
    def test_log_to_file(self):
        """Testa se o log está sendo escrito em arquivo."""
        logger = LanceLogger(log_to_file=True, log_dir=self.test_log_dir)
        test_message = "Teste de log em arquivo"
        
        logger.info(test_message)
        
        # Verifica se o arquivo de log foi criado
        log_files = os.listdir(self.test_log_dir)
        assert len(log_files) == 1
        
        # Verifica se a mensagem foi escrita no arquivo
        log_file_path = os.path.join(self.test_log_dir, log_files[0])
        with open(log_file_path, 'r') as f:
            log_content = f.read()
            assert test_message in log_content


if __name__ == "__main__":
    pytest.main(["-v", __file__])

import pytest
from unittest.mock import MagicMock, patch
import sys
import os

# Adiciona o diretório raiz ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.portals import PortalBase


class TestPortalBase:
    """Testes para a classe base de portais."""
    
    def setup_method(self):
        """Configuração para cada teste."""
        # Cria uma classe concreta que herda de PortalBase para testes
        class ConcretePortal(PortalBase):
            def login(self, username, password):
                return True
                
            def login_with_certificate(self, certificate_path, certificate_password=None):
                return True
                
            def search_auctions(self, keywords=None, start_date=None, end_date=None, auction_type=None):
                return []
                
            def get_auction_details(self, auction_id):
                return {}
                
            def submit_proposal(self, auction_id, item_id, price, additional_data=None):
                return True
                
            def get_auction_status(self, auction_id):
                return {}
                
            def get_current_price(self, auction_id, item_id):
                return 0.0
                
            def submit_bid(self, auction_id, item_id, price):
                return True
                
            def get_messages(self, auction_id):
                return []
                
            def send_message(self, auction_id, message):
                return True
                
            def get_ranking(self, auction_id, item_id):
                return []
        
        self.logger = MagicMock()
        self.portal = ConcretePortal(logger=self.logger)
        
        # Cria um diretório temporário para os testes
        self.test_dir = os.path.join(os.path.dirname(__file__), "test_sessions")
        os.makedirs(self.test_dir, exist_ok=True)
    
    def teardown_method(self):
        """Limpeza após cada teste."""
        # Remove os arquivos criados durante o teste
        if os.path.exists(self.test_dir):
            for file in os.listdir(self.test_dir):
                os.remove(os.path.join(self.test_dir, file))
            
            # Remove o diretório
            os.rmdir(self.test_dir)
    
    def test_initialization(self):
        """Testa a inicialização da classe base."""
        assert self.portal.logger == self.logger
        assert self.portal.logged_in is False
        assert self.portal.session_data == {}
    
    def test_save_session_not_logged_in(self):
        """Testa salvar sessão quando não está logado."""
        result = self.portal.save_session()
        
        assert result is False
        self.logger.warning.assert_called_once()
    
    def test_save_session_with_filepath(self):
        """Testa salvar sessão com caminho de arquivo específico."""
        # Simula login bem-sucedido
        self.portal.logged_in = True
        self.portal.session_data = {"test": "data"}
        
        filepath = os.path.join(self.test_dir, "test_session.json")
        result = self.portal.save_session(filepath)
        
        assert result is True
        assert os.path.exists(filepath)
        self.logger.info.assert_called_once()
    
    def test_save_session_without_filepath(self):
        """Testa salvar sessão sem caminho de arquivo específico."""
        # Simula login bem-sucedido
        self.portal.logged_in = True
        self.portal.session_data = {"test": "data"}
        
        with patch('os.path.dirname') as mock_dirname:
            # Configura o mock para retornar o diretório de teste
            mock_dirname.return_value = self.test_dir
            
            result = self.portal.save_session()
            
            assert result is True
            # Verifica se algum arquivo foi criado no diretório de teste
            assert len(os.listdir(self.test_dir)) == 1
            self.logger.info.assert_called_once()
    
    def test_load_session_success(self):
        """Testa carregar sessão com sucesso."""
        # Cria um arquivo de sessão para teste
        filepath = os.path.join(self.test_dir, "test_session.json")
        test_data = {"test": "data"}
        
        with open(filepath, 'w') as f:
            import json
            json.dump(test_data, f)
        
        result = self.portal.load_session(filepath)
        
        assert result is True
        assert self.portal.session_data == test_data
        assert self.portal.logged_in is True
        self.logger.info.assert_called_once()
    
    def test_load_session_failure(self):
        """Testa falha ao carregar sessão."""
        # Tenta carregar um arquivo que não existe
        filepath = os.path.join(self.test_dir, "nonexistent_session.json")
        
        result = self.portal.load_session(filepath)
        
        assert result is False
        assert self.portal.logged_in is False
        self.logger.error.assert_called_once()


if __name__ == "__main__":
    pytest.main(["-v", __file__])

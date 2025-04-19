import pytest
from unittest.mock import MagicMock, patch
import sys
import os

# Adiciona o diretório raiz ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.bidding import MinimalDecreaseStrategy, TimedStrategy, BiddingManager
from src.core.logger import LanceLogger


class TestMinimalDecreaseStrategy:
    """Testes para a estratégia de decremento mínimo."""
    
    def setup_method(self):
        """Configuração para cada teste."""
        self.logger = MagicMock(spec=LanceLogger)
        self.strategy = MinimalDecreaseStrategy(
            min_decrease_value=0.01,
            min_decrease_percent=0.1,
            logger=self.logger
        )
    
    def test_calculate_bid_fixed_decrease(self):
        """Testa o cálculo de lance com decremento fixo."""
        current_price = 10.0
        expected_bid = 9.99  # 10.0 - 0.01
        
        result = self.strategy.calculate_bid(current_price)
        
        assert result == expected_bid
        self.logger.info.assert_called_once()
    
    def test_calculate_bid_percent_decrease(self):
        """Testa o cálculo de lance com decremento percentual."""
        # Com preço de 100, o decremento percentual (0.1%) seria 0.1,
        # que é maior que o decremento fixo (0.01)
        current_price = 100.0
        expected_bid = 99.9  # 100.0 - (100.0 * 0.1 / 100)
        
        result = self.strategy.calculate_bid(current_price)
        
        assert result == expected_bid
        self.logger.info.assert_called_once()
    
    def test_should_bid_true(self):
        """Testa cenário onde deve dar lance."""
        current_price = 100.0
        my_last_bid = 110.0
        min_price = 90.0
        
        result = self.strategy.should_bid(
            current_price=current_price,
            my_last_bid=my_last_bid,
            min_price=min_price
        )
        
        assert result is True
    
    def test_should_bid_false_already_lowest(self):
        """Testa cenário onde não deve dar lance por já ser o menor preço."""
        current_price = 100.0
        my_last_bid = 99.0  # Já temos o menor preço
        min_price = 90.0
        
        result = self.strategy.should_bid(
            current_price=current_price,
            my_last_bid=my_last_bid,
            min_price=min_price
        )
        
        assert result is False
        self.logger.info.assert_called_once()
    
    def test_should_bid_false_below_min_price(self):
        """Testa cenário onde não deve dar lance por estar abaixo do preço mínimo."""
        current_price = 89.0  # Abaixo do preço mínimo
        my_last_bid = 95.0
        min_price = 90.0
        
        result = self.strategy.should_bid(
            current_price=current_price,
            my_last_bid=my_last_bid,
            min_price=min_price
        )
        
        assert result is False
        self.logger.info.assert_called_once()


class TestTimedStrategy:
    """Testes para a estratégia baseada em tempo."""
    
    def setup_method(self):
        """Configuração para cada teste."""
        self.logger = MagicMock(spec=LanceLogger)
        self.strategy = TimedStrategy(
            bid_times=[60, 30, 10, 3],
            random_delay=False,
            logger=self.logger
        )
    
    def test_should_bid_at_exact_time(self):
        """Testa dar lance em um momento exato programado."""
        # Deve dar lance aos 30 segundos restantes
        result = self.strategy.should_bid(
            seconds_remaining=30,
            current_price=100.0,
            my_last_bid=110.0,
            min_price=90.0
        )
        
        assert result is True
        self.logger.info.assert_called_once()
    
    def test_should_bid_at_lower_time(self):
        """Testa dar lance em um momento abaixo do programado."""
        # Deve dar lance aos 29 segundos restantes (abaixo de 30)
        result = self.strategy.should_bid(
            seconds_remaining=29,
            current_price=100.0,
            my_last_bid=110.0,
            min_price=90.0
        )
        
        assert result is True
        self.logger.info.assert_called_once()
    
    def test_should_not_bid_above_time(self):
        """Testa não dar lance em um momento acima do programado."""
        # Não deve dar lance aos 31 segundos restantes (acima de 30)
        result = self.strategy.should_bid(
            seconds_remaining=31,
            current_price=100.0,
            my_last_bid=110.0,
            min_price=90.0
        )
        
        assert result is False
    
    def test_should_not_bid_already_lowest(self):
        """Testa não dar lance quando já temos o menor preço."""
        result = self.strategy.should_bid(
            seconds_remaining=30,
            current_price=100.0,
            my_last_bid=99.0,  # Já temos o menor preço
            min_price=90.0
        )
        
        assert result is False
    
    def test_calculate_bid_normal(self):
        """Testa cálculo de lance normal."""
        current_price = 100.0
        expected_bid = 99.99  # Usando a estratégia de decremento mínimo
        
        result = self.strategy.calculate_bid(
            current_price=current_price,
            min_decrease_value=0.01,
            min_decrease_percent=0.0
        )
        
        assert result == expected_bid
    
    def test_calculate_bid_aggressive(self):
        """Testa cálculo de lance agressivo nos momentos finais."""
        current_price = 100.0
        expected_bid = 99.98  # Decremento dobrado (0.02)
        
        # Simula que já deu lance nos momentos anteriores
        self.strategy.last_bid_time_index = len(self.strategy.bid_times) - 2
        
        result = self.strategy.calculate_bid(
            current_price=current_price,
            min_decrease_value=0.01,
            min_decrease_percent=0.0,
            aggressive_final_bid=True
        )
        
        assert result == expected_bid
        self.logger.info.assert_called_once()


class TestBiddingManager:
    """Testes para o gerenciador de lances."""
    
    def setup_method(self):
        """Configuração para cada teste."""
        self.logger = MagicMock(spec=LanceLogger)
        self.strategy = MagicMock(spec=MinimalDecreaseStrategy)
        self.manager = BiddingManager(logger=self.logger)
    
    def test_register_auction(self):
        """Testa registro de licitação."""
        auction_id = "TEST-123"
        item_description = "Item de teste"
        
        self.manager.register_auction(
            auction_id=auction_id,
            strategy=self.strategy,
            min_price=90.0,
            max_bids=5,
            item_description=item_description
        )
        
        assert auction_id in self.manager.active_auctions
        assert self.manager.active_auctions[auction_id]['strategy'] == self.strategy
        assert self.manager.active_auctions[auction_id]['min_price'] == 90.0
        assert self.manager.active_auctions[auction_id]['max_bids'] == 5
        assert self.manager.active_auctions[auction_id]['item_description'] == item_description
        self.logger.info.assert_called_once()
    
    def test_process_bid_success(self):
        """Testa processamento de lance com sucesso."""
        auction_id = "TEST-123"
        current_price = 100.0
        expected_bid = 99.9
        
        # Configura o mock da estratégia
        self.strategy.should_bid.return_value = True
        self.strategy.calculate_bid.return_value = expected_bid
        
        # Registra a licitação
        self.manager.register_auction(
            auction_id=auction_id,
            strategy=self.strategy,
            min_price=90.0
        )
        
        # Processa o lance
        result = self.manager.process_bid(
            auction_id=auction_id,
            current_price=current_price
        )
        
        assert result == expected_bid
        assert self.manager.active_auctions[auction_id]['last_bid'] == expected_bid
        assert self.manager.active_auctions[auction_id]['bids_count'] == 1
        assert len(self.manager.active_auctions[auction_id]['bid_history']) == 1
        self.strategy.should_bid.assert_called_once()
        self.strategy.calculate_bid.assert_called_once()
    
    def test_process_bid_should_not_bid(self):
        """Testa processamento de lance quando não deve dar lance."""
        auction_id = "TEST-123"
        current_price = 100.0
        
        # Configura o mock da estratégia
        self.strategy.should_bid.return_value = False
        
        # Registra a licitação
        self.manager.register_auction(
            auction_id=auction_id,
            strategy=self.strategy,
            min_price=90.0
        )
        
        # Processa o lance
        result = self.manager.process_bid(
            auction_id=auction_id,
            current_price=current_price
        )
        
        assert result is None
        assert self.manager.active_auctions[auction_id]['last_bid'] is None
        assert self.manager.active_auctions[auction_id]['bids_count'] == 0
        assert len(self.manager.active_auctions[auction_id]['bid_history']) == 0
        self.strategy.should_bid.assert_called_once()
        self.strategy.calculate_bid.assert_not_called()
    
    def test_process_bid_max_bids_reached(self):
        """Testa processamento de lance quando atingiu o número máximo de lances."""
        auction_id = "TEST-123"
        current_price = 100.0
        
        # Registra a licitação com máximo de 1 lance
        self.manager.register_auction(
            auction_id=auction_id,
            strategy=self.strategy,
            min_price=90.0,
            max_bids=1
        )
        
        # Configura o mock da estratégia
        self.strategy.should_bid.return_value = True
        self.strategy.calculate_bid.return_value = 99.9
        
        # Dá o primeiro lance (deve funcionar)
        self.manager.process_bid(
            auction_id=auction_id,
            current_price=current_price
        )
        
        # Tenta dar o segundo lance (deve falhar)
        result = self.manager.process_bid(
            auction_id=auction_id,
            current_price=99.9
        )
        
        assert result is None
        assert self.manager.active_auctions[auction_id]['bids_count'] == 1
    
    def test_get_auction_status(self):
        """Testa obtenção do status da licitação."""
        auction_id = "TEST-123"
        
        # Registra a licitação
        self.manager.register_auction(
            auction_id=auction_id,
            strategy=self.strategy,
            min_price=90.0
        )
        
        # Obtém o status
        status = self.manager.get_auction_status(auction_id)
        
        assert status['strategy'] == self.strategy
        assert status['min_price'] == 90.0
        assert status['bids_count'] == 0
        assert status['last_bid'] is None
    
    def test_remove_auction(self):
        """Testa remoção de licitação."""
        auction_id = "TEST-123"
        
        # Registra a licitação
        self.manager.register_auction(
            auction_id=auction_id,
            strategy=self.strategy,
            min_price=90.0
        )
        
        # Remove a licitação
        result = self.manager.remove_auction(auction_id)
        
        assert result is True
        assert auction_id not in self.manager.active_auctions
        self.logger.info.assert_called()
    
    def test_remove_auction_not_found(self):
        """Testa remoção de licitação não encontrada."""
        auction_id = "TEST-123"
        
        # Tenta remover uma licitação que não existe
        result = self.manager.remove_auction(auction_id)
        
        assert result is False
        self.logger.warning.assert_called_once()


if __name__ == "__main__":
    pytest.main(["-v", __file__])

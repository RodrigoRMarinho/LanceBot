"""
Módulo de estratégias de lance para o LanceBot.

Este módulo implementa diferentes estratégias para dar lances automáticos
em licitações públicas, respeitando regras e limites configuráveis.
"""

import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Callable

from .logger import LanceLogger

class BiddingStrategy:
    """
    Classe base para estratégias de lance.
    
    Define a interface comum para todas as estratégias de lance
    implementadas no sistema.
    """
    
    def __init__(self, logger: Optional[LanceLogger] = None):
        """
        Inicializa a estratégia de lance.
        
        Args:
            logger: Instância do logger para registrar eventos
        """
        self.logger = logger or LanceLogger()
    
    def calculate_bid(self, current_price: float, **kwargs) -> float:
        """
        Calcula o valor do próximo lance.
        
        Args:
            current_price: Preço atual do item
            **kwargs: Parâmetros adicionais específicos da estratégia
            
        Returns:
            Valor do próximo lance
        """
        raise NotImplementedError("Método deve ser implementado pelas subclasses")
    
    def should_bid(self, **kwargs) -> bool:
        """
        Determina se deve dar um lance no momento atual.
        
        Args:
            **kwargs: Parâmetros para a decisão
            
        Returns:
            True se deve dar lance, False caso contrário
        """
        raise NotImplementedError("Método deve ser implementado pelas subclasses")


class MinimalDecreaseStrategy(BiddingStrategy):
    """
    Estratégia que dá o lance mínimo possível abaixo do valor atual.
    
    Útil para licitações de menor preço onde o objetivo é vencer
    com o menor decremento possível.
    """
    
    def __init__(self, 
                 min_decrease_value: float = 0.01, 
                 min_decrease_percent: float = 0.0,
                 logger: Optional[LanceLogger] = None):
        """
        Inicializa a estratégia de decremento mínimo.
        
        Args:
            min_decrease_value: Valor mínimo de decremento (ex: R$ 0,01)
            min_decrease_percent: Percentual mínimo de decremento (ex: 0.1%)
            logger: Instância do logger
        """
        super().__init__(logger)
        self.min_decrease_value = min_decrease_value
        self.min_decrease_percent = min_decrease_percent
    
    def calculate_bid(self, current_price: float, **kwargs) -> float:
        """
        Calcula o lance com decremento mínimo.
        
        Args:
            current_price: Preço atual do item
            **kwargs: Parâmetros adicionais
            
        Returns:
            Valor do próximo lance
        """
        percent_decrease = current_price * (self.min_decrease_percent / 100)
        
        # Usa o maior entre o decremento fixo e o percentual
        if percent_decrease > self.min_decrease_value and self.min_decrease_percent > 0:
            new_bid = current_price - percent_decrease
        else:
            new_bid = current_price - self.min_decrease_value
            
        # Arredonda para 2 casas decimais
        new_bid = round(new_bid, 2)
        
        self.logger.info(f"Calculado lance de R$ {new_bid:.2f} (atual: R$ {current_price:.2f})")
        return new_bid
    
    def should_bid(self, 
                  current_price: float, 
                  my_last_bid: Optional[float] = None,
                  min_price: Optional[float] = None, 
                  **kwargs) -> bool:
        """
        Determina se deve dar um lance.
        
        Args:
            current_price: Preço atual do item
            my_last_bid: Último lance dado pelo bot
            min_price: Preço mínimo aceitável
            **kwargs: Parâmetros adicionais
            
        Returns:
            True se deve dar lance, False caso contrário
        """
        # Não dar lance se já somos o menor preço
        if my_last_bid is not None and my_last_bid <= current_price:
            self.logger.info(f"Não dando lance: já somos o menor preço (R$ {my_last_bid:.2f})")
            return False
        
        # Não dar lance se o preço estiver abaixo do mínimo aceitável
        if min_price is not None and current_price <= min_price:
            self.logger.info(f"Não dando lance: preço atual (R$ {current_price:.2f}) abaixo do mínimo (R$ {min_price:.2f})")
            return False
            
        return True


class TimedStrategy(BiddingStrategy):
    """
    Estratégia que dá lances em momentos específicos.
    
    Útil para licitações com tempo definido, dando lances
    em momentos estratégicos (ex: últimos segundos).
    """
    
    def __init__(self, 
                 bid_times: List[int] = None,
                 random_delay: bool = False,
                 max_random_delay: int = 5,
                 logger: Optional[LanceLogger] = None):
        """
        Inicializa a estratégia baseada em tempo.
        
        Args:
            bid_times: Lista de segundos restantes para dar lance (ex: [60, 30, 10, 3])
            random_delay: Se True, adiciona um atraso aleatório aos tempos
            max_random_delay: Atraso máximo em segundos
            logger: Instância do logger
        """
        super().__init__(logger)
        self.bid_times = bid_times or [60, 30, 10, 3]
        self.random_delay = random_delay
        self.max_random_delay = max_random_delay
        self.last_bid_time_index = -1
    
    def calculate_bid(self, 
                     current_price: float, 
                     min_decrease_value: float = 0.01,
                     min_decrease_percent: float = 0.0,
                     aggressive_final_bid: bool = False,
                     **kwargs) -> float:
        """
        Calcula o valor do próximo lance baseado no tempo restante.
        
        Args:
            current_price: Preço atual do item
            min_decrease_value: Valor mínimo de decremento
            min_decrease_percent: Percentual mínimo de decremento
            aggressive_final_bid: Se True, dá um lance mais agressivo nos segundos finais
            **kwargs: Parâmetros adicionais
            
        Returns:
            Valor do próximo lance
        """
        # Usa a estratégia de decremento mínimo como base
        base_strategy = MinimalDecreaseStrategy(
            min_decrease_value=min_decrease_value,
            min_decrease_percent=min_decrease_percent,
            logger=self.logger
        )
        
        # Se for o último lance programado e modo agressivo estiver ativado
        if aggressive_final_bid and self.last_bid_time_index >= len(self.bid_times) - 2:
            # Lance mais agressivo nos segundos finais (2x o decremento normal)
            percent_decrease = current_price * (min_decrease_percent * 2 / 100)
            value_decrease = min_decrease_value * 2
            
            if percent_decrease > value_decrease and min_decrease_percent > 0:
                new_bid = current_price - percent_decrease
            else:
                new_bid = current_price - value_decrease
                
            new_bid = round(new_bid, 2)
            self.logger.info(f"Lance agressivo final: R$ {new_bid:.2f}")
            return new_bid
        
        # Caso contrário, usa a estratégia base
        return base_strategy.calculate_bid(current_price)
    
    def should_bid(self, 
                  seconds_remaining: int, 
                  current_price: float,
                  my_last_bid: Optional[float] = None,
                  min_price: Optional[float] = None,
                  **kwargs) -> bool:
        """
        Determina se deve dar um lance baseado no tempo restante.
        
        Args:
            seconds_remaining: Segundos restantes para o fim do pregão
            current_price: Preço atual do item
            my_last_bid: Último lance dado pelo bot
            min_price: Preço mínimo aceitável
            **kwargs: Parâmetros adicionais
            
        Returns:
            True se deve dar lance, False caso contrário
        """
        # Verifica condições básicas usando a estratégia de decremento mínimo
        base_strategy = MinimalDecreaseStrategy(logger=self.logger)
        if not base_strategy.should_bid(
            current_price=current_price,
            my_last_bid=my_last_bid,
            min_price=min_price
        ):
            return False
        
        # Verifica se o tempo atual corresponde a um dos momentos programados para lance
        for i, bid_time in enumerate(self.bid_times):
            # Adiciona atraso aleatório se configurado
            if self.random_delay:
                delay = random.randint(0, self.max_random_delay)
                adjusted_bid_time = bid_time + delay
            else:
                adjusted_bid_time = bid_time
                
            # Verifica se é hora de dar lance e se ainda não demos lance neste momento
            if seconds_remaining <= adjusted_bid_time and i > self.last_bid_time_index:
                self.last_bid_time_index = i
                self.logger.info(f"Dando lance programado a {seconds_remaining}s do fim")
                return True
                
        return False


class BiddingManager:
    """
    Gerenciador de estratégias de lance.
    
    Coordena diferentes estratégias de lance e mantém o estado
    das licitações em andamento.
    """
    
    def __init__(self, logger: Optional[LanceLogger] = None):
        """
        Inicializa o gerenciador de lances.
        
        Args:
            logger: Instância do logger
        """
        self.logger = logger or LanceLogger()
        self.active_auctions = {}  # Dicionário de licitações ativas
        
    def register_auction(self, 
                        auction_id: str, 
                        strategy: BiddingStrategy,
                        min_price: Optional[float] = None,
                        max_bids: Optional[int] = None,
                        item_description: Optional[str] = None) -> None:
        """
        Registra uma nova licitação para participação.
        
        Args:
            auction_id: Identificador único da licitação
            strategy: Estratégia de lance a ser utilizada
            min_price: Preço mínimo aceitável
            max_bids: Número máximo de lances a serem dados
            item_description: Descrição do item licitado
        """
        self.active_auctions[auction_id] = {
            'strategy': strategy,
            'min_price': min_price,
            'max_bids': max_bids,
            'bids_count': 0,
            'last_bid': None,
            'item_description': item_description,
            'start_time': datetime.now(),
            'bid_history': []
        }
        
        self.logger.info(f"Licitação registrada: {auction_id} - {item_description}")
        
    def process_bid(self, 
                   auction_id: str, 
                   current_price: float,
                   seconds_remaining: Optional[int] = None,
                   **kwargs) -> Optional[float]:
        """
        Processa um possível lance para uma licitação.
        
        Args:
            auction_id: Identificador da licitação
            current_price: Preço atual do item
            seconds_remaining: Segundos restantes para o fim (se aplicável)
            **kwargs: Parâmetros adicionais para a estratégia
            
        Returns:
            Valor do lance calculado ou None se não deve dar lance
        """
        if auction_id not in self.active_auctions:
            self.logger.warning(f"Tentativa de processar lance para licitação não registrada: {auction_id}")
            return None
            
        auction = self.active_auctions[auction_id]
        
        # Verifica se atingiu o número máximo de lances
        if auction['max_bids'] is not None and auction['bids_count'] >= auction['max_bids']:
            self.logger.info(f"Número máximo de lances atingido para {auction_id}")
            return None
            
        # Prepara parâmetros para a estratégia
        strategy_params = {
            'current_price': current_price,
            'my_last_bid': auction['last_bid'],
            'min_price': auction['min_price']
        }
        
        # Adiciona segundos restantes se disponível
        if seconds_remaining is not None:
            strategy_params['seconds_remaining'] = seconds_remaining
            
        # Adiciona parâmetros extras
        strategy_params.update(kwargs)
        
        # Verifica se deve dar lance
        if not auction['strategy'].should_bid(**strategy_params):
            return None
            
        # Calcula o valor do lance
        bid_value = auction['strategy'].calculate_bid(**strategy_params)
        
        # Atualiza o estado da licitação
        auction['last_bid'] = bid_value
        auction['bids_count'] += 1
        auction['bid_history'].append({
            'value': bid_value,
            'timestamp': datetime.now(),
            'current_price': current_price
        })
        
        self.logger.info(f"Lance processado para {auction_id}: R$ {bid_value:.2f}")
        return bid_value
        
    def get_auction_status(self, auction_id: str) -> Dict:
        """
        Obtém o status atual de uma licitação.
        
        Args:
            auction_id: Identificador da licitação
            
        Returns:
            Dicionário com informações sobre a licitação
        """
        if auction_id not in self.active_auctions:
            self.logger.warning(f"Tentativa de obter status de licitação não registrada: {auction_id}")
            return {}
            
        return self.active_auctions[auction_id]
        
    def remove_auction(self, auction_id: str) -> bool:
        """
        Remove uma licitação do gerenciador.
        
        Args:
            auction_id: Identificador da licitação
            
        Returns:
            True se removido com sucesso, False caso contrário
        """
        if auction_id in self.active_auctions:
            del self.active_auctions[auction_id]
            self.logger.info(f"Licitação removida: {auction_id}")
            return True
            
        self.logger.warning(f"Tentativa de remover licitação não registrada: {auction_id}")
        return False

"""
Módulo que define as estratégias de lance para o LanceBot.

Este módulo contém diferentes estratégias para calcular lances durante as licitações,
como decremento mínimo e estratégias baseadas em tempo.
"""

from abc import ABC, abstractmethod
import random
from typing import Optional


class BiddingStrategy(ABC):
    """
    Classe base para todas as estratégias de lance.
    """
    @abstractmethod
    def calculate_bid(self, current_price: float) -> float:
        """
        Método para calcular o próximo lance.
        
        Args:
            current_price: Preço atual da licitação.
        
        Returns:
            Novo valor do lance.
        """
        pass


class MinimalDecreaseStrategy(BiddingStrategy):
    """
    Estratégia de lance baseada em decremento mínimo.
    
    Decrementa o preço atual por um valor mínimo ou percentual, garantindo um lance mais competitivo.
    """
    def __init__(self, min_decrease_value: float, min_decrease_percent: float, logger) -> None:
        self.min_decrease_value = min_decrease_value
        self.min_decrease_percent = min_decrease_percent
        self.logger = logger

    def calculate_bid(self, current_price: float) -> float:
        """
        Calcula o novo lance com base em um decremento mínimo.
        
        Args:
            current_price: Preço atual da licitação.
        
        Returns:
            Novo valor do lance.
        """
        decrease = max(self.min_decrease_value, current_price * self.min_decrease_percent)
        new_bid = current_price - decrease
        self.logger.info(f"Lance calculado com decremento: {new_bid:.2f}")
        return new_bid


class TimedStrategy(BiddingStrategy):
    """
    Estratégia de lance baseada no tempo restante da licitação.
    
    Quanto menos tempo resta, mais agressivo o lance pode ser.
    """
    def __init__(self, bid_times: list, random_delay: bool, logger) -> None:
        self.bid_times = bid_times
        self.random_delay = random_delay
        self.logger = logger

    def should_bid(self, seconds_remaining: int, current_price: float, my_last_bid: Optional[float], min_price: float) -> bool:
        """
        Verifica se o bot deve dar um lance com base no tempo restante.
        
        Args:
            seconds_remaining: Tempo restante para o final da licitação (em segundos).
            current_price: Preço atual da licitação.
            my_last_bid: Último lance dado.
            min_price: Preço mínimo para o lance.
        
        Returns:
            True se o bot deve dar um lance, False caso contrário.
        """
        return seconds_remaining in self.bid_times

    def calculate_bid(self, current_price: float, min_decrease_value: float, min_decrease_percent: float, aggressive_final_bid: bool) -> float:
        """
        Calcula o próximo lance baseado no tempo restante.
        
        Args:
            current_price: Preço atual da licitação.
            min_decrease_value: Valor mínimo de decremento.
            min_decrease_percent: Percentual mínimo de decremento.
            aggressive_final_bid: Se o lance final deve ser mais agressivo.
        
        Returns:
            Novo valor do lance.
        """
        if aggressive_final_bid:
            # Lance mais agressivo no final
            return current_price - (min_decrease_value * 2)
        else:
            return current_price - max(min_decrease_value, current_price * min_decrease_percent)


class BiddingManager:
    """
    Gerenciador de lances para coordenar as estratégias de lances e registrar informações.
    """
    def __init__(self, logger) -> None:
        self.logger = logger
        self.auctions = {}

    def register_auction(self, auction_id: str, strategy: BiddingStrategy, min_price: float, max_bids: int, item_description: str) -> None:
        """
        Registra uma licitação para ser gerenciada pelo bot.
        
        Args:
            auction_id: ID da licitação.
            strategy: Estratégia de lance a ser utilizada.
            min_price: Preço mínimo para o lance.
            max_bids: Número máximo de lances que o bot deve dar.
            item_description: Descrição do item da licitação.
        """
        self.auctions[auction_id] = {
            "strategy": strategy,
            "min_price": min_price,
            "max_bids": max_bids,
            "item_description": item_description,
            "bids_count": 0,
            "last_bid": None,
        }

    def process_bid(self, auction_id: str, current_price: float, seconds_remaining: int) -> Optional[float]:
        """
        Processa um lance para uma licitação registrada.
        
        Args:
            auction_id: ID da licitação.
            current_price: Preço atual da licitação.
            seconds_remaining: Tempo restante para o final da licitação.
        
        Returns:
            O valor do novo lance ou None caso nenhum lance tenha sido dado.
        """
        auction = self.auctions.get(auction_id)
        if auction is None:
            self.logger.error(f"Licitação {auction_id} não registrada")
            return None
        
        strategy = auction["strategy"]
        min_price = auction["min_price"]
        max_bids = auction["max_bids"]
        bids_count = auction["bids_count"]
        
        if bids_count >= max_bids:
            self.logger.info(f"Licitação {auction_id} atingiu o número máximo de lances")
            return None
        
        should_bid = strategy.should_bid(seconds_remaining, current_price, auction["last_bid"], min_price)
        
        if should_bid:
            new_bid = strategy.calculate_bid(current_price, min_decrease_value=0.01, min_decrease_percent=0.1, aggressive_final_bid=(seconds_remaining <= 5))
            auction["bids_count"] += 1
            auction["last_bid"] = new_bid
            self.logger.info(f"Lance dado: R$ {new_bid:.2f}")
            return new_bid
        return None

    def get_auction_status(self, auction_id: str) -> dict:
        """
        Obtém o status da licitação.
        
        Args:
            auction_id: ID da licitação.
        
        Returns:
            Dicionário com o status da licitação.
        """
        auction = self.auctions.get(auction_id)
        if auction is None:
            self.logger.error(f"Licitação {auction_id} não registrada")
            return {}
        
        return {
            "bids_count": auction["bids_count"],
            "last_bid": auction["last_bid"],
        }


"""
Pacote core do LanceBot.

Este pacote contém os módulos principais do sistema, incluindo
o gerenciador de lances e o sistema de logging.
"""

from .logger import LanceLogger
from .bidding import BiddingStrategy, MinimalDecreaseStrategy, TimedStrategy, BiddingManager

__all__ = [
    'LanceLogger',
    'BiddingStrategy',
    'MinimalDecreaseStrategy',
    'TimedStrategy',
    'BiddingManager'
]

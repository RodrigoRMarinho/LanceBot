"""
Módulo principal do LanceBot.

Este módulo implementa a interface de linha de comando para o LanceBot,
permitindo testar as funcionalidades básicas do sistema.
"""

import os
import sys
import argparse
import time
from datetime import datetime
from typing import Dict, List, Optional, Union, Any

from src.core.logger import LanceLogger
from src.core.bidding import BiddingStrategy, MinimalDecreaseStrategy, TimedStrategy, BiddingManager
from src.portals.comprasnet import ComprasNetPortal
from src.portals.portaldecompras import PortalComprasPublicas
from src.portals.bllcompras import BLLComprasPortal
from src.portals.licitacoes_e import LicitacoesEPortal


def load_credentials(env_file: str = "LOGIN.env") -> Dict[str, str]:
    """
    Carrega credenciais do arquivo .env
    
    Args:
        env_file: Caminho para o arquivo .env
        
    Returns:
        Dicionário com as credenciais
    """
    credentials = {}
    
    if not os.path.exists(env_file):
        print(f"Arquivo de credenciais {env_file} não encontrado.")
        return credentials
        
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            key, value = line.split('=', 1)
            credentials[key.strip()] = value.strip().strip('"\'')
            
    return credentials


def test_portal(portal_name: str, credentials: Dict[str, str], logger: LanceLogger) -> None:
    """
    Testa a conexão com um portal específico.
    
    Args:
        portal_name: Nome do portal a ser testado
        credentials: Dicionário com credenciais
        logger: Instância do logger
    """
    logger.info(f"Testando conexão com o portal {portal_name}")
    
    if portal_name.lower() == "comprasnet":
        username = credentials.get("COMPRASNET_USER", "")
        password = credentials.get("COMPRASNET_PASS", "")
        
        if not username or not password:
            logger.error("Credenciais para ComprasNet não encontradas no arquivo .env")
            return
            
        portal = ComprasNetPortal(headless=False, logger=logger)
        
    elif portal_name.lower() == "portaldecompras":
        username = credentials.get("PORTALDECOMPRAS_USER", "")
        password = credentials.get("PORTALDECOMPRAS_PASS", "")
        
        if not username or not password:
            logger.error("Credenciais para Portal de Compras Públicas não encontradas no arquivo .env")
            return
            
        portal = PortalComprasPublicas(headless=False, logger=logger)
        
    elif portal_name.lower() == "bllcompras":
        username = credentials.get("BLLCOMPRAS_USER", "")
        password = credentials.get("BLLCOMPRAS_PASS", "")
        
        if not username or not password:
            logger.error("Credenciais para BLL Compras não encontradas no arquivo .env")
            return
            
        portal = BLLComprasPortal(headless=False, logger=logger)
        
    elif portal_name.lower() == "licitacoes-e":
        username = credentials.get("LICITACOESE_USER", "")
        password = credentials.get("LICITACOESE_PASS", "")
        
        if not username or not password:
            logger.error("Credenciais para Licitações-e não encontradas no arquivo .env")
            return
            
        portal = LicitacoesEPortal(headless=False, logger=logger)
        
    else:
        logger.error(f"Portal {portal_name} não suportado")
        return
    
    # Tenta fazer login
    logger.info(f"Tentando login no {portal_name} com usuário {username}")
    login_success = portal.login(username, password)
    
    if login_success:
        logger.info(f"Login no {portal_name} realizado com sucesso!")
        
        # Tenta buscar licitações
        logger.info("Buscando licitações disponíveis...")
        auctions = portal.search_auctions()
        
        if auctions:
            logger.info(f"Encontradas {len(auctions)} licitações")
            
            # Exibe as 5 primeiras licitações
            for i, auction in enumerate(auctions[:5]):
                logger.info(f"Licitação {i+1}: {auction.get('id')} - {auction.get('object', '')[:50]}...")
                
            # Tenta obter detalhes da primeira licitação
            if auctions[0].get('id'):
                auction_id = auctions[0].get('id')
                logger.info(f"Obtendo detalhes da licitação {auction_id}")
                
                details = portal.get_auction_details(auction_id)
                if details:
                    logger.info(f"Detalhes obtidos com sucesso: {len(details.get('items', []))} itens encontrados")
                else:
                    logger.warning("Não foi possível obter detalhes da licitação")
        else:
            logger.warning("Nenhuma licitação encontrada")
    else:
        logger.error(f"Falha no login no {portal_name}")


def test_bidding_strategy() -> None:
    """
    Testa as estratégias de lance do sistema.
    """
    logger = LanceLogger()
    logger.info("Testando estratégias de lance")
    
    # Testa a estratégia de decremento mínimo
    min_strategy = MinimalDecreaseStrategy(min_decrease_value=0.01, min_decrease_percent=0.1, logger=logger)
    
    # Calcula alguns lances
    current_price = 100.0
    logger.info(f"Preço atual: R$ {current_price:.2f}")
    
    new_bid = min_strategy.calculate_bid(current_price)
    logger.info(f"Novo lance (decremento mínimo): R$ {new_bid:.2f}")
    
    # Testa a estratégia baseada em tempo
    timed_strategy = TimedStrategy(bid_times=[60, 30, 10, 3], random_delay=True, logger=logger)
    
    # Simula alguns cenários de tempo
    for seconds in [120, 60, 40, 30, 15, 10, 5, 3, 1]:
        should_bid = timed_strategy.should_bid(
            seconds_remaining=seconds,
            current_price=current_price,
            my_last_bid=None,
            min_price=90.0
        )
        
        if should_bid:
            new_bid = timed_strategy.calculate_bid(
                current_price=current_price,
                min_decrease_value=0.01,
                min_decrease_percent=0.1,
                aggressive_final_bid=(seconds <= 5)
            )
            logger.info(f"Tempo restante: {seconds}s - Dando lance: R$ {new_bid:.2f}")
        else:
            logger.info(f"Tempo restante: {seconds}s - Não dar lance")
    
    # Testa o gerenciador de lances
    manager = BiddingManager(logger=logger)
    
    # Registra uma licitação
    auction_id = "TESTE-123"
    manager.register_auction(
        auction_id=auction_id,
        strategy=timed_strategy,
        min_price=90.0,
        max_bids=5,
        item_description="Item de teste para demonstração"
    )
    
    # Simula alguns lances
    for seconds in [120, 60, 30, 10, 5, 3, 1]:
        bid_value = manager.process_bid(
            auction_id=auction_id,
            current_price=current_price,
            seconds_remaining=seconds
        )
        
        if bid_value:
            logger.info(f"Tempo restante: {seconds}s - Lance processado: R$ {bid_value:.2f}")
            current_price = bid_value  # Atualiza o preço atual
        else:
            logger.info(f"Tempo restante: {seconds}s - Nenhum lance processado")
    
    # Obtém o status final
    status = manager.get_auction_status(auction_id)
    logger.info(f"Total de lances dados: {status['bids_count']}")
    logger.info(f"Último lance: R$ {status['last_bid']:.2f}")


def main():
    """
    Função principal do LanceBot.
    """
    parser = argparse.ArgumentParser(description="LanceBot - Robô para licitações públicas")
    parser.add_argument("--test-portal", type=str, help="Testa conexão com um portal específico")
    parser.add_argument("--test-strategy", action="store_true", help="Testa estratégias de lance")
    parser.add_argument("--env-file", type=str, default="LOGIN.env", help="Arquivo de credenciais")
    
    args = parser.parse_args()
    
    # Configura o logger
    logger = LanceLogger(log_to_file=True)
    logger.info("Iniciando LanceBot")
    
    # Carrega credenciais
    credentials = load_credentials(args.env_file)
    
    if args.test_portal:
        test_portal(args.test_portal, credentials, logger)
    elif args.test_strategy:
        test_bidding_strategy()
    else:
        logger.info("Nenhuma ação especificada. Use --help para ver as opções disponíveis.")
    
    logger.info("LanceBot finalizado")


if __name__ == "__main__":
    main()

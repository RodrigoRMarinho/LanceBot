"""
Módulo para interação com o portal ComprasNet.

Este módulo implementa a interface para o portal de licitações ComprasNet
(www.comprasnet.gov.br), permitindo login, busca de licitações, envio de
propostas e lances automáticos.
"""

import os
import time
import json
from datetime import datetime
from typing import Dict, List, Optional, Union, Any
from pathlib import Path

from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
from .. import PortalBase
from ...core.logger import LanceLogger


class ComprasNetPortal(PortalBase):
    """
    Implementação da interface para o portal ComprasNet.
    
    Permite interação automatizada com o portal de licitações do Governo Federal.
    """
    
    BASE_URL = "https://www.comprasnet.gov.br"
    LOGIN_URL = "https://www.comprasnet.gov.br/seguro/loginPortal.asp"
    
    def __init__(self, headless: bool = True, logger: Optional[LanceLogger] = None):
        """
        Inicializa o portal ComprasNet.
        
        Args:
            headless: Se True, executa o navegador em modo headless (sem interface gráfica)
            logger: Instância do logger para registrar eventos
        """
        super().__init__(logger)
        self.headless = headless
        self.browser = None
        self.context = None
        self.page = None
        
    def _initialize_browser(self) -> None:
        """
        Inicializa o navegador Playwright.
        """
        if self.browser is None:
            self.logger.info("Inicializando navegador para ComprasNet")
            playwright = sync_playwright().start()
            self.browser = playwright.chromium.launch(headless=self.headless)
            self.context = self.browser.new_context(
                viewport={"width": 1280, "height": 800},
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
            )
            self.page = self.context.new_page()
            
    def _close_browser(self) -> None:
        """
        Fecha o navegador Playwright.
        """
        if self.browser:
            self.logger.info("Fechando navegador ComprasNet")
            self.context.close()
            self.browser.close()
            self.browser = None
            self.context = None
            self.page = None
    
    def login(self, username: str, password: str) -> bool:
        """
        Realiza login no portal ComprasNet.
        
        Args:
            username: CPF do usuário (apenas números)
            password: Senha de acesso
            
        Returns:
            True se login bem-sucedido, False caso contrário
        """
        try:
            self._initialize_browser()
            self.logger.info(f"Iniciando login no ComprasNet com usuário {username}")
            
            # Acessa a página de login
            self.page.goto(self.LOGIN_URL)
            
            # Verifica se a página carregou corretamente
            if "Portal de Compras do Governo Federal" not in self.page.title():
                self.logger.error("Página de login do ComprasNet não carregou corretamente")
                return False
            
            # Clica no botão de acesso ao sistema
            self.page.click('text="Acesso ao Sistema"')
            
            # Aguarda carregamento da página de login
            self.page.wait_for_selector('input[name="txtLogin"]')
            
            # Preenche o formulário de login
            self.page.fill('input[name="txtLogin"]', username)
            self.page.fill('input[name="txtSenha"]', password)
            
            # Clica no botão de login
            self.page.click('input[type="submit"]')
            
            # Verifica se o login foi bem-sucedido (aguarda redirecionamento)
            try:
                # Aguarda até 10 segundos pelo redirecionamento ou mensagem de erro
                self.page.wait_for_selector('a:has-text("Sair")', timeout=10000)
                self.logged_in = True
                self.logger.info("Login no ComprasNet realizado com sucesso")
                
                # Salva cookies e dados da sessão
                self.session_data = {
                    "cookies": self.context.cookies(),
                    "storage": self.page.evaluate("() => { return { localStorage: Object.entries(localStorage), sessionStorage: Object.entries(sessionStorage) } }")
                }
                
                return True
            except Exception as e:
                # Verifica se há mensagem de erro na página
                error_text = self.page.inner_text('body') if self.page.query_selector('body') else ""
                if "senha inválida" in error_text.lower() or "usuário inválido" in error_text.lower():
                    self.logger.error("Credenciais inválidas para o ComprasNet")
                else:
                    self.logger.error(f"Erro no login do ComprasNet: {str(e)}")
                return False
                
        except Exception as e:
            self.logger.error(f"Erro ao fazer login no ComprasNet: {str(e)}")
            return False
    
    def login_with_certificate(self, certificate_path: str, certificate_password: Optional[str] = None) -> bool:
        """
        Realiza login no portal ComprasNet usando certificado digital.
        
        Args:
            certificate_path: Caminho para o arquivo do certificado (.pfx)
            certificate_password: Senha do certificado, se necessário
            
        Returns:
            True se login bem-sucedido, False caso contrário
        """
        try:
            # Verifica se o arquivo do certificado existe
            if not os.path.exists(certificate_path):
                self.logger.error(f"Arquivo de certificado não encontrado: {certificate_path}")
                return False
                
            self._initialize_browser()
            self.logger.info(f"Iniciando login com certificado no ComprasNet")
            
            # Acessa a página de login
            self.page.goto(self.LOGIN_URL)
            
            # Clica na opção de login com certificado digital
            self.page.click('text="Acesso por Certificado Digital"')
            
            # Aqui seria necessário implementar a lógica para selecionar o certificado
            # Como o Playwright não suporta diretamente a seleção de certificados,
            # seria necessário usar uma abordagem alternativa, como:
            # 1. Configurar o navegador para usar o certificado automaticamente
            # 2. Usar uma extensão ou ferramenta externa
            
            # Esta implementação é um placeholder e precisaria ser adaptada
            # para um cenário real de uso de certificados
            self.logger.warning("Login com certificado digital não totalmente implementado")
            
            # Verifica se o login foi bem-sucedido
            try:
                # Aguarda até 10 segundos pelo redirecionamento ou elemento que indica sucesso
                self.page.wait_for_selector('a:has-text("Sair")', timeout=10000)
                self.logged_in = True
                self.logger.info("Login com certificado no ComprasNet realizado com sucesso")
                
                # Salva cookies e dados da sessão
                self.session_data = {
                    "cookies": self.context.cookies(),
                    "storage": self.page.evaluate("() => { return { localStorage: Object.entries(localStorage), sessionStorage: Object.entries(sessionStorage) } }")
                }
                
                return True
            except Exception as e:
                self.logger.error(f"Erro no login com certificado: {str(e)}")
                return False
                
        except Exception as e:
            self.logger.error(f"Erro ao fazer login com certificado no ComprasNet: {str(e)}")
            return False
    
    def search_auctions(self, 
                       keywords: Optional[List[str]] = None, 
                       start_date: Optional[datetime] = None,
                       end_date: Optional[datetime] = None,
                       auction_type: Optional[str] = None) -> List[Dict]:
        """
        Busca licitações no portal ComprasNet.
        
        Args:
            keywords: Lista de palavras-chave para busca
            start_date: Data de início para filtro
            end_date: Data de fim para filtro
            auction_type: Tipo de licitação (pregão, dispensa, etc.)
            
        Returns:
            Lista de licitações encontradas
        """
        if not self.logged_in:
            self.logger.error("É necessário estar logado para buscar licitações")
            return []
            
        try:
            self.logger.info("Buscando licitações no ComprasNet")
            
            # Navega para a página de consulta de licitações
            self.page.goto(f"{self.BASE_URL}/consultalicitacoes/ConsLicitacaoDia.asp")
            
            # Preenche os filtros de busca
            if start_date:
                start_date_str = start_date.strftime("%d/%m/%Y")
                self.page.fill('input[name="dt_publ_ini"]', start_date_str)
                
            if end_date:
                end_date_str = end_date.strftime("%d/%m/%Y")
                self.page.fill('input[name="dt_publ_fim"]', end_date_str)
                
            if auction_type:
                # Seleciona o tipo de licitação no dropdown
                self.page.select_option('select[name="tipo_modalidade"]', auction_type)
                
            if keywords and len(keywords) > 0:
                # Preenche o campo de palavras-chave
                keyword_str = " ".join(keywords)
                self.page.fill('input[name="txt_objeto"]', keyword_str)
                
            # Clica no botão de pesquisar
            self.page.click('input[type="submit"]')
            
            # Aguarda o carregamento dos resultados
            self.page.wait_for_selector('table')
            
            # Extrai os resultados da tabela
            results = []
            rows = self.page.query_selector_all('table tr:not(:first-child)')
            
            for row in rows:
                cells = row.query_selector_all('td')
                if len(cells) >= 5:
                    auction_data = {
                        "id": cells[0].inner_text().strip(),
                        "uasg": cells[1].inner_text().strip(),
                        "object": cells[2].inner_text().strip(),
                        "date": cells[3].inner_text().strip(),
                        "status": cells[4].inner_text().strip(),
                        "url": ""
                    }
                    
                    # Tenta obter o link para a licitação
                    link = cells[0].query_selector('a')
                    if link:
                        href = link.get_attribute('href')
                        if href:
                            auction_data["url"] = f"{self.BASE_URL}/{href}"
                    
                    results.append(auction_data)
            
            self.logger.info(f"Encontradas {len(results)} licitações no ComprasNet")
            return results
            
        except Exception as e:
            self.logger.error(f"Erro ao buscar licitações no ComprasNet: {str(e)}")
            return []
    
    def get_auction_details(self, auction_id: str) -> Dict:
        """
        Obtém detalhes de uma licitação específica no ComprasNet.
        
        Args:
            auction_id: Identificador da licitação
            
        Returns:
            Dicionário com detalhes da licitação
        """
        if not self.logged_in:
            self.logger.error("É necessário estar logado para obter detalhes de licitação")
            return {}
            
        try:
            self.logger.info(f"Obtendo detalhes da licitação {auction_id} no ComprasNet")
            
            # Navega para a página de detalhes da licitação
            self.page.goto(f"{self.BASE_URL}/pregao/pregoeiro/ata/ata.asp?co_no_uasg={auction_id.split('-')[0]}&numprp={auction_id.split('-')[1]}")
            
            # Aguarda o carregamento da página
            self.page.wait_for_selector('body')
            
            # Extrai os detalhes da licitação
            details = {
                "id": auction_id,
                "title": self.page.title(),
                "items": []
            }
            
            # Tenta extrair informações básicas
            try:
                details["description"] = self.page.inner_text('td:has-text("Objeto:")')
                details["opening_date"] = self.page.inner_text('td:has-text("Data de Abertura:")')
                details["status"] = self.page.inner_text('td:has-text("Status:")')
            except:
                self.logger.warning(f"Não foi possível extrair todas as informações básicas da licitação {auction_id}")
            
            # Tenta extrair itens da licitação
            try:
                item_rows = self.page.query_selector_all('table:has(th:has-text("Item")) tr:not(:first-child)')
                
                for row in item_rows:
                    cells = row.query_selector_all('td')
                    if len(cells) >= 4:
                        item = {
                            "item_id": cells[0].inner_text().strip(),
                            "description": cells[1].inner_text().strip(),
                            "quantity": cells[2].inner_text().strip(),
                            "unit": cells[3].inner_text().strip()
                        }
                        
                        # Tenta obter o valor de referência, se disponível
                        if len(cells) >= 5:
                            item["reference_value"] = cells[4].inner_text().strip()
                            
                        details["items"].append(item)
            except:
                self.logger.warning(f"Não foi possível extrair itens da licitação {auction_id}")
            
            self.logger.info(f"Detalhes da licitação {auction_id} obtidos com sucesso")
            return details
            
        except Exception as e:
            self.logger.error(f"Erro ao obter detalhes da licitação {auction_id}: {str(e)}")
            return {"id": auction_id, "error": str(e)}
    
    def submit_proposal(self, 
                       auction_id: str, 
                       item_id: str,
                       price: float,
                       additional_data: Optional[Dict] = None) -> bool:
        """
        Submete uma proposta para um item de licitação no ComprasNet.
        
        Args:
            auction_id: Identificador da licitação
            item_id: Identificador do item
            price: Valor da proposta
            additional_data: Dados adicionais específicos do portal
            
        Returns:
            True se proposta enviada com sucesso, False caso contrário
        """
        if not self.logged_in:
            self.logger.error("É necessário estar logado para submeter proposta")
            return False
            
        try:
            self.logger.info(f"Submetendo proposta para item {item_id} da licitação {auction_id}")
            
            # Navega para a página de propostas da licitação
            uasg, pregao = auction_id.split('-')
            self.page.goto(f"{self.BASE_URL}/pregao/fornec/proposta.asp?prgcod={pregao}&uasg={uasg}")
            
            # Aguarda o carregamento da página
            self.page.wait_for_selector('body')
            
            # Verifica se estamos na página correta
            if "Proposta" not in self.page.title():
                self.logger.error("Não foi possível acessar a página de propostas")
                return False
            
     
(Content truncated due to size limit. Use line ranges to read in chunks)
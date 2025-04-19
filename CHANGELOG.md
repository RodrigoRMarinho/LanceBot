# Changelog do LanceBot

## [0.2.0] - 2025-04-19
### Adicionado
- Implementação completa do sistema de logging (src/core/logger.py)
- Implementação do sistema de estratégias de lance (src/core/bidding.py)
- Interface base para portais de licitação (src/portals/__init__.py)
- Implementação específica para o portal ComprasNet (src/portals/comprasnet/)
- Implementação específica para o Portal de Compras Públicas (src/portals/portaldecompras/)
- Implementação específica para o portal BLL Compras (src/portals/bllcompras/)
- Implementação específica para o portal Licitações-e (src/portals/licitacoes_e/)
- Script principal para testes manuais (main.py)
- Testes automatizados para o sistema de estratégias de lance (tests/test_bidding.py)
- Testes automatizados para o sistema de logging (tests/test_logger.py)
- Testes automatizados para a classe base de portais (tests/test_portal_base.py)
- Arquivo de requisitos (requirements.txt)

### Alterado
- Estrutura de diretórios reorganizada conforme padrões de projeto Python
- Documentação atualizada com instruções de uso e configuração

## [0.1.0] - 2025-04-18
### Adicionado
- Documentação inicial do projeto
- Protótipo de interface de usuário
- Estrutura básica do repositório

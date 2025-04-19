# Ambiente de Desenvolvimento

## 📋 Pré-requisitos
- Python 3.10+
- Node.js 16+
- Playwright (`npm install playwright`)
- Certificado digital A1/A3 (para testes de autenticação)

## 🏗️ Estrutura do Projeto
src/
├── core/ # Lógica principal do bot
│ ├── bidding.py # Estratégias de lance
│ └── logger.py # Sistema de logs
├── portals/ # Integrações com portais
│ └── comprasnet/ # Implementação específica
└── ui/ # Interface Electron
├── main.js
└── renderer.js

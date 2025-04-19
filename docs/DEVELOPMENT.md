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

## 🔧 Configuração Inicial
```bash
# Instale dependências Python
pip install -r requirements.txt

# Instale dependências Node.js
npm install

# Configure ambiente de testes
playwright install
git checkout -b feat/nome-da-feature
npm run lint  # Verifique estilo de código
npm run build # Teste o build
# Modo debug (mostra o navegador)
DEBUG=pw:api npm start
npm run package  # Cria executáveis

### ⚙️ **.github/workflows/ci.yml**
```yaml
name: CI Pipeline

on: [push, pull_request]

jobs:
  test:
    name: Test Runner
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.10']
        node-version: ['16.x']

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Set up Node.js ${{ matrix.node-version }}
      uses: actions/setup-node@v3
      with:
        node-version: ${{ matrix.node-version }}

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        npm ci
        npx playwright install --with-deps

    - name: Run Python tests
      run: |
        pytest tests/unit --cov=src --cov-report=xml

    - name: Run JavaScript tests
      run: |
        npm run test

    - name: Upload coverage
      uses: codecov/codecov-action@v3

  lint:
    name: Linter
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-node@v3
      with:
        node-version: '16.x'
    - run: npm ci
    - run: npm run lint
    - run: npm run type-check

#!/bin/bash

# Script para configurar o ambiente de desenvolvimento do LanceBot

# Verifica se o Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "Python 3 não encontrado. Por favor, instale o Python 3.10 ou superior."
    exit 1
fi

# Verifica a versão do Python
python_version=$(python3 --version | cut -d ' ' -f 2)
python_major=$(echo $python_version | cut -d '.' -f 1)
python_minor=$(echo $python_version | cut -d '.' -f 2)

if [ "$python_major" -lt 3 ] || ([ "$python_major" -eq 3 ] && [ "$python_minor" -lt 10 ]); then
    echo "Versão do Python incompatível. É necessário Python 3.10 ou superior."
    echo "Versão atual: $python_version"
    exit 1
fi

# Cria ambiente virtual
echo "Criando ambiente virtual..."
python3 -m venv venv

# Ativa o ambiente virtual
echo "Ativando ambiente virtual..."
source venv/bin/activate

# Instala dependências
echo "Instalando dependências..."
pip install -r requirements.txt

# Instala o Playwright
echo "Instalando Playwright..."
playwright install

# Cria diretórios necessários
echo "Criando diretórios necessários..."
mkdir -p logs sessions

# Cria arquivo de credenciais de exemplo se não existir
if [ ! -f LOGIN.env ]; then
    echo "Criando arquivo de credenciais de exemplo..."
    cp LOGIN.env LOGIN.env.example
    echo "# Exemplo (não use dados reais!)" > LOGIN.env.example
    echo "COMPRASNET_USER=\"seu_usuario\"" >> LOGIN.env.example
    echo "COMPRASNET_PASS=\"sua_senha\"" >> LOGIN.env.example
    echo "PORTALDECOMPRAS_USER=\"seu_email@exemplo.com\"" >> LOGIN.env.example
    echo "PORTALDECOMPRAS_PASS=\"sua_senha\"" >> LOGIN.env.example
    echo "BLLCOMPRAS_USER=\"seu_email@exemplo.com\"" >> LOGIN.env.example
    echo "BLLCOMPRAS_PASS=\"sua_senha\"" >> LOGIN.env.example
    echo "LICITACOESE_USER=\"seu_usuario\"" >> LOGIN.env.example
    echo "LICITACOESE_PASS=\"sua_senha\"" >> LOGIN.env.example
    echo "CERTIFICADO_PATH=\"caminho/do/certificado.pfx\"" >> LOGIN.env.example
    echo "CERTIFICADO_PASS=\"senha_do_certificado\"" >> LOGIN.env.example
fi

echo "Ambiente configurado com sucesso!"
echo "Para ativar o ambiente virtual, execute: source venv/bin/activate"
echo "Para testar o LanceBot, execute: python main.py --help"

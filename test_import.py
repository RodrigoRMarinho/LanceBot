import sys
import os

# Adicionar o diretório src ao PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

try:
    from core.logger import LanceLogger
    print("✅ Importação do LanceLogger bem-sucedida!")

    # Instanciar o logger e testar os métodos
    logger = LanceLogger()

    logger.info("🟢 INFO funcionando!")
    logger.warning("🟡 WARNING funcionando!")
    logger.error("🔴 ERROR funcionando!")
    logger.debug("🔵 DEBUG funcionando!")
    logger.critical("⚫ CRITICAL funcionando!")

    # Teste de exceção
    try:
        1 / 0
    except Exception as ex:
        logger.log_exception(ex, context="Teste de exceção")

except Exception as e:
    print(f"❌ Erro ao importar LanceLogger: {e}")



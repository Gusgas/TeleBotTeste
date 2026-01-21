import os

# Pega as variáveis de ambiente
BOT_TOKEN = os.environ.get("BOT_TOKEN")
MP_ACCESS_TOKEN = os.environ.get("MP_ACCESS_TOKEN")
GROUP_ID = os.environ.get("GROUP_ID")

# Checagem rápida para garantir que tudo foi carregado
if not BOT_TOKEN or not MP_ACCESS_TOKEN or not GROUP_ID:
    raise ValueError("⚠️ Variáveis de ambiente não configuradas corretamente!")

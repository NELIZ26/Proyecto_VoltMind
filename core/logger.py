import logging
import sys

# Configuramos el formato: Fecha - Nivel - Mensaje
FORMATO = "%(asctime)s - %(levelname)s - %(message)s"

# Configuramos el logger principal
logging.basicConfig(
    level=logging.INFO,
    format=FORMATO,
    handlers=[
        # 1. Esto guarda los errores en un archivo llamado "voltmind.log"
        logging.FileHandler("voltmind.log", encoding="utf-8"),
        # 2. Esto sigue mostrando los mensajes en tu terminal de VS Code
        logging.StreamHandler(sys.stdout)
    ]
)
log = logging.getLogger("voltmind")
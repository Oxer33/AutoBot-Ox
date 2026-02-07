# ============================================
# Sistema di Logging - AutoBot Ox
# Configura il logging per tutta l'applicazione
# I log vengono scritti sia su console che su file
# ============================================

import logging
import os
from pathlib import Path
from datetime import datetime

# Cartella dove salveremo i file di log
LOG_DIR = Path(__file__).resolve().parent.parent / "logs"


def configura_logging(livello: int = logging.DEBUG) -> logging.Logger:
    """
    Configura il sistema di logging per tutta l'applicazione.
    
    Cosa fa:
    - Crea una cartella 'logs' se non esiste
    - Scrive i log sia sulla console (terminale) che su un file
    - Il file di log ha il nome con la data corrente (es. autobot_2025-02-07.log)
    
    Args:
        livello: Il livello minimo di log da catturare (default: DEBUG = tutto)
        
    Returns:
        Il logger principale dell'applicazione
    """
    # Crea la cartella logs se non esiste
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    # Nome del file di log con la data di oggi
    nome_file_log = f"autobot_{datetime.now().strftime('%Y-%m-%d')}.log"
    percorso_log = LOG_DIR / nome_file_log

    # Formato dei messaggi di log
    # Esempio: 2025-02-07 14:30:00 | INFO | Config | Configurazione caricata
    formato = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Logger principale
    logger = logging.getLogger("AutoBotOx")
    logger.setLevel(livello)

    # Evita di aggiungere handler duplicati se la funzione viene chiamata più volte
    if logger.handlers:
        return logger

    # Handler per la console (mostra i log nel terminale)
    handler_console = logging.StreamHandler()
    handler_console.setLevel(logging.INFO)  # Console: solo INFO e superiori
    handler_console.setFormatter(formato)

    # Handler per il file (salva TUTTI i log, anche DEBUG)
    handler_file = logging.FileHandler(
        percorso_log,
        encoding="utf-8",
        mode="a"  # 'a' = append, aggiunge ai log esistenti
    )
    handler_file.setLevel(logging.DEBUG)
    handler_file.setFormatter(formato)

    # Aggiungi entrambi gli handler al logger
    logger.addHandler(handler_console)
    logger.addHandler(handler_file)

    logger.info(f"📝 Sistema di logging inizializzato. File log: {percorso_log}")
    return logger


def ottieni_logger(nome_modulo: str) -> logging.Logger:
    """
    Ottiene un logger figlio per un modulo specifico.
    
    Esempio: ottieni_logger("HealthCheck") -> logger con nome "AutoBotOx.HealthCheck"
    
    Args:
        nome_modulo: Nome del modulo (es. "GUI", "Core", "HealthCheck")
        
    Returns:
        Un logger configurato per il modulo
    """
    return logging.getLogger(f"AutoBotOx.{nome_modulo}")

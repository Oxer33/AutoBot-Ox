# ============================================
# Export Cronologia Chat - AutoBot Ox
# Permette di salvare la cronologia della chat
# in formato .txt o .md
# ============================================

import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# Logger per questo modulo
logger = logging.getLogger("AutoBotOx.HistoryExport")


class EsportaCronologia:
    """
    Gestisce l'esportazione della cronologia chat.
    
    Supporta due formati:
    - .txt: Testo semplice, facile da leggere
    - .md: Markdown, formattato con codice evidenziato
    """

    @staticmethod
    def esporta_txt(messaggi: List[Dict], percorso: str) -> bool:
        """
        Esporta la cronologia in formato testo semplice.
        
        Args:
            messaggi: Lista di messaggi della chat
            percorso: Percorso dove salvare il file
            
        Returns:
            True se l'esportazione è riuscita, False altrimenti
        """
        try:
            with open(percorso, "w", encoding="utf-8") as f:
                # Intestazione
                f.write("=" * 60 + "\n")
                f.write(f"  AutoBot Ox - Cronologia Chat\n")
                f.write(f"  Data esportazione: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 60 + "\n\n")

                # Messaggi
                for msg in messaggi:
                    ruolo = msg.get("role", "sconosciuto").upper()
                    contenuto = msg.get("content", "")
                    tipo = msg.get("type", "message")

                    if tipo == "message":
                        f.write(f"[{ruolo}]\n{contenuto}\n\n")
                    elif tipo == "code":
                        linguaggio = msg.get("format", "python")
                        f.write(f"[{ruolo} - CODICE ({linguaggio})]\n{contenuto}\n\n")
                    elif tipo == "console":
                        f.write(f"[OUTPUT CONSOLE]\n{contenuto}\n\n")

                    f.write("-" * 40 + "\n\n")

            logger.info(f"✅ Cronologia esportata in TXT: {percorso}")
            return True

        except Exception as e:
            logger.error(f"❌ Errore esportazione TXT: {e}")
            return False

    @staticmethod
    def esporta_md(messaggi: List[Dict], percorso: str) -> bool:
        """
        Esporta la cronologia in formato Markdown.
        
        Args:
            messaggi: Lista di messaggi della chat
            percorso: Percorso dove salvare il file
            
        Returns:
            True se l'esportazione è riuscita, False altrimenti
        """
        try:
            with open(percorso, "w", encoding="utf-8") as f:
                # Intestazione Markdown
                f.write(f"# AutoBot Ox - Cronologia Chat\n\n")
                f.write(f"**Data esportazione:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write("---\n\n")

                # Messaggi
                for i, msg in enumerate(messaggi, 1):
                    ruolo = msg.get("role", "sconosciuto")
                    contenuto = msg.get("content", "")
                    tipo = msg.get("type", "message")

                    if ruolo == "user":
                        f.write(f"### 👤 Utente\n\n{contenuto}\n\n")
                    elif ruolo == "assistant" and tipo == "message":
                        f.write(f"### 🤖 Assistente\n\n{contenuto}\n\n")
                    elif ruolo == "assistant" and tipo == "code":
                        linguaggio = msg.get("format", "python")
                        f.write(f"### 💻 Codice ({linguaggio})\n\n")
                        f.write(f"```{linguaggio}\n{contenuto}\n```\n\n")
                    elif tipo == "console":
                        f.write(f"### 📟 Output Console\n\n")
                        f.write(f"```\n{contenuto}\n```\n\n")

                    f.write("---\n\n")

            logger.info(f"✅ Cronologia esportata in MD: {percorso}")
            return True

        except Exception as e:
            logger.error(f"❌ Errore esportazione MD: {e}")
            return False

    @staticmethod
    def genera_nome_file(formato: str = "md") -> str:
        """
        Genera un nome file unico basato sulla data e ora corrente.
        
        Args:
            formato: Estensione del file ('txt' o 'md')
            
        Returns:
            Nome del file generato (es. "chat_2025-02-07_14-30-00.md")
        """
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        return f"chat_{timestamp}.{formato}"

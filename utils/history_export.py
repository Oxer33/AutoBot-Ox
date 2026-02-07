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
                # NOTA: In open-interpreter v0.1.x il formato dei messaggi è:
                # {"role": "user", "message": "..."}
                # {"role": "assistant", "message": "...", "code": "...", "language": "...", "output": "..."}
                for msg in messaggi:
                    ruolo = msg.get("role", "sconosciuto").upper()
                    # Supporta sia "message" (v0.1.x) che "content" (formato custom)
                    contenuto = msg.get("message", msg.get("content", ""))

                    # Scrivi il messaggio testuale
                    if contenuto:
                        f.write(f"[{ruolo}]\n{contenuto}\n\n")

                    # Scrivi il codice (se presente)
                    codice = msg.get("code", "")
                    if codice:
                        linguaggio = msg.get("language", "python")
                        f.write(f"[{ruolo} - CODICE ({linguaggio})]\n{codice}\n\n")

                    # Scrivi l'output (se presente)
                    output = msg.get("output", "")
                    if output:
                        f.write(f"[OUTPUT CONSOLE]\n{output}\n\n")

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
                # NOTA: In open-interpreter v0.1.x il formato dei messaggi è:
                # {"role": "user", "message": "..."}
                # {"role": "assistant", "message": "...", "code": "...", "language": "...", "output": "..."}
                for i, msg in enumerate(messaggi, 1):
                    ruolo = msg.get("role", "sconosciuto")
                    # Supporta sia "message" (v0.1.x) che "content" (formato custom)
                    contenuto = msg.get("message", msg.get("content", ""))
                    codice = msg.get("code", "")
                    output = msg.get("output", "")
                    linguaggio = msg.get("language", "python")

                    if ruolo == "user":
                        f.write(f"### 👤 Utente\n\n{contenuto}\n\n")
                    elif ruolo == "assistant":
                        # Messaggio testuale
                        if contenuto:
                            f.write(f"### 🤖 Assistente\n\n{contenuto}\n\n")
                        # Codice generato
                        if codice:
                            f.write(f"### 💻 Codice ({linguaggio})\n\n")
                            f.write(f"```{linguaggio}\n{codice}\n```\n\n")
                        # Output esecuzione
                        if output:
                            f.write(f"### 📟 Output Console\n\n")
                            f.write(f"```\n{output}\n```\n\n")

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

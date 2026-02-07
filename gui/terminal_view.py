# ============================================
# Terminal View (Vista Terminale) - AutoBot Ox
# Area a sfondo nero che mostra il codice Python
# in esecuzione e il relativo output
# ============================================

import logging
import customtkinter as ctk
from typing import Optional
from datetime import datetime

# Logger per questo modulo
logger = logging.getLogger("AutoBotOx.GUI.TerminalView")


class TerminalView(ctk.CTkFrame):
    """
    Vista terminale che mostra il codice e l'output in tempo reale.
    
    Simula un terminale con sfondo nero e testo verde/bianco,
    come quelli che si vedono nei film sugli hacker! 😄
    
    Mostra:
    - Il codice che l'IA genera (evidenziato in verde)
    - L'output dell'esecuzione (in bianco)
    - Gli errori (in rosso)
    - I log di sistema (in giallo)
    """

    def __init__(self, master, **kwargs):
        """
        Crea la vista terminale.
        
        Args:
            master: Widget genitore
        """
        super().__init__(master, **kwargs)

        self.configure(fg_color="transparent")

        # Costruisci l'interfaccia
        self._costruisci_ui()

        # Contatore linee per numerazione
        self._num_linea = 0

        logger.info("🖥️ TerminalView costruita")

    def _costruisci_ui(self) -> None:
        """Costruisce tutti gli elementi della vista terminale."""

        # ========== HEADER ==========
        header = ctk.CTkFrame(self, height=35, fg_color=("gray85", "gray17"))
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="🖥️ Terminale",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=15, pady=5)

        # Pulsante per pulire il terminale
        btn_pulisci = ctk.CTkButton(
            header,
            text="🧹 Pulisci",
            width=80,
            height=25,
            command=self.pulisci,
            font=ctk.CTkFont(size=11),
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray40")
        )
        btn_pulisci.pack(side="right", padx=10, pady=5)

        # ========== AREA TERMINALE ==========
        # Usiamo un CTkTextbox perché permette testo colorato e scrolling
        self._textbox = ctk.CTkTextbox(
            self,
            font=ctk.CTkFont(family="Consolas", size=12),
            fg_color="#0d0d0d",           # Sfondo nero intenso
            text_color="#00ff00",          # Testo verde (stile Matrix!)
            corner_radius=0,
            wrap="word",                   # Vai a capo automaticamente
            state="disabled",              # Solo lettura (l'utente non può scrivere)
            activate_scrollbars=True
        )
        self._textbox.pack(fill="both", expand=True, padx=0, pady=0)

        # Testo iniziale
        self._scrivi_raw(
            "╔══════════════════════════════════════════════════╗\n"
            "║        AutoBot Ox - Terminale v1.0.0            ║\n"
            "║        Pronto per eseguire comandi               ║\n"
            "╚══════════════════════════════════════════════════╝\n\n",
            colore="verde"
        )

    def _scrivi_raw(self, testo: str, colore: str = "verde") -> None:
        """
        Scrive testo nel terminale.
        
        Args:
            testo: Il testo da scrivere
            colore: "verde", "bianco", "rosso", "giallo", "ciano"
        """
        # Abilita la scrittura temporaneamente
        self._textbox.configure(state="normal")

        # Mappa colori
        mappa_colori = {
            "verde": "#00ff00",
            "bianco": "#e0e0e0",
            "rosso": "#ff4444",
            "giallo": "#ffeb3b",
            "ciano": "#00bcd4",
            "grigio": "#757575"
        }

        colore_hex = mappa_colori.get(colore, "#00ff00")

        # Inserisci il testo
        self._textbox.insert("end", testo)

        # Disabilita la scrittura
        self._textbox.configure(state="disabled")

        # Scrolla in basso
        self._textbox.see("end")

    def scrivi_codice(self, codice: str, linguaggio: str = "python") -> None:
        """
        Mostra del codice nel terminale con formattazione appropriata.
        
        Args:
            codice: Il codice sorgente da mostrare
            linguaggio: Il linguaggio di programmazione
        """
        self._num_linea += 1
        timestamp = datetime.now().strftime("%H:%M:%S")

        header = f"\n[{timestamp}] 💻 CODICE ({linguaggio.upper()}):\n"
        separatore = "─" * 50 + "\n"

        self._scrivi_raw(header, "ciano")
        self._scrivi_raw(separatore, "grigio")
        self._scrivi_raw(codice + "\n", "verde")
        self._scrivi_raw(separatore, "grigio")

        logger.debug(f"🖥️ Codice scritto nel terminale ({linguaggio})")

    def scrivi_output(self, output: str) -> None:
        """
        Mostra l'output di un comando nel terminale.
        
        Args:
            output: L'output da mostrare
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        header = f"[{timestamp}] 📟 OUTPUT:\n"

        self._scrivi_raw(header, "bianco")
        self._scrivi_raw(output + "\n", "bianco")

        logger.debug("🖥️ Output scritto nel terminale")

    def scrivi_errore(self, errore: str) -> None:
        """
        Mostra un errore nel terminale (in rosso).
        
        Args:
            errore: Il messaggio di errore
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        header = f"\n[{timestamp}] ❌ ERRORE:\n"

        self._scrivi_raw(header, "rosso")
        self._scrivi_raw(errore + "\n", "rosso")

        logger.debug("🖥️ Errore scritto nel terminale")

    def scrivi_log(self, messaggio: str) -> None:
        """
        Mostra un messaggio di log nel terminale (in giallo).
        
        Args:
            messaggio: Il messaggio di log
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        self._scrivi_raw(f"[{timestamp}] ℹ️ {messaggio}\n", "giallo")

    def scrivi_stato(self, stato: str) -> None:
        """
        Mostra un cambio di stato nel terminale.
        
        Args:
            stato: Il messaggio di stato
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        self._scrivi_raw(f"[{timestamp}] 🔄 {stato}\n", "ciano")

    def pulisci(self) -> None:
        """Pulisce tutto il contenuto del terminale."""
        self._textbox.configure(state="normal")
        self._textbox.delete("1.0", "end")
        self._textbox.configure(state="disabled")
        self._num_linea = 0

        # Rimetti l'header
        self._scrivi_raw(
            "╔══════════════════════════════════════════════════╗\n"
            "║        Terminale pulito                          ║\n"
            "╚══════════════════════════════════════════════════╝\n\n",
            colore="verde"
        )
        logger.info("🧹 Terminale pulito")

    def ottieni_contenuto(self) -> str:
        """
        Restituisce tutto il testo contenuto nel terminale.
        Utile per l'esportazione.
        
        Returns:
            Tutto il testo del terminale
        """
        self._textbox.configure(state="normal")
        contenuto = self._textbox.get("1.0", "end")
        self._textbox.configure(state="disabled")
        return contenuto

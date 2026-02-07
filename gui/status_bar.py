# ============================================
# Status Bar (Barra di Stato) - AutoBot Ox
# Mostra informazioni in tempo reale nella parte
# inferiore della finestra:
# - Stato server locale (Online/Offline)
# - Modello attivo
# - Token utilizzati
# - Uso memoria
# ============================================

import logging
import psutil
import customtkinter as ctk
from typing import Optional

# Logger per questo modulo
logger = logging.getLogger("AutoBotOx.GUI.StatusBar")


class StatusBar(ctk.CTkFrame):
    """
    Barra di stato nella parte inferiore della finestra.
    
    Mostra informazioni utili in tempo reale:
    - Stato del server LLM locale (pallino verde/rosso)
    - Nome del modello attualmente in uso
    - Contatore token utilizzati (per OpenRouter)
    - Utilizzo memoria RAM
    """

    def __init__(self, master, **kwargs):
        """
        Crea la barra di stato.
        
        Args:
            master: Widget genitore
        """
        super().__init__(master, **kwargs)

        # Configura lo stile
        self.configure(
            height=30,
            fg_color=("gray80", "gray15"),
            corner_radius=0
        )
        self.pack_propagate(False)  # Impedisce al frame di ridimensionarsi

        # Costruisci l'interfaccia
        self._costruisci_ui()

        logger.info("📊 StatusBar costruita")

    def _costruisci_ui(self) -> None:
        """Costruisce tutti gli elementi della status bar."""

        # ========== STATO SERVER LOCALE ==========
        self._frame_stato_server = ctk.CTkFrame(self, fg_color="transparent")
        self._frame_stato_server.pack(side="left", padx=10, pady=2)

        self._label_server = ctk.CTkLabel(
            self._frame_stato_server,
            text="● Server Locale: Verifica...",
            font=ctk.CTkFont(size=11),
            text_color="orange"
        )
        self._label_server.pack(side="left")

        # Separatore verticale
        self._crea_separatore()

        # ========== MODELLO ATTIVO ==========
        self._label_modello = ctk.CTkLabel(
            self,
            text="🤖 Modello: Nessuno",
            font=ctk.CTkFont(size=11),
            text_color=("gray30", "gray70")
        )
        self._label_modello.pack(side="left", padx=10, pady=2)

        # Separatore verticale
        self._crea_separatore()

        # ========== TOKEN COUNTER ==========
        self._label_token = ctk.CTkLabel(
            self,
            text="📊 Token: 0",
            font=ctk.CTkFont(size=11),
            text_color=("gray30", "gray70")
        )
        self._label_token.pack(side="left", padx=10, pady=2)

        # Separatore verticale
        self._crea_separatore()

        # ========== USO MEMORIA ==========
        self._label_memoria = ctk.CTkLabel(
            self,
            text="💾 RAM: --%",
            font=ctk.CTkFont(size=11),
            text_color=("gray30", "gray70")
        )
        self._label_memoria.pack(side="right", padx=10, pady=2)

        # Aggiorna la memoria periodicamente
        self._aggiorna_memoria()

    def _crea_separatore(self) -> None:
        """Crea un separatore verticale nella status bar."""
        sep = ctk.CTkFrame(
            self,
            width=1,
            fg_color=("gray60", "gray40")
        )
        sep.pack(side="left", fill="y", padx=5, pady=4)

    # ==========================================
    # Metodi pubblici per aggiornare lo stato
    # ==========================================

    def aggiorna_stato_server(self, online: bool) -> None:
        """
        Aggiorna l'indicatore di stato del server locale.
        
        Args:
            online: True se il server è raggiungibile
        """
        if online:
            self._label_server.configure(
                text="● Server Locale: Online",
                text_color="#4caf50"  # Verde
            )
        else:
            self._label_server.configure(
                text="● Server Locale: Offline",
                text_color="#f44336"  # Rosso
            )

    def aggiorna_modello(self, nome_modello: str) -> None:
        """
        Aggiorna il nome del modello attivo mostrato.
        
        Args:
            nome_modello: Nome del modello (es. "DeepSeek R1")
        """
        # Tronca se troppo lungo
        if len(nome_modello) > 30:
            nome_modello = nome_modello[:27] + "..."
        self._label_modello.configure(text=f"🤖 {nome_modello}")

    def aggiorna_token(self, testo_token: str) -> None:
        """
        Aggiorna il contatore token.
        
        Args:
            testo_token: Testo formattato (es. "Token: 1,234")
        """
        self._label_token.configure(text=f"📊 {testo_token}")

    def _aggiorna_memoria(self) -> None:
        """
        Aggiorna l'indicatore di utilizzo memoria RAM.
        Si auto-aggiorna ogni 5 secondi.
        """
        try:
            # psutil.virtual_memory() ci dice quanta RAM sta usando il PC
            memoria = psutil.virtual_memory()
            percentuale = memoria.percent
            usata_gb = memoria.used / (1024 ** 3)  # Converti in GB
            totale_gb = memoria.total / (1024 ** 3)

            # Colore basato sull'utilizzo
            if percentuale < 60:
                colore = "#4caf50"  # Verde
            elif percentuale < 80:
                colore = "#ff9800"  # Arancione
            else:
                colore = "#f44336"  # Rosso

            self._label_memoria.configure(
                text=f"💾 RAM: {usata_gb:.1f}/{totale_gb:.1f}GB ({percentuale:.0f}%)",
                text_color=colore
            )
        except Exception as e:
            logger.debug(f"⚠️ Errore lettura memoria: {e}")
            self._label_memoria.configure(text="💾 RAM: N/D")

        # Ripeti ogni 5 secondi
        self.after(5000, self._aggiorna_memoria)

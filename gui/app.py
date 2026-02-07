# ============================================
# App Principale - AutoBot Ox
# Finestra principale che assembla tutti i componenti:
# - Sidebar (impostazioni)
# - Chat View (interfaccia chat)
# - Terminal View (output codice)
# - Status Bar (info in tempo reale)
#
# Qui tutto viene collegato insieme!
# ============================================

import logging
import os
import threading
import customtkinter as ctk
from tkinter import filedialog
from typing import Optional

# Importa i componenti della GUI
from gui.sidebar import Sidebar
from gui.chat_view import ChatView
from gui.terminal_view import TerminalView
from gui.status_bar import StatusBar
from gui.dialogs import (
    DialogoErrore,
    DialogoConferma,
    DialogoDebug,
    DialogoApprovazioneCodice
)

# Importa i moduli core
from core.interpreter_wrapper import WrapperInterpreter, TipoMessaggio
from core.provider_manager import GestoreProvider
from core.health_check import ControlloSalute

# Importa le utilità
from config.settings import GestoreImpostazioni
from utils.token_counter import ContaToken
from utils.history_export import EsportaCronologia

# Logger per questo modulo
logger = logging.getLogger("AutoBotOx.GUI.App")

# Intervallo in millisecondi per il polling della coda messaggi
INTERVALLO_POLLING_MS = 100


class AppAutoBot(ctk.CTk):
    """
    Finestra principale dell'applicazione AutoBot Ox.
    
    Questa è la classe "regina" che:
    1. Crea tutti i componenti della GUI
    2. Li collega tra loro tramite callback
    3. Gestisce il flusso dei dati tra GUI e interprete
    4. Si occupa del polling periodico dei messaggi
    
    Per chi è nuovo al codice:
    - CTk è la finestra principale dell'applicazione
    - Ogni componente (sidebar, chat, ecc.) è un "pezzo" della finestra
    - I callback sono funzioni che vengono chiamate quando succede qualcosa
      (es. l'utente preme un pulsante)
    """

    def __init__(self):
        """Inizializza la finestra principale e tutti i componenti."""
        super().__init__()

        logger.info("🚀 Avvio AutoBot Ox...")

        # ==========================================
        # Inizializza i componenti core
        # ==========================================

        # Gestore impostazioni (carica/salva configurazione)
        self._impostazioni = GestoreImpostazioni()

        # Gestore provider LLM (locale/cloud)
        self._provider_manager = GestoreProvider()
        self._configura_providers()

        # Wrapper dell'interprete (il cuore dell'app)
        self._interpreter = WrapperInterpreter()

        # Contatore token (per OpenRouter)
        self._token_counter = ContaToken()

        # Esportatore cronologia
        self._exporter = EsportaCronologia()

        # Health check del server locale
        self._health_check = ControlloSalute(
            url_server=self._impostazioni.ottieni(
                "provider_locale.api_base", "http://localhost:1234/v1"
            ) + "/models",
            intervallo_secondi=self._impostazioni.ottieni(
                "health_check.intervallo_secondi", 5
            ),
            callback_stato=self._on_cambio_stato_server
        )

        # ==========================================
        # Configura la finestra principale
        # ==========================================

        self.title("AutoBot Ox - AI Agent Desktop v1.0.0")
        
        # Dimensioni finestra
        dimensioni = self._impostazioni.ottieni("interfaccia.dimensione_finestra", "1400x900")
        self.geometry(dimensioni)
        self.minsize(1000, 600)

        # Tema scuro (come richiesto!)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # ==========================================
        # Costruisci il layout della GUI
        # ==========================================
        self._costruisci_layout()

        # ==========================================
        # Carica le impostazioni salvate nella GUI
        # ==========================================
        self._carica_impostazioni_gui()

        # ==========================================
        # Avvia i servizi in background
        # ==========================================

        # Avvia il health check del server locale
        self._health_check.avvia()

        # Avvia il polling della coda messaggi
        self._avvia_polling()

        # Inizializza l'interprete con il provider corrente
        self._inizializza_interprete()

        # Gestisci la chiusura della finestra
        self.protocol("WM_DELETE_WINDOW", self._on_chiusura)

        logger.info("✅ AutoBot Ox avviato con successo!")

    def _costruisci_layout(self) -> None:
        """
        Costruisce il layout principale della finestra.
        
        Layout:
        ┌──────────┬────────────────────────────────┐
        │          │         Chat View               │
        │ Sidebar  ├────────────────────────────────┤
        │          │       Terminal View              │
        ├──────────┴────────────────────────────────┤
        │              Status Bar                    │
        └───────────────────────────────────────────┘
        """
        # Configura il grid layout principale
        self.grid_columnconfigure(0, weight=0)  # Sidebar: larghezza fissa
        self.grid_columnconfigure(1, weight=1)  # Area principale: espandibile
        self.grid_rowconfigure(0, weight=1)     # Area principale: espandibile
        self.grid_rowconfigure(1, weight=0)     # Status bar: altezza fissa

        # ========== SIDEBAR ==========
        self._sidebar = Sidebar(
            self,
            callback_cambio_provider=self._on_cambio_provider,
            callback_toggle_autorun=self._on_toggle_autorun,
            callback_cambio_cartella=self._on_cambio_cartella,
            callback_nuova_chat=self._on_nuova_chat,
            callback_export=self._on_export_cronologia,
            callback_salva_apikey=self._on_salva_apikey
        )
        self._sidebar.grid(row=0, column=0, sticky="nsw")

        # ========== AREA PRINCIPALE (Chat + Terminal) ==========
        # Usiamo un PanedWindow per permettere il ridimensionamento
        area_principale = ctk.CTkFrame(self, fg_color="transparent")
        area_principale.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        area_principale.grid_rowconfigure(0, weight=3)  # Chat: 3/4 dello spazio
        area_principale.grid_rowconfigure(1, weight=1)  # Terminal: 1/4 dello spazio
        area_principale.grid_columnconfigure(0, weight=1)

        # Chat View
        self._chat_view = ChatView(
            area_principale,
            callback_invia=self._on_invia_messaggio,
            callback_stop=self._on_emergency_stop,
            callback_approva=self._on_approva_codice,
            callback_rifiuta=self._on_rifiuta_codice
        )
        self._chat_view.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)

        # Terminal View
        self._terminal_view = TerminalView(area_principale)
        self._terminal_view.grid(row=1, column=0, sticky="nsew", padx=0, pady=(2, 0))

        # ========== STATUS BAR ==========
        self._status_bar = StatusBar(self)
        self._status_bar.grid(row=1, column=0, columnspan=2, sticky="sew")

        logger.info("📐 Layout costruito")

    def _configura_providers(self) -> None:
        """Configura i provider LLM dalle impostazioni."""
        # Provider Locale
        self._provider_manager.registra_locale(
            api_base=self._impostazioni.ottieni(
                "provider_locale.api_base", "http://localhost:1234/v1"
            ),
            modello=self._impostazioni.ottieni(
                "provider_locale.modello", "openai/local"
            ),
            timeout=self._impostazioni.ottieni(
                "provider_locale.timeout_secondi", 30
            )
        )

        # Provider Cloud (OpenRouter)
        self._provider_manager.registra_cloud(
            api_base=self._impostazioni.ottieni(
                "provider_cloud.api_base", "https://openrouter.ai/api/v1"
            ),
            modello=self._impostazioni.ottieni(
                "provider_cloud.modello", "deepseek/deepseek-r1-0528:free"
            ),
            api_key=self._impostazioni.ottieni(
                "provider_cloud.api_key", ""
            ),
            timeout=self._impostazioni.ottieni(
                "provider_cloud.timeout_secondi", 60
            )
        )

        # Seleziona il provider attivo
        provider_attivo = self._impostazioni.ottieni("provider_attivo", "locale")
        self._provider_manager.seleziona_provider(provider_attivo)

        logger.info("🔌 Provider configurati")

    def _carica_impostazioni_gui(self) -> None:
        """Carica le impostazioni salvate e le applica alla GUI."""
        # Provider attivo
        provider = self._impostazioni.ottieni("provider_attivo", "locale")
        self._sidebar.imposta_provider(provider)

        # API key
        api_key = self._impostazioni.api_key_openrouter
        if api_key:
            self._sidebar.imposta_apikey(api_key)

        # Auto-run
        auto_run = self._impostazioni.auto_run
        self._sidebar.imposta_autorun(auto_run)

        # Cartella di lavoro
        cartella = self._impostazioni.cartella_lavoro
        self._sidebar.imposta_cartella(cartella)

        # Aggiorna la status bar
        config = self._provider_manager.ottieni_config_attiva()
        if config:
            self._status_bar.aggiorna_modello(config.nome)

        logger.info("📋 Impostazioni GUI caricate")

    def _inizializza_interprete(self) -> None:
        """Inizializza l'interprete con il provider attualmente selezionato."""
        config = self._provider_manager.ottieni_config_interpreter()
        if config:
            # Verifica che la configurazione sia valida
            valido, messaggio = self._provider_manager.verifica_config_valida()
            if not valido:
                logger.warning(f"⚠️ Config non valida: {messaggio}")
                self._terminal_view.scrivi_log(f"⚠️ {messaggio}")
                return

            successo = self._interpreter.inizializza_interpreter(config)
            if successo:
                self._terminal_view.scrivi_stato(
                    f"Interprete inizializzato con: {self._provider_manager.provider_attivo_nome}"
                )
                # Imposta auto-run
                self._interpreter.imposta_auto_run(self._impostazioni.auto_run)
                # Imposta cartella di lavoro
                cartella = self._impostazioni.cartella_lavoro
                if cartella:
                    self._interpreter.imposta_cartella_lavoro(cartella)
            else:
                self._terminal_view.scrivi_errore(
                    "Impossibile inizializzare l'interprete. Controlla la configurazione."
                )

    # ==========================================
    # Polling della coda messaggi
    # ==========================================

    def _avvia_polling(self) -> None:
        """
        Avvia il polling periodico della coda messaggi.
        
        Ogni INTERVALLO_POLLING_MS millisecondi, controlla se ci sono
        nuovi messaggi dall'interprete e li visualizza nella GUI.
        """
        self._processa_messaggi()
        self.after(INTERVALLO_POLLING_MS, self._avvia_polling)

    def _processa_messaggi(self) -> None:
        """
        Legge e processa tutti i messaggi disponibili nella coda.
        
        Questo è il "ponte" tra il thread dell'interprete e la GUI.
        """
        messaggi = self._interpreter.leggi_messaggi()

        for msg in messaggi:
            try:
                if msg.tipo == TipoMessaggio.TESTO:
                    # Testo dall'IA - aggiungi come streaming
                    self._chat_view.aggiungi_testo_streaming(msg.contenuto)
                    self._chat_view.aggiorna_stato("🤖 Sta scrivendo...")

                elif msg.tipo == TipoMessaggio.CODICE:
                    # Codice - mostra nel terminale
                    self._terminal_view.scrivi_codice(msg.contenuto, msg.linguaggio)
                    self._chat_view.aggiungi_messaggio(
                        "assistant",
                        f"💻 Codice ({msg.linguaggio}):\n{msg.contenuto}",
                        tipo="code"
                    )

                elif msg.tipo == TipoMessaggio.OUTPUT_CONSOLE:
                    # Output console - mostra nel terminale
                    self._terminal_view.scrivi_output(msg.contenuto)

                elif msg.tipo == TipoMessaggio.ERRORE:
                    # Errore - mostra sia nel terminale che nella chat
                    self._terminal_view.scrivi_errore(msg.contenuto)
                    self._chat_view.aggiungi_messaggio("error", msg.contenuto)
                    self._chat_view.aggiorna_stato("")

                elif msg.tipo == TipoMessaggio.STATO:
                    # Cambio stato
                    if msg.completo:
                        # Elaborazione terminata
                        self._chat_view.finalizza_streaming()
                        self._chat_view.aggiorna_stato("✅ Pronto")
                        self._chat_view.abilita_input(True)
                    else:
                        self._chat_view.aggiorna_stato(f"⏳ {msg.contenuto}")

                elif msg.tipo == TipoMessaggio.APPROVAZIONE:
                    # Richiesta approvazione - mostra il dialogo
                    self._mostra_approvazione_codice(msg.contenuto, msg.linguaggio)

                # Aggiorna token counter se presente
                if msg.token_input > 0 or msg.token_output > 0:
                    self._token_counter.aggiungi(msg.token_input, msg.token_output)
                    self._status_bar.aggiorna_token(self._token_counter.formatta_breve())

            except Exception as e:
                logger.error(f"❌ Errore processamento messaggio: {e}")

    # ==========================================
    # Callback dalla GUI
    # ==========================================

    def _on_invia_messaggio(self, messaggio: str) -> None:
        """
        Callback: l'utente ha inviato un messaggio.
        
        Args:
            messaggio: Il testo del messaggio
        """
        logger.info(f"📤 Messaggio utente: {messaggio[:50]}...")

        # Disabilita l'input durante l'elaborazione
        self._chat_view.abilita_input(False)
        self._chat_view.aggiorna_stato("⏳ Invio in corso...")

        # Log nel terminale
        self._terminal_view.scrivi_log(f"Messaggio utente: {messaggio[:80]}...")

        # Invia all'interprete
        successo = self._interpreter.invia_messaggio(messaggio)
        if not successo:
            self._chat_view.abilita_input(True)
            self._chat_view.aggiorna_stato("❌ Errore invio")

    def _on_emergency_stop(self) -> None:
        """Callback: l'utente ha premuto il pulsante STOP."""
        logger.warning("🚨 EMERGENCY STOP dall'utente!")
        self._interpreter.emergency_stop()
        self._chat_view.abilita_input(True)
        self._chat_view.aggiorna_stato("🛑 Fermato")
        self._chat_view.finalizza_streaming()
        self._terminal_view.scrivi_errore("🚨 STOP DI EMERGENZA - Operazione interrotta")

    def _on_cambio_provider(self, provider: str) -> None:
        """
        Callback: l'utente ha cambiato provider.
        
        Args:
            provider: "locale" o "cloud"
        """
        logger.info(f"🔄 Cambio provider a: {provider}")

        # Aggiorna le impostazioni
        self._impostazioni.provider_attivo = provider
        self._provider_manager.seleziona_provider(provider)

        # Aggiorna la status bar
        config = self._provider_manager.ottieni_config_attiva()
        if config:
            self._status_bar.aggiorna_modello(config.nome)

        # Reinizializza l'interprete con il nuovo provider
        self._inizializza_interprete()

        # Log
        self._terminal_view.scrivi_stato(
            f"Provider cambiato a: {self._provider_manager.provider_attivo_nome}"
        )

    def _on_toggle_autorun(self, attivo: bool) -> None:
        """
        Callback: l'utente ha attivato/disattivato auto-run.
        
        Args:
            attivo: True se auto-run è attivo
        """
        self._impostazioni.auto_run = attivo
        self._interpreter.imposta_auto_run(attivo)

        stato = "ATTIVATO ⚠️" if attivo else "DISATTIVATO ✅"
        self._terminal_view.scrivi_log(f"Auto-run {stato}")

    def _on_cambio_cartella(self, cartella: str) -> None:
        """
        Callback: l'utente ha selezionato una nuova cartella di lavoro.
        
        Args:
            cartella: Percorso della cartella
        """
        self._impostazioni.cartella_lavoro = cartella
        self._interpreter.imposta_cartella_lavoro(cartella)
        self._terminal_view.scrivi_stato(f"Cartella di lavoro: {cartella}")

    def _on_nuova_chat(self) -> None:
        """Callback: l'utente vuole una nuova conversazione."""
        DialogoConferma(
            self,
            titolo="Nuova Conversazione",
            messaggio="Vuoi iniziare una nuova conversazione?\nLa cronologia attuale verrà cancellata.",
            callback_conferma=self._esegui_nuova_chat
        )

    def _esegui_nuova_chat(self) -> None:
        """Esegue effettivamente il reset della chat."""
        self._interpreter.nuova_conversazione()
        self._chat_view.pulisci_chat()
        self._terminal_view.pulisci()
        self._token_counter.reset()
        self._status_bar.aggiorna_token(self._token_counter.formatta_breve())
        logger.info("🆕 Nuova conversazione avviata")

    def _on_export_cronologia(self) -> None:
        """Callback: l'utente vuole esportare la cronologia."""
        # Chiedi dove salvare
        percorso = filedialog.asksaveasfilename(
            title="Esporta Cronologia Chat",
            defaultextension=".md",
            filetypes=[
                ("Markdown", "*.md"),
                ("Testo", "*.txt"),
            ],
            initialfile=EsportaCronologia.genera_nome_file("md")
        )

        if not percorso:
            return

        cronologia = self._interpreter.cronologia

        if percorso.endswith(".md"):
            successo = EsportaCronologia.esporta_md(cronologia, percorso)
        else:
            successo = EsportaCronologia.esporta_txt(cronologia, percorso)

        if successo:
            self._terminal_view.scrivi_stato(f"Cronologia esportata: {percorso}")
        else:
            DialogoErrore(
                self,
                titolo="Errore Esportazione",
                messaggio=f"Impossibile esportare la cronologia in:\n{percorso}"
            )

    def _on_salva_apikey(self, api_key: str) -> None:
        """
        Callback: l'utente ha salvato una nuova API key.
        
        Args:
            api_key: La nuova API key
        """
        self._impostazioni.api_key_openrouter = api_key
        self._provider_manager.aggiorna_api_key(api_key)
        self._terminal_view.scrivi_stato("🔑 API key OpenRouter aggiornata e salvata")

        # Se il provider attivo è cloud, reinizializza
        if self._provider_manager.provider_attivo_tipo == "cloud":
            self._inizializza_interprete()

    def _on_approva_codice(self) -> None:
        """Callback: l'utente ha approvato l'esecuzione del codice."""
        self._interpreter.approva_esecuzione(True)
        self._terminal_view.scrivi_log("✅ Esecuzione codice approvata")

    def _on_rifiuta_codice(self) -> None:
        """Callback: l'utente ha rifiutato l'esecuzione del codice."""
        self._interpreter.approva_esecuzione(False)
        self._terminal_view.scrivi_log("❌ Esecuzione codice rifiutata")

    def _mostra_approvazione_codice(self, codice: str, linguaggio: str) -> None:
        """
        Mostra il dialogo di approvazione del codice.
        
        Args:
            codice: Il codice da approvare
            linguaggio: Il linguaggio del codice
        """
        DialogoApprovazioneCodice(
            self,
            codice=codice,
            linguaggio=linguaggio,
            callback_approva=self._on_approva_codice,
            callback_rifiuta=self._on_rifiuta_codice
        )

    # ==========================================
    # Health Check callback
    # ==========================================

    def _on_cambio_stato_server(self, online: bool) -> None:
        """
        Callback: lo stato del server locale è cambiato.
        Viene chiamato dal thread di health check, quindi usiamo after()
        per aggiornare la GUI in modo thread-safe.
        
        Args:
            online: True se il server è raggiungibile
        """
        # after() esegue la funzione nel thread principale della GUI
        self.after(0, self._aggiorna_stato_server_gui, online)

    def _aggiorna_stato_server_gui(self, online: bool) -> None:
        """Aggiorna la GUI con lo stato del server (thread-safe)."""
        self._sidebar.aggiorna_stato_server(online)
        self._status_bar.aggiorna_stato_server(online)

        if online:
            self._terminal_view.scrivi_log("Server locale: ONLINE ✅")
        else:
            self._terminal_view.scrivi_log("Server locale: OFFLINE ❌")

    # ==========================================
    # Chiusura applicazione
    # ==========================================

    def _on_chiusura(self) -> None:
        """
        Gestisce la chiusura dell'applicazione.
        Ferma tutti i processi in background prima di chiudere.
        """
        logger.info("🛑 Chiusura AutoBot Ox...")

        # Ferma l'interprete se sta elaborando
        if self._interpreter.is_in_esecuzione:
            self._interpreter.emergency_stop()

        # Ferma il health check
        self._health_check.ferma()

        # Salva le impostazioni
        self._impostazioni.salva()

        logger.info("👋 AutoBot Ox chiuso. Arrivederci!")

        # Chiudi la finestra
        self.destroy()

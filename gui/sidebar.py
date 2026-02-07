# ============================================
# Sidebar (Pannello Laterale) - AutoBot Ox
# Contiene tutte le impostazioni:
# - Selezione provider (locale/cloud)
# - API Key input
# - Toggle auto-run
# - Cartella di lavoro
# - Pulsanti azioni (nuova chat, export, ecc.)
# ============================================

import logging
import customtkinter as ctk
from tkinter import filedialog
from typing import Callable, Optional, Dict

# Logger per questo modulo
logger = logging.getLogger("AutoBotOx.GUI.Sidebar")


class Sidebar(ctk.CTkFrame):
    """
    Pannello laterale sinistro dell'applicazione.
    
    Contiene tutti i controlli e le impostazioni che l'utente
    può modificare durante l'uso dell'app.
    
    Per chi è nuovo al codice:
    - CTkFrame è un "contenitore" rettangolare dove mettiamo altri elementi
    - Ogni elemento (pulsante, campo testo, ecc.) viene posizionato dentro
    - Usiamo pack() per mettere gli elementi uno sotto l'altro
    """

    def __init__(
        self,
        master,
        callback_cambio_provider: Optional[Callable] = None,
        callback_toggle_autorun: Optional[Callable] = None,
        callback_toggle_computer_use: Optional[Callable] = None,
        callback_toggle_vision: Optional[Callable] = None,
        callback_cambio_cartella: Optional[Callable] = None,
        callback_nuova_chat: Optional[Callable] = None,
        callback_export: Optional[Callable] = None,
        callback_salva_apikey: Optional[Callable] = None,
        **kwargs
    ):
        """
        Crea la sidebar con tutti i controlli.
        
        Args:
            master: Il widget genitore (la finestra principale)
            callback_*: Funzioni da chiamare quando l'utente interagisce
        """
        super().__init__(master, **kwargs)

        # Salva i callback
        self._callback_cambio_provider = callback_cambio_provider
        self._callback_toggle_autorun = callback_toggle_autorun
        self._callback_toggle_computer_use = callback_toggle_computer_use
        self._callback_toggle_vision = callback_toggle_vision
        self._callback_cambio_cartella = callback_cambio_cartella
        self._callback_nuova_chat = callback_nuova_chat
        self._callback_export = callback_export
        self._callback_salva_apikey = callback_salva_apikey

        # Configura lo stile della sidebar
        self.configure(
            width=280,
            corner_radius=0,
            fg_color=("gray90", "gray13")  # (tema chiaro, tema scuro)
        )

        # Costruisci tutti gli elementi dell'interfaccia
        self._costruisci_ui()
        logger.info("📱 Sidebar costruita")

    def _costruisci_ui(self) -> None:
        """Costruisce tutti gli elementi della sidebar."""

        # ========== LOGO / TITOLO ==========
        titolo_frame = ctk.CTkFrame(self, fg_color="transparent")
        titolo_frame.pack(fill="x", padx=15, pady=(15, 5))

        ctk.CTkLabel(
            titolo_frame,
            text="🤖 AutoBot Ox",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=("gray10", "gray90")
        ).pack(anchor="w")

        ctk.CTkLabel(
            titolo_frame,
            text="v1.0.0 - AI Agent Desktop",
            font=ctk.CTkFont(size=11),
            text_color=("gray40", "gray60")
        ).pack(anchor="w")

        # Separatore
        self._crea_separatore()

        # ========== SELEZIONE PROVIDER ==========
        self._crea_sezione_label("🔌 Provider LLM")

        self._var_provider = ctk.StringVar(value="locale")
        
        # Radio button per provider locale
        self._radio_locale = ctk.CTkRadioButton(
            self,
            text="LLM Locale (porta 1234)",
            variable=self._var_provider,
            value="locale",
            command=self._on_cambio_provider,
            font=ctk.CTkFont(size=13),
            radiobutton_width=18,
            radiobutton_height=18
        )
        self._radio_locale.pack(fill="x", padx=20, pady=(2, 2))

        # Radio button per provider cloud
        self._radio_cloud = ctk.CTkRadioButton(
            self,
            text="DeepSeek R1 (OpenRouter)",
            variable=self._var_provider,
            value="cloud",
            command=self._on_cambio_provider,
            font=ctk.CTkFont(size=13),
            radiobutton_width=18,
            radiobutton_height=18
        )
        self._radio_cloud.pack(fill="x", padx=20, pady=(2, 8))

        # Indicatore stato server locale
        self._frame_stato_locale = ctk.CTkFrame(self, fg_color="transparent")
        self._frame_stato_locale.pack(fill="x", padx=20, pady=(0, 5))

        self._label_stato_locale = ctk.CTkLabel(
            self._frame_stato_locale,
            text="● Offline",
            font=ctk.CTkFont(size=11),
            text_color="red"
        )
        self._label_stato_locale.pack(anchor="w")

        # Separatore
        self._crea_separatore()

        # ========== API KEY ==========
        self._crea_sezione_label("🔑 API Key OpenRouter")

        self._entry_apikey = ctk.CTkEntry(
            self,
            placeholder_text="Inserisci la tua API key...",
            show="*",  # Nasconde i caratteri come una password
            font=ctk.CTkFont(size=12),
            height=32
        )
        self._entry_apikey.pack(fill="x", padx=15, pady=(2, 5))

        # Frame per pulsanti API key
        frame_apikey_btn = ctk.CTkFrame(self, fg_color="transparent")
        frame_apikey_btn.pack(fill="x", padx=15, pady=(0, 5))

        self._btn_mostra_key = ctk.CTkButton(
            frame_apikey_btn,
            text="👁",
            width=35,
            height=28,
            command=self._toggle_mostra_apikey,
            font=ctk.CTkFont(size=14)
        )
        self._btn_mostra_key.pack(side="left", padx=(0, 5))

        self._btn_salva_key = ctk.CTkButton(
            frame_apikey_btn,
            text="💾 Salva",
            width=80,
            height=28,
            command=self._on_salva_apikey,
            font=ctk.CTkFont(size=12)
        )
        self._btn_salva_key.pack(side="left")

        self._apikey_visibile = False

        # Separatore
        self._crea_separatore()

        # ========== SICUREZZA ==========
        self._crea_sezione_label("🛡️ Sicurezza")

        # Toggle Auto-Run
        self._frame_autorun = ctk.CTkFrame(self, fg_color="transparent")
        self._frame_autorun.pack(fill="x", padx=15, pady=(2, 5))

        ctk.CTkLabel(
            self._frame_autorun,
            text="Auto-Run Codice:",
            font=ctk.CTkFont(size=13)
        ).pack(side="left")

        self._switch_autorun = ctk.CTkSwitch(
            self._frame_autorun,
            text="",
            command=self._on_toggle_autorun,
            width=40,
            onvalue=True,
            offvalue=False
        )
        self._switch_autorun.pack(side="right")

        # Avviso auto-run
        self._label_avviso_autorun = ctk.CTkLabel(
            self,
            text="⚠️ Con Auto-Run attivo, il codice\nviene eseguito senza conferma!",
            font=ctk.CTkFont(size=10),
            text_color="orange",
            justify="left"
        )
        # Inizialmente nascosto, mostrato solo quando auto-run è attivo

        # Toggle Computer Use (controllo mouse/tastiera)
        self._frame_computer_use = ctk.CTkFrame(self, fg_color="transparent")
        self._frame_computer_use.pack(fill="x", padx=15, pady=(5, 2))

        ctk.CTkLabel(
            self._frame_computer_use,
            text="🖱️ Computer Use:",
            font=ctk.CTkFont(size=13)
        ).pack(side="left")

        self._switch_computer_use = ctk.CTkSwitch(
            self._frame_computer_use,
            text="",
            command=self._on_toggle_computer_use,
            width=40,
            onvalue=True,
            offvalue=False
        )
        self._switch_computer_use.pack(side="right")

        # Avviso computer use
        self._label_avviso_computer_use = ctk.CTkLabel(
            self,
            text="🖱️ L'IA può controllare mouse e\ntastiera! FAILSAFE: muovi il mouse\nnell'angolo in alto a sinistra.",
            font=ctk.CTkFont(size=10),
            text_color="#00bcd4",
            justify="left"
        )
        # Inizialmente nascosto

        # Toggle Vision (invio screenshot al modello)
        self._frame_vision = ctk.CTkFrame(self, fg_color="transparent")
        self._frame_vision.pack(fill="x", padx=15, pady=(5, 2))

        ctk.CTkLabel(
            self._frame_vision,
            text="👁️ Vision:",
            font=ctk.CTkFont(size=13)
        ).pack(side="left")

        self._switch_vision = ctk.CTkSwitch(
            self._frame_vision,
            text="",
            command=self._on_toggle_vision,
            width=40,
            onvalue=True,
            offvalue=False
        )
        self._switch_vision.pack(side="right")

        # Avviso vision
        self._label_avviso_vision = ctk.CTkLabel(
            self,
            text="👁️ Uno screenshot verrà inviato\nal modello con ogni messaggio.\nServe un modello con vision!",
            font=ctk.CTkFont(size=10),
            text_color="#8e24aa",
            justify="left"
        )
        # Inizialmente nascosto

        # Separatore
        self._crea_separatore()

        # ========== CARTELLA DI LAVORO ==========
        self._crea_sezione_label("📂 Cartella di Lavoro")

        self._label_cartella = ctk.CTkLabel(
            self,
            text="Non selezionata",
            font=ctk.CTkFont(size=11),
            text_color=("gray40", "gray60"),
            wraplength=240,
            justify="left"
        )
        self._label_cartella.pack(fill="x", padx=15, pady=(2, 5))

        self._btn_cartella = ctk.CTkButton(
            self,
            text="📁 Seleziona Cartella",
            command=self._on_cambio_cartella,
            height=30,
            font=ctk.CTkFont(size=12)
        )
        self._btn_cartella.pack(fill="x", padx=15, pady=(0, 8))

        # Separatore
        self._crea_separatore()

        # ========== AZIONI ==========
        self._crea_sezione_label("⚡ Azioni")

        self._btn_nuova_chat = ctk.CTkButton(
            self,
            text="🆕 Nuova Conversazione",
            command=self._on_nuova_chat,
            height=32,
            font=ctk.CTkFont(size=13),
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray40")
        )
        self._btn_nuova_chat.pack(fill="x", padx=15, pady=(2, 5))

        self._btn_export = ctk.CTkButton(
            self,
            text="💾 Esporta Cronologia",
            command=self._on_export,
            height=32,
            font=ctk.CTkFont(size=13),
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray40")
        )
        self._btn_export.pack(fill="x", padx=15, pady=(0, 8))

        # ========== SPAZIO FLESSIBILE ==========
        # Questo frame espandibile spinge il pulsante info in basso
        spacer = ctk.CTkFrame(self, fg_color="transparent")
        spacer.pack(fill="both", expand=True)

        # ========== INFO IN BASSO ==========
        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.pack(fill="x", padx=15, pady=(5, 15))

        ctk.CTkLabel(
            info_frame,
            text="Powered by Open Interpreter",
            font=ctk.CTkFont(size=10),
            text_color=("gray50", "gray50")
        ).pack(anchor="w")

    # ==========================================
    # Metodi helper per costruire la UI
    # ==========================================

    def _crea_separatore(self) -> None:
        """Crea una linea separatrice orizzontale."""
        sep = ctk.CTkFrame(self, height=1, fg_color=("gray75", "gray25"))
        sep.pack(fill="x", padx=15, pady=8)

    def _crea_sezione_label(self, testo: str) -> None:
        """Crea un'etichetta di sezione (titoletto)."""
        ctk.CTkLabel(
            self,
            text=testo,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("gray20", "gray80"),
            anchor="w"
        ).pack(fill="x", padx=15, pady=(5, 2))

    # ==========================================
    # Event Handler (gestori degli eventi)
    # ==========================================

    def _on_cambio_provider(self) -> None:
        """Chiamato quando l'utente cambia il provider LLM."""
        provider = self._var_provider.get()
        logger.info(f"🔄 Provider cambiato a: {provider}")
        if self._callback_cambio_provider:
            self._callback_cambio_provider(provider)

    def _on_toggle_autorun(self) -> None:
        """Chiamato quando l'utente attiva/disattiva auto-run."""
        attivo = self._switch_autorun.get()
        logger.info(f"🔒 Auto-run: {'ATTIVO' if attivo else 'DISATTIVO'}")

        # Mostra/nascondi avviso
        if attivo:
            self._label_avviso_autorun.pack(fill="x", padx=20, pady=(0, 5))
        else:
            self._label_avviso_autorun.pack_forget()

        if self._callback_toggle_autorun:
            self._callback_toggle_autorun(attivo)

    def _on_toggle_computer_use(self) -> None:
        """Chiamato quando l'utente attiva/disattiva il computer use."""
        attivo = self._switch_computer_use.get()
        logger.info(f"🖱️ Computer Use: {'ATTIVO' if attivo else 'DISATTIVO'}")

        # Mostra/nascondi avviso
        if attivo:
            self._label_avviso_computer_use.pack(fill="x", padx=20, pady=(0, 5))
        else:
            self._label_avviso_computer_use.pack_forget()

        if self._callback_toggle_computer_use:
            self._callback_toggle_computer_use(attivo)

    def _on_toggle_vision(self) -> None:
        """Chiamato quando l'utente attiva/disattiva la vision (screenshot al modello)."""
        attivo = self._switch_vision.get()
        logger.info(f"👁️ Vision: {'ATTIVA' if attivo else 'DISATTIVATA'}")

        # Mostra/nascondi avviso
        if attivo:
            self._label_avviso_vision.pack(fill="x", padx=20, pady=(0, 5))
        else:
            self._label_avviso_vision.pack_forget()

        if self._callback_toggle_vision:
            self._callback_toggle_vision(attivo)

    def _on_cambio_cartella(self) -> None:
        """Apre il dialogo per selezionare la cartella di lavoro."""
        cartella = filedialog.askdirectory(
            title="Seleziona la cartella di lavoro"
        )
        if cartella:
            self._label_cartella.configure(text=cartella)
            logger.info(f"📂 Cartella di lavoro selezionata: {cartella}")
            if self._callback_cambio_cartella:
                self._callback_cambio_cartella(cartella)

    def _on_nuova_chat(self) -> None:
        """Chiamato quando l'utente vuole una nuova conversazione."""
        logger.info("🆕 Richiesta nuova conversazione")
        if self._callback_nuova_chat:
            self._callback_nuova_chat()

    def _on_export(self) -> None:
        """Chiamato quando l'utente vuole esportare la cronologia."""
        logger.info("💾 Richiesta export cronologia")
        if self._callback_export:
            self._callback_export()

    def _on_salva_apikey(self) -> None:
        """Salva la API key inserita."""
        api_key = self._entry_apikey.get().strip()
        if api_key:
            logger.info("🔑 API key salvata")
            if self._callback_salva_apikey:
                self._callback_salva_apikey(api_key)
        else:
            logger.warning("⚠️ API key vuota, non salvata")

    def _toggle_mostra_apikey(self) -> None:
        """Mostra/nasconde la API key nel campo di input."""
        self._apikey_visibile = not self._apikey_visibile
        if self._apikey_visibile:
            self._entry_apikey.configure(show="")
            self._btn_mostra_key.configure(text="🔒")
        else:
            self._entry_apikey.configure(show="*")
            self._btn_mostra_key.configure(text="👁")

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
            self._label_stato_locale.configure(
                text="● Online",
                text_color="green"
            )
        else:
            self._label_stato_locale.configure(
                text="● Offline",
                text_color="red"
            )

    def imposta_apikey(self, api_key: str) -> None:
        """
        Pre-compila il campo API key (es. dal file di configurazione).
        
        Args:
            api_key: La API key da mostrare
        """
        self._entry_apikey.delete(0, "end")
        self._entry_apikey.insert(0, api_key)

    def imposta_provider(self, provider: str) -> None:
        """
        Seleziona il provider indicato.
        
        Args:
            provider: "locale" o "cloud"
        """
        self._var_provider.set(provider)

    def imposta_cartella(self, cartella: str) -> None:
        """
        Aggiorna il testo della cartella di lavoro.
        
        Args:
            cartella: Percorso della cartella
        """
        if cartella:
            self._label_cartella.configure(text=cartella)

    def imposta_autorun(self, attivo: bool) -> None:
        """
        Imposta lo stato dell'interruttore auto-run.
        
        Args:
            attivo: True per attivare, False per disattivare
        """
        if attivo:
            self._switch_autorun.select()
            self._label_avviso_autorun.pack(fill="x", padx=20, pady=(0, 5))
        else:
            self._switch_autorun.deselect()
            self._label_avviso_autorun.pack_forget()

    def imposta_computer_use(self, attivo: bool) -> None:
        """
        Imposta lo stato dell'interruttore computer use.
        
        Args:
            attivo: True per attivare, False per disattivare
        """
        if attivo:
            self._switch_computer_use.select()
            self._label_avviso_computer_use.pack(fill="x", padx=20, pady=(0, 5))
        else:
            self._switch_computer_use.deselect()
            self._label_avviso_computer_use.pack_forget()

    def imposta_vision(self, attivo: bool) -> None:
        """
        Imposta lo stato dell'interruttore vision.
        
        Args:
            attivo: True per attivare, False per disattivare
        """
        if attivo:
            self._switch_vision.select()
            self._label_avviso_vision.pack(fill="x", padx=20, pady=(0, 5))
        else:
            self._switch_vision.deselect()
            self._label_avviso_vision.pack_forget()

    def ottieni_apikey(self) -> str:
        """Restituisce la API key attualmente inserita nel campo."""
        return self._entry_apikey.get().strip()

    def ottieni_provider(self) -> str:
        """Restituisce il provider selezionato ('locale' o 'cloud')."""
        return self._var_provider.get()

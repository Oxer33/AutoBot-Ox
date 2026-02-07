# ============================================
# Chat View (Vista Chat) - AutoBot Ox
# L'interfaccia di chat dove l'utente scrive messaggi
# e vede le risposte dell'IA in tempo reale
# ============================================

import logging
import customtkinter as ctk
from typing import Callable, Optional
from datetime import datetime

# Logger per questo modulo
logger = logging.getLogger("AutoBotOx.GUI.ChatView")


class BollaMessaggio(ctk.CTkFrame):
    """
    Una singola "bolla" di messaggio nella chat.
    
    Come funziona (per principianti):
    - Ogni messaggio (utente o IA) viene mostrato in una "bolla" colorata
    - I messaggi dell'utente sono allineati a destra (blu)
    - I messaggi dell'IA sono allineati a sinistra (grigio)
    - I messaggi di errore sono rossi
    """

    def __init__(self, master, ruolo: str, contenuto: str, tipo: str = "message", **kwargs):
        """
        Crea una bolla di messaggio.
        
        Args:
            master: Widget genitore
            ruolo: "user", "assistant" o "error"
            contenuto: Il testo del messaggio
            tipo: "message", "code", "console"
        """
        super().__init__(master, **kwargs)

        # Colori diversi per ogni tipo di messaggio
        colori = {
            "user": {"bg": "#1a73e8", "fg": "white", "icona": "👤"},
            "assistant": {"bg": "#2d2d2d", "fg": "#e0e0e0", "icona": "🤖"},
            "error": {"bg": "#c62828", "fg": "white", "icona": "❌"},
            "system": {"bg": "#1b5e20", "fg": "white", "icona": "ℹ️"},
        }

        stile = colori.get(ruolo, colori["assistant"])

        self.configure(fg_color="transparent")

        # Frame contenitore della bolla
        bolla_frame = ctk.CTkFrame(
            self,
            fg_color=stile["bg"],
            corner_radius=12
        )

        # Allineamento: utente a destra, IA a sinistra
        if ruolo == "user":
            bolla_frame.pack(anchor="e", padx=(60, 10), pady=4, fill="x")
        else:
            bolla_frame.pack(anchor="w", padx=(10, 60), pady=4, fill="x")

        # Header con icona e timestamp
        header = ctk.CTkFrame(bolla_frame, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=(8, 2))

        nome_ruolo = {
            "user": "Tu",
            "assistant": "AutoBot Ox",
            "error": "Errore",
            "system": "Sistema"
        }

        ctk.CTkLabel(
            header,
            text=f"{stile['icona']} {nome_ruolo.get(ruolo, ruolo)}",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=stile["fg"]
        ).pack(side="left")

        ctk.CTkLabel(
            header,
            text=datetime.now().strftime("%H:%M"),
            font=ctk.CTkFont(size=10),
            text_color="gray60"
        ).pack(side="right")

        # Contenuto del messaggio
        # Salviamo il riferimento per poter aggiornare il testo in-place
        # durante lo streaming (evita flickering da destroy/recreate)
        self.label_contenuto = ctk.CTkLabel(
            bolla_frame,
            text=contenuto,
            font=ctk.CTkFont(size=13),
            text_color=stile["fg"],
            wraplength=500,
            justify="left",
            anchor="w"
        )
        self.label_contenuto.pack(fill="x", padx=10, pady=(2, 10))


class ChatView(ctk.CTkFrame):
    """
    Vista principale della chat.
    
    Contiene:
    1. Area scrollabile con i messaggi (bolle)
    2. Campo di input per scrivere messaggi
    3. Pulsante Invia
    4. Pulsante STOP (emergenza)
    5. Pulsanti Approva/Rifiuta (quando auto-run è disattivato)
    """

    def __init__(
        self,
        master,
        callback_invia: Optional[Callable] = None,
        callback_stop: Optional[Callable] = None,
        callback_approva: Optional[Callable] = None,
        callback_rifiuta: Optional[Callable] = None,
        **kwargs
    ):
        """
        Crea la vista chat.
        
        Args:
            master: Widget genitore
            callback_invia: Funzione chiamata quando si invia un messaggio
            callback_stop: Funzione chiamata quando si preme STOP
            callback_approva: Funzione per approvare l'esecuzione del codice
            callback_rifiuta: Funzione per rifiutare l'esecuzione del codice
        """
        super().__init__(master, **kwargs)

        self._callback_invia = callback_invia
        self._callback_stop = callback_stop
        self._callback_approva = callback_approva
        self._callback_rifiuta = callback_rifiuta

        # Configura il frame principale
        self.configure(fg_color="transparent")

        # Costruisci l'interfaccia
        self._costruisci_ui()

        # Testo corrente dell'assistente (per lo streaming)
        self._testo_streaming = ""
        self._label_streaming = None

        logger.info("💬 ChatView costruita")

    def _costruisci_ui(self) -> None:
        """Costruisce tutti gli elementi della chat view."""

        # ========== HEADER CHAT ==========
        header = ctk.CTkFrame(self, height=40, fg_color=("gray85", "gray17"))
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="💬 Chat",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left", padx=15, pady=5)

        # Indicatore "sta scrivendo..."
        self._label_stato = ctk.CTkLabel(
            header,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="gray50"
        )
        self._label_stato.pack(side="right", padx=15, pady=5)

        # ========== AREA MESSAGGI (SCROLLABILE) ==========
        self._scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=("gray95", "gray10"),
            corner_radius=0
        )
        self._scroll_frame.pack(fill="both", expand=True, padx=0, pady=0)

        # Messaggio di benvenuto
        self._aggiungi_messaggio_benvenuto()

        # ========== FRAME APPROVAZIONE (nascosto di default) ==========
        self._frame_approvazione = ctk.CTkFrame(
            self,
            fg_color=("gray80", "gray20"),
            height=50
        )
        # Non lo packhiamo subito, lo mostriamo solo quando serve

        ctk.CTkLabel(
            self._frame_approvazione,
            text="⚠️ L'IA vuole eseguire del codice. Approvare?",
            font=ctk.CTkFont(size=13)
        ).pack(side="left", padx=15)

        self._btn_approva = ctk.CTkButton(
            self._frame_approvazione,
            text="✅ Approva",
            width=100,
            height=30,
            fg_color="#2e7d32",
            hover_color="#1b5e20",
            command=self._on_approva,
            font=ctk.CTkFont(size=12)
        )
        self._btn_approva.pack(side="right", padx=5, pady=8)

        self._btn_rifiuta = ctk.CTkButton(
            self._frame_approvazione,
            text="❌ Rifiuta",
            width=100,
            height=30,
            fg_color="#c62828",
            hover_color="#b71c1c",
            command=self._on_rifiuta,
            font=ctk.CTkFont(size=12)
        )
        self._btn_rifiuta.pack(side="right", padx=5, pady=8)

        # ========== AREA INPUT ==========
        input_frame = ctk.CTkFrame(self, fg_color=("gray85", "gray17"), height=60)
        input_frame.pack(fill="x", padx=0, pady=0)

        # Campo di input testuale
        self._entry_messaggio = ctk.CTkEntry(
            input_frame,
            placeholder_text="Scrivi un messaggio... (Invio per inviare)",
            font=ctk.CTkFont(size=14),
            height=40
        )
        self._entry_messaggio.pack(side="left", fill="x", expand=True, padx=(10, 5), pady=10)

        # Bind del tasto Invio
        self._entry_messaggio.bind("<Return>", self._on_invio_tastiera)

        # Pulsante STOP (emergenza) - rosso
        self._btn_stop = ctk.CTkButton(
            input_frame,
            text="🛑",
            width=40,
            height=40,
            fg_color="#c62828",
            hover_color="#b71c1c",
            command=self._on_stop,
            font=ctk.CTkFont(size=18)
        )
        self._btn_stop.pack(side="right", padx=(0, 10), pady=10)

        # Pulsante Invia
        self._btn_invia = ctk.CTkButton(
            input_frame,
            text="📤 Invia",
            width=80,
            height=40,
            command=self._on_invia,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self._btn_invia.pack(side="right", padx=5, pady=10)

    def _aggiungi_messaggio_benvenuto(self) -> None:
        """Aggiunge un messaggio di benvenuto alla chat."""
        BollaMessaggio(
            self._scroll_frame,
            ruolo="system",
            contenuto=(
                "Benvenuto in AutoBot Ox! 🤖\n\n"
                "Sono il tuo assistente AI. Posso:\n"
                "• Eseguire comandi sul tuo PC\n"
                "• Scrivere e modificare file\n"
                "• Analizzare dati e creare grafici\n"
                "• E molto altro!\n\n"
                "Seleziona un provider LLM dalla sidebar e inizia a chattare."
            )
        ).pack(fill="x", padx=5, pady=2)

    # ==========================================
    # Event Handler
    # ==========================================

    def _on_invio_tastiera(self, event) -> None:
        """Gestisce la pressione del tasto Invio."""
        self._on_invia()

    def _on_invia(self) -> None:
        """Invia il messaggio scritto dall'utente."""
        messaggio = self._entry_messaggio.get().strip()
        if not messaggio:
            return

        # Pulisci il campo di input
        self._entry_messaggio.delete(0, "end")

        # Aggiungi la bolla del messaggio utente
        self.aggiungi_messaggio("user", messaggio)

        # Chiama il callback per inviare all'interprete
        if self._callback_invia:
            self._callback_invia(messaggio)

        logger.debug(f"📤 Messaggio inviato: {messaggio[:50]}...")

    def _on_stop(self) -> None:
        """Gestisce la pressione del pulsante STOP."""
        logger.warning("🛑 Pulsante STOP premuto!")
        if self._callback_stop:
            self._callback_stop()

    def _on_approva(self) -> None:
        """Gestisce l'approvazione dell'esecuzione del codice."""
        self.nascondi_approvazione()
        if self._callback_approva:
            self._callback_approva()

    def _on_rifiuta(self) -> None:
        """Gestisce il rifiuto dell'esecuzione del codice."""
        self.nascondi_approvazione()
        if self._callback_rifiuta:
            self._callback_rifiuta()

    # ==========================================
    # Metodi pubblici
    # ==========================================

    def aggiungi_messaggio(self, ruolo: str, contenuto: str, tipo: str = "message") -> None:
        """
        Aggiunge un messaggio alla chat.
        
        Args:
            ruolo: "user", "assistant", "error" o "system"
            contenuto: Il testo del messaggio
            tipo: "message", "code" o "console"
        """
        if not contenuto.strip():
            return

        bolla = BollaMessaggio(
            self._scroll_frame,
            ruolo=ruolo,
            contenuto=contenuto,
            tipo=tipo
        )
        bolla.pack(fill="x", padx=5, pady=2)

        # Scrolla in basso automaticamente
        self._scroll_in_basso()

    def aggiungi_testo_streaming(self, testo: str) -> None:
        """
        Aggiunge testo in streaming (pezzo per pezzo) all'ultimo messaggio.
        Usato per mostrare la risposta dell'IA in tempo reale.
        
        Args:
            testo: Il nuovo pezzo di testo da aggiungere
        """
        self._testo_streaming += testo

        # Se non esiste ancora una bolla per lo streaming, creala
        if self._label_streaming is None:
            self._label_streaming = BollaMessaggio(
                self._scroll_frame,
                ruolo="assistant",
                contenuto=self._testo_streaming
            )
            self._label_streaming.pack(fill="x", padx=5, pady=2)
        else:
            # Aggiorna il testo IN-PLACE senza distruggere/ricreare la bolla
            # Questo evita il flickering ad ogni carattere durante lo streaming
            self._label_streaming.label_contenuto.configure(
                text=self._testo_streaming
            )

        # Scrolla solo ogni N caratteri per evitare overhead
        if len(self._testo_streaming) % 20 == 0 or len(testo) > 5:
            self._scroll_in_basso()

    def finalizza_streaming(self) -> None:
        """
        Chiamato quando lo streaming è completato.
        Resetta le variabili di streaming per il prossimo messaggio.
        """
        self._testo_streaming = ""
        self._label_streaming = None

    def mostra_approvazione(self, codice: str = "") -> None:
        """
        Mostra la barra di approvazione per l'esecuzione del codice.
        
        Args:
            codice: Il codice che l'IA vuole eseguire (per mostrarlo all'utente)
        """
        self._frame_approvazione.pack(fill="x", padx=0, pady=0, before=self._entry_messaggio.master)
        logger.info("⚠️ Richiesta approvazione mostrata")

    def nascondi_approvazione(self) -> None:
        """Nasconde la barra di approvazione."""
        self._frame_approvazione.pack_forget()

    def aggiorna_stato(self, testo: str) -> None:
        """
        Aggiorna l'indicatore di stato nel header.
        
        Args:
            testo: Il testo da mostrare (es. "Sta scrivendo...", "Pronto")
        """
        self._label_stato.configure(text=testo)

    def pulisci_chat(self) -> None:
        """Rimuove tutti i messaggi dalla chat."""
        for widget in self._scroll_frame.winfo_children():
            widget.destroy()
        self._testo_streaming = ""
        self._label_streaming = None
        self._aggiungi_messaggio_benvenuto()
        logger.info("🧹 Chat pulita")

    def abilita_input(self, abilitato: bool) -> None:
        """
        Abilita o disabilita il campo di input e il pulsante invia.
        
        Args:
            abilitato: True per abilitare, False per disabilitare
        """
        stato = "normal" if abilitato else "disabled"
        self._entry_messaggio.configure(state=stato)
        self._btn_invia.configure(state=stato)

    def _scroll_in_basso(self) -> None:
        """Scrolla l'area messaggi fino in fondo."""
        self._scroll_frame.update_idletasks()
        self._scroll_frame._parent_canvas.yview_moveto(1.0)

    def focus_input(self) -> None:
        """Mette il focus sul campo di input (per iniziare subito a scrivere)."""
        self._entry_messaggio.focus_set()

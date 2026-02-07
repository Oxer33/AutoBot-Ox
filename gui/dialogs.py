# ============================================
# Dialogs (Finestre di Dialogo) - AutoBot Ox
# Popup per errori, conferme, debug info
# ============================================

import logging
import customtkinter as ctk
from typing import Optional, Callable

# Logger per questo modulo
logger = logging.getLogger("AutoBotOx.GUI.Dialogs")


class DialogoErrore(ctk.CTkToplevel):
    """
    Finestra di dialogo per mostrare errori.
    Appare come un popup sopra la finestra principale.
    """

    def __init__(self, master, titolo: str, messaggio: str, **kwargs):
        """
        Crea e mostra una finestra di errore.
        
        Args:
            master: La finestra genitore
            titolo: Titolo della finestra
            messaggio: Messaggio di errore da mostrare
        """
        super().__init__(master, **kwargs)

        self.title(titolo)
        self.geometry("450x250")
        self.resizable(False, False)

        # Rendi la finestra modale (blocca l'interazione con la finestra principale)
        self.grab_set()
        self.transient(master)

        # Icona errore
        ctk.CTkLabel(
            self,
            text="❌",
            font=ctk.CTkFont(size=40)
        ).pack(pady=(20, 5))

        # Titolo errore
        ctk.CTkLabel(
            self,
            text=titolo,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#f44336"
        ).pack(pady=5)

        # Messaggio errore
        ctk.CTkLabel(
            self,
            text=messaggio,
            font=ctk.CTkFont(size=13),
            wraplength=400,
            justify="center"
        ).pack(pady=10, padx=20)

        # Pulsante OK
        ctk.CTkButton(
            self,
            text="OK",
            width=100,
            command=self.destroy
        ).pack(pady=15)

        # Centra la finestra
        self._centra_finestra()
        logger.info(f"❌ Dialogo errore mostrato: {titolo}")

    def _centra_finestra(self) -> None:
        """Centra la finestra sullo schermo."""
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 450) // 2
        y = (self.winfo_screenheight() - 250) // 2
        self.geometry(f"450x250+{x}+{y}")


class DialogoConferma(ctk.CTkToplevel):
    """
    Finestra di dialogo per conferme (Sì/No).
    Usata per chiedere conferma prima di azioni importanti.
    """

    def __init__(
        self,
        master,
        titolo: str,
        messaggio: str,
        callback_conferma: Optional[Callable] = None,
        callback_annulla: Optional[Callable] = None,
        **kwargs
    ):
        """
        Crea e mostra una finestra di conferma.
        
        Args:
            master: La finestra genitore
            titolo: Titolo della finestra
            messaggio: Messaggio da mostrare
            callback_conferma: Funzione chiamata se l'utente conferma
            callback_annulla: Funzione chiamata se l'utente annulla
        """
        super().__init__(master, **kwargs)

        self._callback_conferma = callback_conferma
        self._callback_annulla = callback_annulla

        self.title(titolo)
        self.geometry("450x220")
        self.resizable(False, False)
        self.grab_set()
        self.transient(master)

        # Icona domanda
        ctk.CTkLabel(
            self,
            text="❓",
            font=ctk.CTkFont(size=40)
        ).pack(pady=(20, 5))

        # Messaggio
        ctk.CTkLabel(
            self,
            text=messaggio,
            font=ctk.CTkFont(size=13),
            wraplength=400,
            justify="center"
        ).pack(pady=10, padx=20)

        # Frame pulsanti
        frame_btn = ctk.CTkFrame(self, fg_color="transparent")
        frame_btn.pack(pady=15)

        ctk.CTkButton(
            frame_btn,
            text="✅ Conferma",
            width=120,
            fg_color="#2e7d32",
            hover_color="#1b5e20",
            command=self._on_conferma
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            frame_btn,
            text="❌ Annulla",
            width=120,
            fg_color="#c62828",
            hover_color="#b71c1c",
            command=self._on_annulla
        ).pack(side="left", padx=10)

        self._centra_finestra()
        logger.info(f"❓ Dialogo conferma mostrato: {titolo}")

    def _on_conferma(self) -> None:
        """Gestisce la conferma."""
        if self._callback_conferma:
            self._callback_conferma()
        self.destroy()

    def _on_annulla(self) -> None:
        """Gestisce l'annullamento."""
        if self._callback_annulla:
            self._callback_annulla()
        self.destroy()

    def _centra_finestra(self) -> None:
        """Centra la finestra sullo schermo."""
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 450) // 2
        y = (self.winfo_screenheight() - 220) // 2
        self.geometry(f"450x220+{x}+{y}")


class DialogoDebug(ctk.CTkToplevel):
    """
    Finestra di debug per mostrare informazioni tecniche dettagliate.
    Utile per il troubleshooting quando qualcosa non funziona.
    """

    def __init__(self, master, titolo: str, dettagli: str, **kwargs):
        """
        Crea e mostra una finestra di debug.
        
        Args:
            master: La finestra genitore
            titolo: Titolo della finestra
            dettagli: Testo dettagliato (errori, stack trace, ecc.)
        """
        super().__init__(master, **kwargs)

        self.title(f"🔍 Debug - {titolo}")
        self.geometry("600x400")
        self.transient(master)

        # Titolo
        ctk.CTkLabel(
            self,
            text=f"🔍 {titolo}",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(15, 5), padx=15, anchor="w")

        # Area testo con i dettagli
        self._textbox = ctk.CTkTextbox(
            self,
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color=("gray95", "gray10"),
            wrap="word"
        )
        self._textbox.pack(fill="both", expand=True, padx=15, pady=10)
        self._textbox.insert("end", dettagli)
        self._textbox.configure(state="disabled")

        # Frame pulsanti
        frame_btn = ctk.CTkFrame(self, fg_color="transparent")
        frame_btn.pack(fill="x", padx=15, pady=(0, 15))

        ctk.CTkButton(
            frame_btn,
            text="📋 Copia",
            width=100,
            command=lambda: self._copia_negli_appunti(dettagli)
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            frame_btn,
            text="Chiudi",
            width=100,
            command=self.destroy
        ).pack(side="right", padx=5)

        self._centra_finestra()
        logger.info(f"🔍 Dialogo debug mostrato: {titolo}")

    def _copia_negli_appunti(self, testo: str) -> None:
        """Copia il testo negli appunti del sistema."""
        self.clipboard_clear()
        self.clipboard_append(testo)
        logger.info("📋 Dettagli debug copiati negli appunti")

    def _centra_finestra(self) -> None:
        """Centra la finestra sullo schermo."""
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 600) // 2
        y = (self.winfo_screenheight() - 400) // 2
        self.geometry(f"600x400+{x}+{y}")


class DialogoApprovazioneCodice(ctk.CTkToplevel):
    """
    Finestra speciale per approvare/rifiutare l'esecuzione del codice.
    Mostra il codice che l'IA vuole eseguire con evidenziazione.
    """

    def __init__(
        self,
        master,
        codice: str,
        linguaggio: str = "python",
        callback_approva: Optional[Callable] = None,
        callback_rifiuta: Optional[Callable] = None,
        **kwargs
    ):
        """
        Crea e mostra la finestra di approvazione codice.
        
        Args:
            master: La finestra genitore
            codice: Il codice che l'IA vuole eseguire
            linguaggio: Il linguaggio del codice
            callback_approva: Funzione da chiamare se approvato
            callback_rifiuta: Funzione da chiamare se rifiutato
        """
        super().__init__(master, **kwargs)

        self._callback_approva = callback_approva
        self._callback_rifiuta = callback_rifiuta

        self.title("⚠️ Approvazione Esecuzione Codice")
        self.geometry("650x450")
        self.grab_set()
        self.transient(master)

        # Avviso
        ctk.CTkLabel(
            self,
            text="⚠️ L'IA vuole eseguire il seguente codice:",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="orange"
        ).pack(pady=(15, 5), padx=15, anchor="w")

        ctk.CTkLabel(
            self,
            text=f"Linguaggio: {linguaggio.upper()}",
            font=ctk.CTkFont(size=12),
            text_color="gray60"
        ).pack(padx=15, anchor="w")

        # Area codice
        self._textbox = ctk.CTkTextbox(
            self,
            font=ctk.CTkFont(family="Consolas", size=12),
            fg_color="#0d0d0d",
            text_color="#00ff00",
            wrap="word"
        )
        self._textbox.pack(fill="both", expand=True, padx=15, pady=10)
        self._textbox.insert("end", codice)
        self._textbox.configure(state="disabled")

        # Avviso sicurezza
        ctk.CTkLabel(
            self,
            text="🛡️ Controlla attentamente il codice prima di approvare!",
            font=ctk.CTkFont(size=11),
            text_color="orange"
        ).pack(padx=15, pady=(0, 5))

        # Frame pulsanti
        frame_btn = ctk.CTkFrame(self, fg_color="transparent")
        frame_btn.pack(fill="x", padx=15, pady=(0, 15))

        ctk.CTkButton(
            frame_btn,
            text="✅ Approva Esecuzione",
            width=180,
            height=35,
            fg_color="#2e7d32",
            hover_color="#1b5e20",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._on_approva
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            frame_btn,
            text="❌ Rifiuta",
            width=180,
            height=35,
            fg_color="#c62828",
            hover_color="#b71c1c",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._on_rifiuta
        ).pack(side="right", padx=10)

        self._centra_finestra()
        logger.info("⚠️ Dialogo approvazione codice mostrato")

    def _on_approva(self) -> None:
        """Gestisce l'approvazione."""
        if self._callback_approva:
            self._callback_approva()
        self.destroy()

    def _on_rifiuta(self) -> None:
        """Gestisce il rifiuto."""
        if self._callback_rifiuta:
            self._callback_rifiuta()
        self.destroy()

    def _centra_finestra(self) -> None:
        """Centra la finestra sullo schermo."""
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 650) // 2
        y = (self.winfo_screenheight() - 450) // 2
        self.geometry(f"650x450+{x}+{y}")

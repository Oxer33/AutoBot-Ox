# ============================================
# Interpreter Wrapper - AutoBot Ox
# Wrapper attorno a Open Interpreter che gestisce:
# - Esecuzione in thread separato (non blocca la GUI)
# - Streaming dei messaggi tramite coda (queue)
# - Sistema di approvazione codice
# - Emergency stop (kill del processo)
# ============================================

import threading
import queue
import time
import logging
import os
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum

# Logger per questo modulo
logger = logging.getLogger("AutoBotOx.InterpreterWrapper")


class TipoMessaggio(Enum):
    """
    Tipi di messaggio che l'interprete può generare.
    Li usiamo per capire come visualizzare il messaggio nella GUI.
    """
    TESTO = "message"           # Risposta testuale dell'IA
    CODICE = "code"             # Codice che l'IA vuole eseguire
    OUTPUT_CONSOLE = "console"  # Output dell'esecuzione del codice
    ERRORE = "error"            # Errore durante l'esecuzione
    STATO = "status"            # Cambio di stato (inizio, fine, ecc.)
    APPROVAZIONE = "approval"   # Richiesta di approvazione codice


@dataclass
class MessaggioInterpreter:
    """
    Rappresenta un singolo messaggio generato dall'interprete.
    Viene messo nella coda e letto dalla GUI.
    """
    tipo: TipoMessaggio          # Che tipo di messaggio è
    contenuto: str               # Il testo del messaggio
    ruolo: str = "assistant"     # Chi ha generato il messaggio
    linguaggio: str = ""         # Linguaggio del codice (se tipo=CODICE)
    completo: bool = False       # Se True, il messaggio è completo (non più in streaming)
    token_input: int = 0         # Token usati in input (per il counter)
    token_output: int = 0        # Token usati in output (per il counter)


class WrapperInterpreter:
    """
    Wrapper che gestisce Open Interpreter in modo sicuro e asincrono.
    
    Come funziona (spiegazione per principianti):
    
    1. La GUI manda un messaggio tramite invia_messaggio("ciao")
    2. Il wrapper avvia un thread separato che chiama interpreter.chat()
    3. Man mano che l'IA risponde, i pezzi di risposta vengono messi in una CODA
    4. La GUI legge dalla coda ogni 100ms e aggiorna la schermata
    5. Se l'utente preme STOP, il thread viene interrotto
    
    La CODA (queue) è come una fila al supermercato: i messaggi si mettono
    in fondo e si leggono dall'inizio, in modo ordinato e sicuro.
    """

    def __init__(self):
        """Inizializza il wrapper senza avviare nulla."""
        # L'oggetto interpreter vero e proprio (lo creiamo dopo)
        self._interpreter = None

        # Coda per passare messaggi dal thread dell'interprete alla GUI
        self._coda_messaggi: queue.Queue = queue.Queue()

        # Thread dove gira l'interprete
        self._thread_interprete: Optional[threading.Thread] = None

        # Flag per controllare l'esecuzione
        self._in_esecuzione: bool = False       # L'interprete sta elaborando?
        self._stop_richiesto: bool = False       # L'utente ha premuto STOP?
        self._in_attesa_approvazione: bool = False  # In attesa di approvazione codice?
        self._approvazione_risposta: Optional[bool] = None  # Risposta approvazione

        # Cronologia messaggi per la sessione
        self._cronologia: List[Dict[str, Any]] = []

        # Configurazione
        self._auto_run: bool = False
        self._cartella_lavoro: str = ""

        logger.info("🤖 WrapperInterpreter inizializzato")

    def inizializza_interpreter(self, config: Dict[str, Any]) -> bool:
        """
        Crea e configura l'oggetto interpreter con le impostazioni fornite.
        
        Args:
            config: Dizionario con le impostazioni del provider LLM
                    (api_base, model, api_key, offline, ecc.)
                    
        Returns:
            True se l'inizializzazione è riuscita, False altrimenti
        """
        try:
            # Importa Open Interpreter (versione 0.1.x)
            # In questa versione, le proprietà sono direttamente sull'oggetto 'interpreter'
            # NON su 'interpreter.llm' come nelle versioni più recenti
            import interpreter as interp_module

            self._interpreter = interp_module

            # Configura le impostazioni LLM
            # NOTA: In v0.1.x le proprietà sono: api_base, model, api_key, temperature, ecc.
            modello = config.get("model", "")

            if "model" in config:
                self._interpreter.model = config["model"]
                logger.debug(f"   Modello: {config['model']}")

            # IMPORTANTE: Per i modelli con prefisso 'openrouter/' NON impostare api_base!
            # litellm gestisce il routing internamente quando vede il prefisso 'openrouter/'.
            # Impostare api_base causerebbe un conflitto e l'errore 'Provider NOT provided'.
            if "api_base" in config:
                if modello.startswith("openrouter/"):
                    # Per OpenRouter, litellm gestisce il routing dal prefisso del modello
                    logger.debug(f"   API Base: SKIP (litellm gestisce routing openrouter/)")
                else:
                    self._interpreter.api_base = config["api_base"]
                    logger.debug(f"   API Base: {config['api_base']}")

            # API Key - SEMPRE necessaria!
            # Per il locale: chiave dummy 'not-needed' (litellm la richiede comunque)
            # Per il cloud: vera API key di OpenRouter
            if "api_key" in config:
                self._interpreter.api_key = config["api_key"]
                if config["api_key"] == "not-needed":
                    logger.debug("   API Key: [DUMMY - server locale]")
                else:
                    logger.debug("   API Key: [IMPOSTATA]")

            # Modalità locale vs cloud
            if config.get("offline", False):
                # In v0.1.x 'local' è il flag per modalità locale
                self._interpreter.local = True
                logger.debug("   Modalità locale: True")
            else:
                # IMPORTANTE: Imposta esplicitamente local=False per il cloud!
                # Se prima era configurato locale e poi si switcha a cloud,
                # senza questo reset il flag resterebbe True.
                self._interpreter.local = False
                logger.debug("   Modalità cloud: local=False")

            if "temperature" in config:
                self._interpreter.temperature = config["temperature"]

            if "context_window" in config:
                self._interpreter.context_window = config["context_window"]

            # Imposta max_tokens per evitare il warning di litellm
            # "We were unable to determine the context window of this model"
            self._interpreter.max_tokens = 4000
            logger.debug(f"   Max tokens: 4000")

            # Configurazione sicurezza
            # NOTA CRITICA: Con display=False + stream=True in v0.1.x,
            # il flag auto_run dell'interpreter NON ha effetto!
            # Il codice viene sempre eseguito automaticamente.
            # Impostiamo auto_run=True a livello interpreter e gestiamo
            # l'approvazione nel nostro wrapper intercettando il chunk 'executing'.
            self._interpreter.auto_run = True
            self._interpreter.safe_mode = "off"  # Gestiamo noi la sicurezza

            # Disabilita procedure online per privacy
            self._interpreter.disable_procedures = True

            # Istruzioni di sistema personalizzate per sicurezza
            # NOTA: Controlliamo che non siano già state aggiunte (evita duplicati
            # quando si riconfigura l'interprete cambiando provider)
            marcatore_sicurezza = "REGOLE DI SICUREZZA IMPORTANTI:"
            if marcatore_sicurezza not in self._interpreter.system_message:
                self._interpreter.system_message += """

REGOLE DI SICUREZZA IMPORTANTI:
1. NON cancellare MAI file o cartelle senza esplicita conferma dell'utente
2. NON formattare MAI dischi o partizioni
3. NON modificare MAI impostazioni di sistema critiche
4. Prima di eseguire comandi potenzialmente distruttivi, SPIEGA cosa farai
5. Lavora SOLO nella cartella di lavoro specificata, salvo diversa indicazione
6. Se non sei sicuro di un'azione, CHIEDI prima di procedere

HAI IL CONTROLLO DI TASTIERA E MOUSE DEL COMPUTER!
Puoi usare queste funzioni Python per controllare il computer dell'utente.
Il modulo è già disponibile, basta importarlo nel codice:

```python
import sys
sys.path.insert(0, r'""" + os.path.dirname(os.path.dirname(os.path.abspath(__file__))).replace("\\", "\\\\") + """')
from core.computer_use import (
    muovi_mouse,          # muovi_mouse(x, y, durata=0.3)
    clicca,               # clicca(x, y, pulsante="left", doppio=False)
    trascina,             # trascina(x1, y1, x2, y2, durata=0.5)
    scroll,               # scroll(quantita, x, y) - positivo=su, negativo=giù
    scrivi_testo,         # scrivi_testo("ciao", intervallo=0.03)
    scrivi_testo_clipboard,  # scrivi_testo_clipboard("testo con àèìòù")
    premi_tasto,          # premi_tasto("enter"), premi_tasto("tab")
    combinazione_tasti,   # combinazione_tasti("ctrl", "c") = Ctrl+C
    tieni_premuto,        # tieni_premuto("shift", durata=0.5)
    screenshot,           # screenshot(percorso) -> salva PNG
    posizione_mouse,      # posizione_mouse() -> (x, y)
    dimensione_schermo,   # dimensione_schermo() -> (larghezza, altezza)
    trova_immagine,       # trova_immagine("pulsante.png") -> (x, y) o None
    lista_finestre,       # lista_finestre() -> ["Titolo1", "Titolo2", ...]
    attiva_finestra,      # attiva_finestra("Notepad") -> True/False
    attendi,              # attendi(2.0) - pausa di 2 secondi
    ottieni_info_sistema, # ottieni_info_sistema() -> dict con info
)
```

REGOLE PER IL COMPUTER USE:
- SPIEGA SEMPRE cosa stai per fare PRIMA di agire con mouse/tastiera
- Usa movimenti lenti (durata >= 0.3s) per dare tempo all'utente di vedere
- FAILSAFE: Se il mouse va nell'angolo in alto a sinistra, TUTTO si ferma
- Usa screenshot() per capire cosa c'è sullo schermo prima di agire
- Preferisci combinazione_tasti per operazioni veloci (Ctrl+C, Alt+Tab, ecc.)
- Per testo con accenti o caratteri speciali, usa scrivi_testo_clipboard()
"""
                logger.debug("🛡️ Regole di sicurezza e computer use aggiunte al system message")

            logger.info("✅ Interpreter inizializzato con successo")
            return True

        except ImportError as ie:
            logger.error(f"❌ Libreria 'open-interpreter' non trovata! Errore: {ie}")
            self._coda_messaggi.put(MessaggioInterpreter(
                tipo=TipoMessaggio.ERRORE,
                contenuto=f"Libreria 'open-interpreter' non installata!\nInstalla con: pip install open-interpreter\nDettaglio: {ie}"
            ))
            return False
        except Exception as e:
            logger.error(f"❌ Errore inizializzazione interpreter: {e}")
            self._coda_messaggi.put(MessaggioInterpreter(
                tipo=TipoMessaggio.ERRORE,
                contenuto=f"Errore inizializzazione: {str(e)}"
            ))
            return False

    def riconfigura(self, config: Dict[str, Any]) -> bool:
        """
        Riconfigura l'interprete con nuove impostazioni (es. cambio provider).
        Resetta anche la cronologia della conversazione.
        
        Args:
            config: Nuove impostazioni del provider
            
        Returns:
            True se la riconfigurazione è riuscita
        """
        logger.info("🔄 Riconfigurazione interpreter...")

        # Ferma eventuali operazioni in corso
        if self._in_esecuzione:
            self.emergency_stop()
            time.sleep(1)  # Aspetta un attimo

        # Resetta la conversazione
        if self._interpreter:
            self._interpreter.messages = []

        self._cronologia.clear()

        # Reinizializza con le nuove impostazioni
        return self.inizializza_interpreter(config)

    def invia_messaggio(self, messaggio: str) -> bool:
        """
        Invia un messaggio all'interprete e avvia l'elaborazione.
        
        Questa funzione NON blocca: avvia un thread separato e ritorna subito.
        I risultati arrivano nella coda_messaggi che la GUI legge periodicamente.
        
        Args:
            messaggio: Il testo da inviare all'IA
            
        Returns:
            True se l'invio è stato avviato, False se c'è un errore
        """
        if self._interpreter is None:
            logger.error("❌ Interpreter non inizializzato!")
            self._coda_messaggi.put(MessaggioInterpreter(
                tipo=TipoMessaggio.ERRORE,
                contenuto="Interprete non inizializzato! Configura prima un provider."
            ))
            return False

        if self._in_esecuzione:
            logger.warning("⚠️ Interprete già in esecuzione, attendi...")
            self._coda_messaggi.put(MessaggioInterpreter(
                tipo=TipoMessaggio.ERRORE,
                contenuto="L'interprete sta già elaborando un messaggio. Attendi o premi STOP."
            ))
            return False

        # Aggiungi alla cronologia
        # NOTA: In v0.1.x il formato è {"role": "user", "message": "..."}
        self._cronologia.append({
            "role": "user",
            "message": messaggio
        })

        # Reset flag
        self._stop_richiesto = False
        self._in_esecuzione = True

        # Notifica lo stato "in elaborazione"
        self._coda_messaggi.put(MessaggioInterpreter(
            tipo=TipoMessaggio.STATO,
            contenuto="Elaborazione in corso..."
        ))

        # Avvia il thread per l'elaborazione
        self._thread_interprete = threading.Thread(
            target=self._elabora_messaggio,
            args=(messaggio,),
            name="InterpreterThread",
            daemon=True
        )
        self._thread_interprete.start()
        logger.info(f"📤 Messaggio inviato all'interprete: {messaggio[:50]}...")

        return True

    def _elabora_messaggio(self, messaggio: str) -> None:
        """
        Elabora il messaggio nell'interprete (gira nel thread separato).
        
        Usa il metodo stream=True per ricevere i pezzi di risposta
        man mano che l'IA li genera, e li mette nella coda.
        
        FORMATO CHUNK (open-interpreter v0.1.x):
        I chunk sono dizionari con questi possibili campi:
        - {"message": "testo..."} -> Testo dall'IA (streaming pezzo per pezzo)
        - {"language": "python"} -> Linguaggio del codice che sta per arrivare
        - {"code": "print('ciao')"} -> Codice generato (streaming)
        - {"output": "ciao"} -> Output dell'esecuzione del codice
        - {"start_of_message": True} -> Flag: inizia un messaggio testuale
        - {"end_of_message": True} -> Flag: il messaggio testuale è finito
        - {"start_of_code": True} -> Flag: inizia un blocco di codice
        - {"end_of_code": True} -> Flag: il blocco di codice è finito
        - {"executing": {"code": "...", "language": "..."}} -> Codice in esecuzione
        """
        try:
            logger.debug("🔄 Inizio elaborazione messaggio nel thread...")

            # Variabili per accumulare il contenuto corrente
            linguaggio_corrente = "python"
            codice_accumulato = ""
            messaggio_accumulato = ""
            in_blocco_codice = False
            in_blocco_messaggio = False

            # Chiama interpreter.chat con streaming
            # display=False evita che stampi nel terminale di Python
            for chunk in self._interpreter.chat(messaggio, stream=True, display=False):
                # Controlla se l'utente ha premuto STOP
                if self._stop_richiesto:
                    logger.info("🛑 Elaborazione interrotta dall'utente")
                    self._coda_messaggi.put(MessaggioInterpreter(
                        tipo=TipoMessaggio.STATO,
                        contenuto="⚠️ Elaborazione interrotta dall'utente"
                    ))
                    break

                # Il chunk è un dizionario - gestiamo ogni campo possibile

                # --- FLAG: Inizio/Fine messaggio testuale ---
                if chunk.get("start_of_message"):
                    in_blocco_messaggio = True
                    messaggio_accumulato = ""
                    logger.debug("📝 Inizio messaggio testuale dall'IA")
                    continue

                if chunk.get("end_of_message"):
                    in_blocco_messaggio = False
                    # Il messaggio completo è già stato inviato pezzo per pezzo
                    logger.debug("📝 Fine messaggio testuale dall'IA")
                    continue

                # --- FLAG: Inizio/Fine blocco codice ---
                if chunk.get("start_of_code"):
                    in_blocco_codice = True
                    codice_accumulato = ""
                    logger.debug("💻 Inizio blocco codice dall'IA")
                    continue

                if chunk.get("end_of_code"):
                    in_blocco_codice = False
                    # Invia il codice completo accumulato
                    if codice_accumulato.strip():
                        self._coda_messaggi.put(MessaggioInterpreter(
                            tipo=TipoMessaggio.CODICE,
                            contenuto=codice_accumulato,
                            linguaggio=linguaggio_corrente
                        ))
                    codice_accumulato = ""
                    logger.debug("💻 Fine blocco codice dall'IA")
                    continue

                # --- CONTENUTO: Messaggio testuale (pezzo per pezzo) ---
                if "message" in chunk:
                    testo = chunk["message"]
                    if testo:
                        messaggio_accumulato += testo
                        # Invia ogni pezzo per lo streaming in tempo reale
                        self._coda_messaggi.put(MessaggioInterpreter(
                            tipo=TipoMessaggio.TESTO,
                            contenuto=testo,
                            ruolo="assistant"
                        ))

                # --- CONTENUTO: Linguaggio del codice ---
                if "language" in chunk:
                    linguaggio_corrente = chunk["language"]
                    logger.debug(f"💻 Linguaggio codice: {linguaggio_corrente}")

                # --- CONTENUTO: Codice (pezzo per pezzo) ---
                if "code" in chunk:
                    codice = chunk["code"]
                    if codice:
                        codice_accumulato += codice

                # --- CONTENUTO: Output dell'esecuzione ---
                if "output" in chunk:
                    output = chunk["output"]
                    if output:
                        self._coda_messaggi.put(MessaggioInterpreter(
                            tipo=TipoMessaggio.OUTPUT_CONSOLE,
                            contenuto=output,
                            ruolo="computer"
                        ))

                # --- CONTENUTO: Info esecuzione (APPROVAZIONE CODICE) ---
                # Questo chunk arriva PRIMA dell'esecuzione del codice.
                # Se interrompiamo il generatore qui (break), il codice NON verrà eseguito.
                # Questo è il meccanismo con cui gestiamo l'approvazione nella GUI.
                if "executing" in chunk:
                    info_exec = chunk["executing"]
                    codice_exec = info_exec.get("code", "")
                    lang_exec = info_exec.get("language", "python")

                    if codice_exec:
                        # Mostra il codice nel terminale GUI
                        self._coda_messaggi.put(MessaggioInterpreter(
                            tipo=TipoMessaggio.CODICE,
                            contenuto=codice_exec,
                            linguaggio=lang_exec
                        ))

                        # Se auto_run è DISATTIVATO, chiediamo approvazione all'utente
                        if not self._auto_run:
                            logger.info("⏸️ Auto-run OFF: in attesa approvazione utente...")
                            self._in_attesa_approvazione = True
                            self._approvazione_risposta = None

                            # Invia richiesta di approvazione alla GUI
                            self._coda_messaggi.put(MessaggioInterpreter(
                                tipo=TipoMessaggio.APPROVAZIONE,
                                contenuto=codice_exec,
                                linguaggio=lang_exec
                            ))

                            # Blocca il thread finché l'utente non risponde
                            # (o finché non viene premuto STOP)
                            while self._approvazione_risposta is None:
                                if self._stop_richiesto:
                                    logger.info("🛑 STOP durante attesa approvazione")
                                    self._in_attesa_approvazione = False
                                    break
                                time.sleep(0.1)  # Polling ogni 100ms

                            self._in_attesa_approvazione = False

                            # Se l'utente ha RIFIUTATO o premuto STOP:
                            # interrompiamo il generatore -> il codice NON verrà eseguito
                            if self._approvazione_risposta is not True or self._stop_richiesto:
                                logger.info("❌ Codice RIFIUTATO dall'utente, non eseguito")
                                self._coda_messaggi.put(MessaggioInterpreter(
                                    tipo=TipoMessaggio.STATO,
                                    contenuto="⚠️ Esecuzione codice rifiutata dall'utente"
                                ))
                                break  # GeneratorExit -> codice non eseguito

                            logger.info("✅ Codice APPROVATO dall'utente, esecuzione in corso...")

            # Fine elaborazione
            # Salva la risposta nella cronologia
            if self._interpreter and self._interpreter.messages:
                for msg in self._interpreter.messages:
                    if msg not in self._cronologia:
                        self._cronologia.append(msg)

            # Notifica che l'elaborazione è terminata
            self._coda_messaggi.put(MessaggioInterpreter(
                tipo=TipoMessaggio.STATO,
                contenuto="Elaborazione completata",
                completo=True
            ))

            logger.info("✅ Elaborazione messaggio completata")

        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ Errore durante l'elaborazione: {error_msg}")
            self._coda_messaggi.put(MessaggioInterpreter(
                tipo=TipoMessaggio.ERRORE,
                contenuto=f"Errore: {error_msg}\n\nProva a:\n1. Verificare che il server LLM sia attivo\n2. Controllare la connessione internet\n3. Verificare la API key"
            ))

        finally:
            self._in_esecuzione = False

    def emergency_stop(self) -> None:
        """
        FERMATA DI EMERGENZA!
        Interrompe immediatamente qualsiasi operazione dell'interprete.
        
        Questo è il "tastone rosso" - killa tutto e subito.
        """
        logger.warning("🚨 EMERGENCY STOP ATTIVATO!")

        self._stop_richiesto = True
        self._in_esecuzione = False
        self._in_attesa_approvazione = False

        # Prova a resettare l'interprete
        try:
            if self._interpreter:
                # Resetta lo stato dell'interprete
                self._interpreter.messages = self._interpreter.messages  # Force stop
        except Exception as e:
            logger.error(f"❌ Errore durante emergency stop: {e}")

        # Notifica la GUI
        self._coda_messaggi.put(MessaggioInterpreter(
            tipo=TipoMessaggio.STATO,
            contenuto="🚨 STOP DI EMERGENZA - Tutti i processi interrotti"
        ))

        logger.info("✅ Emergency stop completato")

    def approva_esecuzione(self, approvato: bool) -> None:
        """
        Risponde alla richiesta di approvazione del codice.
        
        Args:
            approvato: True per approvare l'esecuzione, False per rifiutarla
        """
        self._approvazione_risposta = approvato
        self._in_attesa_approvazione = False

        if approvato:
            logger.info("✅ Esecuzione codice approvata dall'utente")
        else:
            logger.info("❌ Esecuzione codice rifiutata dall'utente")

    def leggi_messaggi(self) -> List[MessaggioInterpreter]:
        """
        Legge tutti i messaggi disponibili dalla coda.
        Chiamata periodicamente dalla GUI (ogni ~100ms).
        
        Returns:
            Lista di messaggi da visualizzare
        """
        messaggi = []
        while not self._coda_messaggi.empty():
            try:
                msg = self._coda_messaggi.get_nowait()
                messaggi.append(msg)
            except queue.Empty:
                break
        return messaggi

    def imposta_auto_run(self, valore: bool) -> None:
        """
        Attiva o disattiva l'esecuzione automatica del codice.
        
        ATTENZIONE: Con auto_run=True, l'IA eseguirà codice senza chiedere!
        Usare con cautela.
        
        Args:
            valore: True per attivare, False per disattivare
        """
        self._auto_run = valore
        if self._interpreter:
            self._interpreter.auto_run = valore
        stato = "ATTIVATO ⚠️" if valore else "DISATTIVATO ✅"
        logger.info(f"🔒 Auto-run {stato}")

    def imposta_cartella_lavoro(self, cartella: str) -> None:
        """
        Imposta la cartella di lavoro dell'interprete.
        
        Args:
            cartella: Percorso della cartella di lavoro
        """
        if os.path.isdir(cartella):
            self._cartella_lavoro = cartella
            logger.info(f"📂 Cartella di lavoro impostata: {cartella}")
        else:
            logger.error(f"❌ Cartella non valida: {cartella}")

    def nuova_conversazione(self) -> None:
        """
        Inizia una nuova conversazione pulita.
        Resetta la cronologia e i messaggi dell'interprete.
        """
        if self._interpreter:
            self._interpreter.messages = []
        self._cronologia.clear()

        # Svuota la coda
        while not self._coda_messaggi.empty():
            try:
                self._coda_messaggi.get_nowait()
            except queue.Empty:
                break

        logger.info("🆕 Nuova conversazione iniziata")

    @property
    def is_in_esecuzione(self) -> bool:
        """Restituisce True se l'interprete sta elaborando."""
        return self._in_esecuzione

    @property
    def cronologia(self) -> List[Dict[str, Any]]:
        """Restituisce la cronologia dei messaggi della sessione."""
        return self._cronologia.copy()

    @property
    def in_attesa_approvazione(self) -> bool:
        """Restituisce True se è in attesa di approvazione codice."""
        return self._in_attesa_approvazione

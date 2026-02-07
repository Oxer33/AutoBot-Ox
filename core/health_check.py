# ============================================
# Health Check (Controllo Salute) - AutoBot Ox
# Verifica periodicamente se il server LLM locale
# è attivo e raggiungibile sulla porta 1234
# ============================================

import threading
import time
import logging
import requests
from typing import Callable, Optional

# Logger per questo modulo
logger = logging.getLogger("AutoBotOx.HealthCheck")


class ControlloSalute:
    """
    Controlla periodicamente se il server LLM locale è raggiungibile.
    
    Come funziona:
    1. Ogni N secondi (default: 5) prova a contattare il server locale
    2. Se il server risponde, lo stato è "online" (pallino verde nella UI)
    3. Se non risponde, lo stato è "offline" (pallino rosso nella UI)
    4. Quando lo stato cambia, notifica la GUI tramite un callback
    
    Il controllo gira in un thread separato per non bloccare la GUI.
    """

    def __init__(
        self,
        url_server: str = "http://localhost:1234/v1/models",
        intervallo_secondi: int = 5,
        callback_stato: Optional[Callable[[bool], None]] = None
    ):
        """
        Inizializza il controllo di salute.
        
        Args:
            url_server: URL da pingare per verificare se il server è attivo
            intervallo_secondi: Ogni quanti secondi controllare
            callback_stato: Funzione da chiamare quando lo stato cambia
                           Riceve True (online) o False (offline)
        """
        self._url_server = url_server
        self._intervallo = intervallo_secondi
        self._callback_stato = callback_stato

        # Stato interno
        self._online: bool = False           # Il server è raggiungibile?
        self._in_esecuzione: bool = False     # Il thread di controllo è attivo?
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()  # Evento per fermare il thread

        logger.info(
            f"🏥 ControlloSalute inizializzato - URL: {url_server}, "
            f"Intervallo: {intervallo_secondi}s"
        )

    def avvia(self) -> None:
        """
        Avvia il controllo periodico in un thread separato.
        Se è già in esecuzione, non fa nulla.
        """
        if self._in_esecuzione:
            logger.warning("⚠️ ControlloSalute già in esecuzione, ignoro avvio duplicato")
            return

        self._stop_event.clear()
        self._in_esecuzione = True

        # Crea e avvia il thread (daemon=True: si chiude quando si chiude l'app)
        self._thread = threading.Thread(
            target=self._loop_controllo,
            name="HealthCheckThread",
            daemon=True
        )
        self._thread.start()
        logger.info("▶️ ControlloSalute avviato")

    def ferma(self) -> None:
        """
        Ferma il controllo periodico.
        Aspetta che il thread corrente termini prima di continuare.
        """
        if not self._in_esecuzione:
            return

        logger.info("⏹️ Fermando ControlloSalute...")
        self._stop_event.set()  # Segnala al thread di fermarsi
        self._in_esecuzione = False

        # Aspetta che il thread termini (max 10 secondi)
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=10)
            logger.info("✅ Thread ControlloSalute terminato")

    def _loop_controllo(self) -> None:
        """
        Loop principale del controllo di salute.
        Gira nel thread separato e controlla periodicamente il server.
        """
        logger.debug("🔄 Loop ControlloSalute iniziato")

        while not self._stop_event.is_set():
            # Esegui il controllo
            nuovo_stato = self._verifica_server()

            # Se lo stato è cambiato, notifica la GUI
            if nuovo_stato != self._online:
                stato_testo = "ONLINE ✅" if nuovo_stato else "OFFLINE ❌"
                logger.info(f"🔄 Stato server locale cambiato: {stato_testo}")
                self._online = nuovo_stato

                # Chiama il callback per aggiornare la GUI
                if self._callback_stato:
                    try:
                        self._callback_stato(nuovo_stato)
                    except Exception as e:
                        logger.error(f"❌ Errore nel callback stato: {e}")

            # Aspetta l'intervallo prima del prossimo controllo
            # Usa wait() invece di sleep() per poter essere interrotto
            self._stop_event.wait(timeout=self._intervallo)

        logger.debug("🛑 Loop ControlloSalute terminato")

    def _verifica_server(self) -> bool:
        """
        Verifica se il server locale è raggiungibile.
        
        Prova a fare una richiesta GET all'endpoint /v1/models.
        Se riceve una risposta (qualsiasi codice HTTP), il server è attivo.
        
        Returns:
            True se il server risponde, False se è irraggiungibile
        """
        try:
            risposta = requests.get(
                self._url_server,
                timeout=3  # Timeout breve per non bloccare
            )
            # Qualsiasi risposta HTTP significa che il server è attivo
            logger.debug(f"🏥 Health check OK - Status: {risposta.status_code}")
            return True

        except requests.ConnectionError:
            logger.debug("🏥 Health check FALLITO - Server non raggiungibile")
            return False
        except requests.Timeout:
            logger.debug("🏥 Health check FALLITO - Timeout")
            return False
        except Exception as e:
            logger.debug(f"🏥 Health check FALLITO - Errore: {e}")
            return False

    @property
    def is_online(self) -> bool:
        """Restituisce True se il server locale è attualmente online."""
        return self._online

    @property
    def is_in_esecuzione(self) -> bool:
        """Restituisce True se il controllo periodico è attivo."""
        return self._in_esecuzione

    def controlla_ora(self) -> bool:
        """
        Esegue un controllo immediato (sincrono) senza aspettare il prossimo ciclo.
        Utile per verifiche on-demand.
        
        Returns:
            True se il server è online, False altrimenti
        """
        self._online = self._verifica_server()
        return self._online

    def imposta_url(self, nuovo_url: str) -> None:
        """
        Cambia l'URL del server da monitorare.
        
        Args:
            nuovo_url: Il nuovo URL (es. "http://localhost:5000/v1/models")
        """
        logger.info(f"🔄 URL server cambiato: {self._url_server} -> {nuovo_url}")
        self._url_server = nuovo_url

    def imposta_callback(self, callback: Callable[[bool], None]) -> None:
        """
        Imposta o aggiorna la funzione callback per i cambiamenti di stato.
        
        Args:
            callback: Funzione che riceve True (online) o False (offline)
        """
        self._callback_stato = callback
        logger.debug("🔄 Callback stato aggiornato")

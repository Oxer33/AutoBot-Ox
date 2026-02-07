# ============================================
# Gestione Impostazioni - AutoBot Ox
# Carica, salva e gestisce tutte le configurazioni
# dell'applicazione in modo sicuro
# ============================================

import json
import os
import logging
from pathlib import Path
from typing import Any, Optional

# Logger per questo modulo
logger = logging.getLogger("AutoBotOx.Config")

# Percorso base dell'applicazione (dove si trova l'eseguibile o lo script)
BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = BASE_DIR / "config"
DEFAULT_CONFIG_PATH = CONFIG_DIR / "default_config.json"
USER_CONFIG_PATH = CONFIG_DIR / "user_config.json"


class GestoreImpostazioni:
    """
    Gestisce il caricamento e il salvataggio delle impostazioni.
    
    Come funziona:
    1. Carica prima il file di configurazione predefinito (default_config.json)
    2. Se esiste un file utente (user_config.json), sovrascrive i valori
    3. Ogni modifica viene salvata nel file utente (mai nel default!)
    """

    def __init__(self):
        """Inizializza il gestore caricando le configurazioni."""
        logger.info("🔧 Inizializzazione GestoreImpostazioni...")
        self._config: dict = {}
        self._carica_configurazione()

    def _carica_configurazione(self) -> None:
        """
        Carica la configurazione in due passaggi:
        1. Legge il file default (sempre presente)
        2. Sovrascrive con il file utente (se esiste)
        """
        # Passo 1: Carica configurazione predefinita
        try:
            with open(DEFAULT_CONFIG_PATH, "r", encoding="utf-8") as f:
                self._config = json.load(f)
                logger.info(f"✅ Configurazione predefinita caricata da: {DEFAULT_CONFIG_PATH}")
        except FileNotFoundError:
            logger.error(f"❌ File configurazione predefinita non trovato: {DEFAULT_CONFIG_PATH}")
            self._config = {}
        except json.JSONDecodeError as e:
            logger.error(f"❌ Errore parsing JSON configurazione predefinita: {e}")
            self._config = {}

        # Passo 2: Sovrascrive con configurazione utente (se esiste)
        if USER_CONFIG_PATH.exists():
            try:
                with open(USER_CONFIG_PATH, "r", encoding="utf-8") as f:
                    config_utente = json.load(f)
                    self._merge_config(self._config, config_utente)
                    logger.info(f"✅ Configurazione utente caricata da: {USER_CONFIG_PATH}")
            except json.JSONDecodeError as e:
                logger.warning(f"⚠️ Errore parsing configurazione utente, uso default: {e}")
        else:
            logger.info("ℹ️ Nessuna configurazione utente trovata, uso configurazione predefinita")

    def _merge_config(self, base: dict, override: dict) -> None:
        """
        Unisce ricorsivamente due dizionari di configurazione.
        I valori in 'override' sovrascrivono quelli in 'base'.
        
        Esempio: se base = {"a": {"b": 1, "c": 2}} e override = {"a": {"b": 99}}
        il risultato sarà {"a": {"b": 99, "c": 2}}
        """
        for chiave, valore in override.items():
            if chiave in base and isinstance(base[chiave], dict) and isinstance(valore, dict):
                self._merge_config(base[chiave], valore)
            else:
                base[chiave] = valore

    def ottieni(self, percorso: str, default: Any = None) -> Any:
        """
        Ottiene un valore dalla configurazione usando un percorso con punti.
        
        Esempio: ottieni("provider_locale.api_base") -> "http://localhost:1234/v1"
        
        Args:
            percorso: Percorso separato da punti (es. "sicurezza.auto_run")
            default: Valore da restituire se il percorso non esiste
            
        Returns:
            Il valore trovato o il default
        """
        chiavi = percorso.split(".")
        valore = self._config

        for chiave in chiavi:
            if isinstance(valore, dict) and chiave in valore:
                valore = valore[chiave]
            else:
                logger.debug(f"⚠️ Chiave non trovata nel percorso: {percorso}")
                return default

        return valore

    def imposta(self, percorso: str, valore: Any) -> None:
        """
        Imposta un valore nella configurazione e salva automaticamente.
        
        Esempio: imposta("sicurezza.auto_run", True)
        
        Args:
            percorso: Percorso separato da punti
            valore: Il nuovo valore da impostare
        """
        chiavi = percorso.split(".")
        config = self._config

        # Naviga fino al penultimo livello, creando dizionari se necessario
        for chiave in chiavi[:-1]:
            if chiave not in config or not isinstance(config[chiave], dict):
                config[chiave] = {}
            config = config[chiave]

        # Imposta il valore finale
        config[chiavi[-1]] = valore
        logger.info(f"✅ Impostazione aggiornata: {percorso} = {valore}")

        # Salva automaticamente nel file utente
        self.salva()

    def salva(self) -> None:
        """
        Salva la configurazione corrente nel file utente.
        Non modifica mai il file di configurazione predefinito!
        """
        try:
            # Assicurati che la cartella config esista
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)

            with open(USER_CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=4, ensure_ascii=False)
                logger.info(f"💾 Configurazione salvata in: {USER_CONFIG_PATH}")
        except Exception as e:
            logger.error(f"❌ Errore salvataggio configurazione: {e}")

    def ottieni_config_completa(self) -> dict:
        """Restituisce una copia dell'intera configurazione."""
        return self._config.copy()

    def reset_a_default(self) -> None:
        """
        Ripristina tutte le impostazioni ai valori predefiniti.
        Elimina il file di configurazione utente.
        """
        logger.info("🔄 Reset configurazione ai valori predefiniti...")
        if USER_CONFIG_PATH.exists():
            USER_CONFIG_PATH.unlink()
            logger.info(f"🗑️ File configurazione utente rimosso: {USER_CONFIG_PATH}")

        self._carica_configurazione()

    @property
    def provider_attivo(self) -> str:
        """Restituisce il provider attualmente selezionato ('locale' o 'cloud')."""
        return self.ottieni("provider_attivo", "locale")

    @provider_attivo.setter
    def provider_attivo(self, valore: str) -> None:
        """Imposta il provider attivo."""
        if valore not in ("locale", "cloud"):
            logger.error(f"❌ Provider non valido: {valore}. Usa 'locale' o 'cloud'.")
            return
        self.imposta("provider_attivo", valore)

    @property
    def auto_run(self) -> bool:
        """Restituisce se l'auto-run è attivo."""
        return self.ottieni("sicurezza.auto_run", False)

    @auto_run.setter
    def auto_run(self, valore: bool) -> None:
        """Imposta l'auto-run."""
        self.imposta("sicurezza.auto_run", valore)

    @property
    def api_key_openrouter(self) -> str:
        """Restituisce la API key di OpenRouter."""
        return self.ottieni("provider_cloud.api_key", "")

    @api_key_openrouter.setter
    def api_key_openrouter(self, valore: str) -> None:
        """Imposta la API key di OpenRouter."""
        self.imposta("provider_cloud.api_key", valore)

    @property
    def cartella_lavoro(self) -> str:
        """Restituisce la cartella di lavoro corrente."""
        cartella = self.ottieni("sicurezza.cartella_lavoro", "")
        if not cartella:
            # Se non è impostata, usa la cartella dell'applicazione
            return str(BASE_DIR)
        return cartella

    @cartella_lavoro.setter
    def cartella_lavoro(self, valore: str) -> None:
        """Imposta la cartella di lavoro."""
        self.imposta("sicurezza.cartella_lavoro", valore)

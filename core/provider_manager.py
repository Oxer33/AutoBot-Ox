# ============================================
# Provider Manager - AutoBot Ox
# Gestisce la configurazione dei provider LLM
# (locale su porta 1234 e DeepSeek su OpenRouter)
# ============================================

import logging
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass

# Logger per questo modulo
logger = logging.getLogger("AutoBotOx.ProviderManager")


@dataclass
class ConfigProvider:
    """
    Rappresenta la configurazione di un singolo provider LLM.
    
    Un provider è un "fornitore" di intelligenza artificiale.
    Può essere locale (LM Studio sulla porta 1234) o cloud (OpenRouter).
    """
    nome: str                    # Nome leggibile (es. "LLM Locale")
    api_base: str               # URL base dell'API
    modello: str                # Nome del modello da usare
    api_key: str = ""           # Chiave API (vuota per il locale)
    offline: bool = False       # Se True, non fa richieste online
    timeout: int = 30           # Timeout in secondi
    temperatura: float = 0.7    # Creatività del modello (0=preciso, 1=creativo)
    contesto_max: int = 16000   # Dimensione massima del contesto in token


class GestoreProvider:
    """
    Gestisce i provider LLM disponibili e permette di switchare tra loro.
    
    Come funziona:
    1. Registra i provider disponibili (locale e cloud)
    2. Permette di selezionare il provider attivo
    3. Restituisce la configurazione corretta per Open Interpreter
    
    Esempio:
        gestore = GestoreProvider()
        gestore.registra_locale("http://localhost:1234/v1", "openai/local")
        gestore.registra_cloud("https://openrouter.ai/api/v1", "deepseek/...", "sk-...")
        
        config = gestore.ottieni_config_attiva()
    """

    def __init__(self):
        """Inizializza il gestore con i provider vuoti."""
        self._providers: Dict[str, ConfigProvider] = {}
        self._provider_attivo: str = "locale"
        logger.info("🔌 GestoreProvider inizializzato")

    def registra_locale(
        self,
        api_base: str = "http://localhost:1234/v1",
        modello: str = "openai/local",
        timeout: int = 30
    ) -> None:
        """
        Registra il provider LLM locale (LM Studio / Ollama).
        
        Args:
            api_base: URL del server locale (default: porta 1234)
            modello: Nome del modello da usare
            timeout: Timeout in secondi per le richieste
        """
        self._providers["locale"] = ConfigProvider(
            nome="LLM Locale (LM Studio / Ollama)",
            api_base=api_base,
            modello=modello,
            # IMPORTANTE: litellm richiede SEMPRE una API key, anche per server locali!
            # Senza questa key dummy, si ottiene: AuthenticationError: No API key provided
            api_key="not-needed",
            offline=True,       # Il locale non ha bisogno di internet
            timeout=timeout,
            contesto_max=4096   # I modelli locali hanno spesso un contesto ridotto
        )
        logger.info(f"✅ Provider locale registrato: {api_base} - Modello: {modello}")

    def registra_cloud(
        self,
        api_base: str = "https://openrouter.ai/api/v1",
        modello: str = "openrouter/deepseek/deepseek-r1-0528:free",
        api_key: str = "",
        timeout: int = 60
    ) -> None:
        """
        Registra il provider cloud (OpenRouter + DeepSeek).
        
        Args:
            api_base: URL dell'API OpenRouter
            modello: Nome del modello DeepSeek
            api_key: Chiave API di OpenRouter
            timeout: Timeout in secondi (più alto perché DeepSeek è lento)
        """
        self._providers["cloud"] = ConfigProvider(
            nome="DeepSeek R1 (OpenRouter)",
            api_base=api_base,
            modello=modello,
            api_key=api_key,
            offline=False,
            timeout=timeout,
            contesto_max=64000  # DeepSeek R1 ha un contesto molto grande
        )
        logger.info(f"✅ Provider cloud registrato: {api_base} - Modello: {modello}")

    def seleziona_provider(self, tipo: str) -> bool:
        """
        Seleziona il provider attivo.
        
        Args:
            tipo: "locale" o "cloud"
            
        Returns:
            True se la selezione è riuscita, False se il tipo non esiste
        """
        if tipo not in self._providers:
            logger.error(f"❌ Provider non trovato: {tipo}. Disponibili: {list(self._providers.keys())}")
            return False

        self._provider_attivo = tipo
        provider = self._providers[tipo]
        logger.info(f"🔄 Provider selezionato: {provider.nome}")
        return True

    def ottieni_config_attiva(self) -> Optional[ConfigProvider]:
        """
        Restituisce la configurazione del provider attualmente selezionato.
        
        Returns:
            ConfigProvider del provider attivo, o None se non configurato
        """
        if self._provider_attivo not in self._providers:
            logger.error(f"❌ Nessun provider attivo configurato")
            return None

        return self._providers[self._provider_attivo]

    def ottieni_config_interpreter(self) -> Dict[str, Any]:
        """
        Restituisce un dizionario con le impostazioni pronte per Open Interpreter.
        
        Questo dizionario può essere usato direttamente per configurare
        l'oggetto interpreter.
        
        Returns:
            Dizionario con le impostazioni per interpreter
        """
        config = self.ottieni_config_attiva()
        if config is None:
            return {}

        risultato = {
            "api_base": config.api_base,
            "model": config.modello,
            "offline": config.offline,
            "temperature": config.temperatura,
            "context_window": config.contesto_max,
        }

        # IMPORTANTE: Passa SEMPRE la api_key!
        # Per il locale usiamo "not-needed" come dummy (litellm la richiede comunque)
        # Per il cloud usiamo la vera API key di OpenRouter
        if config.api_key:
            risultato["api_key"] = config.api_key

        logger.debug(f"📋 Config interpreter generata per: {config.nome}")
        return risultato

    @property
    def provider_attivo_nome(self) -> str:
        """Restituisce il nome leggibile del provider attivo."""
        config = self.ottieni_config_attiva()
        return config.nome if config else "Nessuno"

    @property
    def provider_attivo_tipo(self) -> str:
        """Restituisce il tipo del provider attivo ('locale' o 'cloud')."""
        return self._provider_attivo

    @property
    def providers_disponibili(self) -> Dict[str, str]:
        """
        Restituisce un dizionario con i provider disponibili.
        Formato: {"locale": "LLM Locale (LM Studio)", "cloud": "DeepSeek R1 (OpenRouter)"}
        """
        return {tipo: p.nome for tipo, p in self._providers.items()}

    def aggiorna_api_key(self, api_key: str) -> None:
        """
        Aggiorna la API key del provider cloud.
        
        Args:
            api_key: La nuova API key
        """
        if "cloud" in self._providers:
            self._providers["cloud"].api_key = api_key
            logger.info("🔑 API key cloud aggiornata")
        else:
            logger.warning("⚠️ Nessun provider cloud registrato per aggiornare la API key")

    def verifica_config_valida(self) -> Tuple[bool, str]:
        """
        Verifica che la configurazione del provider attivo sia valida.
        
        Returns:
            Tupla (valido, messaggio_errore)
        """
        config = self.ottieni_config_attiva()

        if config is None:
            return False, "Nessun provider configurato"

        if not config.api_base:
            return False, "URL API base mancante"

        if not config.modello:
            return False, "Modello non specificato"

        # Per il cloud, serve la API key
        if self._provider_attivo == "cloud" and (not config.api_key or config.api_key == "not-needed"):
            return False, "API key OpenRouter mancante! Inseriscila nelle impostazioni."

        return True, "Configurazione valida"

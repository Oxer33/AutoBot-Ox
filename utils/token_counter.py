# ============================================
# Token Counter - AutoBot Ox
# Tiene traccia dei token utilizzati con OpenRouter
# per monitorare i costi e l'utilizzo
# ============================================

import logging
from typing import Optional

# Logger per questo modulo
logger = logging.getLogger("AutoBotOx.TokenCounter")


class ContaToken:
    """
    Tiene traccia dei token utilizzati durante la sessione.
    
    Come funziona:
    - Conta i token in input (quelli che mandiamo all'IA)
    - Conta i token in output (quelli che l'IA ci restituisce)
    - Calcola il totale e una stima approssimativa dei costi
    
    Nota: Il modello deepseek-r1-0528:free è GRATUITO su OpenRouter,
    ma è comunque utile monitorare l'utilizzo per capire quanto
    stiamo usando e non superare eventuali limiti di rate.
    """

    def __init__(self):
        """Inizializza il contatore a zero."""
        self._token_input: int = 0        # Token inviati
        self._token_output: int = 0       # Token ricevuti
        self._richieste_totali: int = 0   # Numero di richieste fatte
        logger.info("📊 ContaToken inizializzato")

    def aggiungi(self, token_input: int = 0, token_output: int = 0) -> None:
        """
        Aggiunge token al conteggio.
        
        Args:
            token_input: Numero di token inviati in questa richiesta
            token_output: Numero di token ricevuti in questa risposta
        """
        self._token_input += token_input
        self._token_output += token_output
        self._richieste_totali += 1
        logger.debug(
            f"📊 Token aggiunti - Input: +{token_input}, Output: +{token_output} | "
            f"Totale sessione: {self.totale}"
        )

    @property
    def token_input(self) -> int:
        """Restituisce il totale dei token inviati."""
        return self._token_input

    @property
    def token_output(self) -> int:
        """Restituisce il totale dei token ricevuti."""
        return self._token_output

    @property
    def totale(self) -> int:
        """Restituisce il totale dei token (input + output)."""
        return self._token_input + self._token_output

    @property
    def richieste(self) -> int:
        """Restituisce il numero totale di richieste fatte."""
        return self._richieste_totali

    def stima_parole(self) -> int:
        """
        Stima approssimativa delle parole generate.
        Regola empirica: ~0.75 parole per token
        """
        return int(self._token_output * 0.75)

    def ottieni_riepilogo(self) -> str:
        """
        Restituisce un riepilogo leggibile dell'utilizzo.
        
        Returns:
            Stringa formattata con il riepilogo dei token
        """
        return (
            f"📊 Riepilogo Token Sessione:\n"
            f"   ├─ Token Input:  {self._token_input:,}\n"
            f"   ├─ Token Output: {self._token_output:,}\n"
            f"   ├─ Token Totali: {self.totale:,}\n"
            f"   ├─ Richieste:    {self._richieste_totali}\n"
            f"   └─ Parole stimate: ~{self.stima_parole():,}"
        )

    def reset(self) -> None:
        """Resetta tutti i contatori a zero."""
        self._token_input = 0
        self._token_output = 0
        self._richieste_totali = 0
        logger.info("🔄 ContaToken resettato")

    def formatta_breve(self) -> str:
        """
        Formato breve per la status bar.
        Esempio: "Token: 1,234 (In: 500 / Out: 734)"
        """
        return f"Token: {self.totale:,} (In: {self._token_input:,} / Out: {self._token_output:,})"

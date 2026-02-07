# ============================================
# Computer Use - AutoBot Ox
# Modulo per il controllo di tastiera e mouse
# tramite l'IA (Open Interpreter).
#
# COME FUNZIONA (spiegazione per principianti):
# L'IA genera codice Python che usa queste funzioni
# per controllare il computer. Ad esempio:
#   from core.computer_use import muovi_mouse, clicca, scrivi_testo
#   muovi_mouse(500, 300)
#   clicca()
#   scrivi_testo("Ciao mondo!")
#
# SICUREZZA:
# - Ogni azione viene loggata per tracciabilità
# - PyAutoGUI ha un failsafe: muovi il mouse nell'angolo
#   in alto a sinistra per interrompere TUTTO
# - Pause tra le azioni per dare tempo all'utente di reagire
# ============================================

import logging
import time
from typing import Optional, Tuple, List

# Logger per questo modulo
logger = logging.getLogger("AutoBotOx.ComputerUse")

# Flag globale per abilitare/disabilitare il computer use
_computer_use_abilitato = False

# Pausa di sicurezza tra le azioni (secondi)
_pausa_sicurezza = 0.3


def _importa_pyautogui():
    """
    Importa pyautogui con le configurazioni di sicurezza.
    
    Ritorna il modulo pyautogui configurato, o None se non disponibile.
    """
    try:
        import pyautogui
        
        # FAILSAFE: Se il mouse va nell'angolo in alto a sinistra,
        # pyautogui solleva un'eccezione e FERMA TUTTO.
        # Questo è il meccanismo di emergenza!
        pyautogui.FAILSAFE = True
        
        # Pausa automatica tra le operazioni (sicurezza)
        pyautogui.PAUSE = _pausa_sicurezza
        
        return pyautogui
    except ImportError:
        logger.error("❌ pyautogui non installato! Installa con: pip install pyautogui")
        return None


def abilita_computer_use(abilitato: bool = True) -> None:
    """
    Abilita o disabilita il controllo del computer.
    
    Args:
        abilitato: True per abilitare, False per disabilitare
    """
    global _computer_use_abilitato
    _computer_use_abilitato = abilitato
    stato = "ABILITATO ✅" if abilitato else "DISABILITATO ❌"
    logger.info(f"🖱️ Computer Use: {stato}")


def is_abilitato() -> bool:
    """Controlla se il computer use è abilitato."""
    return _computer_use_abilitato


def imposta_pausa(secondi: float) -> None:
    """
    Imposta la pausa di sicurezza tra le azioni.
    
    Args:
        secondi: Pausa in secondi (min 0.1, max 5.0)
    """
    global _pausa_sicurezza
    _pausa_sicurezza = max(0.1, min(5.0, secondi))
    logger.info(f"⏱️ Pausa sicurezza impostata a {_pausa_sicurezza}s")


# ============================================
# FUNZIONI MOUSE
# ============================================

def muovi_mouse(x: int, y: int, durata: float = 0.3) -> bool:
    """
    Muove il mouse alle coordinate specificate.
    
    Args:
        x: Coordinata X (pixel da sinistra)
        y: Coordinata Y (pixel dall'alto)
        durata: Durata del movimento in secondi (0.3 = fluido)
    
    Returns:
        True se il movimento è riuscito
    """
    if not _computer_use_abilitato:
        logger.warning("⚠️ Computer Use disabilitato! Abilita prima di usare il mouse.")
        return False
    
    pyautogui = _importa_pyautogui()
    if not pyautogui:
        return False
    
    try:
        logger.info(f"🖱️ Muovo mouse a ({x}, {y}) in {durata}s")
        pyautogui.moveTo(x, y, duration=durata)
        return True
    except pyautogui.FailSafeException:
        logger.critical("🛑 FAILSAFE ATTIVATO! Mouse nell'angolo in alto a sinistra.")
        abilita_computer_use(False)
        return False
    except Exception as e:
        logger.error(f"❌ Errore muovi_mouse: {e}")
        return False


def clicca(
    x: Optional[int] = None, 
    y: Optional[int] = None, 
    pulsante: str = "left",
    doppio: bool = False
) -> bool:
    """
    Clicca con il mouse nella posizione corrente o specificata.
    
    Args:
        x: Coordinata X (None = posizione corrente)
        y: Coordinata Y (None = posizione corrente)
        pulsante: "left", "right", o "middle"
        doppio: True per doppio click
    
    Returns:
        True se il click è riuscito
    """
    if not _computer_use_abilitato:
        logger.warning("⚠️ Computer Use disabilitato!")
        return False
    
    pyautogui = _importa_pyautogui()
    if not pyautogui:
        return False
    
    try:
        tipo = "doppio click" if doppio else "click"
        pos = f"({x}, {y})" if x is not None else "posizione corrente"
        logger.info(f"🖱️ {tipo} {pulsante} a {pos}")
        
        if doppio:
            pyautogui.doubleClick(x=x, y=y, button=pulsante)
        else:
            pyautogui.click(x=x, y=y, button=pulsante)
        return True
    except pyautogui.FailSafeException:
        logger.critical("🛑 FAILSAFE ATTIVATO!")
        abilita_computer_use(False)
        return False
    except Exception as e:
        logger.error(f"❌ Errore clicca: {e}")
        return False


def trascina(
    x_inizio: int, y_inizio: int,
    x_fine: int, y_fine: int,
    durata: float = 0.5
) -> bool:
    """
    Trascina il mouse da un punto a un altro (drag & drop).
    
    Args:
        x_inizio, y_inizio: Punto di partenza
        x_fine, y_fine: Punto di arrivo
        durata: Durata del trascinamento
    
    Returns:
        True se il trascinamento è riuscito
    """
    if not _computer_use_abilitato:
        logger.warning("⚠️ Computer Use disabilitato!")
        return False
    
    pyautogui = _importa_pyautogui()
    if not pyautogui:
        return False
    
    try:
        logger.info(f"🖱️ Trascino da ({x_inizio},{y_inizio}) a ({x_fine},{y_fine})")
        pyautogui.moveTo(x_inizio, y_inizio, duration=0.2)
        pyautogui.drag(
            x_fine - x_inizio, 
            y_fine - y_inizio, 
            duration=durata
        )
        return True
    except pyautogui.FailSafeException:
        logger.critical("🛑 FAILSAFE ATTIVATO!")
        abilita_computer_use(False)
        return False
    except Exception as e:
        logger.error(f"❌ Errore trascina: {e}")
        return False


def scroll(quantita: int, x: Optional[int] = None, y: Optional[int] = None) -> bool:
    """
    Scrolla la rotellina del mouse.
    
    Args:
        quantita: Positivo = su, Negativo = giù (es. 3, -5)
        x, y: Posizione dove scrollare (None = posizione corrente)
    
    Returns:
        True se lo scroll è riuscito
    """
    if not _computer_use_abilitato:
        logger.warning("⚠️ Computer Use disabilitato!")
        return False
    
    pyautogui = _importa_pyautogui()
    if not pyautogui:
        return False
    
    try:
        direzione = "su" if quantita > 0 else "giù"
        logger.info(f"🖱️ Scroll {direzione} di {abs(quantita)}")
        pyautogui.scroll(quantita, x=x, y=y)
        return True
    except pyautogui.FailSafeException:
        logger.critical("🛑 FAILSAFE ATTIVATO!")
        abilita_computer_use(False)
        return False
    except Exception as e:
        logger.error(f"❌ Errore scroll: {e}")
        return False


# ============================================
# FUNZIONI TASTIERA
# ============================================

def scrivi_testo(testo: str, intervallo: float = 0.03) -> bool:
    """
    Scrive testo come se stessi digitando sulla tastiera.
    
    NOTA: Non funziona con caratteri speciali non-ASCII.
    Per quelli usa scrivi_testo_clipboard().
    
    Args:
        testo: Il testo da scrivere
        intervallo: Pausa tra un carattere e l'altro (secondi)
    
    Returns:
        True se la scrittura è riuscita
    """
    if not _computer_use_abilitato:
        logger.warning("⚠️ Computer Use disabilitato!")
        return False
    
    pyautogui = _importa_pyautogui()
    if not pyautogui:
        return False
    
    try:
        logger.info(f"⌨️ Scrivo testo: '{testo[:50]}{'...' if len(testo) > 50 else ''}'")
        pyautogui.typewrite(testo, interval=intervallo)
        return True
    except pyautogui.FailSafeException:
        logger.critical("🛑 FAILSAFE ATTIVATO!")
        abilita_computer_use(False)
        return False
    except Exception as e:
        logger.error(f"❌ Errore scrivi_testo: {e}")
        return False


def scrivi_testo_clipboard(testo: str) -> bool:
    """
    Scrive testo usando la clipboard (copia/incolla).
    Supporta TUTTI i caratteri, inclusi Unicode e caratteri speciali.
    
    Args:
        testo: Il testo da scrivere (qualsiasi carattere)
    
    Returns:
        True se la scrittura è riuscita
    """
    if not _computer_use_abilitato:
        logger.warning("⚠️ Computer Use disabilitato!")
        return False
    
    pyautogui = _importa_pyautogui()
    if not pyautogui:
        return False
    
    try:
        import pyperclip
        logger.info(f"⌨️ Scrivo (clipboard): '{testo[:50]}{'...' if len(testo) > 50 else ''}'")
        pyperclip.copy(testo)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(0.1)
        return True
    except pyautogui.FailSafeException:
        logger.critical("🛑 FAILSAFE ATTIVATO!")
        abilita_computer_use(False)
        return False
    except Exception as e:
        logger.error(f"❌ Errore scrivi_testo_clipboard: {e}")
        return False


def premi_tasto(tasto: str) -> bool:
    """
    Preme un singolo tasto della tastiera.
    
    Tasti comuni: 'enter', 'tab', 'escape', 'backspace', 'delete',
    'space', 'up', 'down', 'left', 'right', 'home', 'end',
    'pageup', 'pagedown', 'f1'-'f12', 'capslock', 'printscreen'
    
    Args:
        tasto: Il nome del tasto da premere
    
    Returns:
        True se la pressione è riuscita
    """
    if not _computer_use_abilitato:
        logger.warning("⚠️ Computer Use disabilitato!")
        return False
    
    pyautogui = _importa_pyautogui()
    if not pyautogui:
        return False
    
    try:
        logger.info(f"⌨️ Premo tasto: {tasto}")
        pyautogui.press(tasto)
        return True
    except pyautogui.FailSafeException:
        logger.critical("🛑 FAILSAFE ATTIVATO!")
        abilita_computer_use(False)
        return False
    except Exception as e:
        logger.error(f"❌ Errore premi_tasto: {e}")
        return False


def combinazione_tasti(*tasti: str) -> bool:
    """
    Preme una combinazione di tasti (es. Ctrl+C, Alt+Tab).
    
    Esempi:
        combinazione_tasti('ctrl', 'c')       # Copia
        combinazione_tasti('ctrl', 'v')       # Incolla
        combinazione_tasti('alt', 'tab')      # Cambia finestra
        combinazione_tasti('ctrl', 'shift', 's')  # Salva con nome
        combinazione_tasti('win', 'e')        # Apri Esplora File
    
    Args:
        *tasti: I tasti da premere contemporaneamente
    
    Returns:
        True se la combinazione è riuscita
    """
    if not _computer_use_abilitato:
        logger.warning("⚠️ Computer Use disabilitato!")
        return False
    
    pyautogui = _importa_pyautogui()
    if not pyautogui:
        return False
    
    try:
        combo = "+".join(tasti)
        logger.info(f"⌨️ Combinazione tasti: {combo}")
        pyautogui.hotkey(*tasti)
        return True
    except pyautogui.FailSafeException:
        logger.critical("🛑 FAILSAFE ATTIVATO!")
        abilita_computer_use(False)
        return False
    except Exception as e:
        logger.error(f"❌ Errore combinazione_tasti: {e}")
        return False


def tieni_premuto(tasto: str, durata: float = 0.5) -> bool:
    """
    Tiene premuto un tasto per una durata specificata.
    
    Args:
        tasto: Il tasto da tenere premuto
        durata: Per quanto tempo (secondi)
    
    Returns:
        True se riuscito
    """
    if not _computer_use_abilitato:
        logger.warning("⚠️ Computer Use disabilitato!")
        return False
    
    pyautogui = _importa_pyautogui()
    if not pyautogui:
        return False
    
    try:
        logger.info(f"⌨️ Tieni premuto '{tasto}' per {durata}s")
        pyautogui.keyDown(tasto)
        time.sleep(durata)
        pyautogui.keyUp(tasto)
        return True
    except pyautogui.FailSafeException:
        logger.critical("🛑 FAILSAFE ATTIVATO!")
        abilita_computer_use(False)
        return False
    except Exception as e:
        logger.error(f"❌ Errore tieni_premuto: {e}")
        return False


# ============================================
# FUNZIONI SCHERMO
# ============================================

def screenshot(percorso: Optional[str] = None) -> Optional[str]:
    """
    Cattura uno screenshot dello schermo.
    
    Args:
        percorso: Percorso dove salvare l'immagine (None = temp)
    
    Returns:
        Percorso del file screenshot, o None se fallito
    """
    if not _computer_use_abilitato:
        logger.warning("⚠️ Computer Use disabilitato!")
        return None
    
    pyautogui = _importa_pyautogui()
    if not pyautogui:
        return None
    
    try:
        import tempfile
        import os
        
        if percorso is None:
            # Salva in una directory temporanea
            temp_dir = tempfile.gettempdir()
            percorso = os.path.join(
                temp_dir, 
                f"autobot_screenshot_{int(time.time())}.png"
            )
        
        logger.info(f"📸 Screenshot salvato in: {percorso}")
        img = pyautogui.screenshot()
        img.save(percorso)
        return percorso
    except Exception as e:
        logger.error(f"❌ Errore screenshot: {e}")
        return None


def posizione_mouse() -> Tuple[int, int]:
    """
    Restituisce la posizione corrente del mouse.
    
    Returns:
        Tupla (x, y) con le coordinate del mouse
    """
    pyautogui = _importa_pyautogui()
    if not pyautogui:
        return (0, 0)
    
    pos = pyautogui.position()
    logger.debug(f"🖱️ Posizione mouse: ({pos.x}, {pos.y})")
    return (pos.x, pos.y)


def dimensione_schermo() -> Tuple[int, int]:
    """
    Restituisce la dimensione dello schermo in pixel.
    
    Returns:
        Tupla (larghezza, altezza)
    """
    pyautogui = _importa_pyautogui()
    if not pyautogui:
        return (0, 0)
    
    size = pyautogui.size()
    logger.debug(f"🖥️ Dimensione schermo: {size.width}x{size.height}")
    return (size.width, size.height)


def trova_immagine(
    percorso_immagine: str, 
    confidenza: float = 0.8
) -> Optional[Tuple[int, int]]:
    """
    Cerca un'immagine sullo schermo e restituisce le coordinate del centro.
    Utile per trovare pulsanti, icone, ecc.
    
    Args:
        percorso_immagine: Percorso dell'immagine da cercare
        confidenza: Livello di confidenza (0.0-1.0, default 0.8)
    
    Returns:
        Tupla (x, y) del centro dell'immagine trovata, o None
    """
    if not _computer_use_abilitato:
        logger.warning("⚠️ Computer Use disabilitato!")
        return None
    
    pyautogui = _importa_pyautogui()
    if not pyautogui:
        return None
    
    try:
        logger.info(f"🔍 Cerco immagine: {percorso_immagine}")
        # confidence richiede opencv-python
        try:
            posizione = pyautogui.locateCenterOnScreen(
                percorso_immagine, confidence=confidenza
            )
        except TypeError:
            # Se opencv non è installato, prova senza confidence
            posizione = pyautogui.locateCenterOnScreen(percorso_immagine)
        
        if posizione:
            logger.info(f"✅ Immagine trovata a ({posizione.x}, {posizione.y})")
            return (posizione.x, posizione.y)
        else:
            logger.info("❌ Immagine non trovata sullo schermo")
            return None
    except Exception as e:
        logger.error(f"❌ Errore trova_immagine: {e}")
        return None


# ============================================
# FUNZIONI FINESTRE
# ============================================

def lista_finestre() -> List[str]:
    """
    Restituisce la lista dei titoli delle finestre aperte.
    
    Returns:
        Lista di stringhe con i titoli delle finestre
    """
    try:
        import pygetwindow as gw
        finestre = [w.title for w in gw.getAllWindows() if w.title.strip()]
        logger.info(f"📋 {len(finestre)} finestre trovate")
        return finestre
    except ImportError:
        logger.error("❌ pygetwindow non disponibile")
        return []
    except Exception as e:
        logger.error(f"❌ Errore lista_finestre: {e}")
        return []


def attiva_finestra(titolo: str) -> bool:
    """
    Porta in primo piano una finestra dato il suo titolo (o parte di esso).
    
    Args:
        titolo: Titolo della finestra (anche parziale)
    
    Returns:
        True se la finestra è stata attivata
    """
    if not _computer_use_abilitato:
        logger.warning("⚠️ Computer Use disabilitato!")
        return False
    
    try:
        import pygetwindow as gw
        
        # Cerca finestre che contengono il titolo
        finestre = gw.getWindowsWithTitle(titolo)
        if finestre:
            finestra = finestre[0]
            logger.info(f"🪟 Attivo finestra: '{finestra.title}'")
            finestra.activate()
            time.sleep(0.3)
            return True
        else:
            logger.warning(f"⚠️ Finestra '{titolo}' non trovata")
            return False
    except ImportError:
        logger.error("❌ pygetwindow non disponibile")
        return False
    except Exception as e:
        logger.error(f"❌ Errore attiva_finestra: {e}")
        return False


# ============================================
# FUNZIONI UTILITY
# ============================================

def attendi(secondi: float) -> None:
    """
    Attende un numero di secondi prima di continuare.
    Utile per aspettare che un programma si carichi.
    
    Args:
        secondi: Tempo di attesa in secondi
    """
    logger.info(f"⏳ Attendo {secondi} secondi...")
    time.sleep(secondi)


def ottieni_info_sistema() -> dict:
    """
    Restituisce informazioni sul sistema per aiutare l'IA
    a capire l'ambiente in cui opera.
    
    Returns:
        Dizionario con info sistema
    """
    info = {}
    
    pyautogui = _importa_pyautogui()
    if pyautogui:
        size = pyautogui.size()
        pos = pyautogui.position()
        info["schermo_larghezza"] = size.width
        info["schermo_altezza"] = size.height
        info["mouse_x"] = pos.x
        info["mouse_y"] = pos.y
    
    info["computer_use_abilitato"] = _computer_use_abilitato
    info["pausa_sicurezza"] = _pausa_sicurezza
    
    # Info finestre
    try:
        import pygetwindow as gw
        finestre = [w.title for w in gw.getAllWindows() if w.title.strip()]
        info["finestre_aperte"] = finestre[:10]  # Max 10 per non esagerare
    except Exception:
        info["finestre_aperte"] = []
    
    logger.debug(f"ℹ️ Info sistema: {info}")
    return info


logger.info("🖱️ Modulo Computer Use caricato")

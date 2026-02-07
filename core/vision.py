# ============================================
# Vision - AutoBot Ox
# Modulo per catturare screenshot e inviarli al
# modello LLM come immagini base64.
#
# COME FUNZIONA (spiegazione per principianti):
# 1. Cattura uno screenshot dello schermo
# 2. Lo ridimensiona per non usare troppi token
# 3. Lo codifica in base64 (formato testo)
# 4. Lo inietta nel messaggio che va al modello LLM
# 5. Il modello "vede" lo screenshot e può agire
#
# NOTA: Serve un modello con capacità vision!
# Modelli compatibili: GPT-4o, Claude 3, Gemini Pro, ecc.
# I modelli solo-testo ignoreranno l'immagine.
# ============================================

import logging
import base64
import io
from typing import Optional, Tuple

# Logger per questo modulo
logger = logging.getLogger("AutoBotOx.Vision")

# Flag globale per abilitare/disabilitare la vision
_vision_abilitata = False

# Screenshot pendente da inviare al modello (base64)
_screenshot_pendente: Optional[str] = None

# Dimensione massima dello screenshot (pixel) per ridurre i token
# 1280x720 è un buon compromesso tra qualità e dimensione
MAX_LARGHEZZA = 1280
MAX_ALTEZZA = 720

# Qualità JPEG (0-100) - più bassa = meno token ma meno qualità
QUALITA_JPEG = 60


def abilita_vision(abilitata: bool = True) -> None:
    """
    Abilita o disabilita l'invio automatico di screenshot al modello.
    
    Args:
        abilitata: True per abilitare, False per disabilitare
    """
    global _vision_abilitata
    _vision_abilitata = abilitata
    stato = "ABILITATA ✅" if abilitata else "DISABILITATA ❌"
    logger.info(f"👁️ Vision: {stato}")


def is_vision_abilitata() -> bool:
    """Controlla se la vision è abilitata."""
    return _vision_abilitata


def cattura_screenshot() -> Optional[str]:
    """
    Cattura uno screenshot dello schermo e lo ritorna come stringa base64.
    
    Lo screenshot viene ridimensionato e compresso in JPEG per
    ridurre il numero di token consumati dal modello vision.
    
    Returns:
        Stringa base64 dello screenshot, o None se errore
    """
    try:
        import pyautogui
        from PIL import Image
        
        # Cattura lo screenshot (oggetto PIL Image)
        logger.debug("📸 Cattura screenshot in corso...")
        img = pyautogui.screenshot()
        
        # Ridimensiona per risparmiare token
        img = _ridimensiona_immagine(img, MAX_LARGHEZZA, MAX_ALTEZZA)
        
        # Converti in JPEG base64 (JPEG è molto più leggero di PNG)
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=QUALITA_JPEG, optimize=True)
        buffer.seek(0)
        
        # Codifica in base64
        img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        
        dimensione_kb = len(img_base64) / 1024
        logger.info(f"📸 Screenshot catturato: {img.width}x{img.height}, {dimensione_kb:.0f}KB base64")
        
        return img_base64
        
    except ImportError as e:
        logger.error(f"❌ Librerie mancanti per screenshot: {e}")
        logger.error("   Installa con: pip install pyautogui Pillow")
        return None
    except Exception as e:
        logger.error(f"❌ Errore cattura screenshot: {e}")
        return None


def imposta_screenshot_pendente(base64_img: Optional[str] = None) -> None:
    """
    Imposta uno screenshot da inviare con il prossimo messaggio.
    
    Se base64_img è None, cattura automaticamente uno screenshot.
    
    Args:
        base64_img: Screenshot in base64, o None per cattura automatica
    """
    global _screenshot_pendente
    
    if base64_img is None:
        _screenshot_pendente = cattura_screenshot()
    else:
        _screenshot_pendente = base64_img
    
    if _screenshot_pendente:
        logger.debug("📸 Screenshot pendente impostato")
    else:
        logger.warning("⚠️ Nessuno screenshot disponibile")


def preleva_screenshot_pendente() -> Optional[str]:
    """
    Preleva lo screenshot pendente e lo rimuove dalla coda.
    
    Returns:
        Stringa base64 dello screenshot, o None se non presente
    """
    global _screenshot_pendente
    screenshot = _screenshot_pendente
    _screenshot_pendente = None
    return screenshot


def _ridimensiona_immagine(img, max_w: int, max_h: int):
    """
    Ridimensiona l'immagine mantenendo le proporzioni.
    
    Args:
        img: Oggetto PIL Image
        max_w: Larghezza massima
        max_h: Altezza massima
    
    Returns:
        Immagine ridimensionata (PIL Image)
    """
    w, h = img.size
    
    # Se già entro i limiti, non ridimensionare
    if w <= max_w and h <= max_h:
        return img
    
    # Calcola il rapporto di ridimensionamento
    rapporto = min(max_w / w, max_h / h)
    nuovo_w = int(w * rapporto)
    nuovo_h = int(h * rapporto)
    
    logger.debug(f"📐 Ridimensionamento: {w}x{h} → {nuovo_w}x{nuovo_h}")
    
    # Usa LANCZOS per la migliore qualità
    from PIL import Image
    return img.resize((nuovo_w, nuovo_h), Image.LANCZOS)

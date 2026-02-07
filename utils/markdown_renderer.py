# ============================================
# Markdown Renderer - AutoBot Ox
# Converte testo markdown in widget tkinter.Text
# con formattazione rich (grassetto, corsivo, headers, ecc.)
#
# COME FUNZIONA (spiegazione per principianti):
# 1. Riceve una stringa con markdown (es. **grassetto**, *corsivo*)
# 2. Analizza il testo riga per riga
# 3. Inserisce il testo in un widget tkinter.Text con "tag" colorati
# 4. I tag applicano font diversi (bold, italic, dimensioni)
#
# PATTERN SUPPORTATI:
# - **testo** → Grassetto
# - *testo* → Corsivo  
# - # Titolo → Header grande
# - ## Sottotitolo → Header medio
# - ### Sotto-sottotitolo → Header piccolo
# - - elemento → Lista puntata (•)
# - `codice` → Codice inline (sfondo scuro)
# - ```blocco``` → Blocco codice (sfondo scuro)
# ============================================

import re
import logging
import tkinter as tk
from typing import List, Tuple

# Logger per questo modulo
logger = logging.getLogger("AutoBotOx.MarkdownRenderer")


def configura_tag_markdown(widget_text: tk.Text, colore_testo: str = "#e0e0e0",
                           font_famiglia: str = "Segoe UI", font_size: int = 13) -> None:
    """
    Configura i tag di formattazione su un widget tkinter.Text.
    Deve essere chiamato PRIMA di inserire testo markdown.
    
    Args:
        widget_text: Il widget tkinter.Text su cui configurare i tag
        colore_testo: Colore del testo normale
        font_famiglia: Font famiglia base
        font_size: Dimensione font base
    """
    # Tag per testo normale
    widget_text.tag_configure("normale", 
                              font=(font_famiglia, font_size),
                              foreground=colore_testo)
    
    # Tag per grassetto (**testo**)
    widget_text.tag_configure("grassetto",
                              font=(font_famiglia, font_size, "bold"),
                              foreground=colore_testo)
    
    # Tag per corsivo (*testo*)
    widget_text.tag_configure("corsivo",
                              font=(font_famiglia, font_size, "italic"),
                              foreground=colore_testo)
    
    # Tag per grassetto+corsivo (***testo***)
    widget_text.tag_configure("grassetto_corsivo",
                              font=(font_famiglia, font_size, "bold italic"),
                              foreground=colore_testo)
    
    # Tag per header # (grande)
    widget_text.tag_configure("h1",
                              font=(font_famiglia, font_size + 6, "bold"),
                              foreground=colore_testo,
                              spacing1=8, spacing3=4)
    
    # Tag per header ## (medio)
    widget_text.tag_configure("h2",
                              font=(font_famiglia, font_size + 3, "bold"),
                              foreground=colore_testo,
                              spacing1=6, spacing3=3)
    
    # Tag per header ### (piccolo)
    widget_text.tag_configure("h3",
                              font=(font_famiglia, font_size + 1, "bold"),
                              foreground=colore_testo,
                              spacing1=4, spacing3=2)
    
    # Tag per codice inline (`codice`)
    widget_text.tag_configure("codice_inline",
                              font=("Consolas", font_size - 1),
                              foreground="#80cbc4",
                              background="#1a1a2e")
    
    # Tag per blocco codice (```codice```)
    widget_text.tag_configure("codice_blocco",
                              font=("Consolas", font_size - 1),
                              foreground="#80cbc4",
                              background="#1a1a2e",
                              lmargin1=10, lmargin2=10,
                              rmargin=10,
                              spacing1=4, spacing3=4)
    
    # Tag per lista puntata (- elemento)
    widget_text.tag_configure("lista",
                              font=(font_famiglia, font_size),
                              foreground=colore_testo,
                              lmargin1=20, lmargin2=30)

    logger.debug("🎨 Tag markdown configurati sul widget Text")


def inserisci_markdown(widget_text: tk.Text, testo: str) -> None:
    """
    Inserisce testo con formattazione markdown in un widget tkinter.Text.
    I tag devono essere già configurati con configura_tag_markdown().
    
    Args:
        widget_text: Il widget tkinter.Text dove inserire
        testo: Il testo markdown da formattare e inserire
    """
    if not testo:
        return
    
    righe = testo.split("\n")
    in_blocco_codice = False
    
    for i, riga in enumerate(righe):
        # Gestione blocchi codice ```
        if riga.strip().startswith("```"):
            in_blocco_codice = not in_blocco_codice
            # Non mostrare la riga ``` stessa
            if i < len(righe) - 1 or in_blocco_codice:
                continue
            else:
                continue
        
        if in_blocco_codice:
            # Dentro un blocco codice: mostra raw con font monospace
            widget_text.insert("end", riga + "\n", "codice_blocco")
            continue
        
        # Header: # ## ###
        if riga.strip().startswith("### "):
            testo_header = riga.strip()[4:]
            widget_text.insert("end", testo_header + "\n", "h3")
            continue
        elif riga.strip().startswith("## "):
            testo_header = riga.strip()[3:]
            widget_text.insert("end", testo_header + "\n", "h2")
            continue
        elif riga.strip().startswith("# "):
            testo_header = riga.strip()[2:]
            widget_text.insert("end", testo_header + "\n", "h1")
            continue
        
        # Lista puntata: - elemento o * elemento
        if riga.strip().startswith("- ") or riga.strip().startswith("* "):
            testo_lista = riga.strip()[2:]
            widget_text.insert("end", "  • ", "lista")
            _inserisci_riga_formattata(widget_text, testo_lista, "lista")
            widget_text.insert("end", "\n")
            continue
        
        # Lista numerata: 1. elemento
        match_num = re.match(r'^\s*(\d+)\.\s+(.*)', riga)
        if match_num:
            numero = match_num.group(1)
            testo_lista = match_num.group(2)
            widget_text.insert("end", f"  {numero}. ", "lista")
            _inserisci_riga_formattata(widget_text, testo_lista, "lista")
            widget_text.insert("end", "\n")
            continue
        
        # Riga normale: applica formattazione inline
        _inserisci_riga_formattata(widget_text, riga, "normale")
        widget_text.insert("end", "\n")


def _inserisci_riga_formattata(widget_text: tk.Text, riga: str, tag_base: str) -> None:
    """
    Inserisce una singola riga con formattazione inline (bold, italic, code).
    
    Analizza il testo per trovare pattern markdown inline:
    - **grassetto**
    - *corsivo*
    - `codice`
    
    Args:
        widget_text: Widget Text dove inserire
        riga: La riga di testo da formattare
        tag_base: Tag base per il testo non formattato
    """
    if not riga:
        return
    
    # Pattern per trovare formattazione inline
    # Ordine importante: prima i pattern più lunghi (*** prima di ** prima di *)
    # Usiamo un approccio a segmenti per gestire l'annidamento
    segmenti = _parsa_inline(riga)
    
    for testo_segmento, formato in segmenti:
        if formato == "grassetto_corsivo":
            widget_text.insert("end", testo_segmento, "grassetto_corsivo")
        elif formato == "grassetto":
            widget_text.insert("end", testo_segmento, "grassetto")
        elif formato == "corsivo":
            widget_text.insert("end", testo_segmento, "corsivo")
        elif formato == "codice":
            widget_text.insert("end", testo_segmento, "codice_inline")
        else:
            widget_text.insert("end", testo_segmento, tag_base)


def _parsa_inline(testo: str) -> List[Tuple[str, str]]:
    """
    Analizza il testo per trovare formattazione inline markdown.
    Ritorna una lista di (testo, formato) dove formato è:
    - "normale" per testo plain
    - "grassetto" per **testo**
    - "corsivo" per *testo*
    - "grassetto_corsivo" per ***testo***
    - "codice" per `testo`
    
    Args:
        testo: Il testo da analizzare
        
    Returns:
        Lista di tuple (testo, formato)
    """
    segmenti = []
    
    # Regex che cattura i vari pattern inline
    # L'ordine dei gruppi è importante: prima i pattern più specifici
    pattern = re.compile(
        r'(\*\*\*(.+?)\*\*\*)'   # ***grassetto corsivo***
        r'|(\*\*(.+?)\*\*)'       # **grassetto**
        r'|(\*(.+?)\*)'           # *corsivo*
        r'|(`(.+?)`)'             # `codice`
    )
    
    ultimo_indice = 0
    
    for match in pattern.finditer(testo):
        # Testo prima del match (normale)
        if match.start() > ultimo_indice:
            testo_prima = testo[ultimo_indice:match.start()]
            if testo_prima:
                segmenti.append((testo_prima, "normale"))
        
        # Determina quale gruppo ha matchato
        if match.group(2) is not None:
            # ***grassetto corsivo***
            segmenti.append((match.group(2), "grassetto_corsivo"))
        elif match.group(4) is not None:
            # **grassetto**
            segmenti.append((match.group(4), "grassetto"))
        elif match.group(6) is not None:
            # *corsivo*
            segmenti.append((match.group(6), "corsivo"))
        elif match.group(8) is not None:
            # `codice`
            segmenti.append((match.group(8), "codice"))
        
        ultimo_indice = match.end()
    
    # Testo dopo l'ultimo match (normale)
    if ultimo_indice < len(testo):
        testo_dopo = testo[ultimo_indice:]
        if testo_dopo:
            segmenti.append((testo_dopo, "normale"))
    
    # Se non ci sono match, tutto il testo è normale
    if not segmenti:
        segmenti.append((testo, "normale"))
    
    return segmenti


def pulisci_markdown(testo: str) -> str:
    """
    Rimuove i marker markdown da una stringa senza formattare.
    Utile per testi dove non si può usare rich text.
    
    Args:
        testo: Testo con markdown
        
    Returns:
        Testo pulito senza marker markdown
    """
    # Rimuovi headers
    testo = re.sub(r'^#{1,3}\s+', '', testo, flags=re.MULTILINE)
    # Rimuovi bold/italic
    testo = re.sub(r'\*\*\*(.+?)\*\*\*', r'\1', testo)
    testo = re.sub(r'\*\*(.+?)\*\*', r'\1', testo)
    testo = re.sub(r'\*(.+?)\*', r'\1', testo)
    # Rimuovi code inline
    testo = re.sub(r'`(.+?)`', r'\1', testo)
    # Rimuovi code blocks
    testo = re.sub(r'```\w*\n?', '', testo)
    return testo

# ✅ TODO LIST - AutoBot Ox

## Legenda
- ✅ Completato
- 🔄 In corso
- ⏳ Da fare
- 🔴 Priorità alta
- 🟡 Priorità media
- 🟢 Priorità bassa

---

## Fase 1: Struttura Base ✅
- ✅ Creare struttura cartelle modulare
- ✅ Creare file __init__.py per ogni modulo
- ✅ Creare requirements.txt con tutte le dipendenze
- ✅ Creare .gitignore
- ✅ Creare ARCHITETTURA.md
- ✅ Creare questo file TODO_LIST.md

## Fase 2: Configurazione ✅
- ✅ Creare default_config.json con tutte le impostazioni
- ✅ Creare settings.py (GestoreImpostazioni) con carica/salva/merge
- ✅ Supporto due file: default (read-only) + utente (read-write)

## Fase 3: Moduli Core ✅
- ✅ logger.py - Sistema di logging (console + file)
- ✅ health_check.py - Heartbeat server locale ogni 5 secondi
- ✅ provider_manager.py - Gestione provider LLM (locale/cloud)
- ✅ interpreter_wrapper.py - Wrapper Open Interpreter con threading
- ✅ token_counter.py - Contatore token per OpenRouter
- ✅ history_export.py - Esportazione cronologia (TXT/MD)

## Fase 4: GUI ✅
- ✅ sidebar.py - Pannello impostazioni laterale
- ✅ chat_view.py - Interfaccia chat con bolle messaggi
- ✅ terminal_view.py - Vista terminale stile hacker
- ✅ status_bar.py - Barra stato con info real-time
- ✅ dialogs.py - Popup errori, conferme, debug, approvazione codice
- ✅ app.py - Finestra principale (assembla tutto)

## Fase 5: Entry Point & Build ✅
- ✅ main.py - Punto di ingresso con verifica dipendenze
- ✅ build.py - Script PyInstaller per EXE portable

## Fase 6: Documentazione ✅
- ✅ README.md
- ✅ ARCHITETTURA.md
- ✅ TODO_LIST.md
- ✅ Commenti dettagliati in tutti i file

## Fase 7: Test & Deploy ✅
- ✅ Test build applicazione (GUI avviata con successo)
- ✅ Push su GitHub (https://github.com/Oxer33/AutoBot-Ox)
- ✅ Fix compatibilità open-interpreter v0.1.11 (import, proprietà, chunk format)
- ✅ Fix duplicazione system_message su riconfigura
- ✅ Fix formato messaggi cronologia/export per v0.1.x
- ✅ Pulizia import inutilizzati
- ✅ Test con LLM locale (LM Studio porta 1234) - funzionante!
- ⏳ Test con DeepSeek R1 via OpenRouter (richiede test utente)

## Fase 8: Fix LLM & Computer Use ✅
- ✅ Fix connessione locale: api_key dummy "not-needed" per litellm
- ✅ Fix connessione OpenRouter: prefisso `openrouter/` per litellm
- ✅ Fix interpreter_wrapper: local=False esplicito per cloud
- ✅ Fix context window warning litellm (max_tokens)
- ✅ Computer Use: modulo core/computer_use.py con pyautogui
- ✅ Computer Use: toggle nella sidebar GUI
- ✅ Computer Use: istruzioni nel system_message per l'IA
- ✅ Computer Use: FAILSAFE (mouse angolo alto-sinistra)
- ✅ Aggiornato requirements.txt, main.py, default_config.json
- ✅ Aggiornato ARCHITETTURA.md con note tecniche

## Fase 9: Fix Computer Use + Vision + Chat ✅
- ✅ Fix computer_use nel subprocess: flag `_computer_use_abilitato` era False nel processo separato
- ✅ Fix auto-inject `abilita_computer_use(True)` nel import_block del monkey-patch
- ✅ Fix context_window locale: da 4096 a 16384 (evita tokentrim su system_message)
- ✅ Fix system_message troppo lungo: ridotto da ~45 righe a ~12 righe compatte
- ✅ Fix chat flickering: aggiornamento in-place `label_contenuto.configure(text=...)` invece di destroy/recreate
- ✅ Fix scroll ottimizzato: scrolla solo ogni 20 caratteri durante streaming
- ✅ Vision: nuovo modulo `core/vision.py` con cattura screenshot + base64 JPEG
- ✅ Vision: monkey-patch `litellm.completion` per iniettare screenshot nel messaggio utente
- ✅ Vision: auto-cattura screenshot prima di ogni messaggio quando attivo
- ✅ Vision: toggle nella sidebar + callback in app.py
- ✅ Vision: caricamento stato dalle impostazioni all'avvio
- ✅ Aggiunto Pillow a requirements.txt e check dipendenze main.py
- ✅ Aggiornato default_config.json con `vision: false`
- ✅ Aggiornato ARCHITETTURA.md con note tecniche vision e monkey-patch

## Fase 10: Fix Stabilità + Markdown + Error Handling ✅
- ✅ Fix crash AST `preprocess_code`: try-except + fallback a codice raw (TypeError unhashable list)
- ✅ Fix vision graceful fallback: auto-disabilita se modello non supporta immagini + retry senza
- ✅ Fix codice duplicato nel terminale: rimosso invio da `end_of_code`, solo da `executing`
- ✅ Rendering markdown nella chat: `utils/markdown_renderer.py` con `tkinter.Text` + tag
  - Supporta: **grassetto**, *corsivo*, `codice inline`, ```blocchi codice```, # headers, liste
  - Ottimizzazione streaming: testo raw durante streaming, markdown completo alla finalizzazione
- ✅ System message migliorato: forza italiano, path Windows (Chrome/Edge/Notepad), regole computer_use dettagliate, no webbrowser.get()
- ✅ Error handling differenziato: messaggi specifici per vision/api_key/connessione
- ✅ Auto-disabilitazione vision nel catch errori generali `_elabora_messaggio`
- ✅ Build test: 13 file compilati senza errori, app avviata con successo

## Miglioramenti Futuri ⏳
- ⏳ 🟡 Crittografia API key con libreria cryptography
- ⏳ 🟢 Supporto temi personalizzabili
- ⏳ 🟢 Plugin system
- ⏳ 🟢 Auto-aggiornamento
- ⏳ 🟢 Voice input
- ⏳ 🟢 Più provider LLM
- ⏳ 🟢 Terminale con colori multipli (tkinter.Text nativo)
- ⏳ 🟢 Streaming markdown progressivo (rendering parziale durante streaming)

---

*Ultimo aggiornamento: 2026-02-07 22:15*

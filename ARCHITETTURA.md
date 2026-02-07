# 🏗️ ARCHITETTURA - AutoBot Ox v1.0.0

## Descrizione
AutoBot Ox è un'applicazione desktop che funge da interfaccia grafica per **Open Interpreter**, permettendo all'utente di interagire con modelli LLM locali o cloud (DeepSeek R1 via OpenRouter) per automatizzare task sul proprio PC.

## Stack Tecnologico
| Tecnologia | Versione | Utilizzo |
|---|---|---|
| Python | 3.10+ | Linguaggio principale |
| CustomTkinter | 5.2.2 | GUI framework (tema scuro) |
| Open Interpreter | 0.1.11 | Core AI (esecuzione comandi) |
| Requests | 2.32.3 | HTTP per health check |
| psutil | 6.1.1 | Monitoraggio sistema |
| Pillow | 11.1.0 | Gestione immagini (Vision) |
| Tkinter (Text) | built-in | Rich text markdown nella chat |
| PyAutoGUI | 0.9.54 | Controllo mouse e tastiera |
| pyperclip | 1.11.0 | Clipboard per testo Unicode |
| PyInstaller | 6.11.1 | Packaging EXE portable |

## Struttura Cartelle

```
AutoBot Ox/
├── main.py                        # 🚀 Entry point dell'applicazione
├── build.py                       # 🔨 Script per compilare in .EXE
├── requirements.txt               # 📦 Dipendenze Python
├── README.md                      # 📖 Documentazione utente
├── ARCHITETTURA.md                # 🏗️ Questo file
├── TODO_LIST.md                   # ✅ Lista cose da fare
├── .gitignore                     # 🙈 File ignorati da Git
│
├── config/                        # ⚙️ MODULO CONFIGURAZIONE
│   ├── __init__.py                #    Inizializzazione modulo
│   ├── settings.py                #    Gestore impostazioni (carica/salva JSON)
│   └── default_config.json        #    Configurazione predefinita
│
├── core/                          # 🧠 MODULO CORE (logica principale)
│   ├── __init__.py                #    Inizializzazione modulo
│   ├── interpreter_wrapper.py     #    Wrapper Open Interpreter con threading
│   ├── provider_manager.py        #    Gestione provider LLM (locale/cloud)
│   ├── health_check.py            #    Heartbeat server locale (porta 1234)
│   ├── computer_use.py            #    Controllo mouse/tastiera (pyautogui)
│   └── vision.py                 #    Cattura screenshot + invio a modelli vision
│
├── gui/                           # 🖥️ MODULO INTERFACCIA GRAFICA
│   ├── __init__.py                #    Inizializzazione modulo
│   ├── app.py                     #    Finestra principale (assembla tutto)
│   ├── sidebar.py                 #    Pannello laterale (impostazioni)
│   ├── chat_view.py               #    Vista chat (messaggi utente/IA)
│   ├── terminal_view.py           #    Vista terminale (codice + output)
│   ├── status_bar.py              #    Barra di stato (info in tempo reale)
│   └── dialogs.py                 #    Finestre popup (errori, conferme)
│
├── utils/                         # 🔧 MODULO UTILITÀ
│   ├── __init__.py                #    Inizializzazione modulo
│   ├── logger.py                  #    Sistema di logging (console + file)
│   ├── token_counter.py           #    Contatore token per OpenRouter
│   ├── history_export.py          #    Esportazione cronologia (TXT/MD)
│   └── markdown_renderer.py       #    Rendering markdown → rich text (tkinter.Text)
│
├── logs/                          # 📝 File di log (auto-generati)
├── output/                        # 📦 EXE compilato (dopo build)
└── DA CANCELLARE/                 # 🗑️ Codice morto / file inutili
```

## Diagramma Flusso Dati

```
┌─────────────────────────────────────────────────────────────┐
│                      GUI (CustomTkinter)                     │
│  ┌──────────┬───────────────────┬─────────────────────────┐ │
│  │ Sidebar  │    Chat View      │    Terminal View         │ │
│  │          │                   │                         │ │
│  │ Provider │ Utente ──► Input  │ Codice ──► Output       │ │
│  │ API Key  │     ▲       │     │     ▲        │          │ │
│  │ AutoRun  │     │       │     │     │        │          │ │
│  │ Cartella │     │       ▼     │     │        ▼          │ │
│  └──────────┘     │   Queue     │     │   Console         │ │
│                   └───────┬─────┘     └────────┘          │ │
│                           │                               │ │
│  ┌────────────────────────┴──────────────────────────────┐│ │
│  │                    Status Bar                          ││ │
│  │  [Server: ●] [Modello: DeepSeek] [Token: 0] [RAM: %] ││ │
│  └────────────────────────────────────────────────────────┘│ │
└──────────────────────────┬──────────────────────────────────┘
                           │ Polling ogni 100ms
                           ▼
┌──────────────────────────────────────────────────────────────┐
│                   CORE (Thread Separato)                      │
│  ┌──────────────────┐  ┌──────────────────┐                  │
│  │ InterpreterWrapper│  │ ProviderManager  │                  │
│  │                  │  │                  │                  │
│  │ • chat()         │  │ • Locale (1234)  │                  │
│  │ • streaming      │  │ • Cloud (OpenR.) │                  │
│  │ • emergency_stop │  │ • switch()       │                  │
│  │ • approvazione   │  └──────────────────┘                  │
│  └──────────┬───────┘                                        │
│             │              ┌──────────────────┐              │
│             │              │  HealthCheck      │              │
│             ▼              │  (Thread daemon)  │              │
│        Open Interpreter    │  • ping ogni 5s   │              │
│        interpreter.chat()  │  • callback stato │              │
│                            └──────────────────┘              │
└──────────────────────────────────────────────────────────────┘
```

## Pattern Architetturali Usati

### 1. **Producer-Consumer con Queue**
- L'interprete (producer) mette messaggi nella coda
- La GUI (consumer) li legge ogni 100ms con polling
- Questo evita race condition tra thread

### 2. **Observer Pattern (Callback)**
- La GUI registra callback sui componenti
- Quando l'utente interagisce, il callback viene chiamato
- Esempio: `callback_cambio_provider(provider)` nella Sidebar

### 3. **Configuration Management**
- Due file: `default_config.json` (mai modificato) e `user_config.json` (personalizzato)
- Merge ricorsivo: le impostazioni utente sovrascrivono quelle default
- API key salvate solo nel file utente (che è gitignored)

## Sicurezza

1. **API Key**: Non hardcodata, salvata nel file utente locale (gitignored)
2. **Auto-Run**: Disattivato di default. NOTA: In open-interpreter v0.1.x con `display=False`, il flag `auto_run` dell'interprete NON ha effetto. L'approvazione è gestita nel nostro `WrapperInterpreter` intercettando il chunk `{"executing": ...}` e bloccando il thread finché l'utente non risponde dalla GUI. Se rifiutato, il generatore viene interrotto (GeneratorExit) e il codice non viene eseguito.
3. **System Message**: Include regole di sicurezza per impedire azioni distruttive. Viene aggiunto una sola volta (marcatore anti-duplicazione).
4. **Emergency Stop**: Pulsante per interrompere immediatamente qualsiasi operazione
5. **Cartella di Lavoro**: L'IA opera solo nella cartella specificata dall'utente
6. **Computer Use**: Disattivato di default. Toggle nella sidebar. FAILSAFE: muovere il mouse nell'angolo in alto a sinistra interrompe tutto. Ogni azione viene loggata.
7. **Vision**: Disattivato di default. Quando attivo, cattura uno screenshot prima di ogni messaggio e lo invia al modello come immagine base64. Serve un modello con capacità vision.

## Componenti Completati ✅
- [x] Struttura modulare del progetto
- [x] Sistema di configurazione (settings.py + JSON)
- [x] Health check server locale con heartbeat
- [x] Provider manager (locale + cloud)
- [x] Interpreter wrapper con threading e coda messaggi
- [x] GUI completa con CustomTkinter (dark mode)
- [x] Sidebar con tutti i controlli
- [x] Chat view con bolle messaggi e streaming
- [x] Terminal view stile hacker
- [x] Status bar con info real-time
- [x] Dialoghi (errore, conferma, debug, approvazione codice)
- [x] Sistema di logging (console + file)
- [x] Token counter per OpenRouter
- [x] Export cronologia (TXT/MD)
- [x] Script build per EXE portable
- [x] Computer Use: controllo mouse/tastiera via pyautogui
- [x] Fix connessione LLM: api_key dummy per locale, prefisso openrouter/ per cloud
- [x] Fix context window warning litellm
- [x] Vision: cattura screenshot + invio a modelli vision (core/vision.py)
- [x] Fix computer_use nel subprocess: auto-abilita flag + auto-inject import
- [x] Fix chat flickering: aggiornamento in-place label durante streaming
- [x] Monkey-patch litellm.completion per vision multimodale
- [x] Fix crash AST preprocess_code: try-except + fallback a codice raw
- [x] Fix vision graceful fallback: auto-disabilita + retry senza immagini
- [x] Fix codice duplicato terminale: invio solo da chunk 'executing'
- [x] Rendering markdown nella chat: bold, italic, headers, liste, codice
- [x] System message migliorato: italiano, path Windows, regole computer_use
- [x] Error handling specifico: vision/api_key/connessione con messaggi chiari
- [x] Nuovo modulo utils/markdown_renderer.py per rich text

## Note Tecniche Importanti

### Connessione LLM
- **Locale**: litellm richiede SEMPRE una api_key, anche per server locali. Usiamo `"not-needed"` come dummy.
- **OpenRouter**: Il modello deve avere il prefisso `openrouter/` (es. `openrouter/deepseek/deepseek-r1-0528:free`). NON impostare `api_base` quando si usa questo prefisso - litellm gestisce il routing internamente.
- **Switch locale↔cloud**: Impostare esplicitamente `local=False` quando si passa a cloud, altrimenti il flag resta `True`.

### Computer Use (core/computer_use.py)
- Usa `pyautogui` per mouse/tastiera e `pyperclip` per clipboard
- Ogni funzione controlla il flag `_computer_use_abilitato` prima di agire
- FAILSAFE di pyautogui: mouse nell'angolo in alto a sinistra = stop totale
- **Monkey-patch preprocess_code**: Auto-inject import + `abilita_computer_use(True)` nel subprocess
- Il codice gira in un subprocess separato, quindi il flag va abilitato anche lì

### Vision (core/vision.py)
- Cattura screenshot con `pyautogui.screenshot()`, ridimensiona con `Pillow`, codifica in base64 JPEG
- **Monkey-patch litellm.completion**: Inietta lo screenshot nell'ultimo messaggio utente in formato multimodale
- Lo screenshot viene catturato PRIMA di inviare il messaggio e iniettato DOPO tokentrim
- Formato multimodale: `{"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}}`
- Serve un modello con capacità vision (GPT-4o, Claude 3, Gemini Pro, ecc.)
- **Graceful fallback**: Se il modello non supporta immagini, la vision viene disabilitata automaticamente e il messaggio viene reinviato senza immagini

### Markdown Renderer (utils/markdown_renderer.py)
- Converte testo markdown in rich text all'interno di widget `tkinter.Text` con tag
- Pattern supportati: **grassetto**, *corsivo*, ***grassetto corsivo***, `codice inline`, ```blocchi codice```, # headers (h1/h2/h3), liste puntate (- •), liste numerate
- Usato nella chat per formattare le risposte dell'IA
- Durante lo streaming: testo raw appeso per performance; alla finalizzazione: re-rendering completo con markdown

### Error Handling
- Messaggi di errore differenziati in base al tipo: vision, api_key, connessione, generico
- Auto-disabilitazione vision se il modello non supporta immagini
- Fallback AST nel preprocess_code: se `ast.unparse()` crasha, il codice viene passato raw

## Componenti Futuri / Miglioramenti Possibili
- [ ] Crittografia API key con libreria cryptography
- [ ] Supporto temi personalizzabili
- [ ] Plugin system per estensioni
- [ ] Auto-aggiornamento dell'applicazione
- [ ] Supporto multi-lingua
- [ ] Integrazione con più provider LLM (Anthropic, OpenAI, ecc.)
- [ ] Voice input (microfono)
- [ ] Terminale con colori multipli (tkinter.Text nativo invece di CTkTextbox)
- [ ] Streaming markdown progressivo (rendering parziale durante lo streaming)

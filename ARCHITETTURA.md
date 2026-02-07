# 🏗️ ARCHITETTURA - AutoBot Ox v1.0.0

## Descrizione
AutoBot Ox è un'applicazione desktop che funge da interfaccia grafica per **Open Interpreter**, permettendo all'utente di interagire con modelli LLM locali o cloud (DeepSeek R1 via OpenRouter) per automatizzare task sul proprio PC.

## Stack Tecnologico
| Tecnologia | Versione | Utilizzo |
|---|---|---|
| Python | 3.10+ | Linguaggio principale |
| CustomTkinter | 5.2.2 | GUI framework (tema scuro) |
| Open Interpreter | 0.4.3 | Core AI (esecuzione comandi) |
| Requests | 2.32.3 | HTTP per health check |
| psutil | 6.1.1 | Monitoraggio sistema |
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
│   └── health_check.py            #    Heartbeat server locale (porta 1234)
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
│   └── history_export.py          #    Esportazione cronologia (TXT/MD)
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
2. **Auto-Run**: Disattivato di default, richiede conferma per ogni esecuzione
3. **System Message**: Include regole di sicurezza per impedire azioni distruttive
4. **Emergency Stop**: Pulsante per interrompere immediatamente qualsiasi operazione
5. **Cartella di Lavoro**: L'IA opera solo nella cartella specificata dall'utente

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

## Componenti Futuri / Miglioramenti Possibili
- [ ] Crittografia API key con libreria cryptography
- [ ] Supporto temi personalizzabili
- [ ] Plugin system per estensioni
- [ ] Auto-aggiornamento dell'applicazione
- [ ] Supporto multi-lingua
- [ ] Integrazione con più provider LLM (Anthropic, OpenAI, ecc.)
- [ ] Voice input (microfono)
- [ ] Screenshot e OCR per OS mode

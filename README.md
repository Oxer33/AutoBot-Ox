# 🤖 AutoBot Ox - AI Agent Desktop

> Un'applicazione desktop che ti permette di controllare il tuo PC usando l'intelligenza artificiale, in modo sicuro e controllato.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-green)
![Open Interpreter](https://img.shields.io/badge/Core-Open%20Interpreter-orange)

## 📖 Cos'è AutoBot Ox?

AutoBot Ox è un'interfaccia grafica per [Open Interpreter](https://github.com/openinterpreter/open-interpreter) che ti permette di:

- 🗣️ **Chattare con l'IA** per eseguire comandi sul tuo PC
- 🔄 **Scegliere tra LLM locale e cloud** (LM Studio o DeepSeek R1 via OpenRouter)
- 🛡️ **Controllare la sicurezza** con approvazione del codice prima dell'esecuzione
- 🖥️ **Vedere in tempo reale** il codice generato e l'output del terminale
- 📊 **Monitorare l'utilizzo** dei token e della memoria RAM

## 🚀 Come Avviare

### Prerequisiti
- Python 3.10 o superiore
- (Opzionale) LM Studio o Ollama per il modello locale sulla porta 1234

### Installazione

```bash
# 1. Clona il repository
git clone https://github.com/tuousername/AutoBot-Ox.git
cd AutoBot-Ox

# 2. Crea un ambiente virtuale (consigliato)
python -m venv venv
venv\Scripts\activate    # Windows

# 3. Installa le dipendenze
pip install -r requirements.txt

# 4. Avvia l'applicazione
python main.py
```

### Primo Avvio

1. **Seleziona un provider LLM** dalla sidebar sinistra:
   - **Locale**: Assicurati che LM Studio o Ollama sia avviato sulla porta 1234
   - **Cloud**: Inserisci la tua API key di OpenRouter

2. **Seleziona la cartella di lavoro**: La cartella dove l'IA avrà i permessi di operare

3. **Inizia a chattare**: Scrivi un messaggio e premi Invio!

## 🏗️ Struttura del Progetto

```
AutoBot Ox/
├── main.py              # Punto di ingresso
├── build.py             # Script per creare l'EXE
├── config/              # Configurazione
├── core/                # Logica principale
├── gui/                 # Interfaccia grafica
└── utils/               # Utilità
```

Per i dettagli completi, vedi [ARCHITETTURA.md](ARCHITETTURA.md).

## 🛡️ Sicurezza

AutoBot Ox è progettato con la sicurezza come priorità:

- **Auto-Run disattivato** di default: ogni codice richiede la tua approvazione
- **Regole di sicurezza** integrate nel prompt di sistema dell'IA
- **Pulsante STOP** di emergenza per interrompere qualsiasi operazione
- **API key** salvata solo localmente (file gitignored)
- **Cartella di lavoro** limitata per impedire accessi non autorizzati

## 📦 Creare l'EXE Portable

```bash
python build.py
```

L'eseguibile verrà creato nella cartella `output/AutoBot_Ox.exe`.

## ⚙️ Configurazione

Le impostazioni sono salvate in `config/default_config.json`.
Le personalizzazioni dell'utente vengono salvate in `config/user_config.json` (auto-generato).

### Provider Supportati

| Provider | Modello | Endpoint |
|---|---|---|
| Locale | Qualsiasi (LM Studio/Ollama) | `http://localhost:1234/v1` |
| Cloud | DeepSeek R1 0528 (free) | `https://openrouter.ai/api/v1` |

## 🤝 Contribuire

Le pull request sono benvenute! Per modifiche importanti, apri prima un issue per discutere le modifiche proposte.

## 📄 Licenza

MIT License - Vedi il file LICENSE per i dettagli.

---

**Fatto con ❤️ in Italia**

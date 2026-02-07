# ============================================
# AutoBot Ox - Entry Point (Punto di Ingresso)
# ============================================
#
# Questo è il file principale che avvia l'applicazione.
# Per avviare AutoBot Ox, esegui: python main.py
#
# Cosa fa questo file:
# 1. Configura il sistema di logging (per tracciare errori e debug)
# 2. Verifica che tutte le dipendenze siano installate
# 3. Avvia la finestra principale dell'applicazione
# ============================================

import sys
import os

# Aggiungi la cartella del progetto al path di Python
# Questo permette di importare i moduli da qualsiasi posizione
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)


def verifica_dipendenze() -> bool:
    """
    Verifica che tutte le librerie necessarie siano installate.
    
    Se una libreria manca, mostra un messaggio chiaro con le istruzioni
    per installarla.
    
    Returns:
        True se tutte le dipendenze sono presenti, False altrimenti
    """
    dipendenze_mancanti = []

    # Lista delle dipendenze da verificare
    # Formato: (nome_import, nome_pip, descrizione)
    dipendenze = [
        ("customtkinter", "customtkinter", "GUI Framework (interfaccia grafica)"),
        ("requests", "requests", "Richieste HTTP (per health check)"),
        ("psutil", "psutil", "Monitoraggio sistema (RAM, CPU)"),
        ("pyautogui", "pyautogui", "Controllo mouse e tastiera (Computer Use)"),
        ("pyperclip", "pyperclip", "Clipboard per testo con caratteri speciali"),
    ]

    for nome_import, nome_pip, descrizione in dipendenze:
        try:
            __import__(nome_import)
        except ImportError:
            dipendenze_mancanti.append((nome_pip, descrizione))

    if dipendenze_mancanti:
        print("\n" + "=" * 60)
        print("  ❌ DIPENDENZE MANCANTI - AutoBot Ox")
        print("=" * 60)
        print("\nLe seguenti librerie devono essere installate:\n")

        for nome, desc in dipendenze_mancanti:
            print(f"  • {nome} - {desc}")

        print(f"\nEsegui questo comando per installarle tutte:")
        print(f"\n  pip install -r requirements.txt")
        print(f"\nOppure installa singolarmente:")
        for nome, desc in dipendenze_mancanti:
            print(f"  pip install {nome}")
        print("\n" + "=" * 60)
        return False

    return True


def verifica_interpreter() -> bool:
    """
    Verifica se Open Interpreter è installato.
    Questo è separato perché è una dipendenza opzionale
    (l'app può avviarsi anche senza, ma non potrà chattare).
    
    Returns:
        True se open-interpreter è disponibile
    """
    try:
        # In open-interpreter v0.1.x, l'import è diretto: import interpreter
        import interpreter
        return True
    except ImportError:
        print("\n⚠️ AVVISO: 'open-interpreter' non è installato!")
        print("   L'app si avvierà ma non potrai chattare con l'IA.")
        print("   Installa con: pip install open-interpreter")
        print()
        return False


def main():
    """
    Funzione principale che avvia AutoBot Ox.
    
    Ordine di esecuzione:
    1. Verifica dipendenze
    2. Configura logging
    3. Avvia la GUI
    """
    print("\n" + "=" * 60)
    print("  🤖 AutoBot Ox - AI Agent Desktop v1.0.0")
    print("  Avvio in corso...")
    print("=" * 60 + "\n")

    # Passo 1: Verifica le dipendenze
    print("🔍 Verifica dipendenze...")
    if not verifica_dipendenze():
        print("\n❌ Impossibile avviare AutoBot Ox. Installa le dipendenze mancanti.")
        input("\nPremi INVIO per chiudere...")
        sys.exit(1)
    print("✅ Tutte le dipendenze sono presenti\n")

    # Passo 1.5: Verifica Open Interpreter (avviso, non blocca)
    interpreter_ok = verifica_interpreter()
    if interpreter_ok:
        print("✅ Open Interpreter disponibile\n")

    # Passo 2: Configura il logging
    print("📝 Configurazione logging...")
    from utils.logger import configura_logging
    logger = configura_logging()
    logger.info("🚀 AutoBot Ox - Avvio applicazione")

    # Passo 3: Avvia la GUI
    print("🖥️ Avvio interfaccia grafica...\n")
    try:
        from gui.app import AppAutoBot

        app = AppAutoBot()
        app.mainloop()

    except Exception as e:
        logger.critical(f"💥 Errore critico: {e}", exc_info=True)
        print(f"\n💥 ERRORE CRITICO: {e}")
        print("\nControlla il file di log nella cartella 'logs/' per i dettagli.")
        input("\nPremi INVIO per chiudere...")
        sys.exit(1)

    logger.info("👋 AutoBot Ox chiuso normalmente")
    print("\n👋 AutoBot Ox chiuso. Arrivederci!")


if __name__ == "__main__":
    main()

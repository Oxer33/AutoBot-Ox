# ============================================
# Script di Build - AutoBot Ox
# Compila l'applicazione in un file .EXE portable
# usando PyInstaller
#
# Uso: python build.py
# ============================================

import os
import sys
import subprocess
import shutil
from pathlib import Path

# Percorso base del progetto
BASE_DIR = Path(__file__).resolve().parent
DIST_DIR = BASE_DIR / "dist"
BUILD_DIR = BASE_DIR / "build"
OUTPUT_DIR = BASE_DIR / "output"


def pulisci_build_precedente():
    """Rimuove i file di build precedenti."""
    print("🧹 Pulizia build precedente...")
    for cartella in [DIST_DIR, BUILD_DIR]:
        if cartella.exists():
            shutil.rmtree(cartella)
            print(f"   Rimossa: {cartella}")


def compila_exe():
    """
    Compila l'applicazione in un file .EXE portable.
    
    Parametri PyInstaller usati:
    - --onefile: Crea un singolo file .exe
    - --windowed: Non mostra la console (è una app GUI)
    - --name: Nome del file eseguibile
    - --icon: Icona dell'applicazione (se disponibile)
    - --add-data: Include file aggiuntivi (configurazione, ecc.)
    """
    print("\n🔨 Compilazione in corso...\n")

    # Comando PyInstaller
    comando = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",                          # Un singolo file .exe
        "--windowed",                         # Nessuna console (app GUI)
        "--name", "AutoBot_Ox",              # Nome dell'eseguibile
        "--clean",                            # Pulisci i file temporanei
        # Include i file di configurazione nell'exe
        "--add-data", f"{BASE_DIR / 'config' / 'default_config.json'};config",
        # File principale
        str(BASE_DIR / "main.py")
    ]

    print(f"📋 Comando: {' '.join(comando)}\n")

    # Esegui PyInstaller
    risultato = subprocess.run(comando, cwd=str(BASE_DIR))

    if risultato.returncode == 0:
        print("\n✅ Compilazione completata con successo!")

        # Sposta l'exe nella cartella output
        OUTPUT_DIR.mkdir(exist_ok=True)
        exe_path = DIST_DIR / "AutoBot_Ox.exe"
        if exe_path.exists():
            dest = OUTPUT_DIR / "AutoBot_Ox.exe"
            shutil.copy2(exe_path, dest)
            print(f"📦 Eseguibile copiato in: {dest}")

            # Copia anche il file di configurazione
            config_dest = OUTPUT_DIR / "config"
            config_dest.mkdir(exist_ok=True)
            shutil.copy2(
                BASE_DIR / "config" / "default_config.json",
                config_dest / "default_config.json"
            )
            print(f"📋 Configurazione copiata in: {config_dest}")

        print(f"\n🎉 L'eseguibile è pronto in: {OUTPUT_DIR}")
        print(f"   Dimensione: {dest.stat().st_size / (1024*1024):.1f} MB")
    else:
        print(f"\n❌ Errore durante la compilazione! Codice: {risultato.returncode}")
        print("   Controlla i messaggi sopra per i dettagli.")

    return risultato.returncode


def main():
    """Funzione principale del build script."""
    print("=" * 60)
    print("  🔨 AutoBot Ox - Build Script")
    print("  Compilazione in EXE portable")
    print("=" * 60)

    # Verifica che PyInstaller sia installato
    try:
        import PyInstaller
        print(f"\n✅ PyInstaller v{PyInstaller.__version__} trovato")
    except ImportError:
        print("\n❌ PyInstaller non installato!")
        print("   Installa con: pip install pyinstaller")
        sys.exit(1)

    # Pulisci build precedente
    pulisci_build_precedente()

    # Compila
    codice_uscita = compila_exe()

    if codice_uscita == 0:
        print("\n" + "=" * 60)
        print("  ✅ BUILD COMPLETATA CON SUCCESSO!")
        print(f"  📦 File: {OUTPUT_DIR / 'AutoBot_Ox.exe'}")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("  ❌ BUILD FALLITA")
        print("  Controlla i log sopra per i dettagli")
        print("=" * 60)

    sys.exit(codice_uscita)


if __name__ == "__main__":
    main()

import subprocess
import logging

# Flag globale per mostrare nell'interfaccia se la sync è andata bene
esito_sync = None

def sync():
    global esito_sync
    try:
        result = subprocess.run(["ls", "/dev/rtc0"], capture_output=True, text=True)
        if result.returncode != 0:
            esito_sync = False
            logging.warning("⛔ Modulo RTC non trovato (/dev/rtc0 assente)")
            return

        subprocess.run(["sudo", "hwclock", "-s"], check=True)
        esito_sync = True
        logging.info("✅ Orologio di sistema sincronizzato con RTC DS3231")
    except subprocess.CalledProcessError as e:
        esito_sync = False
        logging.error(f"Errore nella sincronizzazione RTC: {e}")
    except Exception as e:
        esito_sync = False
        logging.error(f"Errore imprevisto nella sincronizzazione RTC: {e}")

import RPi.GPIO as GPIO
import time

RELE_PIN = 17  # GPIO usato per attivare il relè

def setup_rele():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(RELE_PIN, GPIO.OUT)
    GPIO.output(RELE_PIN, GPIO.HIGH)  # Assicura che parta spento

def apri_cassetto():
    #print("🔓 Apro il cassetto contanti...")
    for _ in range(4):
        GPIO.output(RELE_PIN, GPIO.LOW)
        time.sleep(0.2)
        GPIO.output(RELE_PIN, GPIO.HIGH)
        time.sleep(0.2)

def pulisci():
    GPIO.cleanup()

if __name__ == "__main__":
    setup_rele()
    apri_cassetto()
    pulisci()

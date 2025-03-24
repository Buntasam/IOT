from machine import Pin, PWM, ADC, I2C
import time
import neopixel
from lcd_api import LcdApi
from i2c_lcd import I2cLcd

# Définir les broches
BUTTON_PIN1 = 16  # GPIO du bouton 1
BUTTON_PIN2 = 27  # GPIO du bouton 2
GAS_SENSOR_PIN = 32  # GPIO pour le détecteur de gaz
STEAM_SENSOR_PIN = 34  # GPIO pour le steam sensor
LED_PIN = 26  # GPIO pour la LED RGB 6812
PIR_PIN = 14  # GPIO pour le PIR motion
YLED_PIN = 12  # GPIO pour la LED jaune
FAN_PIN1 = 18  # GPIO pour le ventilateur (première broche)
FAN_PIN2 = 19  # GPIO pour le ventilateur (deuxième broche)
SDA_PIN = 21  # GPIO pour SDA de l'écran LCD
SCL_PIN = 22  # GPIO pour SCL de l'écran LCD
SERVO1_PIN = 5  # GPIO pour le servo moteur 1
SERVO2_PIN = 13  # GPIO pour le servo moteur 2

angle_0 = 25
angle_90 = 77
angle_180 = 128

# Initialisation des composants
servo1 = PWM(Pin(SERVO1_PIN))
servo1.freq(50)
servo2 = PWM(Pin(SERVO2_PIN))
servo2.freq(50)
pir_motion = Pin(PIR_PIN, Pin.IN)
yled = Pin(YLED_PIN, Pin.OUT)
button1 = Pin(BUTTON_PIN1, Pin.IN, Pin.PULL_UP)
button2 = Pin(BUTTON_PIN2, Pin.IN, Pin.PULL_UP)
gas_sensor = ADC(Pin(GAS_SENSOR_PIN))
gas_sensor.atten(ADC.ATTN_0DB)
steam_sensor = ADC(Pin(STEAM_SENSOR_PIN))
steam_sensor.atten(ADC.ATTN_0DB)
fan1 = Pin(FAN_PIN1, Pin.OUT)  # Configurer la première broche du ventilateur en sortie
fan2 = Pin(FAN_PIN2, Pin.OUT)  # Configurer la deuxième broche du ventilateur en sortie

# Initialisation des LEDs
num_leds = 4
led = neopixel.NeoPixel(Pin(LED_PIN), num_leds)

# Initialisation de l'écran LCD
try:
    i2c = I2C(0, sda=Pin(SDA_PIN), scl=Pin(SCL_PIN), freq=10000)
    devices = i2c.scan()
    if devices:
        print(f"Périphériques I2C trouvés: {[hex(d) for d in devices]}")
        lcd_addr = devices[0]
        lcd = I2cLcd(i2c, lcd_addr, 2, 16)
        lcd.clear()
        lcd.move_to(0, 0)
        lcd.putstr("Systeme detecteur")
        lcd.move_to(0, 1)
        lcd.putstr("Initialisation...")
        lcd_available = True
    else:
        print("Aucun périphérique I2C trouvé!")
        lcd_available = False
except Exception as e:
    print(f"Erreur LCD: {e}")
    lcd_available = False


def window_button():
    if button1.value() == 0:
        print("Le bouton est appuyé !")
        if lcd_available:
            lcd.move_to(0, 0)
            lcd.putstr("Bouton: ON  ")
            servo1.duty(angle_0)
    else:
        print("Le bouton est relâché.")
        if lcd_available:
            lcd.move_to(0, 0)
            lcd.putstr("Bouton: OFF ")
            servo1.duty(angle_180)


def door_button():
    if button2.value() == 0:
        servo2.duty(angle_0)
    else:
        servo2.duty(angle_180)


def read_gas_sensor():
    gas_level = gas_sensor.read()
    print("Niveau de gaz:", gas_level)

    if lcd_available:
        lcd.move_to(0, 1)
        lcd.putstr(f"Gaz: {gas_level}      ")

    if gas_level > 2800:
        print("Gaz détecté !")
        for i in range(num_leds):
            led[i] = (250, 0, 0)  # Rouge
        fan_on()
    else:
        print("Pas de gaz détecté.")
        fan_off()
        for i in range(num_leds):
            led[i] = (0, 0, 0)
    led.write()


def read_steam_sensor():
    steam_level = steam_sensor.read()
    print("Niveau de vapeur:", steam_level)

    if lcd_available:
        lcd.move_to(0, 1)
        lcd.putstr(f"Vapeur: {steam_level}   ")

    if steam_level > 2000:
        print("Vapeur détectée !")
        for i in range(num_leds):
            led[i] = (0, 255, 0)  # Vert
        fan_on()
    else:
        print("Pas de vapeur détectée.")
        fan_off()
        for i in range(num_leds):
            led[i] = (0, 0, 255)  # Bleu
    led.write()


def fan_on():
    fan1.value(1)  # Allumer le ventilateur
    fan2.value(0)  # Allumer la deuxième broche du ventilateur
    print("Ventilateur activé")
    if lcd_available:
        lcd.move_to(10, 0)
        lcd.putstr("FAN:ON ")


def fan_off():
    fan1.value(0)  # Éteindre le ventilateur
    fan2.value(0)  # Éteindre la deuxième broche du ventilateur
    print("Ventilateur désactivé")
    if lcd_available:
        lcd.move_to(10, 0)
        lcd.putstr("FAN:OFF")


def PIR_motion():
    value = pir_motion.value()
    if value == 1:
        yled.value(1)
    else:
        yled.value(0)


# Message de démarrage
print("Démarrage du système de détection...")
time.sleep(2)

# Boucle principale
while True:
    try:
        window_button()
        door_button()
        read_gas_sensor()
        PIR_motion()
        time.sleep(2)
        read_steam_sensor()
        time.sleep(1)
    except Exception as e:
        print(f"Erreur: {e}")
        if lcd_available:
            try:
                lcd.clear()
                lcd.move_to(0, 0)
                lcd.putstr("Erreur systeme")
                time.sleep(2)
            except:
                pass


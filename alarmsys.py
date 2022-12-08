import config

import RPi.GPIO as GPIO
import telepot
import time
from telepot.loop import MessageLoop

#Nombre: José Daniel Medrano Guadamuz
#Curso: Arquitectura II
#Profesor: José Luis Medrano Cerdas

#Link Video: https://youtu.be/1TofmBH3hnw

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Pines
pinTrig = 21
pinEcho = 16
button = 22
redLed = 19
greenLed = 13
pirSensor = 4

# Setup
GPIO.setup(pinTrig, GPIO.OUT)
GPIO.setup(pinEcho, GPIO.IN)
GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(redLed, GPIO.OUT)
GPIO.setup(greenLed, GPIO.OUT)
GPIO.setup(pirSensor, GPIO.IN)

GPIO.output(pinTrig, False)
GPIO.output(redLed, False)
GPIO.output(greenLed, False)

# Variables
# La velocidad del sonido es 343 m/s -> 34300 cm/s
speed = 34300
# Indica si la alarma está apagada o encendida.
global alarmStatus
alarmStatus = False
# Indica si los mensajes estan habilitados o desabilitados.
global areMessagesOn
areMessagesOn = True
# Indica si es el primer mensaje que se envia por telegram.
global firstMessage
firstMessage = True
global seconds
seconds = 0
# La ultima vez que se envio un mensaje.
global timeLastMessage
timeLastMessage = 0
token = config.token
bot = telepot.Bot(token)
global idChat
idChat = 1219959442
global OPTIONS
OPTIONS = "Options \n\nActions \n/help \n/setAlarm \n/unsetAlarm \n/disableMessages \n/enableMessages \n\nInfo \n/isAlarmOn \n/getDistance"

# Función que registra la última vez que se envio un mensaje.
def saveLastMessageTime():
    global timeLastMessage
    timeLastMessage = time.time()

# Función que registra la última vez que se envio el mensaje de "Distancia asegurada."
def startClock():
    global seconds
    seconds = time.time()

# Función para obtener cuanto tiempo ha transcurrido desde startClock().
def getTime():
    return float(time.time() - seconds)

# Función para obtener cuanto tiempo ha transcurrido desde saveLastMessageTime().
def getLastMessageTime():
    return float(time.time() - timeLastMessage)

# Función para saber si ya transcurrio 1 min para enviar el mensaje "Distancia asegurada.".
def isOneMinGoneBy():
    return getTime() >= 60

# Función que verifica si hubo movimiento con el sensor PIR.
def isThereMovement():
    if GPIO.input(pirSensor):
        return True
    else:
        return False

# Función para enviar un mensaje por telegram.
def sendMessage(text, isCommand = False):
    global firstMessage
    if areMessagesOn and firstMessage and not isCommand:
        bot.sendMessage(idChat, text)
        saveLastMessageTime()
        firstMessage = False
    elif areMessagesOn and isCommand:
        bot.sendMessage(idChat, text)
    elif areMessagesOn and getLastMessageTime() > (2*60):
        bot.sendMessage(idChat, text)
        saveLastMessageTime()

# Función para desactivar los mensajes en caso de mucho spam.
def disableMessages():
    global areMessagesOn
    areMessagesOn = False

# Función para activar los mensajes.
def enableMessages():
    global areMessagesOn
    areMessagesOn = True

# Armar y desarmar alarma.
# Función para conocer el estado de la alarma.
def isAlarmSet():
    return alarmStatus   

# Función que controla los leds que indican el estado de la alarma.
def setAlarmLeds(enabled):
    if enabled:
        GPIO.output(greenLed, enabled)
        GPIO.output(redLed, not enabled)
    else:
        GPIO.output(greenLed, enabled)
        GPIO.output(redLed, not enabled)

# Función para obtener el estado de alarma.
def getAlarmStatus():
    if alarmStatus:
        return "La alarma está activada."
    else:
        return "La alarma está desactivada."

# Función que activa o arma la alarma.
def setAlarm():
    global alarmStatus
    if isAlarmSet():
        sendMessage("La alarma ya estaba encendida.", True)
        return
    else:
        alarmStatus = True
        sendMessage("La alarma ha sido encendida.", True)
        setAlarmLeds(True)

# Función que desactiva o desarma la alarma.
def unsetAlarm():
    global alarmStatus
    if not isAlarmSet():
        sendMessage("La alarma ya estaba apagada.", True)
        return
    else:
        alarmStatus = False
        sendMessage("La alarma ha sido apagada.", True)
        setAlarmLeds(False)

# Función que se utliza como el callback de GPIO.add_event_detect().
def buttonPressed(pin):
    if isAlarmSet():
        unsetAlarm()
    else:
        setAlarm()
    print("\nPressed\n")

# Función que obtiene la distancia.
def getDistance():
    GPIO.output(pinTrig, True)
    time.sleep(0.00001)
    GPIO.output(pinTrig, False)
    while GPIO.input(pinEcho) == 0:
        start = time.time()
    while GPIO.input(pinEcho) == 1:
        finish = time.time()
    duration = finish - start
    # Para no obtener la distancia de la ida y la vuelta, se divide por 2.
    distance = (speed * duration) / 2 
    # Devuelve la distancia con 2 decimales.
    return float("{:.2f}".format(distance))

# Función que está constantemente verificando la distancia.
def checkDistance(distance):
    # Si la distancia es mayor a 30 y si no ha pasado un minuto desde el 
    # envio de "Distancia asegurada", entonces envie un mensaje con la distancia.
    if distance > 30 and not isOneMinGoneBy():
        print(f"Distancia: {distance} cm.") 
    # Si la distancia es mayor a 30 y ya transcurrio 1 min, envie el mensaje con 
    # la distancia y reinicie el contador.
    elif distance > 30 and isOneMinGoneBy():
        print("\nDistancia asegurada.\n")
        startClock()
    # Si no es alguno de los casos anteriores, entonces hay algo en el rango de 30 cm y,
    # por lo tanto, se mandará una alerta si la alarma esta activada.
    elif distance <= 30 and isThereMovement():
        print("¡ALERTA! ¡ALERTA!")
        sendMessage(f"¡Cuidado! Se ha detectado un objeto a {distance} cm.")
        startClock()

# Función para los comandos.
def connectBot(value):
    global idChat
    idChat = value["chat"]["id"]
    command = value["text"]
    print(f"Command: {command}")
    if command == "/help":
        sendMessage(OPTIONS, True)
    elif command == "/isAlarmOn":
        sendMessage(getAlarmStatus(), True)
    elif command == "/setAlarm":
        setAlarm()
    elif command == "/unsetAlarm":
        unsetAlarm()
    elif command == "/getDistance":
        sendMessage(f"La distancia es {getDistance()} cm.", True)
    elif command == "/disableMessages":
        sendMessage("Ya no recibiras más mensajes.", True)
        disableMessages()
    elif command == "/enableMessages":
        enableMessages()
        sendMessage("Los mensajes han sido habilitados.", True)

# Función principal,
def main():
    try:
        MessageLoop(bot, connectBot).run_as_thread()
        time.sleep(2)
        GPIO.add_event_detect(button, GPIO.FALLING, callback=buttonPressed, bouncetime=400)
        setAlarmLeds(False)
        sendMessage(OPTIONS, True)
        startClock()
        while True:
            if isAlarmSet():
                checkDistance(getDistance())
                time.sleep(1)

    except KeyboardInterrupt:
        print("\Fin\n")
    finally:
        GPIO.cleanup()

# Llamado del main().
main()
import os
import json
import logging
import signal
import sys
import time

import paho.mqtt.client as mqtt
from pymodbus.server import StartTcpServer
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext, ModbusSequentialDataBlock
from pymodbus.device import ModbusDeviceIdentification

# 🔧 Logging konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("SDM630 Emulator")

# 📁 Konfiguration laden
def load_config(path="/data/options.json"):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Fehler beim Laden der Konfiguration: {e}")
        sys.exit(1)

config = load_config()
mqtt_broker = config.get("mqtt_broker", "localhost")
mqtt_topic = config.get("mqtt_topic", "sensor/grid_power")
slave_id = config.get("slave_id", 1)
modbus_port = config.get("modbus_port", 502)

# 🧮 Modbus-Daten vorbereiten
store = ModbusSlaveContext(hr=ModbusSequentialDataBlock(0, [0]*100))
context = ModbusServerContext(slaves={slave_id: store}, single=False)

# 🆔 Geräteidentifikation (optional, aber empfohlen)
identity = ModbusDeviceIdentification()
identity.VendorName = "Thorsten"
identity.ProductCode = "SDM630Emu"
identity.VendorUrl = "https://github.com/tlrt2701/Deye-EmulatorV2"
identity.ProductName = "SDM630 Emulator"
identity.ModelName = "SDM630-TCP"
identity.MajorMinorRevision = "1.0.0"

# 📡 MQTT-Callback
def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        value = float(payload)
        int_value = int(value)
        store.setValues(3, 0, [int_value])  # Holding Register 0
        logger.info(f"MQTT empfangen: {value:.2f} W → Register 0 gesetzt")
    except Exception as e:
        logger.warning(f"Ungültiger MQTT-Wert: {msg.payload} → Fehler: {e}")

def on_disconnect(client, userdata, rc):
    logger.warning("MQTT-Verbindung getrennt. Versuche Neuverbindung...")
    while True:
        try:
            client.reconnect()
            logger.info("MQTT erfolgreich neu verbunden.")
            break
        except Exception:
            time.sleep(5)

# 🧵 MQTT-Client starten
client = mqtt.Client()
client.on_message = on_message
client.on_disconnect = on_disconnect

try:
    client.connect(mqtt_broker, 1883, 60)
except Exception as e:
    logger.error(f"MQTT-Verbindung fehlgeschlagen: {e}")
    sys.exit(1)

client.subscribe(mqtt_topic)
client.loop_start()

# 🛑 Signal-Handling für sauberes Beenden
def handle_exit(signum, frame):
    logger.info("Beende Emulator...")
    client.loop_stop()
    client.disconnect()
    sys.exit(0)

signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)

# 🚀 Modbus TCP-Server starten
logger.info(f"Starte Modbus TCP-Server auf Port {modbus_port}...")
StartTcpServer(context, identity=identity, address=("0.0.0.0", modbus_port))

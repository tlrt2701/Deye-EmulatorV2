import os
import json
import logging
import signal
import sys

import paho.mqtt.client as mqtt
from pymodbus.server.sync import StartTcpServer
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext, ModbusSequentialDataBlock
from pymodbus.device import ModbusDeviceIdentification

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("SDM630 Emulator")

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

store = ModbusSlaveContext(hr=ModbusSequentialDataBlock(0, [0]*100))
context = ModbusServerContext(slaves={slave_id: store}, single=False)

identity = ModbusDeviceIdentification()
identity.VendorName = "Thorsten"
identity.ProductCode = "SDM630Emu"
identity.VendorUrl = "https://github.com/tlrt2701/Deye-EmulatorV2"
identity.ProductName = "SDM630 Emulator"
identity.ModelName = "SDM630-TCP"
identity.MajorMinorRevision = "1.0.0"

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        value = float(payload)
        int_value = int(value)
        store.setValues(3, 0, [int_value])
        logger.info(f"MQTT empfangen: {value:.2f} W → Register 0 gesetzt")
    except Exception as e:
        logger.warning(f"Ungültiger MQTT-Wert: {msg.payload} → Fehler: {e}")

client = mqtt.Client()
client.on_message = on_message

try:
    client.connect(mqtt_broker, 1883, 60)
except Exception as e:
    logger.error(f"MQTT-Verbindung fehlgeschlagen: {e}")
    sys.exit(1)

client.subscribe(mqtt_topic)
client.loop_start()

def handle_exit(signum, frame):
    logger.info("Beende Emulator...")
    client.loop_stop()
    client.disconnect()
    sys.exit(0)

signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)

logger.info(f"Starte Modbus TCP-Server auf Port {modbus_port}...")
StartTcpServer(context, identity=identity, address=("0.0.0.0", modbus_port))

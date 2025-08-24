import os
import json
import logging
from pymodbus.server import StartTcpServer
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext, ModbusSequentialDataBlock
from pymodbus.device import ModbusDeviceIdentification
import paho.mqtt.client as mqtt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SDM630 Emulator")

# Konfiguration laden
options_path = os.getenv("OPTIONS", "/data/options.json")
with open(options_path) as f:
    config = json.load(f)

mqtt_broker = config["mqtt_broker"]
mqtt_topic = config["mqtt_topic"]
slave_id = config["slave_id"]
modbus_port = config["modbus_port"]

# Modbus-Datenblock vorbereiten
store = ModbusSlaveContext(
    hr=ModbusSequentialDataBlock(0, [0]*100)
)
context = ModbusServerContext(slaves={slave_id: store}, single=False)

# MQTT-Callback
def on_message(client, userdata, msg):
    try:
        value = float(msg.payload.decode())
        int_value = int(value)
        store.setValues(3, 0, [int_value])  # Holding Register 0
        logger.info(f"MQTT empfangen: {value:.2f} W → Register 0 gesetzt")
    except Exception as e:
        logger.error(f"Fehler beim Verarbeiten der MQTT-Nachricht: {e}")

# MQTT-Client starten
client = mqtt.Client()
client.on_message = on_message
client.connect(mqtt_broker, 1883, 60)
client.subscribe(mqtt_topic)
client.loop_start()

# Modbus TCP-Server starten
logger.info(f"Starte Modbus TCP-Server auf Port {modbus_port}...")
StartTcpServer(context, address=("0.0.0.0", modbus_port))

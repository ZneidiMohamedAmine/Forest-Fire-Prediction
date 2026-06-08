import os
import json
import paho.mqtt.client as mqtt
from channels.generic.websocket import AsyncWebsocketConsumer
from supervisor.tasks.calcul_fwi import calculate_fwi_task

# Configuration pour TOUTES les applications TTN
TTN_HOST = "eu1.cloud.thethings.network"
TTN_PORT = 8883

TTN_APPS = [
    {
        "user": os.environ.get("TTN_USER_1", "lorae5app2@ttn"),
        "pass": os.environ.get("TTN_PASS_1", "NNSXS.7SPGHIMTGOGDQCROYRSD67YPZL4P5PZQ3MQJRCY.QBM3MPQHNDZWHOBTDDEUVQT2EBHP6ECICHBEWRZWWCGPMUY2FAKA"),
    },
    {
        "user": os.environ.get("TTN_USER_2", "chottmariem@ttn"),
        "pass": os.environ.get("TTN_PASS_2", "NNSXS.3YVGCH7JORI7ISWVUHRFVEM3DXZRKGR6YOUR6GQ.5TNHG2HAPHXQGVE4WT7KBPVJKOGRNLBS23M5X42VH233GLFW2CBA"),
    },
]

class MQTTConsumer(AsyncWebsocketConsumer):
    #accepte connexion WebSocket (frontend)
    async def connect(self):
        await self.accept()
        self.clients = []

        for i, app in enumerate(TTN_APPS):
            client = mqtt.Client(client_id=f"django_mqtt_{i}")
            client.username_pw_set(app["user"], app["pass"])
            client.tls_set()
            client.on_message = self.on_message
            try:
                client.connect(TTN_HOST, TTN_PORT, 60)
                client.subscribe("#", qos=1)
                client.loop_start()
                self.clients.append(client)
                print(f"MQTT connected to TTN app: {app['user']}")
            except Exception as e:
                print(f"MQTT connection failed for {app['user']}: {e}")

    async def disconnect(self, close_code):
        for client in getattr(self, "clients", []):
            client.loop_stop()

    def on_message(self, client, userdata, message):
        try:
            parsed = json.loads(message.payload)
            device_id = parsed["end_device_ids"]["device_id"]
            up = parsed.get("uplink_message", {})
            dp = up.get("decoded_payload", {})
            
            print(f"--- MQTT Message Received ---")
            print(f"Device ID: {device_id}")
            print(f"Decoded Payload: {dp}")

            data = {
                "device_id": device_id,
                "temperature": dp.get("temperature"),
                "humidity": dp.get("humidity"),
                "gaz": dp.get("gaz"),
                "pressure": dp.get("pressure") or dp.get("pressur"), # Handle both spellings
                "rain": dp.get("rain", 0),
                "rssi": (up.get("rx_metadata") or [{}])[0].get("rssi"),
                "battery": dp.get("battery_percent"),
            }
            # Envoie vers Celery
            calculate_fwi_task.delay(data)
        except Exception as e:
            print("MQTT parse error:", e)


#MQTTConsumer = récepteur temps réel des données TTN
#se connecte à TOUTES les applications TTN (MQTT)
#reçoit les données des capteurs
#extrait les valeurs
#envoie au worker Celery (calculate_fwi_task)



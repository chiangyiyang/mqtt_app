import sys
import os
from dotenv import load_dotenv

import paho.mqtt.client as mqtt

from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Slot, Signal, QObject

load_dotenv()  # take environment variables from .env.

led_control_topic = os.getenv('led_control_topic')
led_status_topic = os.getenv('led_status_topic')
server_url = os.getenv('server_url')
server_port = int(os.getenv('server_port'))


# MQTT Client setup
class MQTTClient(QObject):
    message_received = Signal(str)

    def __init__(self, host, port):
        super().__init__()
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(host, port, 60)
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, reason_code, properties):
        print(f"Connected with result code {reason_code}")
        self.client.subscribe(led_status_topic)

    def send_command(self, topic, message):
        self.client.publish(topic, message,retain=True)

    def on_message(self, client, userdata, message):
        decoded_message = message.payload.decode()
        print(decoded_message)
        self.message_received.emit(decoded_message)


# Main Window setup using PySide6
class MainWindow(QMainWindow):
    def __init__(self, mqtt_client):
        super().__init__()
        self.mqtt_client = mqtt_client
        self.setWindowTitle("LED Toggle App")
        self.setGeometry(300, 300, 200, 150)  # x, y, width, height

        self.led_icon = QLabel(self)
        self.led_icon.setPixmap(QPixmap("assets/led_off.png")) 
        self.led_icon.move(68, 0)  
        self.led_icon.resize(64, 64)  

        self.button = QPushButton("Toggle LED", self)
        self.button.clicked.connect(self.on_button_clicked)
        self.button.move(50, 50)  
        # Set the button style to be transparent
        self.button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: black;
                border: 2px solid black;
            }
            QPushButton:hover {
                border-color: blue;
            }
            QPushButton:pressed {
                border-color: red;
            }
        """)
        self.button.resize(100, 50)  
        self.setCentralWidget(self.button)
        self.led_state = False

        self.mqtt_client.message_received.connect(self.update_icon)

    @Slot()
    def on_button_clicked(self):
        self.toggle_led()

    @Slot(str)
    def update_icon(self, message):
        print('yy', message)
        if message == "LED ON":
            self.led_icon.setPixmap(QPixmap("assets/led_on.png"))
        else:
            self.led_icon.setPixmap(QPixmap("assets/led_off.png"))

    def toggle_led(self):
        # Toggle the state of the LED
        self.led_state = not self.led_state
        command = 'ON' if self.led_state else 'OFF'
        self.mqtt_client.send_command(led_control_topic, command)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    mqtt_client = MQTTClient(server_url, server_port)
    
    window = MainWindow(mqtt_client)
    window.show()
    sys.exit(app.exec())

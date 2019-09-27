from flask import Flask
from .config import Config
from flask_socketio import SocketIO

app = Flask(__name__)
app.config.from_object(Config)

from app import gui_page


import sys
import serial
import glob
import json
import logging
from app import app
from flask_socketio import SocketIO, emit
from flask import render_template
from random import randrange, random as rd
from time import sleep
from threading import Thread
from struct import *
from .syncParser import Parser
from serial.tools.list_ports import comports
from datetime import datetime as dt


socketio = SocketIO(app)

# logging
logging.basicConfig(
    filename=dt.now().strftime("%Y_%m_%d_%H%M%S.log"),
    format="%(asctime)s %(message)s",
    level=logging.INFO,
)

# create file
n = "log" + dt.now().strftime("%Y_%m_%d_%H%M%S") + ".txt"


@app.route("/index")
def main():
    return render_template("index.html")



@app.route("/dash")
def dash():
    return render_template("dash.html")

@app.route("/")
@app.route("/dash1")
def dash1():
    return render_template("dash1.html")


@app.route("/test")
def test():
    return render_template("test2.html")


@socketio.on("connect")
def test_connect():
    # while True:
    #     print('foo')
    #     socketio.emit('emit event', {'number': 123123})
    print("connected")
    t1 = Thread(target=rdThread)
    t = Thread(target=serialRead)
    t.start()
    # t1.start()


@socketio.on("my event")
def handle_event(json):
    print("received" + str(json))


def rdThread():
    i = 0

    while i < 25:
        socketio.emit(
            "test",
            {
                "temp": 28.04,
                "millis": 862158,
                "alt": 0.048264697194099426,
                "vel": -0.05553833767771721,
                "acc": -0.03425803780555725,
                "raw_alt": 0.12371826171875,
                "raw_acc": -0.053353309631347656,
                "lat": 42.95886993408203,
                "lon": -78.82363891601562,
                "batt_v": 8.268,
                "phase": "Idle",
            },
        )
        socketio.emit(
            "emit event",
            {"number": round(rd() * 10000, 3), "time": round(rd() * 100000, 3)},
        )
        logging.info(
            str({"number": round(rd() * 10000, 3), "time": round(rd() * 1, 3)})
        )
        with open(n, "a") as outfile:
            json.dump(
                {"number": round(rd() * 10000, 3), "time": round(rd() * 100000, 3)},
                outfile,
                indent=4,
            )
        # print("sent")
        # sleep(3)
        i += 1


def serialRead():
    parser = Parser()    
    with open(n, "a") as outfile:
        # json.dump(data, outfile, indent=4)
        for port, desc, hwid in comports():
            try:
                print(port)
                s = serial.Serial(port, baudrate=115200)
                while True:
                    buf = s.read(40)
                    print("read")
                    print(len(buf))
                    print(len(parser.buf))
                    data = parser.parse(buf)
                    for msg in data:
                        print(msg)
                        socketio.emit("data", msg)
                        # print("sending DATA")
                        logging.info(str(msg))
                        # with open(n, "a") as outfile:
                        json.dump(data, outfile)
                        outfile.write("\n")
                        # print("DATA logged")
                    outfile.flush()
            except (OSError, serial.SerialException):
                pass


if __name__ == "__main__":
    socketio.run(app)

# socketio.run(app)

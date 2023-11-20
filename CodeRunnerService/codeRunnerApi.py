from flask import Flask, request, render_template
from flask_socketio import SocketIO
import json
import threading
import time
import signal


app = Flask(__name__)
socketio = SocketIO(app)

terminate_thread = False
pending_tasks = []
connected_workers = dict()


@socketio.on("connect")
def socket_connect():
    connected_workers[request.sid] = False


@socketio.on("disconnect")
def socket_connect():
    connected_workers.pop(request.sid)


@socketio.on("submit_result")
def submit_result(data):
    connected_workers[request.sid] = False
    socketio.emit("result_callback", data[0], to=data[1])

@socketio.on("enqueue_code")
def enqueue_code(data):
    data["sid"] = request.sid
    pending_tasks.append(data)


def TaskBroker():
    while not terminate_thread:
        if len(pending_tasks) > 0:
            for id, working in connected_workers.items():
                if not working:
                    socketio.emit("run_code", pending_tasks.pop(), to=id)
                    connected_workers[id] = True
                    break
        else:
            time.sleep(0.1)


def handle_interrupt(signum, frame):
    global terminate_thread
    print("Code Runner API Terminating...")
    terminate_thread = True
    exit(0)


signal.signal(signal.SIGINT, handle_interrupt)
signal.signal(signal.SIGTERM, handle_interrupt)

task_broker_thread = threading.Thread(target=TaskBroker)
task_broker_thread.start()

socketio.run(app, port=8989)

import asyncio
from collections import defaultdict
import json
import os
import threading
import queue
import websockets
import webbrowser

events = queue.Queue()

def send(event):
    events.put(event)

async def send_event(websocket, path):
    while True:
        event = events.get()
        await websocket.send(json.dumps(event))


def load_ui():
    dir = os.path.dirname(__file__)
    path = "file://" + os.path.join(dir, "index.html")
    webbrowser.open(url=path, autoraise=True)


def start_event_loop(event_loop, server):
    event_loop.run_until_complete(server)
    event_loop.run_forever()


def start():
    new_loop = asyncio.new_event_loop()
    server = websockets.serve(send_event, '127.0.0.1', 5678, loop=new_loop)
    threading.Thread(target=start_event_loop, args=(new_loop, server)).start()
    load_ui()

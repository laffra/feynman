"""
Explain complex things in simple terms
"""

from concurrent.futures import thread
import functools
import inspect
import os
import re
import sys
import threading
import time

import feynman.server

ispath = re.compile(r".*[/\\]")
ispyfile = re.compile(r".*\.py$")
file2mod = re.compile(r".*python[23].[0-9]*[/\\](.*)")
path2mod = re.compile(r"[/\\]")
module = re.compile(r"<module>")
last_flush = time.time()
updates = { }
config = {}

UPDATE_FLUSH_INTERVAL = 0.05


def create_event(kind, locals):
    event = dict(locals)
    if "self" in event:
        del event["self"]
    event["when"] = time.time()
    event["kind"] = kind
    event["id"] = locals.get("id") or time.time()
    return event

def text(left, top, text, width=100, height=20, textAlign="left", font="Arial", color="black", id=""):
    feynman.server.send(create_event("text", locals()))

def rectangle(left, top, width, height, border="2px solid black", background="transparent", id=""):
    feynman.server.send(create_event("rectangle", locals()))

def oval(left, top, width, height, border="2px solid black", background="transparent", id=""):
    feynman.server.send(create_event("oval", locals()))

def image(left, top, width, height, src, id=""):
    feynman.server.send(create_event("img", locals()))

def line(x1, y1, x2, y2, color="black", stroke=2, id=""):
    feynman.server.send(create_event("line", locals()))

def flush_updates(exit=False):
    global last_flush
    when = time.time()
    if exit or when - last_flush > UPDATE_FLUSH_INTERVAL:
        for key in updates:
            feynman.server.send(create_event("update", updates[key]))
        updates.clear()
        last_flush = when
    if exit:
        threading.Thread(target=lambda: (time.sleep(2), os._exit(0))).start()


def update(id, name, value):
    key = (id, name)
    if key in updates:
        updates[key]["value"] = value
    else:
        updates[key] = locals()
    flush_updates()

def on(function_name):
    def inner(func):
        config[function_name] = func
        return func
    return inner

class Explain(object):
    def __init__(self):
        self.info_cache = set()
        self.modules_to_trace = set()
        self.code_cache = {}

    def send_info(self, item_type, item_name):
        if not self.enabled or item_name in self.info_cache:
            return
        self.info_cache.add(item_name)
        feynman.server.send(create_event("info", locals()))
        return item_name
    
    def getargs(self, code):
        if code in self.code_cache:
            return self.code_cache[code]
        args = inspect.getargs(code).args
        self.code_cache[code] = args
        return args

    def explain(self, name, frame):
        if name in config:
            config[name](**frame.f_locals)
        
    def handle_call(self, frame):
        module_name = frame.f_globals["__name__"]
        if module_name == "feynman": return
        function_name = frame.f_code.co_name
        self.send_info("module", module_name)
        try:
            class_name = "%s.%s" % (module_name, frame.f_locals['self'].__class__.__name__)
            self.send_info("class", class_name)
            name = "%s.%s" % (class_name, function_name)
            self.send_info("method", "%s %s" % (name, " ".join(self.getargs(frame.f_code))))
        except Exception as e:
            name = "%s.%s" % (module_name, function_name)
            self.send_info("function", "%s %s" % (name, " ".join(self.getargs(frame.f_code))))
        self.explain(name, frame)

    def handle_event(self, frame, event, _):
        if event == "return":
            self.handle_call(frame)
        return self.handle_event

    def __enter__(self):
        feynman.server.start()
        threading.setprofile(self.handle_event)
        sys.setprofile(self.handle_event)
        self.enabled = True

    def __exit__(self, type, value, traceback):
        self.enabled = False
        threading.setprofile(None)
        sys.setprofile(None)
        flush_updates(True)

"""
Explain complex things in simple terms
"""

from concurrent.futures import thread
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
event_count = 0
return_value = None

UPDATE_FLUSH_INTERVAL = 0.05

def create_event(kind, locals):
    event = dict(locals)
    if "self" in event:
        del event["self"]
    event["when"] = time.time()
    event["kind"] = kind
    event["id"] = locals.get("id") or f"node-{event_count}"
    feynman.event_count += 1
    return event

def text(text, left=0, top=0, width=100, height=20, textAlign="left", font="Arial", color="black", id="", group=""):
    return feynman.server.send(create_event("text", locals()))

def rectangle(left=0, top=0, width=100, height=100, border="2px solid black", background="transparent", id="", group=""):
    return feynman.server.send(create_event("rectangle", locals()))

def oval(left=0, top=0, width=100, height=100, border="2px solid black", background="transparent", id="", group=""):
    return feynman.server.send(create_event("oval", locals()))

def image(src, left=0, top=0, width=100, height=100, id="", group=""):
    return feynman.server.send(create_event("img", locals()))

def line(x1=0, y1=0, x2=100, y2=100, color="black", stroke=2, id="", group=""):
    return feynman.server.send(create_event("line", locals()))

def html(html):
    if html.endswith(".html"):
        html = getfile(html)
    return feynman.server.send(create_event("html", locals()))

def css(text):
    if text.endswith(".css"):
        text = getfile(text)
    return feynman.server.send(create_event("css", locals()))

def run(text):
    if text.endswith(".js"):
        text = getfile(text)
    return feynman.server.send(create_event("run", locals()))

def getfile(name):
    frame = inspect.currentframe()
    while "/feynman/" in frame.f_globals["__file__"]:
        frame = frame.f_back
    dirname = os.path.dirname(frame.f_globals["__file__"])
    path = os.path.join(dirname, name)
    try:
        return open(path).read()
    except:
        return ""

def group(name, left=0, top=0, width="auto", height="auto", border="none", background="transparent", group="", children=[]):
    id = name
    feynman.server.send(create_event("group", locals()))
    for child in children:
        feynman.run(f"""$('#{child["id"]}').css("position","auto").appendTo($('[name="{name}"]'))""")
    feynman.run(f"$('#{id}').draggable({{containment: 'parent'}})")

def flush_updates(exit=False):
    when = time.time()
    if exit or when - last_flush > UPDATE_FLUSH_INTERVAL:
        for key in updates:
            feynman.server.send(create_event("update", updates[key]))
        updates.clear()
        feynman.last_flush = when
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
        # feynman.server.send(create_event("info", locals()))
        return item_name
    
    def getargs(self, code):
        if code in self.code_cache:
            return self.code_cache[code]
        args = inspect.getargs(code).args
        self.code_cache[code] = args
        return args

    def explain(self, name, frame, return_value, args):
        if name in config:
            feynman.return_value = return_value
            config[name](*[frame.f_locals[arg] for arg in args])
        
    def handle_return(self, frame, return_value):
        module_name = frame.f_globals["__name__"]
        if module_name == "feynman": return
        function_name = frame.f_code.co_name
        self.send_info("module", module_name)
        args = self.getargs(frame.f_code)
        try:
            class_name = "%s.%s" % (module_name, frame.f_locals['self'].__class__.__name__)
            self.send_info("class", class_name)
            name = "%s.%s" % (class_name, function_name)
            self.send_info("method", "%s %s" % (name, " ".join(args)))
        except Exception as e:
            name = "%s.%s" % (module_name, function_name)
            self.send_info("function", "%s %s" % (name, " ".join(args)))
        self.explain(name, frame, return_value, args)

    def handle_event(self, frame, event, arg):
        if event == "return":
            self.handle_return(frame, arg)
        return self.handle_event

    def import_defaults(self):
        html("explain.html")
        css("explain.css")
        run("explain.js")

    def __enter__(self):
        feynman.server.start()
        threading.setprofile(self.handle_event)
        sys.setprofile(self.handle_event)
        self.enabled = True
        self.import_defaults()

    def __exit__(self, type, value, traceback):
        self.enabled = False
        threading.setprofile(None)
        sys.setprofile(None)
        flush_updates(True)

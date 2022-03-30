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
updates = {}
config = {}
config_has_regex = False
trace_targets = []
trace_targets_shown = set()
event_count = 0
return_value = None
function_name = ""

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
            
def compile_config_regexes():
    for name in list(config.keys()):
        regex = re.compile(name)
        if regex != name:
            func = config[name]
            config[regex] = func
            del config[name]

def on(function_name):
    def inner(func):
        config[re.compile(function_name) if config_has_regex else function_name] = func
        if re.compile(function_name) == function_name:
            feynman.config_has_regex = True
            compile_config_regexes()
        return func
    return inner

def trace(moduleOrClass):
    trace_targets.append(f"{moduleOrClass}.")

def get_handlers(target):
    if config_has_regex:
        for pattern, function in config.items():
            if re.match(pattern, target):
                yield function
    else:
        yield config.get(target)


class Explain(object):
    def __init__(self):
        self.info_cache = set()
        self.modules_to_trace = set()
        self.code_cache = {}
    
    def getargs(self, code):
        if code in self.code_cache:
            return self.code_cache[code]
        args = inspect.getargs(code).args
        self.code_cache[code] = args
        return args

    def explain(self, function_name, frame, return_value, args):
        feynman.return_value = return_value
        feynman.function_name = function_name
        for handler in get_handlers(function_name):
            if handler:
                handler(*[frame.f_locals[arg] for arg in args])
        if function_name not in trace_targets_shown:
            for target in trace_targets:
                if function_name.startswith(target):
                    print(f"@feynman.on(\"{function_name}\")")
                    print(f"def {function_name[len(target):]}({','.join(args)}):")
                    print(f"   pass")
                    print()
                    trace_targets_shown.add(function_name)
            
    def handle_return(self, frame, return_value):
        module_name = frame.f_globals["__name__"]
        if module_name == "feynman": return
        function_name = frame.f_code.co_name
        args = self.getargs(frame.f_code)
        try:
            class_name = "%s.%s" % (module_name, frame.f_locals['self'].__class__.__name__)
            name = "%s.%s" % (class_name, function_name)
        except Exception as e:
            name = "%s.%s" % (module_name, function_name)
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

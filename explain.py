from collections import defaultdict
import feynman;
import time

databases = {}
colors = [ "pink", "lightyellow", "lightgreen", "lightblue", "white" ]
counts = defaultdict(int)

def get_x(name):
    if not name in databases:
        databases[name] = len(databases)
    index = databases[name]
    return 100 + index * 303

def get_color(name):
    return colors[ get_x(name) % len(colors) ]

def increment_count(name, operation):
    key = f"{name}-{operation}"
    counts[key] += 1
    return counts[key]

def database(x, y, w, h, name, background="white", font="12px Arial"):
    feynman.rectangle(x, y + h/10, w, 6*h/10, background=background)
    feynman.oval(x, y, w, h/5, background=background)
    feynman.oval(x, y + 3*h/5, w, h/5, background=background)
    feynman.rectangle(x + 2, y + 6*h/10, w, h/10, border="", background=background)
    feynman.text(x, y + 3*h/8, name, w, 24, "center", font)

feynman.text(100, 100, "Reading and writing data between two databases", 900, font="32px Arial")
feynman.text(100, 170, "", 900, font="24px Arial", color="blue", id="step")

@feynman.on("example.Database.__init__")
def createDatabase(self, name):
    database(get_x(name), 250, 90, 170, name, get_color(name), "24px Courier")
    feynman.text(get_x(name) + 100, 290, "read: 0", id=f"{name}-read")
    feynman.text(get_x(name) + 100, 310, "write: 0", id=f"{name}-write")
    feynman.text(get_x(name) + 100, 330, "size: 0", id=f"{name}-size")

@feynman.on("example.Database.read")
def read(self, key):
    feynman.update(f"{self.name}-read", "text", f"read: {increment_count(self.name, 'read')}")

@feynman.on("example.Database.write")
def write(self, key, value):
    feynman.update(f"{self.name}-write", "text", f"write: {increment_count(self.name, 'write')}")
    feynman.update(f"{self.name}-size", "text", f"size: {len(self.data)}")

@feynman.on("example.Database.delete")
def delete(self, key):
    feynman.update(f"{self.name}-size", "text", f"size: {len(self.data)}")

@feynman.on("example.log")
def log(message):
    feynman.update("step", "text", message)


print("running example.py with Feynman.Explain...")
when = time.time()
with feynman.Explain():
    import example
    example.main()
    print("Ran for", time.time() - when, "seconds")

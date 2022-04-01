import sys
sys.path.extend(["../..", "../../.."]) # this module path is not needed when using pip install
import feynman
from collections import defaultdict

feynman.html("explain.html")
feynman.css("explain.css")
feynman.run("explain.js")


counts = defaultdict(int)

def increment_count(name, operation):
    key = f"{name}-{operation}"
    counts[key] += 1
    return counts[key]

def database(name, x, y, w, h):
    feynman.group(name, x, y, group="databases", children=[
        feynman.rectangle(0, h/10, w, 6*h/10),
        feynman.oval(0, 0, w, h/5),
        feynman.oval(0, 3*h/5, w, h/5),
        feynman.rectangle(2, 6*h/10, w, h/10, border=""),
        feynman.text(name, 2, 3*h/8, w, 24, "center"),
    ])
    feynman.run(f"addDatabase('{name}')")

@feynman.on("db.Database.__init__")
def createDatabase(self, name):
    database(name, 0, 20, 100, 170)
    feynman.text("read: 0", 120, 30, id=f"{name}-read", group=name)
    feynman.text("write: 0", 120, 50, id=f"{name}-write", group=name)
    feynman.text("size: 0", 120, 70, id=f"{name}-size", group=name)

@feynman.on("db.Database.read")
def read(self, key):
    feynman.update(f"{self.name}-read", "text", f"read: {increment_count(self.name, 'read')}")
    feynman.run(f"busy('{self.name}')")

@feynman.on("db.Database.write")
def write(self, key, value):
    feynman.update(f"{self.name}-write", "text", f"write: {increment_count(self.name, 'write')}")
    feynman.update(f"{self.name}-size", "text", f"size: {len(self.data)}")
    feynman.run(f"busy('{self.name}')")

@feynman.on("db.Database.delete")
def delete(self, key):
    feynman.update(f"{self.name}-size", "text", f"size: {len(self.data)}")
    feynman.run(f"busy('{self.name}')")

@feynman.on("db.log")
def log(message):
    feynman.update("step", "text", message)

print("running db.py with Feynman.Explain...")
with feynman.Explain():
    import db
    db.main()

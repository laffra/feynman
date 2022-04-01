# What is Feynman?
Feynman is a visualization library to explain complex Python code in simple terms.


| <img src=images/example.gif width=800px> | <img src=images/dashboard.png width=500px> |
| :---: | :---: |
| A Feynman animation showing database access | A dashboard highlighting anomalous metrics |


## Why the name?
    "If you cannot explain something in simple terms, you don't understand it." 
    -- Richard Feynman

## What does it do?
Feynman scripts look like unit tests. But, instead of testing the behavior of a class, a Feynman rule watches the state of a Python module, function, or class, and decides how to best draw a represenation of the runtime state. 

Feynman rules can be used to:
- explain how a complex Python system works in very simple terms
- validate the behavior and state of the system and highlight anomalies
- create a dashboard with metrics 

Other than a debugger, where a given anomaly has to be hunted down and discovered, Feynman facilitates the occurence of the [Aha! moment](https://en.wikipedia.org/wiki/Eureka_effect) by showing surprising things happening in the system. 

## An Example - Database Access

Consider the database defined in [test/db.py](test/db.py):

``` python
class Database(object):
    def __init__(self, name):
        self.name = name
        self.data = {}

    def read(self, key):
        # reading is fast
        time.sleep(0.001)
        return self.data.get(key, None)

    def write(self, key, value):
        # writing is slow
        time.sleep(0.01)
        self.data[key] = value

    def delete(self, key):
        time.sleep(0.005)
        del self.data[key]
```

This simplified API offers a simple key-value store to read and write values based on a key. 

Here is an example that reads and writes 100 objects between two databases we call `book1` and `book2`:

``` python
def main():
    log("step 1. Create two books")
    book1 = open("book1")
    book2 = open("book2")
    count = 100
    keys = [f"key-{n}" for n in range(count)]
    values = [f"value-{n}" for n in range(count)]

    log("step 2. Write values to book 1")
    for key, value in zip(keys, values):
        book1.write(key, value)

    log("step 3. Copy values from book 1 to 2")
    for key in keys:
        value = book1.read(key)
        book2.write(key, value)

    log("step 4. Read values from book 2")
    for n in range(3):
        for key in keys:
            value = book2.read(key)

    log("step 5. Clear book 1")
    for key in keys:
        book1.delete(key)

    log("step 6. Done")
```
    
This example runs for a while, simulating the cost of DB accesses, and produces this output:
```
% python3 test/db.py
step 1. Create two books
step 2. Write values to book 1
step 3. Copy values from book 1 to 2
step 4. Read values from book 2
step 5. Clear book 1
step 6. Done
```

## Visualizing Database Access

To visualize the database read, write, and delete operations for the two databases
we create above we introduce the script in [test/explain/db/explain.py](db/explain.py).

Among other things, we declare a Feynman rule for detecting when new instances
of the `db.Database` class are instantiated. The predicate is defined using
a Python decorator that acts as an IFTT rule. The format is:

``` python
@feynman.on("fully.qualified.function.or.method.name")
def meaningfulFunctionName(same, arguments, asoriginal):
```

The function name in the predicate can be literal, containing
the full modules path, followed by a function name or a method 
name. Alternatively, the predicate may be a regular expression.

### Using a predicate for object creation

In this case, the predicate condition covers any invocation of the `db.Database` constructor. In other
words, any time a new instance of that class is created, we want to do something special.
In this case, we create a visual representation of the database and show
three metrics to track operations happening on the instance.

``` python
@feynman.on("db.Database.__init__")
def createDatabase(self, name):
    database(name, 0, 20, 100, 170)
    feynman.text("read: 0", 120, 30, id=f"{name}-read", group=name)
    feynman.text("write: 0", 120, 50, id=f"{name}-write", group=name)
    feynman.text("size: 0", 120, 70, id=f"{name}-size", group=name)
```

The instances are rendered using a helper function called `database`. That
helper method can come from anywhere and can be imported from another
module, of course. For our example, it is declared in the same `explain` module.

### Using a helper functions

The helper function introduces a new group of drawing primitives. The group itself
is added to another group to render all databases close to each other. Groups can
be moved by the user, to customize the resulting drawing.

``` python
def database(name, x, y, w, h):
    feynman.group(name, x, y, group="databases", children=[
        feynman.rectangle(0, h/10, w, 6*h/10),
        feynman.oval(0, 0, w, h/5),
        feynman.oval(0, 3*h/5, w, h/5),
        feynman.rectangle(2, 6*h/10, w, h/10, border=""),
        feynman.text(name, 2, 3*h/8, w, 24, "center"),
    ])
    feynman.run(f"addDatabase('{name}')")
```

This rule takes care of the static aspects of the database. We will see it when
it gets created. But, we are really interested in its dynamic behavior. How
often do we read and write to it? In other words, can we render its state
to help us understand how it works?

### Showing application state

To show the dynamic behavior of the database, we define declarative visualization 
rules for `read`, `write`, and `delete`, so
that we can show some statistices for each of the two databases we are visualizing.
Below is the rule for `read`. It uses `feynman.update`, that uses three arguments:
`id`, `name`, and `value`. It finds the correct DOM node in the drawing.
Then it updates its property or CSS attribute with the provided value.

``` python
@feynman.on("db.Database.read")
def read(self, key):
    id = f"{self.name}-read"
    name = "text"
    value = f"read: {increment_count(self.name, 'read')}")
    feynman.update(id, name, value)
```

### Declaring custom HTML and JavaScript

Custom html, css, and javascript can be loaded as follows:
``` python
feynman.html("explain.html")
feynman.css("explain.css")
feynman.run("explain.js")
```

In our database example, the `explain.js` is interesting as it introduces a
temperature gauge that animates the state of the database. It shows how
active the database is. 

Functions declared in JavaScript can be called from Feynman scripts
using the `run` function:

``` python
    feynman.run(f"busy('{self.name}')")
```

The JavaScript function we call in this manner uses jQuery, but that is not
required. However, JQuery makes it easy to construct dynamic visualizations
such as Feynman creates.

### Finding out what predicates to use

To discover the names of the fully qualified functions or methods of interest,
run the `feynman.trace` utility. The `ping` example above uses it as follows:

``` python
feynman.trace("ping")
```

This results in all calls for functions declared in the `ping` module to be
traced and the corresponding predicate to be shown when it is discovered the first time:

``` python
@feynman.on("ping.callService")
def callService(url):
   pass

@feynman.on("ping.getDetails")
def getDetails(location):
   pass

@feynman.on("ping.getLocation")
def getLocation(ip):
   pass
```

You can then simply cut and paste them into your `explain.py` and turn off the trace again.

### Combining it all

Finally, we run the original example by calling its `main`:

``` python
print("running test/db.py with Feynman.Explain...")
when = time.time()
with feynman.Explain():
    import db
    db.main()
    print("Ran for", time.time() - when, "seconds")
```

The end result is that the `db` module runs the same as before. 
However, `explain.py` now draws the program state, while `test/db.py` is running, in an easy to understand diagram:

| ![A Feynman animation of test/db.py showing how data is moved between two databases](images/example.gif?raw=true "Title") |
| --- |

## An Example - Creating a Metrics Dashboard

The code in [test/ping.py](test/ping.py) checks the health of a number of websites from around the world. It also tries to guess 
what location the server is based in. It then generates a table
with metrics, resembling this:

```
Locations:
--------------------------------------------------------------------------------
localhost            0.0s  Netherlands
rtlz.nl              0.2s  Netherlands
nos.nl               0.1s  United States
reddit.com           1.8s  United States
chrislaffra.com      0.5s  United States
microsoft.com        0.8s  United States
google.com           0.2s  United States
apple.com            0.2s  United States
mozilla.org          0.9s  United States
wordpress.org        0.8s  United States
en.wikipedia.org     0.2s  Netherlands
linkedin.com         0.9s  United States
vimeo.com            0.3s  United States
youtu.be             0.9s  United States
github.com           0.2s  United States
cnn.com              0.3s  United States
paypal.com           0.8s  United States
cnet.com             0.6s  United States
dropbox.com          1.0s  United States
wikimedia.org        0.1s  Netherlands
web.whatsapp.com     0.1s  Ireland
happymac.app         0.8s  United States
twitch.tv            0.2s  United States
twitter.com          0.6s  United States
--------------------------------------------------------------------------------
```

Of course, localhost connections are really fast. Some sites take
a lot longer than others. However, from the table it is not easy to detect the anomalies in a quick scan. 

However, the metrics can easily be converted to color ranges and shown in a dashboard style, as shown in [test/explain/ping/explain.py](ping/explain.py). The outliers stick out immediately:

![A Feynman animation of ping.py showing ping times](images/dashboard.png)

## Implementation

Feynman is a profiler. It uses `sys.setprofile` to detect the
enter and leave of **every** function call in your Python
program. This makes Feynman about 4X slower than the regular execution.

Feynman worries about its own overhead a lot. The predicates
are evaluated in the same process as the original program.
Feynman opens a websocket server port. It sends
visualization constructs and state updates to that socket.
State updates are buffered and sent at regular interval to 
avoid clogging the socket.

The ui is an HTML page that runs in a browser window. It opens
a socket to the locally running process and starts handling
visualization requests.

## Earlier work

Feynman is inspired by a number of similar projects developed by [Chris Laffra](https://chrislaffra.com). Here are some examples
- [Hotwire](https://www.usenix.org/conference/usenix-6th-c-technical-conference/presentation/hotwire-visual-debugger-c), the closest to project Feynman, to visualize C++ and Smalltalk programs, 1993
- [XRay](https://www.slideshare.net/chrislaffra/eclipse-visualization-and-performance-monitoring), hardwired visualization for Java programs, such as Eclipse, 2003
- [QzAcademy](https://www.slideshare.net/chrislaffra/livecode-python-training-tools-at-bank-of-america), a time travel debugger for the Quartz project, written in Python, 2008
- [PyAlgoViz](https://pyalgoviz.appspot.com), visualization of about 50 algorithms, using a DSL to visualize the internal state at each line of the Python scripts, 2010
- [Cacophonia](https://www.slideshare.net/chrislaffra/project-cacophonia), graph-based visualization of Eclipse, as a Java program, 2021
- [Pynsights](https://github.com/laffra/pynsights), graph visualization of Python modules, 2021

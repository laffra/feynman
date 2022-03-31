const MILLISECONDS = 1000;
const REPLAY_FLUSH_INTERVAL = 0.01;

var start = 0;
var end = 0;
var events = [];
var drawing = $(".drawing");

function findOrCreate(id, kind) {
    if ($("#" + id).length) return $("#" + id);
    return $("<" + kind + ">")
        .attr("id", id)
        .addClass("feynman-node")
        .addClass("feynman-" + kind)
        .appendTo(drawing);
}

function update(node, key, value) {
    if (key.match(/^(id|kind)$/)) return;
    switch (node.prop("tagName")) {
        case "LINE":
            self.updateLine(node, key, value);
            break;
    }
    try {
        node.css(key, value);
        node.attr(key, value);
        node[key](value); 
    } catch(e) {
    }
}

function moveToLastPosition(node) {
    const key = "pos-" + node.attr("id");
    const lastPosition = window.localStorage.getItem(key);
    if (!lastPosition) return;
    const [left, top, width, height] = lastPosition.split(' ');
    console.log("move", key, lastPosition)
    node.css({ left, top, width, height });
}

window.saveLastPosition = (node) => {
    const key = "pos-" + node.attr("id");
    const lastPosition = [
        node.css("left"),
        node.css("top"),
        node.width() + "px",
        node.height() + "px",
    ].join(" ")
    console.log("save", key, lastPosition)
    window.localStorage.setItem(key, lastPosition);
}

window.makeDraggable = (node) => {
    node.draggable({
        drag: () => saveLastPosition(node),
        containment: 'parent',
    }).resizable({
        resize: () => saveLastPosition(node),
        handles: "n, e, s, w"
    });
    moveToLastPosition(node);
}

function clearDrawing() {
    drawing
        .empty()
        .css("opacity", 1.0);
    $("#timeline")
        .slider({ 
            max: (end - start) * MILLISECONDS,
            value: 0,
        });
}

function updateLine(node, name, value) {
    node.attr(name, value);
    var x1 = node.attr("x1");
    var y1 = node.attr("y1");
    var x2 = node.attr("x2");
    var y2 = node.attr("y2");
    if (x1 == null || y1 == null || x2 == null || y2 == null) return;
    if (x2 < x1) {
        [x1, y1, x2, y2] = [x2, y2, x1, y1];
    }
    const length = Math.sqrt((x1-x2)*(x1-x2) + (y1-y2)*(y1-y2));
    const angle = Math.atan((y2-y1)/(x2-x1));
    node.css({
        left: parseFloat(x1) - 0.5*length*(1 - Math.cos(angle)),
        top: parseFloat(y1) + 0.5*length*Math.sin(angle),
        width: length,
        backgroundColor: node.attr("color") || "black",
        height: node.attr("stroke") || 2,
        WebkitTransform: "rotate(" + angle + "rad)",
    })
}

function replayEvent(index, stopWhen) {
    if (index >= events.length) return;
    var whenStart = events[index].when;
    for (;index < events.length; index++) {
        const when = events[index].when;
        if (stopWhen && when >= stopWhen) return;
        if (!stopWhen && when - whenStart > REPLAY_FLUSH_INTERVAL) {
            const ms = (when - whenStart) * MILLISECONDS;
            setTimeout(() => replayEvent(index, stopWhen), ms);
            break;
        }
        handleEvent(events[index]);
    }
}

function updateTimeline(event) {
    start = start || event.when;
    end = Math.max(end, event.when);
    when = event.when - start
    $("#timeline")
        .slider({ 
            min: 0,
            max: (end - start) * MILLISECONDS + (end == event.when ? MILLISECONDS : 0),
            value: when * MILLISECONDS
        });
    $("#timestamp")
        .text("@" + when.toFixed(1) + "s");
}

function assert(ok, message) {
    if (ok) return;
    error(message);
}

function error(message) {
    console.log("ERROR", message)
    $("<error>").text(message).appendTo($("body"));
}

function handleEvent(event) {
    // console.log("###", event.kind, JSON.stringify(event))
    switch (event.kind) {
        case "css":
            $('head').append('<style type="text/css">' + event.text + '</style>');
            break;
        case "run":
            try {
                eval(event.text);
            } catch(e) {
                error("Cannot run '" + event.text + "': " + e)
            }
            break;
        case "html":
            drawing.append($(event.html));
            break;
        case "info":
            break;
        case "update":
            const nodeToUpdate = $("#"+event.id);
            assert(nodeToUpdate.length, "Missing id: " + event.id);
            update(nodeToUpdate, event.name, event.value);
            break;
        default:
            const node = findOrCreate(event.id, event.kind);
            for (const key in event) {
                update(node, key, event[key])
            }
            if (event.group) {
                $("#" + event.group).append(node);
            }
    }
    updateTimeline(event);
};

$("#timeline").slider({
    stop: function( event, ui ) {
        const when = ui.value / 1000;
        replayEvent(0, start + when);
    },
});

function run() {
    drawing.css({ opacity: 1 });
    clearDrawing();
    replayEvent(0);
}

$("#run").on("click", function() {
    drawing.animate({ opacity: 0 }, run);
});

const ws = new WebSocket("ws://127.0.0.1:5678/");
ws.onmessage = function (message) {
    const event = JSON.parse(message.data);
    events.push(event);
    handleEvent(event);
}
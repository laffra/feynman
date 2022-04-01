// This is loaded using feynman.js(...) 

// JQuery and JQuery UI are available, but are not mandatory for using Feynman.


window.databases = [];
window.dbContainer = $('#databases');
window.colors = [ "pink", "lightyellow", "lightgreen", "lightblue", "white" ];

window.scaleDatabases = () => {
    const scale = dbContainer.width() / databases.length / 300;
    console.log("resize", scale, dbContainer.width(), databases.length)
    $(".database").css("-webkit-transform", () => "scale(" + scale + ")");
}

makeDraggable(dbContainer);
dbContainer.resizable({ resize: scaleDatabases });


window.get_color = () => {
    colors.push(colors.shift())
    return colors[0];
}

window.addDatabase = name => {
    const database = $('#' + name);
    const color = get_color();
    database
        .addClass("database")
        .css('left', 20 + databases.length * 300)
        .append(
            $("<group>")
                .attr("id", name + "-status")
                .addClass("db-status")
                .append(
                    $("<div>")
                        .attr("id", name + "-statusbar")
                        .addClass("db-statusbar")
                )
        )
        .find('rectangle,oval')
        .css('background-color', color)
    moveToLastPosition(database);
    databases.push(name);
    $('#databases')
        .css('width', Math.max($('#databases').width(), 270 * databases.length));
    setInterval(() => {
        const bar = $("#" + name + "-statusbar");
        bar.css("width", Math.max(0, bar.width() - 10));
    }, 100)
    scaleDatabases();
}

window.busy = name => {
    const bar = $("#" + name + "-statusbar");
    bar.css("width", Math.min(76, bar.width() + 20));
}
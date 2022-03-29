// Feynman automatically loads this script at load time. 

// JQuery and JQuery UI are available, but are not mandatory for using Feynman.

$('#databases').draggable();

window.databases = [];
window.colors = [ "pink", "lightyellow", "lightgreen", "lightblue", "white" ];

window.get_color = () => {
    colors.push(colors.shift())
    return colors[0];
}

window.addDatabase = name => {
    const database = $('#' + name);
    const color = get_color();
    database
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
    databases.push(name);
    $('#databases')
        .css('width', 270 * databases.length);
    setInterval(() => {
        const bar = $("#" + name + "-statusbar");
        bar.css("width", Math.max(0, bar.width() - 10));
    }, 100)
}

window.busy = name => {
    const bar = $("#" + name + "-statusbar");
    bar.css("width", Math.min(80, bar.width() + 20));
}
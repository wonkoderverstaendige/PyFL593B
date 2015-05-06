$(document).ready(function () {
    if (!window.console) window.console = {};
    if (!window.console.log) window.console.log = function() {};

    $('.modal-trigger').leanModal();

    $('#REN').click(function () {
        var new_status = $('#REN').hasClass("green") ? 0 : 1;
        socket_updater.send('{"command": "status write enable '+new_status+'"}');
    });

    $('.slider').noUiSlider({
        start: [ 0 ],
        margin: 20,
        connect: "lower",
        direction: "rtl",
        orientation: "vertical",
        behaviour: 'snap',
        range: {
            'min': 0,
            'max': 250
        },
    });

    $('.prog').noUiSlider({
        behaviour: 'none',
    }, true);

    $(".slider").noUiSlider_pips({
        mode: 'positions',
        values: [0, 20, 40, 60, 80, 100],
        density: 5
    });

    var channels = ['LD1', 'LD2'];
    var spinner = ['setpoint', 'limit'];
    var labels = ['imon', 'pmon'];
    for (chidx=0; chidx < channels.length; chidx++) {
        var channel = $(".channel"+channels[chidx]);
        for (spinidx=0; spinidx < spinner.length; spinidx++) {
            channel.find('.slider.'+spinner[spinidx]).Link('lower').to(channel.find(".spinner."+spinner[spinidx]), null, wNumb({
                decimals: 0
            }));
        }
    }

});
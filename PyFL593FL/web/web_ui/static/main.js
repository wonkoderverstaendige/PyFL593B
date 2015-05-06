$(document).ready(function(){
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
        format: wNumb({
            decimals: 1,
            postfix: 'mA'
        })
    });

//    $("#slider-format").Link('lower').to($('#input-format'));

    $('.slider').on({
        slide: function() {
            if ($(this).hasClass("setpoint")) {
               op_type = "setpoint";
            } else if ($(this).hasClass("limit")){
               op_type = "limit";
            } else {
                Materialize.toast("Unknown slider type", 3000);
            }
            var ch = $(this).hasClass("channelLD1") ? "LD1" : "LD2";
            var value = parseFloat($(this).val())/1000.0;
            socket_updater.send('{"command": "'+ch+' write '+op_type+' '+value.toFixed(3)+'"}');
            $(this).addClass('user-active');
            setTimeout(function() {
                $(this).removeClass('user-active');
            }, 100);
        }
    });

    $('.prog').noUiSlider({
        behaviour: 'none',
    }, true);

    $(".slider").noUiSlider_pips({
        mode: 'positions',
        values: [0, 20, 40, 60, 80, 100],
        density: 5
    });
    
    $("#commandform").submit(function() {
        newMessage($(this));
        return false;
    });
    
    $("#commandform").keypress(function(e) {
        if (e.which == 13) {
            $(this).submit();
            return false;
        }
    });
    
    socket_updater.start();

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
        for (lblidx=0; lblidx < labels.length; lblidx++) {
            channel.find('.prog.'+labels[lblidx]).Link('lower').to(channel.find(".label."+labels[lblidx]), null, wNumb({
                decimals: 1,
                postfix: " mA"
            }));
        }
    }
});

function newMessage(form) {
    var message = form.formToDict();
    var stringified = JSON.stringify(message);
    socket_updater.send(stringified);
    $('#command').val("").select();
}

jQuery.fn.formToDict = function() {
    var fields = this.serializeArray();
    var json = {}
    for (var i = 0; i < fields.length; i++) {
        json[fields[i].name] = fields[i].value;
    }
    if (json.next) delete json.next;
    return json;
};

var socket_updater = {
    socket: null,
    alarms: ["#OUT", "#XEN", "#LEN", "#REN"],
    url: "ws://" + location.host + "/chatsocket",
    iv: null,

    start: function() {
        socket_updater.socket = new WebSocket(this.url);

        socket_updater.socket.onclose = function() {
        window.clearInterval(socket_updater.iv)
            Materialize.toast("Connection failed", 3000);
            socket_updater.toggleConnectionState(false);
            setTimeout(function() {
                socket_updater.start();
            }, 1000);
        };

        socket_updater.socket.onopen = function() {
            socket_updater.iv = setInterval(onTimerTick, 50); // 20Hz update rate ought to be enough for starters
            //console.log(socket_updater.socket);
            Materialize.toast("Connection established", 3000);
            socket_updater.toggleConnectionState(true);
        };

        socket_updater.socket.onmessage = function(event) {
            socket_updater.parseMessage(JSON.parse(event.data));
        };

        socket_updater.socket.onerror = function(e) {
            console.log(e);
        };

    },

    parseMessage: function(message) {
        var response = message.response;
        if (response.end_code) {
            console.log(response);
            Materialize.toast("ERROR: " + response.end_code, 3000);
        }
        // Check op_type
        // If write, do nothing and wait for update
        if (response.op_type == 0x02) return;

        // If read, update the corresponding element. Not elegant, but straight forward.
        switch(response.op_code) {
            case 0x00: // Model -> Device
                break;
            case 0x01: // Serial -> Device
                break;
            case 0x02: // firmware version -> Device
                break;
            case 0x03: // device type -> Device
                break;
            case 0x04: // channel count -> Device, main control tab
                break;
            case 0x05: // identify -> UNUSED
                break;
            case 0x0C: // save -> UNUSED
                break;
            case 0x0D: // recall -> UNUSED
                break;
            case 0x0E: // password -> UNUSED
                break;
            case 0x0F: // revert -> UNUSED
                break;
            case 0x10: // alarms -> Buttons side panel
                flags = response.data.trim();
                for (var idx=0; idx < socket_updater.alarms.length; idx++) {
                    toggleBtn(socket_updater.alarms[idx], response.data[idx] == "1");
                }
                break;
            case 0x11: // setpoint -> LD1/LD2
                updateSlider($(".channelLD"+response.channel).find('.slider.setpoint'), parseFloat(response.data)*1000);
                break;
            case 0x12: // limit -> LD1/LD2
                updateSlider($(".channelLD"+response.channel).find('.slider.limit'), parseFloat(response.data)*1000);
                break;
            case 0x13: // mode -> LD1/LD2, CC or CP
                break;
            case 0x14: // track -> main control tab channel count, LD1 slider range
                break;
            case 0x15: // imon, LD1/LD2
                updateSlider($(".channelLD"+response.channel).find('.slider.imon'), parseFloat(response.data)*1000);
                break;
            case 0x16: // pmon, LD1/LD2
                updateSlider($(".channelLD"+response.channel).find('.slider.pmon'), parseFloat(response.data)*1000);
                break;
            case 0x17: // enable, LD1/LD2
                break;
            case 0x19: // feedback diode resistor -> UNUSED
                break;
            case 0xE2: // iscale -> UNUSED
                break;
            default:
                Materialize.toast("Unknown op_code: "+response.op_code, 3000);
        }
    },

    send: function(msg) {
        if (socket_updater.socket.readyState) socket_updater.socket.send(msg);
    },

    toggleConnectionState: function (state) {
        // if the socket is not alive, disable all the things!
        if (state) {
            $("#REN").removeClass("disabled");
            for (var idx=0; idx < this.alarms.length; idx++) {
                $(socket_updater.alarms[idx]).removeClass("grey");
            }

        } else {
            $("#REN").addClass("disabled");
            for (var idx=0; idx < socket_updater.alarms.length; idx++) {
                $(socket_updater.alarms[idx]).addClass("grey");
            }
        }
    }
};

function updateSlider(slider, value) {
    if (slider.hasClass("user-active")) return;
    if (parseFloat(slider.val()) != value) {
        slider.val(value);
    }
};

function onTimerTick() {
    var status = ["alarm"];
    var ld = ["setpoint", "limit", "imon", "pmon"];
    for (var idx = 0; idx < status.length; idx++) {
        socket_updater.send('{"command": "status read '+status[idx]+'"}');
        }

    for (var ch = 1; ch <= 2; ch++) {
        for (var idx = 0; idx < ld.length; idx++) {
            socket_updater.send('{"command": "LD'+ch+' read '+ld[idx]+'"}');
        }
    }

};

function toggleEnable (element) {
	$(element).toggleClass("red");
	$(element).children().toggleClass('mdi-content-clear');
	$(element).toggleClass("green");
	$(element).children().toggleClass('mdi-action-done');
};

function toggleBtn (element, state) {
	if (state) {
        $(element).addClass("green");
        $(element).children().addClass('mdi-action-done');
        $(element).removeClass("red");
        $(element).children().removeClass('mdi-content-clear');
	} else {
        $(element).removeClass("green");
        $(element).children().removeClass('mdi-action-done');
        $(element).addClass("red");
        $(element).children().addClass('mdi-content-clear');
	}

};
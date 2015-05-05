$(document).ready(function(){
    if (!window.console) window.console = {};
    if (!window.console.log) window.console.log = function() {};
    
    $('.modal-trigger').leanModal();
    
    $('#REN').click(function () {
		toggleEnable(this);
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
    setInterval(onTimerTick, 1000); // 20Hz update rate ought to be enough for starters
});

function newMessage(form) {
    var message = form.formToDict();
    var stringified = JSON.stringify(message);
    socket_updater.socket.send(stringified);
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

var socket_updater= {
    socket: null,

    start: function() {
        var url = "ws://" + location.host + "/chatsocket";
        socket_updater.socket = new WebSocket(url);
        socket_updater.socket.onmessage = function(event) {
            socket_updater.parseMessage(JSON.parse(event.data));
        }
    },

    parseMessage: function(message) {
        var response = message.response;
        if (response.end_code) {
            console.log(response);
            Materialize.toast("ERROR: " + response.string, 3000);
        }
        // Check op_type
        // If write, just check the end_code. If not 0, throw a toast warning
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
                var alarms = ["#OUT", "#XEN", "#LEN", "#REN"];
                flags = response.data.trim();
                for (var idx=0; idx < alarms.length; idx++) {
                    toggleBtn(alarms[idx], response.data[idx] == "1");
                }
                break;
            case 0x11: // setpoint -> LD1/LD2
                updateSlider(".channelLD"+response.channel+" #setpoint", parseFloat(response.data));
                break;
            case 0x12: // limit -> LD1/LD2
                updateSlider(".channelLD"+response.channel+" #limit", parseFloat(response.data));
                break;
            case 0x13: // mode -> LD1/LD2, CC or CP
                break;
            case 0x14: // track -> main control tab channel count, LD1 slider range
                break;
            case 0x15: // imon, LD1/LD2
                updateSlider(".channelLD"+response.channel+" #imon", parseFloat(response.data));
                break;
            case 0x16: // pmon, LD1/LD2
                updateSlider(".channelLD"+response.channel+" #pmon", parseFloat(response.data));
                break;
            case 0x17: // enable, LD1/LD2
                break;
            case 0x19: // feedback diode resistor -> UNUSED
                break;
            case 0xE2: // iscale -> UNUSED
                break;
            default:
                Materialize.toast("Unknown op_code", 1000);
        }
    }
};

function updateSlider(slider, value) {
//    console.log($(slider).val())
//    console.log(value)
    if (parseFloat($(slider).val()) != value) {
        $(slider).val(value);
    }
};

function onTimerTick() {
    var status = ["alarm"];
    var ld = ["setpoint", "limit", "imon", "pmon"];
    for (var idx = 0; idx < status.length; idx++) {
        socket_updater.socket.send('{"command": "status read '+status[idx]+'"}');
        }

    for (var ch = 1; ch <= 2; ch++) {
        for (var idx = 0; idx < ld.length; idx++) {
            socket_updater.socket.send('{"command": "LD'+ch+' read '+ld[idx]+'"}');
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
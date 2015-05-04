$(document).ready(function(){
    if (!window.console) window.console = {};
    if (!window.console.log) window.console.log = function() {};
    
    $('.modal-trigger').leanModal();
    
    $('#REN').click(function () {
		toggleEnable(this);
    });
    
    $('.slider').noUiSlider({
        start: [ 50 ],
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
    
    updater.start();
});

function newMessage(form) {
    var message = form.formToDict();
    var stringified = JSON.stringify(message); //updater.socket.send()
    updater.socket.send(stringified);
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

var updater = {
    socket: null,

    start: function() {
        var url = "ws://" + location.host + "/chatsocket";
        updater.socket = new WebSocket(url);
        updater.socket.onmessage = function(event) {
            updater.parseMessage(JSON.parse(event.data));
        }
    },

    parseMessage: function(message) {
        console.log(message);
        Materialize.toast(message.response.data, 5000);
        switch(message.response.op_code) {
            case 0:
                break;
            case 1:
                break;
            case 2:
                break;
            case 3:
                break;
            default:
                break;
        }
    }
};

var toggleEnable = function (element) {
	$(element).toggleClass("red");
	$(element).children().toggleClass('mdi-content-clear');
	$(element).toggleClass("green");
	$(element).children().toggleClass('mdi-action-done');
};

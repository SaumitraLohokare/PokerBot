/*
 *  Register callback functions on buttons.
 */
$(document).ready(function() {
    if (!window.console) window.console = {};
    if (!window.console.log) window.console.log = function() {};

    $("#registration_form").on("submit", function(e) {
        e.preventDefault();
        registerPlayer($(this));
    });
    
    $("#start_game_form").on("submit", function(e) {
        e.preventDefault();
        startGame();
    });

    $("#pause_button").on("click", function() {
        togglePause();
    });
  
    updater.start();
});

/*
 *  Callback function invoked when
 *  human player is registered.
 */
function registerPlayer(form) {
    var message = form.formToDict();
    message['type'] = "action_new_member"
    message['name'] = message['body']
    delete message.body
    updater.socket.send(JSON.stringify(message));
}

/*
 * Callback function invoked when
 * game is starged.
 */
function startGame() {
    message = {}
    message['type'] = "action_start_game"
    updater.socket.send(JSON.stringify(message));
}

/*
 * Callback function invoked when
 * human player declared his action in the game.
 */
function declareAction(form) {
  var message = form.formToDict();
  message['type'] = "action_declare_action"
  updater.socket.send(JSON.stringify(message))
}

/*
 * Helper function to get form information as hash.
 */
jQuery.fn.formToDict = function() {
    var fields = this.serializeArray();
    var json = {}
    for (var i = 0; i < fields.length; i++) {
        json[fields[i].name] = fields[i].value;
    }
    if (json.next) delete json.next;
    return json;
};

/*
 *  This object setups and holds websocket.
 */
var updater = {
    socket: null,

    /*
     *  This method is invoked when index page is opened.
     *  Setup websocket and register callback method on it.
     *  URL would be "ws://localhost/pokersocket:8888".
     */
    start: function() {
        var scheme = location.protocol === "https:" ? "wss://" : "ws://";
        var url = scheme + location.host + "/pokersocket";
        console.log("Connecting to WebSocket at: " + url);
        updater.socket = new WebSocket(url);
        updater.socket.onmessage = function(event) {
            var message = JSON.parse(event.data);
            console.log("Received message:", message);
            
            if (message.message_type === 'game_state_update') {
                console.log("Game state update:", message.is_paused);
                if (message.is_paused) {
                    $("#pause_button").text("Resume Game").removeClass("btn-warning").addClass("btn-success");
                    $("#declare_action_form").hide();
                } else {
                    $("#pause_button").text("Pause Game").removeClass("btn-success").addClass("btn-warning");
                    if (isPlayerTurn()) {
                        $("#declare_action_form").show();
                    }
                }
            } else if ('config_update' == message['message_type']) {
              updater.updateConfig(message)
            } else if ('start_game' == message['message_type']) {
              updater.startGame(message)
            } else if ('update_game' == message['message_type']) {
              updater.updateGame(message)
            } else if ('alert_restart_server' == message['message_type']) {
              updater.alert_restart_server(message)
            } else {
              console.error("Unexpected message:", message)
            }
        }
    },

    /*
     * Invoked when received the new message
     * about update of config like new member is registered.
     */
    updateConfig: function(message) {
        var node = $(message.html);
        $("#config_box").html(node)
        if (message.registered) {
          $("#registration_form input[type=submit]").prop("disabled", true);
        }
    },

    /*
     * Invoked when received the message
     * about start of the game.
     */
    startGame: function(message) {
      var node = $(message.html)
      $("#container").html(node)
      $("#declare_action_form").hide()
      $("#declare_action_form").on("submit", function() {
        declareAction($(this));
        return false;
      });
    },

    /*
     * Invoked when received the message about
     * new event of the game like "new round will start".
     */
    updateGame: function(message) {
        $("#declare_action_form").hide()
        content = message['content']
        window.console.log("updateGame: " + JSON.stringify(content))
        message_type = content['update_type']
        window.console.log("event html : " + JSON.stringify(content.event_html))
        if ('round_start_message' == message_type) {
          updater.roundStart(content.event_html)
        } else if ('street_start_message' == message_type) {
          updater.newStreet(content.table_html, content.event_html)
        } else if ('game_update_message' == message_type) {
          updater.newAction(content.table_html, content.event_html)
       } else if ('round_result_message' == message_type) {
         updater.roundResult(content.table_html, content.event_html)
       } else if ('game_result_message' == message_type) {
         updater.gameResult(content.event_html)
       } else if ('ask_message' == message_type) {
         $("#declare_action_form").show()
         updater.askAction(content.table_html, content.event_html)
       } else {
          window.console.error("unexpected message in updateGame: " + content)
       }
    },

    roundStart: function(event_html) {
      $("#event_box").html($(event_html))
    },

    newStreet: function(table_html, event_html) {
      $("#table").html($(table_html))
      $("#event_box").html($(event_html))
    },

    newAction: function(table_html, event_html) {
      $("#table").html($(table_html))
      $("#event_box").html($(event_html))
    },

    roundResult: function(table_html, event_html) {
      $("#table").html($(table_html))
      $("#event_box").html($(event_html))
    },

    gameResult: function(event_html) {
      $("#event_box").html($(event_html))
    },

    askAction: function(table_html, event_html) {
      $("#table").html($(table_html))
      $("#event_box").html($(event_html))
    },

    alert_restart_server: function(message) {
      alert(message.message)
    },

    togglePause: function() {
        var message = {
            'type': "action_toggle_pause"
        };
        updater.socket.send(JSON.stringify(message));
    }

};

function isPlayerTurn() {
    // This is a placeholder - you'll need to implement the actual logic
    // based on your game state
    return $("#declare_action_form").is(":visible");
}


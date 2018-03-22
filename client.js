if (window.WebSocket) {

    function DonatedRaffleUi(apiKey) {
        this.apiKey = apiKey;
        this.reconnectInterval = 5000;
        this.serviceUrl = "ws://127.0.0.1:3337/AnkhBot";
        this.socket = null;

        this.initialize();
    }

    DonatedRaffleUi.events = {
        OPEN: "DONATEDRAFFLE_OPEN",
        CLOSE: "DONATEDRAFFLE_CLOSE",
        WINNER: "DONATEDRAFFLE_WINNER",
        ENTER: "DONATEDRAFFLE_ENTER",
        DONATE: "DONATEDRAFFLE_DONATE"
    };

    DonatedRaffleUi.prototype = {
        initialize: function () {
            this.connect();
        },

        connect: function () {
            var that = this;
            console.log(that);
            this.socket = new WebSocket(that.serviceUrl);
            this.socket.onclose = function (ev) {
                console.info('Connection closed');
                setTimeout(that.connect, this.reconnectInterval);
            },
            this.socket.onopen = function (evt) {
                var auth = {
                    author: "BleepBlamBleep",
                    website: "https://github.com/bap14/Streamlabs_DonatedRaffle",
                    api_key: this.apiKey,
                    events: Object.keys(DonatedRaffleUi.events)
                };
                that.socket.send(JSON.stringify(auth));
                console.log('connected');
            };
            this.socket.onerror = function (evt) {
                console.error(evt);
            };
            this.socket.onmessage = function (evt) {
                var message = JSON.parse(evt.data);

                if (message.event === DonatedRaffleUi.events.OPEN) {
                    console.log('Raffle Opened!');
                }
                else if (message.event === DonatedRaffleUi.events.CLOSE) {
                    console.log("Raffle Closed!");
                }
                else if (message.event === DonatedRaffleUi.events.WINNER) {
                    console.log(message.data);
                    console.log('And the winner is: "' + message.data.winner + '"');
                }
                else if (message.event === DonatedRaffleUi.events.ENTER) {
                    console.log('"' + message.data.user + '" just entered with ' + message.data.numEntries);
                }
                else if (message.event === DonatedRaffleUi.events.DONATE) {
                    console.log('"' + message.data.donatee + '" was given ' + message.data.numEntries + ' entries ' +
                        'thanks to "' + message.data.donator + '".  Thank you!');
                }
            };
        }
    };

    new DonatedRaffleUi(API_Key);
}
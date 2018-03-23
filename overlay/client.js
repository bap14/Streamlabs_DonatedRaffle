/*global $ */
"use strict";

function DonatedRaffleUi(apiKey) {
    this.apiKey = apiKey;
    this.reconnectInterval = 10000;
    this.serviceUrl = "ws://127.0.0.1:3337/streamlabs";
    this.settings = settings;
    this.socket = null;

    this.initialize();
}

DonatedRaffleUi.events = {
    OPEN: "DONATEDRAFFLE_OPEN",
    CLOSE: "DONATEDRAFFLE_CLOSE",
    WINNER: "DONATEDRAFFLE_WINNER",
    ENTER: "DONATEDRAFFLE_ENTER",
    DONATE: "DONATEDRAFFLE_DONATE",
    UPDATE_SETTINGS: "DONATEDRAFFLE_UPDATE_SETTINGS"
};

DonatedRaffleUi.prototype = {
    initialize: function () {
        $('#stage > h1').hide();
        $('#stage > ul').hide();
        this.connect();
    },

    connect: function () {
        var that = this;
        this.socket = new WebSocket(that.serviceUrl);
        this.socket.onclose = function (evt) {
            setTimeout(jQuery.proxy(that.connect, that), that.reconnectInterval);
        },
        this.socket.onopen = function (evt) {
            var auth = {
                author: "BleepBlamBleep",
                website: "https://bap14.github.io/Streamlabs_DonatedRaffle",
                api_key: that.apiKey,
                events: Object.values(DonatedRaffleUi.events)
            };
            that.socket.send(JSON.stringify(auth));
        };
        this.socket.onerror = function (evt) {
            console.error(evt);
        };
        this.socket.onmessage = function (evt) {
            var message = JSON.parse(evt.data);
            if (message.hasOwnProperty('data') && typeof message.data === "string") {
                message.data = JSON.parse(message.data);
            }
            else {
                message.data = {};
            }

            if (message.event === DonatedRaffleUi.events.OPEN) {
                that.raffleOpened(message.data);
            }
            else if (message.event === DonatedRaffleUi.events.CLOSE) {
                that.raffleClosed();
            }
            else if (message.event === DonatedRaffleUi.events.WINNER) {
                that.winnerChosen(message.data);
            }
            else if (message.event === DonatedRaffleUi.events.ENTER) {
                that.userEntered(message.data);
            }
            else if (message.event === DonatedRaffleUi.events.DONATE) {
                that.userDonated(message.data);
            }
            else if (message.event === DonatedRaffleUi.UPDATE_SETTINGS) {
                that.updateSettings(message.data);
            }
        };
    },

    makeItRain: function () {
        var bill,
            billCount = 25,
            delayTime,
            layer = 0,
            leftPosition = 0,
            n = 0,
            randSeed = $(window).width(),
            speed,
            topPosition = -150;

        for (n; n < billCount; n++) {
            leftPosition = Math.floor(randSeed * Math.random());
            delayTime = Math.random() * 20;
            speed = (Math.random() * 10);

            bill = $('<figure class="raining-currency">').css({
                left: leftPosition + 'px',
                top: topPosition + 'px',
                animationDelay: delayTime + 's',
                animationDuration: speed + 's',
                zIndex: layer,
                width: '50px'
            });
            $(bill).prepend('<img src="images/currency.svg" alt="Stream Currency">');
            $('#stage > .background').append(bill);
        }
        setTimeout(function () { $('#stage > .background').html(''); }, 15000);
    },

    raffleOpened: function () {
        console.info('Raffle Opened!');
    },
    raffleClosed: function () {
        console.info('Raffle Closed!');
    },
    winnerChosen: function (data) {
        console.log('And the winner is: "' + data.winner + '"');
        if (this.settings.IsCurrencyGiveaway && parseInt(this.settings.CurrencyGiveawayAmount) > 0) {
            this.makeItRain();
        }
    },
    userEntered: function (data) {
        console.log('"' + data.user + '" just entered with ' + data.entries);
    },
    userDonated: function (data) {
        console.log('"' + data.donatee + '" was given ' + data.entries + ' entries ' +
                    'thanks to "' + data.donator + '".  Thank you!');
    },

    updateSettings: function (settings) {
        this.settings = settings;
        console.log('Updated Settings');
        console.log(this.settings);
    }
};

if (window.WebSocket) {
    new DonatedRaffleUi(API_Key);
}
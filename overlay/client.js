/*global $ */
"use strict";

function DonatedRaffleUi(apiKey) {
    this.apiKey = apiKey;
    this.reconnectInterval = 10000;
    this.serviceUrl = "ws://127.0.0.1:3337/streamlabs";
    this.settings = settings;
    this.socket = null;
    this.winners = [];
    this.winnerInterval = null;

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

    hideRaffleTitle: function () {
        if ($('#title')) {
            $('#title').fadeOut(500).html('');
        }
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
            speed = (Math.random() * 5);

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
    raffleOpened: function (data) {
        this.showRaffleTitle(data.prize);
    },
    raffleClosed: function () {
        this.hideRaffleTitle();
        $('#stage').fadeOut(800).html('').show();
    },
    showRaffleTitle: function (title) {
        var titleEl = $('#prize');
        if (!titleEl.length) {
            titleEl = $('<h1>').attr('id', 'prize').hide();
            $('#stage').append(titleEl);
        }

        if (titleEl && titleEl.is(':visible')) {
            titleEl.fadeOut(500);
        }
        titleEl.html(title).fadeIn(800);
    },
    showWinner: function () {
        if (this.winners.length) {
            if (this.settings.IsCurrencyGiveaway && parseInt(this.settings.CurrencyGiveawayAmount) > 0) {
                // this.makeItRain();
            }

            var winner = $('<h2>').html(this.winners.shift().winner);
            console.log(this.winners);
            $('.background', $('#stage')).append(winner);
            $(winner).fadeIn(600);
            setTimeout($.proxy(function () {
                $('#stage').children('.background h2').fadeOut(600).remove();
            }, this), 5000);
        }
    },
    showWinners: function () {
        console.log(this.winnerInterval);
        console.log(typeof this.winnerInterval);
        if (typeof this.winnerInterval === "undefined" || this.winnerInterval === null) {
            this.showWinner();
            this.winnerInterval = setInterval($.proxy(this.showWinner, this), 7000);
        }
    },
    winnerChosen: function (data) {
        this.winners.push(data);
        //this.showWinners();
        console.log(this.winners);
    },
    userEntered: function (data) {
        var entryCollection = $('#entryCollection');
        if (!entryCollection.length) {
            entryCollection = $('<ul class="collection"></ul>').attr('id', 'entryCollection');
            $('#stage').append(entryCollection);
        }

        var winner = $('<li>').addClass('collection-item')
            .append($('<span class="user">').html(data.user))
            .append($('<span>').addClass('badge').addClass('entries').attr('data-badge-caption', 'entries').html(data.entries));
        entryCollection.append(winner);

        if (entryCollection.is(':hidden')) {
            entryCollection.fadeIn(500);
        }

        if ($('li', entryCollection).length > parseInt(this.settings.UI_RowsVisible)) {
            $('li:first-child', entryCollection).fadeOut(400).remove();
            $('li:last-child', entryCollection).fadeIn(600);
        }
    },
    userDonated: function (data) {
        var entryCollection = $('#entryCollection');
        if (!entryCollection.length) {
            entryCollection = $('<ul class="collection"></ul>').attr('id', 'entryCollection');
            $('#stage').append(entryCollection);
        }

        var winner = $('<li>').addClass('collection-item')
            .append($('<span class="user">').html(data.user))
            .append($('<span>').addClass('badge').addClass('entries').attr('data-badge-caption', 'entries').html(data.entries))
            .append($('<span>').addClass('badge').addClass('donation').attr('data-badge-caption', 'donated').html(data.donator));
        entryCollection.append(winner);

        if (entryCollection.is(':hidden')) {
            entryCollection.fadeIn(500);
        }

        if ($('li', entryCollection).length > parseInt(this.settings.UI_RowsVisible)) {
            $('li:first-child', entryCollection).fadeOut(400).remove();
            $('li:last-child', entryCollection).fadeIn(600);
        }
    },

    updateSettings: function (settings) {
        this.settings = settings;
    }
};

if (window.WebSocket) {
    new DonatedRaffleUi(API_Key);
}
/*global $ */
"use strict";

function DonatedRaffleUi(apiKey) {
    this.apiKey = apiKey;
    this.displayingWinners = false;
    this.reconnectInterval = 10000;
    this.serviceUrl = "ws://127.0.0.1:3337/streamlabs";
    this.settings = settings;
    this.socket = null;
    this.winners = [];

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
        if (/[?&]debug=/i.test(location.search)) {
            this.sendDebugEvents();
        } else {
            this.connect();
        }
    },

    connect: function () {
        let that = this;
        this.socket = new WebSocket(that.serviceUrl);
        this.socket.onclose = (evt) => {
            setTimeout(jQuery.proxy(that.connect, that), that.reconnectInterval);
        },
        this.socket.onopen = (evt) => {
            let auth = {
                author: "BleepBlamBleep",
                website: "https://bap14.github.io/Streamlabs_DonatedRaffle",
                api_key: that.apiKey,
                events: Object.values(DonatedRaffleUi.events)
            };
            that.socket.send(JSON.stringify(auth));
        };
        this.socket.onerror = (evt) => {
            console.error(evt);
        };
        this.socket.onmessage = (evt) => {
            let message = JSON.parse(evt.data);
            if (message.hasOwnProperty('data') && typeof message.data === "string") {
                message.data = JSON.parse(message.data);
            }
            else {
                message.data = {};
            }

            if (message.event === DonatedRaffleUi.events.OPEN && this.settings.Overlay_DisplayRaffleOpen) {
                that.raffleOpened(message.data);
            }
            else if (message.event === DonatedRaffleUi.events.CLOSE) {
                that.raffleClosed();
            }
            else if (message.event === DonatedRaffleUi.events.WINNER && this.settings.Overlay_DisplayWinners) {
                that.winnerChosen(message.data);
            }
            else if (message.event === DonatedRaffleUi.events.ENTER && this.settings.Overlay_DisplayRaffleEntries) {
                that.userEntered(message.data);
            }
            else if (message.event === DonatedRaffleUi.events.DONATE && this.settings.Overlay_DisplayRaffleEntries) {
                that.userDonated(message.data);
            }
            else if (message.event === DonatedRaffleUi.events.UPDATE_SETTINGS) {
                that.updateSettings(message.data);
            }
        };
    },
    getEntryCollection: function () {
        let entryCollection = $('#entryCollection');
        if (!entryCollection.length) {
            entryCollection = $('<ul class="collection"></ul>').attr('id', 'entryCollection');
            $('#stage').append(entryCollection);
        }
        if (entryCollection.is(':hidden')) {
            entryCollection.show();
        }
        return entryCollection;
    },
    hideRaffleTitle: function () {
        if ($('#title')) {
            $('#title').fadeOut(500).html('');
        }
    },
    makeItRain: function () {
        let bill,
            billCount = this.settings.Overlay_NumberOfBills,
            delayTime,
            layer = 0,
            leftPosition = 0,
            n = 0,
            randSeed = $('#stage').width(),
            speed,
            topPosition = -65;

        for (n; n < billCount; n++) {
            leftPosition = Math.floor(randSeed * Math.random());
            delayTime = Math.random() * this.settings.Overlay_CurrencyFallDelay;
            speed = Math.random() * this.settings.Overlay_CurrencyFallSpeed;
            layer = Math.floor(Math.random() * 3) + 1;

            bill = $('<figure class="raining-currency">').css({
                left: leftPosition + 'px',
                top: topPosition + 'px',
                animationDelay: delayTime + 's',
                animationDuration: speed + 's',
                zIndex: layer,
                width: '50px'
            });
            $(bill).html('<img src="images/currency.svg" alt="Stream Currency">');
            $('#stage').append(bill);
            setTimeout(function () {
                $(bill).remove();
            }, 4);
        }
    },
    raffleOpened: function (data) {
        this.showRaffleTitle(data.prize);
    },
    raffleClosed: function () {
        this.hideRaffleTitle();
        $('#stage').fadeOut(800).html('').show();
    },
    showRaffleTitle: function (title) {
        let titleEl = $('#prize');
        if (!titleEl.length) {
            titleEl = $('<h1>').addClass('green').addClass('accent-2').attr('id', 'prize').hide();
            $('#stage').append(titleEl);
        }

        if (titleEl && titleEl.is(':visible')) {
            titleEl.fadeOut(100);
        }
        titleEl.html(title).fadeIn(200);
    },
    showNewEntry: function (entry) {
        let entryCollection = this.getEntryCollection();

        entry.hide();
        entryCollection.append(entry);

        if ($('li', entryCollection).length > parseInt(this.settings.Overlay_RowsVisible)) {
            let firstChild = $('li:first-child', entryCollection);
            firstChild.animate({ opacity: 0, marginTop: (firstChild.outerHeight() * -1) + 'px' }, 200, 'linear', function () {
                firstChild.remove();
            });
        }

        $('li:last-child', entryCollection).fadeIn(100);
    },
    showWinners: function () {
        if (!this.displayingWinners && this.winners.length) {
            this.displayingWinners = true;

            if ($('#stage').is(':hidden')) {
                $('#stage').show();
            }

            let that = this;
            if (
                this.settings.Overlay_ShowRainingMoney &&
                this.settings.IsCurrencyGiveaway &&
                parseInt(this.settings.CurrencyGiveawayAmount) > 0
            ) {
                this.makeItRain();
            }

            if (!$('#stage').hasClass('valign-wrapper')) {
                $('#stage').addClass('valign-wrapper');
            }

            let winner = $('<h2>').addClass('center-align')
                .addClass('grey-text')
                .addClass('text-lighten-5')
                .html(this.winners.shift().winner)
                .hide(),
                isLastWinner = this.winners.length === 0;

            $('#stage').append(winner);
            $(winner).fadeIn(parseFloat(that.settings.Overlay_WinnerFadeTime) * 1000, function () {
                setTimeout($.proxy(function () {
                $('#stage').children('h2')
                    .fadeOut(parseFloat(that.settings.Overlay_WinnerFadeTime) * 1000, function () {
                        this.remove();
                        if (isLastWinner) {
                            $('#stage').removeClass('valign-wrapper');
                        }
                        that.displayingWinners = false;
                        that.showWinners();
                    });
                }, this), parseFloat(that.settings.Overlay_WinnerDisplayTime) * 1000);
            });
        }
    },
    winnerChosen: function (data) {
        this.winners.push(data);
        this.showWinners();
    },
    userEntered: function (data) {
        let entry = $('<li>').addClass('collection-item')
            .append($('<span class="user">').html(data.user))
            .append($('<span>').addClass('badge').addClass('entries').attr('data-badge-caption', 'entries').html(data.entries));

        this.showNewEntry(entry);
    },
    userDonated: function (data) {
        let entry = $('<li>').addClass('collection-item')
            .append($('<span class="user">').html(data.user))
            .append($('<span>').addClass('badge').addClass('entries').attr('data-badge-caption', 'entries').html(data.entries))
            .append($('<span>').addClass('badge').addClass('donation').attr('data-badge-caption', 'donated').html(data.donator));

        this.showNewEntry(entry);
    },

    updateSettings: function (settings) {
        this.settings = settings;
    },

    sendDebugEvents: function () {
        let that = this;
        new Promise((resolve, reject) => {
            that.raffleOpened({ prize: '1,000,000 Currency Giveaway' });
            setTimeout(resolve, 400);
        }).then(() => {
            return new Promise((resolve, reject) => {
                that.userEntered({ user: 'BleepBlamBleep', entries: 1 });
                setTimeout(resolve, 500);
            });
        }).then(() => {
            return new Promise((resolve, reject) => {
                that.userDonated({ user: 'Dolphin311983', donator: 'BleepBlamBleep', entries: 1 });
                setTimeout(resolve, 500);
            });
        }).then(() => {
            return new Promise((resolve, reject) => {
                that.userDonated({ user: 'Cherry_X0', donator: 'SyntaxSe7en', entries: 1 });
                setTimeout(resolve, 500);
            });
        }).then(() => {
            return new Promise((resolve, reject) => {
                that.userEntered({ user: 'SyntaxSe7en', entries: 1 });
                setTimeout(resolve, 500);
            });
        }).then(() => {
            return new Promise((resolve, reject) => {
                that.userEntered({ user: 'MrUniverse08', entries: 1 });
                setTimeout(resolve, 1000);
            });
        }).then(() => {
            return new Promise((resolve, reject) => {
                that.raffleClosed();
                setTimeout(resolve, 1000);
            });
        }).then(() => {
            return new Promise((resolve, reject) => {
                that.winnerChosen({winner: 'Cherry_X0', entriesUsed: 1});
                that.winnerChosen({winner: 'SyntaxSe7en', entriesUsed: 1});
                that.winnerChosen({winner: 'Dolphin311983', entriesUsed: 1});
                that.winnerChosen({winner: 'MrUniverse08', entriesUsed: 1});
                setTimeout(resolve, 12000);
            });
        }).then(() => {
            that.winnerChosen({winner: 'xLethalChicax', entriesUsed: 1});
        });
    }
};

if (window.WebSocket) {
    new DonatedRaffleUi(API_Key);
}
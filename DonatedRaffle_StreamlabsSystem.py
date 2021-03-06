# ------------------------
# Import Libraries
# ------------------------
import sys
import clr
import os
import codecs
import json
import re
import time
# import math # for timed raffles
from random import *
clr.AddReference("IronPython.SQLite.dll")
clr.AddReference("IronPython.Modules.dll")

# ------------------------
# [Required] Script Information
# ------------------------
ScriptName = "Donated Raffle"
Website = "https://github.com/bap14/Streamlabs_DonatedRaffle"
Description = "Creates a raffle system that allows viewers to 'donate' chances to other viewers"
Creator = "BleepBlamBleep"
Version = "0.0.1.3"

# ------------------------
# Set Variables
# ------------------------
countdownUsed = []
donatedEntries = {}
entryPurchases = {}
fileEncoding = 'utf-8-sig'
isRaffleActive = False
raffleEntries = []
RaffleSettings = {}
raffleStartTime = 0
recentWinners = []
selfEntry = {}
settingsFile = os.path.join(os.path.dirname(__file__), "settings", "settings.json")
snapshotDir = os.path.join(os.path.dirname(__file__), "snapshots")
winnerList = []

class Settings:
    def __init__(self, settings_file=None):
        global fileEncoding, settingsFile
        self.config = self.getDefaultSettings()

        settings_dir = os.path.dirname(settingsFile)
        if settings_file is not None:
            settings_dir = os.path.dirname(settings_file)

        if not os.path.isdir(settings_dir):
            os.makedirs(settings_dir)

        Parent.Log("Donated Raffle", "Original Settings File: {0}".format(settings_file))
        if settings_file is not None and not os.path.isfile(settings_file):
            path_tuple = os.path.split(settings_file)
            settingsFilePath = path_tuple[0].split(os.sep)
            settingsFilePath.pop()
            old_settings_file = os.path.join(os.sep.join(settingsFilePath), path_tuple[1])
            if os.path.isfile(old_settings_file):
                os.rename(old_settings_file, settings_file)
            if os.path.isfile(old_settings_file.replace('json', 'js')):
                os.rename(old_settings_file.replace('json', 'js'), settings_file.replace('json', 'js'))

        if os.path.isfile(settings_file):
            Parent.Log("Donated Raffle", "Loading settings file: {0}".format(settings_file))
            with codecs.open(settings_file, encoding=fileEncoding, mode='r') as f:
                self.config.update(json.load(f, encoding=fileEncoding))
        return

    def __getattr__(self, item):
        retval = None
        if item in self.config:
            retval = self.config[item]
        return retval

    def ReloadSettings(self, data):
        global fileEncoding
        Parent.Log("Donated Raffle", "Reloading settings")
        self.config = self.getDefaultSettings()
        self.config.update(json.loads(data, encoding=fileEncoding))
        Parent.BroadcastWsEvent("DONATEDRAFFLE_UPDATE_SETTINGS", json.dumps(self.config))
        return

    def SaveSettings(self, settings_file):
        global fileEncoding
        with codecs.open(settings_file, encoding=fileEncoding, mode='w+') as f:
            json.dump(self.config, f, encoding=fileEncoding, indent=4, sort_keys=True)
        with codecs.open(settings_file.replace('json', 'js'), encoding=fileEncoding, mode='w+') as f:
            f.write("var settings = {0};".format(json.dumps(self.config, encoding=fileEncoding, indent=4,
                                                            sort_keys=True)))
        return

    # ------------------------
    # Get a copy of the default settings JSON structure
    # ------------------------
    def getDefaultSettings(self):
        return {
            "Prize": "",
            "Command": "!raffle",
            "Permission": "Everyone",
            "PermissionInfo": "",
            "EntryCost": 0,
            "MaxPersonalEntries": 1,
            "EnableDonations": False,
            "AllowMultipleDonations": False,
            "IsRaffleTimed": False,
            "RaffleTimerDuration": 300,
            "IsCurrencyGiveaway": False,
            "CurrencyGiveawayAmount": 1000,
            "WinnerListKeyword": "winners",
            "WinnerListPermission": "Everyone",
            "WinnerListPermissionInfo": "",
            "ListAllWinnersKeyword": "all",
            "ListAllWinnersPermission": "Everyone",
            "ListAllWinnersPermissionInfo": "",
            "AnnounceWinnersIndividually": True,
            "CountdownToRaffleClose": False,
            "CountdownFrom": 10,

            "Message_RaffleOpen": "A raffle for: {0} has started! {1} can enter!",
            "Message_RaffleOpenUnlimitedEntry": "[Entry Cost: {0}] - Use `{1} <number>` to enter",
            "Message_RaffleOpenLimitedEntry": "Entry Cost: {0} - Maximum Entries: {1} - Use `{2} <number>` to enter",
            "Message_RaffleOpenDonateEntry": "or `{0} <number> <username>` to donate entries to someone.",
            "Message_NotEnoughCurrency": "@{0} you don't have enough {1}!",
            "Message_MaxEntriesExceeded": "@{0} You are only able to purchase up to {1} entries.",
            "Message_DonationsDisabled": "@{0}, donating entries is not enabled.",
            "Message_MultipleDonationsDisabled": "@{0}, you can only donate entries to one person",
            "Message_RaffleClosed": "Entries have stopped for the raffle! You can no longer enter!",
            "Message_RaffleRefunded": "All {0} has been refunded for the current raffle.",
            "Message_Winner": "@{0}, you have won (with {1} entries)! Speak up in chat!",
            "Message_WinnerCurrency": "@{0}, you have won (with {1} entries)! {2} {3} has been given to you.",
            "Message_DonateToSelfDisallowed": "You cannot donate entires to yourself.",
            "Message_CloseBeforeChoosing": "You must close the raffle before choosing winners.",
            "Message_NoEntrantsFound": "There are no entrants to choose from.",
            "Message_WinnerListing": "@{0}, the most recent winners of the last raffle were: {1}",
            "Message_AllWinnersListing": "@{0}, the winners of the last raffle were: {1}",
            "Message_MultipleWinners": "{0} you have all won! Please speak up in chat!",
            "Message_CountdownAnnouncement": "The raffle will close in {0}",

            "Manage_Command": "!manageraffle",
            "Manage_Permission": "Editor",
            "Manage_PermissionInfo": "",
            "Manage_ClearWinnersKeyword": "clear",
            "Manage_CloseKeyword": "close",
            "Manage_OpenKeyword": "open",
            "Manage_PickKeyword": "pick",
            "Manage_RefundKeyword": "refund",
            "Manage_ResetKeyword": "reset",
            "Manage_SaveSnapshotKeyword": "save",
            "Manage_LoadSnapshotKeyword": "load",

            "Overlay_DisplayRaffleOpen": True,
            "Overlay_DisplayRaffleEntries": True,
            "Overlay_DisplayWinners": True,
            "Overlay_RowsVisible": 4,
            "Overlay_ShowRainingMoney": True,
            "Overlay_NumberOfBills": 25,
            "Overlay_CurrencyFallSpeed": 3,
            "Overlay_CurrencyFallDelay": 2,
            "Overlay_WinnerDisplayTime": 2.5,
            "Overlay_WinnerFadeTime": 0.6
        }.copy()

    def SaveSnapshot(self, key):
        global fileEncoding
        if not os.path.exists(snapshotDir):
            os.makedirs(snapshotDir)
        file_path = os.path.join(snapshotDir, key + ".json")
        with codecs.open(file_path, encoding=fileEncoding, mode='w+') as f:
            json.dump(self.config, f, encoding=fileEncoding, indent=4, sort_keys=True)
        Parent.SendTwitchMessage("Snapshot '{0}' created.".format(key))
        return

    def LoadSnapshot(self, key):
        global fileEncoding, settingsFile, winnerList, entryPurchases, raffleEntries
        file_path = os.path.join(snapshotDir, key + ".json")
        Parent.Log("Donated Raffle", "Loading snapshot from: {0}".format(file_path))
        if os.path.isfile(file_path):
            self.config = self.getDefaultSettings()
            with codecs.open(file_path, encoding=fileEncoding, mode='r') as f:
                self.config.update(json.load(f, encoding=fileEncoding))

            self.SaveSettings(settingsFile)
            ClearWinnersList(announce=False)
            ResetRaffle(announce=False)
            Parent.SendTwitchMessage("Loaded raffle '{0}'.  Winners and entries have been reset.".format(key))
        else:
            Parent.SendTwitchMessage("Snapshot '{0}' does not exist.".format(key))
        return


# ------------------------
# [Required] Initialize Data (Only called on Load)
# ------------------------
def Init():
    global RaffleSettings, isRaffleActive, settingsFile
    isRaffleActive = False
    RaffleSettings = Settings(settingsFile)
    return

def ReloadSettings(jsonData):
    global RaffleSettings, settingsFile
    RaffleSettings.ReloadSettings(jsonData)
    return

# ------------------------
# [Required] Execute Data / Process Messages
# ------------------------
def Execute(data):
    global RaffleSettings, isRaffleActive, raffleEntries
    if data.IsChatMessage():
        if isRaffleActive and data.GetParam(0).lower() == RaffleSettings.Command.lower() and \
                Parent.HasPermission(data.User, RaffleSettings.Permission, RaffleSettings.PermissionInfo):
            user_input = ParseUserInput(data)
            if ValidateEntry(data, user_input["numEntries"]):
                if user_input is not None:
                    # If donations aren't enabled and someone is trying to donate
                    if not RaffleSettings.EnableDonations and user_input["target"] is not None:
                        Parent.SendTwitchMessage("/me " + RaffleSettings.Message_DonationsDisabled.format(
                            Parent.GetDisplayName(data.User)
                        ))
                    # Donations are enabled and someone is trying to donate
                    elif RaffleSettings.EnableDonations and user_input["target"] is not None:
                        if user_input["target"].lower() == data.User.lower():
                            Parent.SendTwitchMessage(RaffleSettings.Message_DonateToSelfDisallowed)
                        else:
                            allowed_to_donate = True
                            if not RaffleSettings.AllowMultipleDonations:
                                if data.User in donatedEntries and len(donatedEntries[data.User]) and \
                                        user_input["target"] not in donatedEntries[data.User]:
                                    allowed_to_donate = False

                            if allowed_to_donate:
                                if ValidateEntryPurchase(data.User, user_input):
                                    DonateEntry(data.User, user_input["numEntries"], user_input["target"])
                                else:
                                    Parent.SendTwitchMessage(
                                        RaffleSettings.Message_MaxEntriesExceeded.format(data.User,
                                                                                         RaffleSettings.MaxPersonalEntries))
                            else:
                                Parent.SendTwitchMessage(RaffleSettings.Message_MultipleDonationsDisabled.format(data.User))
                    # Regular raffle entry
                    else:
                        if ValidateEntryPurchase(data.User, user_input):
                            SelfEntry(data.User, user_input["numEntries"])
                        else:
                            Parent.SendTwitchMessage(
                                RaffleSettings.Message_MaxEntriesExceeded.format(data.User,
                                                                                 RaffleSettings.MaxPersonalEntries))
                else:
                    Parent.Log("Donated Raffle", "Invalid entry received: {0}".format(data.Message))
        elif not isRaffleActive and data.GetParam(0).lower() == RaffleSettings.Command.lower() \
                and data.GetParamCount() == 2:
                if data.GetParam(1).lower() == RaffleSettings.WinnerListKeyword.lower() and len(recentWinners) \
                    and Parent.HasPermission(data.User, RaffleSettings.WinnerListPermission,
                                     RaffleSettings.WinnerListPermissionInfo):
                    AnnounceRecentWinners(data.User)
                elif data.GetParam(1).lower() == RaffleSettings.ListAllWinnersKeyword.lower() and len(winnerList) \
                    and Parent.HasPermission(data.User, RaffleSettings.ListAllWinnersPermission,
                                     RaffleSettings.ListAllWinnersPermissionInfo):
                    AnnounceAllWinners(data.User)
        elif data.GetParam(0).lower() == RaffleSettings.Manage_Command.lower() \
                and Parent.HasPermission(data.User, RaffleSettings.Manage_Permission,
                                         RaffleSettings.Manage_PermissionInfo):
            if data.GetParam(1).lower() == RaffleSettings.Manage_CloseKeyword.lower():
                CloseRaffle()
            elif data.GetParam(1).lower() == RaffleSettings.Manage_ResetKeyword.lower():
                ResetRaffle()
            elif data.GetParam(1).lower() == RaffleSettings.Manage_OpenKeyword.lower():
                OpenRaffle()
            elif data.GetParam(1).lower() == RaffleSettings.Manage_RefundKeyword.lower():
                RefundRaffleEntries()
            elif data.GetParam(1).lower() == RaffleSettings.Manage_PickKeyword.lower():
                winnerCount = 1
                if data.GetParamCount() == 3:
                    winnerCount = int(data.GetParam(2))
                PickWinners(winnerCount)
            elif data.GetParam(1).lower() == RaffleSettings.Manage_ClearWinnersKeyword.lower():
                ClearWinnersList()
            elif data.GetParam(1).lower() == RaffleSettings.Manage_SaveSnapshotKeyword.lower():
                start_index = 2 + len(data.GetParam(0)) + len(data.GetParam(1))
                file_name = SanitizeFilename(data.Message, start_index)
                Parent.Log("Donated Raffle", "Saving new snapshot to file {0}".format(file_name))
                RaffleSettings.SaveSnapshot(file_name)
            elif data.GetParam(1).lower() == RaffleSettings.Manage_LoadSnapshotKeyword.lower():
                start_index = 2 + len(data.GetParam(0)) + len(data.GetParam(1))
                file_name = SanitizeFilename(data.Message, start_index)
                Parent.Log("Donated Raffle", "Loading snapshot from file {0}".format(file_name))
                RaffleSettings.LoadSnapshot(file_name)
    return

# ------------------------
# [Required] Tick Function
# ------------------------
def Tick():
    global RaffleSettings, isRaffleActive, raffleStartTime, countdownUsed
    if isRaffleActive:
        time_elapsed = (time.time() - raffleStartTime)
        if RaffleSettings.IsRaffleTimed and time_elapsed >= RaffleSettings.RaffleTimerDuration:
            CloseRaffle()
        # if RaffleSettings.IsRaffleTimed and RaffleSettings.CountdownToRaffleClose and \
        #         int(RaffleSettings.CountdownFrom) > 0:
        #     time_remaining = math.ceil(RaffleSettings.RaffleTimerDuration - time_elapsed)
        #     if "{0}".format(int(time_remaining)) not in countdownUsed:
        #         countdownUsed.append("{0}".format(int(time_remaining)))
        #         if time_remaining and time_remaining <= int(RaffleSettings.CountdownFrom) and time_remaining % 2 != 0:
        #             Parent.SendTwitchMessage("/me " + RaffleSettings.Message_CountdownAnnouncement.format(
        #                 int(time_remaining)))

    return

def AnnounceAllWinners(user):
    global RaffleSettings, winnerList
    Parent.SendTwitchMessage(RaffleSettings.Message_WinnerListing.format(user, ", ".join(winnerList)))
    return

def AnnounceRecentWinners(user):
    global RaffleSettings, recentWinners
    Parent.SendTwitchMessage(RaffleSettings.Message_WinnerListing.format(user, ", ".join(recentWinners)))
    return

def ClearWinnersList(announce=True):
    global recentWinners
    recentWinners = []
    if announce:
        Parent.SendTwitchMessage("/me Winners list cleared.")
    return

def CloseRaffle():
    global RaffleSettings, isRaffleActive, countdownUsed
    if isRaffleActive:
        isRaffleActive = False
        countdownUsed = []
        Parent.BroadcastWsEvent("DONATEDRAFFLE_CLOSE", "{}")
        Parent.SendTwitchMessage(RaffleSettings.Message_RaffleClosed)
    return

def DonateEntry(user, numEntries, target):
    global donatedEntries, raffleEntries
    if PurchaseEntry(user, numEntries):
        donatedEntries[user][target] += numEntries
        Parent.BroadcastWsEvent("DONATEDRAFFLE_DONATE", json.dumps({
            "user": Parent.GetDisplayName(target),
            "entries": numEntries,
            "donator": Parent.GetDisplayName(user)
        }))
        Parent.Log("Donated Raffle", "{0} donated {1} entries to {2}.".format(Parent.GetDisplayName(user), numEntries,
                                                                              Parent.GetDisplayName(target)))
        for i in range(numEntries):
            raffleEntries.append(target)
    return

def NormalizeUsername(name):
    if name[0] == '@':
        name = name[1:]
    name = name.lower()
    return name

def OpenRaffle():
    global RaffleSettings, isRaffleActive, raffleStartTime
    if not isRaffleActive:
        isRaffleActive = True
        raffleStartTime = time.time()

        if int(RaffleSettings.MaxPersonalEntries) > 0:
            maxInfo = "/me " + RaffleSettings.Message_RaffleOpenLimitedEntry.format(RaffleSettings.EntryCost,
                                                                                    RaffleSettings.MaxPersonalEntries,
                                                                                    RaffleSettings.Command)
        else:
            maxInfo = "/me " + RaffleSettings.Message_RaffleOpenUnlimitedEntry.format(RaffleSettings.EntryCost,
                                                                                      RaffleSettings.Command)

        donationInfo = ""
        if RaffleSettings.EnableDonations:
            donationInfo = " " + RaffleSettings.Message_RaffleOpenDonateEntry.format(RaffleSettings.Command)

        Parent.BroadcastWsEvent("DONATEDRAFFLE_OPEN", json.dumps({
            "prize": RaffleSettings.Prize,
            "permission": RaffleSettings.Permission
        }))
        Parent.SendTwitchMessage("/me " + RaffleSettings.Message_RaffleOpen.format(RaffleSettings.Prize,
                                                                                   RaffleSettings.Permission))
        Parent.SendTwitchMessage(maxInfo + donationInfo)
    return

def ParseUserInput(data):
    parsed_input = dict()
    parsed_input.update({
        "command": None,
        "numEntries": None,
        "target": None
    })

    parsed_input["command"] = data.GetParam(0)
    regex = re.compile(r"^@?.+$")

    # !<command>
    if data.GetParamCount() == 1:
        parsed_input["numEntries"] = 1
    # !<command> 10
    elif data.GetParamCount() == 2 and data.GetParam(1).isdigit():
        parsed_input["numEntries"] = int(data.GetParam(1))
    # !<command> <target>
    elif data.GetParamCount() == 2 and re.match(regex, data.GetParam(1)):
        parsed_input["numEntries"] = 1
        parsed_input["target"] = NormalizeUsername(data.GetParam(1))
    # !<command> 10 <target>
    elif data.GetParamCount() == 3 and data.GetParam(1).isdigit() and re.match(regex, data.GetParam(2)):
        parsed_input["numEntries"] = int(data.GetParam(1)) if int(data.GetParam(1)) > 0 else 1
        parsed_input["target"] = NormalizeUsername(data.GetParam(2))
    # !<command> 10 for <target>
    else:
        parsed_input = None

    # trim preceding "@" from names (if there is one)
    if parsed_input is not None and parsed_input["target"] is not None and parsed_input["target"][0] == "@":
        parsed_input["target"] = parsed_input["target"][1:]

    return parsed_input

def PickWinners(num):
    global RaffleSettings, winnerList, isRaffleActive, raffleEntries
    if isRaffleActive:
        Parent.SendTwitchMessage("/me " + RaffleSettings.Message_CloseBeforeChoosing)
    else:
        if int(num) == 0:
            num = 1

        if len(raffleEntries):
            for x in range(0, num):
                if len(raffleEntries):
                    for i in range(1, randint(5, 25)):
                        shuffle(raffleEntries)

                    randomIndex = randint(1, len(raffleEntries)) - 1
                    winner = raffleEntries[randomIndex]
                    recentWinners.append(winner)
                    winnerList.append(winner)
                    entriesUsed = RemoveEntrant(winner)
                    Parent.BroadcastWsEvent("DONATEDRAFFLE_WINNER", json.dumps({
                        "winner": Parent.GetDisplayName(winner),
                        "entriesUsed": entriesUsed
                    }))
                    Parent.Log("Donated Raffle", "Winner: {0} ({1} entries)".format(Parent.GetDisplayName(winner),
                                                                                       entriesUsed))

                    if RaffleSettings.IsCurrencyGiveaway and RaffleSettings.CurrencyGiveawayAmount > 0:
                        Parent.Log("Donated Raffle", "Giving {0} {1} currency to {2}".format(
                            int(RaffleSettings.CurrencyGiveawayAmount),
                            Parent.GetCurrencyName(),
                            Parent.GetDisplayName(winner)))
                        Parent.AddPoints(winner, int(RaffleSettings.CurrencyGiveawayAmount))

                    if RaffleSettings.AnnounceWinnersIndividually or num == 1:
                        Parent.SendTwitchMessage(RaffleSettings.Message_Winner.format(
                            Parent.GetDisplayName(winner),
                            entriesUsed,
                            RaffleSettings.CurrencyGiveawayAmount,
                            Parent.GetCurrencyName()))

            if not RaffleSettings.AnnounceWinnersIndividually and num > 1:
                Parent.Log("Donated Raffle", RaffleSettings.Message_MultipleWinners.format(", ".join(recentWinners)))
                Parent.SendTwitchMessage(
                        "@" + RaffleSettings.Message_MultipleWinners.format(", @".join(recentWinners),
                                                                            RaffleSettings.CurrencyGiveawayAmount,
                                                                            Parent.GetCurrencyName()))
        else:
            Parent.SendTwitchMessage("/me " + RaffleSettings.Message_NoEntrantsFound)
    return

def PickSingleWinner():
    return PickWinners(1)

def PurchaseEntry(user, num):
    global RaffleSettings, entryPurchases
    purchased = True
    if Parent.RemovePoints(user, RaffleSettings.EntryCost * int(num)):
        if user not in entryPurchases:
            entryPurchases[user] = 0

        entryPurchases[user] += int(num)
    else:
        Parent.SendTwitchMessage(RaffleSettings.Message_NotEnoughCurrency.format(user, Parent.GetCurrencyName()))
        purchased = False
    return purchased

def RefundRaffleEntries():
    global RaffleSettings, entryPurchases, isRaffleActive
    if isRaffleActive:
        isRaffleActive = False

    totalRefunded = 0
    for user, num in entryPurchases.items():
        totalPurchased = RaffleSettings.EntryCost * num
        if Parent.AddPoints(user, totalPurchased):
            # Parent.Log("Donated Raffle", "Refunded {0} {1} currency ({2} entries)".format(Parent.GetDisplayName(user),
            #                                                                               totalPurchased,
            #                                                                               num))
            totalRefunded += totalPurchased
        else:
            Parent.Log("Donated Raffle", "Failed to refund {0} {1} {2}".format(user,
                                                                               totalPurchased,
                                                                               Parent.GetCurrencyName()))

    Parent.SendTwitchMessage("/me " + RaffleSettings.Message_RaffleRefunded.format(Parent.GetCurrencyName()))
    isRaffleActive = False
    return

def RemoveEntrant(username):
    global raffleEntries
    start_len = len(raffleEntries)
    raffleEntries = filter(lambda x: x.lower() != username.lower(), raffleEntries)
    end_len = len(raffleEntries)
    entries_used = start_len - end_len
    return entries_used

def ResetRaffle(announce=True):
    global RaffleSettings, isRaffleActive, donatedEntries, raffleEntries, raffleStartTime, entryPurchases, winnerList, \
        selfEntry, countdownUsed, recentWinners
    countdownUsed = []
    donatedEntries = {}
    entryPurchases = {}
    isRaffleActive = False
    raffleEntries = []
    raffleStartTime = 0
    selfEntry = {}
    recentWinners = []
    winnerList = []
    if announce:
        Parent.SendTwitchMessage("/me Raffle Reset")
    return

def SelfEntry(user, numEntries):
    global raffleEntries
    if PurchaseEntry(user, numEntries):
        Parent.BroadcastWsEvent("DONATEDRAFFLE_ENTER", json.dumps({
            "user": Parent.GetDisplayName(user),
            "entries": numEntries
        }))
        for i in range(numEntries):
            raffleEntries.append(user)
    return

# ----------------
# Clean user-input to remove "illegal" characters for Windows operating system filenames
# ----------------
def SanitizeFilename(message, sindex):
    if not sindex:
        sindex = 0
    file_name = message[sindex:].replace(" ", "_")
    file_name = re.sub(r"\.\.+", ".", file_name)
    file_name = re.sub(r"\\/:\*\?\"<>\|", "-", file_name)
    return file_name

# ----------------
# Check to see if user has not exceeded max entries AND they have the currency to purchase numEntries entries
# ----------------
def ValidateEntry(data, numEntries):
    global RaffleSettings
    isValid = True
    if int(RaffleSettings.MaxPersonalEntries) and numEntries > int(RaffleSettings.MaxPersonalEntries):
        isValid = False
        Parent.SendTwitchMessage(RaffleSettings.Message_MaxEntriesExceeded.format(data.User, RaffleSettings.MaxPersonalEntries))
    else:
        totalCost = RaffleSettings.EntryCost * int(numEntries)
        if totalCost > Parent.GetPoints(data.User):
            isValid = False
            Parent.SendTwitchMessage(RaffleSettings.Message_NotEnoughCurrency.format(data.User, Parent.GetCurrencyName()))
    return isValid

def ValidateEntryPurchase(user, user_input):
    global RaffleSettings, entryPurchases, donatedEntries
    is_valid = True

    # Self entry
    if user_input["target"] is None:
        if user not in selfEntry:
            selfEntry[user] = 0
        if int(RaffleSettings.MaxPersonalEntries) and \
                selfEntry[user] + user_input["numEntries"] > int(RaffleSettings.MaxPersonalEntries):
            is_valid = False
    # Donating entry
    elif user_input["target"] is not None:
        if user not in donatedEntries:
            donatedEntries[user] = {}
        if user_input["target"] not in donatedEntries[user]:
            donatedEntries[user][user_input["target"]] = 0
        if int(RaffleSettings.MaxPersonalEntries) and \
                donatedEntries[user][user_input["target"]] + user_input["numEntries"] > int(RaffleSettings.MaxPersonalEntries):
            is_valid = False
    return is_valid

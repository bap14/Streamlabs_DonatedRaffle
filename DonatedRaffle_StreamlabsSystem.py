# ------------------------
# Import Libraries
# ------------------------
import sys
import clr
clr.AddReference("IronPython.SQLite.dll")
clr.AddReference("IronPython.Modules.dll")
import os
import codecs
import json
import re
import time
from random import *

# ------------------------
# [Required] Script Information
# ------------------------
ScriptName = "Donated Raffle"
Website = "https://github.com/bap14/Streamlabs_DonatedRaffle"
Description = "Creates a raffle system that allows viewers to 'donate' chances to other viewers"
Creator = "BleepBlamBleep"
Version = "0.0.1"

# ------------------------
# Set Variables
# ------------------------
donatedEntries = {}
entryPurchases = {}
fileEncoding = 'utf-8-sig'
isRaffleActive = False
raffleEntries = []
RaffleSettings = {}
raffleStartTime = 0
settingsFile = os.path.join(os.path.dirname(__file__), "settings.json")
snapshotDir = os.path.join(os.path.dirname(__file__), "snapshots")
winnerList = []

class Settings:
    def __init__(self, settings_file=None):
        global fileEncoding
        self.config = self.getDefaultSettings()
        
        if settings_file is not None and os.path.isfile(settings_file):
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
        self.config = self.getDefaultSettings()
        self.config.update(json.loads(data, encoding=fileEncoding))
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
            "Message_Winner": "@{0}, you have won! Speak up in chat!",
            "Message_DonateToSelfDisallowed": "You cannot donate entires to yourself.",
            "Message_CloseBeforeChoosing": "You must close the raffle before choosing winners.",
            "Message_NoEntrantsFound": "There are no entrants to choose from.",
            "Message_WinnerListing": "@{0}, the winners of the last raffle were: {1}",

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
            "Manage_LoadSnapshotKeyword": "load"
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
        global fileEncoding, settingsFile
        file_path = os.path.join(snapshotDir, key + ".json")
        Parent.Log("Donated Raffle", "Loading snapshot from: {0}".format(file_path))
        if os.path.isfile(file_path):
            self.config = self.getDefaultSettings()
            with codecs.open(file_path, encoding=fileEncoding, mode='r') as f:
                self.config.update(json.load(f, encoding=fileEncoding))

            self.SaveSettings(settingsFile)
            Parent.SendTwitchMessage("Loaded raffle {0}".format(key))
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
    global RaffleSettings
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
                        if user_input["target"] == data.User:
                            Parent.SendTwitchMessage(RaffleSettings.Message_DonateToSelfDisallowed)
                        else:
                            allowed_to_donate = True
                            if not RaffleSettings.AllowMultipleDonations:
                                if data.User in donatedEntries and len(donatedEntries[data.User]) and \
                                        user_input["target"] not in donatedEntries[data.User]:
                                    allowed_to_donate = False

                            if allowed_to_donate:
                                if not RaffleSettings.MaxPersonalEntries or \
                                        ValidateEntryPurchase(data.User, user_input):
                                    PurchaseEntry(data.User, user_input["numEntries"])
                                    donatedEntries[data.User][user_input["target"]] += user_input["numEntries"]
                                    Parent.Log("Donated Raffle",
                                               "{0} donated {1} entries to {2}.".format(Parent.GetDisplayName(data.User),
                                                                                        user_input["numEntries"],
                                                                                        Parent.GetDisplayName(user_input["target"])))
                                    for i in range(user_input["numEntries"]):
                                        raffleEntries.append(user_input["target"])
                                else:
                                    Parent.SendTwitchMessage(
                                        RaffleSettings.Message_MaxEntriesExceeded.format(data.User,
                                                                                         RaffleSettings.MaxPersonalEntries))
                            else:
                                Parent.SendTwitchMessage(RaffleSettings.Message_MultipleDonationsDisabled.format(data.User))
                    # Regular raffle entry
                    else:
                        if not RaffleSettings.MaxPersonalEntries or ValidateEntryPurchase(data.User, user_input):
                            PurchaseEntry(data.User, user_input["numEntries"])
                            for i in range(user_input["numEntries"]):
                                raffleEntries.append(data.User)
                        else:
                            Parent.SendTwitchMessage(
                                RaffleSettings.Message_MaxEntriesExceeded.format(data.User,
                                                                                 RaffleSettings.MaxPersonalEntries))
                else:
                    Parent.Log("Donated Raffle", "Invalid entry received: {0}".format(data.Message))
        elif not isRaffleActive and data.GetParam(0).lower() == RaffleSettings.Command.lower() \
                and data.GetParamCount() == 2 and data.GetParam(1).lower() == RaffleSettings.WinnerListKeyword.lower() \
                and len(winnerList) and \
                Parent.HasPermission(data.User, RaffleSettings.WinnerListPermission,
                                     RaffleSettings.WinnerListPermissionInfo):
            Parent.SendTwitchMessage(RaffleSettings.Message_WinnerListing.format(data.User, ", ".join(winnerList)))
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
    global RaffleSettings, isRaffleActive, raffleStartTime
    if isRaffleActive:
        if RaffleSettings.IsRaffleTimed and (time.time() - raffleStartTime) >= RaffleSettings.RaffleTimerDuration:
            CloseRaffle()
    return

def ClearWinnersList():
    global winnerList
    winnerList = []
    # Parent.Log("Donated Raffle", "Existing winners cleared")
    return

def CloseRaffle():
    global RaffleSettings, isRaffleActive
    if isRaffleActive:
        isRaffleActive = False
        Parent.SendTwitchMessage(RaffleSettings.Message_RaffleClosed)
    return

def NormalizeUsername(name):
    if name[0] == '@':
        name = name[1:]
    return name

def OpenRaffle():
    global RaffleSettings, isRaffleActive, raffleStartTime
    if not isRaffleActive:
        isRaffleActive = True
        raffleStartTime = time.time()

        if RaffleSettings.MaxPersonalEntries:
            maxInfo = "/me " + RaffleSettings.Message_RaffleOpenLimitedEntry.format(RaffleSettings.EntryCost,
                                                                                    RaffleSettings.MaxPersonalEntries,
                                                                                    RaffleSettings.Command)
        else:
            maxInfo = "/me " + RaffleSettings.Message_RaffleOpenUnlimitedEntry.format(RaffleSettings.EntryCost,
                                                                                      RaffleSettings.Command)

        donationInfo = ""
        if RaffleSettings.EnableDonations:
            donationInfo = " " + RaffleSettings.Message_RaffleOpenDonateEntry.format(RaffleSettings.Command)

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
    global RaffleSettings, winnerList, isRaffleActive
    if isRaffleActive:
        Parent.SendTwitchMessage("/me " + RaffleSettings.Message_CloseBeforeChoosing)
    else:
        if int(num) == 0:
            num = 1

        if len(raffleEntries):
            for x in range(0, num):
                if len(raffleEntries):
                    for i in range(1, randint(5,25)):
                        shuffle(raffleEntries)

                    randomIndex = randint(1, len(raffleEntries)) - 1
                    winner = raffleEntries[randomIndex]
                    winnerList.append(winner)
                    RemoveEntrant(winner)
                    # Parent.Log("Donated Raffle", "Winners: {0}".format(", ".join(winnerList)))

                    if RaffleSettings.IsCurrencyGiveaway and RaffleSettings.CurrencyGiveawayAmount > 0:
                        Parent.Log("Donated Raffle", "Giving {0} {1} currency to {2}".format(
                            int(RaffleSettings.CurrencyGiveawayAmount),
                            Parent.GetCurrencyName(),
                            Parent.GetDisplayName(winner)))
                        Parent.AddPoints(winner, int(RaffleSettings.CurrencyGiveawayAmount))

                    Parent.SendTwitchMessage(RaffleSettings.Message_Winner.format(Parent.GetDisplayName(winner)))
        else:
            Parent.SendTwitchMessage("/me " + RaffleSettings.Message_NoEntrantsFound)
    return

def PickSingleWinner():
    return PickWinners(1)

def PurchaseEntry(user, num):
    global RaffleSettings, entryPurchases
    if Parent.RemovePoints(user, RaffleSettings.EntryCost * int(num)):
        if user not in entryPurchases:
            entryPurchases[user] = 0

        entryPurchases[user] += int(num)
    else:
        Parent.SendTwitchMessage(RaffleSettings.Message_NotEnoughCurrency.format(user, Parent.GetCurrencyName()))
    return

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
    raffleEntries = filter(lambda x: x != username, raffleEntries)
    return

def ResetRaffle():
    global RaffleSettings, isRaffleActive, donatedEntries, raffleEntries, raffleStartTime, entryPurchases, winnerList
    isRaffleActive = False
    raffleStartTime = 0
    raffleEntries = []
    entryPurchases = {}
    donatedEntries = {}
    winnerList = []
    Parent.SendTwitchMessage("/me Raffle Reset")
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
    if RaffleSettings.MaxPersonalEntries and numEntries > RaffleSettings.MaxPersonalEntries:
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
        if user not in entryPurchases:
            entryPurchases[user] = 0
        if entryPurchases[user] + user_input["numEntries"] > RaffleSettings.MaxPersonalEntries:
            is_valid = False
    # Donating entry
    elif user_input["target"] is not None:
        if user not in donatedEntries:
            donatedEntries[user] = {}
        if user_input["target"] not in donatedEntries[user]:
            donatedEntries[user][user_input["target"]] = 0
        if donatedEntries[user][user_input["target"]] + user_input["numEntries"] > RaffleSettings.MaxPersonalEntries:
            is_valid = False
    return is_valid

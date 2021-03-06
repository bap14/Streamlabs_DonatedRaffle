# Streamlabs ChatBot Donated Raffle

This raffle script mimics the GiveAway functionality. It adds the
ability for users to donate entries to others.

## Features

- Basic Raffle System
- Timed Raffle
- Automatic Currency Giveaway
- Donating Raffle Entries
- Loading and Saving Raffle Configurations (Snapshots)
- Recalling Raffle Winner List
- Pick Multiple Winners At Once

## Installation

There are two ways to install this script.  You can download the zip 
release and manually install the files or download the installer and run
it.

The basics of the installation are as follows:

1. Install the files using one of the methods outlined below
1. Open Streamlabs Chatbot (if it isn't opened already)
1. Connect to the chat servers both as the streamer and the bot
1. In the left-hand list of sections, choose "Scripts"
1. If you haven't configured your `Python 2.7 Directory` path yet:
   (see [this youtube video](https://youtu.be/l3FBpY-0880?t=2m21s) for example)
    - Click the Cog wheel in the top right.
    - Click the "Pick Folder" button for the `Python 2.7 Directory`
      and browse to your Python installations `Lib` directory (by
      default this is: `C:\Python27\Lib`)
    - Click the left arrow to go back to the main script panel
1. Now Right-click in the large pane listing scripts (it may be empty if
    this is your first script to be installed)
1. Select "Reload Scripts" and "Donated Raffle" should now appear.
1. Left-click on the "Donated Raffle" row to bring up it's settings in a
    panel on the right.
1. When you're ready for this script to run, check the "Enabled" checkbox
    in the script listing panel. If this is not checked, this script will
    not have any effect.

### Installer Method

1. Download the [latest release installer](https://github.com/bap14/Streamlabs_DonatedRaffle/releases/latest):
    `Streamlabs.Chatbot.Donated.Raffle.Setup-<version>.exe`
2. Open the installer and follow the instructions.
    > It will automatically check for Python 2.7 and Streamlabs Chatbot. If
    > either is missing, it will attempt to download and install it.
    > 
    > The checks are done via the Registry (as it's how Windows keeps track 
    > of installed programs).
3. When asked for a path, choose the install directory for the `Streamlabs 
    Chatbot.exe` file. This will ensure the script files are placed in the
    proper directory.
    
### Manual Installation Method

1. Download the [latest release zip bundle](https://github.com/bap14/Streamlabs_DonatedRaffle/releases/latest):
    `Streamlabs.Chatbot.Donated.Raffle-<version>.zip`
1. Extractthe files to `<Streamlabs Chatbot Install Dir>\Services\Scripts\DonatedRaffle`
    - `<Streamlabs Chatbot Install>` is the path to the folder that contains `Streamlabs Chatbot.exe`.
    - If you don't have a folder `DonatedRaffle` in the `Scripts` folder, create it first.
    - Within the `DonatedRaffle` folder should be (at minimum) `DonatedRaffle_StreamlabsSystem.py` and `UI_Config.json`

## Configuration Parameters

Configuration of the raffle is done via the GUI itself.  This is currently the only way to configure the raffle settings.

### General

Set the prize, entry command and permissions for the raffle here.

- **Prize** :: Set the title or prize of the raffle.
Will be used as part of some announcements in chat.
- **Command** :: Command chatters will use to enter raffle.
Default: `!raffle`
- **Permission To Enter** :: Who is allowed to purchase entires for the
raffle. Default: `Everyone`
- **Permission Info** :: Used with specific *Permission To Enter* values
to specify who can enter the raffle.
- **Winner List Keyword** :: Keyword chat can use after the raffle has
ended to recall list of winners. Default: `winners`
- **Winner List Permission** :: Who is allowed to recall list of winners
for the raffle. Default: `Everyone`
- **Winner List Permission Info** :: Used with specific *Winner List
Permission* values to specify who can recall the list.

### Raffle Settings

Configure the raffle and its winnings here.

- **Entry Cost** :: How much entering the raffle will cost, per entry.
Default: `0`
- **Maximum Entries** :: Total entries one person can purchse for
themselves or for another person. Default: `1`
- **Enable Donations** :: Allow users to donate their entries to another
viewer. Default: `False`
- **Allow Multiple Donations** :: Allow users to donate entries to
multiple people. Max per-person donation is limited by *Maximum
Entries*. Default: `False`
- **Enable Timer** :: Enable ability for raffle to close automatically
after *Raffle Entry Period*. Default: `False`
- **Raffle Entry Period** :: Amount of seconds raffle should stay open.
Default: `300` (5 minutes)
- **Give Currency As Prize** :: Automatically award a set currency
amount to winners upon choosing them. Default: `False`
- **Currency Giveaway Amount** :: Amount of currency to award winners if
*Give Currency As Prize* is enabled. Default: `1000`

### Messages

This section configures the messages Streamlabs Chatbot will send in
response to different actions it takes.  Placeholders are available to
fill in data about the raffle.

- **Raffle Open** :: "A raffle for: {0} has started! {1} can enter!"
  - `{0}` - *Prize*
  - `{1}` - *Permission To Enter*
- **Raffle Open (Unlimited Entries)** :: "[Entry Cost: {0}] - Use `{1} <number>` to enter"
  - `{0}` - *Entry Cost*
  - `{1}` - *Command*
- **Raffle Open (with Max Entries)** :: "Entry Cost: {0} - Maximum Entries: {1} - Use `{2} <number>` to enter"
  - `{0}` - *Cost*
  - `{1}` - *Max Entries*
  - `{2}` - *Command*
- **Donate Entries** :: "or `{0} <number> <username>` to donate entries to someone."
  - `{0}` - *Command*
- **Raffle Closed** :: "Entries have stopped for the raffle! You can no longer enter!"
- **Raffle Refunded** :: "All {0} has been refunded for the current raffle."
  - `{0}` - Currency Name
- **Raffle Winner Notification** :: "@{0}, you have won (with {1} entries)! Speak up in chat!"
  - `{0}` - Winner's username
  - `{1}` - Total number of chances winner had in raffle
  - `{2}` - *Currency Giveaway Amount* value
  - `{3}` - Currency Name
- **Multiple Winner Notification** :: "{0} you have all won! Please speak up in chat!"
  - `{0}` - Listing of tagged usernames that are in the full winners list
  - `{1}` - *Currency Giveaway Amount* value
  - `{2}` - Currency Name
- **Not Enough Currency** :: "@{0} you don't have enough {1}!"
  - `{0}` - The user trying to purchase entries
  - `{1}` - Currency Name
- **Maximum Entries Response** :: "@{0} You are only able to purchase up to {1} entries."
  - `{0}` - User trying to purchase entries
  - `{1}` - *Maximum Entries*
- **Multiple Donations Disabled** :: "@{0}, you can only donate entries to one person"
  - `{0}` - User trying to purchase entries
- **Entry Donations Disabled** :: "@{0}, donating entries is not enabled."
  - `{0}` - User trying to purchase entries
- **Can Not Donate To Self Notification** :: "You cannot donate entires to yourself."
- **Close Raffle Before Picking Winners Notification** :: "You must close the raffle before choosing winners."
- **No Entrants Notification** :: "There are no entrants to choose from."
- **Recent Winner Listing** :: "@{0}, the winners of the last raffle were: {1}"
  - `{0}` - User running *Command* to retrieve winner list

### Management

These items follow the same idea as most of the items above.  The
*Raffle Management Command* is first, followed by a keyword, then any
other parameters.

- **Raffle Management Command** :: Command used with keywords below
to manage raffle settings via chat. Default: `!manageraffle`
- **Management Permission Level** :: Permission required to manage the
raffle via chat. Default: `Editor`
- **Management Permission Info** :: Extra permission info to specify
user(s) allowed to manage raffle via chat.
- **Keyword To Clear Recent Winners** :: Clear recent winners list. Can
be used to pull "alternate" winner list for competing teams.
Default: `clear`
- **Keyword To Close Raffle** :: Close the currently open raffle.
Default: `close`
- **Keyword To Open Raffle** :: Open the currently configured raffle.
Default: `open`
- **Keyword To Pick Winner(s)** :: Pick a winner. Optionally add the
number of winners to choose after.
Default: `pick`
- **Save Snapshot Keyword** :: Keyword to use to save a snapshot of the
currently configured raffle settings. Default: `save`
  - Anything following the `save` keyword is interpreted as the snapshot
  name and is used as the filename.
- **Load Snapshot Keyword** :: Load saved snapshot and replace current
configured settings with the saved settings. Default: `load`
  - The string after the `load` keyword will be interpreted as the name
  of the snapshot to load.

##### Management Command Examples

- **Open A Raffle** => `!manageraffle open`
- **Close The Raffle** => `!manageraffle close`
- **Pick 3 Winners From Current Raffle** => `!manageraffle pick 3`
- **Reset the winners (to pick a "B" list)** => `!manageraffle clear`
- **Refund All Entrants** => `!manageraffle refund`
- **Reset Raffle To Initial State** => `!manageraffle reset`
- **Save Snapshot** => `!manageraffle save this is my snapshot`
- **Load Snapshot** => `!manageraffle load this is my snapshot`

### Buttons

The buttons section should be self-explanatory. Click a button and the
corresponding action is executed on the raffle (if applicable).

## Support

If you use this script and would like to support further development, you can send donations / tips [via PayPal](https://www.paypal.me/bleepblambleep)

## Notes

1. Streamlabs Chatbot will not always respond to every request immediately.
There is a 2-second cooldown on sending messages.  This will be very
apparent if you use the management command to choose multiple winners and
the setting "Announce Winners Individually" is enabled. The names will 
appear as separate messages in chat.

# Version History

## 0.0.1.3

- Fix donated entries not being case insensitive

## 0.0.1.2

- Case sensitivity and other fixes

## 0.0.1.1

- Add currency giveaway amount to winner notification(s)

## 0.0.1

Initial release of script.

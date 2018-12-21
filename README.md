# Legend-Cogs
<img src="https://imgur.com/fw6Mmwl.png">

[<img src="https://discordapp.com/api/guilds/374596069989810176/widget.png?style=shield">](http://discord.gg/T7XdjFS) [<img src="https://img.shields.io/badge/discord-py-blue.svg">](https://github.com/Rapptz/discord.py)

Made with Python and [RED](https://github.com/Cog-Creators/Red-DiscordBot).

If you want to see this bot in action, join the LeGeND Family Discord at [legendclans.com/discord](http://discord.gg/T7XdjFS)


## Cogs

 * **crtools** - Clash Royale Tools required for most CR cogs to work.
 * **brawlstars** - Brawl Stars band info, profile info and event info.
 * **clashroyale** - Clash Royale clan info, profile info, chest cycle and shop offers.
 * **drafting** - Interactive draft royale cog, pick cards using emojis and create brackets.
 * **legend** - Management system for Legend Clash Royale Family. Used for recruits.
 * **legendbs** - Management system for Legend Brawl Stars Family. Used for recruits.
 * **profanity** - filter and delete message that contain bad words.
 * **tourney** - Clash Royale open tournament finder.
 * **shop** - reward people for donations in credits.
 * **friendlink** - Convert Clash Royale Friend Links to Beautiful Embeds.
 * **clanchest** - Clan Chest Leaderboard for a clan family. (obsolete)
 * **challenges** - Emoji, word and math question challenges.
 * **heist** - Clash Royale Themed Heist cog with additional features, port from Jumper-Cogs.
 * **russianroulette** - Russian Roullete styled game with additional features, port from Jumper-Cogs.
 * **giveaway** - Reaction based giveaway cog for credits and other prizes, port from Jumper-Cogs.
 * **race** - Animal race with additional features, port from Jumper-Cogs.
 * **fourinarow** - Four in a row game with additional features, post from Red-Cogs.
 * **academy** - Coaching command for LeGeND Family.
 * **deck** - Clash Royale deck management system with additional features, port from SML-Cogs.
 * **duels** - Clash Royale 1v1 duels with credit bets with its own elo system.
 * **warlog** - Clash Royale Clan War Logs using images.
 * **warbattles** - Clash Royale Clan War Attack Logs using images. (deck cog required)
 * **fmod** - Advanced Warning system by RSNFreud.
 * **stats** - Count Server Statistics on a Voice Channel.
 * **logging** - log messages and reactions to a database.
 * **seen** - Check when a user was last seen, port from aikaterna-cogs.
 * **welcome** - Welcome a user with an interactive menu.


## Installation

To install a cog on your bot instance:

### 1. Add the repo

`[p]cog repo add Legend-Cogs https://github.com/Gr8z/Legend-Cogs`

### 2. Add the cog you want to install

`[p]cog install Legend-Cogs clashroyale`

[p] = Replace this with your bot's command prefix. (usually '!')


## FAQ

### Why does it say "Cannot reach Clash Royale servers?"

Make sure you have set your Official Clash Royale API Token from https://developer.clashroyale.com using the [p]settokencr.

### Why are some cogs not loading?

Many cogs depend on additional python libraries, and also other cogs. If you want to install a clash royale cog, make sure you have crtools installed first.

### Why are my cogs getting unloaded after restart?

Some of your clash royale cogs might get disabled on restart because it requires crtools to be loaded first. To fix this:

* Go to your bot's root folder and open `red.py`
* look for ``bot.load_extension('cogs.owner')``
* Then add this line after: ``bot.load_extension('cogs.crtools')``



## Credits

* [RED](https://github.com/Cog-Creators/Red-DiscordBot)
* [RoyaleAPI](https://github.com/royaleapi)
* [clashroyale](https://github.com/cgrok/clashroyale)
* [AtomToast](https://github.com/AtomToast)
* [SML](https://github.com/smlbiobot)
* [fourjr](https://github.com/fourjr)
* [Bobloy](https://github.com/bobloy)
* [Joshua](https://github.com/yeongjoshua)
* [SauravAnchlia](https://github.com/SauravAnchlia)
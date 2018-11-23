import discord
from discord.ext import commands
from cogs.utils import checks
import asyncio
import clashroyale
import time
from datetime import datetime
import requests
import json

try:
    from cogs.deck import Deck
except:
    print("Deck Cog not found, please do '!cog install Legend-Cogs deck'")

creditIcon = "https://i.imgur.com/TP8GXZb.png"
credits = "Bot by GR8 | Titan"


class warbattles:
    """Clash Royale Clan War attack log"""

    def __init__(self, bot):
        self.bot = bot
        self.auth = self.bot.get_cog('crtools').auth
        self.clans = self.bot.get_cog('crtools').clans
        self.constants = self.bot.get_cog('crtools').constants
        self.deck = Deck(self.bot)
        self.clash = clashroyale.OfficialAPI(self.auth.getOfficialToken(), is_async=True, timeout=20)
        self.moment = time.time()
        self.completed = [[], []]

    async def compareDeck(self, team, opp):
        """Check if both decks are similar"""
        deck1, deck2 = [], []

        for x in range(0, 8):
            deck1 = team[0].name
            deck2 = opp[0].name

        diff = len(set(deck1) - set(deck2))
        if diff > 3:
            return False
        return True

    async def deckStrength(self, team, opp):
        """Check if deck if underleveled or not"""
        teamCards = 0
        oppCards = 0

        for x in range(0, 8):
            teamCards += await self.constants.get_new_level(team[x])
            oppCards += await self.constants.get_new_level(opp[x])

        diff = oppCards - teamCards
        return '{0:{1}}'.format(diff, '+' if diff else '')

    async def cleanTime(self, time):
        """Converts time to timestamp"""
        return int(datetime.strptime(time, '%Y%m%dT%H%M%S.%fZ').timestamp()) + 3600

    async def get_clan_battles(self, clankey):
        """ Get war battles from each clan member"""
        battles = []
        members = list(self.clans.keysClanMembers(clankey))
        for member in members:
            battles += await self.clash.get_player_battles(member)
            await asyncio.sleep(0.08)
        return battles

    @commands.command(pass_context=True)
    @checks.is_owner()
    async def warbattles(self, ctx):
        """War battle catcher with practice count, run in scedule"""
        for clankey in self.clans.keysClans():
            channel = await self.clans.getClanData(clankey, 'warlog_channel')
            if ((channel is not None) and (clankey not in self.completed[0])):
                try:
                    clanBattles = await self.get_clan_battles(clankey)
                except clashroyale.RequestError:
                    print("WARBATTLES: Cannot reach Clash Royale Servers.")
                    return

                for battle in clanBattles:
                    battledata = {"train": 0, "time": await self.cleanTime(battle.battle_time)}
                    if battledata["time"] > self.moment:
                        if battle.type == "clanWarWarDay" and (battledata["time"] not in self.completed[1]):
                            battledata["tag"] = battle.team[0].tag.strip("#")
                            battledata["name"] = battle.team[0].name
                            battledata["deckLink"] = await self.constants.decklink_url(battle.team[0].cards)
                            battledata["deckLevels"] = await self.deckStrength(battle.team[0].cards,
                                                                               battle.opponent[0].cards)
                            battledata["trophies"] = battle.opponent[0].starting_trophies - battle.team[0].starting_trophies

                            for pracBattle in clanBattles:
                                if pracBattle.team[0].tag.strip('#') == battledata["tag"]:
                                    if pracBattle.type not in ["clanWarWarDay", "PvP"]:
                                        pracTime = await self.cleanTime(pracBattle.battle_time)
                                        if (pracTime < battledata["time"]) and (self.moment - pracTime < 86400):
                                            if await self.compareDeck(pracBattle.team[0].cards, battle.team[0].cards):
                                                battledata["train"] += 1

                            battle.winner = battle.team[0].crowns - battle.opponent[0].crowns
                            if battle.winner >= 1:
                                battledata["wintext"] = "War Day Victory"
                                battledata["winicon"] = "https://royaleapi.com/static/img/ui/cw-war-win.png"
                                battledata["wincolor"] = discord.Color.green()
                            else:
                                battledata["wintext"] = "War Day Defeat"
                                battledata["winicon"] = "https://royaleapi.com/static/img/ui/cw-war-loss.png"
                                battledata["wincolor"] = discord.Color.red()

                            embed = discord.Embed(title="", description=battledata["wintext"], color=battledata["wincolor"])
                            embed.set_author(name=battledata["name"] + " (#"+battledata["tag"]+")",
                                             icon_url=await self.constants.get_clan_image(battle.team[0]))
                            embed.set_thumbnail(url=battledata["winicon"])
                            embed.add_field(name="Opponent Trophies",
                                            value='{0:{1}}'.format(battledata["trophies"], '+' if battledata["trophies"] else ''),
                                            inline=True)
                            embed.add_field(name="Opponent Card Levels", value=battledata["deckLevels"], inline=True)
                            embed.add_field(name="Practices", value=battledata["train"], inline=True)
                            embed.add_field(name="Deck Link",
                                            value="[Copy to war deck]({}&ID={}&war=1)".format(battledata["deckLink"],
                                                                                              battledata["tag"]), inline=True)
                            embed.set_footer(text=credits, icon_url=creditIcon)

                            await self.bot.send_message(discord.Object(id=channel), embed=embed)

                            if clankey == "titan":
                                battledata["wincolor"] = None
                                url = 'https://script.google.com/macros/s/AKfycbx8idfEQE2ochft4vKg7um0VVZ16_li5AnRvDQZHhyLimJjvlw/exec'
                                requests.post(url, data=json.dumps(battledata))

                            card_keys = await self.deck.decklink_to_cards(battledata["deckLink"])
                            newctx = ctx
                            newctx.message.channel = discord.Object(id=channel)
                            await self.deck.upload_deck_image(newctx, card_keys, 'War Deck')

                            self.completed[1].append(battledata["time"])
                self.completed[0].append(clankey)
                await asyncio.sleep(1)
        self.completed = [[], []]
        self.moment = time.time()


def setup(bot):
    bot.add_cog(warbattles(bot))

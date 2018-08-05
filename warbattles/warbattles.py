import discord
from discord.ext import commands
from cogs.utils import checks
import asyncio
import clashroyale
import time

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
        self.deck = Deck(self.bot)
        self.clash = clashroyale.RoyaleAPI(self.auth.getToken(), is_async=True, timeout=20)
        self.moment = time.time()
        self.completed = [[], []]

    async def getLevels(self, deck):
        """Get common, rare, epic, legendary levels"""
        levels = 0
        for card in deck:
            if card.rarity == "Common":
                levels += card.level
            if card.rarity == "Rare":
                levels += card.level + 3
            if card.rarity == "Epic":
                levels += card.level + 6
            if card.rarity == "Legendary":
                levels += card.level + 9

        return levels

    async def deckStrength(self, team, opp):
        """Check if deck if underleveled or not"""
        perc = round((1 - (team / opp)) * 100, 2)
        return '{0:{1}}%'.format(perc, '+' if perc else '')

    @commands.command(pass_context=True)
    @checks.is_owner()
    async def warbattles(self, ctx):
        """War battle catcher with practice count, run in scedule"""
        for clankey in self.clans.keysClans():
            channel = await self.clans.getClanData(clankey, 'warlog_channel')
            if ((channel is not None) and (clankey not in self.completed[0])):
                try:
                    clanBattles = await self.clash.get_clan_battles(await self.clans.getClanData(clankey, 'tag'), type="war")
                except clashroyale.RequestError:
                    print("WARBATTLES: Cannot reach Clash Royale Servers.")
                    return

                for battle in clanBattles:
                    battledata = {"train": 0, "time": battle.utc_time}
                    if battledata["time"] > self.moment:
                        if battle.type == "clanWarWarDay" and (battledata["time"] not in self.completed[1]):
                            battledata["tag"] = battle.team[0].tag
                            battledata["name"] = battle.team[0].name
                            battledata["deckLink"] = battle.team[0].deck_link
                            battledata["deckLevels"] = await self.deckStrength(await self.getLevels(battle.team[0].deck),
                                                                               await self.getLevels(battle.opponent[0].deck))
                            battledata["trophies"] = battle.opponent[0].startTrophies - battle.team[0].startTrophies

                            try:
                                playerBattles = await self.clash.get_player_battles(battledata["tag"])
                            except clashroyale.RequestError:
                                print("WARBATTLES: Cannot reach Clash Royale Servers.")
                                return

                            for pracBattle in playerBattles:
                                if ((pracBattle.type != "clanWarWarDay") and (pracBattle.utc_time < battledata["time"])):
                                    if (pracBattle.team[0].deck_link == battledata["deckLink"]) and (pracBattle.team[0].tag == battledata["tag"]):
                                        battledata["train"] += 1

                            if battle.winner >= 1:
                                battledata["wintext"] = "War Day Victory"
                                battledata["winicon"] = "https://royaleapi.com/static/img/ui/cw-war-win.png"
                                battledata["wincolor"] = discord.Color.green()
                            else:
                                battledata["wintext"] = "War Day Defeat"
                                battledata["winicon"] = "https://royaleapi.com/static/img/ui/cw-war-loss.png"
                                battledata["wincolor"] = discord.Color.red()

                            embed = discord.Embed(title="", description=battledata["wintext"], color=battledata["wincolor"])
                            embed.set_author(name=battledata["name"] + " (#"+battledata["tag"]+")", icon_url=battle.team[0].clan.badge.image)
                            embed.set_thumbnail(url=battledata["winicon"])
                            embed.add_field(name="Opponent Trophies",
                                            value='{0:{1}}'.format(battledata["trophies"], '+' if battledata["trophies"] else ''),
                                            inline=True)
                            embed.add_field(name="Opponent Card Levels", value=battledata["deckLevels"], inline=True)
                            embed.add_field(name="Practices", value=battledata["train"], inline=True)
                            embed.add_field(name="Deck Link", value="[Copy to war deck]({}&ID={}&war=1)".format(battledata["deckLink"], battledata["tag"]), inline=True)
                            embed.set_footer(text=credits, icon_url=creditIcon)

                            await self.bot.send_message(discord.Object(id=channel), embed=embed)

                            card_keys = await self.deck.decklink_to_cards(battledata["deckLink"])
                            newctx = ctx
                            newctx.message.channel = discord.Object(id=channel)
                            await self.deck.upload_deck_image(newctx, card_keys, 'War Deck')

                            self.completed[1].append(battledata["time"])
                            await asyncio.sleep(1)
                self.completed[0].append(clankey)
                await asyncio.sleep(1)
        self.completed = [[], []]
        self.moment = time.time()


def setup(bot):
    bot.add_cog(warbattles(bot))

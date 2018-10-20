import discord
from discord.ext import commands
from .utils.dataIO import dataIO, fileIO
from __main__ import send_cmd_help
import os
import clashroyale
import itertools

settings_path = "data/trade/settings.json"
cards_path = "data/trade/cards.json"

creditIcon = "https://i.imgur.com/TP8GXZb.png"
credits = "Bot by GR8 | Titan"


class Trade:
    """Clash Royale 1v1 trade with bets"""

    def __init__(self, bot):
        self.bot = bot
        self.settings = dataIO.load_json(settings_path)
        self.cards = dataIO.load_json(cards_path)
        self.auth = self.bot.get_cog('crtools').auth
        self.tags = self.bot.get_cog('crtools').tags
        self.constants = self.bot.get_cog('crtools').constants
        self.clash = clashroyale.OfficialAPI(self.auth.getOfficialToken(), is_async=True)

        # init card data
        self.cards_abbrev = {}

        for k, v in self.cards.items():
            for value in v:
                self.cards_abbrev[value] = k
            self.cards_abbrev[k] = k

    def emoji(self, name):
        """Emoji by name."""
        for emoji in self.bot.get_all_emojis():
            if emoji.name == name.replace(" ", "").replace("-", "").replace(".", ""):
                return '<:{}:{}>'.format(emoji.name, emoji.id)
        return ''

    def grouper(self, iterable, n):
        args = [iter(iterable)] * n
        return itertools.zip_longest(*args)

    async def saveCard(self, member, card):
        rarity = await self.constants.card_to_rarity(card)

        if member.id not in self.settings:
            self.settings[member.id] = {}
            self.settings[member.id]["Legendary"] = []
            self.settings[member.id]["Epic"] = []
            self.settings[member.id]["Rare"] = []
            self.settings[member.id]["Common"] = []

        if card not in self.settings[member.id][rarity]:
            self.settings[member.id][rarity].append(card)
        dataIO.save_json(settings_path, self.settings)

    async def removeCard(self, member, card):
        rarity = await self.constants.card_to_rarity(card)

        if member.id not in self.settings:
            self.settings[member.id] = {}
            self.settings[member.id]["Legendary"] = []
            self.settings[member.id]["Epic"] = []
            self.settings[member.id]["Rare"] = []
            self.settings[member.id]["Common"] = []

        if card in self.settings[member.id][rarity]:
            self.settings[member.id][rarity].remove(card)
        dataIO.save_json(settings_path, self.settings)

    async def tradeCards(self, cards):
        trades = {
            "Legendary": [],
            "Epic": [],
            "Rare": [],
            "Common": []
        }

        for card in cards:
            if card.max_level == 13:
                if card.count > 250:
                    trades["Common"].append(card.name)
            elif card.max_level == 11:
                if card.count > 50:
                    trades["Rare"].append(card.name)
            elif card.max_level == 8:
                if card.count > 10:
                    trades["Epic"].append(card.name)
            elif card.max_level == 5:
                if card.count > 1:
                    trades["Legendary"].append(card.name)
        return trades

    @commands.group(pass_context=True, no_pm=True)
    async def trade(self, ctx,):
        """Clash Royale trade commands"""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)

    @trade.command(pass_context=True, no_pm=True)
    async def show(self, ctx, member: discord.Member=None):
        """Show cards you can trade"""
        member = member or ctx.message.author
        giveset = False

        await self.bot.type()

        try:
            profiletag = await self.tags.getTag(member.id)
            profiledata = await self.clash.get_player(profiletag)
            rarities = await self.tradeCards(profiledata.cards)
        except clashroyale.RequestError:
            return await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")
        except KeyError:
            return await self.bot.say("You need to first save your profile using ``{}save #GAMETAG``".format(ctx.prefix))

        embed = discord.Embed(color=0xFAA61A, description="Cards available for trade.")
        embed.set_author(name=profiledata.name + " ("+profiledata.tag+")",
                         icon_url=await self.constants.get_clan_image(profiledata),
                         url="https://royaleapi.com/player/"+profiledata.tag.strip("#"))
        embed.set_footer(text=credits, icon_url=creditIcon)

        for rarity in rarities.keys():
            f_title = rarity
            groups = self.grouper(rarities[rarity], 30)
            for index, cards in enumerate(groups):
                value = "Want: "
                if member.id in self.settings:
                    giveset = True
                    for cardern in self.settings[member.id][rarity]:
                        if cardern is not None:
                            value += self.emoji(cardern)
                else:
                    value += "Type ``{}trade add`` to add cards here.".format(ctx.prefix)
                value += "\nGiving: " if index == 0 else ""
                for card in cards:
                    if card is not None:
                        if giveset:
                            if card not in self.settings[member.id][rarity]:
                                value += self.emoji(card)
                        else:
                            value += self.emoji(card)
                embed.add_field(name=f_title if index == 0 else '\u200b', value=value, inline=False)

        await self.bot.say(embed=embed)

    @trade.command(pass_context=True, no_pm=True)
    async def add(self, ctx, *, card):
        """Add a card you need for trading"""
        author = ctx.message.author
        try:
            card = self.cards_abbrev[card]
        except KeyError:
            return await self.bot.say("Error, Invalid Card")

        await self.saveCard(author, card)
        await self.bot.say("You are now looking for {}".format(self.emoji(card)))

    @trade.command(pass_context=True, no_pm=True)
    async def remove(self, ctx, *, card):
        """Remove a card you dont need for trading"""
        author = ctx.message.author
        try:
            card = self.cards_abbrev[card]
        except KeyError:
            return await self.bot.say("Error, Invalid Card")

        await self.removeCard(author, card)
        await self.bot.say("You are no longer looking for {}".format(self.emoji(card)))


def check_folders():
    if not os.path.exists("data/trade"):
        print("Creating data/trade folder...")
        os.makedirs("data/trade")


def check_files():
    f = settings_path
    if not fileIO(f, "check"):
        print("Creating trade settings.json...")
        fileIO(f, "save", {})


def setup(bot):
    check_folders()
    check_files()
    bot.add_cog(Trade(bot))

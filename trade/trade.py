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
    """Clash Royale Trading Helper"""

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

    async def defualt_settings(self, member):
        self.settings[member.id] = {}
        self.settings[member.id]["want"] = []
        self.settings[member.id]["give"] = []
        self.settings[member.id]["token"] = []

        self.settings[member.id]["want"] = {}
        self.settings[member.id]["want"]["legendary"] = []
        self.settings[member.id]["want"]["epic"] = []
        self.settings[member.id]["want"]["rare"] = []
        self.settings[member.id]["want"]["common"] = []

        self.settings[member.id]["give"] = {}
        self.settings[member.id]["give"]["legendary"] = []
        self.settings[member.id]["give"]["epic"] = []
        self.settings[member.id]["give"]["rare"] = []
        self.settings[member.id]["give"]["common"] = []

        self.settings[member.id]["token"] = {}
        self.settings[member.id]["token"]["legendary"] = False
        self.settings[member.id]["token"]["epic"] = False
        self.settings[member.id]["token"]["rare"] = False
        self.settings[member.id]["token"]["common"] = False

    async def saveCardWant(self, member, card):
        rarity = await self.constants.card_to_rarity(card)
        rarity = rarity.lower()

        if member.id not in self.settings:
            await self.defualt_settings(member)

        if card not in self.settings[member.id]['want'][rarity]:
            self.settings[member.id]['want'][rarity].append(card)
        dataIO.save_json(settings_path, self.settings)

    async def saveCardsGive(self, member, rarity, cards):
        if member.id not in self.settings:
            await self.defualt_settings(member)

        self.settings[member.id]['give'][rarity] = cards
        dataIO.save_json(settings_path, self.settings)

    async def removeCardWant(self, member, card):
        rarity = await self.constants.card_to_rarity(card)
        rarity = rarity.lower()

        if member.id not in self.settings:
            await self.defualt_settings(member)

        if card in self.settings[member.id]['want'][rarity]:
            self.settings[member.id]['want'][rarity].remove(card)
        dataIO.save_json(settings_path, self.settings)

    async def saveToken(self, member, token):
        if member.id not in self.settings:
            await self.defualt_settings(member)

        self.settings[member.id]["token"][token] = True
        dataIO.save_json(settings_path, self.settings)

    async def removeToken(self, member, token):
        if member.id not in self.settings:
            await self.defualt_settings(member)

        self.settings[member.id]["token"][token] = False
        dataIO.save_json(settings_path, self.settings)

    async def tradeCards(self, cards):
        trades = {
            "legendary": [],
            "epic": [],
            "rare": [],
            "common": []
        }

        for card in cards:
            if card.max_level == 13:
                if (card.count == 250 and card.level != 1) or (card.count > 250):
                    trades["common"].append(card.name)
            elif card.max_level == 11:
                if (card.count == 50 and card.level != 1) or (card.count > 50):
                    trades["rare"].append(card.name)
            elif card.max_level == 8:
                if (card.count == 10 and card.level != 1) or (card.count > 10):
                    trades["epic"].append(card.name)
            elif card.max_level == 5:
                if (card.count == 1 and card.level != 1) or (card.count > 1):
                    trades["legendary"].append(card.name)
        return trades

    async def searchTrades(self, card):
        rarity = await self.constants.card_to_rarity(card)
        rarity = rarity.lower()

        trades = {}
        for player in self.settings:
            trades[player] = [False, False, False]
            if card in self.settings[player]["give"][rarity]:
                trades[player][0] = True
            if card in self.settings[player]["want"][rarity]:
                trades[player][1] = True
            if self.settings[player]["token"][rarity]:
                trades[player][2] = True

        return trades

    async def sortTrades(self, trades):
        token_trades = {}
        other_trades = {}

        for player in trades:
            if trades[player][2]:
                token_trades[player] = trades[player]
            else:
                other_trades[player] = trades[player]

        return {**token_trades, **other_trades}

    @commands.group(pass_context=True, no_pm=True)
    async def trade(self, ctx):
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
            f_title = rarity.capitalize()
            groups = self.grouper(rarities[rarity], 30)
            for index, cards in enumerate(groups):
                value = "Want: "
                give = []
                if member.id in self.settings:
                    giveset = True
                    for cardern in self.settings[member.id]['want'][rarity]:
                        if cardern is not None:
                            value += self.emoji(cardern)
                else:
                    value += "Type ``{}trade add`` to add cards here.".format(ctx.prefix)
                value += "\nGiving: " if index == 0 else ""
                for card in cards:
                    if card is not None:
                        if giveset:
                            if card not in self.settings[member.id]['want'][rarity]:
                                value += self.emoji(card)
                                give.append(card)
                        else:
                            value += self.emoji(card)
                            give.append(card)
                embed.add_field(name=f_title if index == 0 else '\u200b', value=value, inline=False)
                await self.saveCardsGive(member, rarity, give)

        tokenText = ""
        if member.id in self.settings:
            for token in self.settings[member.id]["token"]:
                if self.settings[member.id]["token"][token]:
                    tokenText += self.emoji("Token" + token.capitalize())

        if not tokenText:
            tokenText = "*No Tokens*\nType ``{}trade token add`` to add tokens here.".format(ctx.prefix)
        embed.add_field(name="My Tokens", value=tokenText, inline=False)

        await self.bot.say(embed=embed)

    @trade.command(pass_context=True, no_pm=True)
    async def add(self, ctx, *, card):
        """Add a card you need for trading"""
        author = ctx.message.author
        try:
            card = self.cards_abbrev[card]
        except KeyError:
            return await self.bot.say("Error, Invalid Card")

        await self.saveCardWant(author, card)
        await self.bot.say("You are now looking for {}".format(self.emoji(card)))

    @trade.command(pass_context=True, no_pm=True)
    async def remove(self, ctx, *, card):
        """Remove a card you dont need for trading"""
        author = ctx.message.author
        try:
            card = self.cards_abbrev[card]
        except KeyError:
            return await self.bot.say("Error, Invalid Card")

        await self.removeCardWant(author, card)
        await self.bot.say("You are no longer looking for {}".format(self.emoji(card)))

    @trade.group(pass_context=True, no_pm=True)
    async def token(self, ctx):
        """Add/Remove trade tokens"""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)

    @trade.command(pass_context=True, no_pm=True)
    async def search(self, ctx, *, card):
        """Search Trades"""
        server = ctx.message.server
        try:
            card = self.cards_abbrev[card]
        except KeyError:
            return await self.bot.say("Error, Invalid Card")

        trades = await self.searchTrades(card)
        embed = discord.Embed(color=0xFAA61A, description="We found these members who match your card search.")
        embed.set_author(name="{} Traders".format(card),
                         icon_url="https://i.imgur.com/dtSMITE.jpg")
        embed.set_thumbnail(url="https://royaleapi.github.io/cr-api-assets/cards/{}.png".format(card.replace(" ", "-").lower()))
        embed.set_footer(text=credits, icon_url=creditIcon)

        trades = await self.sortTrades(trades)
        givers = "\u200b"
        wanters = "\u200b"
        for player in trades:
            try:
                if trades[player][0]:
                    member = server.get_member(player)
                    givers += "• {} ".format(member.display_name)
                    if trades[player][2]:
                        givers += self.emoji("Token" + await self.constants.card_to_rarity(card))
                    givers += "\n"
                if trades[player][1]:
                    member = server.get_member(player)
                    wanters += "• {} ".format(member.display_name)
                    if trades[player][2]:
                        wanters += self.emoji("Token" + await self.constants.card_to_rarity(card))
                    wanters += "\n"
            except AttributeError:
                pass

        if len(givers) > 1024:
            givers = givers[:1000-len(givers)] + "..."
        embed.add_field(name="Giving {}".format(card), value=givers + "\n\u200b", inline=False)

        if len(wanters) > 1024:
            wanters = wanters[:1000-len(wanters)] + "..."
        embed.add_field(name="Want {}".format(card), value=wanters, inline=False)

        await self.bot.say(embed=embed)

    @token.command(pass_context=True, no_pm=True, name="add")
    async def add_token(self, ctx, *, token):
        """Add a trade token"""
        author = ctx.message.author
        token = token.lower()
        try:
            await self.saveToken(author, token)
        except KeyError:
            return await self.bot.say("Error, Invalid Token")

        await self.bot.say("You now have a {}".format(self.emoji("Token" + token.capitalize())))

    @token.command(pass_context=True, no_pm=True, name="remove")
    async def remove_token(self, ctx, *, token):
        """Remove a trade token"""
        author = ctx.message.author
        token = token.lower()
        try:
            await self.removeToken(author, token)
        except KeyError:
            return await self.bot.say("Error, Invalid Token")

        await self.bot.say("You no longer have a {}".format(self.emoji("Token" + token.capitalize())))


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

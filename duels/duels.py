# Game made by GR8 from Legend Family.

import discord
from discord.ext import commands
from .utils.dataIO import dataIO, fileIO
from __main__ import send_cmd_help
import os
import asyncio
import time
from operator import itemgetter
import clashroyale
from datetime import datetime

settings_path = "data/duels/settings.json"
creditIcon = "https://i.imgur.com/TP8GXZb.png"
credits = "Bot by GR8 | Titan"


class duels:
    """Clash Royale 1v1 Duels with bets"""

    def __init__(self, bot):
        self.bot = bot
        self.settings = dataIO.load_json(settings_path)
        self.auth = self.bot.get_cog('crtools').auth
        self.tags = self.bot.get_cog('crtools').tags
        self.constants = self.bot.get_cog('crtools').constants
        self.clash = clashroyale.OfficialAPI(self.auth.getOfficialToken(), is_async=True)
        self.active = False

    def elo_rating(self, A, B, score, k=32):
        """
        Calculate the new Elo rating for a player
        """

        exp = 1 / (1 + 10 ** ((B - int(A)) / 400))
        return max(0, int(A + k * (score - exp)))

    def account_check(self, id):
        """Check if there is an account made"""
        try:
            REG_USERS = self.settings["USERS"]
            data = True
        except:
            data = False
        if data:
            if id in REG_USERS:
                return True
            else:
                return False
        else:
            return False

    def bank_check(self, user, amount):
        bank = self.bot.get_cog('Economy').bank
        if bank.account_exists(user):
            if bank.can_spend(user, amount):
                return True
            else:
                return False
        else:
            return False

    async def get_rankings(self, ctx, userId=None):
        """Retuns a list of top scores"""
        user = ctx.message.author
        # Get all earned points of players.
        topScore = []
        if len(self.settings["USERS"]) >= 1:
            for p in self.settings["USERS"]:
                points = self.settings["USERS"][p]["SCORE"]
                userName = self.settings["USERS"][p]["NAME"].encode("ascii", errors="ignore").decode()
                topScore.append((p, points, userName.split('|', 1)[0]))
            topScore = sorted(topScore, key=itemgetter(1), reverse=True)
        # Get player rank.
        userIdRank = 0
        for index, p in enumerate(topScore):
            if p[0] == user.id:
                userIdRank = index+1
                break
        return {"topScore": topScore, "userIdRank": userIdRank}

    def emoji(self, name):
        """Emoji by name."""
        for emoji in self.bot.get_all_emojis():
            if emoji.name == name:
                return '<:{}:{}>'.format(emoji.name, emoji.id)
        return ''

    async def cleanTime(self, time):
        """Converts time to timestamp"""
        return int(datetime.strptime(time, '%Y%m%dT%H%M%S.%fZ').timestamp()) + 7200

    async def battleWinner(self, battle):
        """Gets the winner of the battle, with the difference in crowns"""
        return battle.team[0].crowns - battle.opponent[0].crowns

    @commands.group(pass_context=True, no_pm=True)
    async def duel(self, ctx):
        """Play a duel in clashroyale"""

        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)

    @duel.command(pass_context=True)
    async def register(self, ctx):
        """Register to play duels"""
        author = ctx.message.author

        await self.bot.type()

        bank = self.bot.get_cog('Economy').bank
        if not bank.account_exists(author):
            return await self.bot.say("You need to first open a bank account using ``{}bank register``".format(ctx.prefix))

        if not self.account_check(author.id):
            try:
                player_tag = await self.tags.getTag(author.id)
            except KeyError:
                return await self.bot.say("You need to first save your profile using ``{}save clash #GAMETAG``".format(ctx.prefix))

            self.settings["USERS"][author.id] = {
                "WON": 0,
                "SCORE": 0,
                "DUELID": "0",
                "ID": author.id,
                "NAME": author.display_name,
                "TAG": player_tag
            }
            fileIO(settings_path, "save", self.settings)

            embed = discord.Embed(color=discord.Color.green())
            avatar = author.avatar_url if author.avatar else author.default_avatar_url
            embed.set_author(name='{} has been registered to play duels.'.format(author.display_name), icon_url=avatar)

            await self.bot.say(embed=embed)
        else:
            await self.bot.say("{} You are already registered!".format(author.mention))

    @duel.command(pass_context=True)
    @commands.cooldown(1, 5, commands.BucketType.server)
    async def start(self, ctx, bet: int, member: discord.Member=None):
        """Start a duel with bets"""
        author = ctx.message.author
        server = ctx.message.server

        if self.active:
            return await self.bot.say("Another duel is already in progress, type ``{}duel accept``.".format(ctx.prefix))

        if bet < 2000:
            return await self.bot.say("Your bet is too low, minimum credits for a duel are 2000.")

        if bet > 900000:
            return await self.bot.say("Your bet is too high, maximum credits for a duel are 900000.")

        if not self.bank_check(author, bet):
            return await self.bot.say("You do not have {} credits to bet on this duel.".format(str(bet)))

        if not self.account_check(author.id):
            return await self.bot.say("You need to register before starting a duel, type ``{}duel register``.".format(ctx.prefix))

        if member is None:
            privateDuel = None
        else:
            privateDuel = member.id

        if author.id == privateDuel:
            return await self.bot.say("I can't let your duel yourself, go and pick someone else.")

        if privateDuel == self.bot.user.id:
            return await self.bot.say("I don't play Clash Royale, If i did you wouldn't stand a chance.")

        duelPlayer = self.settings['USERS'][author.id]

        await self.bot.type()

        try:
            profiledata = await self.clash.get_player(duelPlayer['TAG'])
        except clashroyale.RequestError:
            return await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")

        self.active = True

        arenaFormat = profiledata.arena.name.replace(' ', '').lower()

        embed = discord.Embed(color=0x0080ff)
        embed.set_author(name=profiledata.name + " ("+profiledata.tag+")", icon_url=await self.constants.get_clan_image(profiledata))
        embed.set_thumbnail(url="https://imgur.com/9DoEq22.jpg")
        embed.add_field(name="Duel Wins", value="{} {}".format(self.emoji("battle"), duelPlayer['WON']), inline=True)
        embed.add_field(name="Duel Score", value="{} {}".format(self.emoji("crtrophy"), duelPlayer['SCORE']), inline=True)
        embed.add_field(name="Trophies", value="{} {:,}".format(self.emoji(arenaFormat), profiledata.trophies), inline=True)
        if profiledata.clan is not None:
            embed.add_field(name="Clan {}".format(profiledata.role.capitalize()),
                            value="{} {}".format(self.emoji("clan"), profiledata.clan.name), inline=True)
        embed.set_footer(text=credits, icon_url=creditIcon)

        if privateDuel is None:
            role_name = "Duels"
            if role_name is not None:
                duels_role = discord.utils.get(server.roles, name=role_name)
                if duels_role is None:
                    await self.bot.create_role(server, name=role_name)
                    duels_role = discord.utils.get(server.roles, name=role_name)

            await self.bot.edit_role(server, duels_role, mentionable=True)
            await self.bot.say(content=("[{}] {} wants to duel one of you in Clash Royale "
                                        "for {} credits, type ``{}duel accept`` the offer.".format(duels_role.mention,
                                                                                                   author.mention,
                                                                                                   bet,
                                                                                                   ctx.prefix)), embed=embed)
            await self.bot.edit_role(server, duels_role, mentionable=False)
        else:
            await self.bot.say(content=("{} wants to duel {} in Clash Royale "
                                        "for {} credits, type ``{}duel accept`` the offer.".format(author.mention,
                                                                                                   member.mention,
                                                                                                   bet,
                                                                                                   ctx.prefix)), embed=embed)
        duelID = str(int(time.time()))
        self.settings["DUELS"][duelID] = {
            "TIME": duelID,
            "PLAYERS": [author.id],
            "WINNER": None,
            "BET": bet,
            "PRIVATE": privateDuel
        }
        self.settings.update({"CONFIG": {'ACTIVE': duelID}})
        fileIO(settings_path, "save", self.settings)

        bank = self.bot.get_cog('Economy').bank
        bank.withdraw_credits(author, bet)

        await asyncio.sleep(180)

        if self.settings["DUELS"].get(duelID):
            if len(self.settings["DUELS"][duelID]["PLAYERS"]) == 1:
                self.settings["DUELS"].pop(duelID)
                fileIO(settings_path, "save", self.settings)
                self.active = False

                pay = bank.get_balance(author) + bet
                bank.set_credits(author, pay)

                await self.bot.say("Duel cancelled, I guess no one is brave enough to go against {}. "
                                   "To get notified for future duels, type in ``!togglerole duels``".format(author.mention))

    @duel.command(pass_context=True)
    async def cancel(self, ctx):
        """Cancel an active duel"""
        author = ctx.message.author

        duelID = self.settings["CONFIG"]["ACTIVE"]
        if duelID not in self.settings["DUELS"]:
            return await self.bot.say("There is no active duel to cancel.")

        duelPlayers = self.settings["DUELS"][duelID]["PLAYERS"]
        duelBet = self.settings["DUELS"][duelID]["BET"]

        if duelPlayers[0] != author.id:
            return await self.bot.say("Sorry, Only the dueler can cancel his own battle.")

        self.settings["DUELS"].pop(duelID)
        fileIO(settings_path, "save", self.settings)
        self.active = False

        bank = self.bot.get_cog('Economy').bank

        for player in duelPlayers:
            user = discord.utils.get(ctx.message.server.members, id=player)
            pay = bank.get_balance(user) + duelBet
            bank.set_credits(user, pay)

        await self.bot.say("Duel cancelled!")

    @duel.command(pass_context=True)
    async def accept(self, ctx):
        """Accept a duel"""
        author = ctx.message.author

        if not self.active:
            return await self.bot.say("There is no duel active to accept, type ``{}duel start`` to start a new duel.".format(ctx.prefix))

        duelID = self.settings["CONFIG"]["ACTIVE"]
        duelPlayers = self.settings["DUELS"][duelID]["PLAYERS"]
        duelBet = self.settings["DUELS"][duelID]["BET"]
        privateDuel = self.settings["DUELS"][duelID]["PRIVATE"]

        if duelPlayers[0] == author.id:
            return await self.bot.say("Sorry, You cannot duel yourself.")

        if privateDuel is not None:
            if privateDuel is not author.id:
                return await self.bot.say("Cannot join the duel, it is set to private.")

        if not self.bank_check(author, duelBet):
            return await self.bot.say("You do not have {} credits to accept the bet on this duel.".format(str(duelBet)))

        if not self.account_check(author.id):
            return await self.bot.say("You need to register before accepting a duel, type ``{}duel register``.".format(ctx.prefix))

        if (self.settings['USERS'][duelPlayers[0]]["SCORE"] + 600) < self.settings['USERS'][author.id]["SCORE"]:
            return await self.bot.say("Sorry, your duel score is too high, ask your opponent to accept your own duel instead.")

        await self.bot.say("{} Are you sure you want to accept the bet of {} credits? (Yes/No)".format(author.mention, str(duelBet)))
        answer = await self.bot.wait_for_message(timeout=15, author=author)

        if answer is None or "yes" not in answer.content.lower():
            return

        bank = self.bot.get_cog('Economy').bank
        bank.withdraw_credits(author, duelBet)
        duelPlayers.append(author.id)

        duelPlayers = self.settings["DUELS"][duelID]["PLAYERS"]

        self.settings['USERS'][duelPlayers[0]]["DUELID"] = duelID
        self.settings['USERS'][duelPlayers[1]]["DUELID"] = duelID
        fileIO(settings_path, "save", self.settings)

        userOne = discord.utils.get(ctx.message.server.members, id=self.settings['USERS'][duelPlayers[0]]["ID"])
        userTwo = discord.utils.get(ctx.message.server.members, id=self.settings['USERS'][duelPlayers[1]]["ID"])

        self.active = False
        await self.bot.say(("**DUEL STARTED** — {} vs {} ({} credits)```"
                            "1. Send your friend links below for your opponent and spectators.\n"
                            "2. Duel each other once using friendly battle.\n"
                            "3. Type {}duel claim after the game to receive your credits.```".format(userOne.mention,
                                                                                                     userTwo.mention,
                                                                                                     str(duelBet*2),
                                                                                                     ctx.prefix)))

    @duel.command(pass_context=True)
    async def claim(self, ctx):
        """claim your prize after winning a duel"""
        author = ctx.message.author

        if not self.account_check(author.id):
            return await self.bot.say("You need to register before claiming your bet, type ``{}duel register``.".format(ctx.prefix))

        duelPlayer = self.settings['USERS'][author.id]
        duelPlayerOpp = None
        duelID = duelPlayer["DUELID"]

        if int(duelID) == 0:
            return await self.bot.say("You have no bets to collect, type ``{}duel start`` to start a new duel.".format(ctx.prefix))

        duelPlayers = self.settings["DUELS"][duelID]["PLAYERS"]
        duelBet = self.settings["DUELS"][duelID]["BET"]
        playerTags = []

        for player in duelPlayers:
            playerTags.append(self.settings['USERS'][player]["TAG"])
            if player != duelPlayer["ID"]:
                duelPlayerOpp = self.settings['USERS'][player]

        await self.bot.type()

        try:
            profiledata = await self.clash.get_player_battles(duelPlayer['TAG'])
        except clashroyale.RequestError:
            return await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")

        msg = ""
        for battle in profiledata:
            battle.winner = await self.battleWinner(battle)
            if (await self.cleanTime(battle.battle_time) > int(duelID)) and (battle.opponent[0].tag.strip("#") in playerTags):
                if battle.winner > 0:

                    duelPlayer["WON"] += 1
                    duelPlayer["SCORE"] = self.elo_rating(duelPlayer["SCORE"], duelPlayerOpp["SCORE"], 1)
                    duelPlayerOpp["SCORE"] = self.elo_rating(duelPlayerOpp["SCORE"], duelPlayer["SCORE"], 0)
                    duelPlayer["DUELID"], duelPlayerOpp["DUELID"] = "0", "0"
                    self.settings["DUELS"][duelID]["WINNER"] = author.id

                    fileIO(settings_path, "save", self.settings)

                    msg = "Congratulations {}, you won the duel against **{}** and recieved **{}** credits!".format(author.mention,
                                                                                                                    battle.opponent[0].name,
                                                                                                                    str(duelBet * 2))
                    bank = self.bot.get_cog('Economy').bank
                    pay = bank.get_balance(author) + (duelBet * 2)
                    bank.set_credits(author, pay)

                    return await self.bot.say(msg)
                elif battle.winner == 0:
                    msg = "Sorry, you and **{}** tied the match, try again.".format(battle.opponent[0].name)
                    return await self.bot.say(msg)
                else:
                    msg = "Sorry {}, you lost the duel against **{}**".format(author.mention, battle.opponent[0].name)
                    return await self.bot.say(msg)

        if not msg:
            await self.bot.say("Error: Could not find the duel results, please try again later.")

    @duel.command(pass_context=True)
    async def leaderboard(self, ctx, page: int=-1):
        """Shows the 'Duel' leaderboard."""
        user = ctx.message.author
        page -= 1
        try:
            resultRankings = await self.get_rankings(ctx, user.id)
            topScore = resultRankings["topScore"]
            playerAmount = len(self.settings["USERS"])
            data = True
        except Exception as e:
            raise
            data = False
        # Put players and their earned points in to a table.
        msgHeader = "{}\n```erlang\nRank   |   Username         |  Score\n----------------------------------\n".format(user.mention)
        if data and playerAmount >= 1:
            pages = []
            totalPages = 0
            usr = 0
            userFoundPage = False
            msg = ""
            while (usr < playerAmount):
                w = usr + 10
                while (w > usr):
                    if usr >= playerAmount:
                        break
                    ul = len(topScore[usr][2])
                    sp = '                '  # 16
                    sp = sp[ul:]
                    sn = '   '
                    if usr+1 >= 10:
                        sn = '  '
                    if usr+1 >= 100:
                        sn = ' '
                    if user.id == topScore[usr][0]:
                        msg = msg+"(#{}){}| » {} |  ({})\n".format(usr+1, sn, topScore[usr][2]+sp, topScore[usr][1])
                        userFoundPage = totalPages
                    else:
                        msg = msg+"(#{}){}|   {} |  ({})\n".format(usr+1, sn, topScore[usr][2]+sp, topScore[usr][1])
                    usr += 1
                pages.append(msg)
                totalPages += 1
                msg = ""
                #usr += 1
            # Determine what page to show.
            if page <= -1:  # Show page with user.
                selectPage = userFoundPage
            elif page >= totalPages:
                selectPage = totalPages-1  # Flood -1
            elif page in range(0, totalPages):
                selectPage = page
            else:  # Show page 0
                selectPage = 0
            await self.bot.say("{}{}\nTotal players:({})\nPage:({}/{})```".format(msgHeader,
                                                                                  pages[selectPage],
                                                                                  playerAmount,
                                                                                  selectPage+1,
                                                                                  totalPages))
        else:
            await self.bot.say("`No accounts in the duel register`".format(user.mention))


def check_folders():
    if not os.path.exists("data/duels"):
        print("Creating data/duels folder...")
        os.makedirs("data/duels")


def check_files():
    f = settings_path
    if not fileIO(f, "check"):
        print("Creating duels settings.json...")
        fileIO(f, "save", {"CONFIG": {}, "USERS": {}, "DUELS": {}})


def setup(bot):
    check_folders()
    check_files()
    bot.add_cog(duels(bot))

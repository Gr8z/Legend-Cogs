# Game made by GR8 from Legend Family.

import discord
from discord.ext import commands
from cogs.utils import checks
from .utils.dataIO import dataIO, fileIO
from __main__ import send_cmd_help
import os
from copy import deepcopy
import asyncio
import time
import requests
from operator import itemgetter, attrgetter

settings_path = "data/duels/settings.json"
creditIcon = "https://i.imgur.com/TP8GXZb.png"
credits = "Bot by GR8 | Titan"

class duels:
    """Clash Royale 1v1 Duels with bets"""

    def __init__(self, bot):
        self.bot = bot
        self.settings = dataIO.load_json(settings_path)
        self.tags = dataIO.load_json('cogs/tags.json')
        self.auth = dataIO.load_json('cogs/auth.json')
        self.active = False

    async def updateClash(self):
        self.tags = dataIO.load_json('cogs/tags.json')

     # Check if there is an account made.
    def account_check(self, id):
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

    def getAuth(self):
        return {"auth" : self.auth['token']}

    def bank_check(self, user, amount):
        bank = self.bot.get_cog('Economy').bank
        if bank.account_exists(user):
            if bank.can_spend(user, amount):
                return True
            else:
                return False
        else:
            return False

    # Retuns a list of top scores.
    async def get_rankings(self, ctx, userId=None):
        user = ctx.message.author
        # Get all earned points of players.
        topScore = []
        if len(self.settings["USERS"]) >= 1:
            for p in self.settings["USERS"]:
                points = self.settings["USERS"][p]["WON"]
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
        if bank.account_exists(author) is False:
            await self.bot.say("You need to first open a bank account using ``{}bank register``".format(ctx.prefix))
            return

        await self.updateClash()

        if self.account_check(author.id) is False:

            if author.id in self.tags:
                self.settings["USERS"][author.id] = {
                    "WON" : 0,
                    "DUELID" : "0",
                    "ID" : author.id,
                    "NAME" : author.display_name,
                    "TAG" : self.tags[author.id]['tag']
                }
                fileIO(settings_path, "save", self.settings)

                embed = discord.Embed(color=discord.Color.green())
                avatar = author.avatar_url if author.avatar else author.default_avatar_url
                embed.set_author(name='{} has been registered to play duels.'.format(author.display_name), icon_url=avatar)
                await self.bot.say(embed=embed)

            else:
                await self.bot.say("You need to first save your profile using ``{}save clash #GAMETAG``".format(ctx.prefix))
        else:
            await self.bot.say("{} You are already registered!".format(author.mention))

    @duel.command(pass_context=True)
    @commands.cooldown(1, 5, commands.BucketType.server)
    async def start(self, ctx, bet : int, member: discord.Member = None):
        """Start a duel with bets"""
        author = ctx.message.author

        if self.active:
            await self.bot.say("Another duel is already in progress, type ``!duel accept``.")
            return

        if bet < 5000:
            await self.bot.say("Your bet is too low, bet a bigger number.")
            return

        if not self.bank_check(author, bet):
            await self.bot.say("You do not have {} credits to bet on this duel.".format(str(bet)))
            return

        if self.account_check(author.id) is False:
            await self.bot.say("You need to register before starting a duel, type ``{}duel register``.".format(ctx.prefix))
            return

        if member is None:
            privateDuel = None
        else:
            privateDuel = member.id


        duelPlayer = self.settings['USERS'][author.id]

        await self.bot.type()

        try:
            profiledata = requests.get('https://api.royaleapi.com/player/{}'.format(duelPlayer['TAG']), headers=self.getAuth(), timeout=10).json()
            
            self.active = True

            if profiledata['clan'] is None:
                clanurl = "https://i.imgur.com/4EH5hUn.png"
            else:
                clanurl = profiledata['clan']['badge']['image']

            embed=discord.Embed(color=0x0080ff)
            embed.set_author(name=profiledata['name'] + " (#"+profiledata['tag']+")", icon_url=clanurl)
            embed.set_thumbnail(url="https://imgur.com/jNDd0ad.png")
            embed.add_field(name="Duel Wins", value=str(duelPlayer['WON']), inline=True)
            embed.add_field(name="Trophies", value=profiledata['trophies'], inline=True)
            if profiledata['clan'] is not None:
                embed.add_field(name="Clan", value=profiledata['clan']['name'], inline=True)
            embed.add_field(name="Arena", value=profiledata['arena']['name'], inline=True)
            embed.set_footer(text=credits, icon_url=creditIcon)

            if privateDuel is None:
                await self.bot.say("{} wants to duel one of you in Clash Royale for {} credits, type ``{}duel accept`` the offer.".format(author.mention, str(bet), ctx.prefix))
            else:
                await self.bot.say("{} wants to duel {} in Clash Royale for {} credits, type ``{}duel accept`` to accept the offer.".format(author.mention, member.mention, str(bet), ctx.prefix))
                
            await self.bot.say(embed=embed)

        except:
            await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")
            return

        
        duelID = str(int(time.time()))
        self.settings["DUELS"][duelID] = {
            "TIME" : duelID,
            "PLAYERS" : [author.id],
            "WINNER" : None,
            "BET" : bet,
            "PRIVATE" : privateDuel
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

                await self.bot.say("Duel cancelled, I guess no one is brave enough to go against " + author.mention)

    @duel.command(pass_context=True)
    async def cancel(self, ctx):
        """Cancel an active duel"""
        author = ctx.message.author

        duelID = self.settings["CONFIG"]["ACTIVE"]
        duelPlayers = self.settings["DUELS"][duelID]["PLAYERS"]
        duelBet = self.settings["DUELS"][duelID]["BET"]

        if duelPlayers[0] != author.id:
            await self.bot.say("Sorry, Only the dueler can cancel his own battle.")
            return

        self.settings["DUELS"].pop(duelID)
        fileIO(settings_path, "save", self.settings)
        self.active = False

        bank = self.bot.get_cog('Economy').bank

        for player in duelPlayers:
            user = discord.utils.get(ctx.message.server.members, id = player)
            pay = bank.get_balance(user) + duelBet
            bank.set_credits(user, pay)

        await self.bot.say("Duel cancelled!")

    @duel.command(pass_context=True)
    async def accept(self, ctx):
        """Accept a duel"""
        author = ctx.message.author

        if not self.active:
            await self.bot.say("There is no duel active to accept, type ``{}duel start`` to start a new duel.".format(ctx.prefix))
            return

        duelID = self.settings["CONFIG"]["ACTIVE"]
        duelPlayers = self.settings["DUELS"][duelID]["PLAYERS"]
        duelBet = self.settings["DUELS"][duelID]["BET"]
        privateDuel = self.settings["DUELS"][duelID]["PRIVATE"]

        if privateDuel is not None:
            if privateDuel is not author.id:
                await self.bot.say("Cannot join the duel, it is set to private.")
                return

        if not self.bank_check(author, duelBet):
            await self.bot.say("You do not have {} credits to accept the bet on this duel.".format(str(duelBet)))
            return

        if self.account_check(author.id) is False:
            await self.bot.say("You need to register before accepting a duel, type ``{}duel register``.".format(ctx.prefix))
            return

        if duelPlayers[0] == author.id:
            await self.bot.say("Sorry, You cannot duel yourself.")
            return

        try:
            profiledata = requests.get('https://api.royaleapi.com/player/{},{}?keys=stats'.format(self.settings['USERS'][duelPlayers[0]]["TAG"], self.settings['USERS'][author.id]["TAG"]), headers=self.getAuth(), timeout=10).json()

            if (profiledata[0]['stats']['maxTrophies'] + 600) < profiledata[1]['stats']['maxTrophies']:
                await self.bot.say("Sorry, your trophies are too high for this duel.")
                return

        except:
            await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")
            return

        await self.bot.say("{} Are you sure you want to accept the bet of {} credits? (Yes/No)".format(author.mention, str(duelBet)))
        answer = await self.bot.wait_for_message(timeout=15, author=author)

        if answer is None:
            return
        elif "yes" not in answer.content.lower():
            return

        duelPlayers.append(author.id)

        bank = self.bot.get_cog('Economy').bank
        bank.withdraw_credits(author, duelBet)

        duelPlayers = self.settings["DUELS"][duelID]["PLAYERS"]

        self.settings['USERS'][duelPlayers[0]]["DUELID"] = duelID
        self.settings['USERS'][duelPlayers[1]]["DUELID"] = duelID
        fileIO(settings_path, "save", self.settings)

        userOne = discord.utils.get(ctx.message.server.members, id = self.settings['USERS'][duelPlayers[0]]["ID"])
        userTwo = discord.utils.get(ctx.message.server.members, id = self.settings['USERS'][duelPlayers[1]]["ID"])

        self.active = False
        await self.bot.say("**DUEL STARTED** — {} vs {} ({} credits)```1. Send your friend links below for your opponent and spectators.\n2. Duel each other once using friendly battle.\n3. Type !duel claim after the game to recieve your credits.```".format(userOne.mention, userTwo.mention, str(duelBet*2)))

    @duel.command(pass_context=True)
    async def claim(self, ctx):
        """claim your prize after winning a duel"""
        author = ctx.message.author

        if self.account_check(author.id) is False:
            await self.bot.say("You need to register before claiming your bet, type ``{}duel register``.".format(ctx.prefix))
            return

        duelPlayer = self.settings['USERS'][author.id]
        duelID = duelPlayer["DUELID"]

        if int(duelID) == 0:
            await self.bot.say("You have no bets to collect, type ``{}duel start`` to start a new duel.".format(ctx.prefix))
            return

        duelPlayers = self.settings["DUELS"][duelID]["PLAYERS"]
        duelBet = self.settings["DUELS"][duelID]["BET"]
        playerTags = []

        for player in duelPlayers:
            playerTags.append(self.settings['USERS'][player]["TAG"])

        await self.bot.type()

        try:
            profiledata = requests.get('https://api.royaleapi.com/player/{}/battles'.format(duelPlayer['TAG']), headers=self.getAuth(), timeout=10).json()
        except:
            await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")
            return

        msg = ""
        for battle in profiledata:
            if (battle["utcTime"] > int(duelID)) and (battle["opponent"][0]["tag"] in playerTags):
                if battle["winner"] > 0:

                    duelPlayer["WON"] += 1
                    duelPlayer["DUELID"] = "0"
                    self.settings["DUELS"][duelID]["WINNER"] = author.id

                    fileIO(settings_path, "save", self.settings)

                    msg = "Congratulations {}, you won the duel against **{}** and recieved **{}** credits!".format(author.mention, battle["opponent"][0]["name"], str(duelBet * 2))
                    await self.bot.say(msg)

                    bank = self.bot.get_cog('Economy').bank
                    pay = bank.get_balance(author) + (duelBet * 2)
                    bank.set_credits(author, pay)

                    return
                elif battle["winner"] == 0:
                    msg = "Sorry, you and **{}** tied the match, try again.".format(battle["opponent"][0]["name"])
                    await self.bot.say(msg)

                    return
                else:
                    msg = "Sorry {}, you lost the duel against **{}**".format(author.mention, battle["opponent"][0]["name"])

                    duelPlayer["DUELID"] = "0"
                    fileIO(settings_path, "save", self.settings)

                    await self.bot.say(msg)

                    return

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
            userIdRank = resultRankings["userIdRank"]
            playerAmount = len(self.settings["USERS"])
            data = True
        except Exception as e:
            raise
            data = False
        # Put players and their earned points in to a table.
        msgHeader = "{}\n```erlang\nRank   |   Username         |  Wins\n----------------------------------\n".format(user.mention)
        if data and playerAmount >= 1:
            pages = []
            totalPages = 0
            usr = 0
            userFound = False
            userFoundPage = False
            msg = ""
            while (usr < playerAmount):
                w=usr+10
                while (w > usr):
                    if usr >= playerAmount:
                        break
                    ul = len(topScore[usr][2])
                    sp = '                '# 16
                    sp = sp[ul:]
                    sn = '   '
                    if usr+1 >= 10: sn = '  '
                    if usr+1 >= 100: sn = ' '
                    if user.id == topScore[usr][0]:
                        msg = msg+"(#{}){}| » {} |  ({})\n".format(usr+1, sn, topScore[usr][2]+sp, topScore[usr][1])
                        userFound = True
                        userFoundPage = totalPages
                    else:
                        msg = msg+"(#{}){}|   {} |  ({})\n".format(usr+1, sn, topScore[usr][2]+sp, topScore[usr][1])
                    usr += 1
                pages.append(msg)
                totalPages += 1
                msg = ""
                usr += 1
            # Determine what page to show.
            if page <= -1:# Show page with user.
                selectPage = userFoundPage
            elif page >= totalPages:
                selectPage = totalPages-1# Flood -1
            elif page in range(0, totalPages):
                selectPage = page
            else:# Show page 0
                selectPage = 0
            await self.bot.say( "{}{}\nTotal players:({})\nPage:({}/{})```".format(msgHeader, pages[selectPage], playerAmount, selectPage+1, totalPages))
        else:
            await self.bot.say( "`No accounts in the duel register`".format(user.mention))

def check_folders():
    if not os.path.exists("data/duels"):
        print("Creating data/duels folder...")
        os.makedirs("data/duels")

def check_files():
    f = settings_path
    if not fileIO(f, "check"):
        print("Creating duels settings.json...")
        dataIO.save_json(f, {"CONFIG" : {}, "USERS" : {},"DUELS" : {}})

def setup(bot):
    check_folders()
    check_files()
    bot.add_cog(duels(bot))
import discord
from discord.ext import commands
import requests
from .utils.dataIO import dataIO, fileIO
from cogs.utils import checks
import asyncio
from fake_useragent import UserAgent
import requests_cache
import json

requests_cache.install_cache('statsroyale_cache', backend='sqlite', expire_after=300)

class shop:
    """Legend Family Shop for credits"""

    def __init__(self, bot):
        self.bot = bot
        self.banks = dataIO.load_json('data/economy/bank.json')
        self.tags = dataIO.load_json('cogs/tags.json')
        self.clans = dataIO.load_json('cogs/clans.json')

    async def updateClash(self):
        self.tags = dataIO.load_json('cogs/tags.json')

    async def _add_roles(self, member, role_names):
        """Add roles"""
        server = member.server
        roles = [discord.utils.get(server.roles, name=role_name) for role_name in role_names]
        try:
            await self.bot.add_roles(member, *roles)
        except discord.Forbidden:
            raise
        except discord.HTTPException:
            raise

    async def _remove_roles(self, member, role_names):
        """Remove roles"""
        server = member.server
        roles = [discord.utils.get(server.roles, name=role_name) for role_name in role_names]
        try:
            await self.bot.remove_roles(member, *roles)
        except:
            pass

    async def _is_member(self, member):
        server = member.server
        botcommander_roles = [discord.utils.get(server.roles, name=r) for r in ["Member", "Family Representative", "Clan Manager", "Clan Deputy", "Co-Leader", "Hub Officer", "admin"]]
        botcommander_roles = set(botcommander_roles)
        author_roles = set(member.roles)
        if len(author_roles.intersection(botcommander_roles)):
            return True
        else:
            return False
            
    async def _is_rare(self, member):
        server = member.server
        botcommander_roles = [discord.utils.get(server.roles, name=r) for r in ["Rare™"]]
        botcommander_roles = set(botcommander_roles)
        author_roles = set(member.roles)
        if len(author_roles.intersection(botcommander_roles)):
            return True
        else:
            return False
            
    async def _is_epic(self, member):
        server = member.server
        botcommander_roles = [discord.utils.get(server.roles, name=r) for r in ["Epic™"]]
        botcommander_roles = set(botcommander_roles)
        author_roles = set(member.roles)
        if len(author_roles.intersection(botcommander_roles)):
            return True
        else:
            return False

    async def _is_legendary(self, member):
        server = member.server
        botcommander_roles = [discord.utils.get(server.roles, name=r) for r in ["LeGeNDary™"]]
        botcommander_roles = set(botcommander_roles)
        author_roles = set(member.roles)
        if len(author_roles.intersection(botcommander_roles)):
            return True
        else:
            return False

    async def _is_payday(self, member):
        server = member.server
        botcommander_roles = [discord.utils.get(server.roles, name=r) for r in ["Pro Payday"]]
        botcommander_roles = set(botcommander_roles)
        author_roles = set(member.roles)
        if len(author_roles.intersection(botcommander_roles)):
            return True
        else:
            return False

    def numClans(self):
        return len(self.clans.keys())

    def bank_check(self, user, amount):
        bank = self.bot.get_cog('Economy').bank
        if bank.account_exists(user):
            if bank.can_spend(user, amount):
                return True
            else:
                return False
        else:
            return False

    async def getClan(self, clantag):
        ua = UserAgent()
        headers = {
            "User-Agent": ua.random
        }

        try:
            await self.bot.send_message(discord.Object(id=393081792824999939), "!clan "+ clantag)
            statsroyale = await self.bot.wait_for_message(timeout=5, author=discord.Object(id=345270428245164032))
            
            response = requests.get('http://statsroyale.com/clan/'+clantag+'?appjson=1', timeout=5, headers=headers, proxies=dict(http="69.39.224.129:80",))
            return response.json()
        except (requests.exceptions.Timeout, json.decoder.JSONDecodeError):
            return None
        except requests.exceptions.RequestException as e:
            return None

    @commands.command(pass_context=True, no_pm=True)
    @checks.is_owner()
    async def sendpayouts(self, ctx):
        """Payout money for clanchest and donations."""

        server = ctx.message.server
        author = ctx.message.author
        
        await self.updateClash()

        bank = self.bot.get_cog('Economy').bank
        banks = list(self.banks['374596069989810176'])

        try:
            clans = [None] * self.numClans()
            index = 0
            msg = await self.bot.say("Please wait, Fetching clan data...")
            for clan in self.clans:
                listClans = await self.getClan(self.clans[clan]["tag"])
                clans[index] = listClans
                index += 1
                await self.bot.edit_message(msg, "Please wait, Fetching clan data ("+str(index)+"/13)")
        except (requests.exceptions.Timeout, json.decoder.JSONDecodeError):
            await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")
            return
        except requests.exceptions.RequestException as e:
            await self.bot.say(e)
            return
        
        for x in range(0, len(clans)):
            for y in range(0, len(clans[x]['alliance']['members'])):

                clan_tag = clans[x]['alliance']['members'][y]['hashtag']
                clan_donations = clans[x]['alliance']['members'][y]['donations']
                clan_clanChestCrowns = clans[x]['alliance']['members'][y]['clanChestCrowns']

                for key in range(0,len(banks)):
                    if clan_tag == self.tags[banks[key]]['tag']:

                        try:
                            user = discord.utils.get(ctx.message.server.members, id = banks[key])

                            rare = await self._is_rare(user)
                            epic = await self._is_epic(user)
                            legendary = await self._is_legendary(user)

                            perCrown = 300
                            perDonation = 15

                            if rare:
                                perCrown *= 1.2
                                perDonation *= 1.2

                            if epic:
                                perCrown *= 1.35
                                perDonation *= 1.35

                            if legendary:
                                perCrown *= 1.5
                                perDonation *= 1.5

                            amount = (clan_donations*perDonation) + (clan_clanChestCrowns*perCrown)
                            pay = bank.get_balance(user) + amount
                            bank.set_credits(user, pay)

                            await self.bot.say(user.name + " - Success")

                            await self.bot.send_message(user,"Hello " + user.name + ", take these credits for the " + str(clan_donations) + " donations and " + str(clan_clanChestCrowns) + " crowns you contributed to your clan this week. (+" + str(amount) + " credits!)")
                        except Exception as e:
                            await self.bot.say(e)

    @commands.group(pass_context=True)
    async def buy(self, ctx):
        """Buy different items from the legend shop"""
        author = ctx.message.author

        await self.bot.type()

        if ctx.invoked_subcommand is None:
            await self.bot.send_file(ctx.message.channel, 'FIF5sug.png')

    @buy.command(pass_context=True, name="1")
    async def buy_1(self, ctx):


        server = ctx.message.server
        author = ctx.message.author
        legendServer = ["374596069989810176"]

        if server.id not in legendServer:
            await self.bot.say("This command can only be executed in the LeGeND Family Server")
            return

        allowed = await self._is_member(author)

        if not allowed:
            await self.bot.say("You cannot use the store, you must be a member of the family. Type !contact to ask for help.")
            return

        await self.bot.say("please contact @GR8#7968 or rakerran#7837 to purchase it for you.")

    @buy.command(pass_context=True, name="2")
    async def buy_2(self, ctx):


        server = ctx.message.server
        author = ctx.message.author
        legendServer = ["374596069989810176"]

        if server.id not in legendServer:
            await self.bot.say("This command can only be executed in the LeGeND Family Server")
            return

        allowed = await self._is_member(author)

        if not allowed:
            await self.bot.say("You cannot use the store, you must be a member of the family. Type !contact to ask for help.")
            return

        await self.bot.say("please contact @GR8#7968 or rakerran#7837 to purchase it for you.")

    @buy.command(pass_context=True, name="3")
    async def buy_3(self, ctx):

        server = ctx.message.server
        author = ctx.message.author
        legendServer = ["374596069989810176"]

        if server.id not in legendServer:
            await self.bot.say("This command can only be executed in the LeGeND Family Server")
            return

        allowed = await self._is_member(author)

        if not allowed:
            await self.bot.say("You cannot use the store, you must be a member of the family. Type !contact to ask for help.")
            return

        await self.bot.say("please contact @GR8#7968 or rakerran#7837 to purchase it for you.")

    @buy.command(pass_context=True, name="4")
    async def buy_4(self , ctx):
        """ Buy Payday Pro from the shop """
        server = ctx.message.server
        author = ctx.message.author
        legendServer = ["374596069989810176"]

        if server.id not in legendServer:
            await self.bot.say("This command can only be executed in the LeGeND Family Server")
            return

        allowed = await self._is_member(author)

        if not allowed:
            await self.bot.say("You cannot use the store, you must be a member of the family. Type !contact to ask for help.")
            return

        payday = await self._is_payday(author)

        if payday:
            await self.bot.say("You already have Pro Payday. Type !contact to ask for help.")
            return

        if self.bank_check(author, 500000):
            bank = self.bot.get_cog('Economy').bank
            pay = bank.get_balance(author) - 500000
            bank.set_credits(author, pay)
            await self._add_roles(author,["Pro Payday"])
            await self.bot.say("Congratulations, now you can get !payday every 10 minutes.")
        else:
            await self.bot.say("You do not have enough credits to buy this item. Type !contact to ask for help.")

    @buy.command(pass_context=True, name="5")
    async def buy_5(self , ctx):
        """ Buy Rare Role from the shop """
        server = ctx.message.server
        author = ctx.message.author
        legendServer = ["374596069989810176"]

        if server.id not in legendServer:
            await self.bot.say("This command can only be executed in the LeGeND Family Server")
            return

        allowed = await self._is_member(author)

        if not allowed:
            await self.bot.say("You cannot use the store, you must be a member of the family. Type !contact to ask for help.")
            return

        rare = await self._is_rare(author)
        epic = await self._is_epic(author)
        legendary = await self._is_legendary(author)

        if rare or epic or legendary:
            await self.bot.say("You already have a special role. Type !contact to ask for help.")
            return

        if self.bank_check(author, 100000):
            bank = self.bot.get_cog('Economy').bank
            pay = bank.get_balance(author) - 100000
            bank.set_credits(author, pay)
            await self._add_roles(author,["Rare™"])
            await self.bot.say("Congratulations, you are now a **Rare™**")
        else:
            await self.bot.say("You do not have enough credits to buy this role. Type !contact to ask for help.")

    @buy.command(pass_context=True, name="6")
    async def buy_6(self , ctx):
        """ Buy Epic Role from the shop """
        server = ctx.message.server
        author = ctx.message.author
        legendServer = ["374596069989810176"]

        if server.id not in legendServer:
            await self.bot.say("This command can only be executed in the LeGeND Family Server")
            return

        allowed = await self._is_member(author)

        if not allowed:
            await self.bot.say("You cannot use the store, you must be a member of the family. Type !contact to ask for help.")
            return

        rare = await self._is_rare(author)
        epic = await self._is_epic(author)
        legendary = await self._is_legendary(author)

        if not rare:
            await self.bot.say("You need to have **Rare™** to buy this role. Type !contact to ask for help.")
            return    

        if epic or legendary:
            await self.bot.say("You already have a special role. Type !contact to ask for help.")
            return

        if self.bank_check(author, 250000):
            bank = self.bot.get_cog('Economy').bank
            pay = bank.get_balance(author) - 250000
            bank.set_credits(author, pay)
            await self._remove_roles(author,["Rare™"])
            await asyncio.sleep(3)
            await self._add_roles(author,["Epic™"])
            await self.bot.say("Congratulations, you are now a **Epic™**")
        else:
            await self.bot.say("You do not have enough credits to buy this role. Type !contact to ask for help.")
        
    @buy.command(pass_context=True, name="7")
    async def buy_7(self , ctx):
        """ Buy Legendary Role from the shop """

        server = ctx.message.server
        author = ctx.message.author
        legendServer = ["374596069989810176"]

        if server.id not in legendServer:
            await self.bot.say("This command can only be executed in the LeGeND Family Server")
            return

        allowed = await self._is_member(author)

        if not allowed:
            await self.bot.say("You cannot use the store, you must be a member of the family. Type !contact to ask for help.")
            return

        rare = await self._is_rare(author)
        epic = await self._is_epic(author)
        legendary = await self._is_legendary(author)

        if not epic:
            await self.bot.say("You need to have **Epic™** to buy this role. Type !contact to ask for help.")
            return    

        if legendary:
            await self.bot.say("You are already have a special role. Type !contact to ask for help.")
            return

        if self.bank_check(author, 750000):
            bank = self.bot.get_cog('Economy').bank
            pay = bank.get_balance(author) - 750000
            bank.set_credits(author, pay)
            await self._remove_roles(author,["Epic™"])
            await asyncio.sleep(3)
            await self._add_roles(author,["LeGeNDary™"])
            await self.bot.say("Congratulations, you are now a **LeGeNDary™**")
        else:
            await self.bot.say("You do not have enough credits to buy this role. Type !contact to ask for help.")

    @buy.command(pass_context=True, name="8")
    async def buy_8(self, ctx):


        server = ctx.message.server
        author = ctx.message.author
        legendServer = ["374596069989810176"]

        if server.id not in legendServer:
            await self.bot.say("This command can only be executed in the LeGeND Family Server")
            return

        allowed = await self._is_member(author)

        if not allowed:
            await self.bot.say("You cannot use the store, you must be a member of the family. Type !contact to ask for help.")
            return

        await self.bot.say("please contact @GR8#7968 or rakerran#7837 to purchase it for you.")

def setup(bot):
    bot.add_cog(shop(bot))

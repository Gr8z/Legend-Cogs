import discord
from discord.ext import commands
import requests
from .utils.dataIO import dataIO, fileIO
from cogs.utils import checks
import asyncio
import json
import math

class shop:
    """Legend Family Shop for credits"""

    def __init__(self, bot):
        self.bot = bot
        self.banks = dataIO.load_json('data/economy/bank.json')
        self.tags = dataIO.load_json('cogs/tags.json')
        self.clans = dataIO.load_json('cogs/clans.json')
        self.auth = dataIO.load_json('cogs/auth.json')

    def getAuth(self):
        return {"auth" : self.auth['token']}

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

    @commands.command(pass_context=True, no_pm=True)
    @checks.is_owner()
    async def sendpayouts(self, ctx):
        """Payout money for clanchest and donations."""

        server = ctx.message.server
        author = ctx.message.author
        
        await self.updateClash()

        bank = self.bot.get_cog('Economy').bank
        #banks = list(self.banks['363728974821457921']) # Test Server
        banks = list(self.banks['374596069989810176'])

        try:
            clans = requests.get('http://api.cr-api.com/clan/'+','.join(self.clans[clan]["tag"] for clan in self.clans), headers=self.getAuth(), timeout=10).json()
        except (requests.exceptions.Timeout, json.decoder.JSONDecodeError):
            await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")
            return
        except requests.exceptions.RequestException as e:
            await self.bot.say(e)
            return
        
        for x in range(0, len(clans)):
            for y in range(0, len(clans[x]['members'])):

                clan_tag = clans[x]['members'][y]['tag']
                clan_donations = clans[x]['members'][y]['donations']
                clan_clanChestCrowns = clans[x]['members'][y]['clanChestCrowns']

                for key in range(0,len(banks)):
                    try:
                        if ((clan_clanChestCrowns+clan_donations) > 0) and (clan_tag == self.tags[banks[key]]['tag']):

                            try:
                                user = discord.utils.get(ctx.message.server.members, id = banks[key])

                                rare = await self._is_rare(user)
                                epic = await self._is_epic(user)
                                legendary = await self._is_legendary(user)

                                perCrown = 300
                                perDonation = 15
                                BonusMult = 1

                                if rare:
                                    BonusMult = 1.2
                                    perCrown *= BonusMult
                                    perDonation *= BonusMult

                                if epic:
                                    BonusMult = 1.35
                                    perCrown *= BonusMult
                                    perDonation *= BonusMult

                                if legendary:
                                    BonusMult = 1.5
                                    perCrown *= BonusMult
                                    perDonation *= BonusMult

                                amount = math.ceil((clan_donations*perDonation) + (clan_clanChestCrowns*perCrown))
                                pay = bank.get_balance(user) + amount
                                bank.set_credits(user, pay)
                                perc = str(math.ceil((BonusMult-1)*100))

                                await self.bot.say(user.display_name + " - Success")

                                if BonusMult > 1:
                                    await self.bot.send_message(user,"Hello " + user.name + ", take these credits*("+ perc +"% Bonus)* for the **" + str(clan_donations) + "** donations and **" + str(clan_clanChestCrowns) + "** crowns you contributed to your clan this week. (+" + str(amount) + " credits!)")
                                else:
                                    await self.bot.send_message(user,"Hello " + user.name + ", take these credits for the **" + str(clan_donations) + "** donations and **" + str(clan_clanChestCrowns) + "** crowns you contributed to your clan this week. (+" + str(amount) + " credits!)")                                    
                            except Exception as e:
                                await self.bot.say(e)
                    except:
                        pass

    @commands.command(pass_context=True, no_pm=True)
    @checks.is_owner()
    async def sendcwpayouts(self, ctx, tag):
        """Payout money for clanwar trophies."""

        server = ctx.message.server
        author = ctx.message.author
        
        await self.updateClash()

        bank = self.bot.get_cog('Economy').bank
        #banks = list(self.banks['363728974821457921']) # Test Server
        banks = list(self.banks['374596069989810176'])

        tag = tag.strip('#').upper().replace('O', '0')
        check = ['P', 'Y', 'L', 'Q', 'G', 'R', 'J', 'C', 'U', 'V', '0', '2', '8', '9']

        if any(i not in check for i in tag):
            await self.bot.say("The ID you provided has invalid characters. Please try again.")
            return

        try:
            tourney = requests.get('http://api.cr-api.com/tournaments/'+tag, headers=self.getAuth(), timeout=10).json()
        except (requests.exceptions.Timeout, json.decoder.JSONDecodeError):
            await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")
            return
        except requests.exceptions.RequestException as e:
            await self.bot.say(e)
            return
        
        for y in range(0, len(tourney['members'])):

            tourney_tag = tourney['members'][y]['tag']
            tourney_score = tourney['members'][y]['score']

            for key in range(0,len(banks)):
                try:
                    if (tourney_score > 0) and (tourney_tag == self.tags[banks[key]]['tag']):

                        try:
                            user = discord.utils.get(ctx.message.server.members, id = banks[key])

                            rare = await self._is_rare(user)
                            epic = await self._is_epic(user)
                            legendary = await self._is_legendary(user)

                            perTrophy = 100
                            BonusMult = 1

                            if rare:
                                BonusMult = 1.2
                                perTrophy *= BonusMult

                            if epic:
                                BonusMult = 1.35
                                perTrophy *= BonusMult

                            if legendary:
                                BonusMult = 1.5
                                perTrophy *= BonusMult

                            amount = math.ceil(tourney_score*perTrophy)
                            pay = bank.get_balance(user) + amount
                            bank.set_credits(user, pay)
                            perc = str(math.ceil((BonusMult-1)*100))

                            await self.bot.say(user.name + " - Success")

                            if BonusMult > 1:
                                await self.bot.send_message(user,"Hello {}, take these credits*({}% Bonus)* for the **{}** trophies you contributed to your clan in **{}**. (+{} credits!)".format(user.name, perc, str(tourney_score), tourney['name'], str(amount) ))
                            else:
                                await self.bot.send_message(user,"Hello {}, take these credits for the **{}** trophies you contributed to your clan in **{}**. (+{} credits!)".format(user.name, str(tourney_score), tourney['name'], str(amount) ))
                        except Exception as e:
                            await self.bot.say(e)
                except:
                    pass

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
            await self.bot.say("You cannot use the store, you must be a member of the family.")
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
            await self.bot.say("You cannot use the store, you must be a member of the family.")
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
            await self.bot.say("You cannot use the store, you must be a member of the family.")
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
            await self.bot.say("You cannot use the store, you must be a member of the family.")
            return

        payday = await self._is_payday(author)

        if payday:
            await self.bot.say("You already have Pro Payday.")
            return

        if self.bank_check(author, 160000):
            bank = self.bot.get_cog('Economy').bank
            pay = bank.get_balance(author) - 160000
            bank.set_credits(author, pay)
            await self._add_roles(author,["Pro Payday"])
            await self.bot.say("Congratulations, now you can get !payday every 10 minutes.")
        else:
            await self.bot.say("You do not have enough credits to buy this item.")

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
            await self.bot.say("You cannot use the store, you must be a member of the family.")
            return

        rare = await self._is_rare(author)
        epic = await self._is_epic(author)
        legendary = await self._is_legendary(author)

        if rare or epic or legendary:
            await self.bot.say("You already have a special role.")
            return

        if self.bank_check(author, 100000):
            bank = self.bot.get_cog('Economy').bank
            pay = bank.get_balance(author) - 100000
            bank.set_credits(author, pay)
            await self._add_roles(author,["Rare™"])
            await self.bot.say("Congratulations, you are now a **Rare™**")
        else:
            await self.bot.say("You do not have enough credits to buy this role.")

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
            await self.bot.say("You cannot use the store, you must be a member of the family.")
            return

        rare = await self._is_rare(author)
        epic = await self._is_epic(author)
        legendary = await self._is_legendary(author)

        if not rare:
            await self.bot.say("You need to have **Rare™** to buy this role.")
            return    

        if epic or legendary:
            await self.bot.say("You already have a special role.")
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
            await self.bot.say("You do not have enough credits to buy this role.")
        
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
            await self.bot.say("You cannot use the store, you must be a member of the family.")
            return

        rare = await self._is_rare(author)
        epic = await self._is_epic(author)
        legendary = await self._is_legendary(author)

        if not epic:
            await self.bot.say("You need to have **Epic™** to buy this role.")
            return    

        if legendary:
            await self.bot.say("You are already have a special role.")
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
            await self.bot.say("You do not have enough credits to buy this role.")

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
            await self.bot.say("You cannot use the store, you must be a member of the family.")
            return

        await self.bot.say("please contact @GR8#7968 or rakerran#7837 to purchase it for you.")

def setup(bot):
    bot.add_cog(shop(bot))

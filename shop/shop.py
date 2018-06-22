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

    async def updateBank(self):
        self.banks = dataIO.load_json('data/economy/bank.json')

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

    def clanArray(self):
        return self.clans.keys()

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
        await self.updateBank()

        bank = self.bot.get_cog('Economy').bank
        banks = list(self.banks['374596069989810176'])

        try:
            clans = requests.get('https://api.royaleapi.com/clan/'+','.join(self.clans[clan]["tag"] for clan in self.clans), headers=self.getAuth(), timeout=20).json()
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

                for key in range(0,len(banks)):
                    try:
                        if (clan_donations > 0) and (clan_tag == self.tags[banks[key]]['tag']):

                            try:
                                user = discord.utils.get(ctx.message.server.members, id = banks[key])

                                rare = await self._is_rare(user)
                                epic = await self._is_epic(user)
                                legendary = await self._is_legendary(user)

                                perDonation = 25
                                BonusMult = 1

                                if rare:
                                    BonusMult = 1.2
                                    perDonation *= BonusMult

                                if epic:
                                    BonusMult = 1.35
                                    perDonation *= BonusMult

                                if legendary:
                                    BonusMult = 1.5
                                    perDonation *= BonusMult

                                amount = math.ceil((clan_donations*perDonation))
                                pay = bank.get_balance(user) + amount
                                bank.set_credits(user, pay)
                                perc = str(math.ceil((BonusMult-1)*100))

                                await self.bot.say("{} - ({} donations)".format(user.display_name, clan_donations))

                                if BonusMult > 1:
                                    await self.bot.send_message(user,"Hello {} , take these credits*({}% Bonus)* for the **{}** donations you contributed to your clan this week. (+{} credits!)".format(user.name, perc, str(clan_donations), str(amount)))
                                else:
                                    await self.bot.send_message(user,"Hello {} , take these credits for the **{}** donations you contributed to your clan this week. (+{} credits!)".format(user.name, str(clan_donations), str(amount)))
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
        await self.updateBank()

        bank = self.bot.get_cog('Economy').bank
        #banks = list(self.banks['363728974821457921']) # Test Server
        banks = list(self.banks['374596069989810176'])

        tag = tag.strip('#').upper().replace('O', '0')
        check = ['P', 'Y', 'L', 'Q', 'G', 'R', 'J', 'C', 'U', 'V', '0', '2', '8', '9']

        if any(i not in check for i in tag):
            await self.bot.say("The ID you provided has invalid characters. Please try again.")
            return

        try:
            tourney = requests.get('https://api.royaleapi.com/tournaments/'+tag, headers=self.getAuth(), timeout=10).json()
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

                            await self.bot.say("{} - ({} trophies)".format(user.display_name, tourney_score))

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

        await self.bot.type()

        if ctx.invoked_subcommand is None:
            await self.bot.send_file(ctx.message.channel, 'FIF5sug.png')

    @buy.command(pass_context=True, name="1")
    async def buy_1(self , ctx):
        """ Buy Payday Pro from the shop """
        server = ctx.message.server
        author = ctx.message.author
        legendServer = ["374596069989810176"]

        if server.id not in legendServer:
            await self.bot.say("This command can only be executed in the LeGeND Family Server")
            return

        payday = await self._is_payday(author)

        if payday:
            await self.bot.say("You already have Pro Payday.")
            return

        if self.bank_check(author, 30000):
            bank = self.bot.get_cog('Economy').bank
            bank.withdraw_credits(author, 30000)
            await self._add_roles(author,["Pro Payday"])
            await self.bot.say("Congratulations, now you can get !payday every 10 minutes.")
        else:
            await self.bot.say("You do not have enough credits to buy this item.")

    @buy.command(pass_context=True, name="2")
    async def buy_2(self, ctx):


        server = ctx.message.server
        author = ctx.message.author
        legendServer = ["374596069989810176"]

        if server.id not in legendServer:
            await self.bot.say("This command can only be executed in the LeGeND Family Server")
            return

        if self.bank_check(author, 75000):
            await self.bot.say("please contact @GR8#7968 to purchase it for you.")
        else:
            await self.bot.say("You do not have enough credits to buy this item.")

    @buy.command(pass_context=True, name="3")
    async def buy_3(self, ctx, emoji):

        server = ctx.message.server
        author = ctx.message.author
        legendServer = ["374596069989810176"]

        if server.id not in legendServer:
            await self.bot.say("This command can only be executed in the LeGeND Family Server")
            return

        if (emoji.startswith("<:") and emoji.endswith(">")) or (emoji.startswith("<a:") and emoji.endswith(">")):
            await self.bot.say("Error, you can only use default emojis.")
            return

        try: 
            await self.bot.add_reaction(ctx.message, emoji)
        except (discord.errors.HTTPException, discord.errors.InvalidArgument):
            await self.bot.say("Error, That's not an emoji I recognize.")
            return

        if self.bank_check(author, 80000):

            try:
                await self.updateClash()
                await self.bot.type()
                profiletag = self.tags[author.id]['tag']
                profiledata = requests.get('https://api.royaleapi.com/player/{}?exclude=games,currentDeck,cards,battles,achievements'.format(profiletag), headers=self.getAuth(), timeout=10).json()
                if profiledata['clan'] is None:
                    clantag = ""
                    clanname = ""
                else: 
                    clantag = profiledata['clan']['tag']
                    clanname = profiledata['clan']['name']
                ign = profiledata['name']
            except (requests.exceptions.Timeout, json.decoder.JSONDecodeError):
                await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")
                return
            except requests.exceptions.RequestException as e:
                await self.bot.say(e)
                return
            except:
                await self.bot.say("You must assosiate a tag with this member first using ``!save #tag @member``")
                return

            membership = False
            for clankey in self.clanArray():
                if self.clans[clankey]['tag'] == clantag:
                    membership = True
                    savekey = clankey
                    break

            if ign is None:
                await self.bot.say("Error, Cannot add emoji.")
            else:
                try:
                    if membership:
                        newclanname = self.clans[savekey]['nickname']
                        newname = "{} {} | {}".format(ign, emoji, newclanname)
                    else:
                        newname = "{} | Guest {}".format(ign, emoji)
                    await self.bot.change_nickname(author, newname)
                except discord.HTTPException:
                    await self.bot.say("I don’t have permission to change nick for this user.")
                else:
                    await self.bot.say("Nickname changed to ** {} **\n".format(newname))

                    bank = self.bot.get_cog('Economy').bank
                    bank.withdraw_credits(author, 80000)
        else:
            await self.bot.say("You do not have enough credits to buy this item.")

    @buy.command(pass_context=True, name="4")
    async def buy_4(self, ctx):

        server = ctx.message.server
        author = ctx.message.author
        legendServer = ["374596069989810176"]

        if server.id not in legendServer:
            await self.bot.say("This command can only be executed in the LeGeND Family Server")
            return

        if self.bank_check(author, 90000):
            await self.bot.say("please contact @GR8#7968 to purchase it for you.")
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

        rare = await self._is_rare(author)
        epic = await self._is_epic(author)
        legendary = await self._is_legendary(author)

        if rare or epic or legendary:
            await self.bot.say("You are already Rare™.")
            return

        if self.bank_check(author, 250000):
            bank = self.bot.get_cog('Economy').bank
            bank.withdraw_credits(author, 250000)
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

        rare = await self._is_rare(author)
        epic = await self._is_epic(author)
        legendary = await self._is_legendary(author)

        if not rare:
            await self.bot.say("You need to have **Rare™** to buy this role.")
            return    

        if epic or legendary:
            await self.bot.say("You are already Rare™.")
            return

        if self.bank_check(author, 750000):
            bank = self.bot.get_cog('Economy').bank
            bank.withdraw_credits(author, 750000)
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

        epic = await self._is_epic(author)
        legendary = await self._is_legendary(author)

        if not epic:
            await self.bot.say("You need to have **Epic™** to buy this role.")
            return    

        if legendary:
            await self.bot.say("You are already LeGeNDary™.")
            return

        if self.bank_check(author, 1000000):
            bank = self.bot.get_cog('Economy').bank
            bank.withdraw_credits(author, 1000000)
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

        if self.bank_check(author, 4000000):
            await self.bot.say("please contact @GR8#7968 to purchase it for you.")
        else:
            await self.bot.say("You do not have enough credits to buy Nitro.")
    
    @buy.command(pass_context=True, name="9")
    async def buy_9(self, ctx, country):

        server = ctx.message.server
        author = ctx.message.author
        legendServer = ["374596069989810176"]

        if server.id not in legendServer:
            await self.bot.say("This command can only be executed in the LeGeND Family Server")
            return
        clist = ''
        world_cup_flare = {'russia':'🇷🇺','brazil':'🇧🇷','japan':'🇯🇵','iran':'🇮🇷','mexico':'🇲🇽','belgium':'🇧🇪','korea':'🇰🇷','saudi-arabia':'🇸🇦'
                           ,'germany':'🇩🇪','england':'🇬🇧','spain':'🇪🇸','nigeria':'🇳🇬','costa-rica':'🇨🇷','poland':'🇵🇱','egypt':'🇪🇬','iceland':'🇮🇸'
                           ,'serbia':'🇷🇸','portugal':'🇵🇹','france':'🇫🇷','uruguay':'🇺🇾','argentina':'🇦🇷','panama':'🇵🇦','colombia':'🇨🇴','senegal':'🇸🇳'
                           ,'morocco':'🇲🇦','tunisia':'🇹🇳','switzerland':'🇨🇭','croatia':'🇭🇷','sweden':'🇸🇪','denmark':'🇩🇰','australia':'🇦🇺','peru':'🇵🇪'
                          }
        for key,value in world_cup_flare.items():
            clist = clist + value + ' ' + key.capitalize()+ '\n'
        try:
            country=world_cup_flare[country.lower()]
        except KeyError:
            await self.bot.say("**{}** is not participating in FIFA World Cup 2018, select from the following options:\n{}".format(country.upper(),clist))
            return
                          
        await self.updateClash()
        await self.bot.type()
        profiletag = self.tags[author.id]['tag']
        profiledata = requests.get('https://api.royaleapi.com/player/{}?exclude=games,currentDeck,cards,battles,achievements'.format(profiletag), headers=self.getAuth(), timeout=10).json()
        if profiledata['clan'] is None:
            clantag = ""
            clanname = ""
        else: 
            clantag = profiledata['clan']['tag']
            clanname = profiledata['clan']['name']
        ign = profiledata['name']
        membership = False
        for clankey in self.clanArray():
            if self.clans[clankey]['tag'] == clantag:
                membership = True
                savekey = clankey
                break

        if ign is None:
            await self.bot.say("Error, Cannot add emoji.")
        else:
            try:
                if membership:
                    newclanname = self.clans[savekey]['nickname']
                    newname = "{} {} | {}".format(ign, country, newclanname)
                else:
                    newname = "{} {} | Guest ".format(ign, country)
                await self.bot.change_nickname(author, newname)
            except discord.HTTPException:
                await self.bot.say("I don’t have permission to change nick for this user.")
            else:
                await self.bot.say("Nickname changed to ** {} **\n".format(newname))
                    
def check_files():
    f = "cogs/tags.json"
    if not fileIO(f, "check"):
        print("Creating empty tags.json...")
        fileIO(f, "save", {"0" : {"tag" : "DONOTREMOVE"}})

    f = "cogs/clans.json"
    if not fileIO(f, "check"):
        print("Creating empty clans.json...")
        fileIO(f, "save", {})

    f = "cogs/auth.json"
    if not fileIO(f, "check"):
        print("enter your RoyaleAPI token in auth.json...")
        fileIO(f, "save", {"token" : "enter your RoyaleAPI token here!"})

def setup(bot):
    check_files()
    bot.add_cog(shop(bot))

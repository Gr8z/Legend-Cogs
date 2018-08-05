import discord
from discord.ext import commands
from .utils.dataIO import dataIO
from cogs.utils import checks
import asyncio
import clashroyale
import math
from PIL import Image
import re
import os
import aiohttp


class shop:
    """Legend Family Shop for credits"""

    def __init__(self, bot):
        self.bot = bot
        self.banks = dataIO.load_json('data/economy/bank.json')
        self.auth = self.bot.get_cog('crtools').auth
        self.tags = self.bot.get_cog('crtools').tags
        self.clans = self.bot.get_cog('crtools').clans
        self.clash = clashroyale.OfficialAPI(self.auth.getOfficialToken(), is_async=True)
        self.session = aiohttp.ClientSession()

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

    def bank_check(self, user, amount):
        bank = self.bot.get_cog('Economy').bank
        if bank.account_exists(user):
            if bank.can_spend(user, amount):
                return True
            else:
                return False
        else:
            return False

    async def _valid_image_url(self, url):

        try:
            async with self.session.get(url) as r:
                image = await r.content.read()

            with open('data/leveler/test.jpg', 'wb') as f:
                f.write(image)

            image = Image.open('data/leveler/test.jpg').convert('RGBA')

            size = os.path.getsize('data/leveler/test.jpg')
            if size > 50000:
                return "Image file size is too big."

            width, height = image.size
            if width != height:
                return "Image is not a square"

            os.remove('data/leveler/test.jpg')

            return None
        except:
            return "Image is not valid"

    @commands.command(pass_context=True, no_pm=True)
    @checks.is_owner()
    async def sendpayouts(self, ctx):
        """Payout money for clanchest and donations."""

        await self.updateBank()

        bank = self.bot.get_cog('Economy').bank
        banks = list(self.banks['374596069989810176'])
        # banks = list(self.banks['363728974821457921'])

        for clankey in self.clans.keysClans():
            try:
                clan = await self.clash.get_clan(await self.clans.getClanData(clankey, 'tag'))
            except clashroyale.RequestError:
                await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")
                return

            for member in clan.member_list:
                clan_tag = member.tags.strip('#')
                clan_donations = member.donations
                clan_wins = await self.clans.getMemberWins(clankey, clan_tag)
                clan_cards = await self.clans.getMemberCards(clankey, clan_tag)

                for key in range(0, len(banks)):
                    try:
                        if (clan_donations+clan_wins+clan_cards > 0) and (clan_tag == await self.tags.getTag(banks[key])):

                            try:
                                user = discord.utils.get(ctx.message.server.members, id=banks[key])

                                rare = await self._is_rare(user)
                                epic = await self._is_epic(user)
                                legendary = await self._is_legendary(user)

                                perDonation = 15
                                perWin = 2000
                                perCard = 1
                                BonusMult = 1

                                if rare:
                                    BonusMult = 1.2
                                    perDonation *= BonusMult
                                    perWin *= BonusMult
                                    perCard *= BonusMult

                                if epic:
                                    BonusMult = 1.35
                                    perDonation *= BonusMult
                                    perWin *= BonusMult
                                    perCard *= BonusMult

                                if legendary:
                                    BonusMult = 1.5
                                    perDonation *= BonusMult
                                    perWin *= BonusMult
                                    perCard *= BonusMult

                                amount = math.ceil((clan_donations*perDonation) + (clan_wins*perWin) + (clan_cards*perCard))
                                pay = bank.get_balance(user) + amount
                                bank.set_credits(user, pay)
                                perc = str(math.ceil((BonusMult-1)*100))

                                await self.bot.say("{} - ({} donations)".format(user.display_name, clan_donations))

                                if BonusMult > 1:
                                    await self.bot.send_message(user, ("Hello {} , take these credits*({}% Bonus)* "
                                                                       "for the **{}** donations, **{}** War Day Wins "
                                                                       "and **{}** Collection Day Cards you "
                                                                       "earned for your clan this week. "
                                                                       "(+{} credits!)".format(user.name,
                                                                                               perc,
                                                                                               clan_donations,
                                                                                               clan_wins,
                                                                                               clan_cards,
                                                                                               amount)))
                                else:
                                    await self.bot.send_message(user, ("Hello {} , take these credits "
                                                                       "for the **{}** donations, **{}** War Day Wins "
                                                                       "and **{}** Collection Day Cards you "
                                                                       "earned for your clan this week. "
                                                                       "(+{} credits!)".format(user.name,
                                                                                               clan_donations,
                                                                                               clan_wins,
                                                                                               clan_cards,
                                                                                               amount)))
                            except Exception as e:
                                await self.bot.say(e)
                    except:
                        pass

    @commands.command(pass_context=True, no_pm=True)
    @checks.is_owner()
    async def sendcwpayouts(self, ctx, tag):
        """Payout money for clanwar trophies."""

        await self.updateBank()

        bank = self.bot.get_cog('Economy').bank
        # banks = list(self.banks['363728974821457921'])
        banks = list(self.banks['374596069989810176'])

        tag = await self.tags.formatTag(tag)

        if not await self.tags.verifyTag(tag):
            await self.bot.say("The ID you provided has invalid characters. Please try again.")
            return

        try:
            tourney = await self.clash.get_tournament(tag)
        except clashroyale.RequestError:
            await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")
            return

        for member in tourney.members_list:

            tourney_tag = member.tag.strip('#')
            tourney_score = member.score

            for key in range(0, len(banks)):
                try:
                    if (tourney_score > 0) and (tourney_tag == await self.tags.getTag(banks[key])):

                        try:
                            user = discord.utils.get(ctx.message.server.members, id=banks[key])

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
                                await self.bot.send_message(user, ("Hello {}, take these credits*({}% Bonus)* "
                                                                   "for the **{}** trophies you contributed to "
                                                                   "your clan in **{}**. "
                                                                   "(+{} credits!)".format(user.name,
                                                                                           perc,
                                                                                           tourney_score,
                                                                                           tourney.name,
                                                                                           amount)))
                            else:
                                await self.bot.send_message(user, ("Hello {}, take these credits "
                                                                   "for the **{}** trophies you contributed to "
                                                                   "your clan in **{}**. "
                                                                   "(+{} credits!)".format(user.name,
                                                                                           tourney_score,
                                                                                           tourney.name,
                                                                                           amount)))
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
    async def buy_1(self, ctx):
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
            await self._add_roles(author, ["Pro Payday"])
            await self.bot.say("Congratulations, now you can get !payday every 10 minutes.")
        else:
            await self.bot.say("You do not have enough credits to buy this item.")

    @buy.command(pass_context=True, name="2")
    async def buy_2(self, ctx, imgurLink):
        """Buy custom background for your profile, picture must be in JPG and 490x490px
        Example command: !buy 2 https://i.imgur.com/2Oc5E9K.jpg"""
        server = ctx.message.server
        author = ctx.message.author
        legendServer = ["374596069989810176"]

        if server.id not in legendServer:
            await self.bot.say("This command can only be executed in the LeGeND Family Server")
            return

        if self.bank_check(author, 75000):
            pattern = re.compile(r"<?(https?:\/\/)?(www\.)?([i.]*)?(imgur\.com)\b([-a-zA-Z0-9/]*)>?(\.jpg)?")

            if not pattern.match(imgurLink):
                await self.bot.say("The URL does not end in **.jpg** or is not from **i.imgur.com**. "
                                   "Please upload a JPG image to imgur.com and get a direct link.")
                return

            validate = await self._valid_image_url(imgurLink)
            if validate is not None:
                await self.bot.say(validate)
                return

            message = ctx.message
            message.content = "{}lvladmin bg setcustombg profile {} {}".format(ctx.prefix, author.id, imgurLink)
            message.author = discord.utils.get(ctx.message.server.members, id="112356193820758016")

            await self.bot.process_commands(message)

            bank = self.bot.get_cog('Economy').bank
            bank.withdraw_credits(author, 75000)

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
                await self.bot.type()
                profiletag = await self.tags.getTag(author.id)
                profiledata = await self.clash.get_player(profiletag)

                if profiledata.clan is None:
                    clantag = ""
                else:
                    clantag = profiledata.clan.tag.strip("#")
                ign = profiledata.name
            except clashroyale.RequestError:
                await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")
                return
            except KeyError:
                await self.bot.say("You must assosiate a tag with this member first using ``{}save #tag @member``".format(ctx.prefix))
                return

            membership = await self.clans.verifyMembership(clantag)

            if ign is None:
                await self.bot.say("Error, Cannot add emoji.")
            else:
                try:
                    if membership:
                        savekey = await self.clans.getClanKey(clantag)
                        newclanname = await self.clans.getClanData(savekey, 'nickname')
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
    async def buy_5(self, ctx):
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
            await self._add_roles(author, ["Rare™"])
            await self.bot.say("Congratulations, you are now a **Rare™**")
        else:
            await self.bot.say("You do not have enough credits to buy this role.")

    @buy.command(pass_context=True, name="6")
    async def buy_6(self, ctx):
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
            await self._remove_roles(author, ["Rare™"])
            await asyncio.sleep(3)
            await self._add_roles(author, ["Epic™"])
            await self.bot.say("Congratulations, you are now a **Epic™**")
        else:
            await self.bot.say("You do not have enough credits to buy this role.")

    @buy.command(pass_context=True, name="7")
    async def buy_7(self, ctx):
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
            await self._remove_roles(author, ["Epic™"])
            await asyncio.sleep(3)
            await self._add_roles(author, ["LeGeNDary™"])
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


def setup(bot):
    bot.add_cog(shop(bot))

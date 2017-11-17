import discord
from discord.ext import commands
import requests
from .utils.dataIO import dataIO, fileIO
from cogs.utils import checks

class shop:
    """Legend Family Shop for credits"""

    def __init__(self, bot):
        self.bot = bot
        self.banks = dataIO.load_json('data/economy/bank.json')
        self.clash = dataIO.load_json('cogs/tags.json')

    async def updateClash(self):
        self.clash = dataIO.load_json('cogs/tags.json')

    @commands.command(pass_context=True, no_pm=True)
    @checks.is_owner()
    async def sendpayouts(self, ctx):
        """Payout money for clanchest and donations."""

        server = ctx.message.server
        author = ctx.message.author
        perCrown = 300
        perDonation = 15

        await self.updateClash()

        bank = self.bot.get_cog('Economy').bank
        banks = list(self.banks['374596069989810176'])
            
        for key in range(0,len(banks)):
            if banks[key] in self.clash:
                try:
                    profiletag = self.clash[banks[key]]['tag']
                    profiledata = requests.get('http://api.cr-api.com/profile/'+profiletag, timeout=10).json()
                      
                    if profiledata['clan'] is None:
                        pass
                    else: 
                        clantag = profiledata['clan']['tag']
                        clandata = requests.get('http://api.cr-api.com/clan/{}'.format(clantag), timeout=10).json()

                        clan_tag = []
                        clan_donations = []
                        clan_clanChestCrowns = []
                        for x in range(0, len(clandata['members'])):
                            clan_tag.append(clandata['members'][x]['tag'])
                            clan_donations.append(clandata['members'][x]['donations'])
                            clan_clanChestCrowns.append(clandata['members'][x]['clanChestCrowns'])

                        index = clan_tag.index(profiletag)
                        amount = (clan_donations[index]*perDonation) + (clan_clanChestCrowns[index]*perCrown)

                        user = discord.utils.get(ctx.message.server.members, id = banks[key])

                        pay = bank.get_balance(user) + amount
                        bank.set_credits(user, pay)

                        await self.bot.send_message(user,"Hello " + user.name + ", take these credits for the " + str(clan_donations[index]) + " donations and " + str(clan_clanChestCrowns[index]) + " crowns you contributed to your clan this week. (+" + str(amount) + " credits!)")

                except Exception as e:
                    #await self.bot.say("Unable to send payout")
                    await self.bot.say(e)

def setup(bot):
    bot.add_cog(shop(bot))

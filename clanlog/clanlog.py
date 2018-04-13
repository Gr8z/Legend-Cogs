import discord
import requests
import json
from discord.ext import commands
from cogs.utils import checks
from .utils.dataIO import dataIO, fileIO
from copy import deepcopy

class Clanlog:
    """Clan Log cog for LeGeND family"""

    def __init__(self, bot):
        self.bot = bot
        self.auth = dataIO.load_json('cogs/auth.json')
        self.clans = dataIO.load_json('cogs/clans.json')
        
    def getAuth(self):
        return {"auth" : self.auth['token']}
    
    def save_data(self):
        dataIO.save_json('cogs/clans.json', self.clans)
        
    def update_data(self):
        self.clans = dataIO.load_json('cogs/clans.json')
    
    @checks.is_owner()
    @commands.command()
    async def clanlog(self):
        try:
            self.update_data()
            old_clans = deepcopy(self.clans)
            
            clan_keys = list(self.clans.keys())
            clan_requests = requests.get("https://api.royaleapi.com/clan/{}".format(','.join(self.clans[clan]["tag"] for clan in self.clans)), headers=self.getAuth(), timeout = 60).json()
            
            for i in range(len(clan_requests)):
                one_clan = []
                for member in clan_requests[i]["members"]:
                    one_clan.append({"name" : member["name"], "tag" : member["tag"]})
                self.clans[clan_keys[i]]["members"] = one_clan
            self.save_data()
                    
            for clankey in old_clans.keys():
                for member in old_clans[clankey]["members"]:
                    if member not in self.clans[clankey]["members"]:
                        title = member["name"] + " (#" + member["tag"] + ")"
                        embed_left = discord.Embed(title = title, url = "https://royaleapi.com/player/{}".format(member["tag"]), color=0xff0000)
                        embed_left.add_field(name = "LEFT", value = old_clans[clankey]["name"], inline = False)
                        await self.bot.say(embed = embed_left)
          
            for clankey in self.clans.keys():
                for member in self.clans[clankey]["members"]:
                    if member not in old_clans[clankey]["members"]:
                        title = member["name"] + " (#" + member["tag"] + ")"
                        embed_join = discord.Embed(title = title, url = "https://royaleapi.com/player/{}".format(member["tag"]), color=0x00ff40)
                        embed_join.add_field(name = "JOINED", value = self.clans[clankey]["name"], inline = False)
                        await self.bot.say(embed = embed_join)
                        
        except(requests.exceptions.Timeout, json.decoder.JSONDecodeError):
            print("CLANLOG: Cannot reach Clash Royale Servers.")
    
    @checks.is_owner()    
    @commands.command()
    async def clanlogdownload(self):
        try:
            self.update_data()
            clan_keys = list(self.clans.keys())
            clan_requests = requests.get("https://api.royaleapi.com/clan/{}".format(','.join(self.clans[clan]["tag"] for clan in self.clans)), headers=self.getAuth(), timeout = 60).json()
            
            for i in range(len(clan_requests)):
                one_clan = []
                for member in clan_requests[i]["members"]:
                    one_clan.append({"name" : member["name"], "tag" : member["tag"]})
                self.clans[clan_keys[i]]["members"] = one_clan
            self.save_data()  
            await self.bot.say("Downloaded.")
        except(requests.exceptions.Timeout, json.decoder.JSONDecodeError):
            await self.bot.say("Cannot reach Clash Royale servers. Try again later!")
        
def check_clans():
    c = dataIO.load_json('cogs/clans.json')
    for clankey in c.keys():
        if 'members' not in c[clankey]:
            c[clankey]['members'] = []  
    dataIO.save_json('cogs/clans.json', c)
            
def check_auth():
    c = dataIO.load_json('cogs/auth.json')
    if 'token' not in c:
        c['token'] = ""
    dataIO.save_json('cogs/auth.json', c)
        
def setup(bot):
    check_auth()
    check_clans()
    bot.add_cog(Clanlog(bot))
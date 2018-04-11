import discord
import requests
import json
from discord.ext import commands
import re
from .utils.dataIO import dataIO, fileIO

class Clanlog:
    """Clan Log cog"""

    def __init__(self, bot):
        self.bot = bot
        self.auth = dataIO.load_json('cogs/auth.json')
        self.c = dataIO.load_json('cogs/clans.json')
        
    def getAuth(self):
        return {"auth" : self.auth['token']}
            
    @commands.command()
    async def clanlog(self):
        try:
            file = open("cogs/members.txt", "a")
            file.close()
            file = open("cogs/members.txt", "r")
            input = file.read()
            file.close()
            
            old_log = []
            old_log_tmp = input.split("|n|")
            for d in old_log_tmp:
                old_log.append(d.split(";n;"))
     
            clan_names = []
            clan_tags = []
                
            for clankey in self.c.keys():
                clan_names.append(self.c[clankey]["nickname"])
                clan_tags.append(self.c[clankey]["tag"])
            
            clan_requests = requests.get("https://api.royaleapi.com/clan/{}".format(",".join(clan_tags)), headers=self.getAuth(), timeout = 60).json()
            
            log = []
            for i in range(len(clan_requests)):
                log_oneclan = []
                for j in range(len(clan_requests[i]["members"])):
                    log_oneclan.append(re.sub(r'[^\x00-\x7f]',r'', clan_requests[i]["members"][j]["name"]))
                log.append(log_oneclan)
              
            log_str = ""
            tmp = []
            for i in log:
                tmp.append(";n;".join(i))
            log_str = "|n|".join(tmp)
            
            embed_left=discord.Embed(title="LEFT/ KICKED", color=0xff0000)
            anyleft = False
                    
            for p in range(len(old_log)):
                for q in range(len(old_log[p])):
                    if old_log[p][q] not in log[p]:
                        clan = clan_names[p]
                        embed_left.add_field(name=old_log[p][q], value=clan, inline=False)
                        anyleft = True
                    
            if anyleft:
                await self.bot.say(embed=embed_left)
                    
            embed_join=discord.Embed(title="JOINED", color=0x00ff40)
            anyjoined = False
                    
            for p in range(len(log)):
                for q in range(len(log[p])):
                    if log[p][q] not in old_log[p]:
                        clan = clan_names[p]
                        embed_join.add_field(name=log[p][q], value=clan, inline=False)
                        anyjoined = True;
                            
            if anyjoined:
                await self.bot.say(embed=embed_join)
                     
            file = open("cogs/members.txt", "w")
            file.write(log_str)
            file.close()
        
        except:
            return
        
    @commands.command()
    async def clanlogdownload(self):
        try:
            clan_names = []
            clan_tags = []
                
            for clankey in self.c.keys():
                clan_names.append(self.c[clankey]["nickname"])
                clan_tags.append(self.c[clankey]["tag"])
                
            clan_requests = requests.get("https://api.royaleapi.com/clan/{}".format(",".join(clan_tags)), headers=self.getAuth(), timeout = 60).json()
            
            log = []
            for i in range(len(clan_requests)):
                log_oneclan = []
                for j in range(len(clan_requests[i]["members"])):
                    log_oneclan.append(re.sub(r'[^\x00-\x7f]',r'', clan_requests[i]["members"][j]["name"]))
                log.append(log_oneclan)
              
            log_str = ""
            tmp = []
            for i in log:
                tmp.append(";n;".join(i))
            log_str = "|n|".join(tmp)
            
            file = open("cogs/members.txt", "w")
            file.write(log_str)
            file.close()
            await self.bot.say("Log downloaded")
        except:
            await self.bot.say("Couldnt't download log")
        
def setup(bot):
    bot.add_cog(Clanlog(bot))
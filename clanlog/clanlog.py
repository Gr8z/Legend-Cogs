import discord
import requests
import json
import os
from discord.ext import commands
from cogs.utils import checks
from .utils.dataIO import dataIO, fileIO
from copy import deepcopy
from time import time as get_time
import matplotlib.pyplot as plt
import matplotlib.dates as mdate
import matplotlib.ticker as ticker
plt.switch_backend('agg')
from datetime import datetime as dt
import operator
import numpy as np
from __main__ import send_cmd_help

class Clanlog:
    """Clan Log cog for LeGeND family"""

    def __init__(self, bot):
        self.bot = bot
        self.auth = dataIO.load_json('cogs/auth.json')
        self.clans = dataIO.load_json('cogs/clans.json')
        self.member_log = dataIO.load_json('data/clanlog/member_log.json')
        self.discord_log = dataIO.load_json('data/clanlog/discord_log.json')
        self.last_count = 0
        
    def getAuth(self):
        return {"auth" : self.auth['token']}
    
    def save_clans(self):
        dataIO.save_json('cogs/clans.json', self.clans)
        
    def save_member_log(self):
        dataIO.save_json('data/clanlog/member_log.json', self.member_log)
        
    def update_clans(self):
        self.clans = dataIO.load_json('cogs/clans.json')
    
    def update_member_log(self):
        self.member_log = dataIO.load_json('data/clanlog/member_log.json')
    
    def update_discord_log(self):
        self.discord_log = dataIO.load_json('data/clanlog/discord_log.json')
   
    @checks.is_owner()
    @commands.command(pass_context=True, no_pm=True)
    async def clanlog(self, ctx):
        """Notifies whenever someone leaves or joins"""
        try:
            self.update_clans()
            old_clans = deepcopy(self.clans)
            
            clan_keys = list(self.clans.keys())
            clan_requests = requests.get("https://api.royaleapi.com/clan/{}".format(','.join(self.clans[clan]["tag"] for clan in self.clans)), headers=self.getAuth(), timeout = 60).json()
            
            count = 0
            for i in range(len(clan_requests)):
                count = count + len(clan_requests[i]["members"])
                one_clan = []
                for member in clan_requests[i]["members"]:
                    one_clan.append({"name" : member["name"], "tag" : member["tag"]})
                self.clans[clan_keys[i]]["members"] = one_clan 
            self.save_clans()
            
            if self.last_count != count:
                self.update_member_log()
                current_time = get_time()   
                self.member_log[str(current_time)] = count
                self.last_count = count
                
                saved_times = list(self.member_log.keys())
                for time in saved_times:
                    if (current_time - float(time)) > 2678400:#one month
                        self.member_log.pop(time, None)
                self.save_member_log()
            
            server = ctx.message.server
                    
            for clankey in old_clans.keys():
                for member in old_clans[clankey]["members"]:
                    if member not in self.clans[clankey]["members"]:
                        title = "{} (#{})".format(member["name"], member["tag"])
                        desc = "left **{}**".format(old_clans[clankey]["name"])
                        embed_left = discord.Embed(title = title, url = "https://royaleapi.com/player/{}".format(member["tag"]), description=desc, color=0xff0000)
                        if server.id == "374596069989810176":
                            if self.clans[clankey]["log_channel"] is not None:
                                try:
                                    await self.bot.send_message(discord.Object(id=self.clans[clankey]["log_channel"]),embed = embed_left)
                                except discord.errors.NotFound:
                                    await self.bot.say("<#{}> NOT FOUND".format(self.clans[clankey]["log_channel"]))
                                except discord.errors.Forbidden:
                                    await self.bot.say("No Permission to send messages in <#{}>".format(self.clans[clankey]["log_channel"]))
                        await self.bot.say(embed = embed_left)
          
            for clankey in self.clans.keys():
                for member in self.clans[clankey]["members"]:
                    if member not in old_clans[clankey]["members"]:
                        title = "{} (#{})".format(member["name"], member["tag"])
                        desc = "joined **{}**".format(old_clans[clankey]["name"])
                        embed_join = discord.Embed(title = title, url = "https://royaleapi.com/player/{}".format(member["tag"]), description=desc, color=0x00ff40)
                        if server.id == "374596069989810176":
                            if self.clans[clankey]["log_channel"] is not None:
                                try:
                                    await self.bot.send_message(discord.Object(id=self.clans[clankey]["log_channel"]),embed = embed_join)
                                except discord.errors.NotFound:
                                    await self.bot.say("<#{}> NOT FOUND".format(self.clans[clankey]["log_channel"]))
                                except discord.errors.Forbidden:
                                    await self.bot.say("No Permission to send messages in <#{}>".format(self.clans[clankey]["log_channel"]))
                        await self.bot.say(embed = embed_join)
                        
        except(requests.exceptions.Timeout, json.decoder.JSONDecodeError, KeyError):
            print("CLANLOG: Cannot reach Clash Royale Servers.")
    
    @checks.is_owner()    
    @commands.command(no_pm=True)
    async def clanlogdownload(self):
        """Downloads data to prevent clanlog from sending too many messages"""
        try:
            self.update_clans()
            clan_keys = list(self.clans.keys())
            clan_requests = requests.get("https://api.royaleapi.com/clan/{}".format(','.join(self.clans[clan]["tag"] for clan in self.clans)), headers=self.getAuth(), timeout = 60).json()
            
            for i in range(len(clan_requests)):
                one_clan = []
                for member in clan_requests[i]["members"]:
                    one_clan.append({"name" : member["name"], "tag" : member["tag"]})
                self.clans[clan_keys[i]]["members"] = one_clan
            self.save_clans()  
            await self.bot.say("Downloaded.")
            
        except(requests.exceptions.Timeout, json.decoder.JSONDecodeError, KeyError):
            await self.bot.say("Cannot reach Clash Royale servers. Try again later!")

    @commands.group(pass_context=True, no_pm=True)
    async def history(self, ctx):
        """Graph with member count history"""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)

    @history.command(pass_context=True, no_pm=True)
    async def clash(self, ctx):
        """Graph with clash member count history"""
        try:
            channel = ctx.message.channel
            await self.bot.send_typing(channel)
            self.update_member_log()
            
            secs, vals = zip(*sorted(self.member_log.items()))

            # Convert to the correct format for matplotlib.
            # mdate.epoch2num converts epoch timestamps to the right format for matplotlib
            secs = mdate.epoch2num(np.array(secs, dtype=float))
 
            fig, ax = plt.subplots(figsize=(10, 6))

            # Plot the date using plot_date rather than plot
            ax.plot_date(secs, vals, linestyle='solid', marker='None')

            # Choose your xtick format string
            date_fmt = '%a, %b %d %Y'
            tick_spacing = 3

            # Use a DateFormatter to set the data to the correct format.
            date_formatter = mdate.DateFormatter(date_fmt)
            ax.xaxis.set_major_formatter(date_formatter)
            ax.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))

            plt.title("CR MEMBER HISTORY OF LEGEND FAMILY", color = "orange", weight = "bold", size = 19)
            plt.xlabel("DATE", color = "gray")
            plt.ylabel("MEMBERS", color = "gray")

            # Sets the tick labels diagonal so they fit easier.
            fig.autofmt_xdate()
            
            plt.savefig("data/clanlog/history.png")
            await self.bot.send_file(channel, "data/clanlog/history.png", filename=None)

        except (IndexError):
            await self.bot.say("Clanlog command needs to collect more data!")

    @history.command(pass_context=True, no_pm=True)
    async def discord(self, ctx):
        """Graph with discord user count history"""
        try:
            channel = ctx.message.channel
            await self.bot.send_typing(channel)
            self.update_discord_log()
            
            secs, vals = zip(*sorted(self.discord_log.items()))

            # Convert to the correct format for matplotlib.
            # mdate.epoch2num converts epoch timestamps to the right format for matplotlib
            secs = mdate.epoch2num(np.array(secs, dtype=float))
 
            fig, ax = plt.subplots(figsize=(10, 6))

            # Plot the date using plot_date rather than plot
            ax.plot_date(secs, vals, linestyle='solid', marker='None')

            # Choose your xtick format string
            date_fmt = '%a, %b %d %Y'
            tick_spacing = 3

            # Use a DateFormatter to set the data to the correct format.
            date_formatter = mdate.DateFormatter(date_fmt)
            ax.xaxis.set_major_formatter(date_formatter)
            ax.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))

            plt.title("DISCORD USER HISTORY OF LEGEND FAMILY", color = "#7289DA", weight = "bold", size = 19)
            plt.xlabel("DATE", color = "gray")
            plt.ylabel("MEMBERS", color = "gray")

            # Sets the tick labels diagonal so they fit easier.
            fig.autofmt_xdate()
            
            plt.savefig("data/clanlog/history.png")
            await self.bot.send_file(channel, "data/clanlog/history.png", filename=None)

        except (IndexError):
            await self.bot.say("Clanlog command needs to collect more data!")
        
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
    
def check_files():
    f = "data/clanlog/member_log.json"
    if not fileIO(f, "check"):
        print("Creating empty member_log.json...")
        dataIO.save_json(f, {"1524540132" : 0})
        
def check_folders():
    if not os.path.exists("data/clanlog"):
        print("Creating data/clanlog folder...")
        os.makedirs("data/clanlog")
        
def setup(bot):
    check_auth()
    check_clans()
    check_folders()
    check_files()
    bot.add_cog(Clanlog(bot))


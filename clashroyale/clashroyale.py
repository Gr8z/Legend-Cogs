import discord
from discord.ext import commands
from .utils.dataIO import dataIO, fileIO
try: # check if BeautifulSoup4 is installed
	from bs4 import BeautifulSoup
	soupAvailable = True
except:
	soupAvailable = False
import json
from flask import Flask, request
import requests
import os
import aiohttp
from __main__ import send_cmd_help
import asyncio
from crapipy import AsyncClient
import socket
import urllib.request  as urllib2

BOTCOMMANDER_ROLES =  ["Family Representative", "Clan Manager", "Clan Deputy", "Co-Leader", "Hub Officer", "admin"];
creditIcon = "https://i.imgur.com/TP8GXZb.png"
credits = "Bot by GR8 | Academy"

clash = os.path.join("cogs", "tags.json")
clash_mini = os.path.join("cogs", "mini_tags.json")
brawl = os.path.join("data", "BrawlStats", "tags.json")
cycle = os.path.join("data", "clashroyale", "chests.json")

class clashroyale:
    """Live statistics for Clash Royale"""

    def __init__(self, bot):
    	self.bot = bot
    	self.clash = dataIO.load_json(clash)
    	self.clash_mini = dataIO.load_json(clash_mini)
    	self.brawl = dataIO.load_json(brawl)
    	self.cycle = dataIO.load_json(cycle)

    @commands.command(pass_context=True, aliases=['clashprofile','cprofile','cProfile'])
    async def clashProfile(self, ctx, member: discord.Member = None):
    	"""View your Clash Royale Profile Data and Statstics."""

    	client = AsyncClient()
    	try :

	    	if member is None:
	    		member = ctx.message.author

	    	profiletag = self.clash[member.id]['tag']

	    	try:
	    		profiledata = await client.get_profile(profiletag)
	    	except:
	    		await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")
	    		return

	    	if profiledata.clan.badge.url is None:
	    		clanurl = "https://i.imgur.com/4EH5hUn.png"
	    	else:
	    		clanurl = "http://api.cr-api.com"+profiledata.clan.badge.url

	    	embed=discord.Embed(title="", color=0x0080ff)
	    	embed.set_author(name=profiledata.name + " (#"+profiledata.tag+")", icon_url=clanurl)
	    	embed.set_thumbnail(url="http://api.cr-api.com" + profiledata.arena.imageURL)
	    	embed.add_field(name="Trophies", value=profiledata.trophies, inline=True)
	    	embed.add_field(name="Legendary Trophies", value=profiledata.legendaryTrophies, inline=True)
	    	embed.add_field(name="Highest Trophies", value=profiledata.stats.maxTrophies, inline=True)
	    	embed.add_field(name="Level", value=profiledata.experience.level, inline=True)
	    	embed.add_field(name="Arena", value=profiledata.arena.name, inline=True)
	    	embed.add_field(name="Experience", value=str(profiledata.experience.xp)+"/"+str(profiledata.experience.xpRequiredForLevelUp), inline=True)
	    	if not profiledata.not_in_clan:
	    		embed.add_field(name="Clan", value=profiledata.clan.name, inline=True)
	    		embed.add_field(name="Role", value=profiledata.clan.role, inline=True)
	    	embed.add_field(name="Cards Found", value=str(profiledata.stats.cardsFound)+"/78", inline=True)
	    	embed.add_field(name="Favourite Card", value=profiledata.stats.favoriteCard.replace('_', ' ').capitalize(), inline=True)
	    	embed.add_field(name="Chests Opened", value=profiledata.chest_cycle.position, inline=True)
	    	embed.add_field(name="Games Played", value=profiledata.games.total, inline=True)
	    	embed.add_field(name="Tournament Games Played", value=profiledata.games.tournamentGames, inline=True)
	    	embed.add_field(name="Win Streak", value=str(max(0,profiledata.games.currentWinStreak))+" Wins", inline=True)
	    	embed.add_field(name="Wins", value=profiledata.games.wins, inline=True)
	    	embed.add_field(name="Losses", value=profiledata.games.losses, inline=True)
	    	embed.add_field(name="Draws", value=profiledata.games.draws, inline=True)
	    	embed.add_field(name="Three Crown Wins", value=profiledata.stats.threeCrownWins, inline=True)
	    	embed.add_field(name="Total Donations", value=profiledata.stats.totalDonations, inline=True)
	    	if hasattr(profiledata.stats, 'challengeMaxWins'):
	    		embed.add_field(name="Challenge Max Wins", value=profiledata.stats.challengeMaxWins, inline=True)
	    		embed.add_field(name="Challenge Cards Won", value=profiledata.stats.challengeCardsWon, inline=True)
	    	embed.add_field(name="Tournament Cards Won", value=profiledata.stats.tournamentCardsWon, inline=True)
	    	embed.set_footer(text=credits, icon_url=creditIcon)

    		await self.bot.say(embed=embed)

    	except:
    		await self.bot.say("You need to first save your profile using ``!save clash #GAMETAG``")

    @commands.command(pass_context=True)
    async def offers(self, ctx, member: discord.Member = None):
    	"""View your Clash Royale upcomming offers"""

    	client = AsyncClient()
    	try :
	    	if member is None:
	    		member = ctx.message.author

	    	profiletag = self.clash[member.id]['tag']

	    	try:
	    		profiledata = await client.get_profile(profiletag)
	    	except:
	    		await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")
	    		return

	    	offersdesc = "<:epicopen:380832590254571521> " + str(profiledata.shop_offers.epic) + " Days   <:legendopen:380832387195469826> " + str(profiledata.shop_offers.legendary) + " Days   <:shopoffer:380832689076305924> " + str(profiledata.shop_offers.arena) + " Days"

	    	embed=discord.Embed(title="", description="", color=0x0080ff)
	    	embed.set_author(name=profiledata.name + " (#"+profiledata.tag+")", icon_url="http://api.cr-api.com"+profiledata.clan.badge.url)
	    	embed.add_field(name="Upcoming Shop Offers", value=offersdesc, inline=True)
	    	embed.set_footer(text=credits, icon_url=creditIcon)	    	

	    	await self.bot.say(embed=embed)

    	except:
    		await self.bot.say("You need to first save your profile using ``!save clash #GAMETAG``")

    @commands.command(pass_context=True)
    async def chests(self, ctx, member: discord.Member = None):
	    """View your upcoming chest cycle for Clash Royale."""
	    client = AsyncClient()
	    try:
	    	if member is None:
	    		member = ctx.message.author

	    	profiletag = self.clash[member.id]['tag']

	    	try:
	    		profiledata = await client.get_profile(profiletag)
	    	except:
	    		await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")
	    		return

	    	valuechest = ""

	    	def chest_first_index(position, key):
	    	    """First index of chest by key."""
	    	    if self.cycle is not None:
	    	        if pos is not None:
	    	            start_pos = position % len(self.cycle)
	    	            chests = self.cycle[start_pos:]
	    	            chests.extend(self.cycle)
	    	            return chests.index(key)+1
	    	    return None

	    	position = profiledata.chest_cycle.position
	    	index = position % len(self.cycle)

	    	for x in range(0,10):
	    		pos = index + x
	    		newPos = -1
	    		if pos < (len(self.cycle)-1):
	    			valuechest += str(self.cycle[pos])
	    		else:
	    			newPos += 1
	    			valuechest += str(self.cycle[newPos])	    	

	    	chest1 = "<:giant:380832560504373249> +" + str(chest_first_index(position, "<:giant:380832560504373249>")) + "  "
	    	chest2 = "<:epic:380832620059033610> +" + str(profiledata.chest_cycle.epic_pos-position) + "  "
	    	chest3 = "<:magic:380832656704798731> +" + str(chest_first_index(position, "<:magic:380832656704798731>")) + "  "
	    	chest4 = "<:super:380832745305276416> +" + str(profiledata.chest_cycle.super_magical_pos-position) + "  " 
	    	if profiledata.chest_cycle.legendary_pos is not None:
	    		chest5 = "<:legend:380832458482122752> +" + str(profiledata.chest_cycle.legendary_pos-position)
	    	else:
	    		chest5 = ""

	    	if profiledata.clan.badge.url is None:
	    		clanurl = "https://i.imgur.com/4EH5hUn.png"
	    	else:
	    		clanurl = "http://api.cr-api.com"+profiledata.clan.badge.url

	    	embed=discord.Embed(title="", color=0x0080ff, description=str(position)+" Chests Opened")
	    	embed.set_author(name=profiledata.name + " (#"+profiledata.tag+")", url='http://cr-api.com/profile/' + profiletag, icon_url=clanurl)
	    	embed.add_field(name="Upcoming Chests", value=valuechest, inline=False)
	    	embed.add_field(name="Special Chests", value=chest1+chest2+chest3+chest4+chest5, inline=False)
	    	embed.set_footer(text=credits, icon_url=creditIcon)
	    	await self.bot.say(embed=embed)

	    except:
	    	await self.bot.say("You need to first save your profile using ``!save clash #GAMETAG``")

    @commands.command(pass_context=True)
    async def clan(self, ctx, clantag):
    	"""View Clash Royale Clan statistics and information """
    	client = AsyncClient()
    	try:
    		clandata = await client.get_clan(clantag)
    	except:
    		await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")
    		return

    	embed=discord.Embed(title=clandata.name + " (#" + clantag + ")", description=clandata.description, color=0x0080ff)
    	embed.set_thumbnail(url='http://api.cr-api.com'+ str(clandata.badge.url))
    	embed.add_field(name="Members", value=str(clandata.memberCount)+"/50", inline=True)
    	embed.add_field(name="Donations", value=clandata.donations, inline=True)
    	embed.add_field(name="Score", value=clandata.score, inline=True)
    	embed.add_field(name="Required Trophies", value=clandata.requiredScore, inline=True)
    	embed.add_field(name="Status", value=clandata.typeName, inline=True)
    	embed.add_field(name="Country", value=clandata.region.name, inline=True)
    	embed.set_footer(text=credits, icon_url=creditIcon)
    	await self.bot.say(embed=embed)

    @commands.command()
    async def api(self):
    	"""Ping the CR API  """

    	socket.setdefaulttimeout( 10 )  # timeout in seconds

    	await self.bot.type()

    	url = 'http://api.cr-api.com/profile/CRRYRPCC'
    	try :
    	    req = urllib2.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    	    response = urllib2.urlopen(req).read()
    	except socket.timeout as e:
    	    await self.bot.say('We failed to reach the server. Reason: ' + str(e))
    	except urllib2.HTTPError as e:
    	    await self.bot.say('The server couldn\'t fulfill the request. Reason: ' + str(e.code))
    	except urllib2.URLError as e:
    	    await self.bot.say('We failed to reach the server. Reason: ' + str(e.reason))
    	else :
    	    await self.bot.say('API is working!')

    @commands.group(pass_context=True)
    async def save(self, ctx):
	    """Save profile tags for Clash Royale and Brawl Stars"""
	    author = ctx.message.author
	    if ctx.invoked_subcommand is None:
	    	await send_cmd_help(ctx)
	    	msg = "```"
	    	if author.id in self.clash: 
	    		msg += "CR Profile: {}\n".format(self.clash[author.id]['tag'])
	    	if author.id in self.brawl: 
	    		msg += "BS Profile: {}\n".format(self.brawl[author.id]['tag'])
	    	if author.id in self.brawl: 
	    		msg += "BS Clan: {}\n".format(self.brawl[author.id]['band_tag'])
	    	msg += "```"
	    	await self.bot.say(msg)

    @save.command(pass_context=True, name="clash")
    async def save_clash(self, ctx, profiletag : str, member: discord.Member = None):
	    """ save your Clash Royale Profile Tag	

	    Example:
	    	!save clash #CRRYTPTT @GR8
	    	!save clash #CRRYRPCC

	    Type !contact to ask for help.
	    """

	    server = ctx.message.server
	    author = ctx.message.author
	    client = AsyncClient()

	    profiletag = profiletag.strip('#').upper().replace('O', '0')
	    check = ['P', 'Y', 'L', 'Q', 'G', 'R', 'J', 'C', 'U', 'V', '0', '2', '8', '9']

	    if any(i not in check for i in profiletag):
	    	await self.bot.say("The ID you provided has invalid characters. Please try again. Type !contact to ask for help.")
	    	return

	    allowed = False
	    if member is None:
	    	allowed = True
	    elif member.id == author.id:
	    	allowed = True
	    else:
	    	botcommander_roles = [discord.utils.get(server.roles, name=r) for r in BOTCOMMANDER_ROLES]
	    	botcommander_roles = set(botcommander_roles)
	    	author_roles = set(author.roles)
	    	if len(author_roles.intersection(botcommander_roles)):
	    		allowed = True

	    if not allowed:
	    	await self.bot.say("You dont have enough permissions to set tags for others. Type !contact to ask for help.")
	    	return

	    if member is None:
	    	member = ctx.message.author

	    try:
	    	profiledata = await client.get_profile(profiletag)

	    	self.clash.update({member.id: {'tag': profiletag}})
	    	dataIO.save_json('cogs/tags.json', self.clash)

	    	await self.bot.say('**' +profiledata.name + ' (#'+ profiletag + ')** has been successfully saved on ' + member.mention)
	    except:
	    	await self.bot.say("We cannot find your ID in our database, please try again. Type !contact to ask for help.")

    @save.command(pass_context=True, name="mini")
    async def save_mini(self, ctx, profiletag : str, member: discord.Member = None):
	    """ save your Clash Royale MINI Profile Tag	

	    Example:
	    	!save mini #8Q8LR0JJU @GR8
	    	!save mini #8Q8LR0JJU

	    Type !contact to ask for help.
	    """

	    server = ctx.message.server
	    author = ctx.message.author

	    profiletag = profiletag.strip('#').upper().replace('O', '0')
	    check = ['P', 'Y', 'L', 'Q', 'G', 'R', 'J', 'C', 'U', 'V', '0', '2', '8', '9']

	    if any(i not in check for i in profiletag):
	    	await self.bot.say("The ID you provided has invalid characters. Please try again. Type !contact to ask for help.")
	    	return

	    allowed = False
	    if member is None:
	    	allowed = True
	    elif member.id == author.id:
	    	allowed = True
	    else:
	    	botcommander_roles = [discord.utils.get(server.roles, name=r) for r in BOTCOMMANDER_ROLES]
	    	botcommander_roles = set(botcommander_roles)
	    	author_roles = set(author.roles)
	    	if len(author_roles.intersection(botcommander_roles)):
	    		allowed = True

	    if not allowed:
	    	await self.bot.say("You dont have enough permissions to set tags for others. Type !contact to ask for help.")
	    	return

	    if member is None:
	    	member = ctx.message.author
	    
	    try:
		    profiledata = requests.get('http://api.cr-api.com/profile/'+profiletag, timeout=10).json()

		    if "8CL09V0C" not in profiledata['clan']['tag']:
		    	await self.bot.say("This feature is only available to members of LeGEnD Minis!")
		    	return

		    self.clash_mini.update({member.id: {'tag': profiledata['tag']}})
		    dataIO.save_json('cogs/mini_tags.json', self.clash_mini)

		    await self.bot.say('Mini player **' +profiledata['name'] + ' (#'+ profiledata['tag'] + ')** has been successfully saved on ' + member.mention)
	    except (requests.exceptions.Timeout):
		    await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")
		    return
	    except requests.exceptions.RequestException as e:
		    await self.bot.say(e)
		    return
	    except:
	    	await self.bot.say("We cannot find your ID in our database, please try again. Type !contact to ask for help.")

    @save.command(pass_context=True, name="brawl")
    async def save_brawl(self, ctx, profiletag : str, member: discord.Member = None):
	    """		save your Brawl Stars Profile Tag	`

	    Example:
	    	!save brawl #LJQ2GGR
	    	!save brawl #LJQ2GGR @GR8

	    Type !contact to ask for help.
	    """
	    server = ctx.message.server
	    author = ctx.message.author

	    profiletag = profiletag.strip('#').upper().replace('O', '0')
	    check = ['P', 'Y', 'L', 'Q', 'G', 'R', 'J', 'C', 'U', 'V', '0', '2', '8', '9']

	    if any(i not in check for i in profiletag):
	    	await self.bot.say("The ID you provided has invalid characters. Please try again. Type !contact to ask for help.")
	    	return

	    allowed = False
	    if member is None:
	    	allowed = True
	    elif member.id == author.id:
	    	allowed = True
	    else:
	    	botcommander_roles = [discord.utils.get(server.roles, name=r) for r in BOTCOMMANDER_ROLES]
	    	botcommander_roles = set(botcommander_roles)
	    	author_roles = set(author.roles)
	    	if len(author_roles.intersection(botcommander_roles)):
	    		allowed = True

	    if not allowed:
	    	await self.bot.say("You dont have enough permissions to set tags for others.")
	    	return

	    if member is None:
	    	member = ctx.message.author
	    
	    url = "https://brawlstats.io/players/" + profiletag
	    refresh = "https://brawlstats.io/players/" + profiletag + "/refresh"
	    requests.get(refresh)

	    async with aiohttp.get(url) as response:
	        soupObject = BeautifulSoup(await response.text(), "html.parser")
	    try:

	        band = soupObject.find('div', {'class':'band-info'}).get_text()

	        if band == 'No Band':
	        	band_tag = '#'
	        else:
	        	band_link = soupObject.find('div', {'class':'band-info'}).find('a')
	        	band_tag = band_link['href'][7:].strip()

	        tagUsername = soupObject.find('div', {'class':'player-name brawlstars-font'}).get_text()

	        self.brawl.update({member.id: {'tag': profiletag, 'band_tag': band_tag}})
	        dataIO.save_json('data/BrawlStats/tags.json', self.brawl)

	        await self.bot.say(tagUsername + ' has been successfully saved. Now you can use ``!brawlProfile`` ``!band``')
	    except:
	    	await self.bot.say("We cannot find your ID in our database, please try again. Type !contact to ask for help.")

def check_folders():
    if not os.path.exists("data/clashroyale"):
        print("Creating data/clashroyale folder...")
        os.makedirs("data/clashroyale")
    if not os.path.exists("data/BrawlStats"):
        print("Creating data/BrawlStats folder...")
        os.makedirs("data/BrawlStats")

def check_files():
    f = "cogs/tags.json"
    if not fileIO(f, "check"):
        print("Creating empty tags.json...")
        fileIO(f, "save", [])
    f = "cogs/mini_tags.json"
    if not fileIO(f, "check"):
        print("Creating empty mini_tags.json...")
        fileIO(f, "save", [])
    f = "data/BrawlStats/tags.json"
    if not fileIO(f, "check"):
        print("Creating empty tags.json...")
        fileIO(f, "save", [])

def setup(bot):
	check_folders()
	check_files()
	if soupAvailable:
		bot.add_cog(clashroyale(bot))
	else:
		raise RuntimeError("You need to run `pip3 install beautifulsoup4`")
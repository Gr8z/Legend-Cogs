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
import socket
import urllib.request  as urllib2
import requests_cache
import time

requests_cache.install_cache('statsroyale_cache', backend='sqlite', expire_after=60)

BOTCOMMANDER_ROLES =  ["Family Representative", "Clan Manager", "Clan Deputy", "Co-Leader", "Hub Officer", "admin"];
creditIcon = "https://i.imgur.com/TP8GXZb.png"
credits = "Bot by GR8 | Titan"

clash = os.path.join("cogs", "tags.json")
clash_mini = os.path.join("cogs", "mini_tags.json")
brawl = os.path.join("data", "BrawlStats", "tags.json")
auth = os.path.join("cogs", "auth.json")

class clashroyale:
	"""Live statistics for Clash Royale"""

	def __init__(self, bot):
		self.bot = bot
		self.clash = dataIO.load_json(clash)
		self.clash_mini = dataIO.load_json(clash_mini)
		self.brawl = dataIO.load_json(brawl)
		self.auth = dataIO.load_json(auth)

	def getAuth(self):
		return {"auth" : self.auth['token']}

	# Converts maxPlayers to Cards
	def getCards(self, maxPlayers):
		if maxPlayers == 50: return 25
		if maxPlayers == 100: return 100
		if maxPlayers == 200: return 400
		if maxPlayers == 1000: return 2000

	# Converts maxPlayers to Cards
	def getCoins(self, maxPlayers):
		if maxPlayers == 50: return 175
		if maxPlayers == 100: return 700
		if maxPlayers == 200: return 2800
		if maxPlayers == 1000: return 14000

	# Converts seconds to time
	def sec2tme(self, sec):
		m, s = divmod(sec, 60)
		h, m = divmod(m, 60)

		if h is 0:
			if m is 0:
				return "{} seconds".format(s)
			else:
				return "{} minutes, {} secs".format(m,s)
		else:
			return "{} hour, {} mins".format(h,m)

	@commands.command(pass_context=True, aliases=['clashprofile','cprofile','cProfile'])
	async def clashProfile(self, ctx, member: discord.Member = None):
		"""View your Clash Royale Profile Data and Statstics."""

		try :

			if member is None:
				member = ctx.message.author

			profiletag = self.clash[member.id]['tag']

			await self.bot.type()

			try:
				profiledata = requests.get('http://api.cr-api.com/player/{}'.format(profiletag), headers=self.getAuth(), timeout=10).json()
			except:
				await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")
				return

			if profiledata['clan'] is None:
				clanurl = "https://i.imgur.com/4EH5hUn.png"
			else:
				clanurl = profiledata['clan']['badge']['image']

			embed=discord.Embed(title="", color=0x0080ff)
			embed.set_author(name=profiledata['name'] + " (#"+profiledata['tag']+")", icon_url=clanurl)
			embed.set_thumbnail(url="https://cr-api.github.io/cr-api-assets/arenas/{}.png".format(profiledata['arena']['arena'].replace(' ', '').lower()))
			embed.add_field(name="Trophies", value=profiledata['trophies'], inline=True)
			embed.add_field(name="Highest Trophies", value=profiledata['stats']['maxTrophies'], inline=True)
			embed.add_field(name="Level", value=profiledata['stats']['level'], inline=True)
			embed.add_field(name="Arena", value=profiledata['arena']['name'], inline=True)
			if profiledata['clan'] is not None:
				embed.add_field(name="Clan", value=profiledata['clan']['name'], inline=True)
				embed.add_field(name="Role", value=profiledata['clan']['role'].capitalize(), inline=True)
			embed.add_field(name="Cards Found", value=str(profiledata['stats']['cardsFound'])+"/81", inline=True)
			embed.add_field(name="Favourite Card", value=profiledata['stats']['favoriteCard']['name'], inline=True)
			embed.add_field(name="Games Played", value=profiledata['games']['total'], inline=True)
			embed.add_field(name="Tournament Games Played", value=profiledata['games']['tournamentGames'], inline=True)
			embed.add_field(name="Wins", value=profiledata['games']['wins'], inline=True)
			embed.add_field(name="Losses", value=profiledata['games']['losses'], inline=True)
			embed.add_field(name="Draws", value=profiledata['games']['draws'], inline=True)
			embed.add_field(name="Three Crown Wins", value=profiledata['stats']['threeCrownWins'], inline=True)
			embed.add_field(name="Total Donations", value=profiledata['stats']['totalDonations'], inline=True)
			embed.add_field(name="Challenge Max Wins", value=profiledata['stats']['challengeMaxWins'], inline=True)
			embed.add_field(name="Challenge Cards Won", value=profiledata['stats']['challengeCardsWon'], inline=True)
			embed.add_field(name="Tournament Cards Won", value=profiledata['stats']['tournamentCardsWon'], inline=True)
			embed.set_footer(text=credits, icon_url=creditIcon)

			await self.bot.say(embed=embed)

		except:
			await self.bot.say("You need to first save your profile using ``!save clash #GAMETAG``")

	@commands.command(pass_context=True)
	async def chests(self, ctx, member: discord.Member = None):
		"""View your upcoming chest cycle for Clash Royale."""

		try:
			if member is None:
				member = ctx.message.author

			profiletag = self.clash[member.id]['tag']

			await self.bot.type()

			try:
				profiledata = requests.get('http://api.cr-api.com/player/{}'.format(profiletag), headers=self.getAuth(), timeout=10).json()
			except:
				await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")
				return

			valuechestText = ' '.join(profiledata['chestCycle']['upcoming']).replace('silver', '<:silver:385784583343439882>').replace('gold', '<:gold:385784630227369985>').replace('giant', '<:giant:380832560504373249>').replace('epic', '<:epic:380832620059033610>').replace('super magical', '<:super:380832745305276416>').replace('magical', '<:magic:380832656704798731>').replace('legendary', '<:legend:380832458482122752>')

			chest1 = "<:giant:380832560504373249> +" + str(profiledata['chestCycle']['giant']+1) + "  "
			chest2 = "<:epic:380832620059033610> +" + str(profiledata['chestCycle']['epic']+1) + "  "
			chest3 = "<:magic:380832656704798731> +" + str(profiledata['chestCycle']['magical']+1) + "  "
			chest4 = "<:super:380832745305276416> +" + str(profiledata['chestCycle']['superMagical']+1) + "  "
			chest5 = "<:legend:380832458482122752> +" + str(profiledata['chestCycle']['legendary']+1) + "  "

			if profiledata['clan'] is None:
				clanurl = "https://i.imgur.com/4EH5hUn.png"
			else:
				clanurl = profiledata['clan']['badge']['image']

			embed=discord.Embed(title="", color=0x0080ff, description="Your Upcoming chests.")
			embed.set_author(name=profiledata['name'] + " (#"+profiledata['tag']+")", icon_url=clanurl)
			embed.add_field(name="Upcoming Chests", value=valuechestText, inline=False)
			embed.add_field(name="Special Chests", value=chest1+chest2+chest3+chest4+chest5, inline=False)
			embed.set_footer(text=credits, icon_url=creditIcon)
			await self.bot.say(embed=embed)

		except:
			await self.bot.say("You need to first save your profile using ``!save clash #GAMETAG``")

	@commands.command(pass_context=True)
	async def clan(self, ctx, clantag):
		"""View Clash Royale Clan statistics and information """

		await self.bot.type()

		try:
			clandata = requests.get('http://api.cr-api.com/clan/{}'.format(clantag), headers=self.getAuth(), timeout=10).json()

			embed=discord.Embed(title=clandata['name'] + " (#" + clandata['tag'] + ")", description=clandata['description'], color=0x0080ff)
			embed.set_thumbnail(url=clandata['badge']['image'])
			embed.add_field(name="Members", value=str(clandata['memberCount'])+"/50", inline=True)
			embed.add_field(name="Donations", value=str(clandata['donations']), inline=True)
			embed.add_field(name="Score", value=str(clandata['score']), inline=True)
			embed.add_field(name="Required Trophies", value=str(clandata['requiredScore']), inline=True)
			embed.add_field(name="Status", value=str(clandata['type'].capitalize()), inline=True)
			embed.add_field(name="Country", value=str(clandata['location']['name']), inline=True)
			embed.set_footer(text=credits, icon_url=creditIcon)
			await self.bot.say(embed=embed)
		
		except:
			await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")
			return

	@commands.command(pass_context=True, aliases=['cw'])
	async def tournament(self, ctx, tag, password = None):
		"""View Clash Royale Tournament Information """

		await self.bot.type()

		try:
			tourneydata = requests.get('http://api.cr-api.com/tournaments/{}'.format(tag), headers=self.getAuth(), timeout=10).json()

			maxCapacity = tourneydata['maxCapacity']
			cards = self.getCards(maxCapacity)
			coins = self.getCoins(maxCapacity)

			try:
				desc = tourneydata['description']
			except KeyError:
				desc = "No description"

			embed=discord.Embed(title=tourneydata['name']+" (#"+tourneydata['tag']+")", description=desc, color=0x00ffff)
			embed.set_thumbnail(url='https://statsroyale.com/images/tournament.png')
			embed.add_field(name="Players", value=str(tourneydata['capacity']) + "/" + str(maxCapacity), inline=True)
			embed.add_field(name="Status", value=tourneydata['status'].capitalize(), inline=True)

			if tourneydata['type'] == "passwordProtected":
				if password is not None:
					embed.add_field(name="Password", value=password, inline=True)
				else:
					await self.bot.say("Error: Please enter a tournament password.")
					return

			if tourneydata['status'] != "ended":
				
				startTime = self.sec2tme((tourneydata['createTime'] + tourneydata['preparationDuration']) - int(time.time()))
				endTime = self.sec2tme((tourneydata['createTime'] + tourneydata['preparationDuration'] + tourneydata['duration']) - int(time.time()))

				embed.add_field(name="Starts In", value=startTime, inline=True)
				embed.add_field(name="Ends In", value=endTime, inline=True)


			embed.add_field(name="Hosted By", value=tourneydata['creator']['name'], inline=True)
			embed.add_field(name="Top prize", value="<:coin:380832316932489268> " + str(cards) + "	 <:tournamentcards:380832770454192140> " +  str(coins), inline=True)
			embed.set_footer(text=credits, icon_url=creditIcon)
			await self.bot.say(embed=embed)

		except:
	   		await self.bot.say("Error: Tournament not found. Please try again later!")

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

		await self.bot.type()

		if member is None:
			member = ctx.message.author

		try:
			profiledata = requests.get('http://api.cr-api.com/player/{}'.format(profiletag), headers=self.getAuth(), timeout=10).json()

			self.clash.update({member.id: {'tag': profiletag}})
			dataIO.save_json('cogs/tags.json', self.clash)

			await self.bot.say('**' +profiledata['name'] + ' (#'+ profiletag + ')** has been successfully saved on ' + member.mention)
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
			profiledata = requests.get('http://api.cr-api.com/player/{}'.format(profiletag), headers=self.getAuth(), timeout=10).json()

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
	f = "cogs/auth.json"
	if not fileIO(f, "check"):
		print("Creating empty auth.json...")
		dataIO.save_json(f, {})

def check_auth():
	c = dataIO.load_json('cogs/auth.json')
	if 'token' not in c:
		c['token'] = ""
	dataIO.save_json('cogs/auth.json', c)

def setup(bot):
	#check_folders()
	check_files()
	check_auth()
	if soupAvailable:
		bot.add_cog(clashroyale(bot))
	else:
		raise RuntimeError("You need to run `pip3 install beautifulsoup4`")
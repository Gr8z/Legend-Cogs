import discord
from discord.ext import commands
from random import randint
import requests
import asyncio
import random
import json
from cogs.utils import checks
from .utils.dataIO import dataIO
import os
from fake_useragent import UserAgent
from datetime import date, datetime, timedelta
from proxybroker import Broker

lastTag = '0'
creditIcon = "https://i.imgur.com/TP8GXZb.png"
credits = "Bot by GR8 | Titan"

proxies_list = [
	'94.249.160.49:6998',
	'93.127.128.41:7341',
	'107.175.43.100:6858',
	'64.44.18.31:3691',
	'172.82.173.100:5218',
	'172.82.177.111:3432',
	'45.43.219.185:2461',
	'45.43.218.82:3577',
	'173.211.31.3:8053',
	'195.162.4.111:4762'
]

# Converts maxPlayers to Cards
def getCards(maxPlayers):
	if maxPlayers == 50: return 25
	if maxPlayers == 100: return 100
	if maxPlayers == 200: return 400
	if maxPlayers == 1000: return 2000

# Converts maxPlayers to Cards
def getCoins(maxPlayers):
	if maxPlayers == 50: return 175
	if maxPlayers == 100: return 700
	if maxPlayers == 200: return 2800
	if maxPlayers == 1000: return 14000

# Converts seconds to time
def sec2tme(sec):
	m, s = divmod(sec, 60)
	h, m = divmod(m, 60)

	if h is 0:
		if m is 0:
			return "{} seconds".format(s)
		else:
			return "{} minutes, {} secs".format(m,s)
	else:
		return "{} hour, {} mins".format(h,m)

def time_str(obj, isobj):
	"""JSON serializer for datetiem and back"""

	fmt = '%Y%m%d%H%M%S' # ex. 20110104172008 -> Jan. 04, 2011 5:20:08pm 

	# if isinstance(obj, (datetime, date)):
	if isobj:
		return obj.strftime(fmt)
	else:
		return datetime.strptime(obj, fmt)


class tournament:
	"""tournament!"""

	def __init__(self, bot):
		self.bot = bot
		self.path = 'data/tourney/settings.json'
		self.cachepath = 'data/tourney/tourneycache.json'
		self.settings = dataIO.load_json(self.path)
		self.tourneyCache = dataIO.load_json(self.cachepath)
		self.auth = dataIO.load_json('cogs/auth.json')
		self.cacheUpdated = False
		
	def save_data(self):
		"""Saves the json"""
		dataIO.save_json(self.path, self.settings)
	
	def save_cache(self):
		"""Saves the cache json"""
		dataIO.save_json(self.cachepath, self.tourneyCache)

	def getAuth(self):
		return {"auth" : self.auth['token']}

	async def _is_allowed(self, member):
		server = member.server
		botcommander_roles = [discord.utils.get(server.roles, name=r) for r in ["Member", "Family Representative", "Clan Manager", "Clan Deputy", "Co-Leader", "Hub Officer", "admin", "Guest"]]
		botcommander_roles = set(botcommander_roles)
		author_roles = set(member.roles)
		if len(author_roles.intersection(botcommander_roles)):
			return True
		else:
			return False
	
	def _get_proxy(self):
		return "http://67.63.33.7"  # For now
	
	async def _fetch_tourney(self):
		"""Fetch tournament data. Run sparingly"""
		url = "{}".format('http://statsroyale.com/tournaments?appjson=1')
		
		if proxies_list:
			randproxy = "http://"+random.choice(proxies_list)
		else:
			randproxy = self._get_proxy()
		
		try:
			async with aiohttp.ClientSession() as session:
				async with session.get(url, timeout=30, proxy=randproxy) as resp:
					data = await resp.json()
		except json.decoder.JSONDecodeError:
			print(resp)
			raise
		except asyncio.TimeoutError:
			print(resp)
			raise
		except:
			print(resp)
			raise
		else:
			return data
		
		return None
	
	async def _expire_cache(self):
		await asyncio.sleep(900)
		self.cacheUpdated = False
	
	async def _update_cache(self):
		try:
			newdata = await self._fetch_tourney()
		except:  # On error: Don't retry, but don't mark cache as updated
			return
		
		if not newdata['success']:
			return # On error: Don't retry, but don't mark cache as updated
		
		newdata = newdata['tournaments']
		
		for tourney in newdata:
			if tourney["hashtag"] not in self.tourneyCache:
				timeLeft = timedelta(seconds=tourney['timeLeft'])
				endtime = datetime.utcnow() + timeLeft
				tourney["endtime"] = time_str(endtime, True)
				self.tourneyCache[tourney["hashtag"]] = tourney
			else:
				tourney["endtime"] = self.tourneyCache[tourney["hashtag"]]["endtime"]  # Keep endtime
				self.tourneyCache[tourney["hashtag"]] = tourney
		
		self.save_cache()
		self.cacheUpdated=True
		
		await self._topTourney(newdata)  # Posts all best tourneys
		
		
	
	async def _get_tourney(self, minPlayers):
		if not self.cacheUpdated:	
			await self._update_cache()

		now = datetime.utcnow()
		
		tourneydata = [t1 for t1 in self.tourneyCache 
						if not t1['full'] and time_str(t1['endtime'], False) - now >= timedelta(seconds=600) and t1['maxPlayers']>=minPlayers]
		
		if not tourneydata:
			return None
		return random.choice(tourneydata)


	async def _topTourney(self, newdata):
		now = datetime.utcnow()
		tourneydata = [t1 for t1 in newdata
						if not t1['full'] and time_str(t1['endtime'], False) - now >= timedelta(seconds=600) and t1['maxPlayers']>50]
		
		for data in tourneydata:
			embed = self._get_embed(data)
				
			for serverid in self.settings.keys():
				if self.settings[serverid]:
					await self.bot.send_message(discord.Object(id=self.settings[serverid]), embed=embed) # Family
			#await self.bot.send_message(discord.Object(id='363728974821457923'), embed=embed) # testing


	@commands.group(pass_context=True, no_pm=True)
	async def tourney(self, ctx, minPlayers: int=0):
		"""Check an open tournament in clash royale instantly"""

		author = ctx.message.author

		await self.bot.send_typing(ctx.message.channel)

		allowed = await self._is_allowed(author)
		if not allowed:
			await self.bot.say("Error, this command is only available for Legend Members and Guests.")
			return
		
		
		tourneydata = await self._get_tourney(minPlayers)
		
		if tourneydata:
			embed = self._get_embed(tourneydata['tournaments'][x])
			await self.bot.say(embed=embed)
		else:
			await self.bot.say("No tourney found")

	@tourney.command(pass_context=True, no_pm=True)
	@checks.admin_or_permissions(administrator=True)
	async def channel(self, ctx, channel: discord.Channel=None):
		serverid = ctx.message.server.id
		if not channel:
			self.settings[serverid] = None
			await self.bot.say("Tournament channel for this server cleared")
		else:
			self.settings[serverid] = channel.id
			await self.bot.say("Tournament channel for this server set to "+channel.mention)
		self.save_data()
		
	def _get_embed(self, aTourney):
		title = aTourney['title']
		length = aTourney['length']
		totalPlayers = aTourney['totalPlayers']
		maxPlayers = aTourney['maxPlayers']
		full = aTourney['full']
		timeLeft = aTourney['timeLeft']
		startTime = aTourney['startTime']
		warmup = aTourney['warmup']
		hashtag = aTourney['hashtag']
		cards = getCards(maxPlayers)
		coins = getCoins(maxPlayers)
		
		embed=discord.Embed(title="Open Tournament", color=randint(0, 0xffffff))
		embed.set_thumbnail(url='https://statsroyale.com/images/tournament.png')
		embed.add_field(name="Title", value=title, inline=True)
		embed.add_field(name="Tag", value="#"+hashtag, inline=True)
		embed.add_field(name="Players", value=str(totalPlayers) + "/" + str(maxPlayers), inline=True)
		embed.add_field(name="Ends In", value=sec2tme(timeLeft), inline=True)
		embed.add_field(name="Top prize", value="<:coin:380832316932489268> " + str(cards) + "     <:tournamentcards:380832770454192140> " +  str(coins), inline=True)
		embed.set_footer(text=credits, icon_url=creditIcon)
		return embed
		

def check_folders():
	if not os.path.exists("data/tourney"):
		print("Creating data/tourney folder...")
		os.makedirs("data/tourney")

def check_files():
	f = "data/tourney/settings.json"
	if not dataIO.is_valid_json(f):
		dataIO.save_json(f, {})
	
	f = "data/tourney/tourneycache.json"
	if not dataIO.is_valid_json(f):
		dataIO.save_json(f, {})

def setup(bot):
	check_folders()
	check_files()
	n = tournament(bot)
	loop = asyncio.get_event_loop()
	loop.create_task(n._expire_cache())
	bot.add_cog(n)
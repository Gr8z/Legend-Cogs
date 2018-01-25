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

from proxybroker import Broker, Proxy
from collections import deque

import aiohttp

from cogs.utils.chat_formatting import pagify

lastTag = '0'
creditIcon = "https://i.imgur.com/TP8GXZb.png"
credits = "Bot by GR8 | Titan"

proxies_list = [
	Proxy(host="67.63.33.7", port=80)
]
	# '94.249.160.49:6998',
	# '93.127.128.41:7341',
	# '107.175.43.100:6858',
	# '64.44.18.31:3691',
	# '172.82.173.100:5218',
	# '172.82.177.111:3432',
	# '45.43.219.185:2461',
	# '45.43.218.82:3577',
	# '173.211.31.3:8053',
	# '195.162.4.111:4762'
# ]

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
		self.queue = asyncio.Queue()
		self.broker = Broker(self.queue)
		self.proxylist = deque(proxies_list,10)
		self.session = aiohttp.ClientSession()
		
	def __unload(self):
		self.session.close()	
		self.broker.stop()
	
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
	
	async def _fetch(self, url, proxy_url, headers):
		resp = None
		try:
			async with self.session.get(url, timeout=30, proxy=proxy_url, headers=headers) as resp:
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
		finally:
			return None
			
	async def _fetch_tourney(self):
		"""Fetch tournament data. Run sparingly"""
		url = "{}".format('http://statsroyale.com/tournaments?appjson=1')
		proxy = await self._get_proxy()
		data = await self._fetch(url, proxy, {})
		
		return data
		
	async def _API_tourney(self, hashtag):
		"""Fetch API tourney from hashtag"""
		url = "{}{}".format('http://api.cr-api.com/tournaments/',hashtag)
		proxy = await self._get_proxy()
		data = await self._fetch(url, proxy, self.getAuth())
		
		return data
	
	async def _get_proxy(self):
		proxy = random.choice(self.proxylist)
		host = proxy.host
		port = proxy.port
		proxystr = 'http://{}:{}'.format(host, port)
		
		return proxystr
		

	async def _expire_cache(self):
		await asyncio.sleep(180)
		self.cacheUpdated = False
		if not self.cacheUpdated:
			await self._update_cache()  # This will automatically post top tournaments
	
	async def _update_cache(self):
		try:
			newdata = await self._fetch_tourney()
		except:  # On error: Don't retry, but don't mark cache as updated
			return None
		
		if not newdata:
			await self.bot.send_message(discord.Object(id="363728974821457923"), "StatsRoyale Failed")
			
		if not newdata['success']:
			await self.bot.send_message(discord.Object(id="363728974821457923"), "StatsRoyale denied")
			return None # On error: Don't retry, but don't mark cache as updated
		
		newdata = newdata['tournaments']
		newdata = [tourney for tourney in newdata if not tourney['full']]
		
		if not newdata:
    		await self.bot.send_message(discord.Object(id="363728974821457923"), "No non-full tournaments found")

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
		
		await self._topTourney(newdata)  # Posts all best tourneys when cache is updated


	async def _get_tourney(self, minPlayers):
		"""tourneyCache is dict of tourneys with hashtag as key"""
		if not self.cacheUpdated:	
			await self._update_cache()

		
		for x in range(10):  # Try 10 times or until tourney is found
			now = datetime.utcnow()
			
			tourneydata = [t1 for tkey, t1 in self.tourneyCache.items()
							if not t1['full'] and t1['maxPlayers']>=minPlayers
							and tkey != lastTag]

			if not tourneydata:
				return None

			aChoice = random.choice(tourneydata)
			if time_str(aChoice['endtime'], False) - now < timedelta(seconds=600):
				self.tourneyCache.pop(aChoice['hashtag'])
				# Now it loops While and can't pick same tourney again
			else:
				bTourney = await self._checkFull(aChoice)
				if not bTourney:
					self.tourneyCache.pop(aChoice['hashtag'])
					# Loop and try again
				else:
					lastTag = aChoice['hashtag']
					return aChoice, bTourney
		
		return None  # Failed to get a tourney after 10 tries
	
	async def _checkFull(self, aTourney):
		try:
			bTourney = await self._API_tourney(aTourney['hashtag'])
		except:
			return None
		
		if bTourney['capacity'] == bTourney['maxCapacity']:
			return None
		else:
			return bTourney

	async def _topTourney(self, newdata):
		"""newdata is a list of tourneys"""
		now = datetime.utcnow()
		tourneydata = [t1 for t1 in newdata
						if not t1['full'] and time_str(t1['endtime'], False) - now >= timedelta(seconds=600) and t1['maxPlayers']>50]
						
		# Adjust parameters for what qualifies as a "top" tourney here ^^^^
		
		for data in tourneydata:
			embed = await self._get_embed(data)
				
			for serverid in self.settings.keys():
				if self.settings[serverid]:
					server = self.bot.get_server(serverid)
					channel = server.get_channel(self.settings[serverid])
					await self.bot.send_message(channel, embed=embed) # Family
					
			#await self.bot.send_message(discord.Object(id='363728974821457923'), embed=embed) # testing
		
	@commands.command(pass_context=True, no_pm=True)
	@checks.is_owner()
	async def showcache(self, ctx):
		"""Displays current cache pagified"""

		for page in pagify(
			str(self.tourneyCache), shorten_by=50):
			
			await self.bot.say(page)
			
	@commands.command(pass_context=True, no_pm=True)
	@checks.is_owner()
	async def clearcache(self, ctx):
		"""Clears current tourney cache"""
		self.tourneyCache = {}
		self.save_cache()
		await self.bot.say("Success")
		
	@commands.command(pass_context=True, no_pm=True)
	@checks.is_owner()
	async def showproxy(self, ctx):
		"""Displays current proxies pagified"""

		for page in pagify(
			str(self.proxylist), shorten_by=50):
			
			await self.bot.say(page)
			
	@commands.command(pass_context=True, no_pm=True)
	async def tourney(self, ctx, minPlayers: int=0):
		"""Check an open tournament in clash royale instantly"""

		author = ctx.message.author

		await self.bot.send_typing(ctx.message.channel)

		allowed = await self._is_allowed(author)
		if not allowed:
			await self.bot.say("Error, this command is only available for Legend Members and Guests.")
			return
		
		tourney, apitourney = await self._get_tourney(minPlayers)
		
		if tourney:
			embed = await self._get_embed(tourney, apitourney)
			await self.bot.say(embed=embed)
		else:
			await self.bot.say("No tourney found")

	@commands.command(pass_context=True, no_pm=True)
	@checks.admin_or_permissions(administrator=True)
	async def tourneychannel(self, ctx, channel: discord.Channel=None):
		serverid = ctx.message.server.id
		if not channel:
			self.settings[serverid] = None
			await self.bot.say("Tournament channel for this server cleared")
		else:
			self.settings[serverid] = channel.id
			await self.bot.say("Tournament channel for this server set to "+channel.mention)
		self.save_data()
		
	@commands.command(pass_context=True, no_pm=True)
	@checks.admin_or_permissions(administrator=True)
	async def tourneywipe(self, ctx, channel: discord.Channel=None):
		
		self.settings = {}
		await self.bot.say("Tournament channel for all servers cleared")

		self.save_data()
		
	async def _get_embed(self, aTourney, bTourney=None):
		"""Builds embed for tourney
		Uses cr-api.com if available"""
		
		if not bTourney:
			try:
				bTourney = await self._API_tourney(aTourney['hashtag'])
			except:
				bTourney = None
			
		now = datetime.utcnow()
		
		embedtitle = "Open Tournament"
		
		if bTourney:
			title = bTourney['name']
			totalPlayers = bTourney['capacity']
			maxPlayers = bTourney['maxCapacity']
			full = bTourney['capacity'] >= bTourney['maxCapacity']
			
			if bTourney['type'] == "passwordProtected":
				embedtitle = "Locked Tournament"
			
			if bTourney['status'] == "ended":
				embedtitle = "Ended Tournament"
			
		else:
			title = aTourney['title']
			totalPlayers = aTourney['totalPlayers']
			maxPlayers = aTourney['maxPlayers']
			full = aTourney['full']
			
		timeLeft = time_str(aTourney['endtime'], False) - now
		timeLeft = int(timeLeft.total_seconds())
		if timeLeft < 0:
			timeLeft = 0
			embedtitle = "Ended Tournament"
			
		hashtag = aTourney['hashtag']
		cards = getCards(maxPlayers)
		coins = getCoins(maxPlayers)
		
		embed=discord.Embed(title="Open Tournament", color=0xFAA61A)
		embed.set_thumbnail(url='https://statsroyale.com/images/tournament.png')
		embed.add_field(name="Title", value=title, inline=True)
		embed.add_field(name="Tag", value="#"+hashtag, inline=True)
		embed.add_field(name="Players", value=str(totalPlayers) + "/" + str(maxPlayers), inline=True)
		embed.add_field(name="Ends In", value=sec2tme(timeLeft), inline=True)
		embed.add_field(name="Top prize", value="<:coin:380832316932489268> " + str(cards) + "     <:tournamentcards:380832770454192140> " +  str(coins), inline=True)
		embed.set_footer(text=credits, icon_url=creditIcon)
		return embed
	

	async def _proxyBroker(self):
	types = ['HTTP']
	countries = ['US', 'DE', 'FR']
	
		await self.broker.find(types=types, limit=50)
		await asyncio.sleep(120)
	
	async def _brokerResult(self):
		anyfound = False
		await self.bot.send_message(discord.Object(id="363728974821457923"), "Waiting on results from Proxy-Broker")
		while True:
			proxy = await self.queue.get()
			if proxy is None: break
			self.proxylist.append(proxy)
			if not anyfound:
				await self.bot.send_message(discord.Object(id="363728974821457923"), "Proxies are being found: {}".format(proxy))
				anyfound = True
		await asyncio.sleep(60)
		
		

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
	loop.create_task(n._proxyBroker())
	loop.create_task(n._brokerResult())
	bot.add_cog(n)
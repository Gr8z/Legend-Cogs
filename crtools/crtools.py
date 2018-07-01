import discord
from discord.ext import commands
from .utils.dataIO import dataIO, fileIO
import os
from cogs.utils import checks

tags_path = "data/crtools/tags.json"
auth_path = "data/crtools/auth.json"
clans_path = "data/crtools/clans.json"
default_clans = {'defualt':{'tag': '', 'role': '', 'role_id': '', 'name': '', 'nickname': '', 'discord': '', 'waiting': [], 'members': [], 'bonustitle': '', 
				'personalbest': 0, 'warTrophies': 0, 'approval': False, 'log_channel': False, 'emoji': ''}}

class tags:
	"""Tags Management"""
	def __init__(self):
		self.tags = dataIO.load_json(tags_path)

	async def verifyTag(self, tag):
		"""Check if a player/can tag is valid"""
		check = ['P', 'Y', 'L', 'Q', 'G', 'R', 'J', 'C', 'U', 'V', '0', '2', '8', '9']

		if any(i not in check for i in tag):
			return False

		return True

	async def formatTag(self, tag):
		"""Sanize and format CR Tag"""
		return tag.strip('#').upper().replace('O', '0')

	async def linkTag(self, tag, userID):
		"""Link a player tag to a discord User"""
		tag = await self.formatTag(tag)

		self.tags.update({userID: {'tag': tag}})
		dataIO.save_json(tags_path, self.tags)

	async def unlinkTag(self, userID):
		"""Unlink a player tag to a discord User"""
		if self.c.pop(str(userID), None):
			dataIO.save_json(tags_path, self.tags)
			return True
		return False

	async def getTag(self, userID):
		"""Get a user's CR Tag"""
		try:
			return self.tags[userID]['tag']
		except KeyError:
			return None

	async def getUser(self, serverUsers, tag):
		"""Get User from CR Tag"""
		for user in serverUsers:
			if user.id in self.tags:
				player_tag = self.tags[user.id]['tag']
				if player_tag == await self.formatTag(tag):
					return user
		return None

class auth:
	"""RoyaleAPI key management"""
	def __init__(self):
		self.auth = dataIO.load_json(auth_path)

	async def addToken(self, key):
		"""Add a RoyaleAPI Token"""
		self.auth['token'] = key
		dataIO.save_json(auth_path, self.auth)
		return True

	def getToken(self):
		"""Get RoyaleAPI Token"""
		return {"auth" : self.auth['token']}

class clans:
	"""Clan Family Management"""
	def __init__(self):
		self.clans = dataIO.load_json(clans_path)

	async def getClans(self):
		"""Return clan array"""
		return self.clans

	async def getClanData(self, clankey, data):
		"""Return clan array"""
		return self.clans[clankey][data]

	async def numClans(self):
		"""Return the number of clans"""
		return len(self.clans.keys())

	def keysClans(self):
		"""Get keys of all the clans"""
		return self.clans.keys()

	async def namesClans(self):
		"""Get name of all the clans"""
		return ", ".join(key for key in self.keysClans())

	async def tagsClans(self):
		"""Get tags of all the clans"""
		return ",".join(self.clans[clan]["tag"] for clan in self.clans)

	async def rolesClans(self):
		"""Get roles of all the clans"""
		roles = ["Member"]
		for x in self.c:
			roles.append(self.clans[x]['role'])
		return roles

	async def verifyMembership(self, clantag):
		"""Check if a clan is part of the family"""
		clantag = await tags.formatTag(clantag)
		for clankey in self.keysClans():
			if self.clans[clankey]['tag'] == clantag:
				return True
		return False

	async def getClanKey(self, clantag):
		"""Get a clan key from a clan tag."""
		clantag = await tags.formatTag(clantag)
		for clankey in self.keysClans():
			if self.clans[clankey]['tag'] == clantag:
				return clankey
		return None

	async def numWaiting(self, clankey):
		"""Get a clan's wating list length from a clan key."""
		return len(self.clans[clankey]['waiting'])

	async def setWarTrophies(self, clankey, trophies):
		"""Set a clan's wartrophies"""
		self.clans[clankey]['warTrophies'] = trophies
		dataIO.save_json(clans_path, self.clans)

	async def addWaitingMember(self, clankey, memberID):
		"""Add a user to a clan's waiting list"""
		if memberID not in self.clans[clankey]['waiting']:
			self.clans[clankey]['waiting'].append(memberID)
			dataIO.save_json(clans_path, self.clans)
			return True
		else:
			return False

	async def delWaitingMember(self, clankey, memberID):
		"""Remove a user to a clan's waiting list"""
		if memberID in self.clans[clankey]['waiting']:
			self.clans[clankey]['waiting'].remove(memberID)
			dataIO.save_json(clans_path, self.clans)

			return True
		else:
			return False

	async def checkWaitingMember(self, clankey, memberID):
		"""check if a user is in a waiting list"""
		return memberID in self.clans[clankey]['waiting']

	async def getWaitingIndex(self, clankey, memberID):
		"""Get the waiting position from a clan's waiting list"""
		return self.clans[clankey]['waiting'].index(memberID)

	async def delClan(self, clankey):
		"""delete a clan from the family"""
		if self.clans.pop(clankey, None):
			dataIO.save_json(clans_path, self.clans)
			return True
		return False

	async def setPBTrophies(self, clankey, trophies):
		"""Set a clan's PB Trohies"""
		self.clans[clankey]['personalbest'] = trophies
		dataIO.save_json(clans_path, self.clans)

	async def setBonus(self, clankey, bonus):
		"""Set a clan's Bonus Statement"""
		self.clans[clankey]['bonustitle'] = bonus
		dataIO.save_json(clans_path, self.clans)

	async def setLogChannel(self, clankey, channel):
		"""Set a clan's log channel"""
		self.clans[clankey]['log_channel'] = channel
		dataIO.save_json(clans_path, self.clans)

	async def setMemberList(self, clankey, members):
		"""Set clan's member list"""
		self.clans[clankey]['members'] = members
		dataIO.save_json(clans_path, self.clans)

	async def togglePrivate(self, clankey):
		"""oggle Private approval of new recruits"""
		self.clans[clankey]['approval'] = not self.clans[clankey]['approval']
		dataIO.save_json(clans_path, self.clans)

		return self.clans[clankey]['approval']

class crtools:
	"""Clash Royale Tools"""
	def __init__(self, bot):
		self.bot = bot
		self.tags = tags()
		self.clans = clans()
		self.auth = auth()

	@commands.command()
	@checks.mod_or_permissions(administrator=True)
	async def settoken(self, key):
		"""Input your Clash Royale API Token from RoyaleAPI.com"""
		auth.addToken(key)
		await self.bot.say("RoyaleAPI Token set")

	@commands.group(pass_context=True)
	@checks.mod_or_permissions(administrator=True)
	async def clans(self, ctx):
		"""Base command for managing clash royale clans. [p]help clans for details"""
		if ctx.invoked_subcommand is None:
			await self.bot.send_cmd_help(ctx)

	@clans.command(pass_context=True, name="delete")
	@checks.is_owner()
	async def clans_delete(self, ctx, clankey):
		"""Remove a clan from tracking"""
		clankey = clankey.lower()
		if await clans.delClan(clankey):
			await self.bot.say("Success")
			return
		else:
			await self.bot.say("Failed")
	
	@clans.command(pass_context=True, name="pb")
	async def clans_pb(self, ctx, clankey, pb: int):
		"""Set a Personal Best requirement for a clan"""
		clankey = clankey.lower()
		try:
			await clans.setPBTrophies(clankey, pb)
		except KeyError:
			await self.bot.say("Please use a valid clanname: {}".format(await clans.namesClans()))
			return 
		   
		await self.bot.say("Success")

	@clans.command(pass_context=True, name="bonus")
	async def clans_bonus(self, ctx, clankey, *bonus):
		"""Add bonus information to title of clan (i.e. Age: 21+)"""
		clankey = clankey.lower()
		try:
			await clans.setBonus(clankey, " ".join(bonus))
		except KeyError:
			await self.bot.say("Please use a valid clanname: {}".format(await clans.namesClans()))
			return 
		
		await self.bot.say("Success")	  

	@clans.command(pass_context=True, name="log")
	async def clans_log(self, ctx, clankey, channel : discord.Channel):
		"""Set Clan's Log channel to track in's and outs"""
		clankey = clankey.lower()
		try:
			server = ctx.message.server

			if not server.get_member(self.bot.user.id).permissions_in(channel).send_messages:
				await self.bot.say("I do not have permissions to send messages to {0.mention}".format(channel))
				return

			if channel is None:
				await self.bot.say("I can't find the specified channel. It might have been deleted.")

			await clans.setLogChannel(clankey, channel.id)

			await self.bot.send_message(channel, "I will now send log messages to {0.mention}".format(channel))
			await self.bot.say("Clash log channel for {} is now set to {}".format(clankey, channel))

		except KeyError:
			await self.bot.say("Please use a valid clanname: {}".format(await clans.namesClans()))
			return 
		except discord.errors.Forbidden:
			await self.bot.say("No permission to send messages to that channel")
		

	@clans.command(pass_context=True, name="private")
	async def clans_private(self, ctx, clankey):
		"""Toggle Private approval of new recruits"""
		clankey = clankey.lower()
		try:
			await self.bot.say("Private Approval now is set to " + str(await clans.togglePrivate(clankey)))
		except KeyError:
			await self.bot.say("Please use a valid clanname: {}".format(await clans.namesClans()))
			return 

def check_folders():
	if not os.path.exists("data/crtools"):
		print("Creating data/crtools folder...")
		os.makedirs("data/crtools")

def check_files():
	if not fileIO(tags_path, "check"):
		print("Creating empty tags.json...")
		fileIO(tags_path, "save", {"0" : {"tag" : "DONOTREMOVE"}})

	if not fileIO(auth_path, "check"):
		print("enter your RoyaleAPI token in data/crtools/auth.json...")
		fileIO(auth_path, "save", {"token" : "enter your RoyaleAPI token here!"})

	if not fileIO(clans_path, "check"):
		print("Creating empty clans.json...")
		fileIO(clans_path, "save", default_clans)

def check_auth():
	c = dataIO.load_json(auth_path)
	if 'token' not in c:
		c['token'] = "enter your RoyaleAPI token here!"
	dataIO.save_json(auth_path, c)

def setup(bot):
	check_folders()
	check_files()
	check_auth()
	bot.add_cog(crtools(bot))
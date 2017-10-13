import discord
from discord.ext import commands

import sys
sys.path.append("../")

import os
import pickle
import asyncio
import re
import requests
import json
import collections
from random import*
from pathlib import Path
from .utils.draft import Draft
from .utils.player import Player
from .utils.dataIO import dataIO, fileIO
#from ext.enterdraftresults import manageLeaderboard

prefix = ["!"]
autodeletetime = 30

async def getRank(player):
	with open("leaderboard.p", "rb") as f:
		l = pickle.load(f)
	for i in range(len(l)):
		if l[i][0] == player.display_name:
			return i+1

async def getEmoji(bot, name):
	return discord.utils.get(bot.get_all_emojis(), name=re.sub("[^a-zA-Z]", "", name))

async def updateDrafterRole(server, player):
	classicRole = discord.utils.get(server.roles, name="Classic Drafter")
	rareRole = discord.utils.get(server.roles, name="Rare Drafter")
	epicRole = discord.utils.get(server.roles, name="Epic Drafter")
	legendaryRole = discord.utils.get(server.roles, name="Legendary Drafter")

	user = server.get_member(player.id)
	roles = user.roles
	if classicRole in roles:
		roles.remove(classicRole)
	if rareRole in roles:
		roles.remove(rareRole)
	if epicRole in roles:
		roles.remove(epicRole)
	if legendaryRole in roles:
		roles.remove(legendaryRole)

	if player.draft_amount > player.old_draft_amount:
		da = player.draft_amount
	else:
		da = player.old_draft_amount

	if da <= 4:
		roles.append(classicRole)
	elif da >= 5 and da <= 9:
		roles.append(rareRole)
	elif da >= 10 and da <= 19:
		roles.append(epicRole)
	elif da >= 20:
		roles.append(legendaryRole)

	return roles

class Drafting():
	"""Commands used for drafting"""
	def __init__(self, bot):
		self.bot = bot
		self.opendrafts = []
		#self.cards = sorted(requests.get("http://www.clashapi.xyz/api/cards").json(), key=lambda card: card["name"])
		self.cards = sorted(dataIO.load_json('data/drafting/cards.json'), key=lambda card: card["name"])
		
	@commands.command(pass_context=True)
	async def createdraft(self, ctx, *, optionalarguments=""):
		"""creates a draft to join

		Only usuable in the "draft_challenge"!
		Open Drafts will be pinned to the channel to keep track of them.
		Players can enter by reacting with the star emoji(clicking on it).
		Cancel the creation of the draft with the octagonal sign

		optional arguments(seperate with commas):
		'size= ' (leaving this out creates a standard 8 man draft)

		'name= ' (leaving this out calles the Draft '<creator>'s Draft')
		
		'eligible= ' (needs to name of a role, leaving this out makes it eligible for everyone and tags @Drafter)
		
		'tag' (if you mention this the bot will add @tag in the creation message. Per default it tags @Drafter but if you change who's eligible it will tag this role instead!)
		
		'starttime= ' (The approximate starttime of the draft, you can leave this out)

		Example: '!createdraft size=4, tag, name=My fancy draft, starttime=2 am in the evening, eligible=V.I.P Drafter' creates a draft called 'My fancy draft' with the size 4 only for V.I.P Drafters aswell as tagging them in the message and mentioning the startingtime
		"""
		modRole = discord.utils.get(ctx.message.server.roles, name="Mod")
		marshalRole = discord.utils.get(ctx.message.server.roles, name="Marshal")

		draftlobby = discord.utils.get(ctx.message.server.channels, name="draft_challenge")
		if ctx.message.channel != draftlobby:
			await self.bot.say("This command should only be used in 'draft_challenge' so we can keep everything in one place 😉", delete_after=autodeletetime)
			return

		host = ctx.message.author
		if not Path("data/drafting/playerData/"+host.id+".p").is_file():
			await self.bot.say(host.mention+", you are not registered yet. Please do so with "+prefix[0]+"register if you want to participate in drafts", delete_after=autodeletetime)
			return

		if "size=" in optionalarguments:
			size = int(optionalarguments.partition("size=")[2].partition(",")[0]) 
		else:
			size = 8

		if size < 2:
			if not marshalRole in host.roles and not modRole in host.roles:
				await self.bot.say("You are not allowed to create drafts with a size smaller than 2.", delete_after=autodeletetime)
				return

		if "name=" in optionalarguments:
			name = optionalarguments.partition("name=")[2].partition(",")[0]
			optionalarguments = optionalarguments.replace(name, "")
		else:
			name = host.display_name+"'s Draft"

		if "eligible=" in optionalarguments:
			eligible = optionalarguments.partition("eligible=")[2].partition(",")[0]
			optionalarguments = optionalarguments.replace(eligible, "")
			eligiblerole = discord.utils.get(ctx.message.server.roles, name=eligible)
			if eligiblerole == None:
				await self.bot.say("Error, creating Draft failed. Invalid eligible statement(needs to be role name)", delete_after=autodeletetime)
				return
		else:
			eligiblerole = ctx.message.server.default_role

		if "tag" in optionalarguments:
			tag = "True"
		else:
			tag = "False"

		if eligiblerole == ctx.message.server.default_role:
			drafterrole = discord.utils.get(ctx.message.server.roles, name="Drafter")
			if tag == "False":
				mention = ""
			else:
				mention = drafterrole.mention
		else:
			if tag == "False":
				mention = ""
			else:
				mention = eligiblerole.mention

		draftobj = Draft(size=size, eligible=eligiblerole.id, name=name, host=host.id)
		print("## Draft '"+draftobj.name+"' has been created by "+host.display_name)
		

		self.opendrafts.append(draftobj.id)
		participants = []
		self.men = True		# If names are displayed as mentions

		async def upPartis():
			partinames = ""
			if self.men == True:
				for p in participants:
					partinames = partinames +" "+ p.mention
			else:
				for p in participants:
					partinames = partinames +" "+ p.display_name + ","

			if partinames == "":
				partinames = "-"
			return partinames

		emb = discord.Embed(title="New "+str(draftobj.size)+" man Draft '"+draftobj.name+"'", description="Draft is in creation", color=0x3498db)
		emb.add_field(name="Host", value=host.mention)
		emb.add_field(name="Draftname", value=draftobj.name)
		emb.add_field(name="Size", value=str(size))
		emb.add_field(name="DraftID", value=draftobj.id)
		emb.add_field(name="Eligible", value=eligiblerole.name)
		if "starttime=" in optionalarguments:
			emb.add_field(name="Starting Time", value=optionalarguments.partition("starttime=")[2].partition(",")[0])
		emb.add_field(name="Current Participants ("+str(len(participants))+")", value=await upPartis(), inline=False)
		emb.set_footer(text="Use star to join the draft. Numbers to adjust draftsize. Octagonal sign to cancel creation. Notepad to toggle mentions.")
		
		msg = await self.bot.say(mention, embed=emb)
		await self.bot.pin_message(msg)
		async for message in self.bot.logs_from(msg.channel, limit=5, after=msg):
			if message.type.pins_add:
				await self.bot.delete_message(message)

		async def toggleMentions():
			if self.men == True:
				self.men = False
				emb.set_field_at(0, name="Host", value=host.display_name)
			else:
				self.men = True
				emb.set_field_at(0, name="Host", value=host.mention)

			emb.set_field_at(len(emb.fields)-1, name="Current Participants ("+str(len(participants))+")", value = await upPartis(), inline=False)
			await self.bot.edit_message(msg, embed=emb)

		buttons = ["⭐", "🔢", "🛑", "🗒"]	# star, numpad, stop, notepad

		for b in buttons:
			await self.bot.add_reaction(msg, b)

		async def handleReaction(react):
			if react.user != self.bot.user:
				if not react.reaction.emoji in buttons:
					await self.bot.remove_reaction(msg, react.reaction.emoji, react.user)
				else:
					if Path("data/drafting/playerData/"+react.user.id+".p").is_file():
						if react.reaction.emoji == "🛑":
							if react.user == host or modRole in react.user.roles:
								await self.bot.delete_message(msg)
								self.opendrafts.remove(draftobj.id)
								await self.bot.say(react.user.mention +" canceled the creation of the draft '"+draftobj.name+"'")
								print("## Draft '"+draftobj.name+"' has been canceled")
								return True
							else:
								await self.bot.remove_reaction(msg, react.reaction.emoji, react.user)

						elif react.reaction.emoji == "🗒":
							await self.bot.remove_reaction(msg, react.reaction.emoji, react.user)
							await toggleMentions()

						elif react.reaction.emoji == "⭐":
							if eligiblerole in react.user.roles:
								await self.bot.remove_reaction(msg, react.reaction.emoji, react.user)
								if react.user in participants:
									participants.remove(react.user)
									emb.set_field_at(len(emb.fields)-1, name="Current Participants ("+str(len(participants))+")", value = await upPartis(), inline=False)
									await self.bot.edit_message(msg, embed=emb)
								else:
									participants.append(react.user)
									emb.set_field_at(len(emb.fields)-1, name="Current Participants ("+str(len(participants))+")", value = await upPartis(), inline=False)
									await self.bot.edit_message(msg, embed=emb)
							else:
								await self.bot.remove_reaction(msg, react.reaction.emoji, react.user)

						elif react.reaction.emoji == "🔢":
							if react.user != host:
								await self.bot.remove_reaction(msg, react.reaction.emoji, react.user)
							else:
								await self.bot.clear_reactions(msg)
								emojis = ["◀"]	# back emoji
								for m in range(2,10):
									emoji = str(m)+"\u20e3"
									emojis.append(emoji)
								for e in emojis:
									await self.bot.add_reaction(msg, e)

								numbers = {"1\u20e3":1, "2\u20e3":2, "3\u20e3":3, "4\u20e3":4, "5\u20e3":5, "6\u20e3":6, "7\u20e3":7, "8\u20e3":8, "9\u20e3":9}
								while True:
									n = await self.bot.wait_for_reaction(message=msg, timeout=15)
									if n == None:
										break
									if n.user != self.bot.user:
										if n.reaction.emoji in emojis:
											if n.reaction.emoji == "◀":	# back
												break
											num = numbers[n.reaction.emoji]
											draftobj.size = num
											break
										else:
											await self.bot.remove_reaction(msg, n.reaction.emoji, n.user)
								emb.set_field_at(2, name="Size", value=str(draftobj.size))
								emb.title = "New "+str(draftobj.size)+" man Draft '"+draftobj.name+"'"
								await self.bot.edit_message(msg, embed=emb)
								await self.bot.clear_reactions(msg)
								for b in buttons:
									await self.bot.add_reaction(msg, b)

					else:
						await self.bot.say(react.user.mention+", you are not registered yet. Please do so with **"+prefix[0]+"register** if you want to participate in drafts", delete_after=autodeletetime)
						await self.bot.remove_reaction(msg, react.reaction.emoji, react.user)

		while True:
			r = await self.bot.wait_for_reaction(message=msg, timeout=10800)
			if r == None:
				await self.bot.delete_message(msg)
				self.opendrafts.remove(draftobj.id)
				await self.bot.say(draftobj.name +" timed out")
				print("## "+draftobj.name +" timed out")
				return

			d = await handleReaction(r)
			if d == True:
				break
			if r.user != self.bot.user:
				if len(participants) == draftobj.size:
					self.opendrafts.remove(draftobj.id)
					
					await self.bot.clear_reactions(msg)

					draftobj.status = "full"
					fullPlayersMsg = "The draft '"+draftobj.name+"'("+draftobj.id+") is filled up! \nThe players are: "
					for p in participants:
						draftobj.players.append(p.id)
						fullPlayersMsg = fullPlayersMsg + p.mention +", "
					fullPlayersMsg = fullPlayersMsg + "\nThe host is: " + host.mention
					fullPlayersMsg = fullPlayersMsg +"\nDo you want to start the draft?(Host only)"
					fullPlayersMsg = await self.bot.say(fullPlayersMsg)
					await self.bot.add_reaction(fullPlayersMsg, "❎")#no
					await self.bot.add_reaction(fullPlayersMsg, "✅")#yes
					while True:
						react = await self.bot.wait_for_reaction(message=fullPlayersMsg)
						if react.user != self.bot.user:
							if react.user == host or modRole in react.user.roles or marshalRole in react.user.roles:
								if react.reaction.emoji == "✅": # yes
									await self.bot.delete_message(msg)
									draftobj.status = "running"
									await self.bot.clear_reactions(fullPlayersMsg)
									await self.bot.edit_message(fullPlayersMsg, fullPlayersMsg.content+"\n*The draft has been started!*")

									playerRole = await self.bot.create_role(ctx.message.server, name=draftobj.name, hoist=False, permissions=discord.Permissions.none(), mentionable=True)
									draftobj.playerRole = playerRole.id
									for p in draftobj.players:
										plr = ctx.message.server.get_member(p)
										if plr == None:
											await self.bot.say("Player with the ID '"+p+"' is no longer on this server!")
											return
										roles = plr.roles
										roles.append(playerRole)
										await self.bot.replace_roles(plr, *roles)

									everyonePerms = discord.PermissionOverwrite(read_messages=False)
									playerPerms = discord.PermissionOverwrite(read_messages=True)
									channelname = re.sub("[^a-zA-Z0-9-_]", "", draftobj.name.replace(" ","_"))
									channel = await self.bot.create_channel(ctx.message.server, channelname, (ctx.message.server.default_role, everyonePerms),(playerRole, playerPerms),(marshalRole, playerPerms),(modRole, playerPerms))
									await self.bot.edit_channel(channel, topic=draftobj.id)
									draftobj.channel = channel.id

									await self.bot.say(host.mention+" started the draft '"+draftobj.name+"'("+draftobj.id+"). Happy drafting! \n"+playerRole.mention+" please use the specific textchannel "+channel.mention+" for setting the draft up(Use **!startdraft** there if you want to do an in-discord draft and **!createbracket** for a bracket) \nUse **'"+prefix[0]+"finishdraft <draftid> <draftpage>'** once you are finished or **'"+prefix[0]+"canceldraft <draftid>'** to cancel it.")
									await self.bot.whisper("DraftID of your Draft '"+draftobj.name+"':")
									await self.bot.whisper(draftobj.id)

									with open("data/drafting/drafts/"+draftobj.id+".p", "wb") as f:
										pickle.dump(draftobj, f)
									print("## Draft '"+draftobj.name+"' is now running")
									return True
								elif react.reaction.emoji == "❎": # no
									await self.bot.delete_message(fullPlayersMsg)
									self.opendrafts.append(draftobj.id)
									for b in buttons:
										await self.bot.add_reaction(msg, b)
									break
								else:
									await self.bot.remove_reaction(fullPlayersMsg, react.reaction.emoji, react.user)
							else:
								await self.bot.remove_reaction(fullPlayersMsg, react.reaction.emoji, react.user)

	async def poolMsg(self, pool, title="", n=13):
		cn = 0
		cm = 0
		line = ""
		msgs = []
		for i in range(int(len(self.cards)/(n*2)) + (len(self.cards)%(n*2) > 0)):
			msgs.append('\u2063')
		title = "**"+title+"**\n"
		for c in pool:
			e = await getEmoji(self.bot, c["name"])
			line = line + str(e)
			cn += 1
			cm += 1
			if cn == n:
				cn = 0
				line = line + " \n"
				if cm == n*2:
					cm = 0
					for i in range(len(msgs)):
						if not len(msgs[i]) > 2:
							if line != "":
								msgs[i] = line
								line = ""
		for i in range(len(msgs)):
			if not len(msgs[i]) > 2:
				if line != "":
					msgs[i] = line
					break

		msgs = [title]+msgs+['\u2063']
		return msgs

	async def getCard(self, name):
		card = None
		for c in self.cards:
			if re.sub("[^a-zA-Z]", "", c["name"]) == name:
				card = c
				break
		return card


	@commands.command(pass_context=True)
	async def startdraft(self, ctx, timer=30):
		"""used for starting in-discord drafts
		Do not mistake this with !createdraft
		
		You can only run this in the respective channel of a draft(created by using !createdraft)
		Pick cards by using the reactions.
		The timer for each pick can be adjusted by adding a number in seconds. Standard is 30s. Minimum is 10
		
		While the draft is running you will not be able to talk in the channel
		"""
		draftid = ctx.message.channel.topic

		try:
			with open("data/drafting/drafts/"+draftid+".p", "rb") as f:
				draftobj = pickle.load(f)
		except:
			await self.bot.say("You can only use this command in a draft channel", delete_after=autodeletetime)
			return

		channel = ctx.message.server.get_channel(draftobj.channel)
		if ctx.message.channel != channel:
			await self.bot.say("You can only use this command in the draft channel", delete_after=autodeletetime)
			return
		if draftobj.status != "running":
			await self.bot.say("This draft is not running", delete_after=autodeletetime)
			return
		if ctx.message.author.id != draftobj.host:
			await self.bot.say("Only the host is able to start the draft", delete_after=autodeletetime)
			return

		perm = discord.PermissionOverwrite()
		perm.read_messages = True
		perm.send_messages = False
		perm.add_reactions = False
		playerRole = discord.utils.get(ctx.message.server.roles, id=draftobj.playerRole)
		await self.bot.edit_channel_permissions(channel, playerRole, perm)

		
		print("## Draft '"+draftobj.name+"' discord-draft has been started")

		players = []
		player_decks = {}
		for p in draftobj.players:
			plr = ctx.message.server.get_member(p)
			if plr == None:
				await self.bot.say("Player with the ID '"+p+"' is no longer on this server!")
				return
			players.append(plr)
			player_decks[plr.id] = []
		shuffle(players)

		if timer < 5:
			timer = 5

		tips = ["Did you know you can use Ctrl+F to check if a card is already drafted?", "Use the reactions below to pick your cards!", "In the last ten seconds of a turn this message will turn yellow to alarm you!", "Did you know that there are only 22 units that can attack air?", "Spells are really valuable! But you can still win without any!", "You can't chat in here during the drafting process: Less distraction, more drafting!", "Green means GO! Red means NO!", "Autopicks won't pick legendaries!"]
		emb = discord.Embed(title=draftobj.name, description="Each player picks one card after another in snakedraft format("+str(timer)+"s time)", color=discord.Colour.red())
		emb.set_footer(text=tips[randint(0,len(tips)-1)])
		emb.add_field(name="Status", value="initializing...", inline=False)
		for p in players:
			emb.add_field(name=p.display_name, value="\u2063", inline=False)

		pool = self.cards[:]
		drafted = []
		d = await self.poolMsg(drafted, "Drafted cards:")

		mainMsg = await self.bot.say(embed=emb)

		dMsgs = []
		for i in d:
			m = await self.bot.say(i)
			dMsgs.append(m)

		emojis = []
		for i in pool:
			e = await getEmoji(self.bot, i["name"])
			emojis.append(e)
		m1 = await self.bot.say("\u2063**A B C D E**")
		for e in emojis[:20]:
			await self.bot.add_reaction(m1, e)
		m1 = await self.bot.get_message(ctx.message.channel, m1.id)
		
		m2 = await self.bot.say("\u2063**F G H I **")
		for e in emojis[20:40]:
			await self.bot.add_reaction(m2, e)
		m2 = await self.bot.get_message(ctx.message.channel, m2.id)

		m3 = await self.bot.say("\u2063**K L M N P R**")
		for e in emojis[40:60]:
			await self.bot.add_reaction(m3, e)
		m3 = await self.bot.get_message(ctx.message.channel, m3.id)

		m4 = await self.bot.say("\u2063**S T V W X Z**")
		for e in emojis[60:]:
			await self.bot.add_reaction(m4, e)
		m4 = await self.bot.get_message(ctx.message.channel, m4.id)

		#perm.add_reactions = True
		playerRole = discord.utils.get(ctx.message.server.roles, id=draftobj.playerRole)
		await self.bot.edit_channel_permissions(channel, playerRole, perm)

		def check(reaction, user):
			return reaction.message.channel == channel and reaction.emoji in emojis
	
		for i in range(8):
			_round = "("+str(i+1)+"/8)"
			for j in range(draftobj.size):
				if i%2 != 0:
					j = draftobj.size-1-j
				turn = players[j]
				
				emb.color = discord.Colour.green()
				emb.set_field_at(0, name="Status", value="**"+turn.display_name+"**'s turn to pick "+_round, inline=False)
				await self.bot.edit_message(mainMsg, embed=emb)

				r = await self.bot.wait_for_reaction(user=turn, check=check, timeout=timer-10)
				if r == None:
					emb.color = discord.Colour.gold()
					await self.bot.edit_message(mainMsg, embed=emb)
					r = await self.bot.wait_for_reaction(user=turn, check=check, timeout=10)
				emb.set_field_at(0, name="Status", value="processing pick...", inline=False)
				emb.color = discord.Colour.red()
				await self.bot.edit_message(mainMsg, embed=emb)

				if r == None:
					card = pool[randint(0,len(pool)-1)]
					while card["rarity"] == "Legendary":
						card = pool[randint(0,len(pool)-1)]
					emoji = await getEmoji(self.bot, card["name"])
					
					for m in [m1,m2,m3,m4]:
						msg = discord.utils.find(lambda n: n.emoji == emoji, m.reactions)
						if msg != None:
							msg = msg.message
							r = discord.utils.get(msg.reactions, emoji=emoji)
							break
				else:
					card = await self.getCard(r.reaction.emoji.name)
					emoji = r.reaction.emoji
					r = r.reaction

				members = await self.bot.get_reaction_users(r)
				for u in members:
					await self.bot.remove_reaction(r.message, r.emoji, u)

				pool.remove(card)
				drafted.append(card)
				d = await self.poolMsg(drafted, "Drafted cards:")
				
				for m in range(len(dMsgs)):
					await self.bot.edit_message(dMsgs[m], d[m])

				player_decks[turn.id].append(card["id"])

				emb.set_field_at(j+1, name=turn.display_name, value=emb.fields[j+1].value+str(emoji), inline=False)
				await self.bot.edit_message(mainMsg, embed=emb)


		emb.set_field_at(0, name="Status", value="over", inline=False)
		emb.color = discord.Colour.default()
		await self.bot.edit_message(mainMsg, embed=emb)

		dic = emb.to_dict()
		draftobj.decks = dic["fields"][1:]
		with open("data/drafting/drafts/"+draftid+".p", "wb") as f:
			pickle.dump(draftobj, f)

		await self.bot.delete_messages([m1,m2,m3,m4])

		await self.bot.say("**DECK LINKS**")
		for p in players:
			await self.bot.say(p.display_name + ": https://link.clashroyale.com/deck/en?deck={}".format(";".join([str(i) for i in player_decks[turn.id]])))
		
		perm = discord.PermissionOverwrite()
		perm.read_messages = True
		perm.send_messages = True
		await self.bot.edit_channel_permissions(channel, playerRole, perm)

	@commands.command(pass_context=True)
	async def createbracket(self, ctx):
		"""creates a round robin bracket for the draft

		Can only be used by the host of the draft in the draftchannel!

		The results of the bracket will be entered into the draftfile.
		If you want the results to be processed and trophies adjusted you need a Marshal or mod to either finish your draft or use !processresults
		"""
		draftid = ctx.message.channel.topic
		try:
			with open("data/drafting/drafts/"+draftid+".p", "rb") as f:
				draftobj = pickle.load(f)
		except:
			await self.bot.say("You can only use this command in a draft channel", delete_after=autodeletetime)
			return

		channel = ctx.message.server.get_channel(draftobj.channel)
		if ctx.message.channel != channel:
			await self.bot.say("You can only use this command in the draft channel", delete_after=autodeletetime)
			return
		if draftobj.status != "running":
			await self.bot.say("This draft is not running", delete_after=autodeletetime)
			return
		modRole = discord.utils.get(ctx.message.server.roles, name="Mod")
		marshalRole = discord.utils.get(ctx.message.server.roles, name="Marshal")
		if ctx.message.author.id != draftobj.host and not modRole in ctx.message.author.roles and not marshalRole in ctx.message.author.roles:
			await self.bot.say("Only the host is able to create the bracket", delete_after=autodeletetime)
			return

		

		draftobj.status = "bracket"
		with open("data/drafting/drafts/"+draftid+".p", "wb") as f:
			pickle.dump(draftobj, f)

		players = []
		for p in draftobj.players:
			plr = ctx.message.server.get_member(p)
			if plr == None:
				await self.bot.say("Player with the ID '"+p+"' is no longer on this server!")
				return
			players.append(plr)

		'''players = []		# for testing on testserver
		for m in ctx.message.server.members:
			players.append(m)
		draftobj.size = len(players)-1'''

		if len(players) % 2:
			UserName = collections.namedtuple("UserName", "display_name")
			players.append(UserName(display_name="None"))

		rotation = players[:]

		fixtures = []
		for i in range(0, len(players)-1):
			fixtures.append(rotation)
			rotation = [rotation[0]] + [rotation[-1]] + rotation[1:-1]

		bracket = []
		for f in fixtures:
			n = len(f)
			bracket.append(list(zip(f[0:n//2],reversed(f[n//2:n]))))

		results = {}
		resEmb = discord.Embed(title="Results", description="Results of the individual players(W/L)", color=discord.Colour.teal())
		resEmb.set_footer(text="Use the tick to finish the bracket once all results are entered. The octagonal cancels this bracket.")
		for p in players:
			if p.display_name != "None":
				results[p.display_name] = [0,0]
				resEmb.add_field(name=p.display_name, value="0/0", inline=False)

		messages = []
		for r in range(len(bracket)):
			emb = discord.Embed(title="Round "+str(r+1), description="Use the notepad to enter the results of this round")
			for m in range(len(bracket[r])):
				p1 = bracket[r][m][0].display_name
				p2 = bracket[r][m][1].display_name
				emb.add_field(name="Match "+str(m+1) ,value="**"+p1+"**\n	vs\n**"+p2+"**")
			msg = await self.bot.say(embed=emb)
			await self.bot.add_reaction(msg, "📝")
			messages.append(msg.id)

		res = await self.bot.say(embed=resEmb)
		messages.append(res.id)
		await self.bot.add_reaction(res, "🛑")
		await self.bot.add_reaction(res, "☑")

		print("## Created Bracket for '"+draftobj.name+"'("+draftobj.id+")")


		def check(reaction, user):
			if modRole in user.roles or marshalRole in user.roles or user.id == draftobj.host:
				return reaction.message.id in messages and reaction.emoji in ["📝", "🛑", "☑", "✅"]
			else:
				return False

		emojis = []
		def checkEmoji(reaction, user):
			return reaction.emoji in emojis and (modRole in user.roles or marshalRole in user.roles or user.id == draftobj.host)

		host = ctx.message.server.get_member(draftobj.host)
		numbers = {"1\u20e3":1, "2\u20e3":2, "3\u20e3":3, "4\u20e3":4, "5\u20e3":5, "6\u20e3":6, "7\u20e3":7, "8\u20e3":8, "9\u20e3":9}
		complete = False
		while True:
			r = await self.bot.wait_for_reaction(check=check)
			msg = r.reaction.message
			
			if r.reaction.emoji == "🛑":
				for m in messages:
					msg = await  self.bot.get_message(channel, m)
					await self.bot.clear_reactions(msg)
				resEmb.color = discord.Colour.red()
				await self.bot.edit_message(res, embed=resEmb)

				with open("data/drafting/drafts/"+draftid+".p", "rb") as f:
					draftobj = pickle.load(f)
				draftobj.status = "running"
				with open("data/drafting/drafts/"+draftid+".p", "wb") as f:
					pickle.dump(draftobj, f)

				await self.bot.say("The Bracket has been canceled")
				print("## The bracket of "+draftobj.name+" has been canceled")
				break
			elif r.reaction.emoji == "☑":
				await self.bot.remove_reaction(msg, "☑", r.user)
				await self.bot.say("The bracket is not completed yet, please enter the missing results", delete_after=5)
			elif r.reaction.emoji =="✅":
				if complete == False:
					await self.bot.remove_reaction(msg, "✅", r.user)
					await self.bot.say("The bracket is not completed yet, please enter the missing results", delete_after=5)
				else:
					for m in messages:
						msg = await self.bot.get_message(channel, m)
						await self.bot.clear_reactions(msg)
					resEmb.color = discord.Colour.green()
					await self.bot.edit_message(res, embed=resEmb)
					with open("data/drafting/drafts/"+draftid+".p", "rb") as f:
						draftobj = pickle.load(f)
					draftobj.results = results
					draftobj.status = "running"
					with open("data/drafting/drafts/"+draftid+".p", "wb") as f:
						pickle.dump(draftobj, f)
					await self.bot.say("The Bracket has been completed")
					print("## The bracket of "+draftobj.name+" has been finished")
					break
			elif r.reaction.emoji == "📝":
				emb = discord.Embed(**msg.embeds[0])
				_round = int(emb.title[-1])
				for f in msg.embeds[0]["fields"]:
					emb.add_field(name=f["name"], value=f["value"])
				
				while True:
					emb.description = "Use the respective number of a match to enter the result for it. Use the back button to finish editing"
					emb.color = discord.Colour.blue()
					await self.bot.edit_message(msg, embed=emb)
					await self.bot.clear_reactions(msg)
					emojis = ["◀"]
					await self.bot.add_reaction(msg, "◀")
					for m in range(len(emb.fields)):
						emoji = str(m+1)+"\u20e3"
						emojis.append(emoji)
						await self.bot.add_reaction(msg, emoji)

					s = await self.bot.wait_for_reaction(message=msg, check=checkEmoji)
					if s.reaction.emoji == "◀":
						break
					else:
						match = numbers[s.reaction.emoji]

						while True:
							emb.description = "Use the numbers to select the winner of *match "+str(match)+"*"
							await self.bot.edit_message(msg, embed=emb)
							emojis = ["◀", "1\u20e3", "2\u20e3"]
							await self.bot.clear_reactions(msg)
							await self.bot.add_reaction(msg, "◀")
							await self.bot.add_reaction(msg, "1\u20e3")
							await self.bot.add_reaction(msg, "2\u20e3")

							t = await self.bot.wait_for_reaction(message=msg, check=checkEmoji)
							if t.reaction.emoji == "◀":
								break
							else:
								winner = numbers[t.reaction.emoji]
								p1 = bracket[_round-1][match-1][0].display_name
								p2 = bracket[_round-1][match-1][1].display_name
								if "None" in [p1, p2]:
									await self.bot.add_reaction(msg, "😂")
									await self.bot.add_reaction(msg, "⛔")
									await asyncio.sleep(0.5)
									break

								v = emb.fields[match-1].value.replace("*","")
								if not v.startswith("("):
									if winner == 1:
										results[p1] = [results[p1][0]+1, results[p1][1]]
										results[p2] = [results[p2][0], results[p2][1]+1]
										pr1 = "*(W)"+p1+"*"
										pr2 = "(L)"+p2
									else:
										results[p1] = [results[p1][0], results[p1][1]+1]
										results[p2] = [results[p2][0]+1, results[p2][1]]
										pr1 = "(L)"+p1
										pr2 = "*(W)"+p2+"*"
								else:
									if winner == 1:
										if not v.startswith("(W)"):
											results[p1] = [results[p1][0]+1, results[p1][1]-1]
											results[p2] = [results[p2][0]-1, results[p2][1]+1]
										pr1 = "*(W)"+p1+"*"
										pr2 = "(L)"+p2
									else:
										if not v.startswith("(L)"):
											results[p1] = [results[p1][0]-1, results[p1][1]+1]
											results[p2] = [results[p2][0]+1, results[p2][1]-1]
										pr1 = "(L)"+p1
										pr2 = "*(W)"+p2+"*"

								emb.set_field_at(match-1, name="Match "+str(match) ,value="**"+pr1+"**\n	vs\n**"+pr2+"**")
								
								for f in range(len(resEmb.fields)):
									if resEmb.fields[f].name == p1:
										resEmb.set_field_at(f, name=p1, value=str(results[p1][0])+"/"+str(results[p1][1]), inline=False)
									elif resEmb.fields[f].name == p2:
										resEmb.set_field_at(f, name=p2, value=str(results[p2][0])+"/"+str(results[p2][1]), inline=False)
								await self.bot.edit_message(res, embed=resEmb)

								if complete == False:
									c = 0
									for key in results:
										if results[key][0]+results[key][1] == draftobj.size-1:
											c += 1
									if c == draftobj.size:
										complete = True
										await self.bot.remove_reaction(res, "☑", self.bot.user)
										await self.bot.add_reaction(res, "✅")
								break

				emb.color = discord.Colour.default()
				emb.description = "Use the notepad to enter the results of this round"
				await self.bot.edit_message(msg, embed=emb)
				await self.bot.clear_reactions(s.reaction.message)
				await self.bot.add_reaction(msg, "📝")

	@commands.command(pass_context=True)
	async def canceldraft(self, ctx, *, draftid=""):
		"""cancels a running draft
		(this command is not used to cancel a draft that is still in the process of making. Use the octagonal sign or the cross instead)

		You need to either enter a valid ID of the draft that should get canceled or use this command in the drafts channel
		"""
		if draftid == "":
			draftid = ctx.message.channel.topic
		
		try:
			with open("data/drafting/drafts/"+draftid+".p", "rb") as f:
				draftobj = pickle.load(f)
		except:
			await self.bot.say("You need to either enter a valid ID of the draft that should get canceled or use this command in the drafts channel", delete_after=autodeletetime)
			return

		if draftobj.status == "finished":
			await self.bot.say("This Draft is finished")
			return
		if draftobj.status == "canceled":
			await self.bot.say("This Draft has already been canceled")
			return

		modRole = discord.utils.get(ctx.message.server.roles, name="Mod")
		marshalRole = discord.utils.get(ctx.message.server.roles, name="Marshal")
		if ctx.message.author.id == draftobj.host or modRole in ctx.message.author.roles or marshalRole in ctx.message.author.roles:
			playerRole = discord.utils.get(ctx.message.server.roles, id=draftobj.playerRole)
			await self.bot.delete_role(ctx.message.server, playerRole)

			lobby = discord.utils.get(ctx.message.server.channels, name="draft_challenge")
			await self.bot.send_message(lobby, ctx.message.author.mention +" canceled the draft '"+draftobj.name+"'("+draftid+")")
			draftobj.status = "canceled"
			with open("data/drafting/drafts/"+draftid+".p", "wb") as f:
				pickle.dump(draftobj, f)
			
			print("## The draft '"+draftobj.name+"' has been canceled")
			
			channel = ctx.message.server.get_channel(draftobj.channel)
			await self.bot.delete_channel(channel)
		else:
			await self.bot.say("Only the host of the draft is allowed to cancel the draft", delete_after=autodeletetime)

	@commands.command(pass_context=True)
	async def finishdraft(self, ctx, draftid="", draftpage=""):
		"""finishes a running draft and processes the results
		(this command is not used to cancel a draft that is still in the process of making. Use the octagonal sign or the cross instead)
		
		'draftid' (You need to enter the id of the running draft that is supposed to be finished.)

		'draftpage' (Please enter the clashvariant.com link of your draft if you drafted there)
		
		If you entered the results through the in-discord bracket system you need to be a Marshal or Mod for the results to be processed and trophies adjusted.

		You need to either enter a valid ID of the draft that should get finished or use this command in the drafts channel
		"""
		if draftid == "":
			draftid = ctx.message.channel.topic

		try:
			with open("data/drafting/drafts/"+draftid+".p", "rb") as f:
				draftobj = pickle.load(f)
		except:
			await self.bot.say("You need to either enter a valid ID of the draft that should get finished or use this command in the drafts channel", delete_after=autodeletetime)
			return

		if draftobj.status == "finished":
			await self.bot.say("This Draft is already finished")
			return
		if draftobj.status == "canceled":
			await self.bot.say("This Draft has been canceled")
			return
		if draftobj.status == "bracket":
			await self.bot.say("There is still a bracket running in this draft. Please complete or cancel it first")
			return

		modRole = discord.utils.get(ctx.message.server.roles, name="Mod")
		marshalRole = discord.utils.get(ctx.message.server.roles, name="Marshal")
		if ctx.message.author.id == draftobj.host or modRole in ctx.message.author.roles or marshalRole in ctx.message.author.roles:
			
			
			playerRole = discord.utils.get(ctx.message.server.roles, id=draftobj.playerRole)
			await self.bot.delete_role(ctx.message.server, playerRole)
			draftobj.status = "finished"
			draftobj.draftpage = draftpage

			with open("data/drafting/drafts/"+draftid+".p", "wb") as f:
				pickle.dump(draftobj, f)

			for plr in draftobj.players:
				try:
					with open("data/drafting/playerData/"+plr+".p", "rb") as p:
						plyr = pickle.load(p)
					if draftobj.host == plr:
						plyr.hosted += 1
					usr = ctx.message.server.get_member(plr)
					plyr.draft_amount += 1
					roles = await updateDrafterRole(ctx.message.server, plyr)
					await self.bot.replace_roles(usr, *roles)
					plyr.drafts.append(draftobj.id)
					if modRole in ctx.message.author.roles or marshalRole in ctx.message.author.roles:
						WL = draftobj.results[usr.display_name]
						if plyr.trophies + int(WL[0])-int(WL[1]) >= 0:
							plyr.trophies += int(WL[0])-int(WL[1])
						else:
							plyr.trophies = 0
						plyr.setArena()
						await manageLeaderboard(ctx.message.server, plyr)
					with open("data/drafting/playerData/"+plr+".p", "wb") as p:
						pickle.dump(plyr, p)
				except:
					print("## Error in Finishdraft at "+plr)

			with open("data/drafting/draftlist.p", "rb") as dl:
				l = pickle.load(dl)
			l.append([draftobj.name, draftobj.id, draftobj.date])
			with open("data/drafting/draftlist.p", "wb") as dl:
				pickle.dump(l, dl)
				
			lobby = discord.utils.get(ctx.message.server.channels, name="draft_challenge")
			await self.bot.send_message(lobby, ctx.message.author.mention +" finished the draft '"+draftobj.name+"'("+draftid+")")
			print("## The draft '"+draftobj.name+"' has been finished")

			channel = ctx.message.server.get_channel(draftobj.channel)
			await self.bot.delete_channel(channel)
		else:
			await self.bot.say("Only the host of the draft is allowed to finish the draft", delete_after=autodeletetime)

	@commands.command(pass_context=True, hidden=True)
	async def seasonreset(self, ctx):
		modRole = discord.utils.get(ctx.message.server.roles, name="Mod")
		if not modRole in ctx.message.author.roles:
			await self.bot.say("You are not allowed to use this command!", delete_after=autodeletetime)
			return
		
		await self.bot.say("Do you really want to iniate the seasonreset? Type 'yes'")
		y = await self.bot.wait_for_message(timeout=11, author=ctx.message.author, content="yes")
		if y == None:
			await self.bot.say("Seasonreset failed")
			return
		await self.bot.add_reaction(y, "👍")
		await self.bot.say("Iniated Seasonreset")

		for file in os.listdir("data/drafting/playerData/"):
			with open("data/drafting/playerData/"+file, "rb") as f:
				plyr = pickle.load(f)
			plyr.trophyreset()
			plyr.setArena()
			plyr.updateDraftAmount()
			await manageLeaderboard(ctx.message.server, plyr)
			roles = await updateDrafterRole(ctx.message.server, plyr)
			
			user = ctx.message.server.get_member(plyr.id)
			if user == None:
				print("## "+plyr.name+" does no longer exists, deleting his file...")
				os.remove("data/drafting/playerData/"+plyr.id+".p")
			else:
				await self.bot.replace_roles(user, *roles)
			with open("data/drafting/playerData/"+file, "wb") as f:
				pickle.dump(plyr, f)

		await self.bot.say("Succesfully finished seasonreset")
		print("## Succesfully finished seasonreset")

	@commands.command(pass_context=True)
	async def register(self, ctx):
		"""registeres you in our database so you can use the draft system"""
		plyr = Player(user=ctx.message.author)
		if Path("data/drafting/playerData/"+ctx.message.author.id+".p").is_file() == False:
			with open("data/drafting/playerData/"+ctx.message.author.id+".p", "wb") as f:
				pickle.dump(plyr, f)
			await self.bot.say("Succesfully registered "+ ctx.message.author.mention, delete_after=autodeletetime)
			print("## "+ctx.message.author.name+" succesfully registered")
			
		else:
			await self.bot.say(ctx.message.author.mention+", you are already registered", delete_after=autodeletetime)

	@commands.command(pass_context=True)
	async def unregister(self,ctx):
		"""deletes your entry in our database and all data within"""
		if Path("data/drafting/playerData/"+ctx.message.author.id+".p").is_file():
			os.remove("data/drafting/playerData/"+ctx.message.author.id+".p")
			await self.bot.say(ctx.message.author.mention+" successfully unregistered and deleted all data stored", delete_after=autodeletetime)
			print("## "+ctx.message.author.name+" succesfully unregistered")
			
		else:
			await self.bot.say(ctx.message.author.mention+" you are not registered", delete_after=autodeletetime)

	@commands.command(pass_context=True)
	async def draftprofile(self, ctx, playername=None):
		"""shows the profile of the selected player(either use name or tag)
		
		if no name is entered it will show your own profile
	
		Drafttrophies can be gained through playing official drafts hosted by Marshals.
		Your gain/loss gets calculated through your wins minus losses(can get negative values, eg. you loose trophies)
		
		Your arena is dependend on your trophies. Every 5 trophies you unlock a new one. You can also drop our of arenas!
	
		Drafts are the total count of your completed drafts.
		"""
		if playername == None:
			playername = ctx.message.author.display_name
		if len(ctx.message.mentions) > 0:
			playername = ctx.message.mentions[0].display_name
		try:
			player = discord.utils.get(ctx.message.server.members, display_name=playername)
		except:
			player = ""
		if Path("data/drafting/playerData/"+player.id+".p").is_file():
			with open("data/drafting/playerData/"+player.id+".p", "rb") as f:
				plyr = pickle.load(f)
			
			plyr.rank = await getRank(player)

			emb = discord.Embed(title="Profile", description="Player: "+player.display_name, color=0x3498db)
			emb.set_thumbnail(url=player.avatar_url)
			emb.add_field(name="Drafttrophies", value=plyr.trophies)
			emb.add_field(name="Legendtrophies", value=plyr.legendtrophies)
			emb.add_field(name="Arena", value=plyr.arena)
			emb.add_field(name="Rank", value=plyr.rank)
			emb.add_field(name="Drafts", value=plyr.draft_amount)
			emb.add_field(name="Last Seasons Drafts", value=plyr.old_draft_amount)
			await self.bot.say(embed=emb)
			print("## showed profile of "+player.display_name)
			
		else:
			await self.bot.say("Playername is either wrong or the player is not registered", delete_after=autodeletetime)

	@commands.command(pass_context=True)
	async def draftme(self, ctx):
		"""gives yourself the 'Drafter' role used to notify you of drafts happening"""
		if ctx.message.server == None:
			await self.bot.say("You can only use this command on a server")
			return
		drafter = discord.utils.get(ctx.message.server.roles, name="Drafter")
		if drafter in ctx.message.author.roles:
			await self.bot.say(ctx.message.author.mention +", you already have this role", delete_after=autodeletetime)
		else:
			await self.bot.add_roles(ctx.message.author, drafter)
			await self.bot.say('Given the role "Drafter" to '+ ctx.message.author.mention, delete_after=autodeletetime)
			print("## Gave role 'Drafter' to "+ ctx.message.author.display_name)
		

	@commands.command(pass_context=True)
	async def undraftme(self, ctx):
		"""removes the role 'Drafter' from you"""
		if ctx.message.server == None:
			await self.bot.say("You can only use this command on a server")
			return
		drafter = discord.utils.get(ctx.message.server.roles, name="Drafter")
		if drafter in ctx.message.author.roles:
			await self.bot.remove_roles(ctx.message.author, drafter)
			await self.bot.say('Removed the role "Drafter" from '+ ctx.message.author.mention, delete_after=autodeletetime)
			print("## Removed the role 'Drafter' from "+ ctx.message.author.display_name)
			
		else:
			await self.bot.say(ctx.message.author.mention +", you dont have this role", delete_after=autodeletetime)

	@commands.command(pass_context=True)
	async def template(self, ctx):
		"""a google docs template for entering the records of your draft

		create yourself a copy of this and you should be good to go
		"""
		await self.bot.say("https://docs.google.com/spreadsheets/d/1GKg2YtHehQrDEKqJ1obSECk0Drh_D1Scznh8Feuw1IE/edit?usp=sharing")
		print("## Sent link to template")
		

	@commands.command(pass_context=True)
	async def showdraft(self, ctx, draftid=""):
		"""Shows the informations of a draft"""
		if Path("drafts/"+draftid+".p").is_file():
			with open("drafts/"+draftid+".p", "rb") as f:
				draftobj = pickle.load(f)
			emb = discord.Embed(title="Draft information", description="Draft ID: "+draftid, color=0x3498db)
			emb.set_thumbnail(url=ctx.message.server.icon_url)
			emb.add_field(name="Name", value=draftobj.name)
			emb.add_field(name="Size", value=str(draftobj.size))
			emb.add_field(name="Date", value=draftobj.date)
			host = ctx.message.server.get_member(draftobj.host)
			if host != None:
				emb.add_field(name="Host", value=host.mention)
			else:
				emb.add_field(name="Host", value="Unknown")
			if draftobj.draftpage != "":
				emb.add_field(name="Draftpage", value=draftobj.draftpage)
			emb.add_field(name="Status", value=draftobj.status)
			eligibleRole = discord.utils.get(ctx.message.server.roles, id=draftobj.eligible)
			if eligibleRole != None:
				emb.add_field(name="Eligible", value=eligibleRole.name)
			else:
				emb.add_field(name="Eligible", value="Unknown")

			if draftobj.results == None:
				emb.add_field(name="Results", value="Nothing entered yet")	
			else:
				results = "*__Player__  __W/L__*\n"
				for key in draftobj.results:
					name = key
					if name.startswith("_"):
						name = name[1:]
					results = results + name +"\n               "+ str(draftobj.results[key][0]) +"/"+ str(draftobj.results[key][1])+"\n"
				emb.add_field(name="Results", value=results, inline=False)
			await self.bot.say(embed=emb)

			if draftobj.decks != None:
				deckEmb = discord.Embed(title="Decks", description="Decks of '"+draftobj.name+"'", color=0x3498db)
				for d in draftobj.decks:
					deckEmb.add_field(name=d["name"], value=d["value"], inline=False)
				await self.bot.say(embed=deckEmb)
			
			print("## showed draftinfos of "+ draftid)
			
		else:
			await self.bot.say("That draft does not exists", delete_after=autodeletetime)

	@commands.command(pass_context=True)
	async def draftlist(self, ctx):
		"""shows a list of the most recent drafts"""
		if not Path("data/drafting/draftlist.p").is_file():
			with open("data/drafting/draftlist.p", "wb") as f:
				l = [["listbeginning", "nothing to see here", "nope nothin"]]
				pickle.dump(l, f)
		with open("data/drafting/draftlist.p", "rb") as f:
			l = pickle.load(f)
		emb = discord.Embed(title="Draft list", description="The 10 most recent drafts", color=0x3498db)
		emb.set_thumbnail(url=ctx.message.server.icon_url)
		emb.set_footer(text="Use !showdraft <id> for more information on a single draft")
		if len(l) >= 10:
			r = 10
		else:
			r = len(l)
		for n in range(r, 1, -1):
			emb.add_field(name=str(r-n+1)+"- "+l[n-1][0]+" | "+l[n-1][2], value="ID: "+l[n-1][1], inline=False)
		await self.bot.say(embed=emb)
		print("## showed draftlist")
		

	@commands.command(pass_context=True)
	async def draftleaderboard(self, ctx):
		"""shows the top of all drafters"""
		if not Path("data/drafting/leaderboard.p").is_file():
			with open("data/drafting/leaderboard.p", "wb") as f:
				l = [["listbeginning", 0]]
				pickle.dump(l, f)
		with open("data/drafting/leaderboard.p", "rb") as f:
			l = pickle.load(f)
		emb = discord.Embed(title="Leaderboard", description="The top drafters", color=0x3498db)
		emb.set_thumbnail(url=ctx.message.server.icon_url)
		if len(l) >= 11:
			r = 11
		else:
			r = len(l)
		for n in range(r-1):
			emb.add_field(name=str(n+1)+"- "+l[n][0], value="    "+str(l[n][1])+" trophies", inline=False)
		await self.bot.say(embed=emb)
		print("## showed leaderboard")


	async def drafting(self, player1, player2, noleg):
		p1deckhalf1 = "-"
		p1deckhalf2 = "-"

		p2deckhalf1 = "-"
		p2deckhalf2 = "-"

		cardemb1 = discord.Embed(title="Card 1", color=discord.Colour.red())
		cardemb2 = discord.Embed(title="Card 2", color=discord.Colour.blue())

		p1card1 = await self.bot.send_message(player1, embed=cardemb1)
		p1card2 = await self.bot.send_message(player1, embed=cardemb2)

		p2card1 = await self.bot.send_message(player2, embed=cardemb1)
		p2card2 = await self.bot.send_message(player2, embed=cardemb2)

		pemb1 = discord.Embed(title="Minidraft vs "+player2.display_name, description="Wait for your turn", color=discord.Colour.green())
		pemb1.set_thumbnail(url=player2.avatar_url)
		pemb1.add_field(name="Round", value="1/4", inline=False)
		pemb1.add_field(name="Your deck", value=p1deckhalf1, inline=False)
		pemb1.add_field(name="Opponents deck", value=p2deckhalf2, inline=False)
		pemb1.add_field(name="Card 1", value="-")
		pemb1.add_field(name="Card 2", value="-")
		msg1 = await self.bot.send_message(player1, embed=pemb1)

		pemb2 = discord.Embed(title="Minidraft vs "+player1.display_name, description="Wait for your turn", color=discord.Colour.green())
		pemb2.set_thumbnail(url=player1.avatar_url)
		pemb2.add_field(name="Round", value="1/4", inline=False)
		pemb2.add_field(name="Your deck", value=p2deckhalf1, inline=False)
		pemb2.add_field(name="Opponents deck", value=p1deckhalf2, inline=False)
		pemb2.add_field(name="Card 1", value="-")
		pemb2.add_field(name="Card 2", value="-")
		msg2 = await self.bot.send_message(player2, embed=pemb2)

		def check(reaction, user):
			if user != self.bot.user:
				if reaction.emoji == "🔴" or reaction.emoji == "🔵":
					return True
			return False

		cardpool = []
		while len(cardpool) < 16:
			i = randint(0,len(self.cards)-1)
			if not self.cards[i] in cardpool:
				if noleg == True:
					if self.cards[i]["rarity"] == "Legendary":
						continue
				cardpool.append(self.cards[i])

		pool1 = []
		for i in range(0, 7, 2):
			pair = []
			pair.append(cardpool[i])
			pair.append(cardpool[i+1])
			pool1.append(pair)

		pool2 = []
		for i in range(8, 15, 2):
			pair = []
			pair.append(cardpool[i])
			pair.append(cardpool[i+1])
			pool2.append(pair)

		p1deckhalf1 = ""
		p1deckhalf2 = ""
		p2deckhalf1 = ""
		p2deckhalf2 = ""

		for r in range(4):
			#player 1
			pemb2.description = "Opponents turn"
			pemb2.set_field_at(0, name="Round", value=str(r+1)+"/4", inline=False)
			await self.bot.edit_message(msg2, embed=pemb2)

			cardemb1.set_image(url="http://www.clashapi.xyz/images/cards/"+pool1[r][0]['idName']+".png")
			cardemb2.set_image(url="http://www.clashapi.xyz/images/cards/"+pool1[r][1]['idName']+".png")

			pemb1.description = "Pick a Card (10 seconds time)"
			pemb1.set_field_at(0, name="Round", value=str(r+1)+"/4", inline=False)
			pemb1.set_field_at(3, name="Card 1", value=pool1[r][0]['name'])
			pemb1.set_field_at(4, name="Card 2", value=pool1[r][1]['name'])

			await self.bot.edit_message(p1card1, embed=cardemb1)
			await self.bot.edit_message(p1card2, embed=cardemb2)
			await self.bot.edit_message(msg1, embed=pemb1)
			await self.bot.add_reaction(msg1, "🔴") # red
			await self.bot.add_reaction(msg1, "🔵") # blue

			react = await self.bot.wait_for_reaction(message=msg1, timeout=10, check=check)
			if react == None:
				c = randint(1,2)
				if c == 1:
					p1deckhalf1 = p1deckhalf1 + pool1[r][0]['name'] + ", "
					p2deckhalf2 = p2deckhalf2 + pool1[r][1]['name'] + ", "
				else:
					p1deckhalf1 = p1deckhalf1 + pool1[r][1]['name'] + ", "
					p2deckhalf2 = p2deckhalf2 + pool1[r][0]['name'] + ", "

			elif react.reaction.emoji == "🔴": # red
				p1deckhalf1 = p1deckhalf1 + pool1[r][0]['name'] + ", "
				p2deckhalf2 = p2deckhalf2 + pool1[r][1]['name'] + ", "

			elif react.reaction.emoji == "🔵": # blue
				p1deckhalf1 = p1deckhalf1 + pool1[r][1]['name'] + ", "
				p2deckhalf2 = p2deckhalf2 + pool1[r][0]['name'] + ", "
			
			pemb1.description = "Opponents turn"
			pemb1.set_field_at(1, name="Your deck", value=p1deckhalf1, inline=False)
			pemb1.set_field_at(2, name="Opponents deck", value=p2deckhalf2, inline=False)
			pemb1.set_field_at(3, name="Card 1", value="-")
			pemb1.set_field_at(4, name="Card 2", value="-")

			await self.bot.delete_message(msg1)
			msg1 = await self.bot.send_message(player1, embed=pemb1)

			cardemb1.set_image(url="")
			cardemb2.set_image(url="")
			await self.bot.edit_message(p1card1, embed=cardemb1)
			await self.bot.edit_message(p1card2, embed=cardemb2)

			#player 2
			cardemb1.set_image(url="http://www.clashapi.xyz/images/cards/"+pool2[r][0]['idName']+".png")
			cardemb2.set_image(url="http://www.clashapi.xyz/images/cards/"+pool2[r][1]['idName']+".png")

			pemb2.description = "Pick a Card (10 seconds time)"
			pemb2.set_field_at(3, name="Card 1", value=pool2[r][0]['name'])
			pemb2.set_field_at(4, name="Card 2", value=pool2[r][1]['name'])

			await self.bot.edit_message(p2card1, embed=cardemb1)
			await self.bot.edit_message(p2card2, embed=cardemb2)
			await self.bot.edit_message(msg2, embed=pemb2)
			await self.bot.add_reaction(msg2, "🔴") # red
			await self.bot.add_reaction(msg2, "🔵") # blue

			react = await self.bot.wait_for_reaction(message=msg2, timeout=10, check=check)
			if react == None:
				c = randint(1,2)
				if c == 1:
					p2deckhalf1 = p2deckhalf1 + pool2[r][1]['name'] + ", "
					p1deckhalf2 = p1deckhalf2 + pool2[r][0]['name'] + ", "
				else:
					p2deckhalf1 = p2deckhalf1 + pool2[r][1]['name'] + ", "
					p1deckhalf2 = p1deckhalf2 + pool2[r][0]['name'] + ", "

			elif react.reaction.emoji == "🔴": # red
				p2deckhalf1 = p2deckhalf1 + pool2[r][0]['name'] + ", "
				p1deckhalf2 = p1deckhalf2 + pool2[r][1]['name']	+ ", "

			elif react.reaction.emoji == "🔵": # blue
				p2deckhalf1 = p2deckhalf1 + pool2[r][1]['name'] + ", "
				p1deckhalf2 = p1deckhalf2 + pool2[r][0]['name'] + ", "

			pemb2.set_field_at(1, name="Your deck", value=p2deckhalf1, inline=False)
			pemb2.set_field_at(2, name="Opponents deck", value=p1deckhalf2, inline=False)
			pemb2.set_field_at(3, name="Card 1", value="-")
			pemb2.set_field_at(4, name="Card 2", value="-")

			await self.bot.delete_message(msg2)
			msg2 = await self.bot.send_message(player2, embed=pemb2)

			cardemb1.set_image(url="")
			cardemb2.set_image(url="")
			await self.bot.edit_message(p2card1, embed=cardemb1)
			await self.bot.edit_message(p2card2, embed=cardemb2)

		pemb1.description = "Minidraft finished"
		pemb2.description = "Minidraft finished"
		await self.bot.edit_message(msg1, embed=pemb1)
		await self.bot.edit_message(msg2, embed=pemb2)

		await self.bot.send_message(player1, "Your final deck:\n"+"```"+p1deckhalf1+p1deckhalf2+"```")
		await self.bot.send_message(player2, "Your final deck:\n"+"```"+p2deckhalf1+p2deckhalf2+"```")

	@commands.group(pass_context=True)
	async def minidraft(self, ctx, opponent:discord.Member):
		"""creates a casual 1v1 minidraft 
		
		Minidrafts work the same way the ingame draftchallenge works.
		You need to @mention the user you want to challenge. He will have 15 Minutes to accept the challenge before it will timeout.

		The draft will be held over DMs with the bot
		"""
		challenger = ctx.message.author
		
		if opponent == challenger:
			await self.bot.say("You cant challenge yourself", delete_after=autodeletetime)
			return
		
		l = ""
		if ctx.invoked_subcommand is None:
			noleg = False
		else:
			noleg = True
			l = "\nNo legendaries will be able to be drafted"

		await self.bot.say(challenger.mention+" challenged "+opponent.mention+" for a minidraft"+l)
		print("## "+challenger.display_name+" challenged "+opponent.display_name+" for a minidraft"+l)

		chMsg = await self.bot.send_message(opponent, "You were challenged for a minidraft by "+challenger.display_name+". "+l+"\nDo you want to accept the challenge?")
		await self.bot.add_reaction(chMsg, "❎")#no
		await self.bot.add_reaction(chMsg, "✅")#yes

		def check_isBot(reaction, user):
			if user == self.bot.user:
				return False
			else:
				return True

		while True:
			react = await self.bot.wait_for_reaction(message=chMsg, timeout=900, check=check_isBot)
			if react == None:
				await self.bot.remove_reaction(chMsg, "❎", self.bot.user)
				await self.bot.remove_reaction(chMsg, "✅", self.bot.user)
				await self.bot.edit_message(chMsg, new_content=chMsg.content+"\n*The challenge timed out*")
				await self.bot.send_message(challenger, "Your challenge for "+opponent.display_name+" timed out")
				print("## "+challenger.display_name+"'s challenge for "+opponent.display_name+" timed out")
				return
			if react.reaction.emoji == "❎": #no
				await self.bot.remove_reaction(chMsg, "❎", self.bot.user)
				await self.bot.remove_reaction(chMsg, "✅", self.bot.user)
				await self.bot.edit_message(chMsg, new_content=chMsg.content+"\n*Challenge declined*")
				await self.bot.send_message(challenger, opponent.display_name+" declined your challenge")
				print("## "+challenger.display_name+"'s challenge for "+opponent.display_name+" got declined")
				return
			if react.reaction.emoji == "✅": # yes
				await self.bot.remove_reaction(chMsg, "❎", self.bot.user)
				await self.bot.remove_reaction(chMsg, "✅", self.bot.user)
				await self.bot.edit_message(chMsg, new_content=chMsg.content+"\n*Challenge accepted*")
				await self.bot.send_message(challenger, opponent.display_name+" accepted your challenge")
				print("## "+challenger.display_name+"'s challenge for "+opponent.display_name+" got accepted")
				break

		for i in range(2):
			if  i == 0:
				participant = challenger
			else:
				participant = opponent
			
			rdyCheck = await self.bot.send_message(participant, "Are you ready to start?")
			await self.bot.add_reaction(rdyCheck, "❎")#no
			await self.bot.add_reaction(rdyCheck, "✅")#yes

			rdy = await self.bot.wait_for_reaction(message=rdyCheck, timeout=180, check=check_isBot)
			if rdy == None:
				await self.bot.remove_reaction(rdyCheck, "❎", self.bot.user)
				await self.bot.remove_reaction(rdyCheck, "✅", self.bot.user)
				await self.bot.edit_message(rdyCheck, new_content=rdyCheck.content+"\n*Readycheck timed out*")
				await self.bot.send_message(challenger, participant.display_name+"'s readychheck timed out")
				await self.bot.send_message(opponent, participant.display_name+"'s readychheck timed out")
				print("## "+participant.display_name+"'s readycheck timed out")
				return
			if rdy.reaction.emoji == "✅": #yes
				await self.bot.remove_reaction(rdyCheck, "❎", self.bot.user)
				await self.bot.remove_reaction(rdyCheck, "✅", self.bot.user)
				await self.bot.edit_message(rdyCheck, new_content=rdyCheck.content+"\n*Readycheck cleared*")
				await self.bot.send_message(challenger, participant.display_name+" cleared readycheck")
				await self.bot.send_message(opponent, participant.display_name+" cleared readycheck")
				print("## "+participant.display_name+" cleared readycheck")
			else:
				await self.bot.remove_reaction(rdyCheck, "❎", self.bot.user)
				await self.bot.remove_reaction(rdyCheck, "✅", self.bot.user)
				await self.bot.edit_message(rdyCheck, new_content=rdyCheck.content+"\n*Readycheck declined*")
				await self.bot.send_message(challenger, participant.display_name+"'s readycheck declined")
				await self.bot.send_message(opponent, participant.display_name+"'s readycheck declined")
				print("## "+participant.display_name+"'s readycheck got declined")
				return

		await self.drafting(challenger, opponent, noleg)


		

def setup(bot):
	bot.add_cog(Drafting(bot))
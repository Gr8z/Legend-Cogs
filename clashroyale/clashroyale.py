import discord
from discord.ext import commands
from .utils.dataIO import dataIO, fileIO
import os
from __main__ import send_cmd_help
import time
import clashroyale as clashroyaleAPI

BOTCOMMANDER_ROLES =  ["Family Representative", "Clan Manager", "Clan Deputy", "Co-Leader", "Hub Officer", "admin"]
creditIcon = "https://i.imgur.com/TP8GXZb.png"
credits = "Bot by GR8 | Titan"

class clashroyale:
	"""Live statistics for Clash Royale"""

	def __init__(self, bot):
		self.bot = bot
		self.auth = self.bot.get_cog('crtools').auth
		self.tags = self.bot.get_cog('crtools').tags
		self.clash = clashroyaleAPI.Client(self.auth.getToken(), is_async=True)

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

	@commands.command(pass_context=True, aliases=['clashprofile'])
	async def clashProfile(self, ctx, member: discord.Member = None):
		"""View your Clash Royale Profile Data and Statstics."""

		if member is None:
			member = ctx.message.author

		await self.bot.type()
		try:
			profiletag = await self.tags.getTag(member.id)
			profiledata = await self.clash.get_player(profiletag)
		except clashroyale.RequestError:
			await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")
			return
		except KeyError:
			await self.bot.say("You need to first save your profile using ``!save #GAMETAG``")
			return

		if profiledata.clan is None:
			clanurl = "https://i.imgur.com/4EH5hUn.png"
		else:
			clanurl = profiledata.clan.badge.image

		embed=discord.Embed(title="", url="https://royaleapi.com/player/"+profiledata.tag, color=0xFAA61A)
		embed.set_author(name=profiledata.name + " (#"+profiledata.tag+")", icon_url=clanurl)
		embed.set_thumbnail(url="https://royaleapi.github.io/cr-api-assets/arenas/{}.png".format(profiledata.arena.arena.replace(' ', '').lower()))
		embed.add_field(name="Trophies", value=profiledata.trophies, inline=True)
		embed.add_field(name="Highest Trophies", value=profiledata.stats.max_trophies, inline=True)
		embed.add_field(name="Level", value=profiledata.stats.level, inline=True)
		embed.add_field(name="Arena", value=profiledata.arena.name, inline=True)
		if profiledata.clan is not None:
			embed.add_field(name="Clan", value=profiledata.clan.name, inline=True)
			embed.add_field(name="Role", value=profiledata.clan.role.capitalize(), inline=True)
		embed.add_field(name="Cards Found", value=str(profiledata.stats.cards_found)+"/86", inline=True)
		embed.add_field(name="Favourite Card", value=profiledata.stats.favorite_card.name, inline=True)
		embed.add_field(name="Games Played", value=profiledata.games.total, inline=True)
		embed.add_field(name="Tournament Games Played", value=profiledata.games.tournament_games, inline=True)
		embed.add_field(name="Wins", value=profiledata.games.wins, inline=True)
		embed.add_field(name="Losses", value=profiledata.games.draws, inline=True)
		embed.add_field(name="War Day Wins", value=profiledata.games.war_day_wins, inline=True)	
		embed.add_field(name="Three Crown Wins", value=profiledata.stats.three_crown_wins, inline=True)
		embed.add_field(name="Total Donations", value=profiledata.stats_total_donations, inline=True)
		embed.add_field(name="Clan Card Collected", value=profiledata.stats.clan_cards_collected, inline=True)
		embed.add_field(name="Challenge Max Wins", value=profiledata.stats.challenge_max_wins, inline=True)
		embed.add_field(name="Challenge Cards Won", value=profiledata.stats.challenge_cards_won, inline=True)
		embed.add_field(name="Tournament Cards Won", value=profiledata.stats.tournament_cards_won, inline=True)
		embed.set_footer(text=credits, icon_url=creditIcon)

		await self.bot.say(embed=embed)

	@commands.command(pass_context=True)
	async def chests(self, ctx, member: discord.Member = None):
		"""View your upcoming chest cycle for Clash Royale."""

		if member is None:
			member = ctx.message.author

		await self.bot.type()
		try:
			profiletag = await self.tags.getTag(member.id)
			profiledata = await self.clash.get_player_chests(profiletag)
		except clashroyale.RequestError:
			await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")
			return
		except KeyError:
			await self.bot.say("You need to first save your profile using ``!save #GAMETAG``")
			return

		valuechestText = ' '.join(profiledata.upcoming).replace('silver', '<:silver:385784583343439882>').replace('gold', '<:gold:385784630227369985>').replace('giant', '<:giant:380832560504373249>').replace('epic', '<:epic:380832620059033610>').replace('super magical', '<:super:380832745305276416>').replace('magical', '<:magic:380832656704798731>').replace('legendary', '<:legend:380832458482122752>')

		chest1 = "<:giant:380832560504373249> +" + str(profiledata.giant+1) + "  "
		chest2 = "<:epic:380832620059033610> +" + str(profiledata.epic+1) + "  "
		chest3 = "<:magic:380832656704798731> +" + str(profiledata.magical+1) + "  "
		chest4 = "<:super:380832745305276416> +" + str(profiledata.super_magical+1) + "  "
		chest5 = "<:legend:380832458482122752> +" + str(profiledata.legendary+1) + "  "

		embed=discord.Embed(title="", color=0xFAA61A, description="Your Upcoming chests.")
		embed.set_author(name="#"+profiletag)
		embed.add_field(name="Upcoming Chests", value=valuechestText, inline=False)
		embed.add_field(name="Special Chests", value=chest1+chest2+chest3+chest4+chest5, inline=False)
		embed.set_footer(text=credits, icon_url=creditIcon)
		
		await self.bot.say(embed=embed)

	@commands.command(pass_context=True, aliases=['clashdeck'])
	async def clashDeck(self, ctx, member: discord.Member = None):
		"""View yours or other's clash royale Deck"""

		if member is None:
			member = ctx.message.author

		await self.bot.type()

		try:
			profiletag = await self.tags.getTag(member.id)
			profiledata = await self.clash.get_player(profiletag, keys="deckLink")
		except clashroyale.RequestError:
			await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")
			return
		except KeyError:
			await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")
			return

		message = ctx.message
		message.content = ctx.prefix + "deck gl " + profiledata.deck_link
		message.author = member
		
		await self.bot.process_commands(message)

	@commands.command(pass_context=True)
	async def clan(self, ctx, clantag):
		"""View Clash Royale Clan statistics and information """

		await self.bot.type()

		try:
			clandata = await self.clash.get_clan(clantag)
		except clashroyale.RequestError:
			await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")
			return

		embed=discord.Embed(title=clandata.name + " (#" + clandata.tag + ")", url="https://legendclans.com/clanInfo/{}".format(clandata.tag), description=clandata.description, color=0xFAA61A)
		embed.set_thumbnail(url=clandata.badge.image)
		embed.add_field(name="Members", value=str(clandata.member_count)+"/50", inline=True)
		embed.add_field(name="Donations", value=str(clandata.donations), inline=True)
		embed.add_field(name="Score", value=str(clandata.score), inline=True)
		embed.add_field(name="Required Trophies", value=str(clandata.required_score), inline=True)
		embed.add_field(name="Status", value=str(clandata.type.title()), inline=True)
		embed.add_field(name="Country", value=str(clandata.location.name), inline=True)
		embed.set_footer(text=credits, icon_url=creditIcon)

		await self.bot.say(embed=embed)

	@commands.command(pass_context=True, aliases=['cw'])
	async def tournament(self, ctx, tag, password = None):
		"""View Clash Royale Tournament Information """

		await self.bot.type()

		tag = await self.tags.formatTag(tag)

		if not await self.tags.verifyTag(tag):
			await self.bot.say("The ID you provided has invalid characters. Please try again.")
			return

		await self.bot.delete_message(ctx.message)

		try:
			tourneydata = await self.clash.get_tournament(tag)
		except clashroyale.RequestError:
			await self.bot.say("Error: Tournament not found. Please double check your #TAG")
			return

		maxPlayers = tourneydata.max_players
		cards = self.getCards(maxPlayers)
		coins = self.getCoins(maxPlayers)

		embed=discord.Embed(title="Click this link to join the Tournament in Clash Royale!", url="https://legendclans.com/tournaments?id={}&pass={}".format(tag, password), color=0xFAA61A)
		embed.set_thumbnail(url='https://statsroyale.com/images/tournament.png')

		embed.set_author(name=tourneydata.name+" (#"+tourneydata.tag+")")

		embed.add_field(name="Players", value=str(tourneydata.current_players) + "/" + str(maxPlayers), inline=True)
		embed.add_field(name="Status", value=tourneydata.status.title(), inline=True)

		if not tourneydata.open:
			if password is not None:
				embed.add_field(name="Password", value=password, inline=True)
			else:
				await self.bot.say("Error: Please enter a tournament password.")
				return

		if tourneydata.status != "ended":

			if tourneydata.status != "inProgress":
				startTime = self.sec2tme((tourneydata.create_time + tourneydata.prep_time) - int(time.time()))
				embed.add_field(name="Starts In", value=startTime, inline=True)

			endTime = self.sec2tme((tourneydata.create_time + tourneydata.prep_time + tourneydata.duration) - int(time.time()))
			embed.add_field(name="Ends In", value=endTime, inline=True)


		embed.add_field(name="Hosted By", value=tourneydata.creator.name, inline=True)
		embed.add_field(name="Top prize", value="<:tournamentcards:380832770454192140> " + str(cards) + "	 <:coin:380832316932489268> " +  str(coins), inline=True)
		embed.set_footer(text=credits, icon_url=creditIcon)
		
		await self.bot.say(embed=embed)

	@commands.command(pass_context=True)
	async def save(self, ctx, profiletag : str, member: discord.Member = None):
		""" save your Clash Royale Profile Tag	

		Example:
			!save #CRRYTPTT @GR8
			!save #CRRYRPCC

		Type !contact to ask for help.
		"""

		server = ctx.message.server
		author = ctx.message.author

		profiletag = await self.tags.formatTag(profiletag)

		if not await self.tags.verifyTag(profiletag):
			await self.bot.say("The ID you provided has invalid characters. Please try again.")
			return

		await self.bot.type()
		
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

		try:
			profiledata = await self.clash.get_player(profiletag)

			checkUser = await self.tags.getUser(server.members, profiletag)
			if checkUser is not None:
				await self.bot.say("Error, This Player ID is already linked with **" + checkUser.display_name + "**")
				return

			await self.tags.linkTag(profiletag, member.id)

			embed = discord.Embed(color=discord.Color.green())
			avatar = member.avatar_url if member.avatar else member.default_avatar_url
			embed.set_author(name='{} (#{}) has been successfully saved.'.format(profiledata.name, profiletag), icon_url=avatar)
			await self.bot.say(embed=embed)
		except:
			await self.bot.say("We cannot find your ID in our database, please try again.")

def setup(bot):
	bot.add_cog(clashroyale(bot))

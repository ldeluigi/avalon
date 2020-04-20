# The Resistance: Avalon - github.com/cameronleong - 16/07/16 #

import random
import shelve
from random import shuffle, randint
from datetime import datetime
from enum import Enum
from collections import namedtuple
from dataclasses import dataclass

import discord
from discord import DMChannel

from text import *


class Team(Enum):
	GOOD = 0
	EVIL = 1

class Phase(Enum):
	INIT = 0
	LOGIN = 1
	NIGHT = 2
	QUEST = 3
	TEAMVOTE = 4
	PRIVATEVOTE = 5
	GAMEOVER = 6

@dataclass
class GameState:
	phase: Phase
	leader: int
	quest: int
	team_attempts: int
	quests_succeeded: int
	quests_failed: int
	required_fails: int

Role = namedtuple("Role", "team name")

SERVANTS = [Role(Team.GOOD, "{}, Loyal Servant of Arthur".format(name))
            for name in ["Galahad", "Tristan", "Guinevere", "Lamorak"]]
MINIONS = [Role(Team.EVIL, "{}, Minion of Mordred".format(name))
           for name in ["Agravain"]]
MERLIN = Role(Team.GOOD, "Merlin")
PERCIVAL = Role(Team.GOOD, "Percival")
ASSASSIN = Role(Team.EVIL, "The Assassin")
MORGANA = Role(Team.EVIL, "Morgana")
MORDRED = Role(Team.EVIL, "Mordred")


def channel_check(channel):
	def _check(m):
		return m.channel == channel
	return _check
def add_channel_check(check, channel):
	def _check(m):
		return channel_check(channel)(m) and check(m)
	return _check

def setup_game(num_players):
	rules = ([2, 3, 2, 3, 3] if num_players == 5
		else [2, 3, 4, 3, 4] if num_players == 6
		else [2, 3, 3, 4, 4] if num_players == 7
		else [3, 4, 4, 5, 5] if 8 <= num_players <= 10
		else None)
	if num_players == 5:
		roles = SERVANTS[:2] + MINIONS[:1] + [MERLIN, ASSASSIN]
	elif num_players == 6:
		roles = SERVANTS[:3] + MINIONS[:1] + [MERLIN, ASSASSIN]
	elif num_players == 7:
		roles = SERVANTS[:2] + MINIONS[:1] + [MERLIN, ASSASSIN, PERCIVAL, MORGANA]
	elif num_players == 8:
		roles = SERVANTS[:3] + MINIONS[:1] + [MERLIN, ASSASSIN, PERCIVAL, MORGANA]
	elif num_players == 9:
		roles = SERVANTS[:3] + MINIONS[:1] + [MERLIN, ASSASSIN, MORDRED, PERCIVAL, MORGANA]
	elif num_players == 10:
		roles = SERVANTS[:4] + MINIONS[:1] + [MERLIN, ASSASSIN, MORDRED, PERCIVAL, MORGANA]
	else:
		roles = None
	return rules, roles

async def avalon(client, message):			#main loop
	#Declarations
	playerlist = [] 				#list of players in the game
	rules = [] 					#number of players for each quest.
	roles = {} 					#active roles based on the # of players. it can be changed.
	canreject = []
	cantreject = []
	gamestate = GameState(Phase.INIT, 0, 1, 5, 0, 0, 1)
	boardstate = [":red_circle:",":red_circle:",":red_circle:",":red_circle:",":red_circle:"]

	if gamestate.phase == Phase.INIT: await login(client, message, playerlist, gamestate, rules, roles)
	if gamestate.phase == Phase.NIGHT: await night(client, message, playerlist, gamestate, rules, roles, canreject, cantreject)
	names = []
	while gamestate.phase in (Phase.QUEST, Phase.TEAMVOTE, Phase.PRIVATEVOTE):
		if gamestate.phase == Phase.QUEST: await quest(client, message, playerlist, gamestate, rules, roles, boardstate, names)
		if gamestate.phase == Phase.TEAMVOTE: await teamvote(client, message, playerlist, gamestate, rules, roles, boardstate, names)
		if gamestate.phase == Phase.PRIVATEVOTE: await privatevote(client, message, playerlist, gamestate, rules, roles, boardstate, names, canreject)
	if gamestate.phase == Phase.GAMEOVER: await gameover(client, message, playerlist, gamestate, rules, roles, boardstate, names, canreject, cantreject)

async def login(client,message,playerlist,gamestate,rules,roles):
	#Login Phase
	gamestate.phase = Phase.LOGIN
	await message.channel.send(loginStr)
	while gamestate.phase == Phase.LOGIN:
		reply = await client.wait_for('message', check=channel_check(message.channel))
		if reply.content == "!join" and len(playerlist) <= 10:
			if reply.author not in playerlist:
				await message.channel.send(joinStr.format(reply.author.mention))
				playerlist.append(reply.author)
				if len(playerlist) == 5:
					await message.channel.send(fiveStr.format(reply.author.mention))
				"""
				## TEST DATA ##
				bot1 = copy.deepcopy(reply.author)
				bot1.name = "Bot 1"
				playerlist.append(bot1)

				bot2 = copy.deepcopy(reply.author)
				bot2.name = "Bot 2"
				playerlist.append(bot2)

				bot3 = copy.deepcopy(reply.author)
				bot3.name = "Bot 3"
				playerlist.append(bot3)

				bot4 = copy.deepcopy(reply.author)
				bot4.name = "Bot 4"
				playerlist.append(bot4)

				bot5 = copy.deepcopy(reply.author)
				bot5.name = "Bot 5"
				playerlist.append(bot5)

				bot6 = copy.deepcopy(reply.author)
				bot6.name = "Bot 6"
				playerlist.append(bot6)

				bot7 = copy.deepcopy(reply.author)
				bot7.name = "Bot 7"
				playerlist.append(bot7)

				bot8 = copy.deepcopy(reply.author)
				bot8.name = "Bot 8"
				playerlist.append(bot8)

				bot9 = copy.deepcopy(reply.author)
				bot9.name = "Bot 9"
				playerlist.append(bot9)"""

			else:
				await message.channel.send(alreadyJoinedStr.format(reply.author.mention))
		if reply.content == "!join" and len(playerlist) > 10:
			await message.channel.send(gameFullStr)
		if reply.content == "!start" and len(playerlist) < 5:
			## TEST DATA ##
			#bot1 = copy.deepcopy(reply.author)
			#bot1.name = "Bot 1"
			#playerlist.append(bot1)
			await message.channel.send(notEnoughPlayers)
		if reply.content == "!start" and len(playerlist) >= 5:
			rules, roles_list = setup_game(len(playerlist))
			if roles_list is None:
				await message.channel.send("Rule Loading Error!")
				continue
			roles += roles_list
			shuffle(roles)
			players_str = ", ".join(p.name for p in playerlist)
			roles_str = "\n".join(":black_small_square: {}".format(r.name) for r in roles_list)
			evil_count = sum(r.team == Team.EVIL for r in roles)
			good_count = len(playerlist) - evil_count
			await message.channel.send(startStr.format(players_str, len(playerlist), good_count, evil_count, roles_str))
			random.seed(datetime.now())
			gamestate.leader = randint(0,len(playerlist)-1)	#leadercounter
			gamestate.phase = Phase.NIGHT
		if reply.content == "!stop":
			await message.channel.send(stopStr)
			gamestate.phase = Phase.INIT

async def night(client,message,playerlist,gamestate,rules,roles,canreject,cantreject):
	await message.channel.send(nightStr)
	evillist = [player for player, role in zip(playerlist, roles)
			if role.team == Team.EVIL]
	merlinlist = [player for player, role in zip(playerlist, roles)
			if role.team == Team.EVIL and role != MORDRED]
	percivallist = [player for player, role in zip(playerlist, roles)
			if role in [MERLIN, MORGANA]]

	shuffle(evillist)
	shuffle(merlinlist)
	shuffle(percivallist)

	def toString(list1):
		string1 = ""
		for x in list1:
			string1 += ":black_small_square: "+x.name+"\n"
		return string1

	for player, role in zip(playerlist, roles):
		#print(str(player.name)+" is "+role.name)	#Cheat code to reveal all roles for debugging purposes
		if role in SERVANTS:
			cantreject.append(player)
			await player.send(loyalDM.format(player.name, key))
		if role in MINIONS:
			canreject.append(player)
			await player.send(minionDM.format(player.name, key, toString(evillist)))
		if role == MERLIN:
			cantreject.append(player)
			await player.send(merlinDM.format(player.name, key, toString(merlinlist)))
		if role == ASSASSIN:
			canreject.append(player)
			await player.send(assassinDM.format(player.name, key, toString(evillist)))
		if role == MORDRED:
			canreject.append(player)
			await player.send(mordredDM.format(player.name, key, toString(evillist)))
		if role == MORGANA:
			canreject.append(player)
			await player.send(morganaDM.format(player.name, key, toString(evillist)))
		if role == PERCIVAL:
			cantreject.append(player)
			await player.send(percivalDM.format(player.name,key,toString(percivallist)))
	await message.channel.send(night2Str)
	gamestate.phase = Phase.QUEST

def mentionToID(a:str):
	a = a.replace("<","")
	a = a.replace(">","")
	a = a.replace("@","")
	a = a.replace("!","")
	return a

async def quest(client,message,playerlist,gamestate,rules,roles,boardstate,names):

	if len(playerlist) >= 7 and gamestate.quest == 4:
		gamestate.required_fails = 2
	else:
		gamestate.required_fails = 1

	playersnamestring = "|"
	for x in playerlist:
		playersnamestring += "` "+x.name+" `|"
	boardstatestring = ""
	for x in boardstate:
		boardstatestring += x+" "

	await message.channel.send(teamStr.format(playersnamestring,playerlist[gamestate.leader].mention,gamestate.quest,rules[gamestate.quest-1],gamestate.required_fails,boardstatestring,rules[gamestate.quest-1]))
	while gamestate.phase == Phase.QUEST:
		votetrigger = await client.wait_for("message", check=channel_check(message.channel))
		if votetrigger.content.startswith("!party") and votetrigger.author == playerlist[gamestate.leader]:
			await message.channel.send(partyStr)
			names.clear()
			valid = 1
			playerlistIDs = list(map(lambda p : p.id, playerlist))
			#print(playerlistIDs)
			for user in votetrigger.mentions:
				names.append(user.mention)
				if user.id not in playerlistIDs:
					await message.channel.send(playernotingame.format(name))
					valid = 0
					break
			#print(names)

			if valid == 1:
				if len(names) == len(set(names)):
					if len(names) == rules[(gamestate.quest-1)]:
						await message.channel.send("Valid request submitted.")
						gamestate.phase = Phase.TEAMVOTE
					else:
						await message.channel.send(malformedStr.format(rules[gamestate.quest-1]))
				else:
					await message.channel.send(duplicateStr.format(rules[gamestate.quest-1]))
				#gamestate.phase = Phase.TEAMVOTE #cheatcode
		if votetrigger.content.startswith("!stop"):
			await message.channel.send(stopStr)
			gamestate.phase = Phase.INIT

async def teamvote(client,message,playerlist,gamestate,rules,roles,boardstate,names):
	await message.channel.send(teamvoteStr.format(gamestate.team_attempts))
	def votecheck(msg):
		if isinstance(msg.channel, DMChannel):
			if msg.author in templist:
				if msg.content == "!approve" or msg.content == "!reject":
					templist.remove(msg.author)
					return True
		elif msg.content.startswith('!stop'):
			return True
		return False

	while gamestate.phase == Phase.TEAMVOTE:
		#wait for votes
		stop = False
		vc=0
		rejectcounter=0
		voteStr="\n**Team Vote Results**:\n"
		templist = playerlist[:]
		for player in templist:
			if player == playerlist[gamestate.leader]:
				templist.remove(player)
		for j in range(0,len(playerlist)-1):
			vc += 1
			pmtrigger = await client.wait_for("message", check=votecheck)
			if pmtrigger.content == "!approve":
				voteStr += ":black_small_square: "+pmtrigger.author.name+" voted **approve**.\n"
			elif pmtrigger.content == "!reject":
				voteStr += ":black_small_square: "+pmtrigger.author.name+" voted **reject**.\n"
				rejectcounter += 1
			if pmtrigger.content == "!stop":
				stop = True
				break
			await message.channel.send(pmtrigger.author.mention+" has submitted their vote ("+str(vc)+"/"+str(len(playerlist)-1)+")")

		if stop == True:
			await message.channel.send(stopStr)
			gamestate.phase = Phase.INIT
			break

		#votes have been submitted
		if gamestate.leader == (len(playerlist)-1):
			gamestate.leader = 0
		else:
			gamestate.leader += 1

		if rejectcounter >= (len(playerlist) / 2):
			gamestate.team_attempts -= 1
			if gamestate.team_attempts == 0:
				voteStr += "\nThe team has been **rejected**. **Evil has won!**"
				await message.channel.send(voteStr)
				gamestate.phase = Phase.GAMEOVER #evil win state
			else:
				voteStr += "\nThe team has been **rejected**. Moving leader to the next player..."
				await message.channel.send(voteStr)
				gamestate.phase = Phase.QUEST
		else:
			gamestate.team_attempts = 5 #reset passcount
			voteStr += "\nThe team has been **approved**. Entering private vote phase."
			await message.channel.send(voteStr)
			gamestate.phase = Phase.PRIVATEVOTE

async def privatevote(client,message,playerlist,gamestate,rules,roles,boardstate,names,canreject):
	while gamestate.phase == Phase.PRIVATEVOTE:
		def privatevotecheck(msg):
			if isinstance(msg.channel, DMChannel):
				if msg.author in activeplayers and msg.author in canreject:
					if msg.content == "!success" or msg.content == "!fail":
						activeplayers.remove(msg.author)
						return True
				elif msg.author in activeplayers:
					if msg.content == "!success":
						activeplayers.remove(msg.author)
						return True
			elif msg.content.startswith('!stop'):
				return True
			return False
		stop = False
		fails = 0
		activeplayers = []
		namestring = ""

		for x in names:
			namestring += x+" "
		for player in playerlist:
			if player.mention in namestring:
				activeplayers.append(player)

		await message.channel.send(privatevoteStr.format(namestring))

		votecount = len(activeplayers)
		for j in range(0,votecount):
			pmtrigger = await client.wait_for("message", check=privatevotecheck)
			if pmtrigger.content == "!success":
				pass
			elif pmtrigger.content == "!fail":
				fails += 1
			if pmtrigger.content == "!stop":
				stop = True
				break
			await message.channel.send(str(pmtrigger.author.name)+" has completed their task.")
		if stop == True:
			await message.channel.send(stopStr)
			gamestate.phase = Phase.INIT
			break

		if fails >= (gamestate.required_fails):
			gamestate.quests_failed += 1
			boardstate[gamestate.quest-1] = ":no_entry_sign:"
			await message.channel.send("\nQuest **failed**. `"+str(fails)+"` adventurer(s) failed to complete their task.\n")
		else:
			gamestate.quests_succeeded += 1
			boardstate[gamestate.quest-1] = ":o:"
			await message.channel.send("\nQuest **succeeded**. `"+str(fails)+"` adventurer(s) failed to complete their task.\n")

		gamestate.quest += 1

		if gamestate.quests_succeeded == 3 or gamestate.quests_failed == 3:
			gamestate.phase = Phase.GAMEOVER
		else:
			gamestate.phase = Phase.QUEST

async def gameover(client,message,playerlist,gamestate,rules,roles,boardstate,names,canreject,cantreject):
	assassin = playerlist[roles.index(ASSASSIN)]
	merlin = playerlist[roles.index(MERLIN)]
	def assassincheck(msg):
		if msg.content.startswith('!assassinate') and msg.author == assassin and len(msg.mentions)==1:
			return True
		elif msg.content.startswith('!stop'):
			return True
		return False
	await message.channel.send(gameoverStr)
	if gamestate.quests_succeeded == 3:
		await message.channel.send("Three quests have been completed successfully.\n\nThe assassin may now `!assassinate` someone. You only have ONE chance to get the name and formatting correct. Make sure you tag the correct target with @!")
		ass = await client.wait_for("message", check=add_channel_check(assassincheck, message.channel))
		if ass.content.startswith('!assassinate'):
			killedID = ass.mentions[0].id
			if merlin.id == killedID:
				await message.channel.send("Merlin has been assassinated!\n\n")
				await message.channel.send(":smiling_imp: **Evil** Wins :smiling_imp:")
				for player in canreject:
					await addscore(client,message,player)
			else:
				await message.channel.send("GOT THE WRONG GUY SON\n\n")
				await message.channel.send(":angel: **Good** Wins :angel: ")
				for player in cantreject:
					await addscore(client,message,player)

	elif gamestate.quests_failed == 3:
		await message.channel.send(":smiling_imp: **Evil** Wins :smiling_imp: ")
		for player in canreject:
			await addscore(client,message,player)
	elif gamestate.quests_succeeded != 3 and gamestate.quests_failed != 3:
		await message.channel.send(":smiling_imp: **Evil** Wins by failure :smiling_imp: ")
		for player in canreject:
			await addscore(client,message,player)
	roles_str = "\n".join("{} is **{}**".format(player.name, role.name)
			for player, role in zip(playerlist, roles))
	roles_str += "\n**30 frickin' dollarydoos** have been credited to members of the winning team.\n\n"
	await message.channel.send(roles_str)
	await message.channel.send(stopStr)
	gamestate.phase = Phase.INIT

async def addscore(client, message, user):
	return
	score = shelve.open('leaderboard', writeback=True)
	if user.id in score:
		current = score[user.id]
		score[user.id] = current + 30
	else:
		score[user.id] = 30
	#await client.send_message(message.channel, str(user.name)+" now has "+str(score[user.id])+" dollarydoos")
	score.sync()
	score.close()

async def scoreboard(client,message):
	counter = 0
	scoreStr= "\n         :star: Top 10 Players :star: \n\n"
	score = shelve.open('leaderboard')
	klist = score.keys()
	scoreboard = {}
	for key in klist:
		m = discord.utils.get(message.guild.members, id=key)
		scoreboard[m.name] = score[key]

	for item in sorted(scoreboard, key=scoreboard.get, reverse=True):
		if counter < 10:
			scoreStr += ':military_medal: `{:20}{:>4}`\n'.format(str(item),str(scoreboard[item]))
			counter = counter + 1
	await message.channel.send(scoreStr)
	score.close()

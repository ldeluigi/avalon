# The Resistance: Avalon - github.com/cameronleong - 16/07/16 #

import asyncio
import random
import re
import shelve
from datetime import datetime
from random import randrange, shuffle
from dataclasses import dataclass, field
from typing import List, Mapping

import discord
from discord import DMChannel

from model import Team, Phase, Role, Quest, Player
from msgqueue import MsgQueue
from skins import Skin, Skins
from strings import StringSet, StringSets


SERVANT = Role(Team.GOOD, "servant")
MINION = Role(Team.EVIL, "minion",)
MERLIN = Role(Team.GOOD, "merlin")
PERCIVAL = Role(Team.GOOD, "percival")
ASSASSIN = Role(Team.EVIL, "assassin")
MORGANA = Role(Team.EVIL, "morgana")
MORDRED = Role(Team.EVIL, "mordred")
OBERON = Role(Team.EVIL, "oberon")

NAME_TO_ROLE = {
	'servant': SERVANT,
	'minion': MINION,
	'merlin': MERLIN,
	'percival': PERCIVAL,
	'assassin': ASSASSIN,
	'morgana': MORGANA,
	'mordred': MORDRED,
	'oberon': OBERON,
}

@dataclass
class GameState:
	phase: Phase = Phase.INIT    # current game phase
	quest_selection = False      # whether leader may choose any incomplete quest
	quests: List[Quest] = field(default_factory=list)
	players: List[Player] = field(default_factory=list)
	players_by_duid: Mapping[int, Player] = field(default_factory=dict)
	leader: int = 0              # index of leader player (0-based)
	current_quest: int = 1       # number of current quest (1-based)
	team_attempts: int = 5       # remaining attempts to form team (incl. current one)
	current_party: List[Player] = field(default_factory=list)
	skin: Skin = Skins["AVALON"]
	t: StringSet = StringSets["avalon-en-base"]
	@property
	def succeeded_quests(self):
		return sum(quest.winning_team is Team.GOOD for quest in self.quests)
	@property
	def failed_quests(self):
		return sum(quest.winning_team is Team.EVIL for quest in self.quests)


RE_PARTY_NAMES = re.compile(r"!party\s+.+")
RE_PARTY_QUEST_NAMES = re.compile(r"!party\s+(\d+)\s+.+")


def channel_check(channel):
	def _check(m):
		return m.channel == channel
	return _check
def add_channel_check(check, channel):
	def _check(m):
		return channel_check(channel)(m) and check(m)
	return _check



def setup_game(num_players, custom_roles):
	if num_players < 1 or num_players > 10:
		return None, None

	if num_players == 1: # Test scenario
		quests = [Quest(1) for n in range(5)]
	elif num_players == 2: # Test scenario
		quests = [Quest(2) for n in range(5)]
	elif num_players == 3: # Test scenario
		quests = [Quest(2) for n in range(5)]
	elif num_players == 4: # Test scenario
		quests = [Quest(2) for n in range(5)]
	else:
		adventurers = ([2, 3, 2, 3, 3] if num_players == 5
			else [2, 3, 4, 3, 4] if num_players == 6
			else [2, 3, 3, 4, 4] if num_players == 7
			else [3, 4, 4, 5, 5])
		quests = [Quest(n) for n in adventurers]
	if num_players >= 7:
		quests[3].required_fails = 2

	if len(custom_roles) > 0:
		if num_players == 4: # Test scenario
			good_count = 2
			evil_count = 2
		if num_players == 5:
			good_count = 3
			evil_count = 2
		elif num_players == 6:
			good_count = 4
			evil_count = 2
		elif num_players == 7:
			good_count = 4
			evil_count = 3
		elif num_players == 8:
			good_count = 5
			evil_count = 3
		elif num_players == 9:
			good_count = 6
			evil_count = 3
		elif num_players == 10:
			good_count = 6
			evil_count = 4
		else: # Test scenario
			good_count = num_players - 1
			evil_count = 1

		good_roles = [role for role in custom_roles if role.is_good][:good_count]
		while len(good_roles) < good_count:
			good_roles.append(SERVANT)
		evil_roles = [role for role in custom_roles if role.is_evil][:evil_count]
		while len(evil_roles) < evil_count:
			evil_roles.append(MINION)
		roles = good_roles + evil_roles
	else:
		if num_players == 1: # Test scenario
			roles = [ASSASSIN]
		elif num_players == 2: # Test scenario
			roles = [ASSASSIN, MERLIN]
		elif num_players == 3: # Test scenario
			roles = [ASSASSIN] + [SERVANT, MERLIN]
		elif num_players == 4: # Test scenario
			roles = [MINION, ASSASSIN] + [SERVANT, MERLIN]
		if num_players == 5:
			roles = [SERVANT, MERLIN, PERCIVAL, ASSASSIN, MORGANA]
		elif num_players == 6:
			roles = 2 * [SERVANT] + [MERLIN, PERCIVAL, ASSASSIN, MORGANA]
		elif num_players == 7:
			roles = 2 * [SERVANT] + [MERLIN, PERCIVAL, ASSASSIN, MORGANA, MORDRED]
		elif num_players == 8:
			roles = 3 * [SERVANT] + [MERLIN, PERCIVAL, ASSASSIN, MORGANA, MORDRED]
		elif num_players == 9:
			roles = 4 * [SERVANT] + [MERLIN, PERCIVAL, ASSASSIN, MORGANA, MORDRED]
		elif num_players == 10:
			roles = 4 * [SERVANT] + [MERLIN, PERCIVAL, ASSASSIN, MORGANA, MORDRED, OBERON]
	return quests, roles

def detect_configuration(command_text:str):
	command = command_text.lower() + " "
	skin, strings = Skins["AVALON"], StringSets["avalon-en-base"]
	if any(f' {x} ' in command for x in ["sw", "starwars", "star wars"]):
		strings = StringSets["avalon-en-starwars"]
		skin = Skins["STARWARS"]
	elif any(f' {x} ' in command for x in ["gs", "guerre stellari"]):
		strings = StringSets["avalon-it-starwars"]
		skin = Skins["STARWARS"]
	elif any(f' {x} ' in command for x in ["it", "ita", "italian", "italiano"]):
		strings = StringSets["avalon-it-base"]
	return skin, strings

async def avalon(client, message):			#main loop
	gamestate = GameState()
	gamestate.skin, gamestate.t = detect_configuration(message.content)
	await gamestate.skin.send_image(gamestate.skin.logo, message.channel)
	if gamestate.phase == Phase.INIT: await login(client, message, gamestate)
	if gamestate.phase == Phase.NIGHT: await night(client, message, gamestate)
	while gamestate.phase in (Phase.QUEST, Phase.TEAMVOTE, Phase.PRIVATEVOTE):
		if gamestate.phase == Phase.QUEST: await quest(client, message, gamestate)
		if gamestate.phase == Phase.TEAMVOTE: await teamvote(client, message, gamestate)
		if gamestate.phase == Phase.PRIVATEVOTE: await privatevote(client, message, gamestate)
	if gamestate.phase == Phase.GAMEOVER: await gameover(client, message, gamestate)

async def login(client, message, gamestate):
	#Login Phase
	gamestate.phase = Phase.LOGIN
	await message.channel.send(gamestate.t.loginStr)
	custom_roles = []
	while gamestate.phase == Phase.LOGIN:
		reply = await client.wait_for('message', check=channel_check(message.channel))
		if reply.content == "!join" and len(gamestate.players) <= 10:
			if not any(p.user.id == reply.author.id for p in gamestate.players):
				await confirm(reply)
				await message.channel.send(gamestate.t.joinStr(reply.author.mention))
				player = Player(reply.author.display_name, reply.author)
				gamestate.players.append(player)
				gamestate.players_by_duid[reply.author.id] = player
				if len(gamestate.players) == 5:
					await message.channel.send(gamestate.t.fiveStr(reply.author.mention))
			else:
				await deny(reply)
				await message.channel.send(gamestate.t.alreadyJoinedStr(reply.author.mention))
		if reply.content.startswith('!roles '):
			custom_role_names = reply.content.split(' ')[1:]
			custom_role_names = [name.lower() for name in custom_role_names if name != '']
			invalid_role_names = [name for name in custom_role_names if not name in NAME_TO_ROLE]
			if len(invalid_role_names) > 0:
				await error(reply)
				await message.channel.send(invalid_role_names[0] + ' is not a valid role.')
				continue

			await confirm(reply)
			if not 'merlin' in custom_role_names:
				custom_role_names.append('merlin')
				await message.channel.send('Merlin is a required role and was automatically added.')
			custom_roles = [NAME_TO_ROLE[name] for name in custom_role_names]
			await message.channel.send('Roles updated!')

		if reply.content == "!join" and len(gamestate.players) > 10:
			await deny(reply)
			await message.channel.send(gamestate.t.gameFullStr)
		if reply.content == "!start" and len(gamestate.players) < 5:
			await deny(reply)
			await message.channel.send(gamestate.t.notEnoughPlayers)
		if (reply.content == "!start" and len(gamestate.players) >= 5) or reply.content == "!teststart":
			await confirm(reply)
			gamestate.quests, roles_list = setup_game(len(gamestate.players), custom_roles)
			if roles_list is None:
				await message.channel.send("Rule Loading Error!")
				continue
			players_str = ", ".join(p.name for p in gamestate.players)
			evil_count = sum(r.is_evil for r in roles_list)
			good_count = len(gamestate.players) - evil_count
			random.seed(datetime.now())
			shuffle(gamestate.players)
			shuffle(roles_list)
			for player, role in zip(gamestate.players, roles_list):
				player.role = role
			gamestate.skin.assign_characters(gamestate.players)
			chars_list = [p.char.name for p in gamestate.players]
			shuffle(chars_list)
			roles_str = "\n".join(":black_small_square: {}".format(r) for r in chars_list)
			await message.channel.send(gamestate.t.startStr(players_str, len(gamestate.players), good_count, evil_count, roles_str))
			gamestate.leader = 0 # leader will be in first seat
			leader_rotation = randrange(len(gamestate.players))	# leadercounter
			gamestate.players = gamestate.players[leader_rotation:] + gamestate.players[:leader_rotation]
			gamestate.phase = Phase.NIGHT
		if reply.content == "!stop":
			await confirm(reply)
			await message.channel.send(gamestate.t.stopStr)
			gamestate.phase = Phase.INIT

async def night(client, message, gamestate):
	await message.channel.send(gamestate.t.nightStr)
	# evil players seen by each other
	evillist = [p for p in gamestate.players if p.role.is_evil and p.role is not OBERON]
	# evil players seen by Merlin (exclude Mordred)
	merlinlist = [p for p in gamestate.players if p.role.is_evil and p.role is not MORDRED]
	# players seen by Percival
	percivallist = [p for p in gamestate.players if p.role in [MERLIN, MORGANA]]

	shuffle(evillist)
	shuffle(merlinlist)
	shuffle(percivallist)

	def toString(players):
		return "\n".join(":black_small_square: {}".format(p.name) for p in players)

	for player in gamestate.players:
		#print(str(player.name)+" is "+player.char.name)	#Cheat code to reveal all roles for debugging purposes
		if player.role is SERVANT:
			secret = gamestate.t.loyalDM(player.name, player.char.name)
		if player.role is MINION:
			secret = gamestate.t.minionDM(player.name, player.char.name, toString(evillist))
		if player.role is MERLIN:
			secret = gamestate.t.merlinDM(player.name, player.char.name, toString(merlinlist))
		if player.role is ASSASSIN:
			secret = gamestate.t.assassinDM(player.name, player.char.name, toString(evillist))
		if player.role is MORDRED:
			secret = gamestate.t.mordredDM(player.name, player.char.name, toString(evillist))
		if player.role is MORGANA:
			secret = gamestate.t.morganaDM(player.name, player.char.name, toString(evillist))
		if player.role is PERCIVAL:
			secret = gamestate.t.percivalDM(player.name, player.char.name, toString(percivallist))
		if player.role is OBERON:
			secret = gamestate.t.oberonDM(player.name, player.char.name)
		await player.user.send(secret, file=gamestate.skin.get_image_file(player.char.image_path))
	await message.channel.send(gamestate.t.night2Str)
	gamestate.phase = Phase.QUEST

def mentionToID(a:str):
	a = a.replace("<","")
	a = a.replace(">","")
	a = a.replace("@","")
	a = a.replace("!","")
	return a

async def quest(client, message, gamestate):
	if gamestate.quest_selection:
		await gamestate.skin.send_table(gamestate, message.channel)
		await gamestate.skin.send_board(gamestate, message.channel)
		await message.channel.send(gamestate.t.teamReminderQuestSel)
	else:
		quest = gamestate.quests[gamestate.current_quest-1]
		await gamestate.skin.send_table(gamestate, message.channel)
		await gamestate.skin.send_board(gamestate, message.channel)
		await message.channel.send(gamestate.t.teamReminder(quest.adventurers))
	while gamestate.phase == Phase.QUEST:
		votetrigger = await client.wait_for("message", check=channel_check(message.channel))
		party_ptn = RE_PARTY_QUEST_NAMES if gamestate.quest_selection else RE_PARTY_NAMES
		party_match = party_ptn.fullmatch(votetrigger.content)
		if party_match and votetrigger.author == gamestate.players[gamestate.leader].user:
			if gamestate.quest_selection:
				quest_num = int(party_match.group(1))
				if not 1 <= quest_num <= len(gamestate.quests):
					await error(votetrigger)
					await message.channel.send(gamestate.t.malformedQuestSel(len(gamestate.quests)))
					continue
				quest = gamestate.quests[quest_num-1]
				if quest.winning_team is not None:
					await deny(votetrigger)
					await message.channel.send(gamestate.t.questAlreadyComplete(quest_num))
					continue
				gamestate.current_quest = quest_num
			gamestate.current_party.clear()
			party_ids = set()
			valid = True
			for user in votetrigger.mentions:
				if user.id in party_ids:
					await message.channel.send(gamestate.t.duplicateStr(quest.adventurers))
					valid = False
					break
				party_ids.add(user.id)
				if user.id not in gamestate.players_by_duid.keys():
					await message.channel.send(gamestate.t.playernotingame(user.display_name))
					valid = False
					break
			if valid:
				if len(party_ids) == quest.adventurers:
					await confirm(votetrigger)
					gamestate.current_party = [gamestate.players_by_duid[i] for i in party_ids]
					gamestate.phase = Phase.TEAMVOTE
				else:
					await error(votetrigger)
					await message.channel.send(gamestate.t.malformedStr(quest.adventurers))
				#gamestate.phase = Phase.TEAMVOTE #cheatcode
		elif votetrigger.content.startswith("!stop"):
			await confirm(votetrigger)
			await message.channel.send(gamestate.t.stopStr)
			gamestate.phase = Phase.INIT
		elif votetrigger.author == gamestate.players[gamestate.leader].user and votetrigger.content.startswith("!party"):
			await error(votetrigger)
			await message.channel.send(gamestate.t.malformedQuestSel(len(gamestate.quests)))

async def teamvote(client, message, gamestate):
	await message.channel.send(gamestate.t.teamvoteStr(gamestate.team_attempts, ", ".join(player.name for player in gamestate.current_party)))
	def votecheck(msg):
		if isinstance(msg.channel, DMChannel):
			if msg.author in voters:
				if msg.content == "!approve" or msg.content == "!reject":
					return True
		elif msg.content == '!stop':
			return True
		return False

	while gamestate.phase == Phase.TEAMVOTE:
		#wait for votes
		vc = 0
		rejectcounter = 0
		voteStr = gamestate.t.teamvoteResults
		voters = [p.user for p in gamestate.players]
		pending_voters = [p.user for p in gamestate.players]
		num_voters = len(voters)
		# del voters[leader]   # enable to exclude leader from voting
		for voter in voters:
			await voter.send(gamestate.t.privateVoteInfo(gamestate.t.leaderInvocation(gamestate.players[gamestate.leader].name), "!approve", "!reject"))
		send_delay_task = None
		with MsgQueue(client=client, check=votecheck) as msgqueue:
			while pending_voters:
				pmtrigger = await msgqueue.nextmsg()
				if pmtrigger.author in pending_voters:
					vc += 1
					pending_voters.remove(pmtrigger.author)
				if send_delay_task != None:
					send_delay_task.cancel()
				author_name = gamestate.players_by_duid[pmtrigger.author.id].name
				if pmtrigger.content == "!approve":
					await confirm(pmtrigger)
					voteStr += ":black_small_square: "
					if any(p.user.id == pmtrigger.author.id for p in gamestate.current_party):
						voteStr += "🏆 "
					voteStr += gamestate.t.votedApprove(author_name)
				elif pmtrigger.content == "!reject":
					await confirm(pmtrigger)
					voteStr += ":black_small_square: "
					if any(p.user.id == pmtrigger.author.id for p in gamestate.current_party):
						voteStr += "🏆 "
					voteStr += gamestate.t.votedReject(author_name)
					rejectcounter += 1
				elif pmtrigger.content == "!stop":
					await confirm(pmtrigger)
					await message.channel.send(gamestate.t.stopStr)
					gamestate.phase = Phase.INIT
					return
				await message.channel.send(gamestate.t.teamvoteCount(author_name, vc, num_voters))
				if len(pending_voters) > 0:
					mentions = ', '.join([user.mention for user in pending_voters])
					send_delay_task = asyncio.create_task(send_after_delay(message.channel, f'Just waiting for {mentions}...'))

		#votes have been submitted
		if gamestate.leader == (len(gamestate.players)-1):
			gamestate.leader = 0
		else:
			gamestate.leader += 1

		if rejectcounter >= (len(gamestate.players) / 2):
			gamestate.team_attempts -= 1
			if gamestate.team_attempts == 0:
				voteStr += gamestate.t.teamvoteEvilWins
				await message.channel.send(voteStr)
				gamestate.phase = Phase.GAMEOVER #evil win state
			else:
				voteStr += gamestate.t.teamvoteRejected
				await message.channel.send(voteStr)
				gamestate.phase = Phase.QUEST
		else:
			gamestate.team_attempts = 5 #reset passcount
			voteStr += gamestate.t.teamvoteAccepted
			await message.channel.send(voteStr)
			gamestate.phase = Phase.PRIVATEVOTE

async def privatevote(client, message, gamestate):
	while gamestate.phase == Phase.PRIVATEVOTE:
		def privatevotecheck(msg):
			if isinstance(msg.channel, DMChannel):
				if msg.author in activeplayers and gamestate.players_by_duid[msg.author.id].role.is_evil:
					if msg.content == "!success" or msg.content == "!fail":
						return True
				elif msg.author in activeplayers:
					if msg.content == "!success":
						return True
			elif msg.content == '!stop':
				return True
			return False
		fails = 0
		activeplayers = [p.user for p in gamestate.current_party]
		pending_players = [p.user for p in gamestate.current_party]
		namestring = " ".join(p.name for p in gamestate.current_party)

		await message.channel.send(gamestate.t.privatevoteStr(namestring))

		votecount = len(activeplayers)
		for voter in activeplayers:
			await voter.send(gamestate.t.privateVoteInfo(gamestate.t.quest, "!success", "!fail"))
		send_delay_task = None
		with MsgQueue(client=client, check=privatevotecheck) as msgqueue:
			while pending_players:
				pmtrigger = await msgqueue.nextmsg()
				if send_delay_task != None:
					send_delay_task.cancel()
				pending_players.remove(pmtrigger.author)
				if pmtrigger.content == "!success":
					await confirm(pmtrigger)
					await gamestate.skin.send_image(gamestate.skin.success_choice, pmtrigger.channel)
				elif pmtrigger.content == "!fail":
					await confirm(pmtrigger)
					await gamestate.skin.send_image(gamestate.skin.fail_choice, pmtrigger.channel)
					fails += 1
				if pmtrigger.content == "!stop":
					await confirm(pmtrigger)
					await message.channel.send(gamestate.t.stopStr)
					gamestate.phase = Phase.INIT
					return
				author_name = gamestate.players_by_duid[pmtrigger.author.id].name
				await message.channel.send(gamestate.t.privatevoteDone(author_name))
				if len(pending_players) > 0:
					mentions = ", ".join([user.mention for user in pending_players])
					send_delay_task = asyncio.create_task(send_after_delay(message.channel, f"Just waiting for {mentions}..."))
		
		quest = gamestate.quests[gamestate.current_quest-1]
		if fails >= quest.required_fails:
			quest.winning_team = Team.EVIL
			resultText = gamestate.t.questFailed(fails)
		else:
			quest.winning_team = Team.GOOD
			resultText = gamestate.t.questSucceeded(fails)
		await message.channel.send(resultText, file=await gamestate.skin.get_votes_file(message.channel, votecount - fails, fails))

		if not gamestate.quest_selection:
			gamestate.current_quest += 1

		if (gamestate.succeeded_quests == 3 or gamestate.failed_quests == 3):
			gamestate.phase = Phase.GAMEOVER
		else:
			gamestate.phase = Phase.QUEST

async def send_after_delay(channel, message):
	await asyncio.sleep(20)
	await channel.send(message)

async def gameover(client, message, gamestate):
	await gamestate.skin.send_board(gamestate, message.channel)
	if gamestate.succeeded_quests == 3:
		merlinPlayer = next(filter(lambda p: p.role == MERLIN, gamestate.players), None)
		merlin = None
		if merlinPlayer != None:
			merlin = merlinPlayer.user

		assassinPlayer = next(filter(lambda p: p.role == ASSASSIN, gamestate.players), None)
		if assassinPlayer == None:
			assassinPlayer = next(filter(lambda p: p.role == MORDRED, gamestate.players), None)
		if assassinPlayer == None:
			assassinPlayer = next(filter(lambda p: p.role.is_evil, gamestate.players), None)
		if assassinPlayer == None:
			await message.channel.send("No minions of Mordred are in this game - loyal knights win!")
			await message.channel.send(gamestate.t.stopStr)
			gamestate.phase = Phase.INIT
			return
		assassin = assassinPlayer.user
		def assassincheck(msg):
			if msg.content.startswith('!assassinate') and msg.author == assassin and len(msg.mentions)==1:
				return True
			elif msg.content == '!stop':
				return True
			return False
		await message.channel.send(gamestate.t.gameoverStr + gamestate.t.assassinatePrompt(assassin.mention))
		ass = await client.wait_for("message", check=add_channel_check(assassincheck, message.channel))
		if ass.content.startswith('!assassinate'):
			await confirm(ass)
			killedID = ass.mentions[0].id
			if merlin != None and merlin.id == killedID:
				await message.channel.send(gamestate.t.assassinateSucceeded)
				winning_team = Team.EVIL
			else:
				await message.channel.send(gamestate.t.assassinateFailed)
				winning_team = Team.GOOD
	elif gamestate.failed_quests == 3:
		await message.channel.send(gamestate.t.gameoverStr + gamestate.t.evilWinsByQuests)
		winning_team = Team.EVIL
	else:
		await message.channel.send(gamestate.t.gameoverStr + gamestate.t.evilWinsByFailure)
		winning_team = Team.EVIL
	for player in gamestate.players:
		if player.role.team is winning_team:
			await addscore(client, message, player.user)
	roles_str = "\n".join(gamestate.t.roleReveal(player.name, player.char.name)
			for player in gamestate.players)
	#roles_str += "\n**30 frickin' dollarydoos** have been credited to members of the winning team.\n\n"
	await message.channel.send(roles_str)
	await message.channel.send(gamestate.t.stopStr)
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

async def confirm(message):
	await message.add_reaction("✅")
async def deny(message):
	await message.add_reaction("⛔")
async def error(message):
	await message.add_reaction("❌")

import discord
from enum import Enum
from typing import List, Mapping, Optional
from dataclasses import dataclass, field

class Team(Enum):
	GOOD = 0   # loyal servants of Arthur, including Merlin and Percival
	EVIL = 1   # minions of Mordred, including Assassin, Morgana, Mordred

class Phase(Enum):
	INIT = 0          # initial state (unstable?)
	LOGIN = 1         # players are joining
	NIGHT = 2         # roles are disclosed to players (unstable)
	QUEST = 3         # team must be selected by leader
	TEAMVOTE = 4      # team must be voted by all players
	PRIVATEVOTE = 5   # quest is ongoing, adventurers must pick success or fail
	GAMEOVER = 6      # game is over (unstable)

@dataclass(frozen=True)
class Role:
	"""A role used in the game."""
	team: Team   # team, either GOOD (loyal servants) or EVIL (traitors)
	name: str    # full displayed name of the role
	@property
	def is_good(self):
		return self.team is Team.GOOD
	@property
	def is_evil(self):
		return self.team is Team.EVIL

@dataclass
class Quest:
	adventurers: int                      # team size for this quest
	required_fails: int = 1               # minimum fails needed for mission to fail
	winning_team: Optional[Team] = None   # outcome of quest, initially None

@dataclass
class Player:
	name: str                     # displayed name of player
	user: discord.abc.User        # reference to Discord user
	role: Optional[Role] = None   # player's role (set when game starts)



SERVANTS = [Role(Team.GOOD, "{}, Loyal Servant of Arthur".format(name))
            for name in ["Galahad", "Tristan", "Guinevere", "Lamorak"]]
MINIONS = [Role(Team.EVIL, "{}, Minion of Mordred".format(name))
           for name in ["Agravain", "Gareth"]]
MERLIN = Role(Team.GOOD, "Merlin")
PERCIVAL = Role(Team.GOOD, "Percival")
ASSASSIN = Role(Team.EVIL, "The Assassin")
MORGANA = Role(Team.EVIL, "Morgana")
MORDRED = Role(Team.EVIL, "Mordred")
OBERON = Role(Team.EVIL, "Oberon")

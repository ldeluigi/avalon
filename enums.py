from enum import Enum

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
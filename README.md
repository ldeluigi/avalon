# The Resistance: Avalon - Discord Edition

_Discord bot built using discord.py library. Original game by Don Eskridge._

You can host the bot yourself (remember to set the .env var SECRET_TOKEN to your discord bot token),
or you can add the public instance by clicking on this link:

https://discord.com/api/oauth2/authorize?client_id=699024385498939473&permissions=67632193&scope=bot

### Public instance status:

<a href="https://www.statuscake.com" title="Website Uptime Monitoring"><img src="https://app.statuscake.com/button/index.php?Track=K8Ne4neFxb&Days=1&Design=2" /></a>

_Note: permissions listed in the link are all required. Not granting one or more of them could lead to errors._

## Rules

_Information in this section drawn from a combination of the game's manual, Wikipedia and theresistanceonline.com_

**The Resistance: Avalon** is a variant of **The Resistance**. It is similar in structure to party games such as Mafia and Werewolf, where a small, secret group of informed players attempt to disrupt a larger uninformed group, while the larger group attempts to identify the traitors and eliminate them. The Resistance uses slightly different mechanics from similar games, and was designed to avoid player elimination and increase available information for player decisions.

Avalon is a game of hidden loyalty. Players are either Loyal Servants of Arthur fighting for Goodness and honor or aligned with the Evil ways of Mordred. Good wins the game by successfully completing three Quests. Evil wins if three Quests end in failure. Evil can also win by assassinating Merlin at game's end or if a Quest cannot be undertaken.

- The game requires between five and ten players.
- Approximately one third of the players are randomly chosen as **Evil**; the rest are **Good**. This depends on the player count.
- Evil players have knowledge of who their fellow evil players are. The Good players do not have any additional information.
- The game consists of up to five rounds called Quests.
- Each quest has a leader. The leader proposes a quest party of a certain size as determined by the game, which the group approves by public vote.
- The leader for the first quest is randomly determined, it will then pass in a sequential fashion as determined by the player list.
- If the group does not approve the quest by a simple majority, leadership passes to the next player.
- If the group cannot approve a quest party after five attempts, Evil wins.
- Once a mission team is chosen, it votes by secret ballot whether the mission succeeds or fails.
- Good will always vote for success and are unable to fail, but Evil has the option of voting for success or failure.
- It usually only takes one traitor to sabotage a quest, but in games of 7 or more the fourth quest will require two fails.
- (optional) After the 2nd, 3rd, and 4th missions, the player with the Lady of the Lake inspects the loyalty of another player. The lady of the lake then passes to te inspected player.
- If three quests succeed, Good wins. If three fail, Evil wins.
- In the event of a Good victory, a character known as the assassin will choose one person to assassinate. If Merlin is correctly identified and assassinated, Evil wins.

### Special Roles

#### Good

- Merlin - Merlin has knowledge of all the Evil players in the game (except Mordred). He must lead the forces of good, but do so with subtlety lest he be identified by the Assassin.
- Percival - Has knowledge of who Merlin is. If Morgana is in the game, Morgana will also appear as Merlin. Percival must carefully determine which is the true Merlin and condemn the imposter Morgana.

#### Evil

- The Assassin - If Good wins, if the Assassin is able to correctly identify Merlin- Evil will win instead.
- Morgana - Appears to Percival as Merlin. Must attempt to turn Percival against the true Merlin.
- Mordred - The Big Bad. Fully hidden. Merlin does not know who the Mordred player is.
- Oberon - The Blind Bad. Other evil characters don't know who he is, neither he knows who the other bads are.

### Original Rulebook

The original game rules can be found at http://upload.snakesandlattes.com/rules/r/ResistanceAvalon.pdf

## Commands

### In the discord group with the bot

- `!avalon` - Starts the game.  
  *You can select aspect/skin of the game and language by passing arguments to this command. See [the list](#custom-game-settings).*
- `!help` - Direct messages the user a link to this page.
- `!stop` - End the currently running game.
- `!join` - Used to join the game during the login phase.
- `!party` - Used by the leader to propose a party during the team building phase.
- `!assassinate` - Used by the Assassin in the event of a Good victory to assassinate a member of the game. This command does not have any input verification and only allows you **one** try. Ensure that you @tag the correct person!
- `!lady` - Examine a player's loyalty using Lady of the Lake

### In private to the bot

- `!approve/!reject` - Used to approve or reject a party during the team building phase.
- `!success/!fail` - Used to succeed or fail a quest during the secret vote phase.

### Custom game settings

#### Custom aspect and language

When you run `!avalon` you can pass special arguments that will be interpreted in order to select a language (between available translations) and a custom skin (that is a different set of role names, images and lore setting).  
Examples:
- `it`,`ita`,`italian` set language to italian;
- `sw`,`star wars` set skin to Star Wars and language to english;
- `gs`,`guerre stellari` set language to italian and skin to Star Wars (in italian "Guerre Stellari");

#### Custom Roles

During the join/login phase, players can set the role list by typing `!roles [roles-list]`, where roles-list is a list of roles separated by a space. With this command the lady of the lake can be enabled, by adding 'lady' to the roles list (even though she is not an actual player role).

## Coming Soon

- Suggest more features in the [Issue tab](https://github.com/ldeluigi/avalon/issues) of GitHub.

# Technical Stuff

## Requirements

_Only if you wish to download the source code and host your own copy of Avalon_

- Python 3.8
- pip - https://pip.pypa.io/en/stable/installing
- discord.py - https://github.com/Rapptz/discord.py  
  `pip install -U discord.py`
- dotenv - https://pypi.org/project/python-dotenv/  
  `pip install -U python-dotenv`
- pillow - https://pillow.readthedocs.io/en/stable/  
  `pip install -U Pillow`

**Alternatively, you can simply run** `pip install -r requirements.txt`

# Run instructions

1. Download dependencies  
   _Note: make sure python version meets requirements._
1. Setup the `SECRET_TOKEN` as environment variable or create a file called ".env" in the main folder containing:  
   `SECRET_TOKEN=token`  
   Where `token` is your discord bot token. ([Learn more](https://discord.com/developers/docs/topics/oauth2))
1. Run the start command:  
   `python dreamlord.py`

## CI/CD Status Badges

Continuous Integration:  
![Cross-Platform Build & Check Dependencies](https://github.com/ldeluigi/avalon/workflows/Cross-Platform%20Build%20&%20Check%20Dependencies/badge.svg)

Continuous Deployment:  
![Build and deploy Python app to Azure Web App - discord-avalon-bot](https://github.com/ldeluigi/avalon/workflows/Build%20and%20deploy%20Python%20app%20to%20Azure%20Web%20App%20-%20discord-avalon-bot/badge.svg?branch=release)

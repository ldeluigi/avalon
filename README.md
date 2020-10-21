# The Resistance: Avalon - Discord Edition
*Discord bot built using discord.py library. Original game by Don Eskridge.*

You can host the bot yourself (remember to set the .env var SECRET_TOKEN to your discord bot token),
or you can add the public instance by clicking on this link:

https://discord.com/api/oauth2/authorize?client_id=699024385498939473&permissions=67632193&scope=bot

### Public instance status:  
<a href="https://www.statuscake.com" title="Website Uptime Monitoring"><img src="https://app.statuscake.com/button/index.php?Track=K8Ne4neFxb&Days=1&Design=2" /></a>

*Note: permissions listed in the link are all required. Not granting one or more of them could lead to errors.*

## Rules
*Information in this section drawn from a combination of the game's manual, Wikipedia and theresistanceonline.com*

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
- `!avalon` - Starts the game.
- `!help` - Direct messages the user a link to this page.
- `!stop` - End the currently running game.
- `!join` - Used to join the game during the login phase.
- `!party` - Used by the leader to propose a party during the team building phase.
- `!approve/!reject` - Used to approve or reject a party during the team building phase.
- `!success/!fail` - Used to succeed or fail a quest during the secret vote phase.
- `!assassinate` - Used by the Assassin in the event of a Good victory to assassinate a member of the game. This command does not have any input verification and only allows you **one** try. Ensure that you @tag the correct person!

## Coming Soon
- Suggest more features in the [Issue tab](https://github.com/ldeluigi/avalon/issues) of GitHub.
- Simultaneous messages support (long term milestone)

# Technical Requirements
*Only if you wish to download the source code and host your own copy of Avalon*
- Python 3.5
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
*Note: make sure python version meets requirements.*
1. Setup the `SECRET_TOKEN` as environment variable or create a file called ".env" in the main folder containing:   
`SECRET_TOKEN=token`   
Where `token` is your discord bot token. ([Learn more](https://discord.com/developers/docs/topics/oauth2))   
1. Run the start command:   
`python dreamlord.py`  

import discord
import random
import linecache
import re
import shelve
import sys
import os
from random import shuffle
from avalon import avalon, confirm
from discord import DMChannel, Message
from discord.errors import Forbidden
from traceback import print_exc
#from wordgame import *
from dotenv import load_dotenv
load_dotenv()

client = discord.Client()
busyChannels = []
prefix = os.getenv("BOT_PREFIX", "!")
game_string = "The Resistance - Avalon. Type " + \
    prefix + "help or " + prefix + "start to begin."
game = discord.Game(name=game_string)


@client.event
async def on_message(message):
    if message.author == client.user:			# we do not want the bot to reply to itself
        return

    # non-prefixed commands
    if len(message.mentions) == 1 and client.user in message.mentions and re.match(r"^<[@!]{1,2}[\d]+>$", message.content):
        await confirm(message)
        await message.channel.send('\nMy prefix is currently `' + prefix + '`')

    if not message.content.startswith(prefix):
        return

    command = message.content[len(prefix):]

    # prefixed commands
    if command.startswith('hello'):
        await confirm(message)
        msg = 'Greetings {0.author.mention}'.format(message)
        await message.channel.send(msg)

    if command.startswith('avalon'):
        if message.channel in busyChannels:
            await message.channel.send("Channel busy with another activity.")
        elif not isinstance(message.channel, DMChannel):
            await confirm(message)
            busyChannels.append(message.channel)
            await message.channel.send("Starting **The Resistance: Avalon - Discord Edition** in `#"+message.channel.name+"`...")
            await avalon(client, message, prefix)
            busyChannels.remove(message.channel)

    if command.startswith('help'):
        # message.channel.send()
        await confirm(message)
        await message.author.send('Please visit https://github.com/ldeluigi/avalon to find out more.')


@client.event
async def on_ready():
    print('Connected!')
    print('Username: ' + client.user.name)
    print('ID: ' + str(client.user.id))
    await client.change_presence(activity=game)


@client.event
async def on_error(event, *args, **kwargs):
    if sys.exc_info()[0] == Forbidden and \
            event == "on_message" and \
            isinstance(args[0], Message):
        message = args[0]
        await message.channel.send(
            "```Error```\nInsufficient permissions, I can't do it. Type `!help` for help."
        )
    else:
        print_exc()


def run(token):
    try:
        client.loop.run_until_complete(client.start(token))
    except KeyboardInterrupt:
        print('Interrupted - Shutting Down')
        client.loop.run_until_complete(client.change_presence(
            status=discord.Status.offline, activity=None))
        client.loop.run_until_complete(client.logout())
        # cancel all tasks lingering
    finally:
        client.loop.close()


run(os.getenv("SECRET_TOKEN"))

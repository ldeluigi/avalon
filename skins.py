import discord
import os
import io
import math
import random
from dataclasses import dataclass
from typing import List, Tuple
from enum import Enum
from PIL import Image, ImageDraw, ImageColor, ImageFont
from asyncio import get_event_loop

from model import Team, Role, Player


IMAGE_DIR = "img"

@dataclass(frozen=True)
class Character:
    """A character representing a role in the game."""
    name: str
    image_path: str

@dataclass(frozen=True)
class PlayerBaseItem:
    path: str

@dataclass(frozen=True)
class PlayerBase:
    p5: PlayerBaseItem
    p6: PlayerBaseItem
    p7: PlayerBaseItem
    p8: PlayerBaseItem
    p9: PlayerBaseItem
    p10: PlayerBaseItem

@dataclass(frozen=True)
class Skin:
    """A class that represents a skin for game images."""
    path: str
    assassin: Character
    background: str
    board: PlayerBase
    evil_servants: List[Character]
    fail_choice: str
    fail_mark: str
    lady_evil: str
    lady_good: str
    logo: str
    loyal_servants: List[Character]
    merlin: Character
    mordred: Character
    morgana: Character
    oberon: Character
    percival: Character
    reject_mark: str
    role_back: str
    success_choice: str
    success_mark: str
    table: PlayerBase
    font: str

    def get_image(self, path:str):
        return IMAGE_DIR + os.path.sep + self.path + os.path.sep + path

    def get_image_file(self, path:str):
        return discord.File(self.get_image(path))

    def assign_characters(self, players: List[Player]):
        servants = []
        minions = []
        for p in players:
            if p.role.key == "servant":
                servants.append(p)
            elif p.role.key == "minion":
                minions.append(p)
            else:
                p.char = getattr(self, p.role.key)
        for p, c in zip(servants, random.sample(self.loyal_servants, len(servants))):
            p.char = c
        for p, c in zip(minions, random.sample(self.evil_servants, len(minions))):
            p.char = c

    async def send_image(self, path: str, channel):
        await channel.send(file=self.get_image_file(path))

    async def send_board(self, gamestate, channel):
        def _make_board():
            path = self.board.p10.path
            if len(gamestate.players) == 5:
                path = self.board.p5.path
            elif len(gamestate.players) == 6:
                path = self.board.p6.path
            elif len(gamestate.players) == 7:
                path = self.board.p7.path
            elif len(gamestate.players) == 8:
                path = self.board.p8.path
            elif len(gamestate.players) == 9:
                path = self.board.p9.path
            with Image.open(self.get_image(path)) as boardIm:
                circleWidth = int(boardIm.width / 10)
                with Image.open(self.get_image(self.reject_mark)) \
                 .resize((circleWidth, circleWidth)) as attemptIm:
                    left_times = 5 - gamestate.team_attempts
                    boardIm.alpha_composite(attemptIm, dest=(
                        int(boardIm.width / 16 + left_times * (boardIm.width / 27 + circleWidth)),
                        int(boardIm.height * 9.4 / 12)
                    ))
                    circleWidth = int(boardIm.width / 6.3)
                    with Image.open(self.get_image(self.success_mark)) \
                        .resize((circleWidth, circleWidth)) as successIm, \
                        Image.open(self.get_image(self.fail_mark)) \
                            .resize((circleWidth, circleWidth)) as failIm:
                        for quest, index in zip(gamestate.quests, range(0, len(gamestate.quests))):
                            pos = (int(boardIm.width / 27 + index * (boardIm.width / 34 + circleWidth)),
                             int(boardIm.height / 2.47))
                            if (quest.winning_team is Team.GOOD):
                                boardIm.alpha_composite(successIm, dest=pos)
                            if (quest.winning_team is Team.EVIL):
                                boardIm.alpha_composite(failIm, dest=pos)
                        arr = io.BytesIO()
                        boardIm.save(arr, format='PNG')
                        arr.seek(0)
                        return discord.File(arr, "board.png")
        await channel.send(file=await get_event_loop().run_in_executor(None, _make_board))

    async def send_table(self, gamestate, channel):
        def _make_table():
            path = self.table.p10.path
            if len(gamestate.players) == 5:
                path = self.table.p5.path
            elif len(gamestate.players) == 6:
                path = self.table.p6.path
            elif len(gamestate.players) == 7:
                path = self.table.p7.path
            elif len(gamestate.players) == 8:
                path = self.table.p8.path
            elif len(gamestate.players) == 9:
                path = self.table.p9.path
            with Image.open(self.get_image(path)) as tableIm:
                tableImDraw = ImageDraw.Draw(tableIm)
                tableCenter = (int(tableIm.width / 2.75), int(tableIm.height / 1.83))
                tableRadius = int(tableIm.width / 3.6)
                player_list = gamestate.players
                firstAngle = 2 * math.pi / len(player_list)
                stepAngle = 2 * math.pi / len(player_list)
                font = ImageFont.truetype(self.get_image(self.font), size=20)
                for player, index in zip(player_list, range(0, len(player_list))):
                    xOffset = tableRadius * math.cos(firstAngle - index * stepAngle)
                    yOffset = -(tableRadius * math.sin(firstAngle - index * stepAngle))
                    if (index == gamestate.leader):
                        fillColor = ImageColor.getrgb("yellow")
                    else:
                        fillColor = ImageColor.getrgb("white")
                    tableImDraw.text(xy=(tableCenter[0] + xOffset, tableCenter[1] + yOffset),
                        text=player.name, fill=fillColor, font=font, align="center")
                chars_list = list(map(lambda p: p.char, gamestate.players))
                chars_list.sort(key=lambda char: char.name)
                char_height = int(tableIm.height / len(chars_list))

                def get_image_for_char(char: Character):
                    return Image.open(self.get_image(char.image_path))

                def get_resized_image_for_char(char: Character):
                    charIm = get_image_for_char(char)
                    return charIm.resize((int(char_height * charIm.width / charIm.height), int(char_height)))

                if all(chars_list):
                    images_width = []
                    for char in chars_list:
                        with get_resized_image_for_char(char) as charIm:
                            images_width.append(charIm.width)
                    table_offset = max(images_width)
                    newIm = Image.new("RGBA", (tableIm.width + table_offset, tableIm.height))
                    newIm.alpha_composite(tableIm, dest=(table_offset, 0))
                    for index, char in enumerate(chars_list):
                        with get_resized_image_for_char(char) as charIm:
                                newIm.alpha_composite(charIm, dest=(0, index * char_height))
                    tableIm = newIm
                arr = io.BytesIO()
                tableIm.save(arr, format='PNG')
                arr.seek(0)
                return discord.File(arr, "table.png")
        await channel.send(file=await get_event_loop().run_in_executor(None, _make_table))

    async def get_votes_file(self, channel, success_votes:int, fail_votes:int):
        def _make_votes():
            with Image.open(self.get_image(self.success_choice)) as successIm, \
                Image.open(self.get_image(self.fail_choice)) as failIm:
                total_votes = success_votes + fail_votes
                total_width = success_votes * successIm.width + fail_votes * failIm.width + max(0, (10 - total_votes) * successIm.width)
                total_height = max(successIm.height, failIm.height)
                vote_list = [True] * success_votes + [False] * fail_votes
                random.shuffle(vote_list)
                newIm = Image.new("RGBA", (total_width, total_height))
                current_width = 0
                for vote in vote_list:
                    if vote:
                        newIm.alpha_composite(successIm, dest=(current_width, 0))
                        current_width += successIm.width
                    else:
                        newIm.alpha_composite(failIm, dest=(current_width, 0))
                        current_width += failIm.width
                arr = io.BytesIO()
                newIm.save(arr, format='PNG')
                arr.seek(0)
                return discord.File(arr, "votes.png")
        return await get_event_loop().run_in_executor(None, _make_votes)


Skins = dict(
    AVALON = Skin(
        path="avalon",
        assassin=Character("The Assassin", "assassin.png"),
        background="wood_bg.jpg",
        board=PlayerBase(
            p5=PlayerBaseItem("5_players_board.png"),
            p6=PlayerBaseItem("6_players_board.png"),
            p7=PlayerBaseItem("7_players_board.png"),
            p8=PlayerBaseItem("8_players_board.png"),
            p9=PlayerBaseItem("9_players_board.png"),
            p10=PlayerBaseItem("10_players_board.png")
        ),
        evil_servants=[
            Character("Agravain, Minion of Mordred", "evil_servant.png"),
            Character("Gareth, Minion of Mordred", "evil_servant.png"),
        ],
        fail_choice="fail_choose_card.png",
        fail_mark="fail_mark.png",
        lady_evil="lady_evil.png",
        lady_good="lady_good.png",
        logo="logo.png",
        loyal_servants=[
            Character("Galahad, Loyal Servant of Arthur", "loyal_servant.png"),
            Character("Tristan, Loyal Servant of Arthur", "loyal_servant.png"),
            Character("Guinevere, Loyal Servant of Arthur", "loyal_servant.png"),
            Character("Lamorak, Loyal Servant of Arthur", "loyal_servant.png"),
        ],
        merlin=Character("Merlin", "merlin.png"),
        mordred=Character("Mordred", "mordred.png"),
        morgana=Character("Morgana", "morgana.png"),
        oberon=Character("Oberon", "oberon.png"),
        percival=Character("Percival", "percival.png"),
        reject_mark="reject_mark.png",
        role_back="role_back.png",
        success_choice="success_choose_card.png",
        success_mark="success_mark.png",
        table=PlayerBase(
            p5=PlayerBaseItem("5_players_table.png"),
            p6=PlayerBaseItem("6_players_table.png"),
            p7=PlayerBaseItem("7_players_table.png"),
            p8=PlayerBaseItem("8_players_table.png"),
            p9=PlayerBaseItem("9_players_table.png"),
            p10=PlayerBaseItem("10_players_table.png")
        ),
        font="medieval.ttf"
    ),
    STARWARS = Skin(
        path="starwars",
        assassin=Character("Boba Fett", "boba_fett_assassin.png"),
        background="stars_bg.jpg",
        board=PlayerBase(
            p5=PlayerBaseItem("5_players_board.png"),
            p6=PlayerBaseItem("6_players_board.png"),
            p7=PlayerBaseItem("7_players_board.png"),
            p8=PlayerBaseItem("8_players_board.png"),
            p9=PlayerBaseItem("9_players_board.png"),
            p10=PlayerBaseItem("10_players_board.png")
        ),
        evil_servants=[
            Character("Stormtrooper", "trooper_evil.png"),
            Character("Stormtrooper", "trooper_evil.png"),
        ],
        fail_choice="fail_choose_card.png",
        fail_mark="fail_mark.png",
        lady_evil="lady_evil.png",
        lady_good="lady_good.png",
        logo="logo.png",
        loyal_servants=[
            Character("Rebel", "ally_0.png"),
            Character("C-3PO", "ally_1.png"),
            Character("Chewbacca", "ally_2.png"),
            Character("Princess Leia", "ally_3.png"),
            Character("R2-D2", "ally_4.png"),
            Character("Han Solo", "ally_5.png"),
        ],
        merlin=Character("Obi-Wan Kenobi", "obiwan.png"),
        mordred=Character("Emperor Palpatine", "palpatine.png"),
        morgana=Character("Darth Vader", "dartfener.png"),
        oberon=Character("Jabba the Hutt", "jabba.png"),
        percival=Character("Luke Skywalker", "luke.png"),
        reject_mark="reject_mark.png",
        role_back="role_back.png",
        success_choice="success_choose_card.png",
        success_mark="success_mark.png",
        table=PlayerBase(
            p5=PlayerBaseItem("5_players_table.png"),
            p6=PlayerBaseItem("6_players_table.png"),
            p7=PlayerBaseItem("7_players_table.png"),
            p8=PlayerBaseItem("8_players_table.png"),
            p9=PlayerBaseItem("9_players_table.png"),
            p10=PlayerBaseItem("10_players_table.png")
        ),
        font="starjedi.ttf"
    )
)
